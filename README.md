# Shorts Agent

AI-powered Python pipeline for generating YouTube Shorts content.

---

## 🚀 Overview | Обзор

EN:  
This project builds a full short-form video pipeline using OpenAI:
- script generation
- thumbnail generation
- voice generation (EN / RU)
- final video rendering

RU:  
Это пайплайн для создания коротких видео (Shorts):
- генерация сценария
- генерация превью (картинки)
- озвучка (английская / русская)
- сборка финального видео

---

## 📁 Project Structure

src/
  agents/
    script_agent.py
    image_prompt_agent.py
    image_generator_agent.py

  prompts/
    it_shorts_prompt.py
    thumbnail_prompt.py

  schemas/
    it_shorts_schema.py
    thumbnail_schema.py

  utils/
    file_utils.py

  tools/
    list_models.py

  pipeline.py
  tts_generator.py
  video_builder.py

---

## ⚙️ Installation | Установка

git clone https://github.com/yourname/shorts-agent.git  
cd shorts-agent  

python -m venv .venv  

Windows:
.venv\Scripts\activate  

pip install -r requirements.txt  

Create .env:

OPENAI_API_KEY=your_api_key_here

---

## 📂 Output

output/dev/
  script.json
  thumbnail_prompt.json
  thumbnail.png
  voiceover_en.mp3
  voiceover_ru.mp3
  final_video_en.mp4
  final_video_ru.mp4

---

# 🧠 1. Script / Image Pipeline

Run:

python pipeline.py

Commands:

Script only:
python pipeline.py

Full pipeline (script + thumbnail + image):
python pipeline.py -i

Flag:
-i → включает генерацию картинки

---

# 🎤 2. Voice Generator

Run:

python tts_generator.py

Commands:

English only:
python tts_generator.py -er

Russian only:
python tts_generator.py -rr

Both:
python tts_generator.py

---

## 💰 Request Logic

EN (-er):
- rewrite
- TTS  
= 2 запроса

RU (-rr):
- translate
- rewrite
- TTS  
= 3 запроса

Both:
- EN rewrite + TTS
- RU translate + rewrite + TTS  
= 5 запросов

---

# 🎬 3. Video Builder

Run:

python video_builder.py

Commands:

English video:
python video_builder.py -e

Russian video:
python video_builder.py -r

Both:
python video_builder.py

---

## ⚠️ Important

video_builder.py:
- не использует OpenAI API
- работает локально (moviepy + ffmpeg)

---

## 🔁 Recommended Workflows

🔥 Быстрый тест (дешево):
python pipeline.py

🔥 С картинкой:
python pipeline.py -i

🔥 EN видео:
python pipeline.py -i  
python tts_generator.py -er  
python video_builder.py -e  

🔥 RU видео:
python pipeline.py -i  
python tts_generator.py -rr  
python video_builder.py -r  

🔥 Полный пайплайн:
python pipeline.py -i  
python tts_generator.py  
python video_builder.py  

---

## 🛠 Tech

- Python
- OpenAI API
- MoviePy
- Pillow
- imageio-ffmpeg
- JSON Schema
- python-dotenv