from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class ProfileBase(BaseModel):
    name: str


class ProfileCreate(ProfileBase):
    name: str = Field(min_length=3, max_length=100)


class ProfileResponse(ProfileBase):
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: str
    is_active: bool
    profile_id: int


class UserCreate(UserBase):
    username: str = Field(min_length=3, max_length=200)
    email: str = Field(min_length=3, max_length=200)
    password: str = Field(min_length=3, max_length=200)
    is_active: bool
    profile_id: int


class UserUpdate(UserBase):
    username: Optional[str]
    email: Optional[str]
    is_active: Optional[bool]
    profile_id: Optional[int]


class UserPasswordReset(UserBase):
    password: Optional[str]


class UserResponse(UserBase):
    id: int
    profile: Optional[ProfileResponse]

    class Config:
        from_attributes = True


class ClientTypeBase(BaseModel):
    type: str


class ClientTypeCreate(ClientTypeBase):
    type: str


class ClientTypeResponse(ClientTypeBase):
    id: int

    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    name: str
    address: str
    email: str
    phone: str
    postal: str
    nui: str
    rc: str
    type_id: int


class ClientCreate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: int
    type: Optional[ClientTypeBase]

    class Config:
        from_attributes = True


class ContactPersonBase(BaseModel):
    name: str


class ContactPersonCreate(ContactPersonBase):
    name: str
    email: str
    phone: str
    client_id: int


class ContactPersonResponse(ContactPersonBase):
    id: int
    name: str
    email: str
    phone: str
    client_id: int

    class Config:
        from_attributes = True


class VendorBase(BaseModel):
    name: str


class VendorCreate(VendorBase):
    name: str
    email: str
    phone: str
    address: str


class VendorResponse(VendorBase):
    id: int
    name: str
    email: str
    phone: str
    address: str

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str


class ProductCreate(ProductBase):
    name: str
    description: str
    unit: str
    stock_security_level: float


class ProductResponse(ProductBase):
    id: int
    name: str
    description: str
    unit: str
    stock_security_level: float

    class Config:
        from_attributes = True


class ProductInputBase(BaseModel):
    pass


class ProductInputCreate(ProductInputBase):
    product_id: int
    vendor_id: int
    user_id: int
    quantity: float
    price: float
    date_input: date


class ProductInputResponse(ProductInputBase):
    id: int
    product_id: int
    vendor_id: int
    product: str
    vendor: str
    user_id: int
    quantity: float
    price: float
    date_input: date

    class Config:
        from_attributes = True


class ProductOutputBase(BaseModel):
    pass


class ProductOutputCreate(ProductInputBase):
    product_id: int
    user_id: int
    quantity: float
    price: float
    date_output: date


class ProductOutputResponse(ProductInputBase):
    id: int
    product_id: int
    product: str
    user_id: int
    quantity: float
    price: float
    date_output: date

    class Config:
        from_attributes = True


class TechnicianRoleBase(BaseModel):
    pass


class TechnicianRoleCreate(TechnicianRoleBase):
    role: str


class TechnicianRoleResponse(TechnicianRoleBase):
    id: int
    role: str

    class Config:
        from_attributes = True


class TechnicianBase(BaseModel):
    pass


class TechnicianCreate(TechnicianBase):
    name: str
    email: str
    phone: str
    role_id: int


class TechnicianResponse(TechnicianBase):
    id: int
    name: str
    email: str
    phone: str
    role: Optional[TechnicianRoleResponse] = {}

    class Config:
        from_attributes = True


class JobBase(BaseModel):
    pass


class JobCreate(JobBase):
    job_name: str
    job_description: str
    duration: float
    price: float
    date_program: Optional[date] = None


class JobResponse(JobBase):
    id: int
    job_name: str
    job_description: str
    duration: float
    price: float
    date_program: date

    class Config:
        from_attributes = True


class JobAssignBase(BaseModel):
    pass


class JobAssignCreate(JobBase):
    job_id: int
    technician_id: int
    date_start: date
    date_end: date


class JobAssignResponse(JobBase):
    id: int
    job_id: int
    technician_id: int
    date_start: date
    date_end: date
    technician: Optional[TechnicianResponse] = {}
    job: Optional[JobResponse] = {}

    class Config:
        from_attributes = True


class JobReportBase(BaseModel):
    pass


class JobReportCreate(JobReportBase):
    job_id: int
    technician_id: int
    report_heading: str
    report_description: str


class JobReportResponse(JobReportBase):
    id: int
    job_id: int
    technician_id: int
    report_heading: str
    report_description: str

    class Config:
        from_attributes = True


