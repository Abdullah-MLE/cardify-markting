"""
Scraper Service
Handles web scraping and text extraction.
"""
import requests
from bs4 import BeautifulSoup


class ScraperService:
    """Service to extract text from websites."""

    def scrape_website(self, url: str) -> str:
        """Scrape text content from a given URL."""
        if not url.startswith("http"):
            url = "https://" + url

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts, styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            text = soup.get_text(separator=' ', strip=True)
            
            # Basic cleanup
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            cleaned_text = '\n'.join(lines)
            
            return cleaned_text[:15000] # Limit to 15k chars for prompt safety
            
        except Exception as e:
            raise Exception(f"Failed to scrape {url}: {str(e)}")


# Module-level singleton
_scraper_service: ScraperService | None = None

def get_scraper_service() -> ScraperService:
    global _scraper_service
    if _scraper_service is None:
        _scraper_service = ScraperService()
    return _scraper_service
