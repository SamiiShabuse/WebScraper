import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.parse import urljoin
from dotenv import load_dotenv
import os
from datetime import datetime
import time

# CONFIGURATION
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SEARCH_QUERY = "high schools near Drexel University"
EXCEL_FILENAME = f"highschools_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
KEYWORD_FILE = "keywords.txt"


# Load keywords from a file
def load_keywords(filepath=KEYWORD_FILE):
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]


def get_with_retries(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response
        except Exception as e:
            print(f"        ⚠️ Retry {attempt + 1} failed for {url}: {e}")
            time.sleep(delay)
    print(f"        ❌ Failed to fetch {url} after {retries} attempts.")
    return None


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
def find_directory_links(html, base_url):
    keywords = load_keywords()
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text(strip=True).lower()

        for keyword in keywords:
            if keyword in href or keyword in text:
                full_link = urljoin(base_url, href)
                if full_link not in links:
                    links.append(full_link)
            for sep in ["-", "_", " "]:
                pattern = f"{sep}{keyword}"
                if pattern in href or pattern in text:
                    full_link = urljoin(base_url, href)
                    if full_link not in links:
                        links.append(full_link)

    return links




# STEP 3: SCRAPE TEACHER INFO FROM DIRECTORY PAGE
def extract_teacher_info(html, school_url):
    soup = BeautifulSoup(html, "html.parser")
    teachers = []
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

    # Extract from table rows
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all(["td", "th"])
            if len(cols) >= 2:
                row_text = " ".join(col.get_text(strip=True) for col in cols)
                emails = re.findall(email_pattern, row_text)
                for email in emails:
                    name_guess = cols[0].get_text(strip=True)
                    position = cols[1].get_text(strip=True) if len(cols) > 1 else ""
                    teachers.append({
                        "Name": name_guess,
                        "Email": email,
                        "Position": position,
                        "School Website": school_url
                    })

    # Fallback: extract from plain text
    text = soup.get_text()
    emails = re.findall(email_pattern, text)
    for email in set(emails):
        name_guess = email.split("@")[0].replace('.', ' ').replace('_', ' ').title()
        if not any(email in t["Email"] for t in teachers):
            teachers.append({
                "Name": name_guess,
                "Email": email,
                "Position": "",
                "School Website": school_url
            })

    return teachers

def page_has_teacher_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # 1. Check for tables with at least 2 rows and 2+ columns
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        if len(rows) >= 2:
            first_row = rows[0].find_all(["td", "th"])
            if len(first_row) >= 2:
                return True

    # 2. Check for at least 3 unique emails
    text = soup.get_text()
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    if len(set(emails)) >= 3:
        return True

    # 3. Check for job-related keywords
    keywords = ["teacher", "faculty", "principal", "math", "science", "staff", "department", "email:"]
    for word in keywords:
        if word.lower() in text.lower():
            return True

    return False


# STEP 4: SAVE TO EXCEL
def save_to_excel(data, filename):
    print(f"[*] Saving data to {filename}...")
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print("[*] Data saved successfully.")

# MAIN FUNCTION
def main():
    all_teachers = []
    school_links = get_school_links(SEARCH_QUERY, SERPAPI_KEY)

    for link in school_links:
        try:
            print(f"\n[*] Visiting: {link}")
            home_res = get_with_retries(link)
            if not home_res:
                print(f"    ❌ Skipping {link} — failed to fetch homepage.")
                continue

            dir_links = find_directory_links(home_res.text, link)
            if not dir_links:
                print("    ✘ No staff-related links found")
                continue

            found_data = False
            for dir_link in dir_links:
                print(f"    ↳ Trying: {dir_link}")
                dir_res = get_with_retries(dir_link)
                if not dir_res:
                    print(f"        ❌ Skipping {dir_link} — failed to fetch.")
                    continue

                if not page_has_teacher_data(dir_res.text):
                    print("        ❌ Page doesn't appear to contain staff info")
                    continue

                teachers = extract_teacher_info(dir_res.text, dir_link)
                if teachers:
                    all_teachers.extend(teachers)
                    found_data = True
                    print(f"        ✅ Found {len(teachers)} teachers")
                    break
                else:
                    print("        ⚠️ No teacher data extracted")

            if not found_data:
                print("    ❌ All matching pages scanned but no usable data found")

        except Exception as e:
            print(f"⚠️ Error with school: {link} → {e}")

    save_to_excel(all_teachers, EXCEL_FILENAME)
    print("[✓] All tasks completed.")
    print(f"[*] Total teachers found: {len(all_teachers)}")


if __name__ == "__main__":
    main()
