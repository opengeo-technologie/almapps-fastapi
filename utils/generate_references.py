from typing import Annotated
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import extract
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import PurchaseOrder, Quotation, Invoice, Payment, Expense
from ..database import SessionLocal


router = APIRouter(prefix="/generate-code", tags=["Generate Code"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def get_next_reference(db: db_dependency):
    current_year = datetime.now().year

    # Récupérer la dernière commande de l'année courante
    last_order = (
        db.query(PurchaseOrder)
        .filter(extract("year", PurchaseOrder.date_op) == current_year)
        .order_by(PurchaseOrder.id.desc())
        .first()
    )

    if not last_order:
        # Première commande de l'année
        next_ref = f"PO-{current_year}-001"
    else:
        parts = last_order.reference.split("-")
        if len(parts) == 3 and parts[2].isdigit():
            next_number = int(parts[2]) + 1
            next_ref = f"PO-{current_year}-{next_number:03d}"
        else:
            # Fallback si le format n’est pas reconnu
            next_ref = f"PO-{current_year}-001"

    return next_ref


def get_next_reference_pro(db: db_dependency):
    current_year = datetime.now().year

    # Récupérer la dernière commande de l'année courante
    last_order = (
        db.query(Quotation)
        .filter(extract("year", Quotation.date_op) == current_year)
        .order_by(Quotation.id.desc())
        .first()
    )

    if not last_order:
        # Première commande de l'année
        next_ref = f"PRO-{current_year}-001"
    else:
        parts = last_order.reference.split("-")
        if len(parts) == 3 and parts[2].isdigit():
            next_number = int(parts[2]) + 1
            next_ref = f"PRO-{current_year}-{next_number:03d}"
        else:
            # Fallback si le format n’est pas reconnu
            next_ref = f"PRO-{current_year}-001"

    return next_ref


def get_next_reference_invoice(db: db_dependency):
    current_year = datetime.now().year

    # Récupérer la dernière commande de l'année courante
    last_order = (
        db.query(Invoice)
        .filter(extract("year", Invoice.date_op) == current_year)
        .order_by(Invoice.id.desc())
        .first()
    )

    if not last_order:
        # Première commande de l'année
        next_ref = f"INV-{current_year}-001"
    else:
        parts = last_order.reference.split("-")
        if len(parts) == 3 and parts[2].isdigit():
            next_number = int(parts[2]) + 1
            next_ref = f"INV-{current_year}-{next_number:03d}"
        else:
            # Fallback si le format n’est pas reconnu
            next_ref = f"INV-{current_year}-001"

    return next_ref


def get_next_reference_payment(db: db_dependency):
    current_year = datetime.now().year

    # Récupérer la dernière commande de l'année courante
    last_order = (
        db.query(Payment)
        .filter(extract("year", Payment.date_op) == current_year)
        .order_by(Payment.id.desc())
        .first()
    )

    if not last_order:
        # Première commande de l'année
        next_ref = f"REF-{current_year}-001"
    else:
        parts = last_order.reference.split("-")
        if len(parts) == 3 and parts[2].isdigit():
            next_number = int(parts[2]) + 1
            next_ref = f"REF-{current_year}-{next_number:03d}"
        else:
            # Fallback si le format n’est pas reconnu
            next_ref = f"REF-{current_year}-001"

    return next_ref


def get_expense_reference(db: db_dependency):
    current_year = datetime.now().year

    # Récupérer la dernière commande de l'année courante
    last_order = (
        db.query(Expense)
        .filter(extract("year", Expense.date) == current_year)
        .order_by(Expense.id.desc())
        .first()
    )

    if not last_order:
        # Première commande de l'année
        next_ref = f"EXP-{current_year}-001"
    else:
        parts = last_order.reference.split("-")
        if len(parts) == 3 and parts[2].isdigit():
            next_number = int(parts[2]) + 1
            next_ref = f"EXP-{current_year}-{next_number:03d}"
        else:
            # Fallback si le format n’est pas reconnu
            next_ref = f"EXP-{current_year}-001"

    return next_ref
