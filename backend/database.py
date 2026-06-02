from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

MYSQL_PASSWORD = quote_plus("taradevi@2407")

DATABASE_URL = f"mysql+pymysql://root:{MYSQL_PASSWORD}@localhost/cloudforge"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()