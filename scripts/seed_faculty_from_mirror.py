import os
import json
import re
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.services.db import Faculty, Base
from src.core.config import settings

def clean_name(name):
    """Removes titles and normalizes name for searching without corrupting letters."""
    name = name.lower()
    title_pattern = r'^\s*(prof\.|dr\.|professor|prof|dr|mr\.|mrs\.|ms\.|sh\.|sh|\(dr\.\))\s+'
    for _ in range(3):
        name = re.sub(title_pattern, '', name, flags=re.IGNORECASE)
    name = re.sub(r'\(dr\.?\)', '', name, flags=re.IGNORECASE)
    return " ".join(name.split()).strip()

def extract_faculty_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")
    data = {}

    # 1. Extract from LD+JSON (Person Schema)
    all_scripts = soup.find_all("script", type="application/ld+json")
    for script in all_scripts:
        if not script.string: continue
        try:
            # Clean string from control characters
            clean_js = re.sub(r"[\x00-\x1F\x7F]", " ", script.string)
            js_data = json.loads(clean_js, strict=False)
            
            # Handle list of objects or single object
            if isinstance(js_data, list):
                persons = [obj for obj in js_data if obj.get("@type") == "Person"]
                if persons:
                    js_data = persons[0]
            
            if js_data.get("@type") == "Person":
                data['name'] = js_data.get("name")
                data['contact_info'] = js_data.get("email")
                desc = js_data.get("description", "")
                if desc:
                    data['biography'] = BeautifulSoup(desc, "html.parser").get_text(separator=" ").strip()
                data['source_url'] = js_data.get("url")
                break
        except:
            continue

    # 2. Fallbacks: Name & Designation from Title/Meta
    if not data.get('name'):
        title_tag = soup.find("title")
        if title_tag:
            # Title format: Name - Designation
            parts = title_tag.text.split("-")
            data['name'] = parts[0].strip()
            if len(parts) > 1 and not data.get('designation'):
                data['designation'] = parts[-1].strip()

    if not data.get('name') or data['name'] == "JUIT":
        return None

    data['clean_name'] = clean_name(data['name'])

    # 3. HTML Scrapers (Bio, Contact, Research)
    
    # Bio Fallback
    bio_div = soup.find("div", class_="faculty-bio")
    if bio_div:
        # Avoid overwriting if JSON had better data, but usually HTML is more complete
        bio_text = bio_div.get_text(separator=" ").strip()
        if len(bio_text) > len(data.get('biography', '')):
            data['biography'] = bio_text

    # Contact Fallback (Look for email patterns if missing)
    if not data.get('contact_info'):
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@juit\.ac\.in", html)
        if email_match:
            data['contact_info'] = email_match.group(0)

    # Research Interests & Projects
    # Often in div class="faculty-pub" or after <u>Research Interests</u>
    pub_div = soup.find("div", class_="faculty-pub")
    if pub_div:
        pub_text = pub_div.get_text(separator=" ").strip()
        if "Research Interests" in pub_text:
            parts = pub_text.split("Research Interests", 1)
            data['research_interests'] = parts[1].split("\n")[0].strip()[:500] # Cap length
        
        if "Open Project Titles" in pub_text:
             parts = pub_text.split("Open Project Titles", 1)
             data['open_projects'] = parts[1].strip()[:500]

    # Designation Fallback
    if not data.get('designation'):
        # Look for div with class 'fac-3' or similar in their breadcrumb/header
        fac_3 = soup.find("div", class_="fac-3")
        if fac_3:
            data['designation'] = fac_3.text.strip()

    # 4. Links & ID
    pdf_link = soup.find("a", href=re.compile(r"\.pdf$"))
    if pdf_link:
        href = pdf_link['href']
        data['profile_pdf'] = href if href.startswith("http") else "https://www.juit.ac.in/" + href.lstrip("/")

    id_match = re.search(r"id=(\d+)", file_path)
    if id_match:
        data['id'] = int(id_match.group(1))

    if not data.get('source_url') and id_match:
        data['source_url'] = f"https://www.juit.ac.in/faculty.php?id={id_match.group(1)}"

    return data

def seed_from_mirror(mirror_dir):
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print(f"Scanning {mirror_dir} for faculty pages...")
    processed_ids = set()
    total_count = 0

    for root, dirs, files in os.walk(mirror_dir):
        for file in files:
            if "faculty.php" in file:
                path = os.path.join(root, file)
                
                # OPTIMIZATION: Extract ID from filename first
                id_match = re.search(r"id=(\d+)", file)
                fid = None
                if id_match:
                    fid = int(id_match.group(1))
                    if fid in processed_ids:
                        continue
                
                faculty_data = extract_faculty_data(path)
                
                if faculty_data:
                    fid = faculty_data.get('id', fid)
                    if fid and fid not in processed_ids:
                        try:
                            # session.merge updates if exists, inserts if not
                            session.merge(Faculty(**faculty_data))
                            processed_ids.add(fid)
                            total_count += 1
                            if total_count % 10 == 0:
                                print(f"Synced {total_count} profiles...")
                        except Exception as e:
                            print(f"Error syncing faculty ID {fid}: {e}")
                            session.rollback()

    session.commit()
    print(f"Done! Total unique profiles synced: {total_count}")
    session.close()

if __name__ == "__main__":
    mirror_path = os.path.join(settings.ROOT_DIR, "www.juit.ac.in")
    if os.path.exists(mirror_path):
        seed_from_mirror(mirror_path)
    else:
        print("Mirror directory not found.")
