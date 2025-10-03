from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Invoice
from ..database import SessionLocal
from ..schemas import InvoiceResponse, InvoiceCreate, InvoiceUpdate
from typing import List


router = APIRouter(prefix="/invoices", tags=["Invoices"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[InvoiceResponse])
async def read_all(db: db_dependency):
    return db.query(Invoice).all()


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def read_invoice(db: db_dependency, invoice_id: int = Path(gt=0)):
    query = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Data not found")
    return query


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_invoice(db: db_dependency, invoice_request: InvoiceCreate):
    request_model = Invoice(**invoice_request.model_dump())

    db.add(request_model)
    db.commit()
    db.refresh(request_model)
    return request_model


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
