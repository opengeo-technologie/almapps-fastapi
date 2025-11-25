# app/routers/cash.py
from pathlib import Path
from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import extract
from starlette import status
from ..models import Expense
from ..database import SessionLocal
from datetime import date
from ..schemas import ExpenseResponse, ExpenseCreate, ExpenseUpdate
from ..utils.generate_references import get_expense_reference

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[ExpenseResponse])
async def read_all(db: db_dependency):
    return db.query(Expense).all()


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def read_expense(db: db_dependency, expense_id: int = Path(gt=0)):
    query = db.query(Expense).filter(Expense.id == expense_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Data not found")
    return query


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_expense(db: db_dependency, db_request: ExpenseCreate):

    # ✅ Generate reference
    ref = get_expense_reference(db)

    # ✅ Update schema value directly
    updated_expense = db_request.model_copy(update={"reference": ref})
    # print(updated_order.model_dump())
    query = Expense(**updated_expense.model_dump())

    db.add(query)
    db.commit()

    db.refresh(query)  # refresh to get generated fields like id
    return query


@router.put("/update/{expense_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def update_expense(
    db: db_dependency,
    db_request: ExpenseUpdate,
    expense_id: int = Path(gt=0),
):

    request_model = db.query(Expense).filter(Expense.id == expense_id).first()
    if request_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    update_data = db_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(request_model, key, value)

    db.commit()
    db.refresh(request_model)
    return request_model


@router.delete("/delete/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(db: db_dependency, expense_id: int = Path(gt=0)):

    db_model = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_model)
    db.commit()
    return {"ok": True, "message": "Data deleted"}


@router.get("/report-per-year/{year}", response_model=List[ExpenseResponse])
async def read_expense(db: db_dependency, year: int = Path(gt=0)):
    query = db.query(Expense).filter(extract("year", Expense.date) == year).all()
    # if not query:
    #     raise HTTPException(status_code=404, detail="Data not found")
    return query


@router.get("/report-per-month/{month}", response_model=List[ExpenseResponse])
async def read_expense(db: db_dependency, month: int = Path(gt=0)):
    query = db.query(Expense).filter(extract("month", Expense.date) == month).all()
    # if not query:
    #     raise HTTPException(status_code=404, detail="Data not found")
    return query


@router.get("/report-per-week/{week}", response_model=List[ExpenseResponse])
async def read_expense(db: db_dependency, week: int = Path(gt=0)):
    query = db.query(Expense).filter(extract("week", Expense.date) == week - 1).all()
    # if not query:
    #     raise HTTPException(status_code=404, detail="Data not found")
    return query
