import google.generativeai as genai
from typing import Dict

def generate_seo_report(model, website_data: Dict, url: str) -> str:
    """Generate comprehensive SEO report using Gemini AI"""
    
    prompt = f"""
    As a professional SEO consultant, analyze this website and provide actionable recommendations:

    WEBSITE: {url}
    
    CURRENT SEO ELEMENTS:
    - Title: {website_data.get('title')}
    - Meta Description: {website_data.get('meta_description')}
    - H1 Headings: {website_data.get('h1_tags', [])}
    - H2 Headings: {website_data.get('h2_tags', [])}
    - Content Length: {website_data.get('word_count')} words
    - Content Preview: {website_data.get('content_preview')[:1000]}...

    Provide your analysis in this exact structure:

    🎯 **EXECUTIVE SUMMARY**
    [Brief overview of main issues and opportunities]

    🔍 **ON-PAGE SEO ANALYSIS**
    • Title Tag Optimization
    • Meta Description Improvements  
    • Heading Structure Review
    • Content Quality Assessment

    💡 **KEYWORD OPPORTUNITIES**
    • Primary Keyword Suggestions
    • Long-Tail Variations
    • Content Gap Identification

    🛠️ **IMMEDIATE FIXES** (Quick Wins)
    • Critical Meta Tag Issues
    • Content Optimization Tasks
    • Technical Quick Fixes

    🚀 **GROWTH STRATEGY** (Medium-Term)
    • Content Expansion Ideas
    • Internal Linking Opportunities
    • User Experience Improvements

    📈 **LONG-TERM PLAN** 
    • Authority Building
    • Advanced Technical SEO
    • Competitive Positioning

    Format with clear bullet points and actionable steps. Be specific and practical.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error generating SEO report: {str(e)}"

def analyze_keyword_strategy(model, keyword: str) -> str:
    """Generate keyword strategy using Gemini AI"""
    
    prompt = f"""
    As a professional SEO strategist, analyze this keyword and provide comprehensive strategy:

    KEYWORD/TOPIC: "{keyword}"

    Provide your analysis in this exact structure:

    🎯 **KEYWORD ASSESSMENT**
    • Search Intent Analysis
    • Competition Level
    • Commercial Potential

    💡 **CONTENT STRATEGY**
    • Primary Content Ideas
    • Supporting Topic Clusters
    • Content Format Recommendations

    🔍 **KEYWORD EXPANSION**
    • Related Primary Keywords
    • Long-Tail Variations
    • Question-Based Keywords

    📊 **COMPETITOR INSIGHTS**
    • What Top Pages Are Doing Well
    • Content Gaps to Exploit
    • Unique Angle Opportunities

    🚀 **ACTION PLAN**
    • Immediate Content Tasks
    • Medium-Term Strategy
    • Long-Term Authority Building

    Be specific and provide actionable recommendations with clear next steps.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error generating keyword strategy: {str(e)}"