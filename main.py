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
def find_directory_link(home_html, base_url):
    soup = BeautifulSoup(home_html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # if re.search(r"(staff|directory|contact)", href, re.IGNORECASE):
        #     return urljoin(base_url, href)
        if any(keyword in href.lower() for keyword in ["staff", "directory", "contact"]):
            return urljoin(base_url, a["href"])
    return None

# STEP 3: SCRAPE TEACHER INFO FROM DIRECTORY PAGE
def extract_teacher_info(html, school_url):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

    emails = list(set(re.findall(email_pattern, text)))
    teachers = []

    for email in emails:
        name_guess = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
        teachers.append({
            "Name": name_guess,
            "Email": email,
            "Subject": "",  # Advanced: use NLP to detect subject later
            "School Website": school_url
        })
    return teachers

# STEP 4: SAVE TO EXCEL
def save_to_excel(data, filename):
    print(f"[*] Saving data to {filename}...")
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print("[*] Data saved successfully.")

# MAIN FUNCTION
def main():
    pass

if __name__ == "__main__":
    main()
    