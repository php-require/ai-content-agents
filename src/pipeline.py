import json
import os
import argparse
from datetime import datetime

from agents.script_agent import generate_shorts_script
from agents.image_prompt_agent import generate_thumbnail_prompt
from agents.image_generator_agent import generate_image


DEV_MODE = True


def slugify(text: str) -> str:
    safe = "".join(c.lower() if c.isalnum() else "-" for c in text)
    safe = "-".join(part for part in safe.split("-") if part)
    return safe[:60]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--i", action="store_true", help="Run full pipeline (image included)")
    args = parser.parse_args()

    generate_all = args.i

    topic = "AI agents are changing content creation"
    niche = "tech"
    tone = "exciting"
    target_language = "English"

    # 🔥 ВСЕГДА создаём run_name
    run_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{slugify(topic)}"

    # 📁 выбор папки
    if DEV_MODE:
        output_dir = os.path.join("output", "dev")
        print(f"\n🚀 RUN (DEV MODE): {run_name}")
    else:
        output_dir = os.path.join("output", run_name)
        print(f"\n🚀 RUN: {run_name}")

    os.makedirs(output_dir, exist_ok=True)

    # ========================
    # 1. SCRIPT AGENT
    # ========================
    print("\n--- Generating Shorts Script ---")

    shorts_result = generate_shorts_script(
        topic=topic,
        niche=niche,
        tone=tone,
        target_language=target_language
    )

    with open(os.path.join(output_dir, "script.json"), "w", encoding="utf-8") as f:
        json.dump(shorts_result, f, indent=2, ensure_ascii=False)

    print("✅ Script done")

    # ========================
    # 2. IMAGE PROMPT AGENT
    # ========================
    if generate_all:
        print("\n--- Generating Thumbnail Prompt ---")

        thumbnail_result = generate_thumbnail_prompt(shorts_result)

        with open(os.path.join(output_dir, "thumbnail_prompt.json"), "w", encoding="utf-8") as f:
            json.dump(thumbnail_result, f, indent=2, ensure_ascii=False)

        print("✅ Thumbnail prompt done")
        print("\n🎯 IMAGE PROMPT:")
        print(thumbnail_result["image_prompt"])
    else:
        print("\n⏸ Skipping thumbnail + image (script only)")

    # ========================
    # 3. IMAGE GENERATOR
    # ========================
    if generate_all:
        print("\n--- Generating Image ---")

        image_result = generate_image(
            image_prompt=thumbnail_result["image_prompt"],
            output_path=os.path.join(output_dir, "thumbnail.png")
        )

        with open(os.path.join(output_dir, "image_result.json"), "w", encoding="utf-8") as f:
            json.dump(image_result, f, indent=2, ensure_ascii=False)

        print("✅ Image generated")

    print(f"\n📁 All saved to: {output_dir}")


if __name__ == "__main__":
    main()