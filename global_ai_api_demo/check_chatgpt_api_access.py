"""
python -m global_ai_api_demo.check_chatgpt_api_access
"""

import openai

openai.api_key = "your_api_key_here"  # Replace with your actual OpenAI API key

models = openai.models.list()

for model in models.data:
    print(model.id)
