import cv2
import torch
import os
from pathlib import Path

# --- Set folder hasil ---
RESULT_DIR = Path("assets")
RESULT_DIR.mkdir(exist_ok=True)

# --- Load model YOLOv5 (PyPI v7.0.12) ---
# Best.pt = model hilal
model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', source='pypi')

# --- Fungsi deteksi gambar ---
def detect_image(img_path):
    results = model(img_path)
    # simpan hasil di folder assets
    results.save(save_dir=RESULT_DIR)
    # ambil file terakhir yang disimpan
    save_path = list(RESULT_DIR.glob("*.jpg"))[-1]
    return str(save_path)

# --- Fungsi deteksi video ---
def detect_video(video_path):
    cap = cv2.VideoCapture(video_path)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = int(cap.get(cv2.CAP_PROP_FPS))

    # Output video
    out_path = RESULT_DIR / "result_video.mp4"
    out = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # deteksi frame
        results = model(frame)
        # render hasil deteksi ke frame
        frame_result = results.render()[0]
        out.write(frame_result)

    cap.release()
    out.release()
    return str(out_path)
