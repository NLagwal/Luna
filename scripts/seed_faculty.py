from src.services.db import db_service, Faculty
from sqlalchemy import insert
from src.core.config import settings

def seed_faculty():
    faculty_data = [
        {
            "name": "Dr. Rajendra Kumar Sharma",
            "clean_name": "rajendra kumar sharma",
            "designation": "Vice Chancellor",
            "biography": "Prof. (Dr.) Rajendra Kumar Sharma is an accomplished academic leader with over three decades of experience.",
            "research_interests": "Power Systems, Academic Leadership",
            "contact_info": "vc@juit.ac.in",
            "source_url": "https://www.juit.ac.in/authorities"
        },
        {
            "name": "Prof. Shruti Jain",
            "clean_name": "shruti jain",
            "designation": "Dean (Academics)",
            "biography": "Prof. Shruti Jain is the Dean (Academics) at JUIT.",
            "research_interests": "Electronics, Nanoelectronics",
            "contact_info": "shruti.jain@juit.ac.in",
            "source_url": "https://www.juit.ac.in/faculty/ece/shruti-jain"
        }
    ]
    
    with db_service.SessionLocal() as session:
        for f_data in faculty_data:
            # Check if exists
            existing = session.query(Faculty).filter_by(clean_name=f_data["clean_name"]).first()
            if not existing:
                session.add(Faculty(**f_data))
        session.commit()
    
    # Refresh metadata in service
    db_service._load_faculty_metadata()
    print("Seeded sample faculty data.")

if __name__ == "__main__":
    seed_faculty()
