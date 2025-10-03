from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/db_president_work"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/almapps_new_db"
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://kaiseioy_almapps_user:B)h#W?Xs3}JP@162.0.209.239:3306/kaiseioy_almapps_new"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
