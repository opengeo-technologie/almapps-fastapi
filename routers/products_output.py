from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import ProductOutput
from ..database import SessionLocal
from ..schemas import ProductOutputResponse, ProductOutputCreate
from typing import List


router = APIRouter(prefix="/products-outputs", tags=["Products Outputs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[ProductOutputResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT P.name AS product, PO.* 
        FROM products_outputs PO, products P
        WHERE PO.product_id = P.id;
    """
        )
    )
    data = []
    for row in result:
        data.append(
            {
                "id": row.id,
                "product_id": row.product_id,
                "user_id": row.user_id,
                "product": row.product,
                "quantity": row.quantity,
                "price": row.price,
                "date_output": row.date_output,
            }
        )
    return data


@router.get("/{product_output_id}", response_model=ProductOutputResponse)
async def read_product(db: db_dependency, product_output_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM products_outputs
        WHERE id = :product_output_id
    """
        ),
        {"product_output_id": product_output_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "product_id": result.product_id,
        "user_id": result.user_id,
        "quantity": result.quantity,
        "price": result.price,
        "date_output": result.date_output,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_product_output(
    db: db_dependency, product_output_request: ProductOutputCreate
):
    product_output_model = ProductOutput(**product_output_request.model_dump())

    db.add(product_output_model)
    db.commit()


@router.put("/product-output/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_product_output(
    db: db_dependency,
    product_output_request: ProductOutputCreate,
    product_output_id: int = Path(gt=0),
):

    product_output_model = (
        db.query(ProductOutput).filter(ProductOutput.id == product_output_id).first()
    )
    if product_output_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    product_output_model.product_id = product_output_request.product_id
    product_output_model.user_id = product_output_request.user_id
    product_output_model.quantity = product_output_request.quantity
    product_output_model.price = product_output_request.price
    product_output_model.date_output = product_output_request.date_output

    db.add(product_output_model)
    db.commit()


@router.delete("/product-input/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_output(db: db_dependency, product_output_id: int = Path(gt=0)):

    product_input_model = (
        db.query(ProductOutput).filter(ProductOutput.id == product_output_id).first()
    )
    if product_input_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(ProductOutput).filter(ProductOutput.id == product_output_id).delete()

    db.commit()
