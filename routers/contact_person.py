from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import ContactPerson
from ..database import SessionLocal
from ..schemas import ContactPersonResponse, ContactPersonCreate
from typing import List


router = APIRouter(prefix="/contact-person", tags=["Client Contact"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[ContactPersonResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT * FROM client_contact_person;
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
                "client_id": row.client_id,
            }
        )
    return data


@router.get("/{contact_id}", response_model=ContactPersonResponse)
async def read_client_contact(db: db_dependency, contact_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM client_contact_person
        WHERE id = :contact_id
    """
        ),
        {"contact_id": contact_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "name": result.name,
        "email": result.email,
        "phone": result.phone,
        "client_id": result.client_id,
    }


@router.get("/client/{client_id}", response_model=ContactPersonResponse)
async def read_client_contact(db: db_dependency, client_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM client_contact_person
        WHERE client_id = :client_id
    """
        ),
        {"client_id": client_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "name": result.name,
        "email": result.email,
        "phone": result.phone,
        "client_id": result.client_id,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_client_contact(
    db: db_dependency, contact_request: ContactPersonCreate
):
    contact_model = ContactPerson(**contact_request.model_dump())

    db.add(contact_model)
    db.commit()


@router.put("/update/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_client_contact(
    db: db_dependency,
    contact_request: ContactPersonCreate,
    contact_id: int = Path(gt=0),
):

    contact_model = (
        db.query(ContactPerson).filter(ContactPerson.id == contact_id).first()
    )
    if contact_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    contact_model.name = contact_request.name
    contact_model.email = contact_request.email
    contact_model.phone = contact_request.phone
    contact_model.client_id = contact_request.client_id

    db.add(contact_model)
    db.commit()


@router.delete("/delete/{contact_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_client_contact(db: db_dependency, contact_id: int = Path(gt=0)):

    contact_model = (
        db.query(ContactPerson).filter(ContactPerson.id == contact_id).first()
    )
    if contact_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(ContactPerson).filter(ContactPerson.id == contact_id).delete()

    db.commit()
