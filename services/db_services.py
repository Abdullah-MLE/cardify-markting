from libs.SupabaseClient.supabase_client import SupabaseManager
import streamlit as st
import io
import uuid
from PIL import Image

def get_companies():
    client = SupabaseManager.get_client()
    if not client: return []
    try:
        res = client.table("companies").select("*").execute()
        return res.data
    except:
        return []

def get_campaigns(company_id=None):
    client = SupabaseManager.get_client()
    if not client: return []
    try:
        query = client.table("campaigns").select("*")
        if company_id:
            query = query.eq("company_id", company_id)
        return query.execute().data
    except:
        return []

def get_scheduled_content(company_id=None):
    client = SupabaseManager.get_client()
    if not client: return []
    try:
        query = client.table("content").select("*")
        if company_id:
            query = query.eq("company_id", company_id)
        return query.execute().data
    except:
        return []

def get_templates(company_id=None):
    client = SupabaseManager.get_client()
    if not client: return []
    try:
        query = client.table("templates").select("*")
        if company_id:
            query = query.eq("company_id", company_id)
        return query.execute().data
    except:
        return []

def get_company_data(company_id):
    client = SupabaseManager.get_client()
    if not client or not company_id: return None
    try:
        res = client.table("companies").select("*").eq("id", company_id).execute()
        return res.data[0] if res.data else None
    except:
        return None

def update_company(company_id, update_data):
    client = SupabaseManager.get_client()
    if not client or not company_id: return None
    try:
        res = client.table("companies").update(update_data).eq("id", company_id).execute()
        return res.data
    except Exception as e:
        print(e)
        return None

def create_campaign(campaign_data):
    client = SupabaseManager.get_client()
    if not client: return None
    try:
        res = client.table("campaigns").insert(campaign_data).execute()
        return res.data
    except Exception as e:
        print(e)
        return None

def create_template(template_data):
    client = SupabaseManager.get_client()
    if not client: return None
    try:
        res = client.table("templates").insert(template_data).execute()
        return res.data
    except Exception as e:
        print(e)
        return None

def delete_template(template_id):
    client = SupabaseManager.get_client()
    if not client: return False
    try:
        client.table("templates").delete().eq("id", template_id).execute()
        return True
    except Exception as e:
        print(e)
        return False

def create_content(content_data):
    client = SupabaseManager.get_client()
    if not client: return None
    try:
        res = client.table("content").insert(content_data).execute()
        return res.data
    except Exception as e:
        print(e)
        return None

def create_company(company_data):
    client = SupabaseManager.get_client()
    if not client: return None
    try:
        res = client.table("companies").insert(company_data).execute()
        return res.data
    except Exception as e:
        print(e)
        return None

def get_company_users(company_id):
    client = SupabaseManager.get_client()
    if not client: return []
    try:
        res = client.table("users").select("*").eq("company_id", company_id).execute()
        return res.data
    except Exception as e:
        print(e)
        return []

def create_user(user_data):
    client = SupabaseManager.get_client()
    if not client: return None
    try:
        res = client.table("users").insert(user_data).execute()
        return res.data
    except Exception as e:
        print(e)
        return None

def delete_content(content_id):
    client = SupabaseManager.get_client()
    if not client: return False
    try:
        client.table("content").delete().eq("id", content_id).execute()
        return True
    except Exception as e:
        print(e)
        return False

def update_content(content_id, update_data):
    client = SupabaseManager.get_client()
    if not client: return None
    try:
        res = client.table("content").update(update_data).eq("id", content_id).execute()
        return res.data
    except Exception as e:
        print(e)
        return None

def update_campaign(campaign_id, update_data):
    client = SupabaseManager.get_client()
    if not client or not campaign_id: return None
    try:
        res = client.table("campaigns").update(update_data).eq("id", campaign_id).execute()
        return res.data
    except Exception as e:
        print(e)
        return None

def delete_campaign(campaign_id):
    client = SupabaseManager.get_client()
    if not client: return False
    try:
        client.table("campaigns").delete().eq("id", campaign_id).execute()
        return True
    except Exception as e:
        print(e)
        return False

def update_template(template_id, update_data):
    client = SupabaseManager.get_client()
    if not client or not template_id: return None
    try:
        res = client.table("templates").update(update_data).eq("id", template_id).execute()
        return res.data
    except Exception as e:
        print(e)
        return None

def delete_company(company_id):
    client = SupabaseManager.get_client()
    if not client or not company_id: return False
    try:
        # Cascade delete child tables in order
        client.table("users").delete().eq("company_id", company_id).execute()
        client.table("templates").delete().eq("company_id", company_id).execute()
        client.table("content").delete().eq("company_id", company_id).execute()
        client.table("campaigns").delete().eq("company_id", company_id).execute()
        client.table("companies").delete().eq("id", company_id).execute()
        return True
    except Exception as e:
        print(e)
        return False

def upload_image(image_bytes: bytes, bucket_name: str = "media", folder: str = "generated") -> str:
    """
    Converts image bytes to WEBP format and uploads to Supabase storage.
    Returns the public URL of the uploaded image, or None if failed.
    """
    client = SupabaseManager.get_client()
    if not client: return None
    
    try:
        # Convert to WEBP
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        webp_io = io.BytesIO()
        # Save as webp with 80 quality to optimize size while keeping quality
        img.save(webp_io, format="WEBP", quality=80)
        webp_bytes = webp_io.getvalue()
        
        # Generate unique filename
        filename = f"{folder}/{uuid.uuid4().hex}.webp"
        
        # Upload
        res = client.storage.from_(bucket_name).upload(
            path=filename,
            file=webp_bytes,
            file_options={"content-type": "image/webp"}
        )
        
        # Get public URL
        public_url = client.storage.from_(bucket_name).get_public_url(filename)
        return public_url
    except Exception as e:
        print(f"Error uploading image to Supabase: {e}")
        return None
