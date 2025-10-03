from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Job
from ..database import SessionLocal
from ..schemas import JobResponse, JobCreate
from typing import List


router = APIRouter(prefix="/jobs", tags=["Jobs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[JobResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT * FROM jobs;
    """
        )
    )
    data = []
    for row in result:
        data.append(
            {
                "id": row.id,
                "job_name": row.job_name,
                "job_description": row.job_description,
                "duration": row.duration,
                "price": row.price,
                "date_program": row.date_program,
            }
        )
    return data


@router.get("/{job_id}", response_model=JobResponse)
async def read_job(db: db_dependency, job_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM jobs
        WHERE id = :job_id
    """
        ),
        {"job_id": job_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "job_name": result.job_name,
        "job_description": result.job_description,
        "duration": result.duration,
        "price": result.price,
        "date_program": result.date_program,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_job(db: db_dependency, job_request: JobCreate):
    job_model = Job(**job_request.model_dump())

    db.add(job_model)
    db.commit()
    db.refresh(job_model)  # refresh to get generated fields like id
    return job_model


@router.put("/update/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_job(
    db: db_dependency,
    job_request: JobCreate,
    job_id: int = Path(gt=0),
):

    job_model = db.query(Job).filter(Job.id == job_id).first()
    if job_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    job_model.job_name = job_request.job_name
    job_model.job_description = job_request.job_description
    job_model.duration = job_request.duration
    job_model.price = job_request.price

    db.add(job_model)
    db.commit()


@router.delete("/delete/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    db_model = db.query(Job).filter(Job.id == job_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_model)
    db.commit()
    return {"ok": True, "message": "Data deleted"}
