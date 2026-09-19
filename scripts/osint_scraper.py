import urllib.request, xml.etree.ElementTree as ET, logging, os

log_file = os.path.expanduser('~/genesis_node_00/core/genesis.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_osint_headlines(query='crypto'):
    url = f'https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read()
        root = ET.fromstring(html)
        items = []
        for item in root.findall('.//item')[:3]:
            title = item.find('title').text
            items.append(title)
        return items
    except Exception as e:
        logging.error(f'OSINT Scraping Failed: {str(e)}')
        return []

if __name__ == '__main__':
    print('[OSINT HOOK] Testing News Feed Scraping...')
    headlines = fetch_osint_headlines('bitcoin')
    for i, h in enumerate(headlines, 1):
        print(f'   {i}. {h}')
