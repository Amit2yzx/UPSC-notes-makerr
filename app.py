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

# Set page config (must be the first Streamlit command)
st.set_page_config(
    page_title="UPSC News Analyzer & Note Maker",
    page_icon="📚",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main Theme Colors */
    :root {
        --primary-color: #2c3e50;
        --secondary-color: #3498db;
        --accent-color: #e74c3c;
        --success-color: #2ecc71;
        --warning-color: #f1c40f;
        --background-color: #f5f6fa;
        --text-color: #2c3e50;
    }

    /* Global Styles */
    .stMarkdown {
        font-family: 'Segoe UI', 'Georgia', serif;
        color: var(--text-color);
    }

    /* Header Styles */
    .stMarkdown h1 {
        color: var(--primary-color);
        border-bottom: 3px solid var(--secondary-color);
        padding-bottom: 15px;
        margin-bottom: 30px;
        font-size: 2.5em;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .stMarkdown h2 {
        color: var(--secondary-color);
        border-left: 5px solid var(--secondary-color);
        padding-left: 15px;
        margin: 20px 0;
        font-size: 1.8em;
    }

    .stMarkdown h3 {
        color: var(--primary-color);
        font-size: 1.4em;
        margin: 15px 0;
    }

    /* Article Container Styles */
    .article-container {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(0,0,0,0.1);
    }

    .article-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    /* Notes Container Styles */
    .notes-container {
        background-color: var(--background-color);
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 4px solid var(--success-color);
    }

    /* Quiz Container Styles */
    .quiz-container {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(0,0,0,0.1);
    }

    .quiz-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }

    /* Question Styles */
    .question-text {
        font-size: 1.1em;
        line-height: 1.6;
        color: var(--text-color);
        margin: 15px 0;
        padding: 10px;
        background-color: var(--background-color);
        border-radius: 8px;
    }

    /* Radio Button Styles */
    .stRadio > div {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        transition: all 0.3s ease;
    }

    .stRadio > div:hover {
        background-color: var(--background-color);
        transform: translateX(5px);
    }

    /* Feedback Styles */
    .stSuccess {
        background-color: rgba(46, 204, 113, 0.1);
        border-left: 4px solid var(--success-color);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }

    .stError {
        background-color: rgba(231, 76, 60, 0.1);
        border-left: 4px solid var(--accent-color);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }

    /* Results Container */
    .results-container {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .results-container h2 {
        color: white;
        border: none;
        font-size: 2em;
        margin-bottom: 20px;
    }

    .results-container h3 {
        color: white;
        font-size: 1.8em;
        margin: 15px 0;
    }

    /* Button Styles */
    .stButton > button {
        background-color: var(--secondary-color);
        color: white;
        border: none;
        padding: 10px 25px;
        border-radius: 25px;
        font-size: 1.1em;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Warning Message Style */
    .stWarning {
        background-color: rgba(241, 196, 15, 0.1);
        border-left: 4px solid var(--warning-color);
        padding: 15px;
        border-radius: 8px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Configure News API
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
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
            news = newsapi.get_everything(
                sources=','.join(upsc_sources),
                from_param=date_range[0].strftime('%Y-%m-%d'),
                to=date_range[1].strftime('%Y-%m-%d'),
                language='en',
                sort_by='publishedAt',
                page_size=10
            )

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
                                            prompt = f"""
                                            Create comprehensive UPSC-style notes for the following news article in a visually appealing format:
                                            Title: {article['title']}
                                            Description: {article['description']}
                                            Article URL: {article['url']}
                                            
                                            Please structure the notes using the following format:
                                            
                                            # 📌 {article['title']}
                                            
                                            ## 🔗 Source Information
                                            | Category | Details |
                                            |----------|---------|
                                            | Source | {article['source']['name']} |
                                            | Published Date | {article['publishedAt']} |
                                            | Article Link | [{article['url']}]({article['url']}) |
                                            
                                            ## 🎯 Key Facts
                                            | Category | Details |
                                            |----------|---------|
                                            | Important Dates | [List dates] |
                                            | Key People/Organizations | [List names] |
                                            | Statistics | [List key numbers] |
                                            
                                            ## ⚖️ Constitutional/Legal Aspects
                                            ### Relevant Articles
                                            - Article XXX: [Details]
                                            - Article YYY: [Details]
                                            
                                            ### Legal Implications
                                            - Point 1
                                            - Point 2
                                            
                                            ## 📚 UPSC Relevance
                                            ### Related Topics
                                            ```mermaid
                                            graph TD
                                                A[Main Topic] --> B[Subtopic 1]
                                                A --> C[Subtopic 2]
                                                B --> D[Detail 1]
                                                C --> E[Detail 2]
                                            ```
                                            
                                            ### Potential Questions
                                            1. Question 1
                                            2. Question 2
                                            
                                            ## 🌍 Additional Context
                                            ### Historical Background
                                            > Important historical context goes here
                                            
                                            ### Related Policies
                                            - Policy 1
                                            - Policy 2
                                            
                                            ### International Perspective
                                            | Country | Similar Initiatives |
                                            |---------|-------------------|
                                            | Country 1 | Initiative 1 |
                                            | Country 2 | Initiative 2 |
                                            
                                            ## 📊 Data Visualization
                                            ```mermaid
                                            pie title Distribution of Key Components
                                                "Component 1" : 30
                                                "Component 2" : 40
                                                "Component 3" : 30
                                            ```
                                            
                                            ## 📝 Summary
                                            Key takeaways in bullet points:
                                            - Point 1
                                            - Point 2
                                            
                                            ## 🔍 Quick Reference
                                            | Category | Key Points |
                                            |----------|------------|
                                            | Important Dates | [Dates] |
                                            | Key People | [Names] |
                                            | Related Topics | [Topics] |
                                            
                                            Use emojis, tables, and diagrams where appropriate to make the notes more engaging and easier to understand.
                                            Keep the information concise but comprehensive.
                                            Use different heading levels (H1, H2, H3) for better organization.
                                            Include blockquotes for important historical context.
                                            Use tables for structured data.
                                            Use mermaid diagrams for relationships and data visualization.
                                            """
                                            
                                            response = model.generate_content(prompt)
                                            if response.text:
                                                st.session_state.notes[article['title']] = response.text
                                                st.success("Notes generated successfully!")
                                                
                                                # Display the generated notes
                                                st.markdown(response.text)
                                                
                                                # Add a divider between articles
                                                st.markdown("---")
                                        except Exception as e:
                                            st.error(f"Error generating notes: {str(e)}")
                                            st.info("Please check your Gemini API key configuration")
                            
                            with button_col2:
                                if st.button("Generate Quiz", key=f"quiz_{article['title']}"):
                                    with st.spinner("Generating quiz..."):
                                        try:
                                            quiz_prompt = f"""
                                            Create a quiz with 5 multiple-choice questions based on this article:
                                            Title: {article['title']}
                                            Description: {article['description']}
                                            
                                            Format the quiz as follows:
                                            
                                            # 📝 Quick Quiz
                                            
                                            ## Question 1
                                            [Question text]
                                            
                                            A) [Option A]
                                            B) [Option B]
                                            C) [Option C]
                                            D) [Option D]
                                            
                                            **Answer:** [Correct option letter]
                                            
                                            ## Question 2
                                            [Question text]
                                            
                                            A) [Option A]
                                            B) [Option B]
                                            C) [Option C]
                                            D) [Option D]
                                            
                                            **Answer:** [Correct option letter]
                                            
                                            [Continue for all 5 questions]
                                            
                                            Make sure the questions:
                                            1. Are directly related to the article content
                                            2. Test understanding rather than just memorization
                                            3. Have clear, unambiguous answers
                                            4. Include explanations for the correct answers
                                            5. Cover different aspects of the article
                                            """
                                            
                                            quiz_response = model.generate_content(quiz_prompt)
                                            if quiz_response.text:
                                                # Store quiz in session state
                                                st.session_state.quiz = quiz_response.text
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
    st.header("📝 Saved Notes")
    if st.session_state.saved_notes:
        for title, notes in st.session_state.saved_notes.items():
            with st.expander(title):
                st.text_area("", notes, height=200, key=f"saved_{title}")
    else:
        st.info("No saved notes yet. Generate notes from news articles to save them here!")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ for UPSC Aspirants")

def fetch_news(query, from_date, to_date):
    try:
        params = {
            'q': query,
            'from': from_date,
            'to': to_date,
            'sortBy': 'relevancy',
            'language': 'en',
            'apiKey': NEWS_API_KEY
        }
        
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data and 'status' in data and data['status'] == 'ok' and 'articles' in data and data['articles']:
            # Filter out articles with None values in critical fields
            valid_articles = []
            for article in data['articles']:
                if (article.get('title') and 
                    article.get('description') and 
                    article.get('source') and 
                    article.get('source', {}).get('name') and
                    article.get('publishedAt')):
                    valid_articles.append(article)
            
            if valid_articles:
                return valid_articles
            else:
                st.error("No valid articles found (missing critical data in responses).")
                return []
        else:
            st.error("No articles found for the given criteria or API returned an error.")
            return []
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news: {str(e)}")
        return []
    except json.JSONDecodeError:
        st.error("Error parsing API response")
        return []
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []

def generate_upsc_notes(article):
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Generate UPSC-style notes from this news article:
        
        Title: {article['title']}
        Description: {article['description']}
        
        Format the notes in the following structure:
        
        # Key Points
        - Point 1
        - Point 2
        ...
        
        # Important Facts
        - Fact 1
        - Fact 2
        ...
        
        # Related Topics
        - Topic 1
        - Topic 2
        ...
        
        # UPSC Relevance
        - Relevance point 1
        - Relevance point 2
        ...
        
        Make the notes concise, factual, and relevant for UPSC preparation.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        st.error(f"Error generating notes: {str(e)}")
        return None

def generate_quiz(article):
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Generate 5 multiple choice questions based on this news article:
        
        Title: {article['title']}
        Description: {article['description']}
        
        Format each question as follows:
        
        ## Question 1
        A) Option 1
        B) Option 2
        C) Option 3
        D) Option 4
        **Answer:** A
        
        Make the questions:
        1. Clear and concise
        2. Based on key facts from the article
        3. Relevant for UPSC preparation
        4. Have only one correct answer
        5. Include explanations for the correct answer
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        st.error(f"Error generating quiz: {str(e)}")
        return None

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

