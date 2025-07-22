"""
Usage:
python global_ai_api_demo/deepseek_api_demo.py
or
python -m global_ai_api_demo.deepseek_api_demo
"""

import requests

api_key = "sk-99209fc999c74188bf9b7f4f639fc1d9"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello, how are you?"}]
}

response = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers=headers,
    json=data
)

print(response.json())