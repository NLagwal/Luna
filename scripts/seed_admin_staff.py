from src.services.db import db_service, Faculty
from sqlalchemy import insert
import re

def clean_name(name):
    """Removes titles and normalizes name for searching without corrupting letters."""
    name = name.lower()
    title_pattern = r'^\s*(prof\.|dr\.|professor|prof|dr|mr\.|mrs\.|ms\.|sh\.|sh|\(dr\.\))\s+'
    for _ in range(3):
        name = re.sub(title_pattern, '', name, flags=re.IGNORECASE)
    name = re.sub(r'\(dr\.?\)', '', name, flags=re.IGNORECASE)
    return " ".join(name.split()).strip()

def seed_admin_staff():
    admin_data = [
        # Registrar Office
        {
            "name": "Mr. Sanjay Kumar Verma",
            "designation": "Assistant Registrar (Academics)",
            "contact_info": "+91 01792 239362 | sanjay.tewatiya@juit.ac.in",
            "biography": "Assistant Registrar (Academics) in the Registrar Office.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Atul Sharma",
            "designation": "Personal Assistant to Registrar",
            "contact_info": "+91 01792 239377 | atul.sharma@juit.ac.in",
            "biography": "Personal Assistant to Registrar in the Registrar Office.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Amit Kumar Shrivastava",
            "designation": "Admin. Coordinator (University Division)",
            "contact_info": "+91 01792 239257 | amitk.shrivastava@juit.ac.in",
            "biography": "Admin. Coordinator in the University Division.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Chaman Lal",
            "designation": "Admin. Coordinator (University Division)",
            "contact_info": "+91 01792 239551 | chaman.lal@juit.ac.in",
            "biography": "Admin. Coordinator in the University Division.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Arindam Das",
            "designation": "Asst. Admin. Officer (University Division)",
            "contact_info": "+91 01792 239379 | arindam.das@juit.ac.in",
            "biography": "Asst. Admin. Officer in the University Division.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Dinesh Singh",
            "designation": "Asstt. Admin Officer (University Division)",
            "contact_info": "+91 01792 239364 | dinesh.singh@juit.ac.in",
            "biography": "Asstt. Admin Officer in the University Division.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Harendra Kumar",
            "designation": "Lab Engineer (University Division)",
            "contact_info": "+91 01792 239359 | harendra.kumar@juit.ac.in",
            "biography": "Lab Engineer in the University Division.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Roshan Lal",
            "designation": "Jr. Lab Assistant (University Division)",
            "contact_info": "+91 01792 239297 | roshan.lal@juit.ac.in",
            "biography": "Jr. Lab Assistant in the University Division.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Akhilesh Kumar Singh",
            "designation": "Asstt. Admin. Officer (Administration)",
            "contact_info": "+91 01792 239255 | akhilesh.singh@juit.ac.in",
            "biography": "Asstt. Admin. Officer in Administration.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. M. R. Zinta",
            "designation": "HR Head",
            "contact_info": "+91 01792 239320 | mr.zinta@juit.ac.in",
            "biography": "Human Resources Head at JUIT.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Sandeep Thakur",
            "designation": "HR Coordinator",
            "contact_info": "+91 01792 239338 | sandeep.thakur@juit.ac.in",
            "biography": "Human Resources Coordinator.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Mohinder Kapoor",
            "designation": "Personal Assistant to VC",
            "contact_info": "+91 01792 239278 | mohinder.kapoor@juit.ac.in",
            "biography": "Personal Assistant to the Vice Chancellor, Asstt. Admin. Officer.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        # Finance and Accounts Staff
        {
            "name": "Sh. Hemant Vyas",
            "designation": "Chief Finance Officer",
            "contact_info": "+91 01792239370 | hemant.vyas@juit.ac.in",
            "biography": "Chief Finance Officer (CFO) at JUIT.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Sh. Govind Nath Jha",
            "designation": "Finance Officer",
            "contact_info": "+91 01792239367 | govind.jha@juit.ac.in",
            "biography": "Finance Officer in the Accounts department.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Sh. Ravinder Singh Dogra",
            "designation": "Asstt. Finance Officer",
            "contact_info": "+91 01792239340 | ravinder.dogra@juit.ac.in",
            "biography": "Asstt. Finance Officer.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Sh. Sanjay Bhatt",
            "designation": "Asstt. Finance Officer",
            "contact_info": "+91 01792239295 | sanjay.bhatt@juit.ac.in",
            "biography": "Asstt. Finance Officer.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Sh. Manish Sharma",
            "designation": "Asstt. Finance Officer",
            "contact_info": "+91 01792239372 | manish.sharma@juit.ac.in",
            "biography": "Asstt. Finance Officer.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Sh. Pankaj Sharma",
            "designation": "Coordinator",
            "contact_info": "+91 01792-239328 | pankajsharma.accounts@juit.ac.in",
            "biography": "Accounts Coordinator.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Sh. Mahipal Singh Rawat",
            "designation": "Jr. Coordinator",
            "contact_info": "+91 01792-239372 | mahipalsingh.rawat@juit.ac.in",
            "biography": "Junior Coordinator in Finance and Accounts.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        # IT Infrastructure Staff
        {
            "name": "Mr. Sanjay Jain",
            "designation": "Principal Consultant",
            "contact_info": "+91 01792-239244 | sanjay.jain@juit.ac.in",
            "biography": "Principal Consultant in IT Infrastructure.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Ajay Nigam",
            "designation": "Sr. Consultant",
            "contact_info": "+91 01792-239244 | ajay.nigam@juit.ac.in",
            "biography": "Sr. Consultant in IT Infrastructure.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Pardeep Singh",
            "designation": "Consultant",
            "contact_info": "+91 01792-239244 | pardeep.singh@juit.ac.in",
            "biography": "Consultant in IT Infrastructure.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Ashutosh Verma",
            "designation": "Consultant",
            "contact_info": "+91 01792-239407 | ashutosh.verma@juit.ac.in",
            "biography": "Consultant in IT Infrastructure.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Ashish Tyagi",
            "designation": "Consultant",
            "contact_info": "+91 01792-239314 | ashish.tyagi@juit.ac.in",
            "biography": "Consultant in IT Infrastructure.",
            "source_url": "https://www.juit.ac.in/staff"
        },
        {
            "name": "Mr. Mahender Lal Sharma",
            "designation": "Consultant",
            "contact_info": "+91 01792-239436 | mahender.sharma@juit.ac.in",
            "biography": "Consultant in IT Infrastructure.",
            "source_url": "https://www.juit.ac.in/staff"
        }
    ]

    with db_service.SessionLocal() as session:
        for idx, staff in enumerate(admin_data, start=10001):
            staff['clean_name'] = clean_name(staff['name'])
            staff['id'] = idx
            session.merge(Faculty(**staff))
        session.commit()
    
    print(f"Seeded {len(admin_data)} administrative staff profiles.")
    db_service._load_faculty_metadata()

if __name__ == "__main__":
    seed_admin_staff()
