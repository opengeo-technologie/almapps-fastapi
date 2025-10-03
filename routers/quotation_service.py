from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import QuotationService
from ..database import SessionLocal
from ..schemas import (
    QuotationServiceResponse,
    QuotationServiceCreate,
    QuotationServiceUpdate,
)
from typing import List


router = APIRouter(
    prefix="/quotations_services",
    tags=["Quotations Services"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Get all
@router.get("/", response_model=List[QuotationServiceResponse])
def read_all(db: Session = Depends(get_db)):
    return db.query(QuotationService).all()


# Get by id
@router.get("/{quotation_service_id}", response_model=QuotationServiceResponse)
def read_quotation_service(quotation_service_id: int, db: Session = Depends(get_db)):
    db_quotation_service = (
        db.query(QuotationService)
        .filter(QuotationService.id == quotation_service_id)
        .first()
    )
    if not db_quotation_service:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_quotation_service


# Create
@router.post(
    "/create",
    response_model=QuotationServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_quotation_service(
    quotation_service: QuotationServiceCreate, db: Session = Depends(get_db)
):
    db_quotation_service = QuotationService(**quotation_service.model_dump())
    db.add(db_quotation_service)
    db.commit()
    db.refresh(db_quotation_service)
    return db_quotation_service


# Update
@router.put("/update/{quotation_service_id}", response_model=QuotationServiceResponse)
def update_quotation_service(
    quotation_service_id: int,
    quotation_service_update: QuotationServiceUpdate,
    db: Session = Depends(get_db),
):
    db_quotation_service = (
        db.query(QuotationService)
        .filter(QuotationService.id == quotation_service_id)
        .first()
    )
    if not db_quotation_service:
        raise HTTPException(status_code=404, detail="Data not found")

    update_data = quotation_service_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_quotation_service, key, value)

    db.commit()
    db.refresh(db_quotation_service)
    return db_quotation_service


# Delete
@router.delete("/delete/{quotation_service_id}")
def delete_quotation_service(QuotationService: int, db: Session = Depends(get_db)):
    db_quotation_service = (
        db.query(QuotationService)
        .filter(QuotationService.id == QuotationService)
        .first()
    )
    if not db_quotation_service:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_quotation_service)
    db.commit()
    return {"ok": True, "message": "Data deleted"}
