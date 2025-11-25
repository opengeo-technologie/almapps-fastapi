from .database import Base
import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from datetime import date
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Boolean,
    Date,
    Float,
)


# User profile model (SuperAdmin, Admin, Accountant, Manager, Technician, cashier, stock manager )
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    users = relationship("User", back_populates="profile")


#  Users saving model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    profile = relationship("Profile", back_populates="users")
    invoices = relationship("Invoice", back_populates="user")
    purchase_orders = relationship("PurchaseOrder", back_populates="user")
    quotations = relationship("Quotation", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    tool_output = relationship("ToolOutput", back_populates="user")
    tool_return = relationship("ToolReturn", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    expense = relationship("Expense", back_populates="user")


# Client's type model (Personal, Company)
class ClientType(Base):
    __tablename__ = "clients_types"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(255), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    client = relationship("Client", back_populates="type")


# Client's saving model
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    postal = Column(String(255), nullable=True)
    nui = Column(String(255), nullable=True)
    rc = Column(String(255), nullable=True)
    type_id = Column(Integer, ForeignKey("clients_types.id"))
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    type = relationship("ClientType", back_populates="client")
    quotations = relationship("Quotation", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")
    contact = relationship("ContactPerson", back_populates="client")


# Contact person model if client is company
class ContactPerson(Base):
    __tablename__ = "client_contact_person"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"))
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    client = relationship("Client", back_populates="contact")


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    unit = Column(String(255), nullable=True)
    stock_security_level = Column(Float, nullable=True, default=0.0)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    order_products = relationship("PurchaseOrderProduct", back_populates="product")
    quotation_products = relationship("QuotationProduct", back_populates="product")
    invoice_products = relationship("InvoiceProduct", back_populates="product")
    product_inputs = relationship("ProductInput", back_populates="product")


class ProductInput(Base):
    __tablename__ = "products_inputs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Float, nullable=False, default=0.0)
    price = Column(Float, nullable=False, default=0.0)
    date_input = Column(Date, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    product = relationship("Product", back_populates="product_inputs")


class ProductOutput(Base):
    __tablename__ = "products_outputs"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Float, nullable=False, default=0.0)
    price = Column(Float, nullable=True, default=0.0)
    date_output = Column(Date, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )


class RoleTechnician(Base):
    __tablename__ = "technicians_roles"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(255), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    technicians = relationship("Technician", back_populates="role")


class Technician(Base):
    __tablename__ = "technicians"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("technicians_roles.id"))
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    invoice_technicians = relationship("InvoiceTechnician", back_populates="technician")
    role = relationship("RoleTechnician", back_populates="technicians")
    tool_output = relationship("ToolOutput", back_populates="technician")
    tool_return = relationship("ToolReturn", back_populates="technician")
    task = relationship("ExpenseTask", back_populates="technician")
    jobs_assign = relationship("JobAssign", back_populates="technician")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    stock_level = Column(Float, nullable=True, default=0.0)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    tool_output = relationship("ToolOutput", back_populates="tool")


class ToolOutput(Base):
    __tablename__ = "tools_outputs"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey("tools.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Float, nullable=False, default=0.0)
    date_output = Column(Date, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    tool = relationship("Tool", back_populates="tool_output")
    technician = relationship("Technician", back_populates="tool_output")
    user = relationship("User", back_populates="tool_output")
    tool_return = relationship("ToolReturn", back_populates="tool_output")


class ToolReturn(Base):
    __tablename__ = "tools_returns"

    id = Column(Integer, primary_key=True, index=True)
    tool_output_id = Column(Integer, ForeignKey("tools_outputs.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Float, nullable=False, default=0.0)
    date_return = Column(Date, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    tool_output = relationship("ToolOutput", back_populates="tool_return")
    technician = relationship("Technician", back_populates="tool_return")
    user = relationship("User", back_populates="tool_return")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String(255), nullable=False)
    job_description = Column(String(1000), nullable=True)
    duration = Column(Float, nullable=True, default=0.0)
    price = Column(Float, nullable=True, default=0.0)
    date_program = Column(Date, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    invoice_jobs = relationship("InvoiceJob", back_populates="job")
    tasks_job = relationship("ExpenseTask", back_populates="job")
    jobs_assign = relationship("JobAssign", back_populates="job")


class JobAssign(Base):
    __tablename__ = "jobs_assigns"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"))
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    technician = relationship("Technician", back_populates="jobs_assign")
    job = relationship("Job", back_populates="jobs_assign")
    tasks_job_assign = relationship("ExpenseTask", back_populates="job_assign")


class JobReport(Base):
    __tablename__ = "jobs_reports"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"))
    report_heading = Column(String(255), nullable=False)
    report_description = Column(String(2000), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )


class JobReportImage(Base):
    __tablename__ = "jobs_reports_images"

    id = Column(Integer, primary_key=True, index=True)
    job_report_id = Column(Integer, ForeignKey("jobs_reports.id"))
    file_path = Column(String(255), nullable=False)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )


class CompanyDetail(Base):
    __tablename__ = "company_details"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    po_box = Column(String(255), nullable=True)
    bank_name = Column(String(255), nullable=True)
    bank_iban = Column(String(255), nullable=True)
    bank_swift_code = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    rc = Column(String(255), nullable=True)
    nui = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=True)
    contact_phone1 = Column(String(255), nullable=True)
    contact_phone2 = Column(String(255), nullable=True)
    contact_email1 = Column(String(255), nullable=True)
    contact_email2 = Column(String(255), nullable=True)
    status = Column(Boolean, default=True)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    purchase_orders = relationship("PurchaseOrder", back_populates="company")
    quotations = relationship("Quotation", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")
    payments = relationship("Payment", back_populates="company")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(15), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("company_details.id"))
    date_op = Column(Date, nullable=False)
    amount = Column(Float, nullable=True, default=0.0)
    tva_status = Column(Boolean, default=False)
    discount_status = Column(Boolean, default=False)
    discount_percent = Column(Float, default=0.0)
    shipping_status = Column(Boolean, default=False)
    shipping_amount = Column(Float, default=0.0)
    shipping_terms = Column(String(255), nullable=True)
    shipping_method = Column(String(255), nullable=True)
    shipping_date = Column(Date, nullable=True)
    status = Column(Boolean, nullable=True)
    currency_used = Column(String(20), nullable=True)
    locale_currency = Column(String(20), nullable=True)
    on_delete = Column(Boolean, nullable=True)
    reason_delete = Column(String(255), nullable=True)
    user_id_del = Column(Integer, default=0, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    vendor = relationship("Vendor", back_populates="purchase_orders")
    company = relationship("CompanyDetail", back_populates="purchase_orders")
    user = relationship("User", back_populates="purchase_orders")
    products = relationship(
        "PurchaseOrderProduct",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def computed_amount(self):
        """Dynamically compute the total from items (not stored in DB)."""
        return sum(item.total_amount for item in self.products)


class PurchaseOrderProduct(Base):
    __tablename__ = "purchase_order_products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    unit_price = Column(Float, default=0.0)
    quantity = Column(Float, default=0.0)
    status = Column(Boolean, nullable=True, default=True)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    product = relationship("Product", back_populates="order_products")
    purchase_order = relationship("PurchaseOrder", back_populates="products")

    @hybrid_property
    def total_amount(self):
        return self.unit_price * self.quantity


class QuotationType(Base):
    __tablename__ = "quotations_types"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(200), nullable=False)

    quotations = relationship("Quotation", back_populates="type")


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(15), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    type_id = Column(Integer, ForeignKey("quotations_types.id"))
    company_id = Column(Integer, ForeignKey("company_details.id"))
    date_op = Column(Date, nullable=False)
    amount = Column(Float, nullable=True, default=0.0)
    tva_status = Column(Boolean, default=False)
    discount_status = Column(Boolean, default=False)
    discount_percent = Column(Float, default=0.0)
    delivery_status = Column(Boolean, default=False)
    delivery_amount = Column(Float, default=0.0)
    status = Column(Boolean, nullable=True)
    currency_used = Column(String(20), nullable=True)
    locale_currency = Column(String(20), nullable=True)
    on_delete = Column(Boolean, nullable=True)
    reason_delete = Column(String(255), nullable=True)
    user_id_del = Column(Integer, default=0, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    type = relationship("QuotationType", back_populates="quotations")
    client = relationship("Client", back_populates="quotations")
    company = relationship("CompanyDetail", back_populates="quotations")
    user = relationship("User", back_populates="quotations")
    services = relationship(
        "QuotationService",
        back_populates="quotation",
        cascade="all, delete-orphan",
    )
    products = relationship(
        "QuotationProduct",
        back_populates="quotation",
        cascade="all, delete-orphan",
    )


class QuotationProduct(Base):
    __tablename__ = "quotations_products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quotation_id = Column(Integer, ForeignKey("quotations.id"))
    market_price = Column(Float, default=0.0)
    unit_price = Column(Float, default=0.0)
    quantity = Column(Float, default=0.0)
    status = Column(Boolean, nullable=True, default=True)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    product = relationship("Product", back_populates="quotation_products")
    quotation = relationship("Quotation", back_populates="products")

    @hybrid_property
    def total_amount(self):
        return self.unit_price * self.quantity

    @hybrid_property
    def total_amount_market(self):
        return self.market_price * self.quantity


class QuotationService(Base):
    __tablename__ = "quotations_Service"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(255), nullable=False)
    quotation_id = Column(Integer, ForeignKey("quotations.id"))
    unit_price = Column(Float, default=0.0)
    quantity = Column(Float, default=0.0)
    status = Column(Boolean, nullable=True, default=True)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    quotation = relationship("Quotation", back_populates="services")

    @hybrid_property
    def total_amount(self):
        return self.unit_price * self.quantity


class InvoiceType(Base):
    __tablename__ = "invoice_types"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(200), nullable=False)

    invoices = relationship("Invoice", back_populates="type")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(15), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"))
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type_id = Column(Integer, ForeignKey("invoice_types.id"))
    company_id = Column(Integer, ForeignKey("company_details.id"))
    date_op = Column(Date, nullable=False)
    amount = Column(Float, nullable=True, default=0.0)
    tva_status = Column(Boolean, default=False)
    status = Column(Boolean, nullable=True)
    has_heading = Column(Boolean, nullable=True)
    has_po = Column(Boolean, nullable=True)
    heading = Column(String(255), nullable=True)
    currency_used = Column(String(20), nullable=True)
    locale_currency = Column(String(20), nullable=True)
    on_delete = Column(Boolean, nullable=True)
    reason_delete = Column(String(255), nullable=True)
    user_id_del = Column(Integer, default=0, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    type = relationship("InvoiceType", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    company = relationship("CompanyDetail", back_populates="invoices")
    user = relationship("User", back_populates="invoices")
    expense = relationship("Expense", back_populates="invoice")
    jobs = relationship(
        "InvoiceJob",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )
    products = relationship(
        "InvoiceProduct",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )
    technicians = relationship(
        "InvoiceTechnician",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )

    payments = relationship(
        "Payment",
        back_populates="invoice",
        cascade="all, delete-orphan",
    )


class InvoiceJob(Base):
    __tablename__ = "invoice_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    invoice_id = Column(Integer, ForeignKey("invoices.id"))

    invoice = relationship("Invoice", back_populates="jobs")
    job = relationship("Job", back_populates="invoice_jobs")


class InvoiceProduct(Base):
    __tablename__ = "invoice_products"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    unit_price = Column(Float, default=0.0)
    quantity = Column(Float, default=0.0)

    invoice = relationship("Invoice", back_populates="products")
    product = relationship("Product", back_populates="invoice_products")


class InvoiceTechnician(Base):
    __tablename__ = "invoice_technicians"

    id = Column(Integer, primary_key=True, index=True)
    technician_id = Column(Integer, ForeignKey("technicians.id"))
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    normal_hour1 = Column(Integer, default=0)
    normal_hour2 = Column(Integer, default=0)
    normal_unit_price = Column(Float, default=0.0)
    overtime_hour1 = Column(Integer, default=0)
    overtime_hour2 = Column(Integer, default=0)
    overtime_unit_price = Column(Float, default=0.0)
    allowance_hour1 = Column(Integer, default=0)
    allowance_hour2 = Column(Integer, default=0)
    allowance_unit_price = Column(Float, default=0.0)

    invoice = relationship("Invoice", back_populates="technicians")
    technician = relationship("Technician", back_populates="invoice_technicians")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    method = Column(String(100), nullable=False)

    payments = relationship("Payment", back_populates="method")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(15), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("company_details.id"))
    date_op = Column(Date, nullable=False)
    method_id = Column(Integer, ForeignKey("payment_methods.id"))
    amount = Column(Float, default=0.0)
    file_path = Column(String(255), nullable=True)
    currency_used = Column(String(20), nullable=True)
    locale_currency = Column(String(20), nullable=True)
    on_delete = Column(Boolean, nullable=True)
    reason_delete = Column(String(255), nullable=True)
    user_id_del = Column(Integer, default=0, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    invoice = relationship("Invoice", back_populates="payments")
    company = relationship("CompanyDetail", back_populates="payments")
    user = relationship("User", back_populates="payments")
    method = relationship("PaymentMethod", back_populates="payments")


class CashRegister(Base):
    __tablename__ = "cash_registers"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=date.today, unique=True)
    opening_balance = Column(Float, nullable=False)
    closing_balance = Column(Float)
    status = Column(String(20), default="open")  # open / closed

    transactions = relationship("Transaction", back_populates="cash")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    type = Column(String(10))  # 'in' or 'out'
    amount = Column(Float, nullable=False)
    description = Column(String(255))
    date = Column(Date, default=date.today)
    cash_id = Column(Integer, ForeignKey("cash_registers.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    cash = relationship("CashRegister", back_populates="transactions")
    user = relationship("User", back_populates="transactions")


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(15), nullable=False)
    date = Column(Date, default=date.today)
    amount = Column(Float, nullable=False)
    label = Column(String(255), nullable=False)
    type_expense = Column(String(20))
    user_id = Column(Integer, ForeignKey("users.id"))
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)

    invoice = relationship("Invoice", back_populates="expense")
    tasks = relationship("ExpenseTask", back_populates="expense")
    user = relationship("User", back_populates="expense")


class ExpenseTask(Base):
    __tablename__ = "expense_tasks"
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    job_assign_id = Column(Integer, ForeignKey("jobs_assigns.id"), nullable=True)
    task = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)

    expense = relationship("Expense", back_populates="tasks")
    technician = relationship("Technician", back_populates="task")
    job = relationship("Job", back_populates="tasks_job")
    job_assign = relationship("JobAssign", back_populates="tasks_job_assign")
