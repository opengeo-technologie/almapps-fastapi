from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Payment, Invoice
from ..database import SessionLocal
from ..schemas import (
    PaymentResponse,
    PaymentCreate,
    PaymentUpdate,
    InvoicePaymentResponse,
)
from typing import List


router = APIRouter(prefix="/payments", tags=["Payments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Read all
@router.get("/", response_model=List[PaymentResponse])
def get_purchase_orders(db: Session = Depends(get_db)):
    return db.query(Payment).all()


# Read by ID
@router.get("/{po_id}", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
def get_payment(po_id: int, db: Session = Depends(get_db)):
    query = db.query(Payment).filter(Payment.id == po_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return query


@router.get("/invoices/all", response_model=List[InvoicePaymentResponse])
def get_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).all()


@router.get("/invoices/all/{invoice_id}", response_model=InvoicePaymentResponse)
def get_invoices_payment_by_id(invoice_id: int, db: Session = Depends(get_db)):
    query = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return query


# Create
@router.post(
    "/create", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED
)
def create_payment(po: PaymentCreate, db: db_dependency):
    query = Payment(**po.model_dump())
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


# Update
@router.put(
    "/update/{po_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_206_PARTIAL_CONTENT,
)
def update_payment(po_id: int, po: PaymentUpdate, db: db_dependency):
    query = db.query(Payment).filter(Payment.id == po_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    for key, value in po.model_dump(exclude_unset=True).items():
        setattr(query, key, value)

    db.commit()
    db.refresh(query)
    return query


# Delete
@router.delete("/delete/{po_id}")
def delete_payment(po_id: int, db: Session = Depends(get_db)):
    query = db.query(Payment).filter(Payment.id == po_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    db.delete(query)
    db.commit()
    return {"detail": "Purchase order deleted"}
