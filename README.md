# VCC Image Music Generator

Upload an image and AI will analyse it, then compose a unique music track using ElevenLabs. If people are detected in the image, it generates a full song with sung vocals inspired by the scene.

## How it works

1. **Image analysis** — Groq (Llama 4 Scout vision) identifies objects, mood, atmosphere, colours, and people in the image, then crafts a detailed music prompt.
2. **Music generation** — ElevenLabs Sound Generation API produces an atmospheric instrumental track based on the prompt (images without people).
3. **Song generation** *(people only)* — ElevenLabs Music Generation composes a full song with sung vocals and matching instrumentation, using lyrics and style derived from the image analysis.

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org) installed and on your PATH
- Groq API key (free at [console.groq.com](https://console.groq.com))
- ElevenLabs API key with the following permissions enabled:
  - Text to Speech — Access
  - Sound Effects — Access
  - Music Generation — Access

## Setup

### 1. Clone and install

```bash
git clone https://github.com/joshuamootoo/vcc-image-music-gen.git
cd vcc-image-music-gen
pip install -r requirements.txt
```

**Install ffmpeg** (required for audio processing):
- Windows: `winget install ffmpeg`
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### 2. Configure API keys

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### 3. Run

```bash
python app.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Project structure

```
app.py                  FastAPI backend
services/
  image_analyzer.py     Groq vision image analysis
  music_generator.py    ElevenLabs sound effects (instrumental)
  voice_generator.py    ElevenLabs music.compose (song with vocals)
static/index.html       Single-page frontend
outputs/                Generated audio files (gitignored)
```
