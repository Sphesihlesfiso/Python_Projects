import requests
from bs4 import BeautifulSoup

# Target URL
url = 'https://547cfb2939e8.ngrok-free.app'

# Send HTTP request
response = requests.get(url)

# Parse HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all article titles (assuming they're in <h2> tags)
titles = soup.find_all('button')

# Print each title
for i, title in enumerate(titles, start=1):
    print(f"{i}. {title.get_text(strip=True)}")
