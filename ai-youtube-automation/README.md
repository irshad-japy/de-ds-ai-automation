# AI Creator System — FastAPI

Run
uvicorn app.main:app --reload

Open docs: http://127.0.0.1:8000/docs

Example Flow (manual)

POST /publish/hashnode with a ContentItem JSON

POST /generate/takeaways

POST /generate_thumbnail/thumbnail

POST /generate/narration

POST /share/socials
-------------------------------------
voice generation
uvicorn api.main:app --reload --port 8099

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8099/generate-voice" `
  -Method Post `
  -Form @{file = Get-Item "C:\Users\erirs\projects\ird-projects\de_ds_ai_automation\voice_generation\scripts\generate_voice.py"} `
  -OutFile "C:\Users\erirs\projects\ird-projects\de_ds_ai_automation\voice_generation\output\voice_output.mp3"
-------------------------------------

run story_explain command
# audio_storybot

### Run
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8099
```
Then POST to `/explain` with either `file_path` or `file_url`.

✅ 1️⃣ Test with a local file path
$body = @{
  file_path = $demo
  mode = "story"
  language = "en"
  controls = @{
    target_audience = "Beginner"
    tone = "calm"
    humor_level = 1
    reading_time_sec = 90
    target_words = 180
    analogy_domain = "cricket"
    language = "English"
  }
} | ConvertTo-Json -Depth 6

$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8099/explain" -ContentType "application/json" -Body $body
# Client-side save (optional, in addition to the server-side save)
[IO.File]::WriteAllBytes("output.mp3", [Convert]::FromBase64String($response.audio_b64))
$response.meta.saved_to
"Saved output.mp3 locally and also on server."

✅ 2️⃣ Test with a remote file URL
# Replace with a URL that returns 200 OK in your browser (GitHub Raw > copy link)
$u = "https://raw.githubusercontent.com/irshad-japy/de-ds-ai-automation/master/utils/write_json.py"

$body = @{
  file_url = $u
  mode = "story"
  language = "en"
  controls = @{
    target_audience = "Beginner"
    tone = "calm"
    humor_level = 1
    reading_time_sec = 90
    target_words = 180
    analogy_domain = "cricket"
    language = "English"
  }
} | ConvertTo-Json -Depth 6

$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8099/explain" -ContentType "application/json" -Body $body
[IO.File]::WriteAllBytes("output.mp3", [Convert]::FromBase64String($response.audio_b64))
$response.meta.saved_to
"Saved output.mp3 locally and also on server."


# Does the file actually exist?
Test-Path 'C:\Users\erirs\projects\ird-projects\de_ds_ai_automation\ai-learning-productivity\audio_storybot\app.py'


C) With background music (after installing ffmpeg)
$bg = (Resolve-Path .\assets\soft-bg.mp3).Path -replace '\\','/'
$body = @{
  file_path = $demo
  mode = "story"
  language = "en"
  bg_music_path = $bg
  controls = @{
    target_audience = "Beginner"
    tone = "calm"
    humor_level = 1
    reading_time_sec = 90
    target_words = 180
    analogy_domain = "cricket"
    language = "English"
  }
} | ConvertTo-Json -Depth 6

$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8099/explain" -ContentType "application/json" -Body $body
$response.meta.saved_to

% check file path is correct or not
$u = "https://raw.githubusercontent.com/irshad-japy/de-ds-ai-automation/master/utils/write_json.py"

try {
  $r = Invoke-WebRequest -Uri $u -Method Head -ErrorAction Stop
  "OK: $($r.StatusCode) $($r.StatusDescription)"
} catch {
  "ERROR: $($_.Exception.Response.StatusCode.value__)"
}
