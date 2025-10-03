import random
import datetime
from faker import Faker
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from .models import (
    Profile,
    User,
    ClientType,
    Client,
    ContactPerson,
    Vendor,
    Product,
    ProductInput,
    ProductOutput,
    RoleTechnician,
    Technician,
    Tool,
    ToolOutput,
    ToolReturn,
    Job,
    JobAssign,
    JobReport,
    JobReportImage,
    CompanyDetail,
    PurchaseOrder,
    PurchaseOrderProduct,
)

fake = Faker()


def seed_db(db: Session):
    # --- Profiles ---
    profiles = [
        "SuperAdmin",
        "Admin",
        "Accountant",
        "Manager",
        "Technician",
        "Cashier",
        "Stock Manager",
    ]
    profile_objs = []
    for p in profiles:
        pr = Profile(name=p)
        db.add(pr)
        profile_objs.append(pr)
    db.commit()

    # --- Users ---
    users = []
    for _ in range(10):
        user = User(
            username=fake.user_name(),
            email=fake.unique.email(),
            password="hashedpassword",
            is_active=True,
            profile_id=random.choice(profile_objs).id,
        )
        db.add(user)
        users.append(user)
    db.commit()

    # --- Client Types ---
    types = ["Personal", "Company"]
    client_types = []
    for t in types:
        ct = ClientType(type=t)
        db.add(ct)
        client_types.append(ct)
    db.commit()

    # --- Clients ---
    clients = []
    for _ in range(5):
        c = Client(
            name=fake.company(),
            address=fake.address(),
            email=fake.email(),
            phone=fake.phone_number(),
            postal=fake.postcode(),
            nui=fake.uuid4(),
            rc=fake.bothify(text="RC-####"),
            type_id=random.choice(client_types).id,
        )
        db.add(c)
        clients.append(c)
    db.commit()

    # --- Contact Person ---
    for client in clients:
        if client.type_id == [ct.id for ct in client_types if ct.type == "Company"][0]:
            cp = ContactPerson(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number(),
                client_id=client.id,
            )
            db.add(cp)
    db.commit()

    # --- Vendors ---
    vendors = []
    for _ in range(5):
        v = Vendor(
            name=fake.company(),
            email=fake.company_email(),
            phone=fake.phone_number(),
            address=fake.address(),
        )
        db.add(v)
        vendors.append(v)
    db.commit()

    # --- Products ---
    products = []
    for _ in range(10):
        p = Product(
            name=fake.word().capitalize(),
            description=fake.sentence(),
            unit=random.choice(["kg", "L", "pcs", "m"]),
            stock_security_level=random.uniform(1, 50),
        )
        db.add(p)
        products.append(p)
    db.commit()

    # --- Product Inputs ---
    for _ in range(20):
        pi = ProductInput(
            product_id=random.choice(products).id,
            vendor_id=random.choice(vendors).id,
            user_id=random.choice(users).id,
            quantity=random.uniform(1, 100),
            price=random.uniform(10, 500),
            date_input=fake.date_this_year(),
        )
        db.add(pi)
    db.commit()

    # --- Technicians Roles ---
    roles = ["Electrician", "Plumber", "Mechanic"]
    role_objs = []
    for r in roles:
        rr = RoleTechnician(role=r)
        db.add(rr)
        role_objs.append(rr)
    db.commit()

    # --- Technicians ---
    techs = []
    for _ in range(5):
        t = Technician(
            name=fake.name(),
            email=fake.email(),
            phone=fake.phone_number(),
            role_id=random.choice(role_objs).id,
        )
        db.add(t)
        techs.append(t)
    db.commit()

    # --- Tools ---
    tools = []
    for _ in range(5):
        tool = Tool(
            name=fake.word().capitalize(),
            description=fake.sentence(),
            stock_level=random.randint(5, 50),
        )
        db.add(tool)
        tools.append(tool)
    db.commit()

    # --- Tool Outputs & Returns ---
    for _ in range(10):
        to = ToolOutput(
            tool_id=random.choice(tools).id,
            technician_id=random.choice(techs).id,
            user_id=random.choice(users).id,
            quantity=random.randint(1, 5),
            date_output=fake.date_this_year(),
        )
        db.add(to)

        tr = ToolReturn(
            tool_id=to.tool_id,
            technician_id=to.technician_id,
            user_id=to.user_id,
            quantity=random.randint(1, to.quantity),
            date_return=fake.date_this_year(),
        )
        db.add(tr)
    db.commit()

    # --- Company Details ---
    companies = []
    for _ in range(2):
        c = CompanyDetail(
            name=fake.company(),
            address=fake.address(),
            phone=fake.phone_number(),
            email=fake.company_email(),
            bank_name=fake.company(),
            bank_iban=fake.iban(),
            bank_swift_code=fake.bothify("SWIFT####"),
        )
        db.add(c)
        companies.append(c)
    db.commit()

    # --- Purchase Orders & Products ---
    for _ in range(5):
        po = PurchaseOrder(
            reference=fake.bothify("PO#######"),
            vendor_id=random.choice(vendors).id,
            user_id=random.choice(users).id,
            company_id=random.choice(companies).id,
            date_op=fake.date_this_year(),
            tva_status=random.choice([True, False]),
            discount_status=random.choice([True, False]),
            shipping_status=random.choice([True, False]),
            status=True,
            currency_used="XAF",
            locale_currency="fr-CM",
        )
        db.add(po)
        db.commit()

        for _ in range(random.randint(1, 4)):
            pop = PurchaseOrderProduct(
                product_id=random.choice(products).id,
                po_id=po.id,
                unit_price=random.uniform(50, 500),
                quantity=random.randint(1, 10),
            )
            db.add(pop)
        db.commit()

    print("✅ Database seeded successfully!")


if __name__ == "__main__":
    db = SessionLocal()
    seed_db(db)
