from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import JobReport
from ..database import SessionLocal
from ..schemas import JobReportResponse, JobReportCreate
from typing import List


router = APIRouter(prefix="/jobs-report", tags=["Jobs Report"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[JobReportResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT * FROM jobs_reports;
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
                "report_heading": row.report_heading,
                "report_description": row.report_description,
            }
        )
    return data


@router.get("/{job_report_id}", response_model=JobReportResponse)
async def read_job_report(db: db_dependency, job_report_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM jobs_reports
        WHERE id = :job_report_id
    """
        ),
        {"job_report_id": job_report_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "job_id": result.job_id,
        "technician_id": result.technician_id,
        "report_heading": result.report_heading,
        "report_description": result.report_description,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_job_report(db: db_dependency, job_report_request: JobReportCreate):
    job_report_model = JobReport(**job_report_request.model_dump())

    db.add(job_report_model)
    db.commit()
    db.refresh(job_report_model)  # refresh to get generated fields like id
    return job_report_model


@router.put("/update/{job_report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_job_report(
    db: db_dependency,
    job_report_request: JobReportCreate,
    job_report_id: int = Path(gt=0),
):

    job_report_model = db.query(JobReport).filter(JobReport.id == job_report_id).first()
    if job_report_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    job_report_model.job_id = job_report_request.job_id
    job_report_model.technician_id = job_report_request.technician_id
    job_report_model.report_heading = job_report_request.report_heading
    job_report_model.report_description = job_report_request.report_description

    db.add(job_report_model)
    db.commit()


@router.delete("/delete/{job_report_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_job_report(db: db_dependency, job_report_id: int = Path(gt=0)):

    job_report_model = db.query(JobReport).filter(JobReport.id == job_report_id).first()
    if job_report_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(JobReport).filter(JobReport.id == job_report_id).delete()

    db.commit()
