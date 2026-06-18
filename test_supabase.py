import sys
from libs.SupabaseClient.supabase_client import SupabaseManager

client = SupabaseManager.get_client()
res = client.table("campaigns").select("*").limit(1).execute()
print("Campaigns columns:", res.data[0].keys() if res.data else "No data")

res2 = client.table("content").select("*").limit(1).execute()
print("Content columns:", res2.data[0].keys() if res2.data else "No data")
