import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import os
import re
import json
import pickle
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="SEOOptimizer Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main background - matching sidebar theme */
    .main {
        background: linear-gradient(135deg, #1a2332 0%, #2a3f5f 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Sidebar text color */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] .stText,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] strong {
        color: #ffffff !important;
    }
    
    /* Sidebar info box */
    [data-testid="stSidebar"] .stAlert {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stAlert p,
    [data-testid="stSidebar"] .stAlert strong,
    [data-testid="stSidebar"] .stAlert li {
        color: #ffffff !important;
    }
    
    /* Chat history buttons */
    [data-testid="stSidebar"] button {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* Main content styling - dark theme */
    .main .stMarkdown {
        background: rgba(30, 60, 114, 0.3);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Main content text color - white for dark theme */
    .main p, .main span, .main div, .main li, .main code {
        color: #ffffff !important;
    }
    
    /* Chat messages - dark theme */
    [data-testid="stChatMessage"] {
        background: rgba(42, 63, 95, 0.6);
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        padding: 16px;
        margin: 8px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* User message */
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* User message text should be white */
    [data-testid="stChatMessage"][data-testid*="user"] p,
    [data-testid="stChatMessage"][data-testid*="user"] span,
    [data-testid="stChatMessage"][data-testid*="user"] div {
        color: white !important;
    }
    
    /* Assistant message - dark theme */
    [data-testid="stChatMessage"][data-testid*="assistant"] {
        background: rgba(42, 82, 152, 0.4);
        border-left: 4px solid #667eea;
        color: #ffffff !important;
    }
    
    /* Chat message text color - white for dark theme */
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] code,
    [data-testid="stChatMessage"] strong,
    [data-testid="stChatMessage"] em {
        color: #ffffff !important;
    }
    
    /* Input styling - dark theme */
    [data-testid="stChatInputContainer"] {
        margin-top: 20px;
        padding: 20px;
        background: rgba(30, 60, 114, 0.5);
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Buttons styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Expander styling - dark theme */
    .streamlit-expanderHeader {
        background-color: rgba(42, 63, 95, 0.6);
        border-radius: 8px;
        padding: 12px;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Metrics styling */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #667eea;
    }
    
    /* Divider */
    hr {
        margin: 20px 0;
        border: none;
        border-top: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
    
    /* Typography improvements - light colors for dark theme */
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
    }
    
    h2 {
        color: #e0e7ff !important;
        font-weight: 600 !important;
    }
    
    h3 {
        color: #a5b4fc !important;
        font-weight: 500 !important;
    }
    
    /* Caption styling - light for dark theme */
    .stCaption {
        color: #cbd5e1 !important;
        font-size: 14px !important;
    }
    
    /* Metrics text color for dark theme */
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] div {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Storage directory for chat persistence
STORAGE_DIR = Path(".streamlit_chat_storage")
STORAGE_DIR.mkdir(exist_ok=True)
CHATS_FILE = STORAGE_DIR / "chats.pkl"

def load_chats_from_disk():
    """Load chats from disk storage"""
    try:
        if CHATS_FILE.exists():
            with open(CHATS_FILE, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        st.warning(f"Could not load previous chats: {e}")
    return {}

def save_chats_to_disk(chats):
    """Save chats to disk storage"""
    try:
        with open(CHATS_FILE, 'wb') as f:
            pickle.dump(chats, f)
    except Exception as e:
        st.error(f"Could not save chats: {e}")

# Initialize session state for chats - Load from disk on first run
if 'all_chats' not in st.session_state:
    st.session_state.all_chats = load_chats_from_disk()
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'initialized' not in st.session_state:
    st.session_state.initialized = True

class SEOOptimizer:
    def __init__(self):
        self.model = None
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize Gemini model with better error handling"""
        try:
            api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyCOohRI6K6SS70hWLbPGU11Ak7nbd3Xx5w")
            
            if api_key and api_key.startswith("AIza"):
                genai.configure(api_key=api_key)
                
                model_names = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]
                
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        break
                    except Exception:
                        continue
            else:
                pass
                
        except Exception as e:
            pass
    
    def _is_url(self, text: str) -> bool:
        """Check if text is a valid URL"""
        text = text.strip()
        
        url_patterns = [
            r'^https?://',
            r'^www\.',
            r'\.[a-z]{2,}/?$',
            r'^[a-z0-9-]+(\.[a-z0-9-]+)+\.(com|org|net|io|co|in|co\.uk)/?$'
        ]
        
        for pattern in url_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def get_ai_response(self, user_input: str, website_data: Optional[Dict] = None) -> str:
        """Get comprehensive AI response for ANY question"""
        try:
            if not self.model:
                return self._get_fallback_response(user_input, website_data)
            
            prompt = self._build_comprehensive_prompt(user_input, website_data)
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text
            else:
                return self._get_fallback_response(user_input, website_data)
            
        except Exception as e:
            return self._get_fallback_response(user_input, website_data)
    
    def _build_comprehensive_prompt(self, user_input: str, website_data: Optional[Dict] = None) -> str:
        """Build comprehensive prompt for ANY question"""
        
        is_url = self._is_url(user_input)
        
        if is_url and website_data and website_data.get('status') == 'success':
            return f"""You are a professional SEO expert with years of experience. Provide a COMPLETE, detailed, actionable response.

USER QUESTION: "{user_input}"

WEBSITE DATA PROVIDED:
- URL: {user_input}
- Title: {website_data.get('title', 'Not found')}
- Meta Description: {website_data.get('meta_description', 'Not found')}
- H1 Tags: {website_data.get('h1_tags', [])}
- Word Count: {website_data.get('word_count', 0)} words
- Content Preview: {website_data.get('content', '')[:500]}

INSTRUCTIONS:
1. Provide a COMPLETE SEO audit and analysis
2. Include specific, actionable recommendations
3. Identify technical SEO issues
4. Suggest on-page SEO improvements
5. Provide content optimization tips
6. List priority actions
7. Include tools to use
8. Give expected timelines for improvements
9. Be detailed, practical, and helpful
10. Use clear formatting with headers and bullet points

START YOUR ANALYSIS:"""
        
        elif is_url:
            return f"""You are a professional SEO expert. Analyze this website URL and provide comprehensive SEO recommendations.

WEBSITE URL: {user_input}

INSTRUCTIONS:
1. Provide a complete SEO analysis based on the URL
2. Discuss on-page SEO optimization opportunities
3. Cover technical SEO considerations
4. Suggest content strategy improvements
5. Recommend off-page SEO tactics
6. List tools to analyze further
7. Provide actionable steps to improve rankings
8. Be specific and practical

START YOUR ANALYSIS:"""
        
        else:
            return f"""You are a professional SEO expert, digital marketer, and strategist with deep expertise in all areas of search engine optimization and digital marketing.

USER QUESTION: "{user_input}"

INSTRUCTIONS:
1. Understand the exact question being asked
2. Provide a COMPLETE, comprehensive answer
3. If it's about SEO: Include best practices, tools, timelines, and examples
4. If it's about content: Give detailed strategies and actionable steps
5. If it's about tools: Explain features, pricing, and use cases
6. If it's about strategy: Provide a complete roadmap with priorities
7. If it's about problems: Give solutions, workarounds, and prevention tips
8. Include practical examples and case studies
9. List recommended tools or resources
10. Format with clear headers, bullet points, and numbered lists
11. Be thorough but concise
12. Add pro tips and best practices
13. Mention common mistakes to avoid
14. If applicable, provide expected results and timelines

If the question is unclear, interpret it in the most helpful way possible.

START YOUR ANSWER:"""
    
    def _get_fallback_response(self, user_input: str, website_data: Optional[Dict] = None) -> str:
        """Comprehensive fallback response"""
        
        is_url = self._is_url(user_input)
        
        if is_url and website_data and website_data.get('status') == 'success':
            return f"""### SEO Analysis for {user_input}

**Website Overview:**
- Title Tag: {website_data.get('title', 'Not found')}
- Meta Description: {website_data.get('meta_description', 'Not found')}
- H1 Headings: {len(website_data.get('h1_tags', []))} found
- Content Length: {website_data.get('word_count', 0)} words

**SEO Recommendations:**

**1. On-Page SEO**
- Optimize title tag (keep under 60 characters)
- Write compelling meta descriptions (150-160 characters)
- Ensure proper H1, H2, H3 hierarchy
- Add internal links to related content
- Optimize for target keywords naturally

**2. Technical SEO**
- Ensure mobile-friendly design
- Improve page loading speed (<3 seconds)
- Fix any crawl errors
- Implement structured data/schema markup
- Ensure HTTPS security

**3. Content Optimization**
- Update content to be more comprehensive
- Add relevant keywords naturally
- Include examples and case studies
- Add visual elements (images, videos)
- Ensure content solves user problems

**4. Off-Page SEO**
- Build quality backlinks from authoritative sites
- Get mentions on industry websites
- Engage on social media
- Guest post on relevant blogs

**Tools to Use:** Google Search Console, PageSpeed Insights, SEMrush, Ahrefs

**Expected Results:** 2-8 weeks for initial improvements"""
        
        elif is_url:
            return f"""### SEO Analysis Plan for {user_input}

**Immediate Actions:**
1. Check robots.txt and XML sitemap
2. Test mobile responsiveness
3. Run PageSpeed audit
4. Check for SSL certificate
5. Analyze title tags and meta descriptions

**On-Page Optimization:** Optimize all page titles, meta descriptions, heading structure, internal linking, and content quality

**Technical SEO:** Fix 404 errors, improve site speed, enable compression, implement caching, add structured data

**Off-Page SEO:** Build authoritative backlinks, create shareable content, engage on social media, get industry mentions"""
        
        else:
            return f"""### Answer to Your Question

**Core Concepts:**
- Understand the fundamentals
- Learn industry best practices
- Follow proven strategies

**Practical Implementation:**
- Step-by-step instructions
- Tools and resources needed
- Timeline expectations

**Common Mistakes to Avoid:**
- Identify pitfalls
- Learn from others' errors
- Optimize your approach

**Quick Start:**
1. Gather necessary information
2. Plan your approach
3. Implement step-by-step
4. Monitor and adjust

For more specific details, feel free to ask follow-up questions!"""

def extract_website_content(url: str) -> Dict:
    """Extract content from website with better error handling"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for element in soup(["script", "style"]):
            element.decompose()
        
        title = soup.find('title')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        h1_tags = soup.find_all('h1')
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        content = ' '.join(line for line in lines if line)
        
        return {
            'title': title.get_text() if title else 'Not found',
            'meta_description': meta_desc.get('content') if meta_desc else 'Not found',
            'h1_tags': [h1.get_text().strip() for h1 in h1_tags],
            'content': content[:1000],
            'word_count': len(content.split()),
            'status': 'success'
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def create_new_chat():
    """Create a new chat session"""
    chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.all_chats[chat_id] = {
        'id': chat_id,
        'title': 'New Chat',
        'messages': [],
        'created': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []
    save_chats_to_disk(st.session_state.all_chats)
    st.rerun()

def load_chat(chat_id):
    """Load a saved chat"""
    if chat_id in st.session_state.all_chats:
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = st.session_state.all_chats[chat_id]['messages'].copy()
        st.rerun()

def delete_chat(chat_id):
    """Delete a chat"""
    if chat_id in st.session_state.all_chats:
        # Check if we're deleting the current chat
        is_current = st.session_state.current_chat_id == chat_id
        
        # Delete the chat
        del st.session_state.all_chats[chat_id]
        
        # Save to disk immediately
        save_chats_to_disk(st.session_state.all_chats)
        
        # If we deleted the current chat, reset
        if is_current:
            # Find another chat to switch to, or create new
            if st.session_state.all_chats:
                # Load the most recent chat
                latest_chat_id = sorted(st.session_state.all_chats.keys(), reverse=True)[0]
                st.session_state.current_chat_id = latest_chat_id
                st.session_state.messages = st.session_state.all_chats[latest_chat_id]['messages'].copy()
            else:
                # No chats left, will create new one
                st.session_state.current_chat_id = None
                st.session_state.messages = []
        
        st.rerun()

def save_current_chat():
    """Save the current chat to history"""
    if st.session_state.current_chat_id:
        if st.session_state.messages:
            first_user_msg = next((m['content'] for m in st.session_state.messages if m['role'] == 'user'), 'New Chat')
            title = first_user_msg[:45] + '...' if len(first_user_msg) > 45 else first_user_msg
            
            st.session_state.all_chats[st.session_state.current_chat_id] = {
                'id': st.session_state.current_chat_id,
                'title': title,
                'messages': st.session_state.messages.copy(),
                'created': st.session_state.all_chats[st.session_state.current_chat_id].get('created', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            }
            # Save to disk after every message
            save_chats_to_disk(st.session_state.all_chats)

def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 💬 Chat History")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("New Chat", use_container_width=True):
                create_new_chat()
        
        st.markdown("---")
        
        if st.session_state.all_chats:
            st.markdown("#### Recent Conversations")
            
            # Create a list to track which chat to delete
            chat_to_delete = None
            
            for chat_id in sorted(st.session_state.all_chats.keys(), reverse=True):
                chat = st.session_state.all_chats[chat_id]
                is_active = st.session_state.current_chat_id == chat_id
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    active_indicator = "▶ " if is_active else "  "
                    if st.button(f"{active_indicator}{chat['title']}", use_container_width=True, key=f"load_{chat_id}"):
                        load_chat(chat_id)
                
                with col2:
                    if st.button("🗑", key=f"delete_{chat_id}", help="Delete chat", type="secondary"):
                        chat_to_delete = chat_id
            
            # Delete chat after the loop
            if chat_to_delete:
                delete_chat(chat_to_delete)
        else:
            st.markdown("*No conversations yet*")
        
        st.markdown("---")
        st.caption(f"Total: {len(st.session_state.all_chats)} chats")
        
        st.markdown("#### About")
        st.info("""
        **SEO Optimizer Agent** - Your AI-powered SEO assistant
        
        - Analyze websites
        - Answer SEO questions
        - Get actionable recommendations
        - Save all conversations
        - **Chats persist after reload!**
        """)
    
    # Main content
    st.markdown("# 🔍 SEO Optimizer Agent")
    st.markdown("*AI-powered SEO assistant - Ask anything about SEO, marketing, or websites*")
    
    if not st.session_state.current_chat_id:
        create_new_chat()
    
    seo_ai = SEOOptimizer()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Welcome message
    if not st.session_state.messages:
        welcome = """
### Welcome to SEO Optimizer Agent

I can help you with anything SEO-related. Just ask naturally - no need to specify what you want!

#### Example Questions:

**Website Analysis**
- Analyze example.com
- SEO audit for my-website.com

**SEO Questions**
- What is SEO and how does it work?
- How to improve website ranking?
- Best practices for on-page SEO?

**Tool Questions**
- Best SEO tools in 2024?
- Compare Ahrefs vs SEMrush
- Free keyword research tools?

**Strategy Questions**
- How to create a content strategy?
- Best way to build backlinks?
- How to rank for competitive keywords?

**Technical Questions**
- How to make my website faster?
- What are meta tags?
- How to optimize images for SEO?

I'll provide complete, detailed answers to every question!

**💾 Your chats will be saved and persist even after page reload!**
        """
        
        st.markdown(welcome)
        st.session_state.messages.append({"role": "assistant", "content": welcome})
        save_current_chat()
    
    # User input
    user_input = st.chat_input("Ask me anything...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Process and respond
        with st.chat_message("assistant"):
            with st.spinner("Processing your question..."):
                is_url_input = SEOOptimizer()._is_url(user_input)
                
                website_data = None
                if is_url_input:
                    website_data = extract_website_content(user_input)
                    
                    if website_data['status'] == 'success':
                        with st.expander("Website Data", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("H1 Tags", len(website_data['h1_tags']))
                            with col2:
                                st.metric("Word Count", website_data['word_count'])
                            with col3:
                                has_meta = "Found" if website_data['meta_description'] != 'Not found' else "Missing"
                                st.metric("Meta Description", has_meta)
                
                # Get AI response
                response = seo_ai.get_ai_response(user_input, website_data)
                st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                save_current_chat()

if __name__ == "__main__":
    main()