from sqlalchemy import create_engine, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# create a base class
Base = declarative_base()


def get_db():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL + "trip_management_service",
        poolclass=pool.QueuePool,
        pool_size=10000,
        max_overflow=8000,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    return db


# FACTORY DESIGN PATERN
class DBFactory:
    def __init__(self):
        self.db = None

    def __enter__(self):
        self.db = get_db()
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        if self.db:
            self.db.close()