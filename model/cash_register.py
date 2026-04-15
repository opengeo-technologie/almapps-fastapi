from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, event
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import date
from ..database import Base


class CashRegister(Base):
    __tablename__ = "cash_registers"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today, unique=True, index=True)
    opening_balance = Column(Float, nullable=False)
    closing_balance = Column(Float)
    status = Column(String(20), default="open")  # open / closed
    linked_to_previous = Column(Integer, default=0)  # 1 if linked, 0 if manual
    previous_register_id = Column(
        Integer, ForeignKey("cash_registers.id"), nullable=True
    )
    opened_by = Column(Integer, ForeignKey("users.id"))
    closed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    transactions = relationship(
        "Transaction", back_populates="cash", cascade="all, delete-orphan"
    )

    # Self-referential relationship for linking registers
    previous_register = relationship(
        "CashRegister", remote_side=[id], foreign_keys=[previous_register_id]
    )

    # User relationships
    opener = relationship("User", foreign_keys=[opened_by])
    closer = relationship("User", foreign_keys=[closed_by])

    @property
    def total_income(self):
        return sum(t.amount for t in self.transactions if t.type == "in")

    @property
    def total_expenses(self):
        return sum(t.amount for t in self.transactions if t.type == "out")

    @property
    def expected_closing(self):
        return self.opening_balance + self.total_income - self.total_expenses

    @property
    def difference(self):
        if self.closing_balance is None:
            return None
        return self.closing_balance - self.expected_closing

    def __repr__(self):
        return f"<CashRegister {self.date} - {self.status}>"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(10), nullable=False)  # 'in' or 'out'
    amount = Column(Float, nullable=False)
    category = Column(String(100))  # Sales, Tips, Supplies, Utilities, etc.
    description = Column(String(255))
    date = Column(Date, default=date.today, index=True)
    cash_id = Column(Integer, ForeignKey("cash_registers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    cash = relationship("CashRegister", back_populates="transactions")
    user = relationship("User", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.type} ${self.amount} - {self.category}>"


# ==================== CASCADE UPDATE EVENT LISTENER ====================


@event.listens_for(CashRegister.closing_balance, "set")
def receive_closing_balance_update(target, value, oldvalue, initiator):
    """
    Event listener that triggers CASCADE UPDATE when a closing balance is modified.

    When a CashRegister's closing_balance is updated:
    1. Find any register that links to this one (next day's register)
    2. Update that register's opening_balance to match the new closing
    3. Recursively update the chain
    """
    # Skip if value hasn't actually changed or is being set for first time
    if oldvalue == value or oldvalue is None:
        return

    # Skip if we're in the middle of a session flush (prevents recursion issues)
    if not hasattr(target, "__dict__"):
        return

    session = Session.object_session(target)
    if session is None:
        return

    # Find the next register (if any) that links to this one
    next_register = (
        session.query(CashRegister)
        .filter(
            CashRegister.previous_register_id == target.id,
            CashRegister.linked_to_previous == 1,
        )
        .first()
    )

    if next_register:
        # Update the next register's opening balance
        next_register.opening_balance = value

        # If the next register is closed, recalculate and potentially cascade further
        if (
            next_register.status == "closed"
            and next_register.closing_balance is not None
        ):
            # The closing stays the same, but we need to check if there's another register after it
            next_next_register = (
                session.query(CashRegister)
                .filter(
                    CashRegister.previous_register_id == next_register.id,
                    CashRegister.linked_to_previous == 1,
                )
                .first()
            )

            if next_next_register:
                # Cascade continues: next register's closing becomes the opening of the next-next
                next_next_register.opening_balance = next_register.closing_balance


def cascade_update_opening_balances(
    session: Session, register_id: int, new_closing: float
):
    """
    Manually trigger cascade update through the register chain.

    This function updates all linked registers' opening balances when a
    previous register's closing balance is modified.

    Args:
        session: SQLAlchemy session
        register_id: ID of the register whose closing was changed
        new_closing: The new closing balance value

    Returns:
        List of updated register IDs
    """
    updated_registers = []
    current_closing = new_closing
    current_register_id = register_id

    while True:
        # Find the next register linked to current one
        next_register = (
            session.query(CashRegister)
            .filter(
                CashRegister.previous_register_id == current_register_id,
                CashRegister.linked_to_previous == 1,
            )
            .first()
        )

        if not next_register:
            break

        # Update opening balance
        old_opening = next_register.opening_balance
        next_register.opening_balance = current_closing
        updated_registers.append(
            {
                "register_id": next_register.id,
                "date": next_register.date,
                "old_opening": old_opening,
                "new_opening": current_closing,
            }
        )

        # If this register is closed, its closing becomes the next opening
        if (
            next_register.status == "closed"
            and next_register.closing_balance is not None
        ):
            current_closing = next_register.closing_balance
            current_register_id = next_register.id
        else:
            # Chain stops at open register
            break

    session.commit()
    return updated_registers
