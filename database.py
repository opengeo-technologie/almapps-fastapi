from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/db_president_work"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/almapps_new_db"
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://kaiseioy_almapps_user:B)h#W?Xs3}JP@162.0.209.239:3306/kaiseioy_almapps_new"
# SQLALCHEMY_DATABASE_URL = (
#     "mysql+pymysql://almapps_user:AlmappsConnect2025!@127.0.0.1/almapps_db"
# )
# SQLALCHEMY_DATABASE_URL = (
#     f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# )

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
