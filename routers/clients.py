from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Client
from ..database import SessionLocal
from ..schemas import ClientResponse, ClientCreate
from typing import List


router = APIRouter(prefix="/clients", tags=["Clients"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[ClientResponse])
async def read_all(db: db_dependency):
    return db.query(Client).all()


@router.get("/{client_id}", response_model=ClientResponse)
async def read_client(db: db_dependency, client_id: int = Path(gt=0)):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_client


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_client(db: db_dependency, client_request: ClientCreate):
    client_model = Client(**client_request.model_dump())

    db.add(client_model)
    db.commit()

    db.refresh(client_model)  # refresh to get generated fields like id
    return client_model


@router.put("/update/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_client(
    db: db_dependency,
    client_request: ClientCreate,
    client_id: int = Path(gt=0),
):

    client_model = db.query(Client).filter(Client.id == client_id).first()
    if client_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    client_model.name = client_request.name
    client_model.email = client_request.email
    client_model.address = client_request.address
    client_model.phone = client_request.phone
    client_model.postal = client_request.postal
    client_model.nui = client_request.nui
    client_model.rc = client_request.rc
    client_model.type_id = client_request.type_id

    db.add(client_model)
    db.commit()

    db.refresh(client_model)  # refresh to get generated fields like id
    return client_model


@router.delete("/delete/{client_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_client(db: db_dependency, client_id: int = Path(gt=0)):

    client_model = db.query(Client).filter(Client.id == client_id).first()
    if client_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(Client).filter(Client.id == client_id).delete()

    db.commit()
