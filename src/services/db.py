from sqlalchemy import create_engine, Column, Integer, String, JSON, Text, select
from sqlalchemy.orm import sessionmaker, declarative_base
from rapidfuzz import process, utils, fuzz
import json
import os
from src.core.config import settings

Base = declarative_base()

class Faculty(Base):
    __tablename__ = "faculty"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    clean_name = Column(String(255), nullable=False, index=True)
    designation = Column(String(255))
    biography = Column(Text)
    research_interests = Column(Text)
    open_projects = Column(Text)
    contact_info = Column(String(255))
    profile_pdf = Column(String(512))
    source_url = Column(String(512))
    additional_info = Column(JSON)
    publication_profiles = Column(JSON)
    publication_counts = Column(JSON)

class DatabaseService:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.faculty_names = []
        self.name_to_id = {}
        self._load_faculty_metadata()
        
        # Load Facts & Topics
        self.facts = self._load_json("juit_facts.json")
        self.topics = self._load_json("topics.json")

    def _load_json(self, filename):
        candidates = [
            os.path.join(settings.ROOT_DIR, "data", filename),
            os.path.join(settings.ROOT_DIR, filename)
        ]
        for path in candidates:
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
        return {}

    def _load_faculty_metadata(self):
        try:
            with self.SessionLocal() as session:
                faculty = session.execute(select(Faculty.id, Faculty.clean_name)).all()
                self.faculty_names = [f.clean_name for f in faculty]
                self.name_to_id = {f.clean_name: f.id for f in faculty}
        except Exception as e:
            print(f"Error loading faculty metadata: {e}")

    def get_faculty_by_id(self, faculty_id):
        with self.SessionLocal() as session:
            return session.get(Faculty, faculty_id)

    FACULTY_ALIASES = {
        "pkg": "pradeep kumar gupta",
        "p k g": "pradeep kumar gupta",
        "pk gupta": "pradeep kumar gupta",
        "dr pk gupta": "pradeep kumar gupta",
        "p.k. gupta": "pradeep kumar gupta",
        "dr. p.k. gupta": "pradeep kumar gupta",
        "dr p k gupta": "pradeep kumar gupta",
        "prof pkg": "pradeep kumar gupta",
        "prof. pkg": "pradeep kumar gupta",
        "pankaj kumar gupta": "pradeep kumar gupta",
        "pankaj gupta": "pradeep kumar gupta",
        "dr pankaj kumar gupta": "pradeep kumar gupta",
        "dr. pankaj kumar gupta": "pradeep kumar gupta",
        "dr pankaj gupta": "pradeep kumar gupta",
    }

    @staticmethod
    def _faculty_scorer(s1, s2, **kwargs):
        ts = fuzz.token_sort_ratio(s1, s2)
        tset = fuzz.token_set_ratio(s1, s2)
        return 0.5 * ts + 0.5 * tset

    def fuzzy_search_faculty(self, query):
        if not self.faculty_names:
            return None
        
        import re
        q_clean = query.lower().strip()
        
        # 1. Exact alias match
        if q_clean in self.FACULTY_ALIASES:
            target = self.FACULTY_ALIASES[q_clean]
            if target in self.name_to_id:
                return (target, 100.0, 0)
        
        # 2. Word boundary alias match inside multi-word query
        for alias, target in sorted(self.FACULTY_ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
            if re.search(r'\b' + re.escape(alias) + r'\b', q_clean):
                if target in self.name_to_id:
                    return (target, 100.0, 0)
        
        # 3. Hybrid fuzzy search resistant to false positive single-word matches
        match = process.extractOne(
            query, 
            self.faculty_names, 
            scorer=self._faculty_scorer, 
            processor=utils.default_process
        )
        return match

    def get_fact(self, query):
        import re
        query_lower = query.lower().strip()
        # Create normalized query without punctuation/parentheses for flexible phrase matching
        norm_query = " ".join(re.sub(r'[^\w\s]', ' ', query_lower).split())
        
        # Sort keywords by length descending so longer phrases match first
        for keyword in sorted(self.topics.keys(), key=len, reverse=True):
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, query_lower) or re.search(pattern, norm_query):
                key = self.topics[keyword]
                fact = self.facts.get(key)
                if fact:
                    # Combine brief text and verbose description for maximum context
                    combined_text = fact.get("text", "")
                    verbose = fact.get("verbose", "")
                    if verbose and verbose != combined_text:
                        combined_text = f"{combined_text} {verbose}"
                    return {"text": combined_text, "ref": fact.get("ref")}
        return None


db_service = DatabaseService()
