from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import PurchaseOrder
from ..database import SessionLocal
from ..schemas import (
    PurchaseOrderResponse,
    PurchaseOrderCreate,
    PurchaseOrderUpdate,
)
from typing import List
from ..utils.generate_references import get_next_reference


router = APIRouter(prefix="/purchase_orders", tags=["Purchase Orders"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Read all
@router.get("/", response_model=List[PurchaseOrderResponse])
def get_purchase_orders(db: Session = Depends(get_db)):
    return db.query(PurchaseOrder).all()


# Read by ID
@router.get(
    "/{po_id}", response_model=PurchaseOrderResponse, status_code=status.HTTP_200_OK
)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    db_po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not db_po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return db_po


# Create
@router.post(
    "/create", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED
)
def create_purchase_order(po: PurchaseOrderCreate, db: db_dependency):
    # db_po = PurchaseOrder(**po.model_dump())

    # ✅ Generate reference
    ref = get_next_reference(db)

    # ✅ Update schema value directly
    updated_data = po.model_copy(update={"reference": ref})
    # print(updated_order.model_dump())
    query = PurchaseOrder(**updated_data.model_dump())
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


# Update
@router.put(
    "/update/{po_id}",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_206_PARTIAL_CONTENT,
)
def update_purchase_order(po_id: int, po: PurchaseOrderUpdate, db: db_dependency):
    db_po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not db_po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    for key, value in po.model_dump(exclude_unset=True).items():
        setattr(db_po, key, value)

    db.commit()
    db.refresh(db_po)
    return db_po


# Delete
@router.delete("/delete/{po_id}")
def delete_purchase_order(po_id: int, db: Session = Depends(get_db)):
    db_po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not db_po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    db.delete(db_po)
    db.commit()
    return {"detail": "Purchase order deleted"}
