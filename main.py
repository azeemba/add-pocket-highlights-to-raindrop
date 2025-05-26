from dataclasses import dataclass
import json
import argparse
import os
from typing import Sequence
import requests

"""
Script to add "pocket" highlights to "raindrop" application.

Structure of pocket highlights:

[
{"url":"https://en.wikipedia.org/wiki/Entropy_in_thermodynamics_and_information_theory",
    "title":"Entropy in thermodynamics and information theory - Wikipedia",
    "highlights":[{"quote":"","created_at":1547165505}]
}, ...]
"""


@dataclass
class Highlight:
    quote: str
    created_at: int


@dataclass
class PocketHighlight:
    url: str
    title: str
    highlights: list[Highlight]


def load_pocket_highlights(filename: str) -> dict[str, PocketHighlight]:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    highlights_by_url = {}
    for item in data:
        url = item["url"].split("?", 1)[0].rstrip("/")
        title = item["title"]
        highlights = [Highlight(**h) for h in item.get("highlights", [])]
        if url in highlights_by_url:
            highlights_by_url[url].highlights.extend(highlights)
        else:
            highlights_by_url[url] = PocketHighlight(
                url=url, title=title, highlights=highlights
            )
    return highlights_by_url


def load_token() -> str:
    # Try to load from environment variable first
    token = os.environ.get("TOKEN")
    if token:
        return token

    # Try to load from .env file
    try:
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("TOKEN="):
                    return line.strip().split("=", 1)[1]
    except FileNotFoundError:
        pass

    raise RuntimeError("TOKEN not found in environment or .env file")


def fetch_raindrop_id(token: str, url: str):
    """Get the raindrop id for the URL, requires "search" - kinda annoying"""
    url_api = "https://api.raindrop.io/rest/v1/raindrops/0"
    headers = make_header(token)
    params = {"search": url, "nested": "true"}
    try:
        response = requests.get(url_api, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["items"][0]["_id"]
    except Exception as e:
        print(f"Error fetching raindrop for URL {url}: {e}")
        return None


def make_header(token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    return headers


def fetch_all_raindrop_ids(token: str, urls: Sequence[str]) -> dict[str, str]:
    url_to_raindrop = {}
    for url in urls:
        url_to_raindrop[url] = fetch_raindrop_id(token, url)
        print(url, url_to_raindrop[url])

    with open("in_progress_ids.json", "w", encoding="utf-8") as f:
        json.dump(url_to_raindrop, f, ensure_ascii=False, indent=2)
    return url_to_raindrop


def add_highlight(highlights: PocketHighlight, raindrop_id: str):
    """
    Documentation of the API we want to use
    PUT https://api.raindrop.io/rest/v1/raindrop/{id}

    Just specify a highlights array in body with object for each highlight

    For example:

    {"highlights": [ { "text": "Some quote", "color": "yellow", "note": "Some note" } ] }
    """
    url_api = f"https://api.raindrop.io/rest/v1/raindrop/{raindrop_id}"
    headers = make_header(load_token())
    body = {
        "highlights": [
            {"text": h.quote, "color": "yellow", "note": ""}
            for h in highlights.highlights
        ]
    }
    try:
        response = requests.put(url_api, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        print(
            f"Added {len(highlights.highlights)} highlights to raindrop {raindrop_id}"
        )
    except Exception as e:
        print(f"Error adding highlights to raindrop {raindrop_id}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Add Pocket highlights to Raindrop.")
    parser.add_argument("highlights", help="Path to Pocket highlights JSON file")
    args = parser.parse_args()

    highlights = load_pocket_highlights(args.highlights)
    print(f"Loaded {len(highlights)} URLs with highlights.")

    token = load_token()

    url_to_raindrop = {}
    if os.path.exists("in_progress_ids.json"):
        with open("in_progress_ids.json", "r", encoding="utf-8") as f:
            url_to_raindrop = json.load(f)
    else:
        url_to_raindrop = fetch_all_raindrop_ids(token, highlights.keys())

    for url, highlight in highlights.items():
        add_highlight(highlight, url_to_raindrop[url])


if __name__ == "__main__":
    main()
