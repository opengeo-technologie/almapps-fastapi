from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import PurchaseOrderProduct
from ..database import SessionLocal
from ..schemas import (
    PurchaseOrderProductResponse,
    PurchaseOrderProductCreate,
    PurchaseOrderProductUpdate,
)
from typing import List


router = APIRouter(
    prefix="/purchase_order_products",
    tags=["Purchase Order Products"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Get all
@router.get("/", response_model=List[PurchaseOrderProductResponse])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(PurchaseOrderProduct).offset(skip).limit(limit).all()


# Get by id
@router.get("/{product_id}", response_model=PurchaseOrderProductResponse)
def read_purchase_order_product(product_id: int, db: Session = Depends(get_db)):
    db_product = (
        db.query(PurchaseOrderProduct)
        .filter(PurchaseOrderProduct.id == product_id)
        .first()
    )
    if not db_product:
        raise HTTPException(status_code=404, detail="PurchaseOrderProduct not found")
    return db_product


# Create
@router.post(
    "/create",
    response_model=PurchaseOrderProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase_order_product(
    product: PurchaseOrderProductCreate, db: Session = Depends(get_db)
):
    db_product = PurchaseOrderProduct(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


# Update
@router.put("/update/{product_id}", response_model=PurchaseOrderProductResponse)
def update_purchase_order_product(
    product_id: int,
    product_update: PurchaseOrderProductUpdate,
    db: Session = Depends(get_db),
):
    db_product = (
        db.query(PurchaseOrderProduct)
        .filter(PurchaseOrderProduct.id == product_id)
        .first()
    )
    if not db_product:
        raise HTTPException(status_code=404, detail="PurchaseOrderProduct not found")

    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


# Delete
@router.delete("/delete/{product_id}")
def delete_purchase_order_product(product_id: int, db: Session = Depends(get_db)):
    db_product = (
        db.query(PurchaseOrderProduct)
        .filter(PurchaseOrderProduct.id == product_id)
        .first()
    )
    if not db_product:
        raise HTTPException(status_code=404, detail="PurchaseOrderProduct not found")

    db.delete(db_product)
    db.commit()
    return {"ok": True, "message": "PurchaseOrderProduct deleted"}
