"""
python -m global_ai_api_demo.chatgpt_api_demo
"""

import os
import asyncio
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

# 🔐 Use env var for security
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise EnvironmentError("❌ OPENAI_API_KEY environment variable is not set.")

client = AsyncOpenAI(api_key=API_KEY)

async def first_completion() -> ChatCompletion:
    return await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "How are you doing ChatGPT?"}],
    )

async def second_completion() -> ChatCompletion:
    return await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say this is a test"}],
    )

async def main() -> None:
    try:
        first, second = await asyncio.gather(first_completion(), second_completion())

        print("----- first response -----")
        print(first.choices[0].message.content)

        print("----- second response -----")
        print(second.choices[0].message.content)

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
