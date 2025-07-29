"""
python ai_blog_writer/serp_search.py
python -m ai_blog_writer.serp_search
"""


import requests
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.write_json import write_to_temp_json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SERP_API_KEY = os.getenv("SERP_API_KEY")

def get_realtime_data(topic: str) -> str:
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "bing",               # Required
        "q": topic,                       # Your search query
        "api_key": SERP_API_KEY 
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Print for debugging (optional)
    print("🔍 Full response:\n", data)

    snippets = []
    for result in data.get("organic_results", []):
        if "snippet" in result:
            snippets.append(result["snippet"])

    # return "\n".join(snippets[:30]) if snippets else "No real-time facts found."
    return "\n".join(snippets) if snippets else "No real-time facts found."

if __name__ == "__main__":
    data = get_realtime_data("give me python example code to write stris is palindrome or not")
    write_to_temp_json(data)
