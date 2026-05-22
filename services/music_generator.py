import os
from elevenlabs import ElevenLabs

MUSIC_DURATION = 15.0  # seconds — ElevenLabs sound generation max is 22s


def generate_music(music_prompt: str) -> bytes:
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    audio_chunks = client.text_to_sound_effects.convert(
        text=music_prompt,
        duration_seconds=MUSIC_DURATION,
        prompt_influence=0.4,
    )
    return b"".join(audio_chunks)
