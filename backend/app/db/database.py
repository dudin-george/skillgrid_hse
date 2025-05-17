from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create engine using the settings
engine = create_engine(settings.DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 