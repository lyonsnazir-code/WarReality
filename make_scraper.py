import requests 
from bs4 import BeautifulSoup 
from urllib.parse import quote_plus 
def fetch_osint_headlines(query, max_results=5): 
    q = quote_plus(query) 
    url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en" 
    try: 
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10) 
        soup = BeautifulSoup(res.content, features="xml")  = [i.title.text for i in soup.find_all("item")[:max_results]] 
