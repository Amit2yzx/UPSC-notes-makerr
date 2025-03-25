import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure Google API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Set page config
st.set_page_config(
    page_title="UPSC Current Affairs Quiz",
    page_icon="📝",
    layout="wide"
)

# Add CSS styles
st.markdown("""
<style>
    .quiz-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
    }
    .question-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 30px;
        border-left: 5px solid #4285F4;
    }
    .question-number {
        font-weight: bold;
        color: #4285F4;
    }
    .question-text {
        font-size: 1.2rem;
        margin-bottom: 15px;
        font-weight: bold;
    }
    .correct-answer {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 4px;
        margin-top: 10px;
    }
    .wrong-answer {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 4px;
        margin-top: 10px;
    }
    .score-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 30px auto;
        max-width: 500px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .score-title {
        font-size: 1.5rem;
        margin-bottom: 10px;
        color: #333;
    }
    .score-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4285F4;
        margin: 15px 0;
    }
    .high-score {
        color: #0f9d58;
    }
    .nav-button {
        margin-top: 20px;
    }
    .upsc-header {
        background-color: #f0f4ff;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 25px;
        text-align: center;
        border-left: 8px solid #3366ff;
    }
    .tip-box {
        background-color: #fffde7;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 15px 0;
        border-left: 4px solid #ffc107;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for quiz
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False

# Function to generate quiz using Gemini
def generate_quiz(title, description):
    try:
        # Use Gemini 2.0 Flash model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Create a quiz with 5 UPSC-style multiple-choice questions based on this news article:
        
        Title: {title}
        Description: {description}
        
        Follow these specific guidelines:
        1. Create questions that test analytical understanding of the topic in UPSC Civil Services Examination style
        2. Questions should focus on:
           - Current affairs implications of the news
           - Historical context and background
           - Government policies, programs, or initiatives mentioned
           - International relations aspects if applicable
           - Constitutional, legal, or administrative dimensions
           - Geography, economy, or social aspects related to the topic
           - Connections to other important issues in India
        3. Make questions challenging but fair, similar to UPSC Prelims
        4. Include options that require careful distinction between similar concepts
        
        Use this EXACT format for each question:
        
        ## Question 1
        [Write a UPSC-style question about the article]
        
        A) [Option A - make plausible but only one correct]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        
        Answer: [Correct letter]
        
        ## Question 2
        [Another UPSC-style question]
        
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        
        Answer: [Correct letter]
        
        [Continue for all 5 questions]
        
        IMPORTANT:
        - Each question MUST have exactly four options labeled A), B), C), and D)
        - Each question MUST have exactly one correct answer clearly marked
        - All questions should be factually accurate and based on the article content
        - Questions should be similar to those appearing in UPSC Civil Services Examination
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating quiz: {e}")
        return None

# Function to parse quiz content
def parse_quiz(quiz_text):
    if not quiz_text:
        return []
        
    # Split quiz by question markers
    question_blocks = re.split(r'##\s*Question\s*\d+', quiz_text)
    
    # Skip the first block if it's empty
    if question_blocks and not question_blocks[0].strip():
        question_blocks = question_blocks[1:]
    
    questions = []
    
    for i, block in enumerate(question_blocks, 1):
        if not block.strip():
            continue
            
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        
        # Find question text (first line after header)
        question_text = lines[0] if lines else f"Question {i}"
        
        # Extract options and correct answer
        options = []
        correct_answer = None
        
        for line in lines:
            if line.startswith(('A)', 'B)', 'C)', 'D)')):
                options.append(line)
            elif 'Answer:' in line:
                correct_answer = line.split(':', 1)[1].strip()
        
        questions.append({
            'number': i,
            'text': question_text,
            'options': options,
            'answer': correct_answer
        })
    
    return questions

# Title with UPSC focus
st.markdown("<div class='upsc-header'><h1>📝 UPSC Current Affairs Quiz</h1><p>Test your knowledge of current affairs in UPSC Civil Services style</p></div>", unsafe_allow_html=True)

# Check if quiz exists in session state
if 'quiz_title' in st.session_state:
    # Display quiz title
    st.markdown(f"<div class='quiz-title'>Quiz: {st.session_state.quiz_title}</div>", unsafe_allow_html=True)
    
    # Generate quiz if not already generated
    if 'quiz_content' not in st.session_state:
        with st.spinner("Generating quiz questions..."):
            if 'quiz_title' in st.session_state and 'quiz_description' in st.session_state:
                quiz_text = generate_quiz(
                    st.session_state.quiz_title,
                    st.session_state.quiz_description
                )
                if quiz_text:
                    st.session_state.quiz_content = quiz_text
                    st.success("Quiz generated successfully!")
            else:
                st.error("Missing article information. Please go back and generate the quiz again.")
    
    # Display quiz if available
    if 'quiz_content' in st.session_state:
        # Parse quiz questions
        questions = parse_quiz(st.session_state.quiz_content)
        
        if not questions:
            st.warning("No questions found in the quiz. Please go back and try again.")
        else:
            # Initialize answers in session state if not already present
            if 'user_answers' not in st.session_state:
                st.session_state.user_answers = {}
            
            # Display questions
            for q in questions:
                with st.container():
                    st.markdown(f"""
                    <div class="question-box">
                        <div class="question-number">Question {q['number']}</div>
                        <div class="question-text">{q['text']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if q['options']:
                        # Display options as radio buttons
                        answer = st.radio(
                            f"Select your answer for Question {q['number']}:",
                            q['options'],
                            key=f"q_{q['number']}",
                            label_visibility="collapsed"
                        )
                        
                        # Save answer to session state
                        st.session_state.user_answers[q['number']] = answer
                        
                        # Show result if quiz submitted
                        if st.session_state.quiz_submitted:
                            if answer and q['answer'] and answer.startswith(q['answer']):
                                st.markdown('<div class="correct-answer">✓ Correct!</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="wrong-answer">✗ Incorrect. The correct answer is {q["answer"]}</div>', unsafe_allow_html=True)
                    else:
                        st.warning("No options available for this question.")
                    
                    st.markdown("<hr>", unsafe_allow_html=True)
            
            # Submit button
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if not st.session_state.quiz_submitted:
                    if st.button("Submit Answers", use_container_width=True, type="primary"):
                        st.session_state.quiz_submitted = True
                        st.rerun()
            
            with col2:
                if st.button("Return to Articles", use_container_width=True):
                    st.switch_page("app.py")
            
            # Display score if quiz submitted
            if st.session_state.quiz_submitted:
                # Calculate score
                score = 0
                for q in questions:
                    user_answer = st.session_state.user_answers.get(q['number'])
                    if user_answer and q['answer'] and user_answer.startswith(q['answer']):
                        score += 1
                
                # Display score card with UPSC-specific feedback
                score_percent = int((score / len(questions)) * 100)
                
                # UPSC-specific feedback based on score
                if score_percent >= 80:
                    score_class = "high-score"
                    feedback = "Excellent! You're performing at the level required for UPSC Prelims. Keep it up!"
                elif score_percent >= 60:
                    score_class = ""
                    feedback = "Good attempt! You're on the right track for UPSC preparation, but need more practice."
                else:
                    score_class = ""
                    feedback = "Keep studying! Regular practice with current affairs will improve your UPSC readiness."
                
                st.markdown(f"""
                <div class="score-card">
                    <div class="score-title">UPSC Quiz Results</div>
                    <div class="score-value {score_class}">{score}/{len(questions)}</div>
                    <div>You scored {score_percent}%</div>
                    <div style="margin-top:15px; font-style:italic; padding:10px; background-color:#f5f5f5; border-radius:5px;">
                        "{feedback}"
                    </div>
                </div>
                
                <div class="tip-box">
                    <strong>UPSC Preparation Tip:</strong> Review current affairs daily and link news events to static UPSC syllabus topics for better understanding.
                </div>
                """, unsafe_allow_html=True)
                
                # Show balloons for high score
                if score_percent >= 80 and 'balloons_shown' not in st.session_state:
                    st.balloons()
                    st.session_state.balloons_shown = True
                
                # Reset button
                if st.button("Take Quiz Again", use_container_width=True):
                    st.session_state.quiz_submitted = False
                    st.session_state.user_answers = {}
                    if 'balloons_shown' in st.session_state:
                        del st.session_state.balloons_shown
                    st.rerun()
else:
    st.warning("No quiz available. Please generate a quiz from the main page first.")
    
    # Add a button to go back to main page
    st.markdown("<div class='nav-button'>", unsafe_allow_html=True)
    if st.button("Go to Main Page", use_container_width=True):
        st.switch_page("app.py")
    st.markdown("</div>", unsafe_allow_html=True) 