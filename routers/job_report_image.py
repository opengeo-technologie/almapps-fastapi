import os
import shutil
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path, UploadFile, File
from starlette import status
from ..models import JobReportImage
from ..database import SessionLocal
from ..schemas import JobReportImageResponse, JobReportImageCreate
from typing import List


router = APIRouter(prefix="/jobs-report-image", tags=["Jobs Report Image"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[JobReportImageResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT * FROM jobs_reports_images;
    """
        )
    )
    data = []
    for row in result:
        data.append(
            {
                "id": row.id,
                "job_report_id": row.job_report_id,
                "file_path": row.file_path,
            }
        )
    return data


@router.get("/{job_report_image_id}", response_model=JobReportImageResponse)
async def read_job_report_image(
    db: db_dependency, job_report_image_id: int = Path(gt=0)
):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM jobs_reports_images
        WHERE id = :job_report_image_id
    """
        ),
        {"job_report_image_id": job_report_image_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "job_report_id": result.job_id,
        "file_path": result.technician_id,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_job_report_image(
    db: db_dependency, job_report_id: str, file: UploadFile = File()
):
    UPLOAD_DIR = "backend1/uploads/reports/images"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    UPLOAD_PATH = "uploads/reports/images"
    file_location = f"{UPLOAD_PATH}/{file.filename}"

    # Save the uploaded image
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job_report_model = JobReportImage(
        job_report_id=job_report_id, file_path=file_location
    )
    db.add(job_report_model)
    db.commit()
    db.refresh(job_report_model)  # refresh to get generated fields like id
    return job_report_model


# @router.put("/update/{job_report_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def update_job_report(
#     db: db_dependency,
#     job_report_image_request: JobReportImageCreate,
#     file: UploadFile,
#     job_report_id: int = Path(gt=0),
# ):

#     job_report_model = db.query(JobReport).filter(JobReport.id == job_report_id).first()
#     if job_report_model is None:
#         raise HTTPException(status_code=404, detail="Data not found.")

#     job_report_model.job_id = job_report_request.job_id
#     job_report_model.technician_id = job_report_request.technician_id
#     job_report_model.report_heading = job_report_request.report_heading
#     job_report_model.report_description = job_report_request.report_description

#     db.add(job_report_model)
#     db.commit()


# @router.delete("/delete/{job_report_id}", status_code=status.HTTP_202_ACCEPTED)
# async def delete_job_report(db: db_dependency, job_report_id: int = Path(gt=0)):

#     job_report_model = db.query(JobReport).filter(JobReport.id == job_report_id).first()
#     if job_report_model is None:
#         raise HTTPException(status_code=404, detail="Data not found.")

#     db.query(JobReport).filter(JobReport.id == job_report_id).delete()

#     db.commit()
