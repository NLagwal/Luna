import os

class Settings:
    # Project Paths
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(ROOT_DIR, "data")
    
    # Database Configuration
    DB_USER = os.getenv("DB_USER", "luna_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "luna_password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5433")
    DB_NAME = os.getenv("DB_NAME", "luna_db")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # ChromaDB Configuration
    CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8002"))
    COLLECTION_NAME = "luna_vault"

    
    # AI Models & Providers
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "omniroute")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:20128/v1")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OMNIROUTE_MODEL = os.getenv("OMNIROUTE_MODEL", "antigravity/gemini-3.6-flash-medium")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "antigravity/gemini-3.6-flash-medium")
    EMBED_MODEL = os.getenv("EMBED_MODEL", "embeddinggemma:latest")
    LLM_MODEL = os.getenv("LLM_MODEL", "gemma4:e2b")

    
    # Search Thresholds
    FUZZY_MATCH_THRESHOLD = 80
    AMBIGUITY_THRESHOLD = 65
    VECTOR_DISTANCE_THRESHOLD = 1.5  # Adjust based on distance metric
    
    # Memory
    SESSION_TTL = 3600  # 1 hour

settings = Settings()
