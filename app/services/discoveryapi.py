import requests
import os
from dotenv import load_dotenv

load_dotenv()
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")

BASE_URL = "https://app.ticketmaster.com/discovery/v2"


def search_artist(artist_name: str):
    """Fetch and clean artist info from Ticketmaster Discovery API."""
    url = f"{BASE_URL}/attractions.json"
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "keyword": artist_name
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    raw_artists = data.get("_embedded", {}).get("attractions", [])

    cleaned_artists = []
    for artist in raw_artists:
        cleaned_artists.append({
            "id": artist.get("id"),
            "name": artist.get("name")
        })

    return cleaned_artists


def get_upcoming_events(artist_id: str):
    """Fetch and clean upcoming events for an artist from Ticketmaster."""
    url = f"{BASE_URL}/events.json"
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "attractionId": artist_id
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    raw_events = data.get("_embedded", {}).get("events", [])

    cleaned_events = []
    for event in raw_events:
        cleaned_event = {
            "id": event.get("id"),
            "name": event.get("name"),
            "date": event.get("dates", {}).get("start", {}).get("dateTime"),
            "ticket_url": event.get("url"),
        }

        # Build location string
        venue = event.get("_embedded", {}).get("venues", [{}])[0]
        city = venue.get("city", {}).get("name", "")
        country = venue.get("country", {}).get("name", "")
        venue_name = venue.get("name", "")
        location = f"{venue_name}, {city}, {country}".strip(", ")

        cleaned_event["location"] = location
        cleaned_events.append(cleaned_event)

    return cleaned_events