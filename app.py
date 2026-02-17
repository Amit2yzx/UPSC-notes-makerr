import streamlit as st
import pandas as pd
from newsapi import NewsApiClient
import google.generativeai as genai
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import plotly.graph_objects as go
import plotly.express as px
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.app_logo import add_logo
from streamlit_extras.tags import tagger_component
from streamlit_extras.chart_container import chart_container
from streamlit_extras.grid import grid
import requests
import time
from upsc_notes_generator import generate_upsc_notes, generate_quiz
import re
from bs4 import BeautifulSoup

# Set page config (must be the first Streamlit command)
st.set_page_config(
    page_title="UPSC News Analyzer & Note Maker",
    page_icon="��",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Main title styling */
    .main-title {
        font-size: 2.5rem;
        background: linear-gradient(45deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Section headers */
    .section-header {
        color: #1E3A8A;
        font-size: 1.8rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 700;
        background: linear-gradient(45deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Article container styling */
    .article-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .article-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Article title styling */
    .article-title {
        color: #1E3A8A;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Article content styling */
    .article-content {
        color: #374151;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(45deg, #1E3A8A, #3B82F6);
        color: white;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        background: linear-gradient(45deg, #3B82F6, #1E3A8A);
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Input fields styling */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        background: rgba(255, 255, 255, 0.9);
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* Date input styling */
    .stDateInput>div>div>input {
        border-radius: 10px;
        border: 1px solid #E5E7EB;
        background: rgba(255, 255, 255, 0.9);
    }
    
    /* Notes container styling */
    .notes-container {
        background: rgba(248, 250, 252, 0.9);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Quiz container styling */
    .quiz-container {
        background: rgba(240, 249, 255, 0.9);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(186, 230, 253, 0.3);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Results container styling */
    .results-container {
        background: rgba(236, 253, 245, 0.9);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(167, 243, 208, 0.3);
        backdrop-filter: blur(10px);
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 0.5rem;
        font-weight: 600;
        color: #1E3A8A;
    }
    
    /* Success message styling */
    .stSuccess {
        background: rgba(236, 253, 245, 0.9);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid rgba(167, 243, 208, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Error message styling */
    .stError {
        background: rgba(254, 242, 242, 0.9);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid rgba(254, 202, 202, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Info message styling */
    .stInfo {
        background: rgba(239, 246, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid rgba(191, 219, 254, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .stRadio > div:hover {
        background: rgba(255, 255, 255, 0.95);
        transform: translateX(5px);
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6B7280;
        font-size: 0.9rem;
        background: linear-gradient(135deg, rgba(245, 247, 250, 0.9) 0%, rgba(195, 207, 226, 0.9) 100%);
        border-radius: 15px;
        margin-top: 2rem;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Configure API keys - works both locally and on Streamlit Cloud
try:
    # Try to get from Streamlit secrets first (for cloud deployment)
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
    st.sidebar.success("API keys loaded from Streamlit secrets")
except Exception as e:
    # Fall back to environment variables (for local development)
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    st.sidebar.info("Using API keys from environment variables")
    
# Debug message for API key status
if not NEWS_API_KEY:
    st.sidebar.error("NEWS_API_KEY is missing or empty")
if not GOOGLE_API_KEY:
    st.sidebar.error("GOOGLE_API_KEY is missing or empty")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Configure News API
NEWS_API_URL = "https://newsapi.org/v2/everything"
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# Initialize session state
if 'notes' not in st.session_state:
    st.session_state.notes = {}
if 'saved_notes' not in st.session_state:
    st.session_state.saved_notes = {}
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'quiz' not in st.session_state:
    st.session_state.quiz = {}
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}

# Title and description
st.title("📚 UPSC News Analyzer & Note Maker")
st.write("Create comprehensive UPSC notes from current affairs!")

# Sidebar
st.sidebar.header("UPSC Note-Taking Guidelines")
st.sidebar.markdown("""
### Key Principles:
1. **Focus on Facts**
   - Author names
   - Organization affiliations
   - Important dates
   - Key statistics

2. **Syllabus Alignment**
   - Constitutional aspects
   - Legal implications
   - Policy impacts
   - Economic significance

3. **Note Structure**
   - Brief and concise
   - Issue-based approach
   - Subject-wise organization
   - Regular updates
""")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Date range selection
    today = datetime.now()
    last_week = today - timedelta(days=7)
    
    # Initialize date range in session state if not exists
    if 'date_range' not in st.session_state:
        st.session_state.date_range = (last_week, today)
    
    # Date range selection with session state
    date_range = st.date_input(
        "Select Date Range",
        value=st.session_state.date_range,
        max_value=today
    )
    
    # Update session state with new date range
    st.session_state.date_range = date_range

    # Define UPSC-relevant sources and domains
    upsc_sources = [
        'the-hindu',
        'the-times-of-india',
        'the-indian-express',
        'the-wire',
        'scroll-in',
        'the-quint'
    ]
    
    # Fetch news
    try:
        if len(date_range) == 2:  # Ensure we have both start and end dates
            from_date = date_range[0].strftime('%Y-%m-%d')
            to_date = date_range[1].strftime('%Y-%m-%d')
            
            st.write(f"Fetching news from {from_date} to {to_date}")
            
            # First try using the newsapi client
            try:
                news = newsapi.get_everything(
                    sources=','.join(upsc_sources),
                    from_param=from_date,
                    to=to_date,
                    language='en',
                    sort_by='publishedAt',
                    page_size=10
                )
            except Exception as e:
                st.warning(f"Error with newsapi client: {str(e)}")
                # Fall back to using fetch_news function with requests
                articles = fetch_news("UPSC", from_date, to_date)
                if articles:
                    news = {"status": "ok", "totalResults": len(articles), "articles": articles}
                else:
                    news = {"status": "error", "totalResults": 0, "articles": []}

            # Display news articles
            st.header("Current Affairs")
            
            if news['status'] == 'ok' and news['totalResults'] > 0:
                for article in news['articles']:
                    # Create a container for each article
                    article_container = st.container()
                    
                    with article_container:
                        # Article header with title and link
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                            <h3>{article['title']}</h3>
                            <a href="{article['url']}" target="_blank" style="text-decoration: none;">
                                <span style="font-size: 20px;">🔗</span>
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Article content in an expander
                        with st.expander("View Article Details"):
                            # Article content
                            st.write(article['description'])
                            st.write(f"Source: {article['source']['name']}")
                            st.write(f"Published: {article['publishedAt']}")
                            
                            # Note taking and Quiz section
                            st.subheader("UPSC Notes & Quiz")
                            
                            # Create two columns for buttons
                            button_col1, button_col2 = st.columns(2)
                            
                            with button_col1:
                                if st.button("Generate UPSC Notes", key=f"generate_{article['title']}"):
                                    with st.spinner("Generating UPSC notes..."):
                                        try:
                                            notes = generate_upsc_notes(article['title'], article['description'])
                                            if notes:
                                                st.session_state.notes[article['title']] = notes
                                                st.success("Notes generated successfully!")
                                                
                                                # Display the generated notes
                                                st.markdown(notes)
                                                
                                                # Add a divider between articles
                                                st.markdown("---")
                                        except Exception as e:
                                            st.error(f"Error generating notes: {str(e)}")
                                            st.info("Please check your Gemini API key configuration")
                            
                            with button_col2:
                                if st.button("Generate Quiz", key=f"quiz_{article['title']}"):
                                    with st.spinner("Generating quiz..."):
                                        try:
                                            quiz = generate_quiz(article)
                                            if quiz:
                                                st.session_state.quiz = quiz
                                                st.session_state.quiz_title = article['title']
                                                st.session_state.quiz_description = article['description']
                                                st.success("Quiz generated successfully!")
                                                
                                                # Add a link to view the quiz
                                                st.markdown(f"""
                                                <div style="text-align: center; margin: 10px 0;">
                                                    <a href="/quiz" target="_blank" style="
                                                        display: inline-block;
                                                        padding: 10px 20px;
                                                        background-color: #4CAF50;
                                                        color: white;
                                                        text-decoration: none;
                                                        border-radius: 5px;
                                                        font-weight: bold;
                                                    ">
                                                        Take the Quiz 📝
                                                    </a>
                                                </div>
                                                """, unsafe_allow_html=True)
                                            else:
                                                st.error("Failed to generate quiz. Please try again.")
                                        except Exception as e:
                                            st.error(f"Error generating quiz: {str(e)}")
                                            st.info("Please check your Gemini API key configuration")
                        
                        # Add a divider between articles
                        st.markdown("---")
            else:
                st.info("No articles found for the selected criteria. Try adjusting the date range or search terms.")
        else:
            st.error("Please select both start and end dates")

    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        st.info("Please check your News API key configuration")

with col2:
    # Saved Notes Section
    st.markdown('<h2 class="section-header">📝 Saved Notes</h2>', unsafe_allow_html=True)
    if st.session_state.saved_notes:
        for title, notes in st.session_state.saved_notes.items():
            with st.expander(title):
                st.text_area("", notes, height=200, key=f"saved_{title}")
    else:
        st.info("📚 No saved notes yet. Generate notes from news articles to save them here!")

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #6B7280; font-size: 0.9rem;">
    Made with ❤️ for UPSC Aspirants
</div>
""", unsafe_allow_html=True)

def fetch_news(query, from_date, to_date):
    try:
        st.write(f"Making direct request to News API with query: {query}, from: {from_date}, to: {to_date}")
        
        if not NEWS_API_KEY:
            st.error("NEWS_API_KEY is missing or empty")
            return []
            
        params = {
            'q': query,
            'from': from_date,
            'to': to_date,
            'sortBy': 'relevancy',
            'language': 'en',
            'apiKey': NEWS_API_KEY
        }
        
        st.write("Sending request to News API...")
        response = requests.get(NEWS_API_URL, params=params)
        
        if response.status_code != 200:
            st.error(f"API returned status code {response.status_code}: {response.text}")
            return []
            
        st.write("Parsing JSON response...")
        try:
            data = response.json()
        except Exception as json_err:
            st.error(f"Failed to parse JSON response: {str(json_err)}")
            st.write(f"Response text: {response.text[:200]}...")  # Show beginning of response
            return []
        
        if not data:
            st.error("API returned empty response")
            return []
            
        if 'status' not in data:
            st.error("API response missing 'status' field")
            st.write(f"Response keys: {list(data.keys())}")
            return []
            
        if data['status'] != 'ok':
            st.error(f"API returned error status: {data.get('status')} - {data.get('message', 'No message')}")
            return []
            
        if 'articles' not in data:
            st.error("API response missing 'articles' field")
            st.write(f"Response keys: {list(data.keys())}")
            return []
        
        if not data['articles']:
            st.warning("API returned empty articles list")
            return []
        
        # Filter out articles with None values in critical fields
        valid_articles = []
        invalid_count = 0
        
        for article in data['articles']:
            if (article.get('title') and 
                article.get('description') and 
                article.get('source') and 
                isinstance(article.get('source'), dict) and
                article.get('source', {}).get('name') and
                article.get('publishedAt')):
                valid_articles.append(article)
            else:
                invalid_count += 1
        
        if invalid_count > 0:
            st.warning(f"Filtered out {invalid_count} invalid articles with missing fields")
        
        if valid_articles:
            st.success(f"Successfully fetched {len(valid_articles)} valid articles")
            return valid_articles
        else:
            st.error("No valid articles found (missing critical data in responses)")
            return []
            
    except requests.exceptions.RequestException as e:
        st.error(f"Request error fetching news: {str(e)}")
        return []
    except json.JSONDecodeError as je:
        st.error(f"JSON parsing error: {str(je)}")
        return []
    except Exception as e:
        st.error(f"Unexpected error fetching news: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return []

def parse_quiz_content(quiz_text):
    if not quiz_text:
        st.error("No quiz content to parse")
        return []
        
    questions = []
    current_question = None
    current_options = []
    
    try:
        lines = quiz_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('## Question'):
                if current_question:
                    questions.append({
                        'question': current_question,
                        'options': current_options
                    })
                current_question = line.replace('## Question', '').strip()
                current_options = []
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                current_options.append(line.strip())
        
        if current_question:
            questions.append({
                'question': current_question,
                'options': current_options
            })
        
        return questions
    except Exception as e:
        st.error(f"Error parsing quiz content: {str(e)}")
        return []

def extract_answer(quiz_text):
    if not quiz_text:
        st.error("No quiz content to extract answers from")
        return {}
        
    answers = {}
    current_question = None
    
    try:
        lines = quiz_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('## Question'):
                current_question = line.replace('## Question', '').strip()
            elif line.startswith('**Answer:**'):
                if current_question:
                    answers[current_question] = line.replace('**Answer:**', '').strip()
        
        return answers
    except Exception as e:
        st.error(f"Error extracting answers: {str(e)}")
        return {}

def fetch_article_content(url):
    """
    Fetch the full content of an article from a URL.
    
    Args:
        url (str): The URL of the article
        
    Returns:
        str: The full content of the article
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract article content
        article_content = ""
        
        # Try multiple approaches to extract content
        content_found = False
        
        # Approach 1: Look for common article content containers
        article_containers = soup.find_all(['article', 'div', 'section'], class_=re.compile(r'article|content|story|main|body|text'))
        for container in article_containers:
            # Get all text elements
            paragraphs = container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if paragraphs:
                for p in paragraphs:
                    text = p.get_text().strip()
                    if text and len(text) > 20:  # Only include substantial paragraphs
                        article_content += text + "\n\n"
                content_found = True
        
        # Approach 2: If no content found, try getting all paragraphs
        if not content_found:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 20:  # Only include substantial paragraphs
                    article_content += text + "\n\n"
            content_found = bool(article_content)
        
        # Approach 3: If still no content, try getting the main content area
        if not content_found:
            main_content = soup.find('main') or soup.find('div', role='main')
            if main_content:
                article_content = main_content.get_text(separator='\n\n', strip=True)
                content_found = True
        
        # Approach 4: Last resort - get all text but clean it up
        if not content_found:
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'header', 'footer']):
                script.decompose()
            
            # Get text and clean it up
            article_content = soup.get_text(separator='\n\n', strip=True)
            
            # Remove excessive whitespace and empty lines
            article_content = re.sub(r'\n\s*\n', '\n\n', article_content)
            article_content = re.sub(r'\s+', ' ', article_content)
            
            # Split into paragraphs and filter out short ones
            paragraphs = [p.strip() for p in article_content.split('\n\n') if len(p.strip()) > 20]
            article_content = '\n\n'.join(paragraphs)
        
        # Clean up the content
        article_content = re.sub(r'\n\s*\n', '\n\n', article_content)  # Remove excessive newlines
        article_content = re.sub(r'\s+', ' ', article_content)  # Normalize whitespace
        article_content = article_content.strip()
        
        return article_content
        
    except Exception as e:
        st.error(f"Error fetching article content: {str(e)}")
        return None

# Add a section for manual article input
st.sidebar.markdown("---")
st.sidebar.subheader("Manual Article Input")
article_url = st.sidebar.text_input("Article URL", "http://timesofindia.indiatimes.com/articleshow/120024193.cms")
if st.sidebar.button("Fetch Article"):
    with st.spinner("Fetching article content..."):
        article_content = fetch_article_content(article_url)
        if article_content:
            st.session_state.manual_article = {
                'title': "Sugar factory land to be developed as ethanol production plant",
                'description': article_content,
                'url': article_url,
                'source': {'name': 'Times of India'},
                'publishedAt': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            st.success("Article fetched successfully!")
            
            # Display the article content
            st.markdown("### Article Content")
            st.write(article_content)
            
            # Add Generate Notes button
            if st.button("Generate UPSC Notes"):
                with st.spinner("Fetching article content..."):
                    article_content = fetch_article_content(article_url)
                    if article_content:
                        with st.spinner("Generating UPSC notes..."):
                            notes = generate_upsc_notes("Article from URL", article_content)
                            if notes:
                                st.session_state.notes[article_url] = notes
                                st.success("Notes generated successfully!")
                                st.markdown(notes)
                    else:
                        st.error("Failed to fetch article content. Please try again or enter the content manually.")
        else:
            st.error("Failed to fetch article content. Please try again or enter the content manually.")

# Add a debug section for manual text input
st.sidebar.markdown("---")
st.sidebar.subheader("Manual Text Input")
manual_title = st.sidebar.text_input("Article Title", "Weekly Health Horoscope Predictions April 05, 2025: Tips for wellness and balance based on each zodiac sign, Know here")
manual_content = st.sidebar.text_area("Article Content", "This week's horoscope emphasizes health and wellness for each zodiac sign. It suggests various ways to improve physical and mental health, including exercise, proper diet, hydration, and stress management strategies. The advice aims to help individuals maintain a balanced lifestyle and enhance their overall well-being.", height=200)

if st.sidebar.button("Use Manual Input"):
    st.session_state.manual_article = {
        'title': manual_title,
        'description': manual_content,
        'url': "Manual Input",
        'source': {'name': 'Manual Input'},
        'publishedAt': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    st.success("Manual input set successfully!")
    
    # Display the article content
    st.markdown("### Article Content")
    st.write(manual_content)
    
    # Add Generate Notes button
    if st.button("Generate UPSC Notes"):
        with st.spinner("Generating UPSC notes..."):
            notes = generate_upsc_notes(manual_title, manual_content)
            if notes:
                st.session_state.notes[manual_title] = notes
                st.success("Notes generated successfully!")
                st.markdown(notes)

# Title
st.markdown('<h1 class="main-title">📰 UPSC News Analyzer</h1>', unsafe_allow_html=True)

# Sidebar for search parameters
with st.sidebar:
    st.markdown('<h2 class="section-header">Search Parameters</h2>', unsafe_allow_html=True)
    
    # Search query with icon
    st.markdown('🔍 **Search Query**')
    query = st.text_input("", "UPSC", key="search_query")
    
    # Date range with icons
    st.markdown('📅 **Date Range**')
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("From", datetime.now() - timedelta(days=7))
    with col2:
        to_date = st.date_input("To", datetime.now())
    
    # Search button with icon
    if st.button("🔍 Search News"):
        with st.spinner("🔍 Fetching news articles..."):
            articles = fetch_news(query, from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d'))
            if articles:
                st.session_state.articles = articles
                st.success(f"✨ Found {len(articles)} articles!")
            else:
                st.warning("❌ No articles found. Try different search criteria.")

# Main content area
if st.session_state.articles:
    st.markdown('<h2 class="section-header">📰 Latest News Articles</h2>', unsafe_allow_html=True)
    
    for i, article in enumerate(st.session_state.articles):
        with st.container():
            st.markdown(f"""
            <div class="article-container">
                <h3 class="article-title">{article['title']}</h3>
                <div class="article-content">
                    <p>{article['description']}</p>
                    <p><strong>Source:</strong> {article['source']['name']} | <strong>Published:</strong> {article['publishedAt']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Generate notes button with icon
            if st.button(f"📝 Generate UPSC Notes", key=f"notes_{i}"):
                with st.spinner("📚 Generating notes..."):
                    article_content = fetch_article_content(article['url'])
                    if article_content:
                        with st.spinner("✨ Creating UPSC notes..."):
                            notes = generate_upsc_notes(article['title'], article_content)
                            if notes:
                                st.session_state.notes[article['title']] = notes
                                st.success("✅ Notes generated successfully!")
                                st.markdown(f"""
                                <div class="notes-container">
                                    {notes}
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Failed to fetch article content. Please try again.")
            
            # Display notes if available
            if i in st.session_state.notes:
                st.markdown(f"""
                <div class="notes-container">
                    {st.session_state.notes[i]}
                </div>
                """, unsafe_allow_html=True)
            
            # Generate quiz button with icon
            if st.button(f"❓ Generate Quiz", key=f"quiz_{i}"):
                with st.spinner("🎯 Generating quiz..."):
                    quiz = generate_quiz(article['title'], article['description'])
                    if quiz:
                        st.session_state.quiz[article['title']] = quiz
                        st.success("✅ Quiz generated successfully!")
                        
                        # Parse quiz content
                        questions = []
                        answers = {}
                        current_question = None
                        
                        for line in quiz.split('\n'):
                            line = line.strip()
                            if line.startswith('Q'):
                                current_question = line
                                questions.append({'question': current_question})
                            elif line.startswith(('a)', 'b)', 'c)', 'd)')):
                                if current_question:
                                    if current_question not in answers:
                                        answers[current_question] = []
                                    answers[current_question].append(line)
                            elif line.startswith('Answer:'):
                                if current_question:
                                    answers[current_question] = line.replace('Answer:', '').strip()
                        
                        # Display quiz with styling
                        st.markdown(f"""
                        <div class="quiz-container">
                            <h3>📝 Quiz on {article['title']}</h3>
                        """, unsafe_allow_html=True)
                        
                        for j, q in enumerate(questions, 1):
                            st.markdown(f"**Q{j}:** {q['question']}")
                            if isinstance(answers.get(q['question']), list):
                                options = answers[q['question']]
                                selected = st.radio(
                                    "Select your answer:",
                                    options,
                                    key=f"q_{i}_{j}",
                                    label_visibility="collapsed"
                                )
                        
                        # Submit button with icon
                        if st.button("📤 Submit Quiz", key=f"submit_{i}"):
                            score = 0
                            total = len(questions)
                            
                            for j, q in enumerate(questions, 1):
                                selected = st.session_state.quiz_answers.get(f"q_{i}_{j}")
                                correct = answers.get(q['question'])
                                if selected and correct and selected.startswith(correct):
                                    score += 1
                            
                            st.markdown(f"""
                            <div class="results-container">
                                <h2>🎯 Quiz Results</h2>
                                <h3>Score: {score}/{total}</h3>
                                <p style="font-size: 1.2em;">Percentage: {(score/total)*100:.1f}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if score == total:
                                st.balloons()
                    else:
                        st.error("❌ Failed to generate quiz. Please try again.")
            
            st.markdown("---")
else:
    st.info("👈 Use the sidebar to search for news articles.")

# Add a section for specific news sources and date
st.sidebar.markdown("---")
st.markdown('<h2 class="section-header">📰 Specific News Sources</h2>', unsafe_allow_html=True)
news_source = st.sidebar.selectbox("Select News Source", ["The Hindu", "The Indian Express"])
news_date = st.sidebar.date_input("Select Date", datetime.now())

if st.sidebar.button("🔍 Fetch News"):
    with st.spinner(f"🔍 Fetching news from {news_source} for {news_date.strftime('%d %B %Y')}..."):
        # Format date for API
        formatted_date = news_date.strftime("%Y-%m-%d")
        
        # Create search query based on source
        if news_source == "The Hindu":
            query = "source:thehindu.com"
        else:  # The Indian Express
            query = "source:indianexpress.com"
        
        # Fetch news from News API using the same date for both from and to parameters
        news_url = f"https://newsapi.org/v2/everything?q={query}&from={formatted_date}&to={formatted_date}&sortBy=publishedAt&apiKey={NEWS_API_KEY}&language=en"
        response = requests.get(news_url)
        news_data = response.json()
        
        if news_data["status"] == "ok" and news_data["totalResults"] > 0:
            st.session_state.news_articles = news_data["articles"]
            st.session_state.news_date = news_date
            st.session_state.news_source = news_source
            st.success(f"Found {len(news_data['articles'])} articles from {news_source} for {news_date.strftime('%d %B %Y')}")
        else:
            st.error(f"No articles found from {news_source} for {news_date.strftime('%d %B %Y')}")

# Display news articles if available
if "news_articles" in st.session_state and st.session_state.news_articles:
    st.markdown(f"## {st.session_state.news_source} News for {st.session_state.news_date.strftime('%d %B %Y')}")
    
    for i, article in enumerate(st.session_state.news_articles):
        with st.expander(f"{i+1}. {article['title']}", expanded=False):
            st.markdown(f"**Source:** {article['source']['name']}")
            st.markdown(f"**Published:** {article['publishedAt']}")
            
            if article['urlToImage']:
                st.image(article['urlToImage'], width=600)
            
            st.markdown("**Description:**")
            st.write(article['description'])
            
            st.markdown("**Content:**")
            st.write(article['content'])
            
            st.markdown(f"[Read full article]({article['url']})")
            
            # Generate notes button
            if st.button(f"Generate UPSC Notes", key=f"notes_{i}"):
                with st.spinner("Fetching article content..."):
                    article_content = fetch_article_content(article['url'])
                    if article_content:
                        with st.spinner("Generating UPSC notes..."):
                            notes = generate_upsc_notes(article['title'], article_content)
                            if notes:
                                st.session_state.notes[article['title']] = notes
                                st.success("Notes generated successfully!")
                                st.markdown(notes)
                    else:
                        st.error("Failed to fetch article content. Please try again.")
            
            # Display notes if available
            if article['title'] in st.session_state.notes:
                st.markdown("### Generated UPSC Notes")
                st.markdown(st.session_state.notes[article['title']], unsafe_allow_html=True) 