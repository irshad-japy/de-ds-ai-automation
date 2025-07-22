"""
python global_ai_api_demo/cohere_api_demo.py
or
python -m global_ai_api_demo.cohere_api_demo
"""

import requests

api_key = "8D6X1eqh4BIibpgR08T4Ohh3XcTCy8Nt7bNoxcxK"
endpoint = "https://api.cohere.ai/v1/generate"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Define the input data
data = {
    "model": "command",
    "prompt": "write frequently ask roles and responsbilities on pyspark",
    "max_tokens": 100
}

# Send the POST request
response = requests.post(endpoint, headers=headers, json=data)

# Print HTTP status code and the JSON response
print("Status Code:", response.status_code)
print("Response JSON:", response.json())