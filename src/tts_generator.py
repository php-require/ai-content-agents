import json
import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image
from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    VideoClip,
    ImageClip,
)

OUTPUT_DIR = Path("output/dev")
SCRIPT_PATH = OUTPUT_DIR / "script.json"
THUMB_PATH = OUTPUT_DIR / "thumbnail.png"

VOICE_EN_PATH = OUTPUT_DIR / "voiceover_en.mp3"
VOICE_RU_PATH = OUTPUT_DIR / "voiceover_ru.mp3"

FINAL_EN_PATH = OUTPUT_DIR / "final_video_en.mp4"
FINAL_RU_PATH = OUTPUT_DIR / "final_video_ru.mp4"

VIDEO_SIZE = (1080, 1920)

CAPTION_WIDTH = 920
CAPTION_Y = 1280
FONT_SIZE = 74
TEXT_STROKE = 4

# Плавный зум
ZOOM_START = 1.00
ZOOM_END = 1.08


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


def ease_in_out(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * t)


def make_static_background_clip(image_path: str, duration: float) -> ImageClip:
    """
    Полностью статичный фон.
    Используется, если зум выключен.
    """
    return (
        ImageClip(image_path)
        .resized(height=VIDEO_SIZE[1])
        .with_duration(duration)
        .with_position("center")
    )


def prepare_base_image(image_path: str) -> Image.Image:
    """
    Готовим увеличенное изображение, из которого потом вырезаются кадры.
    Это стабильнее, чем покадровый resize исходного клипа.
    """
    img = Image.open(image_path).convert("RGB")

    target_w, target_h = VIDEO_SIZE

    # Берем максимальный scale, чтобы canvas всегда был достаточным
    scale_for_canvas = max(ZOOM_START, ZOOM_END)
    canvas_w = int(target_w * scale_for_canvas)
    canvas_h = int(target_h * scale_for_canvas)

    src_w, src_h = img.size
    scale = max(canvas_w / src_w, canvas_h / src_h)

    resized_w = int(src_w * scale)
    resized_h = int(src_h * scale)

    img = img.resize((resized_w, resized_h), Image.LANCZOS)

    left = (resized_w - canvas_w) // 2
    top = (resized_h - canvas_h) // 2
    img = img.crop((left, top, left + canvas_w, top + canvas_h))

    return img


def make_smooth_background_clip(image_path: str, duration: float):
    """
    Если зум выключен — возвращаем статичный ImageClip.
    Если включен — делаем плавный фон через crop из большого canvas.
    """
    if abs(ZOOM_END - ZOOM_START) < 1e-9:
        return make_static_background_clip(image_path, duration)

    base_img = prepare_base_image(image_path)
    base_np = np.array(base_img)

    canvas_h, canvas_w = base_np.shape[:2]
    out_w, out_h = VIDEO_SIZE

    def make_frame(t: float):
        progress = min(max(t / max(duration, 0.001), 0.0), 1.0)
        eased = ease_in_out(progress)

        zoom = ZOOM_START + (ZOOM_END - ZOOM_START) * eased

        crop_w = int(round(out_w / zoom))
        crop_h = int(round(out_h / zoom))

        x = int(round((canvas_w - crop_w) / 2))
        y = int(round((canvas_h - crop_h) / 2))

        frame = base_np[y:y + crop_h, x:x + crop_w]
        frame_img = Image.fromarray(frame).resize((out_w, out_h), Image.LANCZOS)
        return np.array(frame_img)

    return VideoClip(make_frame, duration=duration)


def make_caption_clip(text: str, start: float, duration: float) -> TextClip:
    return (
        TextClip(
            text=text,
            font_size=FONT_SIZE,
            color="white",
            method="caption",
            size=(CAPTION_WIDTH, 280),
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
    final_duration = min(total_scene_duration, audio.duration)

    background = make_smooth_background_clip(str(THUMB_PATH), final_duration)

    clips = [background]

    for scene in scenes:
        start_sec = float(scene["start_sec"])
        end_sec = float(scene["end_sec"])

        if start_sec >= final_duration:
            continue

        scene_duration = min(end_sec, final_duration) - start_sec
        if scene_duration <= 0:
            continue

        caption = scene["caption"]

        clips.append(
            make_caption_clip(
                text=caption,
                start=start_sec,
                duration=scene_duration,
            )
        )

    final_video = CompositeVideoClip(
        clips,
        size=VIDEO_SIZE,
    ).with_duration(final_duration)

    final_video = final_video.with_audio(audio)

    final_video.write_videofile(
        str(output_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
    )

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