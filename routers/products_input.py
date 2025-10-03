from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import ProductInput
from ..database import SessionLocal
from ..schemas import ProductInputResponse, ProductInputCreate
from typing import List


router = APIRouter(prefix="/products-input", tags=["Products Inputs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[ProductInputResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT P.name AS product, V.name AS vendor, PI.* 
        FROM products_inputs PI, products P, vendors V
        WHERE PI.product_id = P.id
        AND PI.vendor_id = V.id;
    """
        )
    )
    data = []
    for row in result:
        data.append(
            {
                "id": row.id,
                "product_id": row.product_id,
                "vendor_id": row.vendor_id,
                "product": row.product,
                "vendor": row.vendor,
                "user_id": row.user_id,
                "quantity": row.quantity,
                "price": row.price,
                "date_input": row.date_input,
            }
        )
    return data


@router.get("/{product_id}", response_model=ProductInputResponse)
async def read_product(db: db_dependency, product_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM products_inputs
        WHERE id = :product_id
    """
        ),
        {"product_id": product_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "product_id": result.product_id,
        "vendor_id": result.vendor_id,
        "user_id": result.user_id,
        "quantity": result.quantity,
        "price": result.price,
        "date_input": result.date_input,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_product_input(
    db: db_dependency, product_input_request: ProductInputCreate
):
    product_input_model = ProductInput(**product_input_request.model_dump())

    db.add(product_input_model)
    db.commit()


@router.put("/update/{product_input_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_product_input(
    db: db_dependency,
    product_input_request: ProductInputCreate,
    product_input_id: int = Path(gt=0),
):

    product_input_model = (
        db.query(ProductInput).filter(ProductInput.id == product_input_id).first()
    )
    if product_input_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    product_input_model.product_id = product_input_request.product_id
    product_input_model.vendor_id = product_input_request.vendor_id
    product_input_model.user_id = product_input_request.user_id
    product_input_model.quantity = product_input_request.quantity
    product_input_model.price = product_input_request.price
    product_input_model.date_input = product_input_request.date_input

    db.add(product_input_model)
    db.commit()


@router.delete("/delete/{product_input_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_product_input(db: db_dependency, product_input_id: int = Path(gt=0)):

    product_input_model = (
        db.query(ProductInput).filter(ProductInput.id == product_input_id).first()
    )
    if product_input_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(ProductInput).filter(ProductInput.id == product_input_id).delete()

    db.commit()
