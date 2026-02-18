import os
import zipfile
import tempfile
import numpy as np
import pandas as pd

from fastapi import HTTPException, UploadFile
from sqlalchemy import select, func


def clean_string(value):
    """Trim spaces if value is a string"""
    if isinstance(value, str):
        return value.strip()
    return value


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

    # Clean unique field
    df[unique_field] = df[unique_field].apply(clean_string)

    # Check required columns
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400, detail=f"Missing columns: {', '.join(missing)}"
        )

    # If there are other columns (like price), we keep the first occurrence
    grouped_df = df.groupby(unique_field, as_index=False).agg(
        {
            quantity_field: "sum",
            **{
                col: "first"
                for col in df.columns
                if col not in [unique_field, quantity_field]
            },
        }
    )

    inserted = 0
    updated = 0
    for _, row in grouped_df.iterrows():
        unique_value = clean_string(row[unique_field])
        quantity_value = int(row[quantity_field] or 0)

        existing_obj = (
            db.query(model)
            .filter(
                func.trim(func.lower(getattr(model, unique_field)))
                == unique_value.lower()
            )
            .first()
        )

        if existing_obj:
            current_qty = getattr(existing_obj, quantity_field) or 0
            setattr(existing_obj, quantity_field, current_qty + quantity_value)
            updated += 1
        else:
            obj_data = {}
            for col in required_columns:
                value = row[col]
                if col == unique_field:
                    value = clean_string(value)
                obj_data[col] = value

            db.add(model(**obj_data))
            inserted += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"inserted": inserted, "updated_quantity": updated}
