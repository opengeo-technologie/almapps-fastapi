from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import CompanyDetail
from ..database import SessionLocal
from ..schemas import CompanyDetailResponse, CompanyDetailCreate, CompanyDetailUpdate
from typing import List


router = APIRouter(prefix="/company-detail", tags=["Company Detail"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Get all company details
@router.get("/", response_model=List[CompanyDetailResponse])
async def read_all(db: db_dependency):
    return db.query(CompanyDetail).all()


# Get one company detail by ID
@router.get("/{company_id}", response_model=CompanyDetailResponse)
async def read_company_detail(db: db_dependency, company_id: int = Path(gt=0)):
    company = db.query(CompanyDetail).filter(CompanyDetail.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/company/activated", response_model=CompanyDetailResponse)
async def read_company_detail_activated(db: db_dependency):
    company = db.query(CompanyDetail).filter(CompanyDetail.status == True).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_company_detail(db: db_dependency, company: CompanyDetailCreate):
    db_company = CompanyDetail(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@router.put("/update/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_company_detail(
    db: db_dependency,
    company_id: int,
    company_update: CompanyDetailUpdate,
):

    company = db.query(CompanyDetail).filter(CompanyDetail.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    for key, value in company_update.model_dump(exclude_unset=True).items():
        setattr(company, key, value)

    db.commit()
    db.refresh(company)
    return company


@router.delete("/delete/{company_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_company_detail(db: db_dependency, company_id: int = Path(gt=0)):

    company = db.query(CompanyDetail).filter(CompanyDetail.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()
    return {"message": "Company deleted successfully"}
