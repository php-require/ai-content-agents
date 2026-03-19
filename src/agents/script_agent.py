import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from schemas.it_shorts_schema import SHORTS_SCHEMA
from prompts.it_shorts_prompt import IT_SHORTS_PROMPT

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=api_key)


def generate_shorts_script(
    topic: str,
    niche: str = "tech",
    tone: str = "exciting",
    target_language: str = "English"
) -> dict:

    user_prompt = f"""
Create a YouTube Shorts content package.

Topic: {topic}
Niche: {niche}
Tone: {tone}
Language: {target_language}

Requirements:
- make it feel native to Shorts
- avoid fluff
- focus on strong retention
- make visuals specific, not abstract
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": IT_SHORTS_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": SHORTS_SCHEMA
        },
        temperature=0.9
    )

    # 🔥 ДОБАВИЛИ ВОТ ЭТО
    usage = response.usage

    if usage:
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens

        # примерные цены для gpt-4o
        input_cost = input_tokens * 0.000005
        output_cost = output_tokens * 0.000015
        total_cost = input_cost + output_cost

        print(f"\n💰 Cost: ${total_cost:.4f}")
        print(f"Input tokens: {input_tokens}")
        print(f"Output tokens: {output_tokens}")

    # -----

    content = response.choices[0].message.content
    return json.loads(content)