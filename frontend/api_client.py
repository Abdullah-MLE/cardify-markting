"""API Client for connecting Streamlit to FastAPI."""
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/api/v1"

def _handle_response(resp):
    try:
        data = resp.json()
    except Exception:
        data = resp.text
        
    if not resp.ok:
        error_msg = data.get("detail") if isinstance(data, dict) else str(data)
        st.error(f"API Error: {error_msg}")
        return None
    return data

class APIClient:
    # --- Auth ---
    @staticmethod
    def login(username, password):
        resp = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
        if not resp.ok:
            return {"error": resp.json().get("detail", "Login failed")}
        return resp.json()

    # --- Companies ---
    @staticmethod
    def get_companies():
        resp = requests.get(f"{API_URL}/companies/")
        return _handle_response(resp) or []

    @staticmethod
    def get_company(company_id):
        resp = requests.get(f"{API_URL}/companies/{company_id}")
        return _handle_response(resp)

    @staticmethod
    def create_company(data):
        resp = requests.post(f"{API_URL}/companies/", json=data)
        return _handle_response(resp)

    @staticmethod
    def update_company(company_id, data):
        resp = requests.put(f"{API_URL}/companies/{company_id}", json={"data": data})
        return _handle_response(resp)

    @staticmethod
    def delete_company(company_id):
        resp = requests.delete(f"{API_URL}/companies/{company_id}")
        return _handle_response(resp)

    @staticmethod
    def get_users(company_id):
        resp = requests.get(f"{API_URL}/companies/{company_id}/users")
        return _handle_response(resp) or []

    @staticmethod
    def create_user(company_id, username, password, role):
        data = {"company_id": company_id, "username": username, "password": password, "role": role}
        resp = requests.post(f"{API_URL}/companies/users", json=data)
        return _handle_response(resp)

    @staticmethod
    def scrape_company(url, company_id):
        resp = requests.post(f"{API_URL}/companies/scrape_and_update", json={"url": url, "company_id": company_id})
        return _handle_response(resp)

    @staticmethod
    def edit_company_profile(company_data, notes, company_id):
        data = {"company_data": company_data, "notes": notes, "company_id": company_id}
        resp = requests.post(f"{API_URL}/companies/edit_and_update", json=data)
        return _handle_response(resp)

    # --- Campaigns ---
    @staticmethod
    def get_campaigns(company_id):
        resp = requests.get(f"{API_URL}/campaigns/company/{company_id}")
        return _handle_response(resp) or []

    @staticmethod
    def create_campaign(data):
        resp = requests.post(f"{API_URL}/campaigns/", json=data)
        return _handle_response(resp)

    @staticmethod
    def update_campaign(campaign_id, data):
        resp = requests.put(f"{API_URL}/campaigns/{campaign_id}", json={"data": data})
        return _handle_response(resp)

    @staticmethod
    def generate_ai_plan(campaign_id, company_id, camp_data, user_brief):
        data = {
            "campaign_id": campaign_id,
            "company_id": company_id,
            "camp_data": camp_data,
            "user_brief": user_brief
        }
        resp = requests.post(f"{API_URL}/campaigns/generate_plan", json=data)
        res = _handle_response(resp)
        return res.get("ai_plan") if res else None

    @staticmethod
    def generate_campaign_content(campaign_id, company_id, camp_data, ai_plan_text, user_brief):
        data = {
            "campaign_id": campaign_id,
            "company_id": company_id,
            "camp_data": camp_data,
            "ai_plan_text": ai_plan_text,
            "user_brief": user_brief
        }
        resp = requests.post(f"{API_URL}/campaigns/generate_content", json=data)
        return _handle_response(resp)

    # --- Content ---
    @staticmethod
    def get_scheduled_content(company_id):
        resp = requests.get(f"{API_URL}/content/company/{company_id}")
        return _handle_response(resp) or []

    @staticmethod
    def create_content(data):
        resp = requests.post(f"{API_URL}/content/", json={"data": data})
        return _handle_response(resp)

    @staticmethod
    def update_content(content_id, data):
        resp = requests.put(f"{API_URL}/content/{content_id}", json={"data": data})
        return _handle_response(resp)

    @staticmethod
    def delete_content(content_id):
        resp = requests.delete(f"{API_URL}/content/{content_id}")
        return _handle_response(resp)

    @staticmethod
    def create_single_post(company_id, h1, notes="", campaign_id=None, publish_date=None, publish_time=None):
        data = {
            "company_id": company_id, 
            "h1": h1, 
            "notes": notes,
            "campaign_id": campaign_id,
            "publish_date": str(publish_date) if publish_date else None,
            "publish_time": publish_time
        }
        resp = requests.post(f"{API_URL}/content/single_post", json=data)
        return _handle_response(resp)

    @staticmethod
    def generate_media(content_id, template_id, user_instructions):
        data = {"template_id": template_id, "user_instructions": user_instructions}
        resp = requests.post(f"{API_URL}/content/{content_id}/generate_media", json=data)
        res = _handle_response(resp)
        return res.get("urls") if res else []

    @staticmethod
    def edit_media(content_id, notes, slide_index=None):
        data = {"notes": notes, "slide_index": slide_index}
        resp = requests.post(f"{API_URL}/content/{content_id}/edit_media", json=data)
        res = _handle_response(resp)
        return res.get("url") if res else None

    @staticmethod
    def upload_image(file_bytes, filename="uploaded.png", content_type="image/png"):
        files = {"file": (filename, file_bytes, content_type)}
        resp = requests.post(f"{API_URL}/content/upload", files=files)
        res = _handle_response(resp)
        return res.get("url") if res else None

    # --- Templates ---
    @staticmethod
    def get_templates(company_id):
        resp = requests.get(f"{API_URL}/templates/company/{company_id}")
        return _handle_response(resp) or []

    @staticmethod
    def create_template(data):
        resp = requests.post(f"{API_URL}/templates/", json=data)
        return _handle_response(resp)

    @staticmethod
    def update_template(template_id, data):
        resp = requests.put(f"{API_URL}/templates/{template_id}", json=data)
        return _handle_response(resp)

    @staticmethod
    def delete_template(template_id):
        resp = requests.delete(f"{API_URL}/templates/{template_id}")
        return _handle_response(resp)

    @staticmethod
    def analyze_template(post_url, company_id):
        resp = requests.post(f"{API_URL}/templates/analyze", json={"post_url": post_url, "company_id": company_id})
        return _handle_response(resp)

    @staticmethod
    def extract_template(analysis, company_id, post_url, instructions):
        data = {
            "analysis": analysis,
            "company_id": company_id,
            "post_url": post_url,
            "instructions": instructions
        }
        resp = requests.post(f"{API_URL}/templates/extract", json=data)
        return _handle_response(resp)

    @staticmethod
    def prompt_template(company_id, prompt, aspect_ratio):
        data = {"company_id": company_id, "prompt": prompt, "aspect_ratio": aspect_ratio}
        resp = requests.post(f"{API_URL}/templates/prompt", json=data)
        return _handle_response(resp)

    @staticmethod
    def edit_template(template_id, notes):
        resp = requests.post(f"{API_URL}/templates/{template_id}/edit", json={"notes": notes})
        res = _handle_response(resp)
        return res.get("url") if res else None

    @staticmethod
    def create_template_from_image(company_id, post_url, instructions=""):
        data = {
            "company_id": company_id,
            "post_url": post_url,
            "instructions": instructions
        }
        resp = requests.post(f"{API_URL}/templates/create_from_image", json=data)
        return _handle_response(resp)