class JobReportImageBase(BaseModel):
    pass


class JobReportImageCreate(JobReportImageBase):
    job_report_id: int
    # file_path: str


class JobReportImageResponse(JobReportImageBase):
    id: int
    job_report_id: int
    file_path: str

    class Config:
        from_attributes = True


class CompanyDetailBase(BaseModel):
    name: str
    address: str
    po_box: Optional[str] = None
    bank_name: Optional[str] = None
    bank_iban: Optional[str] = None
    bank_swift_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    rc: Optional[str] = None
    nui: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone1: Optional[str] = None
    contact_phone2: Optional[str] = None
    contact_email1: Optional[str] = None
    contact_email2: Optional[str] = None
    status: Optional[bool] = True


class CompanyDetailCreate(CompanyDetailBase):
    pass


class CompanyDetailUpdate(CompanyDetailBase):
    pass


class CompanyDetailResponse(CompanyDetailBase):
    id: int

    class Config:
        from_attributes = True


class PurchaseOrderProductBase(BaseModel):
    product_id: int
    po_id: int
    unit_price: float = 0.0
    quantity: float = 0.0
    status: Optional[bool] = True


class PurchaseOrderProductCreate(PurchaseOrderProductBase):
    pass


class PurchaseOrderProductUpdate(BaseModel):
    unit_price: Optional[float]
    quantity: Optional[float]
    status: Optional[bool]


class PurchaseOrderProductResponse(PurchaseOrderProductBase):
    id: int
    total_amount: float
    product: Optional[ProductResponse]

    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    reference: str
    vendor_id: int
    user_id: int
    company_id: int
    date_op: date
    amount: Optional[float] = 0.0
    tva_status: Optional[bool] = False
    discount_status: Optional[bool] = False
    discount_percent: Optional[float] = 0.0
    shipping_status: Optional[bool] = False
    shipping_amount: Optional[float] = 0.0
    shipping_terms: Optional[str] = None
    shipping_method: Optional[str] = None
    shipping_date: Optional[date] = None
    status: Optional[bool] = None
    currency_used: Optional[str] = None
    locale_currency: Optional[str] = None
    on_delete: Optional[bool] = None
    reason_delete: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    pass


class PurchaseOrderUpdate(PurchaseOrderBase):
    pass


class PurchaseOrderResponse(PurchaseOrderBase):
    id: int
    vendor: Optional[VendorResponse]
    company: Optional[CompanyDetailResponse]
    products: Optional[List[PurchaseOrderProductResponse]] = []

    class Config:
        from_attributes = True


class QuotationTypeBase(BaseModel):
    type: str


class QuotationTypeCreate(QuotationTypeBase):
    pass


class QuotationTypeUpdate(QuotationTypeBase):
    pass


class QuotationTypeResponse(QuotationTypeBase):
    id: int

    class Config:
        from_attributes = True


class QuotationProductBase(BaseModel):
    product_id: int
    quotation_id: int
    market_price: Optional[float]
    unit_price: float
    quantity: float
    status: bool


class QuotationProductCreate(QuotationProductBase):
    pass


class QuotationProductUpdate(BaseModel):
    market_price: Optional[float]
    unit_price: float
    quantity: float
    status: bool


class QuotationProductResponse(QuotationProductBase):
    id: int
    product: Optional[ProductResponse]

    class Config:
        from_attributes = True


class QuotationServiceBase(BaseModel):
    service: str
    quotation_id: int
    unit_price: float
    quantity: float
    status: bool


class QuotationServiceCreate(QuotationServiceBase):
    pass


class QuotationServiceUpdate(BaseModel):
    # service: str
    unit_price: float
    quantity: float
    status: bool


class QuotationServiceResponse(QuotationServiceBase):
    id: int

    class Config:
        from_attributes = True


class QuotationBase(BaseModel):
    reference: str
    client_id: int
    user_id: int
    type_id: int
    company_id: int
    date_op: date
    amount: Optional[float] = 0.0
    tva_status: Optional[bool] = False
    discount_status: Optional[bool] = False
    discount_percent: Optional[float] = 0.0
    delivery_status: Optional[bool] = False
    delivery_amount: Optional[float] = 0.0
    status: Optional[bool] = False
    currency_used: Optional[str] = None
    locale_currency: Optional[str] = None
    on_delete: Optional[bool] = None
    reason_delete: Optional[str] = None


class QuotationCreate(QuotationBase):
    pass


class QuotationUpdate(QuotationBase):
    pass


