
# Output Script Helper

This folder contains a **standalone helper** to generate scripts (story or script mode) using your existing FastAPI (`audio_storybot/app.py`) and optionally synthesize **MP3 voice** via gTTS.

## Quickstart

1) In your project, run the FastAPI app:

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8099
```

2) In another terminal, run the helper:

```bash
python generate_script.py --file-path "C:\path\to\file.py" --mode story --language en --voice en
```

or with a raw URL:

```bash
python generate_script.py --file-url "https://raw.githubusercontent.com/user/repo/main/app.py" --mode script --voice en
```

### Tuning knobs
- `--audience Beginner`  (Beginner/Intermediate/Advanced)
- `--tone calm`
- `--humor 1`
- `--seconds 90`
- `--words 180`
- `--analogy cricket`
- `--voice en` (uses gTTS; omit to skip audio)

Outputs are saved right here in `output_script/` as `.txt`, `.md`, and optionally `.mp3`.

## Notes
- If you need Indian English voice, try `--voice en` (gTTS uses English). For more control, swap gTTS for any local TTS you prefer (e.g., pyttsx3, Edge-TTS).
- If the script can't reach the API, ensure it's running at `http://localhost:8099/explain` or set `STORYBOT_URL`.


# Local file
python generate_script.py --file-path "C:\Users\erirs\projects\ird-projects\de_ds_ai_automation\Local_Qdrant_RAG\main.py" --mode story --language en --voice en

# OR raw URL
python generate_script.py --file-url "https://raw.githubusercontent.com/user/repo/main/app.py" --mode script --voice en
