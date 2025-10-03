from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Vendor
from ..database import SessionLocal
from ..schemas import VendorResponse, VendorCreate
from typing import List


router = APIRouter(prefix="/vendors", tags=["Vendors"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[VendorResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT * FROM vendors;
    """
        )
    )
    data = []
    for row in result:
        data.append(
            {
                "id": row.id,
                "name": row.name,
                "email": row.email,
                "phone": row.phone,
                "address": row.address,
            }
        )
    return data


@router.get("/{vendor_id}", response_model=VendorResponse)
async def read_vendor(db: db_dependency, vendor_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM vendors
        WHERE id = :vendor_id
    """
        ),
        {"vendor_id": vendor_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "name": result.name,
        "email": result.email,
        "phone": result.phone,
        "address": result.address,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_client(db: db_dependency, contact_request: VendorCreate):
    vendor_model = Vendor(**contact_request.model_dump())

    db.add(vendor_model)
    db.commit()


@router.put("/update/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_vendor(
    db: db_dependency,
    contact_request: VendorCreate,
    vendor_id: int = Path(gt=0),
):

    vendor_model = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if vendor_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    vendor_model.name = contact_request.name
    vendor_model.address = contact_request.address
    vendor_model.email = contact_request.email
    vendor_model.phone = contact_request.phone

    db.add(vendor_model)
    db.commit()


@router.delete("/delete/{vendor_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_vendor(db: db_dependency, vendor_id: int = Path(gt=0)):

    vendor_model = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if vendor_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(Vendor).filter(Vendor.id == vendor_id).delete()

    db.commit()
