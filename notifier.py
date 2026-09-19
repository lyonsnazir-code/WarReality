import os, requests  
from dotenv import load_dotenv  
load_dotenv()  
def send_discord_alert(message):  
    url = os.getenv("DISCORD_WEBHOOK_URL")  
    if not url: return  
    requests.post(url, json={"content": message}) 
