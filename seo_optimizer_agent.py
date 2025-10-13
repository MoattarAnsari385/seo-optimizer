import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

# Simple page config
st.set_page_config(
    page_title="SEOOptimizer Agent",
    page_icon="🔍",
    layout="centered"
)

def setup_api_key():
    """Setup API key with multiple fallbacks"""
    api_key = None
    
    # Method 1: Check secrets file
    try:
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            api_key = st.secrets['GEMINI_API_KEY']
            st.sidebar.success("✅ API key loaded from secrets")
    except Exception as e:
        st.sidebar.warning(f"Secrets file issue: {e}")
    
    # Method 2: Check environment variable
    if not api_key:
        env_key = os.getenv('GEMINI_API_KEY')
        if env_key:
            api_key = env_key
            st.sidebar.success("✅ API key loaded from environment")
    
    # Method 3: User input in sidebar
    if not api_key:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔐 FREE API Key Setup")
        api_key_input = st.sidebar.text_input(
            "Enter your FREE Gemini API Key:",
            type="password",
            placeholder="Paste your FREE API key here...",
            help="Get free API key from: https://aistudio.google.com/app/apikey"
        )
        
        if api_key_input:
            api_key = api_key_input
            st.sidebar.success("✅ FREE API key entered")
        else:
            st.sidebar.info("""
            **Get FREE API Key:**
            1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
            2. Login with Google account
            3. Click 'Create API Key' (FREE)
            4. Copy and paste above
            """)
    
    return api_key

def initialize_gemini():
    """Initialize Gemini AI for FREE tier"""
    api_key = setup_api_key()
    
    if not api_key:
        st.error("🔐 FREE API Key Required")
        st.markdown("""
        ## Free Tier Setup
        
        **Step-by-Step:**
        1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Login with your Google account
        3. Click **"Create API Key"** button
        4. Copy the **FREE** API key
        5. Paste in the sidebar input field
        
        **Free Tier Features:**
        - 60 requests per minute
        - No credit card required
        - Perfect for testing
        """)
        return None

    try:
        genai.configure(api_key=api_key)
        
        # ✅ FREE TIER MODEL - Use gemini-pro only
        model = genai.GenerativeModel("gemini-pro")
        
        # Test connection with simple prompt
        test_response = model.generate_content("Hello, respond with 'OK' if working.")
        st.sidebar.success("✅ Free tier model connected!")
        return model

    except Exception as e:
        st.error(f"❌ Free Tier Error: {str(e)}")
        st.info("""
        **Free Tier Solutions:**
        - Make sure you're using **gemini-pro** model only
        - Check if API key is valid and active
        - Free tier has 60 requests/minute limit
        - Try refreshing the page
        """)
        return None

def extract_website_content(url):
    """Extract content from website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Add https if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts and styles
        for element in soup(["script", "style"]):
            element.decompose()
        
        # Extract SEO elements
        title = soup.find('title')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        h1_tags = soup.find_all('h1')
        
        # Clean text content
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        content = ' '.join(line for line in lines if line)
        
        return {
            'title': title.get_text() if title else 'Not found',
            'meta_description': meta_desc.get('content') if meta_desc else 'Not found',
            'h1_tags': [h1.get_text().strip() for h1 in h1_tags],
            'content': content[:800],
            'word_count': len(content.split()),
            'status': 'success'
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def analyze_with_ai(model, user_input, is_url=True, website_data=None):
    """Analyze using AI"""
    if is_url:
        prompt = f"""
        As an SEO expert, analyze this website:

        URL: {user_input}
        Title: {website_data.get('title')}
        Meta Description: {website_data.get('meta_description')}
        H1 Headings: {website_data.get('h1_tags')}
        Content Length: {website_data.get('word_count')} words

        Provide actionable SEO recommendations:

        🔍 **ON-PAGE SEO ANALYSIS**
        • Title tag optimization suggestions
        • Meta description improvements
        • Heading structure review

        💡 **KEYWORD OPPORTUNITIES**
        • Primary keyword suggestions
        • Long-tail keyword ideas

        🛠️ **IMMEDIATE FIXES**
        • Quick wins to implement now

        🚀 **GROWTH STRATEGY**
        • Content expansion ideas
        • Technical improvements

        Be specific and practical. Use bullet points.
        """
    else:
        prompt = f"""
        As an SEO strategist, analyze this keyword: "{user_input}"

        Provide comprehensive strategy:

        🔍 **KEYWORD ANALYSIS**
        • Search intent assessment
        • Competition level
        • Commercial potential

        💡 **CONTENT STRATEGY**
        • Primary content ideas
        • Supporting topics
        • Content formats

        🎯 **KEYWORD EXPANSION**
        • Related keywords
        • Long-tail variations
        • Question-based keywords

        🚀 **ACTION PLAN**
        • Immediate steps
        • Long-term strategy

        Be specific and actionable. Use bullet points.
        """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Analysis error: {str(e)}"

def is_valid_url(text):
    """Check if text is a valid URL"""
    try:
        result = urllib.parse.urlparse(text)
        return all([result.scheme, result.netloc])
    except:
        return False

def main():
    """Main application"""
    st.title("🔍 SEOOptimizer Agent")
    st.caption("🎯 FREE Tier - AI-Powered SEO Analysis")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize AI model
    model = initialize_gemini()
    
    # Free tier status
    if model:
        st.sidebar.markdown("---")
        st.sidebar.success("🆓 Free Tier Active")
        st.sidebar.caption("60 requests/minute")
    
    # Reset button
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Welcome message
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            welcome_msg = """
            **Hi! I'm SEOOptimizer Agent** 🆓
            
            **Free Tier Version** - Perfect for testing!

            **I can help you with:**
            • Website SEO analysis
            • Keyword research  
            • Actionable recommendations

            **Free Tier Features:**
            ✅ 60 requests per minute
            ✅ No credit card required
            ✅ Perfect for learning SEO

            **Get started:**
            Share your website URL or keyword!
            """
            st.markdown(welcome_msg)
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
    
    # User input
    user_input = st.chat_input("Enter website URL or keyword...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Check if model is ready
        if not model:
            with st.chat_message("assistant"):
                error_msg = "Please setup your FREE Gemini API key in the sidebar to continue."
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            # Process input
            with st.chat_message("assistant"):
                with st.spinner("🔍 Analyzing..."):
                    is_url_input = is_valid_url(user_input)
                    
                    if is_url_input:
                        # URL analysis
                        website_data = extract_website_content(user_input)
                        
                        if website_data['status'] == 'success':
                            # Show basic info
                            with st.expander("📊 Website Overview", expanded=False):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Title:** {website_data['title']}")
                                    st.write(f"**H1 Count:** {len(website_data['h1_tags'])}")
                                with col2:
                                    st.write(f"**Word Count:** {website_data['word_count']}")
                                    st.write(f"**Meta Description:** {'✅ Found' if website_data['meta_description'] != 'Not found' else '❌ Missing'}")
                            
                            # AI analysis
                            analysis = analyze_with_ai(model, user_input, True, website_data)
                            response = f"**🌐 SEO Analysis for: {user_input}**\n\n{analysis}"
                        else:
                            response = f"❌ Could not analyze website: {website_data['error']}"
                    else:
                        # Keyword analysis
                        analysis = analyze_with_ai(model, user_input, False)
                        response = f"**🔑 Keyword Analysis for: '{user_input}'**\n\n{analysis}"
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()