from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import JobAssign
from ..database import SessionLocal
from ..schemas import JobAssignResponse, JobAssignCreate, TechnicianResponse
from typing import List


router = APIRouter(prefix="/jobs_assign", tags=["Jobs Assign"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[JobAssignResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT * FROM jobs_assigns;
    """
        )
    )
    data = []
    for row in result:
        data.append(
            {
                "id": row.id,
                "job_id": row.job_id,
                "technician_id": row.technician_id,
                "date_start": row.date_start,
                "date_end": row.date_end,
            }
        )
    return data


@router.get("/{job_assign_id}", response_model=JobAssignResponse)
async def read_job(db: db_dependency, job_assign_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM jobs_assigns
        WHERE id = :job_assign_id
    """
        ),
        {"job_assign_id": job_assign_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "job_id": result.job_id,
        "technician_id": result.technician_id,
        "date_start": result.date_start,
        "date_end": result.date_end,
    }


@router.get("/technicians/{job_id}", response_model=List[TechnicianResponse])
async def read_technicians_assign_job(db: db_dependency, job_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT T.*, R.id as role_id, R.role AS role
        FROM jobs_assigns J, technicians T, technicians_roles R
        WHERE J.technician_id = T.id
        AND T.role_id = R.id
        AND job_id = :job_id
    """
        ),
        {"job_id": job_id},
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


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_job_assign(db: db_dependency, job_assign_request: JobAssignCreate):
    job_assign_model = JobAssign(**job_assign_request.model_dump())

    db.add(job_assign_model)
    db.commit()
    db.refresh(job_assign_model)  # refresh to get generated fields like id
    return job_assign_model


@router.put("/update/{job_assign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_job_assign(
    db: db_dependency,
    job_assign_request: JobAssignCreate,
    job_assign_id: int = Path(gt=0),
):

    job_assign_model = db.query(JobAssign).filter(JobAssign.id == job_assign_id).first()
    if job_assign_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    job_assign_model.job_id = job_assign_request.job_id
    job_assign_model.technician_id = job_assign_request.technician_id
    job_assign_model.date_start = job_assign_request.date_start
    job_assign_model.date_end = job_assign_request.date_end

    db.add(job_assign_model)
    db.commit()


@router.delete("/delete/{job_id}/{technician_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_job_assign(
    db: db_dependency, job_id: int = Path(gt=0), technician_id: int = Path(gt=0)
):

    job_assign_model = (
        db.query(JobAssign)
        .filter(JobAssign.job_id == job_id)
        .filter(JobAssign.technician_id == technician_id)
        .first()
    )
    if job_assign_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(JobAssign).filter(JobAssign.job_id == job_id).filter(
        JobAssign.technician_id == technician_id
    ).delete()

    db.commit()
