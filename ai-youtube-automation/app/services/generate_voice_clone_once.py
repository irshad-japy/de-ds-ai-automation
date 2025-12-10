"""
python app/services/generate_voice_clone_once.py
"""

from pathlib import Path
from xtts_voice_helper import clone_voice_once

if __name__ == "__main__":
    REF_AUDIO = Path(
        r"C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/output/Screen_Recording200452_audio.wav"
    )
    MY_SPEAKER_ID = "deepakVoice01"

    # language=None → falls back to DEFAULT_LANGUAGE (XTTS_LANGUAGE or "en")
    clone_voice_once(
        ref_audio_path=REF_AUDIO,
        speaker_id=MY_SPEAKER_ID,
        output_dir="clone_voice",   # will be under OUTPUT_ROOT/clone_voice if relative
        clone_text="वंदे मातरम् पर हमारा यह दूसरा एपिसोड है। इस एपिसोड में हमने ‘आनंदमठ’ और गांधी जी के विचारों पर बात की है। यह वीडियो भी थोड़ा लंबा है। इसके बाद तीसरा वीडियो भी आएगा, जो आज लोकसभा में हुई बहस के संदर्भ में होगा। उसका भी इंतज़ार कीजिए।",
        language="hi",              # explicit English
    )