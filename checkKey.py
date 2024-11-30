import requests

from config import API_KEY

url = "https://api.openai.com/v1/models"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

response = requests.get(url, headers=headers)
print(response.json())
