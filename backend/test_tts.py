import asyncio

from app.ai.tts_service import synthesize_paios


async def main():
    path = await synthesize_paios(
        "PAIOS online. Neural voice communication initialized."
    )

    print(f"TTS generated successfully: {path}")


if __name__ == "__main__":
    asyncio.run(main())
