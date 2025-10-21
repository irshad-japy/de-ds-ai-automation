# AI Creator System — FastAPI


## Prereqs
- Python 3.10+
- ffmpeg installed (for pydub)
- (Optional) Poetry


## Install
```bash
poetry install
# or
pip install -r requirements.txt

Run
uvicorn app.main:app --reload

Open docs: http://127.0.0.1:8000/docs

Example Flow (manual)

POST /publish/hashnode with a ContentItem JSON

POST /generate/takeaways

POST /generate/thumbnail

POST /generate/narration

POST /share/socials