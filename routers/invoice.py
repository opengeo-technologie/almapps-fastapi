from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Invoice
from ..database import SessionLocal
from ..schemas import (
    InvoiceResponse,
    InvoiceCreate,
    InvoiceUpdate,
    InvoicePaymentResponse,
)
from typing import List
from ..utils.generate_references import get_next_reference_invoice


router = APIRouter(prefix="/invoices", tags=["Invoices"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[InvoicePaymentResponse])
async def read_all(db: db_dependency):
    return db.query(Invoice).all()


@router.get("/{invoice_id}", response_model=InvoicePaymentResponse)
async def read_invoice(db: db_dependency, invoice_id: int = Path(gt=0)):
    query = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Data not found")
    return query


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_invoice(db: db_dependency, invoice_request: InvoiceCreate):
    # request_model = Invoice(**invoice_request.model_dump())

    # ✅ Generate reference
    ref = get_next_reference_invoice(db)

    # ✅ Update schema value directly
    updated_expense = invoice_request.model_copy(update={"reference": ref})
    # print(updated_order.model_dump())
    query = Invoice(**updated_expense.model_dump())

    db.add(query)
    db.commit()
    db.refresh(query)
    return query


@router.put("/update/{invoice_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def update_invoice(
    db: db_dependency,
    invoice_request: InvoiceUpdate,
    invoice_id: int = Path(gt=0),
):

    request_model = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if request_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    update_data = invoice_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(request_model, key, value)

    db.commit()
    db.refresh(request_model)
    return request_model


@router.delete("/delete/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(db: db_dependency, invoice_id: int = Path(gt=0)):

    db_model = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_model)
    db.commit()
    return {"ok": True, "message": "Data deleted"}
