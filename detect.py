import torch
import os
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.torch_utils import select_device
from yolov5.utils.general import non_max_suppression, scale_coords

device = select_device("")
model = DetectMultiBackend("best.pt", device=device, dnn=False)
stride, names, pt = model.stride, model.names, model.pt

def detect_image(img_path):
    import cv2  # import lokal untuk menghindari ImportError
    img0 = cv2.imread(img_path)
    img = torch.from_numpy(img0).unsqueeze(0).float() / 255.0
    if img.ndim == 3:
        img = img[None]

    pred = model(img, augment=False, visualize=False)
    pred = non_max_suppression(pred, 0.25, 0.45)[0]

    if pred is not None and len(pred):
        pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], img0.shape).round()
        for *xyxy, conf, cls in pred:
            label = f"{names[int(cls)]} {conf:.2f}"
            cv2.rectangle(img0, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0,255,0), 2)
            cv2.putText(img0, label, (int(xyxy[0]), int(xyxy[1]-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    save_path = "assets/result_image.jpg"
    cv2.imwrite(save_path, img0)
    return save_path

def detect_video(video_path):
    import cv2  # import lokal
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

        img = torch.from_numpy(frame).unsqueeze(0).float() / 255.0
        if img.ndim == 3:
            img = img[None]

        pred = model(img, augment=False, visualize=False)
        pred = non_max_suppression(pred, 0.25, 0.45)[0]

        if pred is not None and len(pred):
            pred[:, :4] = scale_coords(img.shape[2:], pred[:, :4], frame.shape).round()
            for *xyxy, conf, cls in pred:
                label = f"{names[int(cls)]} {conf:.2f}"
                cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0,255,0), 2)
                cv2.putText(frame, label, (int(xyxy[0]), int(xyxy[1]-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        out.write(frame)

    cap.release()
    out.release()
    return out_path
