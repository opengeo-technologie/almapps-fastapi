from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import QuotationProduct
from ..database import SessionLocal
from ..schemas import (
    QuotationProductResponse,
    QuotationProductCreate,
    QuotationProductUpdate,
)
from typing import List


router = APIRouter(
    prefix="/quotations_products",
    tags=["Quotations Products"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Get all
@router.get("/", response_model=List[QuotationProductResponse])
def read_all(db: Session = Depends(get_db)):
    return db.query(QuotationProduct).all()


# Get by id
@router.get("/{quotation_product_id}", response_model=QuotationProductResponse)
def read_quotation(quotation_product_id: int, db: Session = Depends(get_db)):
    db_quotation_product = (
        db.query(QuotationProduct)
        .filter(QuotationProduct.id == quotation_product_id)
        .first()
    )
    if not db_quotation_product:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_quotation_product


# Create
@router.post(
    "/create",
    response_model=QuotationProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_quotation_product(
    quotation_product: QuotationProductCreate, db: Session = Depends(get_db)
):
    db_quotation_product = QuotationProduct(**quotation_product.model_dump())
    db.add(db_quotation_product)
    db.commit()
    db.refresh(db_quotation_product)
    return db_quotation_product


# Update
@router.put("/update/{quotation_product_id}", response_model=QuotationProductResponse)
def update_quotation_product(
    quotation_product_id: int,
    quotation_product_update: QuotationProductUpdate,
    db: Session = Depends(get_db),
):
    db_quotation_product = (
        db.query(QuotationProduct)
        .filter(QuotationProduct.id == quotation_product_id)
        .first()
    )
    if not db_quotation_product:
        raise HTTPException(status_code=404, detail="Data not found")

    update_data = quotation_product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_quotation_product, key, value)

    db.commit()
    db.refresh(db_quotation_product)
    return db_quotation_product


# Delete
@router.delete("/delete/{quotation_product_id}")
def delete_quotation_product(quotation_product_id: int, db: Session = Depends(get_db)):
    db_quotation_product = (
        db.query(QuotationProduct)
        .filter(QuotationProduct.id == quotation_product_id)
        .first()
    )
    if not db_quotation_product:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_quotation_product)
    db.commit()
    return {"ok": True, "message": "Data deleted"}
