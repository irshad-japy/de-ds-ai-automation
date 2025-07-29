# blog_generator.py
"""
python -m ai_blog_writer.blog_generator
"""

import cohere
import os
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

def generate_blog(topic: str) -> str:
    prompt = PromptTemplate(
        input_variables=["topic"],
        template="""
Write an SEO-optimized blog article on the following topic.

Topic: {topic}

Requirements:
- Length: 100 to 200 words
- Structure: Introduction, subheadings, conclusion
- Tone: Informative, engaging
- SEO: Include relevant keywords naturally
- Formatting: Use proper paragraphing

Only return the blog article without any explanation.
"""
    )

    final_prompt = prompt.format(topic=topic)

    # Use Cohere chat endpoint to generate content
    response = co.chat(
        message=final_prompt,
        temperature=0.7,
        max_tokens=2048
    )

    return response.text.strip()

    