# Title
st.title("📰 UPSC News Analyzer")

# Sidebar for search parameters
with st.sidebar:
    st.header("Search Parameters")
    
    # Search query
    query = st.text_input("Enter search query:", "UPSC")
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("From Date", datetime.now() - timedelta(days=7))
    with col2:
        to_date = st.date_input("To Date", datetime.now())
    
    # Search button
    if st.button("Search News"):
        with st.spinner("Fetching news articles..."):
            articles = fetch_news(query, from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d'))
            if articles:
                st.session_state.articles = articles
                st.success(f"Found {len(articles)} articles!")
            else:
                st.warning("No articles found. Try different search criteria.")

# Main content area
if st.session_state.articles:
    for i, article in enumerate(st.session_state.articles):
        with st.container():
            # Article content
            st.markdown(f"""
            <div class="article-container">
                <h2>{article['title']}</h2>
                <p>{article['description']}</p>
                <p><strong>Source:</strong> {article['source']['name']} | <strong>Published:</strong> {article['publishedAt']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Generate notes button
            if st.button(f"Generate UPSC Notes", key=f"notes_{i}"):
                with st.spinner("Generating UPSC notes..."):
                    notes = generate_upsc_notes(article)
                    if notes:
                        st.session_state.notes[i] = notes
                        st.success("Notes generated successfully!")
            
            # Display notes if available
            if i in st.session_state.notes:
                st.markdown(f"""
                <div class="notes-container">
                    {st.session_state.notes[i]}
                </div>
                """, unsafe_allow_html=True)
            
            # Generate quiz button
            if st.button(f"Generate Quiz", key=f"quiz_{i}"):
                with st.spinner("Generating quiz..."):
                    try:
                        quiz_prompt = f"""
                        Create a quiz with 5 multiple-choice questions based on this article:
                        Title: {article['title']}
                        Description: {article['description']}
                        
                        Format the quiz as follows:
                        
                        # 📝 Quick Quiz
                        
                        ## Question 1
                        [Question text]
                        
                        A) [Option A]
                        B) [Option B]
                        C) [Option C]
                        D) [Option D]
                        
                        **Answer:** [Correct option letter]
                        
                        ## Question 2
                        [Question text]
                        
                        A) [Option A]
                        B) [Option B]
                        C) [Option C]
                        D) [Option D]
                        
                        **Answer:** [Correct option letter]
                        
                        [Continue for all 5 questions]
                        
                        Make sure the questions:
                        1. Are directly related to the article content
                        2. Test understanding rather than just memorization
                        3. Have clear, unambiguous answers
                        4. Include explanations for the correct answers
                        5. Cover different aspects of the article
                        """
                        
                        quiz_response = model.generate_content(quiz_prompt)
                        if quiz_response.text:
                            # Store quiz in session state
                            st.session_state.quiz = quiz_response.text
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
            
            # Display quiz if available
            if i in st.session_state.quiz:
                # Parse quiz content
                questions = parse_quiz_content(st.session_state.quiz[i])
                answers = extract_answer(st.session_state.quiz[i])
                
                st.markdown("### 📝 Quiz")
                
                # Display each question with radio buttons
                for j, q in enumerate(questions, 1):
                    with st.container():
                        # Display question
                        st.markdown(f"""
                        <div class="quiz-container">
                            <h3>Question {j}</h3>
                            <div class="question-text">{q['question']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display options
                        if q['options']:
                            selected_option = st.radio(
                                "Select your answer:",
                                q['options'],
                                key=f"q_{i}_{j}",
                                label_visibility="collapsed"
                            )
                            
                            # Store the answer
                            st.session_state.quiz_answers[f"q_{i}_{j}"] = selected_option
                            
                            # Show feedback if answer is selected
                            if f"q_{i}_{j}" in st.session_state.quiz_answers:
                                correct_answer = answers.get(q['question'])
                                if correct_answer:
                                    if selected_option.startswith(correct_answer):
                                        st.success("🎉 Correct! Well done!")
                                    else:
                                        st.error(f"❌ Wrong! The correct answer is {correct_answer}")
                        else:
                            st.warning("No options available for this question.")
                        
                        st.markdown("---")
                
                # Add a submit button at the bottom
                if st.button("Submit Quiz", key=f"submit_{i}"):
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
            
            st.markdown("---")
else:
    st.info("👈 Use the sidebar to search for news articles.") 