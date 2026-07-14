from supabase import create_client, Client
from config import config

class SupabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            cls._instance.client = None
            url: str = config.SUPABASE_URL
            key: str = config.SUPABASE_KEY
            if url and key:
                try:
                    cls._instance.client = create_client(url, key)
                except Exception as e:
                    print(f"Error creating Supabase client: {e}")
                    cls._instance = None
        return cls._instance

    @classmethod
    def get_client(cls) -> Client:
        manager = cls()
        if manager is None:
            return None
        return manager.client
