from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Product
from ..database import SessionLocal
from ..schemas import ProductResponse, ProductCreate
from typing import List


router = APIRouter(prefix="/products", tags=["Products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=List[ProductResponse])
async def read_all(db: db_dependency):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT * FROM products;
    """
        )
    )
    data = []
    for row in result:
        data.append(
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "unit": row.unit,
                "stock_security_level": row.stock_security_level,
            }
        )
    return data


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(db: db_dependency, product_id: int = Path(gt=0)):
    # Query parcels with geometry as GeoJSON
    result = db.execute(
        text(
            """
        SELECT *
        FROM products
        WHERE id = :product_id
    """
        ),
        {"product_id": product_id},
    ).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Data not found")

    return {
        "id": result.id,
        "name": result.name,
        "description": result.description,
        "unit": result.unit,
        "stock_security_level": result.stock_security_level,
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_product(db: db_dependency, product_request: ProductCreate):
    product_model = Product(**product_request.model_dump())

    db.add(product_model)
    db.commit()
    db.refresh(product_model)  # refresh to get generated fields like id
    return product_model


@router.put("/update/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_product(
    db: db_dependency,
    product_request: ProductCreate,
    product_id: int = Path(gt=0),
):

    product_model = db.query(Product).filter(Product.id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    product_model.name = product_request.name
    product_model.description = product_request.description
    product_model.unit = product_request.unit
    product_model.stock_security_level = product_request.stock_security_level

    db.add(product_model)
    db.commit()


@router.delete("/delete/{product_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_product(db: db_dependency, product_id: int = Path(gt=0)):

    product_model = db.query(Product).filter(Product.id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail="Data not found.")

    db.query(Product).filter(Product.id == product_id).delete()

    db.commit()
