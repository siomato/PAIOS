from pathlib import Path
import tempfile
import uuid

import edge_tts


PAIOS_TTS_VOICE = "en-US-AriaNeural"
PAIOS_TTS_RATE = "-10%"
PAIOS_TTS_PITCH = "-18Hz"
PAIOS_TTS_VOLUME = "+0%"


async def synthesize_paios(text: str) -> Path:

    text = (text or "").strip()

    if not text:
        raise ValueError("TTS text cannot be empty.")

    output_dir = (
        Path(tempfile.gettempdir())
        / "paios_tts"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        output_dir
        / f"paios_{uuid.uuid4().hex}.mp3"
    )

    communicate = edge_tts.Communicate(
        text=text,
        voice=PAIOS_TTS_VOICE,
        rate=PAIOS_TTS_RATE,
        pitch=PAIOS_TTS_PITCH,
        volume=PAIOS_TTS_VOLUME,
    )

    await communicate.save(
        str(output_path)
    )

    if (
        not output_path.exists()
        or output_path.stat().st_size == 0
    ):
        raise RuntimeError(
            "PAIOS TTS generated an empty audio file."
        )

    return output_path
