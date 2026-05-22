import base64
import io
import json
import os
import re

import requests
from PIL import Image

MAX_DIMENSION = 1568
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent"

ANALYSIS_PROMPT = """Analyze this image carefully for the purpose of generating an inspired music track. Return ONLY a valid JSON object with these exact keys:

{
  "scene_description": "A 1-2 sentence description of the overall scene",
  "objects": ["list", "of", "key", "objects", "and", "visual", "elements"],
  "mood": "Single word or short phrase: the dominant emotional mood",
  "atmosphere": "Short phrase: the atmospheric quality (e.g. warm and golden, cold and stark, mysterious and shadowy)",
  "colors": ["dominant", "color", "palette", "descriptors"],
  "setting": "Where this takes place (e.g. urban street, dense forest, cosy indoor, abstract space)",
  "has_people": true,
  "people_count": 1,
  "people_description": "Describe apparent age, gender, expression, energy and demeanour of people present. Empty string if no people.",
  "music_style": "Specific genre and style (e.g. ambient electronic, melancholic jazz, epic orchestral, lo-fi hip-hop)",
  "music_instruments": ["piano", "strings", "etc"],
  "music_tempo": "slow or medium or fast",
  "music_energy": "calm or moderate or intense",
  "music_prompt": "A detailed 2-3 sentence prompt for sound generation capturing the essence of this image. Be specific about instruments, tempo, mood, and sonic textures. Write it as a music description, not a command.",
  "suggested_voice_type": "One of: soprano, mezzo-soprano, tenor, baritone, narrator. Match to the people in the image. Omit this key entirely if has_people is false.",
  "lyrics": "3-4 lines of evocative lyrics inspired by the scene and the people, suitable for singing or reciting. Omit this key entirely if has_people is false."
}

Ensure has_people and people_count are accurate. Return only the JSON, no other text."""


def _resize_image(image_bytes: bytes, media_type: str) -> tuple[bytes, str]:
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > MAX_DIMENSION:
        scale = MAX_DIMENSION / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    fmt = "JPEG" if media_type in ("image/jpeg", "image/jpg") else "PNG"
    out_type = "image/jpeg" if fmt == "JPEG" else "image/png"
    img.save(buf, format=fmt, quality=85)
    return buf.getvalue(), out_type


def analyze_image(image_bytes: bytes, media_type: str) -> dict:
    image_bytes, media_type = _resize_image(image_bytes, media_type)

    payload = {
        "contents": [{
            "parts": [
                {"text": ANALYSIS_PROMPT},
                {"inline_data": {
                    "mime_type": media_type,
                    "data": base64.standard_b64encode(image_bytes).decode("utf-8"),
                }},
            ]
        }]
    }

    response = requests.post(
        GEMINI_URL,
        headers={"x-goog-api-key": os.environ["GOOGLE_API_KEY"]},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()

    content = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return json.loads(content)
