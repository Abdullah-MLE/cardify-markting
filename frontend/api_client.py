"""API Client for connecting Streamlit directly to database services and AI services, bypassing the FastAPI HTTP server."""
import streamlit as st

API_URL = "http://127.0.0.1:8000/api/v1"  # Retained for backwards compatibility if needed

class APIClient:
    # --- Auth ---
    @staticmethod
    def login(username, password):
        from services import auth_service
        try:
            return auth_service.authenticate_user(username, password)
        except Exception as e:
            return {"error": str(e)}

    # --- Companies ---
    @staticmethod
    def get_companies():
        from services import db_services
        return db_services.get_companies() or []

    @staticmethod
    def get_company(company_id):
        from services import db_services
        return db_services.get_company_data(company_id)

    @staticmethod
    def create_company(data):
        from services import db_services
        return db_services.create_company(data)

    @staticmethod
    def update_company(company_id, data):
        from services import db_services
        return db_services.update_company(company_id, data)

    @staticmethod
    def delete_company(company_id):
        from services import db_services
        return db_services.delete_company(company_id)

    @staticmethod
    def get_users(company_id):
        from services import db_services
        return db_services.get_company_users(company_id) or []

    @staticmethod
    def create_user(company_id, username, password, role):
        from services import db_services
        data = {"company_id": company_id, "username": username, "password": password, "role": role}
        return db_services.create_user(data)

    @staticmethod
    def scrape_company(url, company_id):
        from services.scraper_service import get_scraper_service
        from services.company_service import get_company_service
        from services import db_services
        try:
            scraper = get_scraper_service()
            text = scraper.scrape_website(url)
            svc = get_company_service()
            profile = svc.extract_company_profile(text)
            
            update_data = {k: v for k, v in profile.model_dump().items() if v is not None}
            if update_data:
                db_services.update_company(company_id, update_data)
            return {"success": True, "updated_fields": list(update_data.keys())}
        except Exception as e:
            st.error(f"Scraping failed: {e}")
            return None

    @staticmethod
    def edit_company_profile(company_data, notes, company_id):
        from services.company_service import get_company_service
        from services import db_services
        try:
            svc = get_company_service()
            updated = svc.edit_company_profile(company_data, notes)
            
            update_data = {k: v for k, v in updated.model_dump().items() if v is not None}
            if update_data:
                db_services.update_company(company_id, update_data)
            return {"success": True, "updated_fields": list(update_data.keys())}
        except Exception as e:
            st.error(f"Editing profile failed: {e}")
            return None

    # --- Campaigns ---
    @staticmethod
    def get_campaigns(company_id):
        from services import db_services
        return db_services.get_campaigns(company_id) or []

    @staticmethod
    def create_campaign(data):
        from services import db_services
        return db_services.create_campaign(data)

    @staticmethod
    def update_campaign(campaign_id, data):
        from services import db_services
        # The frontend calls update_company and update_campaign with key "data" inside a wrapper dict sometimes,
        # or as raw dict. Let's extract 'data' if nested, otherwise use raw data.
        update_data = data.get("data", data) if isinstance(data, dict) else data
        return db_services.update_campaign(campaign_id, update_data)

    @staticmethod
    def generate_ai_plan(campaign_id, company_id, camp_data, user_brief):
        from services.campaign_service import get_campaign_service
        try:
            svc = get_campaign_service()
            return svc.generate_ai_plan(campaign_id, company_id, camp_data, user_brief)
        except Exception as e:
            st.error(f"Failed to generate plan: {e}")
            return None

    @staticmethod
    def generate_campaign_content(campaign_id, company_id, camp_data, ai_plan_text, user_brief):
        from services.campaign_service import get_campaign_service
        try:
            svc = get_campaign_service()
            return svc.generate_campaign_content_loop(
                campaign_id, company_id, camp_data, ai_plan_text, user_brief
            )
        except Exception as e:
            st.error(f"Failed to generate content: {e}")
            return None

    # --- Content ---
    @staticmethod
    def get_scheduled_content(company_id):
        from services import db_services
        return db_services.get_scheduled_content(company_id) or []

    @staticmethod
    def create_content(data):
        from services import db_services
        create_data = data.get("data", data) if isinstance(data, dict) else data
        return db_services.create_content(create_data)

    @staticmethod
    def update_content(content_id, data):
        from services import db_services
        update_data = data.get("data", data) if isinstance(data, dict) else data
        return db_services.update_content(content_id, update_data)

    @staticmethod
    def delete_content(content_id):
        from services import db_services
        return db_services.delete_content(content_id)

    @staticmethod
    def create_single_post(company_id, h1, notes="", campaign_id=None, publish_date=None, publish_time=None):
        from services.content_service import get_content_service
        from services import db_services
        try:
            svc = get_content_service()
            content = svc.create_single_post(company_id, h1, notes)
            content_dict = content.model_dump() if hasattr(content, 'model_dump') else content
            
            # Update routing info if provided
            update_data = {}
            if campaign_id: 
                update_data["campaign_id"] = campaign_id
            if publish_date: 
                update_data["publish_date"] = str(publish_date)
                from datetime import date
                try:
                    update_data["publish_day"] = date.fromisoformat(str(publish_date)).strftime("%A")
                except Exception:
                    pass
            if publish_time: 
                pt = publish_time
                update_data["publish_time"] = pt + ":00" if len(pt) == 5 else pt
                
            if update_data and content_dict and "id" in content_dict:
                res = db_services.update_content(content_dict["id"], update_data)
                if res and len(res) > 0:
                    content_dict.update(res[0])
                    
            return content_dict
        except Exception as e:
            st.error(f"Failed to create single post: {e}")
            return None

    @staticmethod
    def generate_media(content_id, template_id, user_instructions):
        from services.content_service import get_content_service
        try:
            svc = get_content_service()
            urls = svc.generate_content_media(content_id, template_id, user_instructions)
            return urls or []
        except Exception as e:
            st.error(f"Failed to generate media: {e}")
            return []

    @staticmethod
    def edit_media(content_id, notes, slide_index=None):
        from services.content_service import get_content_service
        try:
            svc = get_content_service()
            return svc.edit_content_media(content_id, notes, slide_index)
        except Exception as e:
            st.error(f"Failed to edit media: {e}")
            return None

    @staticmethod
    def upload_image(file_bytes, filename="uploaded.png", content_type="image/png"):
        from services import db_services
        try:
            return db_services.upload_image(file_bytes, folder="uploads")
        except Exception as e:
            st.error(f"Upload failed: {e}")
            return None

    # --- Templates ---
    @staticmethod
    def get_templates(company_id):
        from services import db_services
        return db_services.get_templates(company_id) or []

    @staticmethod
    def create_template(data):
        from services import db_services
        return db_services.create_template(data)

    @staticmethod
    def update_template(template_id, data):
        from services import db_services
        return db_services.update_template(template_id, data)

    @staticmethod
    def delete_template(template_id):
        from services import db_services
        return db_services.delete_template(template_id)

    @staticmethod
    def analyze_template(post_url, company_id):
        from services.template_service import get_template_service
        try:
            svc = get_template_service()
            analysis = svc.analyze_template(post_url, company_id)
            return analysis.model_dump() if hasattr(analysis, 'model_dump') else analysis
        except Exception as e:
            st.error(f"Failed to analyze template: {e}")
            return None

    @staticmethod
    def extract_template(analysis, company_id, post_url, instructions):
        from services.template_service import get_template_service
        from services import db_services
        from schemas.ai_models import TemplateAnalysis
        try:
            svc = get_template_service()
            analysis_obj = TemplateAnalysis(**analysis)
            tpl_bytes = svc.create_template_from_image(analysis_obj, company_id, post_url, instructions)
            tpl_url = db_services.upload_image(tpl_bytes, folder="templates")
            constraints = svc.generate_template_constraints(company_id, post_url, tpl_url)
            return {"url": tpl_url, "constraints": constraints, "aspect_ratio": analysis_obj.aspect_ratio}
        except Exception as e:
            st.error(f"Failed to extract template: {e}")
            return None

    @staticmethod
    def prompt_template(company_id, prompt, aspect_ratio):
        from services.template_service import get_template_service
        from services import db_services
        try:
            svc = get_template_service()
            tpl_bytes = svc.create_template_from_prompt(company_id, prompt, aspect_ratio)
            tpl_url = db_services.upload_image(tpl_bytes, folder="templates")
            return {"url": tpl_url}
        except Exception as e:
            st.error(f"Failed to generate template: {e}")
            return None

    @staticmethod
    def edit_template(template_id, notes):
        from services.template_service import get_template_service
        from services import db_services
        try:
            svc = get_template_service()
            new_bytes = svc.edit_template(template_id, notes)
            new_url = db_services.upload_image(new_bytes, folder="templates")
            return new_url
        except Exception as e:
            st.error(f"Failed to edit template: {e}")
            return None

    @staticmethod
    def create_template_from_image(company_id, post_url, instructions=""):
        from services.template_service import get_template_service
        from services import db_services
        try:
            svc = get_template_service()
            tpl_bytes = svc.create_template_from_image(company_id, post_url, instructions)
            tpl_url = db_services.upload_image(tpl_bytes, folder="templates")
            if not tpl_url:
                return None
            tpl_data = {
                "company_id": company_id,
                "template_url": tpl_url,
                "template_constraints": "Use this template for company brand posts. Place headline and details in empty spaces.",
                "template_info": "Extracted from Image",
                "aspect_ratio": "1:1",
                "source_post_url": post_url,
                "is_source_same_company": True
            }
            return db_services.create_template(tpl_data)
        except Exception as e:
            st.error(f"Failed to extract template: {e}")
            return None
