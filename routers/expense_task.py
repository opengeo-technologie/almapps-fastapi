# app/routers/cash.py
from pathlib import Path
from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status
from ..models import ExpenseTask
from ..database import SessionLocal
from datetime import date
from ..schemas import ExpenseTaskResponse, ExpenseTaskCreate, ExpenseTaskUpdate

router = APIRouter(prefix="/expense-tasks", tags=["Expense Tasks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[ExpenseTaskResponse])
async def read_all(db: db_dependency):
    return db.query(ExpenseTask).all()


@router.get("/{expense_task_id}", response_model=ExpenseTaskResponse)
async def read_expense_task(db: db_dependency, expense_task_id: int = Path(gt=0)):
    query = db.query(ExpenseTask).filter(ExpenseTask.id == expense_task_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Data not found")
    return query


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_expense_task(db: db_dependency, db_request: ExpenseTaskCreate):
    db_model = ExpenseTask(**db_request.model_dump())

    db.add(db_model)
    db.commit()

    db.refresh(db_model)  # refresh to get generated fields like id
    return db_model


@router.put("/update/{expense_task_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def update_expense_task(
    db: db_dependency,
    db_request: ExpenseTaskUpdate,
    expense_task_id: int = Path(gt=0),
):

    request_model = (
        db.query(ExpenseTask).filter(ExpenseTask.id == expense_task_id).first()
    )
    if request_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    update_data = db_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(request_model, key, value)

    db.commit()
    db.refresh(request_model)
    return request_model


@router.delete("/delete/{expense_task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(db: db_dependency, expense_task_id: int = Path(gt=0)):

    db_model = db.query(ExpenseTask).filter(ExpenseTask.id == expense_task_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_model)
    db.commit()
    return {"ok": True, "message": "Data deleted"}
