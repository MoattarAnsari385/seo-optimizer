import requests
from bs4 import BeautifulSoup
import urllib.parse
from typing import Dict, List, Optional
import re

def validate_url(url: str) -> bool:
    """Validate if the input is a proper URL"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_seo_content(url: str) -> Dict[str, any]:
    """
    Extract SEO-relevant content from a URL
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract key SEO elements
        title = soup.find('title')
        meta_description = soup.find('meta', attrs={'name': 'description'})
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        
        # Extract headings
        h1_tags = [h1.get_text().strip() for h1 in soup.find_all('h1')]
        h2_tags = [h2.get_text().strip() for h2 in soup.find_all('h2')]
        h3_tags = [h3.get_text().strip() for h3 in soup.find_all('h3')]
        
        # Extract meta robots
        meta_robots = soup.find('meta', attrs={'name': 'robots'})
        
        # Extract main content
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Calculate basic metrics
        word_count = len(content.split())
        content_preview = content[:1500] + '...' if len(content) > 1500 else content
        
        return {
            'title': title.get_text() if title else 'Not found',
            'meta_description': meta_description.get('content') if meta_description else 'Not found',
            'meta_keywords': meta_keywords.get('content') if meta_keywords else 'Not found',
            'canonical': canonical.get('href') if canonical else 'Not found',
            'meta_robots': meta_robots.get('content') if meta_robots else 'Not found',
            'h1_tags': h1_tags,
            'h2_tags': h2_tags,
            'h3_tags': h3_tags,
            'content_preview': content_preview,
            'word_count': word_count,
            'status': 'success'
        }
        
    except requests.exceptions.RequestException as e:
        return {'status': 'error', 'error': f"Network error: {str(e)}"}
    except Exception as e:
        return {'status': 'error', 'error': f"Processing error: {str(e)}"}