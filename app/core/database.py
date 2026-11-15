from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
#Create the SQL engine
engine = create_engine(settings.DATABASE_URL)
#Create the session local factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#Create the declarative base class
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()