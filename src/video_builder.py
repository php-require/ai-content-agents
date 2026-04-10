import json
import argparse
from pathlib import Path

from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
)

OUTPUT_DIR = Path("output/dev")
SCRIPT_PATH = OUTPUT_DIR / "script.json"
THUMB_PATH = OUTPUT_DIR / "thumbnail.png"

VOICE_EN_PATH = OUTPUT_DIR / "voiceover_en.wav"
VOICE_RU_PATH = OUTPUT_DIR / "voiceover_ru.wav"

FINAL_EN_PATH = OUTPUT_DIR / "final_video_en.mp4"
FINAL_RU_PATH = OUTPUT_DIR / "final_video_ru.mp4"

VIDEO_SIZE = (1080, 1920)

# текст
CAPTION_WIDTH = 900
CAPTION_Y = 1320          # было слишком низко
FONT_SIZE = 78
TEXT_STROKE = 4

# фон
ZOOM_START = 1.00
ZOOM_END = 1.12


def load_script() -> dict:
    if not SCRIPT_PATH.exists():
        raise FileNotFoundError(f"Missing file: {SCRIPT_PATH}")

    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def choose_audio_and_output(lang: str) -> tuple[Path, Path]:
    if lang == "en":
        return VOICE_EN_PATH, FINAL_EN_PATH
    if lang == "ru":
        return VOICE_RU_PATH, FINAL_RU_PATH
    raise ValueError("lang must be 'en' or 'ru'")


def get_total_scene_duration(scenes: list[dict]) -> float:
    if not scenes:
        raise ValueError("No scenes found in script.json")
    return max(float(scene["end_sec"]) for scene in scenes)


def make_background_clip(image_path: str, duration: float) -> ImageClip:
    """
    Один общий фон на всю длительность ролика.
    Поэтому зум идет плавно и не сбрасывается на каждой сцене.
    """
    clip = (
        ImageClip(image_path)
        .resized(height=VIDEO_SIZE[1])
        .with_duration(duration)
        .with_position("center")
    )

    return clip.resized(
        lambda t: ZOOM_START + (ZOOM_END - ZOOM_START) * (t / max(duration, 0.001))
    )


def make_caption_clip(text: str, start: float, duration: float) -> TextClip:
    """
    Отдельный текстовый клип на нужный тайминг.
    """
    return (
        TextClip(
            text=text,
            font_size=FONT_SIZE,
            color="white",
            method="caption",
            size=(CAPTION_WIDTH, 260),   # фиксированная высота, чтобы текст не резало
            text_align="center",
            stroke_color="black",
            stroke_width=TEXT_STROKE,
            transparent=True,
        )
        .with_start(start)
        .with_duration(duration)
        .with_position(("center", CAPTION_Y))
    )


def build_video(lang: str) -> None:
    if not THUMB_PATH.exists():
        raise FileNotFoundError(f"Missing file: {THUMB_PATH}")

    audio_path, output_path = choose_audio_and_output(lang)

    if not audio_path.exists():
        raise FileNotFoundError(f"Missing audio file: {audio_path}")

    script_data = load_script()
    scenes = script_data.get("scenes", [])
    total_scene_duration = get_total_scene_duration(scenes)

    audio = AudioFileClip(str(audio_path))
    print("Audio duration:", audio.duration)

    final_duration = min(total_scene_duration, audio.duration)

    background = make_background_clip(str(THUMB_PATH), final_duration)
    overlay_clips = [background]

    for scene in scenes:
        start_sec = float(scene["start_sec"])
        end_sec = float(scene["end_sec"])

        if start_sec >= final_duration:
            continue

        scene_duration = min(end_sec, final_duration) - start_sec
        if scene_duration <= 0:
            continue

        caption_clip = make_caption_clip(
            text=scene["caption"],
            start=start_sec,
            duration=scene_duration,
        )
        overlay_clips.append(caption_clip)

    final_video = CompositeVideoClip(
        overlay_clips,
        size=VIDEO_SIZE,
    ).with_duration(final_duration)

    # важный момент: подрезаем/ставим аудио явно
    final_audio = audio.subclipped(0, final_duration)
    final_video = final_video.with_audio(final_audio)

    final_video.write_videofile(
        str(output_path),
        fps=30,
        codec="libx264",
        audio=True,
        audio_codec="aac",
        audio_fps=44100,
        temp_audiofile=str(OUTPUT_DIR / "temp_audio.m4a"),
        remove_temp=True,
    )

    audio.close()
    final_audio.close()
    final_video.close()

    print(f"\n✅ Video saved to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--english", action="store_true", help="Build English video")
    parser.add_argument("-r", "--russian", action="store_true", help="Build Russian video")
    args = parser.parse_args()

    build_en = args.english
    build_ru = args.russian

    if not build_en and not build_ru:
        build_en = True
        build_ru = True

    if build_en:
        print("\n--- BUILDING ENGLISH VIDEO ---")
        build_video("en")

    if build_ru:
        print("\n--- BUILDING RUSSIAN VIDEO ---")
        build_video("ru")


if __name__ == "__main__":
    main()