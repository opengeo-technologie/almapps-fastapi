from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import QuotationType
from ..database import SessionLocal
from ..schemas import (
    QuotationTypeResponse,
    QuotationTypeCreate,
    QuotationTypeUpdate,
)
from typing import List


router = APIRouter(
    prefix="/quotations_types",
    tags=["Quotations Types"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Get all
@router.get("/", response_model=List[QuotationTypeResponse])
def read_all(db: Session = Depends(get_db)):
    return db.query(QuotationType).all()


# Get by id
@router.get("/{quotation_type_id}", response_model=QuotationTypeResponse)
def read_quotation_type(quotation_type_id: int, db: Session = Depends(get_db)):
    db_quotation_type = (
        db.query(QuotationType).filter(QuotationType.id == quotation_type_id).first()
    )
    if not db_quotation_type:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_quotation_type


# Create
@router.post(
    "/create",
    response_model=QuotationTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_quotation_type(
    quotation_type: QuotationTypeCreate, db: Session = Depends(get_db)
):
    db_quotation_type = QuotationType(**quotation_type.model_dump())
    db.add(db_quotation_type)
    db.commit()
    db.refresh(db_quotation_type)
    return db_quotation_type


# Update
@router.put("/update/{quotation_type_id}", response_model=QuotationTypeResponse)
def update_quotation_type(
    quotation_type_id: int,
    quotation_type_update: QuotationTypeUpdate,
    db: Session = Depends(get_db),
):
    db_quotation_type = (
        db.query(QuotationType).filter(QuotationType.id == quotation_type_id).first()
    )
    if not db_quotation_type:
        raise HTTPException(status_code=404, detail="Data not found")

    update_data = quotation_type_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_quotation_type, key, value)

    db.commit()
    db.refresh(db_quotation_type)
    return db_quotation_type


# Delete
@router.delete("/delete/{quotation_type_id}")
def delete_quotation_type(quotation_type_id: int, db: Session = Depends(get_db)):
    db_quotation_type = (
        db.query(QuotationType).filter(QuotationType.id == quotation_type_id).first()
    )
    if not db_quotation_type:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_quotation_type)
    db.commit()
    return {"ok": True, "message": "Data deleted"}
