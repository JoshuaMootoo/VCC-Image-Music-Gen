import base64
import io
import json
import os
import re
import requests
from PIL import Image

MAX_DIMENSION = 1568
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

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
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

    payload = {
        "model": GROQ_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": ANALYSIS_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{b64}"}},
            ],
        }],
        "max_tokens": 1500,
    }

    response = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
        json=payload,
        timeout=30,
    )
    if not response.ok:
        raise RuntimeError(f"Groq error {response.status_code}: {response.text}")
    response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"].strip()
    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return json.loads(content)
