from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Tool, ToolOutput, ToolReturn
from ..database import SessionLocal
from ..schemas import (
    ToolReturnCreate,
    ToolReturnResponse,
)
from typing import List


router = APIRouter(prefix="/tools-return", tags=["Tools Return management"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[ToolReturnResponse])
async def read_all(db: db_dependency):
    return db.query(ToolReturn).all()


@router.get("/{tool_id}", response_model=ToolReturnResponse)
async def read_tool(db: db_dependency, tool_id: int = Path(gt=0)):
    db_model = db.query(ToolReturn).filter(ToolReturn.id == tool_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Data not found")
    return db_model


@router.post(
    "/create", response_model=ToolReturnResponse, status_code=status.HTTP_201_CREATED
)
async def create_tool(db: db_dependency, tool_request: ToolReturnCreate):
    db_model = ToolReturn(**tool_request.model_dump())

    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.put(
    "/update/{tool_id}",
    response_model=ToolReturnResponse,
    status_code=status.HTTP_206_PARTIAL_CONTENT,
)
async def update_tool(
    db: db_dependency,
    tool_request: ToolReturnCreate,
    tool_id: int = Path(gt=0),
):

    db_model = db.query(ToolReturn).filter(ToolReturn.id == tool_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Data not found")

    update_data = tool_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_model, key, value)

    db.commit()
    db.refresh(db_model)
    return db_model


@router.delete("/delete/{tool_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_tool(db: db_dependency, tool_id: int = Path(gt=0)):

    db_model = db.query(ToolReturn).filter(ToolOutput.id == tool_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Data not found")

    db.delete(db_model)
    db.commit()
    return {"ok": True, "message": "Data deleted"}
