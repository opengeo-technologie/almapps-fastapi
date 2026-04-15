from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import date, datetime


# ==================== Transaction Schemas ====================


class TransactionBase(BaseModel):
    type: Literal["in", "out"]
    amount: float = Field(gt=0)
    category: Optional[str] = None
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    date: date


class TransactionResponse(TransactionBase):
    id: int
    date: date
    cash_id: int
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


# ==================== Cash Register Schemas ====================


class CashRegisterBase(BaseModel):
    date: date
    opening_balance: float = Field(ge=0)


class CashRegisterOpen(BaseModel):
    opening_balance: Optional[float] = Field(
        None, ge=0, description="Manual opening balance"
    )
    link_to_previous: bool = Field(False, description="Link to previous day's closing?")
    register_date: Optional[date] = Field(
        None, description="Date for the register (defaults to today)"
    )


class CashRegisterClose(BaseModel):
    closing_balance: float = Field(ge=0)


class UpdateClosingBalance(BaseModel):
    register_id: int
    new_closing_balance: float = Field(ge=0)


class CashRegisterResponse(BaseModel):
    id: int
    date: date
    opening_balance: float
    closing_balance: Optional[float]
    status: str
    linked_to_previous: int
    previous_register_id: Optional[int]
    opened_by: Optional[int]
    closed_by: Optional[int]

    class Config:
        from_attributes = True


class CashRegisterDetail(CashRegisterResponse):
    total_income: float
    total_expenses: float
    expected_closing: float
    difference: Optional[float]
    transactions: List[TransactionResponse] = []

    class Config:
        from_attributes = True


# ==================== Response Schemas ====================


class CloseRegisterResponse(BaseModel):
    message: str
    register_id: int
    date: date
    opening_balance: float
    closing_balance: float
    total_income: float
    total_expenses: float
    expected_closing: float
    difference: float
    status: str


class CascadeUpdateResponse(BaseModel):
    message: str
    register_id: int
    old_closing: float
    new_closing: float
    cascade_updates: List[dict]
    cascade_count: int


class ChainItem(BaseModel):
    register_id: int
    date: date
    opening_balance: float
    closing_balance: Optional[float] = None
    expected_closing: float = None
    difference: Optional[float] = None
    status: str
    linked_to_previous: bool
    previous_register_id: Optional[int] = None


class RegisterChainResponse(BaseModel):
    total_registers: int
    chain: List[ChainItem]
    chain_integrity: bool
