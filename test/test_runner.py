import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from main import load_keywords  # <- assuming your main file is scraper.py
import os

def find_directory_link_debug(html, base_url, keywords):
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text(strip=True).lower()

        for keyword in keywords:
            if keyword in href or keyword in text:
                return urljoin(base_url, href), keyword
            for sep in ["-", "_", " "]:
                if f"{sep}{keyword}" in href or f"{sep}{keyword}" in text:
                    return urljoin(base_url, href), f"{sep}{keyword}"
    return None, None

def run_test(school_links, report_file="test_report.txt"):
    keywords = load_keywords()
    with open(report_file, "w", encoding="utf-8") as f:
        for link in school_links:
            try:
                print(f"[*] Testing: {link}")
                res = requests.get(link, timeout=10)
                match_url, matched_keyword = find_directory_link_debug(res.text, link, keywords)
                if match_url:
                    f.write(f"✅ MATCHED: {link} → {match_url} (via: '{matched_keyword}')\n")
                else:
                    f.write(f"❌ NO MATCH: {link}\n")
            except Exception as e:
                f.write(f"⚠️ ERROR: {link} → {e}\n")

    print(f"[✓] Test complete. See results in {report_file}")

if __name__ == "__main__":
    # Example hardcoded test data (replace with your actual list or load from JSON)
    test_links = [
        "https://robeson.philasd.org/",
        "https://scienceleadership.org/",
        "https://centralhs.philasd.org/",
        "https://benfranklinhs.philasd.org/"
    ]
    run_test(test_links)
