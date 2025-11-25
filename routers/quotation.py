from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Quotation
from ..database import SessionLocal
from ..schemas import (
    QuotationResponse,
    QuotationCreate,
    QuotationUpdate,
)
from typing import List
from ..utils.generate_references import get_next_reference_pro


router = APIRouter(
    prefix="/quotations",
    tags=["Quotations"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Get all
@router.get("/", response_model=List[QuotationResponse])
def read_all(db: Session = Depends(get_db)):
    return db.query(Quotation).all()


# Get by id
@router.get("/{quotation_id}", response_model=QuotationResponse)
def read_quotation(quotation_id: int, db: Session = Depends(get_db)):
    db_quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_quotation


# Create
@router.post(
    "/create",
    response_model=QuotationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_quotation(quotation: QuotationCreate, db: Session = Depends(get_db)):
    # db_quotation = Quotation(**quotation.model_dump())

    # ✅ Generate reference
    ref = get_next_reference_pro(db)

    # ✅ Update schema value directly
    updated_expense = quotation.model_copy(update={"reference": ref})
    # print(updated_order.model_dump())
    query = Quotation(**updated_expense.model_dump())
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


# Update
@router.put(
    "/update/{quotation_id}",
    response_model=QuotationResponse,
    status_code=status.HTTP_206_PARTIAL_CONTENT,
)
def update_quotation(
    quotation_id: int,
    quotation_update: QuotationUpdate,
    db: Session = Depends(get_db),
):
    db_quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Data not found")

    update_data = quotation_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_quotation, key, value)

    db.commit()
    db.refresh(db_quotation)
    return db_quotation


# Delete
@router.delete("/delete/{quotation_id}")
def delete_quotation(quotation_id: int, db: Session = Depends(get_db)):
    db_quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not db_quotation:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_quotation)
    db.commit()
    return {"ok": True, "message": "Data deleted"}
