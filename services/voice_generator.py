import os
from elevenlabs import ElevenLabs
from elevenlabs.types import MusicPrompt, SongSection


def generate_song(lyrics: str, voice_type: str, music_style: str, music_instruments: list) -> bytes:
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

    lines = [l.strip() for l in lyrics.strip().splitlines() if l.strip()]

    voice_styles = {
        "soprano":       ["bright female vocal", "soprano"],
        "mezzo-soprano": ["warm female vocal", "mezzo-soprano"],
        "tenor":         ["clear male vocal", "tenor"],
        "baritone":      ["deep male vocal", "baritone"],
        "narrator":      ["expressive vocal", "clear voice"],
    }
    local_styles = voice_styles.get(voice_type.lower(), voice_styles["narrator"])

    global_styles = ["vocals", "singing"]
    if music_style:
        global_styles += [s.strip() for s in music_style.replace(",", " ").split() if s.strip()]
    if music_instruments:
        global_styles += music_instruments[:3]

    plan = MusicPrompt(
        positive_global_styles=global_styles,
        negative_global_styles=["instrumental only", "no vocals", "spoken word"],
        sections=[
            SongSection(
                section_name="verse",
                positive_local_styles=local_styles,
                negative_local_styles=[],
                duration_ms=max(len(lines) * 5000, 15000),
                lines=lines,
            )
        ],
    )

    audio_chunks = client.music.compose(
        composition_plan=plan,
        output_format="mp3_44100_128",
        force_instrumental=False,
    )
    return b"".join(audio_chunks)
