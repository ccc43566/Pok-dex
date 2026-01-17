import requests
from bs4 import BeautifulSoup

url = "https://wiki.52poke.com/wiki/%E9%81%93%E5%85%B7%E5%88%97%E8%A1%A8"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all tables
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

for i, table in enumerate(tables):
    classes = table.get('class', [])
    print(f"Table {i}: classes = {classes}")
    if 'bgd-道具' in ' '.join(classes):
        print(f"Found matching table: {classes}")
        rows = table.find_all('tr')
        print(f"Table has {len(rows)} rows")
        # Print first few rows
        for j, row in enumerate(rows[:5]):
            cols = row.find_all('td')
            print(f"Row {j}: {len(cols)} cols")
            for k, col in enumerate(cols):
                text = col.get_text(strip=True)[:50]
                html = str(col)[:100]
                print(f"  Col {k}: text='{text}' html='{html}'")
