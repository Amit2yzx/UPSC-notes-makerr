from newsapi import NewsApiClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('NEWS_API_KEY')
print(f"API Key loaded: {'Yes' if api_key else 'No'}")

# Initialize News API client
newsapi = NewsApiClient(api_key=api_key)

# Test the connection
try:
    print("Testing News API connection...")
    response = newsapi.get_top_headlines(country='us', page_size=1)
    print("Connection successful!")
    print(f"Status: {response['status']}")
    print(f"Total results: {response['totalResults']}")
except Exception as e:
    print(f"Error: {str(e)}") 