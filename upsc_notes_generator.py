import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

def extract_relevant_content(article_url):
    """
    Step 1: Extract relevant content from HTML
    """
    try:
        # Fetch webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(article_url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']):
            element.decompose()
            
        # Extract main content
        main_content = ""
        
        # Try different content selectors
        content_selectors = [
            'article', 
            'div[class*="article"]',
            'div[class*="content"]',
            'div[class*="story"]',
            'main',
            'div[class*="main"]',
            'div[role="main"]'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                main_content = content.get_text(separator='\n', strip=True)
                break
                
        # If no content found with selectors, try getting all paragraphs
        if not main_content:
            paragraphs = soup.find_all('p')
            main_content = '\n'.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
        
        # Clean content
        main_content = re.sub(r'\n\s*\n', '\n\n', main_content)
        main_content = re.sub(r'\s+', ' ', main_content)
        main_content = main_content.strip()
        
        return main_content
        
    except Exception as e:
        st.error(f"Error extracting content: {str(e)}")
        return None

def is_india_related(content):
    """
    Use Gemini to determine if the article is India-related or foreign news
    """
    try:
        classification_prompt = f"""
        Analyze this news article and determine if it's primarily about India or a foreign country/region.
        
        CONTENT: {content}
        
        Classify the article as:
        1. "INDIA" - if the article is primarily about India, Indian politics, economy, society, or India's domestic affairs
        2. "FOREIGN" - if the article is primarily about another country or international affairs with minimal India connection
        
        Respond with ONLY one word: either "INDIA" or "FOREIGN"
        """
        
        classification_response = model.generate_content(classification_prompt)
        classification = classification_response.text.strip().upper()
        
        return classification == "INDIA"
        
    except Exception as e:
        print(f"Error in classification: {str(e)}")
        # Default to foreign news if there's an error
        return False

def analyze_content(content, is_india_news):
    """
    Step 2: Analyze the extracted content
    """
    if is_india_news:
        analysis_prompt = f"""
        Analyze this India-related news article for UPSC preparation:
        CONTENT: {content}

        1. Extract only essential information:
           - Key Facts & Figures
           - Important Dates & Timeline
           - Names of People/Organizations
           - Government Policies/Schemes
           - Statistical Data
           - Geographic Information

        2. Identify:
           - Main theme and sub-themes
           - UPSC relevance and which papers it relates to
           - Connection to static portions of the UPSC syllabus

        Format your response as:
        ANALYSIS:
        [Your analysis]

        KEY INFORMATION:
        [Extracted information]

        SUMMARY:
        [Concise summary]
        """
    else:
        analysis_prompt = f"""
        Analyze this international news article for UPSC preparation:
        CONTENT: {content}

        1. Extract only essential information:
           - Key Facts & Figures
           - Important Dates & Timeline
           - Names of People/Organizations
           - International Policies/Agreements
           - Statistical Data
           - Geographic Information

        2. Identify:
           - Main theme and sub-themes
           - India's connection to this news (if any)
           - UPSC relevance and which papers it relates to
           - Connection to static portions of the UPSC syllabus

        Format your response as:
        ANALYSIS:
        [Your analysis]

        KEY INFORMATION:
        [Extracted information]

        SUMMARY:
        [Concise summary]
        """
    
    with st.spinner("Analyzing content..."):
        analysis_response = model.generate_content(analysis_prompt)
        return analysis_response.text

def add_context(analysis_result, is_india_news):
    """
    Step 3: Add context and implications
    """
    if is_india_news:
        context_prompt = f"""
        Based on this analysis:
        {analysis_result}

        1. For India-related news:
           - Identify government schemes/policies mentioned
           - Extract constitutional/legal aspects
           - Connect to relevant government initiatives

        2. Connect to UPSC syllabus:
           - Map to specific papers and topics
           - Identify potential essay topics
           - Generate sample answer points for GS papers

        3. Identify future implications if present:
           - Upcoming policy changes or reforms
           - Future government initiatives mentioned
           - Potential economic or social impacts
           - Long-term strategic implications
           - Future challenges or opportunities

        Format your response as:
        CONTEXT:
        [Context information]

        IMPLICATIONS:
        [Implications]

        FUTURE IMPLICATIONS:
        [Future context if present, otherwise "No specific future implications mentioned"]

        SYLLABUS CONNECTION:
        [Syllabus connections]
        """
    else:
        context_prompt = f"""
        Based on this analysis:
        {analysis_result}

        1. For international news:
           - Identify global implications
           - Extract India's position/response if mentioned
           - Connect to India's foreign policy if relevant

        2. Connect to UPSC syllabus:
           - Map to specific papers and topics
           - Identify potential essay topics
           - Generate sample answer points for GS papers

        3. Identify future implications if present:
           - Upcoming international developments
           - Future policy changes or agreements
           - Potential impacts on India
           - Long-term strategic implications
           - Future challenges or opportunities

        Format your response as:
        CONTEXT:
        [Context information]

        IMPLICATIONS:
        [Implications]

        FUTURE IMPLICATIONS:
        [Future context if present, otherwise "No specific future implications mentioned"]

        SYLLABUS CONNECTION:
        [Syllabus connections]
        """
    
    with st.spinner("Adding context..."):
        context_response = model.generate_content(context_prompt)
        return context_response.text

def compile_notes(analysis_result, context_result, is_india_news):
    """
    Step 4: Compile final UPSC notes
    """
    if is_india_news:
        notes_prompt = f"""
        Compile comprehensive UPSC notes based on:
        {analysis_result}
        {context_result}

        Create notes with the following structure:

        1. Theme & Syllabus Connection
           - Main theme and sub-themes
           - Relevant UPSC papers and topics
           - Connection to static portions of the syllabus

        2. Key Facts & Timeline
           - Important dates and events
           - Key statistics and data
           - Geographic information
           - Current status and developments

        3. Important Stakeholders
           - Government bodies and agencies
           - Organizations and institutions
           - Key individuals and their roles
           - Other relevant stakeholders

        4. Government Response
           - Policy initiatives
           - Administrative actions
           - Financial measures
           - Regulatory frameworks

        5. Constitutional/Legal Aspects
           - Relevant constitutional provisions
           - Legal frameworks
           - Regulatory requirements
           - Judicial precedents (if any)

        6. UPSC Application
           - Essay topics
           - Answer writing points
           - Important quotes
           - Data points to remember

        7. Important Names & Roles
           - Include ALL key people mentioned in the article
           - Provide detailed information about each person:
             * Full name and title
             * Current position/role
             * Party affiliation (if politician)
             * Tenure in current position
             * Previous relevant positions
             * Key contributions or statements

        8. Key Terms & Concepts
           - Explain ALL important terms mentioned in the article
           - Provide detailed definitions and relevance
           - Include recent developments related to key concepts
           - Explain technical terms and jargon
           - Include policy initiatives and programs

        9. Practice Questions
            - 2-3 Prelims-style questions
            - 1-2 Mains-style questions
            - Include answer explanations

        10. Quick Revision
            - 5-7 key points to remember
            - Important dates and facts
            - Key names and terms

        Make the notes:
        - Visually appealing with strategic use of emojis
        - Include "Key Takeaway" boxes
        - Add "Did You Know?" fact boxes where relevant
        - Include "Memory Tips" for difficult concepts
        - Add "Think About This" reflection questions
        - Include "Quote This" sections with impactful statements

        IMPORTANT INSTRUCTIONS:
        - DO NOT include introductory text like "Here are comprehensive UPSC notes..."
        - DO NOT make obvious statements
        - Focus on meaningful, non-obvious information
        - Be concise and factual
        - Start directly with the content without any preamble
        - DO NOT include visual elements or chart suggestions
        - For important names, include ALL key people with comprehensive information
        - For key terms, provide detailed definitions and recent developments
        - Ensure ALL information from the article is included in the notes
        - Do not omit any important details mentioned in the article
        """
    else:
        notes_prompt = f"""
        Compile comprehensive UPSC notes based on:
        {analysis_result}
        {context_result}

        Create notes with the following structure:

        1. Theme & Syllabus Connection
           - Main theme and sub-themes
           - Relevant UPSC papers and topics
           - Connection to static portions of the syllabus

        2. Key Facts & Timeline
           - Important dates and events
           - Key statistics and data
           - Geographic information
           - Current status and developments

        3. Important Stakeholders
           - International organizations and institutions
           - Key individuals and their roles
           - Other relevant stakeholders

        4. International Implications
           - Global context
           - India's position
           - Bilateral/multilateral aspects
           - Foreign policy dimensions

        5. UPSC Application
           - Essay topics
           - Answer writing points
           - Important quotes
           - Data points to remember

        6. Important Names & Roles
           - Include ALL key people mentioned in the article
           - Provide detailed information about each person:
             * Full name and title
             * Current position/role
             * Key contributions or statements

        7. Key Terms & Concepts
           - Explain ALL important terms mentioned in the article
           - Provide detailed definitions and relevance
           - Include recent developments related to key concepts
           - Explain technical terms and jargon

        8. Practice Questions
            - 2-3 Prelims-style questions
            - 1-2 Mains-style questions
            - Include answer explanations

        9. Quick Revision
            - 5-7 key points to remember
            - Important dates and facts
            - Key names and terms

        Make the notes:
        - Visually appealing with strategic use of emojis
        - Include "Key Takeaway" boxes
        - Add "Did You Know?" fact boxes where relevant
        - Include "Memory Tips" for difficult concepts
        - Add "Think About This" reflection questions
        - Include "Quote This" sections with impactful statements

        IMPORTANT INSTRUCTIONS:
        - DO NOT include introductory text like "Here are comprehensive UPSC notes..."
        - DO NOT make obvious statements
        - Focus on meaningful, non-obvious information
        - Be concise and factual
        - Start directly with the content without any preamble
        - DO NOT include visual elements or chart suggestions
        - For important names, include ALL key people with comprehensive information
        - For key terms, provide detailed definitions and recent developments
        - Ensure ALL information from the article is included in the notes
        - Do not omit any important details mentioned in the article
        """
    
    with st.spinner("Compiling final notes..."):
        notes_response = model.generate_content(notes_prompt)
        return notes_response.text

def generate_upsc_notes(article_title, article_content):
    """
    Generate concise UPSC notes from article title and content.
    """
    try:
        # Determine if the article is India-related or foreign news
        is_india_news = is_india_related(article_content)
        
        # Step 1: Analysis & Extraction
        analysis_prompt = f"""
        Create a brief analysis of this article for UPSC:
        Title: {article_title}
        Content: {article_content}

        Focus on:
        1. Key Facts (with dates)
        2. Important Names & Roles
        3. Key Terms & Concepts (include UPSC relevance and current context)
        4. Government Schemes & Policies (include launch dates, objectives, and recent updates)
        5. Current Affairs Context
        6. UPSC Syllabus Connections
        Keep each point brief but include all relevant dates and updates.
        """
        
        analysis_result = model.generate_content(analysis_prompt).text

        # Step 2: Context & Implications
        context_prompt = f"""
        Based on this analysis:
        {analysis_result}

        Provide brief context on:
        1. Historical Context (with dates)
        2. Policy Implications
        3. Government Initiatives (include timeline and progress)
        4. International Relations
        5. Economic Impact
        Keep each point concise and include key dates.
        """
        
        context_result = model.generate_content(context_prompt).text

        # Step 3: Note Compilation
        notes_prompt = f"""
        Compile concise UPSC notes using:
        Analysis: {analysis_result}
        Context: {context_result}

        Structure as brief bullet points:
        1. Article Summary (2-3 lines)
        2. Key Facts & Dates
        3. Important Names & Roles (brief)
        4. Key Terms & Concepts (include UPSC relevance)
        5. Government Schemes & Policies (with launch dates and recent updates)
        6. Historical Context (with dates)
        7. Current Affairs Context
        8. UPSC Syllabus Connections
        9. Policy Implications
        10. Practice Questions (2-3)
        Keep each section brief but include all essential dates and updates.
        For government schemes, include:
        - Launch date
        - Key objectives
        - Recent updates/developments
        - UPSC relevance
        
        For key terms, include:
        - Definition
        - Current context
        - UPSC relevance
        - Recent developments
        """
        
        final_notes = model.generate_content(notes_prompt).text

        return final_notes

    except Exception as e:
        print(f"Error in generate_upsc_notes: {str(e)}")
        return f"Error generating notes: {str(e)}"

def generate_quiz(article_title, article_description):
    """
    Generate a UPSC-style quiz from a news article.
    """
    try:
        quiz_prompt = f"""
        Create a UPSC-style quiz with 5 multiple-choice questions based on this article:
        
        TITLE: {article_title}
        CONTENT: {article_description}
        
        Format each question as follows:
        
        ## Question 1
        [Question text]
        
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        
        **Answer:** [Correct option letter]
        **Explanation:** [Brief explanation of the correct answer]
        
        Make the questions:
        1. Clear and concise
        2. Based on key facts from the article
        3. Relevant for UPSC preparation
        4. Have only one correct answer
        5. Include explanations for the correct answer
        6. Focus on analytical understanding rather than memorization
        """
        
        with st.spinner("Generating UPSC-style quiz..."):
            quiz_response = model.generate_content(quiz_prompt)
            return quiz_response.text
            
    except Exception as e:
        st.error(f"Error generating quiz: {str(e)}")
        return None

# Example usage in Streamlit
if __name__ == "__main__":
    st.title("UPSC Notes Generator")
    
    article_url = st.text_input("Article URL", "https://example.com/article")
    
    if st.button("Generate UPSC Notes"):
        notes = generate_upsc_notes(article_title, article_content)
        st.markdown(notes, unsafe_allow_html=True)
    
    if st.button("Generate Quiz"):
        quiz = generate_quiz(article_title, article_description)
        st.markdown(quiz, unsafe_allow_html=True) 