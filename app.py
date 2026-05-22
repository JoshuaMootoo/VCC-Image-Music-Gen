import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

from services.image_analyzer import analyze_image
from services.music_generator import generate_music
from services.voice_generator import generate_voice

app = FastAPI(title="VCC Image Music Generator")

OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/generate")
async def generate(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type '{file.content_type}'. Use JPEG, PNG, WebP, or GIF.",
        )

    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image exceeds 10 MB limit.")

    try:
        analysis = analyze_image(image_bytes, file.content_type)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {exc}")

    session_id = uuid.uuid4().hex[:10]

    try:
        music_bytes = generate_music(analysis["music_prompt"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Music generation failed: {exc}")

    music_path = OUTPUTS_DIR / f"{session_id}_music.mp3"
    music_path.write_bytes(music_bytes)

    result = {
        "analysis": analysis,
        "music_url": f"/outputs/{session_id}_music.mp3",
        "voice_url": None,
    }

    if analysis.get("has_people") and analysis.get("lyrics"):
        voice_type = analysis.get("suggested_voice_type", "narrator")
        try:
            voice_bytes = generate_voice(analysis["lyrics"], voice_type, analysis.get("music_style", ""))
            voice_path = OUTPUTS_DIR / f"{session_id}_voice.mp3"
            voice_path.write_bytes(voice_bytes)
            result["voice_url"] = f"/outputs/{session_id}_voice.mp3"
        except Exception as exc:
            # Non-fatal — music is still available
            result["voice_error"] = str(exc)

    return JSONResponse(result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
