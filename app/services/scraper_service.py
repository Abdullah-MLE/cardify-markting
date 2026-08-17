import requests
from app.services.base_service import BaseService
from app.schemas.db_models import Company

from app.core.prompts import extract_company_system_prompt, extract_company_user_prompt


class ScraperService(BaseService):

    def scrape_website(self, url: str):
        server_url = "http://72.62.226.82:11235/md"
        payload = {
            "url": url,
            "f": "raw",
            "q": None,
            "c": "0"
        }
        response = requests.post(server_url, json=payload)
        data = response.json()
        markdown = data.get('markdown', '')
        
        if not markdown or len(markdown.strip()) < 50:
            raise ValueError("Failed to scrape website content or content is too short.")
            
        return markdown

    def extract_company_info(self, input_text: str) -> Company:
        result = self.generate_text(
            prompt=extract_company_user_prompt(input_text),
            system_instruction=extract_company_system_prompt(),
            response_schema=Company
        )
        return result
