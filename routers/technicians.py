from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Technician
from ..database import SessionLocal
from ..schemas import TechnicianResponse, TechnicianCreate
from typing import List


router = APIRouter(prefix="/technicians", tags=["Technicians"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[TechnicianResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT T.*, R.id as role_id, R.role AS role FROM technicians T, technicians_roles R
        WHERE T.role_id = R.id;
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
                "role": {"id": row.role_id, "role": row.role},
            }
        )
    return data


@router.get("/{technician_id}", response_model=TechnicianResponse)
async def read_technician(db: db_dependency, technician_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM technicians
        WHERE id = :technician_id
    """
        ),
        {"technician_id": technician_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "name": result.name,
        "email": result.email,
        "phone": result.phone,
        "role_id": result.role_id,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_technician(db: db_dependency, tech_request: TechnicianCreate):
    tech_model = Technician(**tech_request.model_dump())

    db.add(tech_model)
    db.commit()
    db.refresh(tech_model)  # refresh to get generated fields like id
    return tech_model


@router.put("/update/{technician_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_technician(
    db: db_dependency,
    tech_request: TechnicianCreate,
    technician_id: int = Path(gt=0),
):

    tech_model = db.query(Technician).filter(Technician.id == technician_id).first()
    if tech_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    tech_model.name = tech_request.name
    tech_model.email = tech_request.email
    tech_model.phone = tech_request.phone
    tech_model.role_id = tech_request.role_id

    db.add(tech_model)
    db.commit()


@router.delete("/delete/{technician_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_technician(db: db_dependency, technician_id: int = Path(gt=0)):

    tech_model = db.query(Technician).filter(Technician.id == technician_id).first()
    if tech_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(Technician).filter(Technician.id == technician_id).delete()

    db.commit()
