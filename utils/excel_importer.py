import os
import zipfile
import tempfile
import numpy as np
import pandas as pd

from fastapi import HTTPException, UploadFile
from sqlalchemy import select, func


def import_excel_file(
    file: UploadFile,
    model,
    db,
    unique_field: str,  # e.g. "name"
    quantity_field: str,  # e.g. "quantity"
    required_columns: list[str],
):
    """
    Generic Excel importer for any PostGIS-enabled SQLAlchemy model.

    :param file: Excel file to upload .xlsx
    :param model: SQLAlchemy model class
    :param db: SQLAlchemy session
    :param field_mapping: dict mapping model_field -> file_field
                          Example: {"name": "REG_NAME", "code": "REG_CODE"}
    """

    # Validate extension
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files allowed")

    try:
        df = pd.read_excel(file.file)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Excel file")

    # Check required columns
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400, detail=f"Missing columns: {', '.join(missing)}"
        )

    objects = []
    inserted = 0
    updated = 0
    for _, row in df.iterrows():
        unique_value = row[unique_field]
        quantity_value = row[quantity_field]

        existing_obj = (
            db.query(model).filter(getattr(model, unique_field) == unique_value).first()
        )

        if existing_obj:
            # ✅ Update quantity only
            current_qty = getattr(existing_obj, quantity_field) or 0
            setattr(existing_obj, quantity_field, current_qty + int(quantity_value))
            updated += 1
        else:
            # ➕ Create new record
            obj_data = {col: row[col] for col in required_columns}
            db.add(model(**obj_data))
            inserted += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"inserted": inserted, "updated_quantity": updated}
