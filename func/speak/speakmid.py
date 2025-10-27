# func/speak/speakmid.py
import asyncio
import edge_tts
import pygame
import tempfile
import os

async def _speak_async(text: str):
    """Internal async TTS using Edge-TTS Python API (no terminal junk)."""
    voice = "en-CA-LiamNeural"
    rate = "+22%"
    pitch = "+9Hz"

    output_file = os.path.join(tempfile.gettempdir(), "ava_voice.mp3")
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(output_file)

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

def mid(text: str):
    """Main callable for Ava's speaking."""
    try:
        asyncio.run(_speak_async(text))
    except RuntimeError:
        # If event loop already running (like inside PyQt), use alternative
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_speak_async(text))
