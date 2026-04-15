from pathlib import Path
from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status

from backend1.utils.auth_utils import get_current_user
from ..model.cash_register import (
    CashRegister,
    Transaction,
    cascade_update_opening_balances,
)


from ..database import SessionLocal
from datetime import date
from ..schema.cash_register import (
    CascadeUpdateResponse,
    CashRegisterClose,
    CashRegisterDetail,
    CashRegisterResponse,
    ChainItem,
    CloseRegisterResponse,
    RegisterChainResponse,
    TransactionResponse,
    TransactionCreate,
    CashRegisterOpen,
    UpdateClosingBalance,
)

router = APIRouter(prefix="/cash", tags=["cash"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# ==================== Cash Register Endpoints ====================


@router.get("/register/previous/{current_date}")
def get_previous_register_by_date(current_date: date, db: Session = Depends(get_db)):
    """Get register from date directly before specified date"""
    previous = (
        db.query(CashRegister)
        .filter(CashRegister.date < current_date, CashRegister.status == "closed")
        .order_by(CashRegister.date.desc())
        .first()
    )

    if not previous:
        return None
        # raise HTTPException(
        #     status_code=404, detail=f"No previous register found before {current_date}"
        # )

    return {
        "id": previous.id,
        "date": previous.date,
        "closing_balance": previous.closing_balance,
    }


@router.get("/register/next/{current_date}")
def get_next_register_by_date(current_date: date, db: Session = Depends(get_db)):
    """Get register from date directly after specified date"""
    next_register = (
        db.query(CashRegister)
        .filter(CashRegister.date > current_date, CashRegister.status == "closed")
        .order_by(CashRegister.date.asc())
        .first()
    )

    if not next_register:
        return None
        # raise HTTPException(
        #     status_code=404, detail=f"No next register found after {current_date}"
        # )

    return {
        "id": next_register.id,
        "date": next_register.date,
        "previous_register_id": next_register.previous_register_id,
        "closing_balance": next_register.closing_balance,
        "opening_balance": next_register.opening_balance,
    }


@router.post(
    "/register/open",
    response_model=CashRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def open_register(
    request: CashRegisterOpen, user_id: int = 1, db: Session = Depends(get_db)
):
    """
    Open a new cash register.
    - Can link to previous day's closing balance
    - Or specify manual opening balance
    """
    user = get_current_user(db, user_id)

    # Use provided date or default to today
    register_date = request.register_date or date.today()

    # Check if register already exists for this date
    existing = db.query(CashRegister).filter(CashRegister.date == register_date).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Register already exists for {register_date}. Close or delete it first.",
        )

    # Check for open registers (only one can be open at a time)
    open_register = db.query(CashRegister).filter(CashRegister.status == "open").first()
    if open_register:
        raise HTTPException(
            status_code=400,
            detail=f"Register for {open_register.date} is already open. Close it first.",
        )

    previous_register = get_previous_register_by_date(register_date, db)
    next_register = get_next_register_by_date(register_date, db)

    # Determine opening balance
    opening_balance = 0.0
    linked_to_previous = 0
    previous_register_id = None

    if previous_register:

        opening_balance = previous_register["closing_balance"]
        linked_to_previous = 1
        previous_register_id = previous_register["id"]
    else:
        if request.opening_balance is None:
            raise HTTPException(
                status_code=400,
                detail="opening_balance required when not linking to previous.",
            )
        opening_balance = request.opening_balance

    # Create new register
    new_register = CashRegister(
        date=register_date,
        opening_balance=opening_balance,
        status="open",
        linked_to_previous=linked_to_previous,
        previous_register_id=previous_register_id,
        opened_by=user.id,
    )

    db.add(new_register)
    db.commit()
    db.refresh(new_register)

    if next_register and linked_to_previous:
        update_register_previous_register_id(db, next_register["id"], new_register.id)

    return new_register


@router.post(
    "/register/transaction",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_transaction(
    transaction: TransactionCreate, user_id: int = 1, db: Session = Depends(get_db)
):
    """Add a transaction to the current open register"""
    user = get_current_user(db, user_id)

    # Get open register
    register = db.query(CashRegister).filter(CashRegister.status == "open").first()
    if not register:
        raise HTTPException(status_code=400, detail="No open register. Open one first.")

    # Create transaction
    db_transaction = Transaction(
        type=transaction.type,
        amount=transaction.amount,
        date=transaction.date,
        category=transaction.category,
        description=transaction.description,
        cash_id=register.id,
        user_id=user.id,
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


@router.post("/register/close", response_model=CloseRegisterResponse)
def close_register(
    request: CashRegisterClose, user_id: int = 1, db: Session = Depends(get_db)
):
    """Close the current open register"""
    user = get_current_user(db, user_id)

    register = db.query(CashRegister).filter(CashRegister.status == "open").first()
    if not register:
        raise HTTPException(status_code=400, detail="No open register to close.")

    next_register = get_next_register_by_date(register.date, db)

    if next_register:
        cascade_update_opening_balances(db, register.id, request.closing_balance)

    # Update register
    register.closing_balance = request.closing_balance
    register.status = "closed"
    register.closed_by = user.id

    db.commit()
    db.refresh(register)

    # Calculate metrics
    difference = register.difference
    status_text = (
        "balanced" if difference == 0 else ("over" if difference > 0 else "short")
    )

    return CloseRegisterResponse(
        message=f"✅ Register closed - {status_text}",
        register_id=register.id,
        date=register.date,
        opening_balance=register.opening_balance,
        closing_balance=register.closing_balance,
        total_income=register.total_income,
        total_expenses=register.total_expenses,
        expected_closing=register.expected_closing,
        difference=difference,
        status=status_text,
    )


@router.put("/register/closing", response_model=CascadeUpdateResponse)
def update_closing_balance(
    request: UpdateClosingBalance, db: Session = Depends(get_db)
):
    """
    🔄 UPDATE CLOSING BALANCE - AUTO-CASCADES TO LINKED REGISTERS!

    When you update a register's closing balance, all linked subsequent
    registers' opening balances are automatically updated.
    """
    register = (
        db.query(CashRegister).filter(CashRegister.id == request.register_id).first()
    )

    if not register:
        raise HTTPException(
            status_code=404, detail=f"Register {request.register_id} not found"
        )

    if register.status != "closed":
        raise HTTPException(status_code=400, detail="Can only update closed registers")

    old_closing = register.closing_balance

    # Update closing balance
    register.closing_balance = request.new_closing_balance
    db.commit()

    # Cascade update to linked registers
    cascade_updates = cascade_update_opening_balances(
        db, request.register_id, request.new_closing_balance
    )

    return CascadeUpdateResponse(
        message=f"🔄 Closing updated! {len(cascade_updates)} register(s) auto-updated",
        register_id=request.register_id,
        old_closing=old_closing,
        new_closing=request.new_closing_balance,
        cascade_updates=cascade_updates,
        cascade_count=len(cascade_updates),
    )


@router.get("/register/chain", response_model=RegisterChainResponse)
def get_register_chain(db: Session = Depends(get_db)):
    """
    📊 VIEW COMPLETE REGISTER CHAIN
    Shows how registers link together and validates chain integrity
    """
    registers = db.query(CashRegister).order_by(CashRegister.date).all()
    print(f"Total registers in chain: {len(registers)}")

    chain = []
    chain_valid = True

    for register in registers:
        item = ChainItem(
            register_id=register.id,
            date=register.date,
            opening_balance=register.opening_balance,
            closing_balance=register.closing_balance,
            expected_closing=register.expected_closing,
            difference=register.difference,
            status=register.status,
            linked_to_previous=bool(register.linked_to_previous),
            previous_register_id=register.previous_register_id,
        )

        # Validate chain integrity
        if register.linked_to_previous and register.previous_register_id:
            previous = (
                db.query(CashRegister)
                .filter(CashRegister.id == register.previous_register_id)
                .first()
            )

            if previous and previous.closing_balance != register.opening_balance:
                chain_valid = False

        chain.append(item)

    return RegisterChainResponse(
        total_registers=len(chain), chain=chain, chain_integrity=chain_valid
    )


@router.get("/register/current", response_model=CashRegisterDetail)
def get_current_register(db: Session = Depends(get_db)):
    """Get the current open register with all details"""
    register = db.query(CashRegister).filter(CashRegister.status == "open").first()
    if not register:
        raise HTTPException(status_code=404, detail="No open register")

    return register


@router.get("/register/history", response_model=List[CashRegisterResponse])
def get_register_history(db: Session = Depends(get_db)):
    """Get all registers ordered by date"""
    return db.query(CashRegister).order_by(CashRegister.date.desc()).all()


@router.get("/register/{register_id}", response_model=CashRegisterDetail)
def get_register_details(register_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific register"""
    register = db.query(CashRegister).filter(CashRegister.id == register_id).first()
    if not register:
        raise HTTPException(status_code=404, detail="Register not found")

    return register


@router.get("/register/date/{register_date}", response_model=CashRegisterDetail)
def get_register_by_date(register_date: date, db: Session = Depends(get_db)):
    """Get register for a specific date"""
    register = db.query(CashRegister).filter(CashRegister.date == register_date).first()
    if not register:
        raise HTTPException(
            status_code=404, detail=f"No register found for {register_date}"
        )

    return register


@router.put("/register/{register_id}/reopen")
def reopen_register(register_id: int, db: Session = Depends(get_db)):
    """
    Reopen a closed register
    Removes closing balance and actual cash count
    """
    register = db.query(CashRegister).filter(CashRegister.id == register_id).first()

    if not register:
        raise HTTPException(
            status_code=404, detail=f"Register with ID {register_id} not found"
        )

    if register.status != "closed":
        raise HTTPException(status_code=400, detail="Register is not closed")

    # Check if there's another open register
    open_register = db.query(CashRegister).filter(CashRegister.status == "open").first()

    if open_register:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reopen: Register {open_register.id} for {open_register.date} is already open",
        )

    # Reopen the register
    register.status = "open"
    register.closing_balance = 0
    register.actual_cash_count = 0
    register.closed_by = None

    db.commit()
    db.refresh(register)

    return {
        "message": "Register reopened successfully",
        "register_id": register_id,
        "date": str(register.date),
        "status": "open",
        "opening_balance": float(register.opening_balance),
    }


# ==================== Transaction Queries ====================


@router.get("/transactions/", response_model=List[TransactionResponse])
def get_all_transactions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all transactions with pagination"""
    return db.query(Transaction).offset(skip).limit(limit).all()


@router.get("/transactions/user/{user_id}", response_model=List[TransactionResponse])
def get_user_transactions(user_id: int, db: Session = Depends(get_db)):
    """Get all transactions by a specific user"""
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()


@router.get(
    "/transactions/date/{transaction_date}", response_model=List[TransactionResponse]
)
def get_transactions_by_date(transaction_date: date, db: Session = Depends(get_db)):
    """Get all transactions for a specific date"""
    return db.query(Transaction).filter(Transaction.date == transaction_date).all()


@router.get(
    "/transactions/register/{register_id}", response_model=List[TransactionResponse]
)
def get_register_transactions(register_id: int, db: Session = Depends(get_db)):
    """Get all transactions for a specific register"""
    return db.query(Transaction).filter(Transaction.cash_id == register_id).all()


# ==================== Statistics & Reports ====================


@router.get("/stats/summary")
def get_summary_stats(db: Session = Depends(get_db)):
    """Get overall statistics"""
    total_registers = db.query(CashRegister).count()
    open_registers = (
        db.query(CashRegister).filter(CashRegister.status == "open").count()
    )
    closed_registers = (
        db.query(CashRegister).filter(CashRegister.status == "closed").count()
    )
    total_transactions = db.query(Transaction).count()
    total_income = db.query(Transaction).filter(Transaction.type == "in").count()
    total_expenses = db.query(Transaction).filter(Transaction.type == "out").count()

    return {
        "total_registers": total_registers,
        "open_registers": open_registers,
        "closed_registers": closed_registers,
        "total_transactions": total_transactions,
        "income_transactions": total_income,
        "expense_transactions": total_expenses,
    }


# ==================== HELPER FUNCTION ====================


def update_register_previous_register_id(
    db: Session, register_id: int, new_previous_id: int
):
    """Update the previous_register_id of a register"""
    register = db.query(CashRegister).filter(CashRegister.id == register_id).first()
    if not register:
        raise HTTPException(
            status_code=404, detail=f"Register with ID {register_id} not found"
        )

    register.previous_register_id = new_previous_id
    db.commit()
    db.refresh(register)

    return {
        "message": f"Register {register_id} previous_register_id updated to {new_previous_id}",
        "register_id": register_id,
        "new_previous_register_id": new_previous_id,
    }


def cascade_update_opening_balances(
    db: Session, register_id: int, new_closing_balance: float
) -> list:
    """
    When a closing balance is updated, cascade update all linked registers
    """
    updates = []
    current_register_id = register_id
    current_closing = new_closing_balance

    while True:
        # Find next linked register
        next_register = (
            db.query(CashRegister)
            .filter(
                CashRegister.previous_register_id == current_register_id,
                CashRegister.linked_to_previous == 1,
            )
            .first()
        )

        if not next_register:
            break

        # Stop if we hit an open register (don't update)
        if next_register.status == "open":
            break

        # Update opening balance
        old_opening = float(next_register.opening_balance)
        next_register.opening_balance = current_closing
        next_register.closing_balance = next_register.expected_closing

        updates.append(
            {
                "register_id": next_register.id,
                "date": str(next_register.date),
                "old_opening": old_opening,
                "new_opening": current_closing,
            }
        )

        # Move to next in chain
        current_register_id = next_register.id
        current_closing = (
            next_register.closing_balance
            if next_register.closing_balance
            else current_closing
        )

    db.commit()

    return updates
