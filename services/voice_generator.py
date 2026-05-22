import os
from elevenlabs import ElevenLabs

# Stable default ElevenLabs voice IDs
_VOICES = {
    "soprano": "EXAVITQu4vr4xnSDxMaL",       # Sarah — bright female
    "mezzo-soprano": "21m00Tcm4TlvDq8ikWAM",  # Rachel — warm female
    "tenor": "TxGEqnHWrfWFTfGW9XjX",          # Josh — clear male
    "baritone": "pNInz6obpgDQGcFmaJgB",        # Adam — resonant male
    "narrator": "onwK4e9ZLuTAKqWW03F9",        # Daniel — neutral narrator
}
_DEFAULT_VOICE = _VOICES["narrator"]


def generate_voice(lyrics: str, voice_type: str = "narrator") -> bytes:
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    voice_id = _VOICES.get(voice_type.lower(), _DEFAULT_VOICE)
    audio_chunks = client.text_to_speech.convert(
        voice_id=voice_id,
        text=lyrics,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    return b"".join(audio_chunks)