class QuotationResponse(QuotationBase):
    id: int
    type: Optional[QuotationTypeResponse]
    client: Optional[ClientResponse]
    company: Optional[CompanyDetailResponse]
    products: Optional[List[QuotationProductResponse]] = []
    services: Optional[List[QuotationServiceResponse]] = []

    class Config:
        from_attributes = True


class InvoiceTypeBase(BaseModel):
    type: str


class InvoiceTypeCreate(InvoiceTypeBase):
    pass


class InvoiceTypeUpdate(InvoiceTypeBase):
    pass


class InvoiceTypeResponse(InvoiceTypeBase):
    id: int

    class Config:
        from_attributes = True


class InvoiceProductBase(BaseModel):
    product_id: int
    invoice_id: int
    unit_price: float
    quantity: float


class InvoiceProductCreate(InvoiceProductBase):
    pass


class InvoiceProductUpdate(BaseModel):
    unit_price: float
    quantity: float


class InvoiceProductResponse(InvoiceProductBase):
    id: int
    product: Optional[ProductResponse]

    class Config:
        from_attributes = True


class InvoiceJobBase(BaseModel):
    job_id: int
    invoice_id: int


class InvoiceJobCreate(InvoiceJobBase):
    pass


class InvoiceJobUpdate(BaseModel):
    pass


class InvoiceJobResponse(InvoiceJobBase):
    id: int
    job: Optional[JobResponse]

    class Config:
        from_attributes = True


class InvoiceTechnicianBase(BaseModel):
    technician_id: int
    invoice_id: int
    normal_hour1: Optional[int] = 0
    normal_hour2: Optional[int] = 0
    normal_unit_price: Optional[float] = 0.0
    overtime_hour1: Optional[int] = 0
    overtime_hour2: Optional[int] = 0
    overtime_unit_price: Optional[float] = 0
    allowance_hour1: Optional[int] = 0
    allowance_hour2: Optional[int] = 0
    allowance_unit_price: Optional[int] = 0


class InvoiceTechnicianCreate(InvoiceTechnicianBase):
    pass


class InvoiceTechnicianUpdate(BaseModel):
    normal_hour1: Optional[int] = 0
    normal_hour2: Optional[int] = 0
    normal_unit_price: Optional[float] = 0.0
    overtime_hour1: Optional[int] = 0
    overtime_hour2: Optional[int] = 0
    overtime_unit_price: Optional[float] = 0
    allowance_hour1: Optional[int] = 0
    allowance_hour2: Optional[int] = 0
    allowance_unit_price: Optional[int] = 0


class InvoiceTechnicianResponse(InvoiceTechnicianBase):
    id: int
    technician: Optional[TechnicianResponse]

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    reference: str
    client_id: int
    purchase_order_id: Optional[int] = None
    user_id: Optional[int]
    type_id: Optional[int]
    company_id: Optional[int]
    date_op: date
    amount: Optional[float] = 0
    tva_status: Optional[bool] = False
    status: Optional[bool] = False
    has_heading: Optional[bool] = False
    has_po: Optional[bool] = False
    heading: Optional[str] = None
    currency_used: Optional[str] = None
    locale_currency: Optional[str] = None
    on_delete: Optional[bool] = None
    reason_delete: Optional[str] = None
    # user_id_del: Optional[int] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    client_id: int
    purchase_order_id: Optional[int] = None
    date_op: date
    amount: Optional[float] = 0
    tva_status: Optional[bool] = False
    has_heading: Optional[bool] = False
    has_po: Optional[bool] = False
    heading: Optional[str] = None
    status: Optional[bool] = False
    currency_used: Optional[str] = None
    locale_currency: Optional[str] = None
    on_delete: Optional[bool] = None
    reason_delete: Optional[str] = None
    user_id_del: Optional[int] = None


class InvoiceResponse(InvoiceBase):
    id: int
    technicians: Optional[List[InvoiceTechnicianResponse]] = []
    products: Optional[List[InvoiceProductResponse]] = []
    jobs: Optional[List[InvoiceJobResponse]] = []
    client: Optional[ClientResponse]
    company: Optional[CompanyDetailResponse]
    user: Optional[UserResponse]
    type: Optional[InvoiceTypeResponse]

    class Config:
        from_attributes = True


class PaymentMethodBase(BaseModel):
    method: str


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodUpdate(PaymentMethodBase):
    pass


