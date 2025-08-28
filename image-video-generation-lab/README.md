# image-video-generation-lab

Beginner‑friendly **Image & Video Generation** lab with three tools in one Gradio app:

1) **Text‑to‑Image** (Stable Diffusion via 🤗 diffusers)
2) **AI Meme Generator** (overlay top/bottom text)
3) **AI Shorts / Video Generator** (script → TTS → slideshow → MP4 + SRT captions)

> Works on CPU (slow) or GPU (faster). Optional ElevenLabs TTS. Optional Whisper for captions.

---

## 1) Prerequisites

- **Python** 3.10+
- **FFmpeg** installed and on PATH
  - Windows (PowerShell): `winget install Gyan.FFmpeg` (or install from ffmpeg.org)
  - macOS (Homebrew): `brew install ffmpeg`
  - Linux (Debian/Ubuntu): `sudo apt-get update && sudo apt-get install -y ffmpeg`
- **PyTorch** (install per your OS/GPU)
  - **CUDA 12.x GPU (Windows/Linux):**
    ```bash
    pip install --upgrade pip
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    ```
  - **CPU only (any OS):**
    ```bash
    pip install --upgrade pip
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    ```

> If you already have torch installed, you can skip the above.

---

## 2) Setup

```bash
# Clone or unzip this project
cd image-video-generation-lab

# Create & activate virtual env (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
# python -m venv .venv
# source .venv/bin/activate

# Install Python deps (Torch must be installed beforehand as above)
pip install -r requirements.txt
or
poetry add $(cat image-video-generation-lab/requirements.txt)

```

(Optional) If you want **ElevenLabs TTS**:
1. Copy `.env.example` to `.env` and set `ELEVENLABS_API_KEY` (and voice id if you have one).
2. Leave it blank to use offline `pyttsx3` TTS.

> **Model selection**: By default we use `stabilityai/sd-turbo` (fast). You may need a free HuggingFace account and to accept model terms.
If needed, login once:
```bash
pip install huggingface_hub
huggingface-cli login
```
You can change the model id in the UI or via `MODEL_ID` in `.env`.

---

## 3) Run the Gradio App

```bash
python -m image-video-generation-lab.src.app
# or
python src/app.py
```

Your browser will open at a local URL (e.g., http://127.0.0.1:7860).

Outputs are saved under the `outputs/` folder:
- `outputs/images/` (text-to-image)
- `outputs/memes/` (memes)
- `outputs/videos/` (MP4) and `outputs/audio/` (TTS .wav) and sidecar `.srt` captions

---

## 4) Quick CLI Examples (optional)

Generate one image from prompt:
```bash
python -m src.t2i.generate -p "cinematic 8k photorealistic portrait of a lion" -o outputs/images
```

Create a meme using a background prompt (no upload needed):
```bash
python -m src.meme.generate --background-prompt "dramatic sunset landscape" --top "WHEN PROD WORKS" --bottom "AND YOU DID NOTHING"
```

Create a short video (slideshow + TTS + captions):
```bash
python -m src.shorts.generate --script "AI will transform workflows. Automate boring tasks. Focus on impact." --slides 5 --seconds 3
```

---

## 5) Notes

- First run may download models (Diffusers, Whisper if enabled).
- **Captions**: By default we generate an `.srt` by splitting your script across the audio length.
  If you set `USE_WHISPER=true` in `.env` and have `whisper` installed, we'll try to transcribe and build captions from the audio.
- **Subtitles rendering**: Most players (VLC, Windows Movies & TV, etc.) auto‑load the `.srt` next to the MP4. To burn captions into the video, see comments in `src/shorts/generate.py` for an ffmpeg command.

Enjoy! ✨

-----------------------------------
try to install gradio its depend on 
ruff
issue1. starlette but have installed verion smaller required higher
issue2: isse vc_redist.x64.exe to need to install 
issue3: in short folder generates.py file getting issue like syntax or not proper import file
issue4: space in device 
issue5: dll failed to get cpu or gpu related issue
issue7: ImageClip is attribute error to generate short videos