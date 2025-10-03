from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import InvoiceJob
from ..database import SessionLocal
from ..schemas import InvoiceJobResponse, InvoiceJobCreate, InvoiceJobUpdate
from typing import List


router = APIRouter(prefix="/invoices-jobs", tags=["Invoices Jobs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[InvoiceJobResponse])
async def read_all(db: db_dependency):
    return db.query(InvoiceJob).all()


@router.get("/{invoice_job_id}", response_model=InvoiceJobResponse)
async def read_invoice_job(db: db_dependency, invoice_job_id: int = Path(gt=0)):
    query = db.query(InvoiceJob).filter(InvoiceJob.id == invoice_job_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Data not found")
    return query


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_invoice_job(db: db_dependency, invoice_job_request: InvoiceJobCreate):
    request_model = InvoiceJob(**invoice_job_request.model_dump())

    db.add(request_model)
    db.commit()
    db.refresh(request_model)
    return request_model


@router.put("/update/{invoice_job_id}", status_code=status.HTTP_206_PARTIAL_CONTENT)
async def update_invoice_job(
    db: db_dependency,
    invoice_job_request: InvoiceJobUpdate,
    invoice_job_id: int = Path(gt=0),
):

    request_model = db.query(InvoiceJob).filter(InvoiceJob.id == invoice_job_id).first()
    if request_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    update_data = invoice_job_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(request_model, key, value)

    db.commit()
    db.refresh(request_model)
    return request_model


@router.delete("/delete/{invoice_job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice_job(db: db_dependency, invoice_job_id: int = Path(gt=0)):

    db_model = db.query(InvoiceJob).filter(InvoiceJob.id == invoice_job_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_model)
    db.commit()
    return {"ok": True, "message": "Data deleted"}
