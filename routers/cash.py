# app/routers/cash.py
from pathlib import Path
from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status
from ..models import CashRegister, Transaction
from ..database import SessionLocal
from datetime import date
from ..schemas import CashRegisterResponse, TransactionResponse, TransactionCreate

router = APIRouter(prefix="/cash", tags=["cash"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[CashRegisterResponse])
async def read_all(db: db_dependency):
    return db.query(CashRegister).all()


@router.get("/register/{cash_id}", response_model=CashRegisterResponse)
async def read_cash_register(db: db_dependency, cash_id: int = Path(gt=0)):
    query = db.query(CashRegister).filter(CashRegister.id == cash_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Data not found")
    return query


@router.get("/opened_register", response_model=CashRegisterResponse)
async def read_opened_register(db: db_dependency):
    return db.query(CashRegister).filter(CashRegister.status == "open").first()


@router.post("/open")
def open_cash(opening_balance: float, db: db_dependency):
    today = date.today()
    existing = db.query(CashRegister).filter(CashRegister.date == today).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Caisse déjà ouverte pour aujourd'hui."
        )

    prev_opened = db.query(CashRegister).filter(CashRegister.status == "open").first()

    if prev_opened:
        entries = sum(t.amount for t in prev_opened.transactions if t.type == "in")
        exits = sum(t.amount for t in prev_opened.transactions if t.type == "out")
        prev_opened.closing_balance = prev_opened.opening_balance + entries - exits
        prev_opened.status = "closed"
        db.commit()
    prev = db.query(CashRegister).order_by(CashRegister.date.desc()).first()
    opening_balance = prev.closing_balance if prev else opening_balance

    new_cash = CashRegister(opening_balance=opening_balance)
    db.add(new_cash)
    db.commit()
    db.refresh(new_cash)
    return new_cash


@router.post("/close")
def close_cash(db: db_dependency):
    cash = db.query(CashRegister).filter(CashRegister.status == "open").first()

    if not cash:
        raise HTTPException(
            status_code=404, detail="Caisse non trouvée ou déjà fermée."
        )

    entries = sum(t.amount for t in cash.transactions if t.type == "in")
    exits = sum(t.amount for t in cash.transactions if t.type == "out")
    cash.closing_balance = cash.opening_balance + entries - exits
    cash.status = "closed"
    db.commit()
    return {"closing_balance": cash.closing_balance, "status": "closed"}


@router.get("/transactions", response_model=List[TransactionResponse])
async def read_all(db: db_dependency):
    return db.query(Transaction).all()


@router.get("/transactions/{cash_id}", response_model=List[TransactionResponse])
async def read_transactions_per_cash_register(
    db: db_dependency, cash_id: int = Path(gt=0)
):
    query = db.query(Transaction).filter(Transaction.cash_id == cash_id).all()
    return query


@router.post("/transactions/create", status_code=status.HTTP_201_CREATED)
async def create_transaction(db: db_dependency, db_request: TransactionCreate):
    db_model = Transaction(**db_request.model_dump())

    db.add(db_model)
    db.commit()

    db.refresh(db_model)  # refresh to get generated fields like id
    return db_model


@router.get("/transaction/{transaction_id}", response_model=TransactionResponse)
async def read_transactions_per_cash_register(
    db: db_dependency, transaction_id: int = Path(gt=0)
):
    query = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Data not found")
    return query


@router.put(
    "/transactions/update/{transaction_id}", status_code=status.HTTP_206_PARTIAL_CONTENT
)
async def update_transaction(
    db: db_dependency,
    db_request: TransactionCreate,
    transaction_id: int = Path(gt=0),
):

    request_model = (
        db.query(Transaction).filter(Transaction.id == transaction_id).first()
    )
    if request_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    update_data = db_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(request_model, key, value)

    db.commit()
    db.refresh(request_model)
    return request_model


@router.delete(
    "/transactions/delete/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_transaction(db: db_dependency, transaction_id: int = Path(gt=0)):

    db_model = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_model)
    db.commit()
    return {"ok": True, "message": "Data deleted"}
