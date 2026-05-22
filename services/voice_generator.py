import os
from elevenlabs import ElevenLabs
from elevenlabs.types import MusicPrompt, SongSection


def generate_voice(lyrics: str, voice_type: str = "narrator", music_style: str = "") -> bytes:
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

    lines = [l.strip() for l in lyrics.strip().splitlines() if l.strip()]

    voice_styles = {
        "soprano":       ["bright female vocal", "soprano", "clear and high"],
        "mezzo-soprano": ["warm female vocal", "mezzo-soprano", "rich and smooth"],
        "tenor":         ["clear male vocal", "tenor", "bright and resonant"],
        "baritone":      ["deep male vocal", "baritone", "warm and powerful"],
        "narrator":      ["neutral vocal", "clear voice", "expressive"],
    }
    local_styles = voice_styles.get(voice_type.lower(), voice_styles["narrator"])

    global_styles = ["vocals", "singing"]
    if music_style:
        global_styles += [s.strip() for s in music_style.replace(",", " ").split() if s.strip()]

    plan = MusicPrompt(
        positive_global_styles=global_styles,
        negative_global_styles=["instrumental only", "no vocals"],
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
