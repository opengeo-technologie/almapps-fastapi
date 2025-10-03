from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import User
from ..database import SessionLocal
from ..schemas import UserCreate, UserResponse, UserUpdate, UserPasswordReset
import profile
from typing import List
from passlib.context import CryptContext


router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/", response_model=List[UserResponse])
async def read_all(db: db_dependency):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(db: db_dependency, user_id: int = Path(gt=0)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_user


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserCreate):
    create_user_model = User(
        email=user_request.email,
        username=user_request.username,
        profile_id=user_request.profile_id,
        password=bcrypt_context.hash(user_request.password),
        is_active=True,
    )
    # create_user_model = User(**user_request.model_dump())

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    return create_user_model


@router.put("/password/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    db: db_dependency,
    user_verification: UserPasswordReset,
    user_id: int = Path(gt=0),
):
    user_model = db.query(User).filter(User.id == user_id).first()

    # if not bcrypt_context.verify(
    #     user_verification.password, user_model.hashed_password
    # ):
    #     raise HTTPException(status_code=401, detail="Error on password change")
    user_model.password = bcrypt_context.hash(user_verification.password)
    db.add(user_model)
    db.commit()
    db.refresh(user_model)


@router.put("/update/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
    db: db_dependency,
    user_request: UserUpdate,
    user_id: int = Path(gt=0),
):

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Data not found")

    update_data = user_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user_id: int = Path(gt=0)):

    user_model = db.query(User).filter(User.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(User).filter(User.id == user_id).delete()

    db.commit()
