# UPSC News Analyzer

A Streamlit application for generating UPSC-style notes and quizzes from current news articles.

## Features

- Fetch latest news from multiple sources using News API
- Generate UPSC-focused notes from news articles
- Create interactive multiple-choice quizzes in UPSC exam format
- Clean, modern user interface
- Score tracking and performance feedback

## Requirements

- Python 3.6+
- Streamlit
- Google Generative AI (Gemini)
- News API key
- Various Python packages (see requirements.txt)

## Installation

1. Clone the repository
```
git clone https://github.com/yourusername/upsc-news-analyzer.git
cd upsc-news-analyzer
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys
```
NEWS_API_KEY=your_news_api_key
GOOGLE_API_KEY=your_google_api_key
```

4. Run the application
```
streamlit run app.py
```

## Usage

1. Browse news articles from various sources
2. View article details 
3. Generate UPSC-style notes for any article
4. Create interactive quizzes based on article content
5. Test your knowledge with UPSC-format questions

## License

MIT License 