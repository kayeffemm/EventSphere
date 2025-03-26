import requests
import os
from dotenv import load_dotenv

load_dotenv()
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")

BASE_URL = "https://app.ticketmaster.com/discovery/v2"

def search_artist(artist_name: str):
    """Fetch artist information from Ticketmaster Discovery API."""
    url = f"{BASE_URL}/attractions.json"
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "keyword": artist_name
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("_embedded", {}).get("attractions", [])
    else:
        return None


def get_upcoming_events(artist_id: str):
    """Fetch upcoming events for an artist."""
    url = f"{BASE_URL}/events.json"
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "attractionId": artist_id
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("_embedded", {}).get("events", [])
    else:
        return None