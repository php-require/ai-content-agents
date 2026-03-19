import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from schemas.thumbnail_schema import THUMBNAIL_SCHEMA
from prompts.thumbnail_prompt import THUMBNAIL_PROMPT

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=api_key)


def generate_thumbnail_prompt(
    shorts_data: dict[str, Any],
    tone: str = "aggressive marketing",
    platform: str = "YouTube Shorts"
) -> dict:
    """
    Generates a structured thumbnail package from the output of script_agent.

    Expected input:
        shorts_data: dict returned by generate_shorts_script()

    Returns:
        dict matching THUMBNAIL_SCHEMA
    """

    if not isinstance(shorts_data, dict):
        raise TypeError("shorts_data must be a dict")

    user_prompt = f"""
Create a viral thumbnail package for {platform}.

Thumbnail generation context:
- Tone: {tone}
- Goal: maximize click-through rate
- Audience: people scrolling fast in a short-form feed

Here is the content package from the first agent:
{json.dumps(shorts_data, ensure_ascii=False, indent=2)}

Requirements:
- make the thumbnail extremely clickable
- aggressive marketing is allowed
- focus on curiosity, tension, surprise, contrast
- keep composition simple and bold
- use 1 main subject, максимум 2 if really needed
- avoid generic corporate visuals
- avoid abstract concepts
- image must be instantly readable at small size
- describe the image like a real visual scene, not a vague idea
- prefer cinematic lighting and strong focal point
- avoid too much tiny text inside the image
- output only valid schema content
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": THUMBNAIL_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": THUMBNAIL_SCHEMA
        },
        temperature=1.0
    )

    usage = response.usage
    if usage:
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens

        # примерный расчет по аналогии с твоим первым агентом
        input_cost = input_tokens * 0.000005
        output_cost = output_tokens * 0.000015
        total_cost = input_cost + output_cost

        print(f"\n💰 Thumbnail prompt cost: ${total_cost:.4f}")
        print(f"Input tokens: {input_tokens}")
        print(f"Output tokens: {output_tokens}")

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Model returned empty content")

    return json.loads(content)