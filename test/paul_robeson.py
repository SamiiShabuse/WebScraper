import requests
from bs4 import BeautifulSoup
import pandas as pd

def extract_staff_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    staff_data = []

    # Find all tables on the page
    tables = soup.find_all('table')

    for table in tables:
        # Find all rows in the table
        rows = table.find_all('tr')
        for row in rows:
            # Find all cells in the row
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                name = cells[0].get_text(strip=True)
                position = cells[1].get_text(strip=True)
                email = cells[2].get_text(strip=True)
                staff_data.append({
                    'Name': name,
                    'Position': position,
                    'Email': email
                })

    return staff_data

# Example usage
url = 'https://robeson.philasd.org/parents/'
staff_info = extract_staff_info(url)
df = pd.DataFrame(staff_info)
df.to_excel('paul_robeson.xlsx', index=False)
