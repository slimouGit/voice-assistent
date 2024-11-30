import requests

from config import API_KEY

url = "wss://api.openai.com/v1/realtime"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

response = requests.get(url, headers=headers)
print(response.json())
