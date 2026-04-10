import json
import os
import argparse
from datetime import datetime

from agents.script_agent import generate_shorts_script
from agents.image_prompt_agent import generate_thumbnail_prompt
from agents.image_generator_agent import generate_image
from tts_generator import generate_tts, merge_wav_files

DEV_MODE = True


def slugify(text: str) -> str:
    safe = "".join(c.lower() if c.isalnum() else "-" for c in text)
    safe = "-".join(part for part in safe.split("-") if part)
    return safe[:60]


def extract_voice_lines(script_data: dict) -> list[str]:
    voiceover = script_data.get("voiceover")

    if isinstance(voiceover, list):
        parts = [str(x).strip() for x in voiceover if str(x).strip()]
        if parts:
            return parts

    if isinstance(voiceover, str) and voiceover.strip():
        return [voiceover.strip()]

    scenes = script_data.get("scenes", [])
    parts = []

    for scene in scenes:
        text = (
            scene.get("voiceover")
            or scene.get("line")
            or scene.get("caption")
            or ""
        ).strip()

        if text:
            parts.append(text)

    if not parts:
        raise ValueError("No voice text found in script.json")

    return parts


def chunk_voice_lines(lines: list[str], max_chars: int = 180) -> list[str]:
    chunks = []
    current = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if not current:
            current = line
        elif len(current) + 1 + len(line) <= max_chars:
            current += " " + line
        else:
            chunks.append(current)
            current = line

    if current:
        chunks.append(current)

    return chunks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--i", action="store_true", help="Run full pipeline (image included)")
    args = parser.parse_args()

    generate_all = args.i

    topic = "AI agents are changing content creation"
    niche = "tech"
    tone = "exciting"
    target_language = "English"

    run_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{slugify(topic)}"

    if DEV_MODE:
        output_dir = os.path.join("output", "dev")
        print(f"\n🚀 RUN (DEV MODE): {run_name}")
    else:
        output_dir = os.path.join("output", run_name)
        print(f"\n🚀 RUN: {run_name}")

    os.makedirs(output_dir, exist_ok=True)

    # 1. SCRIPT
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

    # 2. TTS (ПО ЧАНКАМ + СКЛЕЙКА)
    print("\n--- Generating TTS ---")

    voice_lines = extract_voice_lines(shorts_result)
    voice_chunks = chunk_voice_lines(voice_lines, max_chars=180)

    generated_files = []

    for i, chunk in enumerate(voice_chunks, start=1):
        output_file = os.path.join(output_dir, f"voice_chunk_{i}.wav")
        print(f"\n🔹 TTS chunk {i}/{len(voice_chunks)}")
        print(f"Text: {chunk}")

        generate_tts(
            text=chunk,
            output_path=output_file,
            lang="en"
        )

        generated_files.append(output_file)

    print("✅ TTS chunks generated")

    merged_voice_path = os.path.join(output_dir, "voiceover_en.wav")
    merge_wav_files(generated_files, merged_voice_path)

    print(f"✅ Final merged TTS saved: {merged_voice_path}")

    # 3. IMAGE + THUMBNAIL
    if generate_all:
        print("\n--- Generating Thumbnail Prompt ---")

        thumbnail_result = generate_thumbnail_prompt(shorts_result)

        with open(os.path.join(output_dir, "thumbnail_prompt.json"), "w", encoding="utf-8") as f:
            json.dump(thumbnail_result, f, indent=2, ensure_ascii=False)

        print("✅ Thumbnail prompt done")
        print("\n🎯 IMAGE PROMPT:")
        print(thumbnail_result["image_prompt"])

        print("\n--- Generating Image ---")

        image_result = generate_image(
            image_prompt=thumbnail_result["image_prompt"],
            output_path=os.path.join(output_dir, "thumbnail.png")
        )

        with open(os.path.join(output_dir, "image_result.json"), "w", encoding="utf-8") as f:
            json.dump(image_result, f, indent=2, ensure_ascii=False)

        print("✅ Image generated")
    else:
        print("\n⏸ Skipping thumbnail + image (script only)")

    print("\n📦 Generated audio chunks:")
    for file_path in generated_files:
        print(f" - {file_path}")

    print(f"\n📁 All saved to: {output_dir}")


if __name__ == "__main__":
    main()