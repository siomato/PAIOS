from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.ai.tts_service import synthesize_paios


router = APIRouter(tags=["PAIOS Voice"])


class SpeakRequest(BaseModel):
    text: str


@router.post("/speak")
async def speak(request: SpeakRequest):

    text = (request.text or "").strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )

    try:

        audio_path = await synthesize_paios(text)

        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename="paios.mp3",
            headers={
                "Cache-Control": "no-store",
                "X-PAIOS-Voice": "en-US-AriaNeural",
            },
        )

    except Exception as exc:

        print(f"PAIOS TTS ERROR: {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"PAIOS voice generation failed: {exc}"
        )