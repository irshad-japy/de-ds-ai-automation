from __future__ import annotations
import argparse, os
from pathlib import Path
from dotenv import load_dotenv

from .elevenlabs_backend import ElevenLabsTTS
from .edge_backend import edge_tts_synth
from .pyttsx3_backend import pyttsx3_synth

def parse_args():
    ap = argparse.ArgumentParser(description="TTS CLI for Python 3.12 (ElevenLabs / Edge / pyttsx3)")
    ap.add_argument("--backend", choices=["elevenlabs", "edge", "pyttsx3"], required=True)
    ap.add_argument("--text", "-t", required=True)
    ap.add_argument("--out", "-o", default="outputs/audio/tts_out.wav")

    # ElevenLabs
    ap.add_argument("--api_key", default=None)
    ap.add_argument("--voice_id", default=None)
    ap.add_argument("--clone_from", nargs="*", default=None, help="one or more audio files to clone from (ElevenLabs)")
    ap.add_argument("--el_model", default="eleven_multilingual_v2")
    ap.add_argument("--format", default="mp3", choices=["mp3", "wav"])

    # Edge TTS
    ap.add_argument("--edge_voice", default="en-US-AriaNeural")
    ap.add_argument("--edge_rate", default="+0%")
    ap.add_argument("--edge_volume", default="+0dB")

    # pyttsx3
    ap.add_argument("--offline_voice", default=None)  # name contains e.g. "Zira"
    ap.add_argument("--offline_rate", type=int, default=175)

    return ap.parse_args()

def main():
    load_dotenv()
    args = parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.backend == "elevenlabs":
        api_key = args.api_key or os.getenv("ELEVENLABS_API_KEY", "")
        if not api_key:
            raise SystemExit("Missing ELEVENLABS_API_KEY (env or --api_key).")
        el = ElevenLabsTTS(api_key)

        if args.clone_from:
            refs = [Path(p) for p in args.clone_from]
            out = el.clone_and_synth(
                text=args.text,
                out_path=out_path,
                ref_audio=refs,
                new_voice_name="MyClonedVoice",
                model_id=args.el_model,
                audio_format=args.format,
            )
        else:
            if not args.voice_id:
                raise SystemExit("For ElevenLabs without --clone_from, pass --voice_id.")
            out = el.synth(
                text=args.text,
                out_path=out_path,
                voice_id=args.voice_id,
                model_id=args.el_model,
                audio_format=args.format,
            )
        print(out)

    elif args.backend == "edge":
        out = edge_tts_synth(
            text=args.text,
            out_path=out_path.with_suffix(".mp3"),
            voice=args.edge_voice,
            rate=args.edge_rate,
            volume=args.edge_volume,
        )
        print(out)

    elif args.backend == "pyttsx3":
        out = pyttsx3_synth(
            text=args.text,
            out_path=out_path,
            rate=args.offline_rate,
            voice=args.offline_voice,
        )
        print(out)

if __name__ == "__main__":
    main()
