# VCC Image Music Generator

Upload an image and AI will analyse it with Claude Vision, then compose a unique music track using ElevenLabs. If people are detected in the image, it also generates sung/spoken lyrics inspired by the scene and creates a matching vocal track.

## How it works

1. **Image analysis** — Claude (`claude-sonnet-4-6`) identifies objects, mood, atmosphere, colours, and people in the image, then crafts a detailed music prompt.
2. **Music generation** — ElevenLabs Sound Generation API produces an atmospheric music track based on the prompt.
3. **Vocal track** *(people only)* — Claude writes evocative lyrics; ElevenLabs TTS renders them with a voice matched to the person's characteristics.

## Setup

### 1. Clone and install

```bash
git clone https://github.com/joshuamootoo/vcc-image-music-gen.git
cd vcc-image-music-gen
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env and add your keys:
#   ANTHROPIC_API_KEY=...
#   ELEVENLABS_API_KEY=...
```

### 3. Run

```bash
python app.py
# Open http://localhost:8000
```

## Project structure

```
app.py                  FastAPI backend
services/
  image_analyzer.py     Claude Vision image analysis
  music_generator.py    ElevenLabs sound generation
  voice_generator.py    ElevenLabs TTS vocal track
static/index.html       Single-page frontend
outputs/                Generated audio files (gitignored)
```

## Requirements

- Python 3.10+
- Anthropic API key (Claude claude-sonnet-4-6 vision)
- ElevenLabs API key (Sound Generation + TTS)
