# Advanced Video Editing API (FastAPI)
[See detailed README in previous cell if needed; this file is included in the zip.]

uvicorn app.main:app --reload --port 8080

Health check:
curl http://localhost:8080/health

A) Clean noise & normalize loudness
$body = @'
{ "video_path": "input/demo.mp4" }
'@
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/denoise_normalize" -ContentType "application/json" -Body $body

B) Remove dead air / blank frames
$body = @'
{ "video_path": "input/demo.mp4" }
'@
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/auto_trim_blank" -ContentType "application/json" -Body $body

C) Blur sensitive on-screen text (emails/phones/IDs)
$body = @'
{ "video_path": "input/demo.mp4", "sample_every": 1.0, "min_line_len": 10 }
'@
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/auto_blur_sensitive" -ContentType "application/json" -Body $body

D) Full cleanup (trim → denoise → blur) in one call
$body = @'
{ "video_path": "input/demo.mp4" }
'@
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/cleanup" -ContentType "application/json" -Body $body

E) Auto-generate professional script (OCR outline → clean template)
$body = @'
{
  "video_path": "input/demo.mp4",
  "sample_every": 1.0,
  "scene_sensitivity": 0.20,
  "target_seconds": 75,
  "min_line_len": 10,
  "max_lines": 18
}
'@
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/autoscript" -ContentType "application/json" -Body $body

F) TTS narration (duration-aware) + merge
$body = @'
{
  "voiceover_json_path": "output/demo_voiceover.json",
  "video_path": "input/demo.mp4",
  "target_seconds": 75,
  "loudnorm": true
}
'@
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/produce_narrated" -ContentType "application/json" -Body $body

G) Replace audio track with your own WAV/MP3
$body = @'
{
  "video_path": "input/demo.mp4",
  "audio_path": "input/narration.wav",
  "loudnorm": true
}
'@
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/replac e_audio" -ContentType "application/json" -Body $body

H) One-shot: autoscript → TTS → merge
$body = @'
{
  "video_path": "input/demo.mp4",
  "target_seconds": 75,
  "loudnorm": true
}
'@
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/produce_full" -ContentType "application/json" -Body $body


-----------------------------------------------
Thumnail commands
$body = @'
{
  "video_path": "input/demo.mp4",
  "at_seconds": 7,
  "overlay_title": "Automate Tasks",
  "overlay_sub": "in 1 Minute",
  "overlay_small": "Step by Step",
  "logo_path": "assets/logo.png"
}
'@
$r = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/thumbnail" -ContentType "application/json" -Body $body
$r.saved_path


Batch (evenly spaced):
$body = @'
{
  "video_path": "input/demo.mp4",
  "evenly_n": 5,
  "start_at": 5.0
}
'@
$r = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/thumbnails/batch" -ContentType "application/json" -Body $body
$r.generated | ForEach-Object { $_.saved_path }
