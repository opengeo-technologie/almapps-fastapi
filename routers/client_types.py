from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import ClientType
from ..database import SessionLocal
from ..schemas import ClientTypeResponse, ClientTypeCreate
from typing import List


router = APIRouter(prefix="/client-types", tags=["Client types"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[ClientTypeResponse])
async def read_all(db: db_dependency):
    return db.query(ClientType).all()


@router.get("/{client_type_id}", response_model=ClientTypeResponse)
async def read_client_type(db: db_dependency, client_type_id: int = Path(gt=0)):
    db_client_type = (
        db.query(ClientType).filter(ClientType.id == client_type_id).first()
    )
    if not db_client_type:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_client_type


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_client_type(db: db_dependency, client_type_request: ClientTypeCreate):
    client_type_model = ClientType(**client_type_request.model_dump())

    db.add(client_type_model)
    db.commit()


@router.put("/client_type/{client_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_client_type(
    db: db_dependency,
    client_type_request: ClientTypeCreate,
    client_type_id: int = Path(gt=0),
):

    client_type_model = (
        db.query(ClientType).filter(ClientType.id == client_type_id).first()
    )
    if client_type_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    client_type_model.type = client_type_request.type

    db.add(client_type_model)
    db.commit()


@router.delete("/client_type/{client_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_type(db: db_dependency, client_type_id: int = Path(gt=0)):

    client_type_model = (
        db.query(ClientType).filter(ClientType.id == client_type_id).first()
    )
    if client_type_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(ClientType).filter(ClientType.id == client_type_id).delete()

    db.commit()
