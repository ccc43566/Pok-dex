import requests
from bs4 import BeautifulSoup

url = "https://wiki.52poke.com/wiki/%E9%99%A4%E8%99%AB%E5%96%B7%E9%9B%BE%EF%BC%88%E9%81%93%E5%85%B7%EF%BC%89"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Check all images
all_images = soup.find_all('img')
print(f"Total images: {len(all_images)}")
for img in all_images:
    src = img.get('src')
    print(f"Image: {src}")
    if 'sprite' in src.lower() or 'item' in src.lower() or 'media.52poke' in src:
        alt = img.get('alt', '')
        print(f"Potential sprite: {src} | Alt: {alt}")
