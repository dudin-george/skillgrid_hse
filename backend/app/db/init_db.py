import sys
from sqlalchemy import create_engine

from app.core.config import settings
from app.models.models import Base

def init_db():
    # Get database URL from settings
    db_url = settings.DATABASE_URL
    
    print(f"Connecting to database: {db_url}")
    
    # Create engine
    engine = create_engine(db_url)
    
    try:
        # Create all tables
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        return True
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1) 