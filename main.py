import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urljoin

from dotenv import load_dotenv
import os

# CONFIGURATION
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SEARCH_QUERY = "high schools near Drexel University"
EXCEL_FILENAMES = "drexel_highschools.xlsx"

# STEP 1: GET SCHOOL LINKS FROM GOOGLE
def get_school_links(query, api_key):
    print("[*] Searching for school websites...")
    params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
    }
    response = requests.get("https://serpapi.com/search", params=params)
    results = response.json()

    links = []
    for result in results.get("organic_results", []):
        link = result.get("link")
        if link:
            links.append(link)
    return links


# STEP 2: FIND STAFF/DIRECTORY PAGE

def main():
    pass

if __name__ == "__main__":
    main()
    