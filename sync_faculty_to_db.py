import json
import os
from sqlalchemy import create_engine, Column, String, Text, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Config
DB_URL = "postgresql://postgres:root@localhost:5432/padhai_app_db"
JSON_FILE = "faculty_structured_db.json"

Base = declarative_base()

class Faculty(Base):
    __tablename__ = 'faculty'
    id = Column(String(50), primary_key=True)
    name = Column(String(200))
    clean_name = Column(String(200))
    designation = Column(String(200))
    contact_info = Column(Text)
    profile_pdf = Column(String(500))
    biography = Column(Text)
    research_interests = Column(Text)
    open_projects = Column(Text)
    additional_info = Column(JSON)
    publication_profiles = Column(JSON)
    publication_counts = Column(JSON)
    source_url = Column(String(500))

def sync():
    if not os.path.exists(JSON_FILE):
        print(f"File {JSON_FILE} not found.")
        return

    with open(JSON_FILE, 'r') as f:
        data = json.load(f)

    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    print(f"Syncing {len(data)} faculty profiles to database...")
    
    # Simple strategy: delete all and re-insert for clean state
    # Or we could use merge/upsert, but this is simpler for expansion
    session.query(Faculty).delete()
    
    for fid, profile in data.items():
        faculty = Faculty(
            id=profile['id'],
            name=profile['name'],
            clean_name=profile['clean_name'],
            designation=profile['designation'],
            contact_info=profile.get('contact_info', ''),
            profile_pdf=profile.get('profile_pdf', ''),
            biography=profile.get('biography', ''),
            research_interests=profile.get('research_interests', ''),
            open_projects=profile.get('open_projects', ''),
            additional_info=profile.get('additional_info', {}),
            publication_profiles=profile.get('publication_profiles', {}),
            publication_counts=profile.get('publication_counts', {}),
            source_url=profile.get('source_url', '')
        )
        session.add(faculty)
    
    session.commit()
    print("Database sync complete.")

if __name__ == "__main__":
    sync()
