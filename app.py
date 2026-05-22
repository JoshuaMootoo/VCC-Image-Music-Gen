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
from services.voice_generator import generate_song

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
    result = {"analysis": analysis, "track_url": None}

    if analysis.get("has_people") and analysis.get("lyrics"):
        try:
            track_bytes = generate_song(
                lyrics=analysis["lyrics"],
                voice_type=analysis.get("suggested_voice_type", "narrator"),
                music_style=analysis.get("music_style", ""),
                music_instruments=analysis.get("music_instruments", []),
            )
            track_path = OUTPUTS_DIR / f"{session_id}_track.mp3"
            track_path.write_bytes(track_bytes)
            result["track_url"] = f"/outputs/{session_id}_track.mp3"
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Song generation failed: {exc}")
    else:
        try:
            track_bytes = generate_music(analysis["music_prompt"])
            track_path = OUTPUTS_DIR / f"{session_id}_track.mp3"
            track_path.write_bytes(track_bytes)
            result["track_url"] = f"/outputs/{session_id}_track.mp3"
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Music generation failed: {exc}")

    return JSONResponse(result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
