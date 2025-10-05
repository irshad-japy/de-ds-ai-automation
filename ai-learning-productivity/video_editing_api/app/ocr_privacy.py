
from __future__ import annotations
import cv2, pytesseract, re
from moviepy import VideoFileClip
import numpy as np

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(\+?\d[\d\-\s]{7,}\d)")
ID_RE    = re.compile(r"(?:PAN|AADHAAR|PASSPORT|SSN|EMPID)\s*[:\-]?\s*[A-Z0-9\-]{4,}", re.I)

def _blur_boxes(img_bgr, boxes, k=31):
    for (x, y, w, h) in boxes:
        x2, y2 = x+w, y+h
        roi = img_bgr[y:y2, x:x2]
        if roi.size:
            img_bgr[y:y2, x:x2] = cv2.GaussianBlur(roi, (k,k), 0)
    return img_bgr

def _find_sensitive_boxes(img_bgr, min_line_len: int=10):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 5, 50, 50)
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    boxes = []
    for i, txt in enumerate(data["text"]):
        if not txt or len(txt) < min_line_len:
            continue
        if EMAIL_RE.search(txt) or PHONE_RE.search(txt) or ID_RE.search(txt):
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            boxes.append((x, y, w, h))
    return boxes

def auto_blur_sensitive(in_video: str, out_video: str, sample_every: float=0.8, radius: float=0.6, min_line_len: int=10):
    with VideoFileClip(in_video) as clip:
        marks = []
        t = 0.0
        while t < clip.duration:
            frame = clip.get_frame(t)
            bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            boxes = _find_sensitive_boxes(bgr, min_line_len=min_line_len)
            if boxes:
                marks.append((t, boxes))
            t += max(0.5, sample_every)

        def blur_if_needed(rgb_frame, t):
            boxes_to_apply = []
            for tm, bx in marks:
                if abs(tm - t) <= radius:
                    boxes_to_apply.extend(bx)
            if not boxes_to_apply:
                return rgb_frame
            bgr = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            bgr = _blur_boxes(bgr, boxes_to_apply)
            return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        edited = clip.fl(lambda gf, tt: blur_if_needed(gf(tt), tt), apply_to=['mask','video'])
        edited.write_videofile(out_video, codec="libx264", audio_codec="aac", threads=4,
                               temp_audiofile="__tmp_audio.m4a", remove_temp=True)
