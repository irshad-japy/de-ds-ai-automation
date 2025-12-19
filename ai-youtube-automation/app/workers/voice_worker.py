from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime

from app.services.generate_voice import generate_voice as eleven_generate_voice
from app.services.generate_voice_2 import generate_voice as default_generate_system_voice
from app.services.xtts_voice_helper import tts_with_cached_speaker


def main():
    req_path = Path(sys.argv[1])
    payload = json.loads(req_path.read_text(encoding="utf-8"))

    text = payload["text"]
    service_model = payload.get("service_model", "Default")
    speaker_id = payload.get("speaker_id")
    language = payload.get("language", "en")
    # print(f'generate_voice payload: {payload}')
    # output path passed from API (preferred), else generate here
    out_path = payload.get("out_path")
    if not out_path:
        project_root = Path(__file__).resolve().parents[2]
        output_dir = project_root / "output" / "final_video"
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = str(output_dir / f"{service_model.lower()}_voice_{ts}.wav")

    if service_model == "TTS":
        # XTTS typically needs a speaker_id
        path = tts_with_cached_speaker(
            text=text,
            speaker_id=speaker_id,
            out_path=str(out_path),
            language=language,
        )

    elif service_model == "ElevenLabs":
        
        path = eleven_generate_voice(
            text=text,
            speaker_id=speaker_id,
            out_path=str(out_path),
            language=language,
        )

    else:  # "Default"
        path = default_generate_system_voice(
            text=text,
            out_path=str(out_path),
        )

    print(str(Path(path).resolve()))

if __name__ == "__main__":
    main()
