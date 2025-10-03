from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Profile
from ..database import SessionLocal
from ..schemas import ProfileResponse, ProfileCreate
from typing import List


router = APIRouter(prefix="/profiles", tags=["Profiles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[ProfileResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT * FROM profiles;
    """
        )
    )
    data = []
    for row in result:
        data.append(
            {
                "id": row.id,
                "name": row.name,
            }
        )
    return data


@router.get("/{profile_id}", response_model=ProfileResponse)
async def read_profile(db: db_dependency, profile_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM profiles
        WHERE id = :profile_id
    """
        ),
        {"profile_id": profile_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "name": result.name,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_profile(db: db_dependency, profile_request: ProfileCreate):
    profile_model = Profile(**profile_request.model_dump())

    db.add(profile_model)
    db.commit()


@router.put("/profile/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_profile(
    db: db_dependency,
    profile_request: ProfileCreate,
    profile_id: int = Path(gt=0),
):

    profile_model = db.query(Profile).filter(Profile.id == profile_id).first()
    if profile_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")

    profile_model.name = profile_request.name

    db.add(profile_model)
    db.commit()


@router.delete("/profile/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(db: db_dependency, profile_id: int = Path(gt=0)):

    profile_model = db.query(Profile).filter(Profile.id == profile_id).first()
    if profile_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")

    db.query(Profile).filter(Profile.id == profile_id).delete()

    db.commit()
