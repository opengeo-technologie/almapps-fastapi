from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import RoleTechnician
from ..database import SessionLocal
from ..schemas import TechnicianRoleResponse, TechnicianRoleCreate
from typing import List


router = APIRouter(prefix="/technicians_roles", tags=["Technicians Roles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[TechnicianRoleResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT * FROM technicians_roles;
    """
        )
    )
    data = []
    for row in result:
        data.append(
            {
                "id": row.id,
                "role": row.role,
            }
        )
    return data


@router.get("/{role_id}", response_model=TechnicianRoleResponse)
async def read_role(db: db_dependency, technician_role_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM technicians_roles
        WHERE id = :technician_role_id
    """
        ),
        {"technician_role_id": technician_role_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "role": result.role,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_role(db: db_dependency, role_request: TechnicianRoleCreate):
    role_model = RoleTechnician(**role_request.model_dump())

    db.add(role_model)
    db.commit()


@router.put("/update/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_role(
    db: db_dependency,
    role_request: TechnicianRoleCreate,
    technician_role_id: int = Path(gt=0),
):

    role_model = (
        db.query(RoleTechnician).filter(RoleTechnician.id == technician_role_id).first()
    )
    if role_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    role_model.role = role_request.role

    db.add(role_model)
    db.commit()


@router.delete("/delete/{role_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_role(db: db_dependency, technician_role_id: int = Path(gt=0)):

    role_model = (
        db.query(RoleTechnician).filter(RoleTechnician.id == technician_role_id).first()
    )
    if role_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(RoleTechnician).filter(RoleTechnician.id == technician_role_id).delete()

    db.commit()
