import torch
import cv2
import os

def detect_image(img_path, model_path="best.pt"):
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, source='github')
    results = model(img_path)
    save_path = "assets/result_image.jpg"
    results.save(save_path)
    return save_path

def detect_video(video_path, model_path="best.pt"):
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, source='github')
    cap = cv2.VideoCapture(video_path)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = int(cap.get(cv2.CAP_PROP_FPS))

    out_path = "assets/result_video.mp4"
    out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)
        frame_result = results.render()[0]
        out.write(frame_result)

    cap.release()
    out.release()
    return out_path
