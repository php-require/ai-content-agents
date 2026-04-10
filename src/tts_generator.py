import os
import shutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from moviepy import AudioFileClip, concatenate_audioclips

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve_project_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def _get_f5_config(lang: str) -> tuple[str, Path, str]:
    """
    Возвращает настройки для F5-TTS
    """
    model = os.getenv("F5_MODEL", "F5TTS_v1_Base")

    if lang == "ru":
        ref_audio_raw = os.getenv("F5_REF_AUDIO_RU") or os.getenv("F5_REF_AUDIO")
        ref_text = os.getenv("F5_REF_TEXT_RU") or os.getenv("F5_REF_TEXT", "")
    else:
        ref_audio_raw = os.getenv("F5_REF_AUDIO")
        ref_text = os.getenv("F5_REF_TEXT", "")

    if not ref_audio_raw:
        raise ValueError(f"❌ F5 reference audio not set for lang={lang}")

    ref_audio = _resolve_project_path(ref_audio_raw)

    if not ref_audio.exists():
        raise FileNotFoundError(f"❌ Reference audio not found: {ref_audio}")

    if not ref_text.strip():
        raise ValueError(f"❌ F5 reference text not set for lang={lang}")

    return model, ref_audio, ref_text.strip()


def generate_tts(text: str, output_path: str, lang: str = "en") -> str:
    """
    Генерация озвучки через F5-TTS

    Args:
        text: текст для озвучки
        output_path: куда сохранить wav
        lang: "en" или "ru"

    Returns:
        путь к аудиофайлу
    """
    if not text or not text.strip():
        raise ValueError("❌ Empty text for TTS")

    if shutil.which("f5-tts_infer-cli") is None:
        raise RuntimeError("❌ f5-tts_infer-cli not found in PATH")

    model, ref_audio, ref_text = _get_f5_config(lang)

    output_file = _resolve_project_path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n🎤 Generating TTS ({lang})...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Reference audio: {ref_audio}")
    print(f"Output file: {output_file}")
    print(f"Text length: {len(text)} chars")

    cmd = [
        "f5-tts_infer-cli",
        "--model", model,
        "--ref_audio", str(ref_audio),
        "--ref_text", ref_text,
        "--gen_text", text.strip(),
        "--output_file", str(output_file),
    ]

    try:
        result = subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=True,
            cwd=str(PROJECT_ROOT),
        )

        if result.stdout and result.stdout.strip():
            print("\n--- F5 STDOUT ---")
            print(result.stdout)

        if result.stderr and result.stderr.strip():
            print("\n--- F5 STDERR ---")
            print(result.stderr)

    except subprocess.CalledProcessError as e:
        print("\n--- F5 COMMAND ---")
        print(" ".join(cmd))

        print("\n--- F5 STDOUT ---")
        print((e.stdout or "").strip() or "(empty)")

        print("\n--- F5 STDERR ---")
        print((e.stderr or "").strip() or "(empty)")

        raise RuntimeError(f"❌ F5-TTS failed: {e}")

    if not output_file.exists():
        raise FileNotFoundError(f"❌ TTS output not created: {output_file}")

    print(f"✅ TTS saved: {output_file}")
    return str(output_file)


def merge_wav_files(input_files: list[str], output_file: str) -> str:
    """
    Склеивает несколько wav-файлов в один.
    """
    if not input_files:
        raise ValueError("❌ No input audio files to merge")

    resolved_inputs = [_resolve_project_path(p) for p in input_files]
    resolved_output = _resolve_project_path(output_file)
    resolved_output.parent.mkdir(parents=True, exist_ok=True)

    missing = [str(p) for p in resolved_inputs if not p.exists()]
    if missing:
        raise FileNotFoundError(f"❌ Missing audio chunks: {missing}")

    clips = []
    final_audio = None

    try:
        for file_path in resolved_inputs:
            clips.append(AudioFileClip(str(file_path)))

        final_audio = concatenate_audioclips(clips)
        final_audio.write_audiofile(str(resolved_output))

    finally:
        for clip in clips:
            try:
                clip.close()
            except Exception:
                pass

        if final_audio is not None:
            try:
                final_audio.close()
            except Exception:
                pass

    if not resolved_output.exists():
        raise FileNotFoundError(f"❌ Merged audio not created: {resolved_output}")

    print(f"✅ Merged audio saved: {resolved_output}")
    return str(resolved_output)