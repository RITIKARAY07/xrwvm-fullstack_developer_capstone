import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    "backend_url", "http://localhost:3030"
).rstrip("/")

sentiment_analyzer_url = os.getenv(
    "sentiment_analyzer_url", "http://localhost:5050"
).rstrip("/")


def get_request(endpoint, **kwargs):
    try:
        response = requests.get(
            f"{backend_url}/{endpoint.lstrip('/')}",
            timeout=10,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        print(f"Backend GET request failed: {error}")
        return None


def analyze_review_sentiments(text):
    try:
        response = requests.get(
            f"{sentiment_analyzer_url}/analyze/{quote(str(text), safe='')}",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        print(f"Sentiment analysis request failed: {error}")
        return None


def post_review(data_dict):
    try:
        response = requests.post(
            f"{backend_url}/insert_review",
            json=data_dict,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        print(f"Review submission failed: {error}")
        return None
