from src.services.db import Base, Faculty
from sqlalchemy import create_engine
from src.core.config import settings

def setup_database():
    print(f"Connecting to {settings.DATABASE_URL}...")
    engine = create_engine(settings.DATABASE_URL)
    
    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Database setup complete.")

if __name__ == "__main__":
    setup_database()
