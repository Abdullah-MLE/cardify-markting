from libs.SupabaseClient.supabase_client import SupabaseManager

def authenticate_user(username, password):
    client = SupabaseManager.get_client()
    if not client:
        return {"error": "Database not connected"}
        
    try:
        # Simple plain text password check for MVP
        response = client.table("users").select("*").eq("username", username).execute()
        users = response.data
        if not users:
            return {"error": "User not found"}
            
        user = users[0]
        if user["password"] == password:
            return {"user": user}
        else:
            return {"error": "Invalid password"}
    except Exception as e:
        return {"error": str(e)}
