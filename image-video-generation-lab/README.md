# image-video-generation-lab

Beginner‑friendly **Image & Video Generation** lab with three tools in one Gradio app:

1) **Text‑to‑Image** (Stable Diffusion via 🤗 diffusers)
2) **AI Meme Generator** (overlay top/bottom text)
3) **AI Shorts / Video Generator** (script → TTS → slideshow → MP4 + SRT captions)

> Works on CPU (slow) or GPU (faster). Optional ElevenLabs TTS. Optional Whisper for captions.

---

---

## 2) Setup

```bash
# Clone or unzip this project
cd image-video-generation-lab

poetry add $(cat image-video-generation-lab/requirements.txt)

poetry shall
```

If you want **ElevenLabs TTS**:
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
``

-----------------------------------------
6. Using the Voice / TTS Tab
A. ElevenLabs (Cloud TTS)
model id is: eleven_multilingual_v2

B. B. Local Parler-TTS (Offline AI TTS)
model id is : parler-tts/parler-tts-mini-v1
