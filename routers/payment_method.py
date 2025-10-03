from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import PaymentMethod
from ..database import SessionLocal
from ..schemas import (
    PaymentMethodResponse,
    PaymentMethodCreate,
    PaymentMethodUpdate,
)
from typing import List


router = APIRouter(prefix="/payment-methods", tags=["Payment Method"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Read all
@router.get("/", response_model=List[PaymentMethodResponse])
def get_payment_methods(db: Session = Depends(get_db)):
    return db.query(PaymentMethod).all()


# Read by ID
@router.get(
    "/{po_id}", response_model=PaymentMethodResponse, status_code=status.HTTP_200_OK
)
def get_payment_method(po_id: int, db: Session = Depends(get_db)):
    query = db.query(PaymentMethod).filter(PaymentMethod.id == po_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return query


# Create
@router.post(
    "/create", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED
)
def create_payment_method(po: PaymentMethodCreate, db: db_dependency):
    query = PaymentMethod(**po.model_dump())
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


# Update
@router.put(
    "/update/{po_id}",
    response_model=PaymentMethodResponse,
    status_code=status.HTTP_206_PARTIAL_CONTENT,
)
def update_payment_method(po_id: int, po: PaymentMethodUpdate, db: db_dependency):
    query = db.query(PaymentMethod).filter(PaymentMethod.id == po_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    for key, value in po.model_dump(exclude_unset=True).items():
        setattr(query, key, value)

    db.commit()
    db.refresh(query)
    return query


# Delete
@router.delete("/delete/{po_id}")
def delete_payment_method(po_id: int, db: Session = Depends(get_db)):
    query = db.query(PaymentMethod).filter(PaymentMethod.id == po_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    db.delete(query)
    db.commit()
    return {"detail": "Purchase order deleted"}
