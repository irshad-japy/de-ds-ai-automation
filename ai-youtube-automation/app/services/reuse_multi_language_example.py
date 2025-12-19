"""
python -m app.services.reuse_multi_language_example
"""

# reuse_multi_language_example.py
from app.services.xtts_voice_helper import tts_with_cached_speaker

MY_SPEAKER_ID = "deepakVoice01"

def main():
    # English
    output_path = tts_with_cached_speaker(
        text="This is our second episode on Vande Mataram. In this episode, we talk about Anandamath and Mahatma Gandhi’s views. This video is also a bit long. After this, there will be a third video as well, based on the debate that took place in the Lok Sabha today. Stay tuned for that too.",
        speaker_id=MY_SPEAKER_ID,
        out_path="C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/ai-youtube-automation/output/clone_voice/deepak_en.wav",
        language="en",
    )

    # Hindi
    tts_with_cached_speaker(
        text="वंदे मातरम् पर हमारा यह दूसरा एपिसोड है। इस एपिसोड में हमने ‘आनंदमठ’ और गांधी जी के विचारों पर बात की है। यह वीडियो भी थोड़ा लंबा है। इसके बाद तीसरा वीडियो भी आएगा, जो आज लोकसभा में हुई बहस के संदर्भ में होगा। उसका भी इंतज़ार कीजिए।",
        speaker_id=MY_SPEAKER_ID,
        out_path="clone_voice/deepak_hi.wav",
        language="hi",
    )

if __name__ == "__main__":
    main()
