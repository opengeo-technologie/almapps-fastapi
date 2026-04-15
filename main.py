from fastapi import FastAPI, Request, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import logging
from .logging_config import setup_logging
from .core.dependencies import log_request
from .database import SessionLocal
from .models import Base
from .database import engine

# from .core.geoip import get_country
from .routers import (
    auth,
    products_input,
    products_output,
    profile,
    users,
    client_types,
    clients,
    contact_person,
    vendors,
    products,
    technicians_role,
    technicians,
    job,
    job_assign,
    job_report,
    job_report_image,
    company_info,
    purchase_order,
    purchase_order_product,
    generate_references,
    quotation_type,
    quotation_product,
    quotation,
    quotation_service,
    invoice,
    invoice_job,
    invoice_products,
    invoice_technician,
    invoice_type,
    payment_method,
    payment,
    tools,
    tools_output,
    tools_return,
    # cash,
    expense,
    expense_task,
    logs,
    cash_register,
)

logger = logging.getLogger("request")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 STARTUP
    setup_logging()
    logging.getLogger(__name__).info("FastAPI started")

    yield

    # 🔹 SHUTDOWN
    logging.getLogger(__name__).info("FastAPI stopped")


app = FastAPI(
    lifespan=lifespan,
    version="1.0.0",
    title="ALMAPPS API",
    description="API for ALMAPPS application",
)


def get_client_ip(request):
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = round(time.time() - start_time, 4)

    client_ip = get_client_ip(request)
    # country = get_country(client_ip)
    user_agent = request.headers.get("user-agent", "unknown")

    logger.info(
        "%s %s | status=%s | client_ip=%s | %s | duration=%ss",
        request.method,
        request.url.path,
        response.status_code,
        client_ip,
        user_agent,
        duration,
    )

    return response


# Allow your frontend origin
origins = [
    "http://localhost:4200",  # Angular dev server
    "http://127.0.0.1:4200",  # Alternate local address
    # Add your production domain if deployed
    "https://almapps2.kais-consulting.com",
]

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all origins (not recommended in production)
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],  # Accept, Content-Type, Authorization, etc.
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def health_check():
    return {"status": "Healthy"}


@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application started")


# UPLOAD_DIR = "uploads/reports/images"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

app.include_router(cash_register.router)
app.include_router(auth.router)
app.include_router(generate_references.router)
app.include_router(logs.router)
app.include_router(profile.router)
app.include_router(users.router)
app.include_router(client_types.router)
app.include_router(clients.router)
app.include_router(contact_person.router)
app.include_router(vendors.router)
app.include_router(products.router)
app.include_router(products_input.router)
app.include_router(products_output.router)
app.include_router(technicians_role.router)
app.include_router(technicians.router)
app.include_router(job.router)
app.include_router(job_assign.router)
app.include_router(job_report.router)
app.include_router(job_report_image.router)
app.include_router(company_info.router)
app.include_router(purchase_order.router)
app.include_router(purchase_order_product.router)
app.include_router(quotation_type.router)
app.include_router(quotation.router)
app.include_router(quotation_product.router)
app.include_router(quotation_service.router)
app.include_router(invoice_type.router)
app.include_router(invoice.router)
app.include_router(invoice_job.router)
app.include_router(invoice_products.router)
app.include_router(invoice_technician.router)
app.include_router(payment_method.router)
app.include_router(payment.router)
app.include_router(tools.router)
app.include_router(tools_output.router)
app.include_router(tools_return.router)
# app.include_router(cash.router)
app.include_router(expense.router)
app.include_router(expense_task.router)
