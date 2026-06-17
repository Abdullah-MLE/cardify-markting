from supabase import create_client, Client
from config import config

class SupabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseManager, cls).__new__(cls)
            url: str = config.SUPABASE_URL
            key: str = config.SUPABASE_KEY
            if url and key:
                cls._instance.client: Client = create_client(url, key)
            else:
                cls._instance.client = None
        return cls._instance

    @classmethod
    def get_client(cls) -> Client:
        manager = cls()
        return manager.client
