import os
import json
import glob
from bs4 import BeautifulSoup

def build_db():
    input_dir = 'www.juit.ac.in'
    faculty_files = glob.glob(os.path.join(input_dir, 'faculty.php?id=*'), recursive=True)
    
    faculty_db = {}

    for file_path in faculty_files:
        try:
            # Extract faculty ID from filename
            # Example: faculty.php?id=442&dep=cse&page=0
            filename = os.path.basename(file_path)
            if 'id=' not in filename: continue
            
            fid = filename.split('id=')[1].split('&')[0]
            
            # Prefer 'main' pages (no year1 param) and keep the most detailed one
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Get Name and Designation
            details_div = soup.find('div', class_='fac-details-right')
            if not details_div: continue
            
            name_tag = details_div.find('strong', class_='small-heading')
            if not name_tag: continue
            
            name = name_tag.get_text().strip()
            # Clean name (remove Dr. Prof. etc for matching)
            clean_name = name.replace('Dr.', '').replace('Prof.', '').replace('dr.', '').replace('prof.', '').strip().lower()
            
            # Get designation, phone, email and profile PDF
            designation = ""
            contact_info = ""
            profile_pdf = ""
            
            p_tag = details_div.find('p')
            if p_tag:
                text_content = p_tag.get_text(separator='|').split('|')
                lines = [line.strip() for line in text_content if line.strip()]
                if len(lines) > 1:
                    designation = lines[1]
                contact_info = " ".join(lines[1:]) # Combine the rest as contact info
                
                pdf_link = p_tag.find('a', href=True)
                if pdf_link and 'profiles/' in pdf_link['href']:
                    profile_pdf = f"https://www.juit.ac.in/{pdf_link['href']}"

            # Get Bio and Interests
            bio_div = soup.find('div', class_='faculty-bio')
            bio_text = ""
            interests = ""
            projects = ""
            additional_info = {}
            
            if bio_div:
                all_text = bio_div.get_text(separator='\n').strip()
                
                # More comprehensive list of headers to split by
                headers = [
                    'Biography :', 'Biography:', 'Area of Interest:', 'Research Interests:', 
                    'Open Project Titles:', 'Education', 'Experience', 'Expertization:',
                    'Awards & Honors:', 'Awards:', 'Honors:', 'Professional Societies:',
                    'Specialization:', 'Professional Experience:', 'Educational Background:'
                ]
                
                # Split content into parts based on headers
                content_parts = {}
                last_header = "Intro"
                current_lines = []
                
                for line in all_text.split('\n'):
                    line = line.strip()
                    if not line: continue
                    
                    found_header = False
                    for h in headers:
                        if line.startswith(h):
                            if current_lines:
                                content_parts[last_header] = "\n".join(current_lines).strip()
                            last_header = h.replace(':', '').strip()
                            current_lines = [line[len(h):].strip()]
                            found_header = True
                            break
                    
                    if not found_header:
                        current_lines.append(line)
                
                if current_lines:
                    content_parts[last_header] = "\n".join(current_lines).strip()

                # Extract specific fields from content_parts
                bio_text = content_parts.get('Biography', content_parts.get('Intro', ""))
                interests = content_parts.get('Area of Interest', content_parts.get('Research Interests', content_parts.get('Specialization', "")))
                projects = content_parts.get('Open Project Titles', "")
                
                # Store everything else in additional_info
                for k, v in content_parts.items():
                    if k not in ['Biography', 'Intro', 'Area of Interest', 'Research Interests', 'Specialization', 'Open Project Titles']:
                        additional_info[k] = v

            # Get Publication Profiles and Counts
            pub_div = soup.find('div', class_='faculty-pub')
            pub_profiles = {}
            pub_counts = {}
            if pub_div:
                # Profiles (Scholar, Scopus, etc)
                links = pub_div.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if 'scholar.google' in href: pub_profiles['google_scholar'] = href
                    elif 'scopus.com' in href: pub_profiles['scopus'] = href
                    elif 'orcid.org' in href: pub_profiles['orcid'] = href
                    elif 'researcherid' in href: pub_profiles['researcherid'] = href
                    elif 'irins' in href: pub_profiles['vidwan'] = href
                
                # Counts by year
                count_links = pub_div.find_all('a', class_='link-style')
                for cl in count_links:
                    txt = cl.get_text()
                    if '(' in txt and ')' in txt:
                        year_part = txt.split('(')[0].strip()
                        count_part = txt.split('(')[1].split(')')[0].strip()
                        if year_part.isdigit():
                            pub_counts[year_part] = count_part

            # Store in DB - overwrite only if we find a version with more content
            if fid not in faculty_db or len(bio_text) > len(faculty_db[fid].get('biography', '')):
                faculty_db[fid] = {
                    "id": fid,
                    "name": name,
                    "clean_name": clean_name,
                    "designation": designation,
                    "contact_info": contact_info,
                    "profile_pdf": profile_pdf,
                    "biography": bio_text,
                    "research_interests": interests,
                    "open_projects": projects,
                    "additional_info": additional_info,
                    "publication_profiles": pub_profiles,
                    "publication_counts": pub_counts,
                    "source_url": f"https://www.juit.ac.in/{filename}"
                }
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Save to JSON
    with open('faculty_structured_db.json', 'w', encoding='utf-8') as f:
        json.dump(faculty_db, f, indent=4)
    
    print(f"Built structured DB with {len(faculty_db)} unique faculty profiles.")

if __name__ == "__main__":
    build_db()
