import base64
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=api_key)


def generate_image(
    image_prompt: str,
    output_path: str,
    model: str = "gpt-image-1",
    size: str = "1024x1536",
    quality: str = "high",
    output_format: str = "png",
    background: str = "opaque"
) -> dict[str, Any]:
    """
    Generate an image from a text prompt and save it to disk.

    Args:
        image_prompt: Final prompt for image generation.
        output_path: Where to save the generated image.
        model: Image model name.
        size: Image size, e.g. 1024x1024, 1024x1536, 1536x1024, auto.
        quality: low, medium, high, or auto.
        output_format: png, jpeg, or webp.
        background: opaque, transparent, or auto.

    Returns:
        dict with saved file path and metadata.
    """

    if not image_prompt or not image_prompt.strip():
        raise ValueError("image_prompt must not be empty")

    if not output_path or not output_path.strip():
        raise ValueError("output_path must not be empty")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    response = client.images.generate(
        model=model,
        prompt=image_prompt,
        size=size,
        quality=quality,
        output_format=output_format,
        background=background,
    )

    if not getattr(response, "data", None):
        raise ValueError("Image API returned no data")

    first_image = response.data[0]

    image_b64 = getattr(first_image, "b64_json", None)
    if not image_b64:
        raise ValueError("Image API did not return b64_json")

    image_bytes = base64.b64decode(image_b64)
    output_file.write_bytes(image_bytes)

    usage = getattr(response, "usage", None)
    if usage:
        print("\n🖼 Image generation usage:")
        print(f"Input tokens: {getattr(usage, 'input_tokens', 'n/a')}")
        print(f"Output tokens: {getattr(usage, 'output_tokens', 'n/a')}")
        print(f"Total tokens: {getattr(usage, 'total_tokens', 'n/a')}")

        input_details = getattr(usage, "input_tokens_details", None)
        if input_details:
            print(
                "Input details:"
                f" text_tokens={getattr(input_details, 'text_tokens', 'n/a')},"
                f" image_tokens={getattr(input_details, 'image_tokens', 'n/a')}"
            )

    result = {
        "image_path": str(output_file),
        "model": model,
        "size": size,
        "quality": quality,
        "output_format": output_format,
        "background": background,
        "revised_prompt": getattr(first_image, "revised_prompt", None),
    }

    return result