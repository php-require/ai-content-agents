# 🚀 Shorts Agent

AI-powered pipeline for generating YouTube Shorts videos (script → voice → image → final video)

---

## 🧠 Overview | Обзор

EN:  
This project builds a **fully automated AI pipeline** for short-form video content:

- script generation (OpenAI)
- thumbnail prompt + image generation
- voice generation via **F5-TTS (local, free)**
- smart chunking + audio merging
- final video rendering (MoviePy)

No paid TTS. No external voice services. Everything runs locally except text generation.

---

## 📁 Project Structure

shorts-agent/

├── assets/  
│   └── voice_clean.wav  

├── output/  
│   └── dev/  
│       ├── script.json  
│       ├── thumbnail_prompt.json  
│       ├── thumbnail.png  
│       ├── voice_chunk_1.wav  
│       ├── voice_chunk_2.wav  
│       ├── ...  
│       ├── voiceover_en.wav  
│       └── final_video_en.mp4  

├── src/  
│   ├── agents/  
│   │   ├── script_agent.py  
│   │   ├── image_prompt_agent.py  
│   │   └── image_generator_agent.py  
│   │  
│   ├── prompts/  
│   ├── schemas/  
│   ├── utils/  
│   │  
│   ├── pipeline.py  
│   ├── tts_generator.py  
│   └── video_builder.py  

---

## ⚙️ Installation | Установка

git clone https://github.com/yourname/shorts-agent.git  
cd shorts-agent  

python -m venv .venv  

Windows:  
.venv\Scripts\activate  

pip install -r requirements.txt  

---

## 🔑 .env Configuration

OPENAI_API_KEY=your_api_key_here  

F5_MODEL=F5TTS_v1_Base  
F5_REF_AUDIO=assets/voice_clean.wav  
F5_REF_TEXT=Hello, this is a clean reference voice sample for text to speech generation.  

---

## 🎤 Voice System (F5-TTS)

- Fully local  
- No cost per generation  
- Uses reference audio + text  
- Generates voice in chunks for stability  

### ⚠️ Important

Reference audio must be:

- clean voice (no noise)  
- single speaker  
- 5–10 seconds  
- calm tone (no эмоции, крики)  
- must match F5_REF_TEXT  

---

## 🔁 Pipeline Flow

Script → Voice (chunked) → Merge → Image → Video  

---

# 🚀 How to Run

## 🔥 Full Pipeline (recommended)

python src/pipeline.py -i  

This generates:

- script  
- thumbnail prompt  
- thumbnail image  
- voice chunks  
- merged voice file  

---

## 🎬 Build Final Video

python src/video_builder.py -e  

Output:

output/dev/final_video_en.mp4  

---

# 🧠 How Voice Works

Instead of generating one long audio:

- text is split into chunks  
- each chunk → separate .wav  
- then merged into one final audio  

Example:

voice_chunk_1.wav  
voice_chunk_2.wav  
voice_chunk_3.wav  
→ voiceover_en.wav  

---

# ⚙️ Chunking Logic

- ~120–180 characters per chunk  
- prevents F5 crashes  
- keeps voice natural  

---

# 🎬 Video Builder

- MoviePy based  
- caption overlay  
- smooth zoom animation  
- attaches merged audio  
- exports final mp4  

---

## ⚠️ Common Issues

### ❌ No sound in video

Check:

- voiceover_en.wav exists  
- audio duration is not 0  
- MoviePy uses with_audio()  
- ffmpeg installed  

---

### ❌ F5 crashes

Fix:

- reduce chunk size  
- clean reference audio  
- match reference text  

---

### ❌ Weird voice / emotion spikes

Cause:

- bad reference audio  

Fix:

- record clean voice sample  

---

# 🔥 Recommended Workflow

## Fast test

python src/pipeline.py  

---

## Full generation

python src/pipeline.py -i  
python src/video_builder.py -e  

---

# 🛠 Tech Stack

- Python  
- OpenAI API  
- F5-TTS (local)  
- MoviePy  
- FFmpeg  
- Pillow  
- python-dotenv  

---

# 💡 Key Idea

This is not just a generator.

It is a **content factory**:

- scalable  
- cheap  
- automatable  
- ready for YouTube Shorts / TikTok  

---
