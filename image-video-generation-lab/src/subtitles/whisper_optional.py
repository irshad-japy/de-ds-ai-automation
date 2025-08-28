from pathlib import Path

def transcribe_with_whisper(audio_path: Path):
    try:
        import whisper
    except ImportError:
        return None  # whisper not available
    model = whisper.load_model("base")  # downloads once
    result = model.transcribe(str(audio_path), fp16=False)
    # Build a trivial SRT from segments
    from datetime import timedelta
    import srt
    subs = []
    for i, seg in enumerate(result.get("segments", []), start=1):
        start = timedelta(seconds=seg["start"])
        end = timedelta(seconds=seg["end"])
        subs.append(srt.Subtitle(index=i, start=start, end=end, content=seg["text"].strip()))
    return srt.compose(subs) if subs else None