class PaymentMethodResponse(PaymentMethodBase):
    id: int

    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    reference: str
    invoice_id: int
    company_id: Optional[int]
    user_id: Optional[int]
    method_id: Optional[int]
    date_op: date
    amount: Optional[float] = 0
    file_path: Optional[str] = None
    currency_used: Optional[str] = None
    locale_currency: Optional[str] = None
    on_delete: Optional[bool] = None
    reason_delete: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    method_id: Optional[int]
    date_op: date
    amount: Optional[float] = 0
    file_path: Optional[str] = None
    currency_used: Optional[str] = None
    locale_currency: Optional[str] = None
    on_delete: Optional[bool] = None
    reason_delete: Optional[str] = None


class PaymentResponse(PaymentBase):
    id: int
    invoice: Optional[InvoiceResponse]
    company: Optional[CompanyDetailResponse]
    user: Optional[UserResponse]
    method: Optional[PaymentMethodResponse]

    class Config:
        from_attributes = True


class PaymentSimpleResponse(PaymentBase):
    id: int

    class Config:
        from_attributes = True


class InvoicePaymentResponse(InvoiceBase):
    id: int
    payments: Optional[List[PaymentSimpleResponse]] = []
    technicians: Optional[List[InvoiceTechnicianResponse]] = []
    products: Optional[List[InvoiceProductResponse]] = []
    jobs: Optional[List[InvoiceJobResponse]] = []
    client: Optional[ClientResponse]
    company: Optional[CompanyDetailResponse]
    user: Optional[UserResponse]
    type: Optional[InvoiceTypeResponse]

    class Config:
        from_attributes = True


class ToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    stock_level: Optional[float] = None


class ToolCreate(ToolBase):
    pass


class ToolUpdate(ToolBase):
    pass


class ToolResponse(ToolBase):
    id: int

    class Config:
        from_attributes = True


class ToolOutputBase(BaseModel):
    tool_id: Optional[int]
    technician_id: Optional[int]
    user_id: Optional[int]
    quantity: Optional[float]
    date_output: date


class ToolOutputCreate(ToolOutputBase):
    pass


class ToolOutputUpdate(ToolOutputBase):
    pass


class ToolOutputResponse(ToolOutputBase):
    id: int
    tool: Optional[ToolResponse]
    technician: Optional[TechnicianResponse]
    user: Optional[UserResponse]

    class Config:
        from_attributes = True


class ToolReturnBase(BaseModel):
    technician_id: Optional[int]
    user_id: Optional[int]
    tool_output_id: Optional[int]
    quantity: Optional[float]
    date_return: date


class ToolReturnCreate(ToolReturnBase):
    pass


class ToolReturnUpdate(ToolReturnBase):
    pass


class ToolReturnResponse(ToolReturnBase):
    id: int
    tool_output: Optional[ToolOutputResponse]
    technician: Optional[TechnicianResponse]
    user: Optional[UserResponse]

    class Config:
        from_attributes = True


class CashRegisterBase(BaseModel):
    opening_balance: Optional[float]
    closing_balance: Optional[float] = None
    status: Optional[str] = None
    date: date


class CashRegisterCreate(CashRegisterBase):
    pass


class CashRegisterUpdate(CashRegisterBase):
    pass


class CashRegisterResponse(CashRegisterBase):
    id: int

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    type: Optional[str]
    amount: Optional[float] = None
    description: Optional[str] = None
    date: date
    cash_id: Optional[int]
    user_id: Optional[int]


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    cash: Optional[CashRegisterResponse]
    user: Optional[UserResponse]

    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    reference: Optional[str]
    amount: Optional[float] = None
    label: Optional[str] = None
    type_expense: Optional[str] = None
    date: date
    user_id: Optional[int] = None
    invoice_id: Optional[int] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(ExpenseBase):
    pass


# class ExpenseResponse(ExpenseBase):
#     id: int
#     invoice: Optional[InvoiceResponse]
#     # user: Optional[UserResponse]

#     class Config:
#         from_attributes = True


class ExpenseTaskBase(BaseModel):
    amount: Optional[float] = None
    task: Optional[str] = None
    expense_id: Optional[int] = None
    technician_id: Optional[int] = None
    job_assign_id: Optional[int] = None
    job_id: Optional[int] = None


class ExpenseTaskCreate(ExpenseTaskBase):
    pass


class ExpenseTaskUpdate(ExpenseTaskBase):
    pass


class ExpenseTaskResponse(ExpenseTaskBase):
    id: int
    technician: Optional[TechnicianResponse]
    job: Optional[JobResponse]

    class Config:
        from_attributes = True


class ExpenseResponse(ExpenseBase):
    id: int
    invoice: Optional[InvoiceResponse]
    user: Optional[UserResponse]
    tasks: Optional[List[ExpenseTaskResponse]] = []

    class Config:
        from_attributes = True
