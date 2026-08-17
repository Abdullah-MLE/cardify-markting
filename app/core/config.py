import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "TANSIQ.AI"
    VERSION: str = "1.0.0"
    
    SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")
    
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")

settings = Settings()
