from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import InvoiceType
from ..database import SessionLocal
from ..schemas import InvoiceTypeResponse, InvoiceTypeCreate, InvoiceTypeUpdate
from typing import List


router = APIRouter(prefix="/invoices-types", tags=["Invoices types"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[InvoiceTypeResponse])
async def read_all(db: db_dependency):
    return db.query(InvoiceType).all()


@router.get("/{invoice_type_id}", response_model=InvoiceTypeResponse)
async def read_invoice_type(db: db_dependency, invoice_type_id: int = Path(gt=0)):
    query = db.query(InvoiceType).filter(InvoiceType.id == invoice_type_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Data not found")
    return query


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_invoice_type(
    db: db_dependency, invoice_type_request: InvoiceTypeCreate
):
    request_model = InvoiceType(**invoice_type_request.model_dump())

    db.add(request_model)
    db.commit()
    db.refresh(request_model)
    return request_model


@router.put("/update/{invoice_type_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def update_invoice_type(
    db: db_dependency,
    invoice_type_request: InvoiceTypeUpdate,
    invoice_type_id: int = Path(gt=0),
):

    request_model = (
        db.query(InvoiceType).filter(InvoiceType.id == invoice_type_id).first()
    )
    if request_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    update_data = invoice_type_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(request_model, key, value)

    db.commit()
    db.refresh(request_model)
    return request_model


@router.delete("/delete/{invoice_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice_type(db: db_dependency, invoice_type_id: int = Path(gt=0)):

    db_model = db.query(InvoiceType).filter(InvoiceType.id == invoice_type_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_model)
    db.commit()
    return {"ok": True, "message": "Data deleted"}
