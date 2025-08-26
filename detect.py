import torch
import cv2
import os
from pathlib import Path
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.general import non_max_suppression, scale_coords
from yolov5.utils.torch_utils import select_device

def detect_image(image_path, model_path="best.pt"):
    device = select_device('')
    model = DetectMultiBackend(model_path, device=device)
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_tensor = torch.from_numpy(img_rgb).permute(2,0,1).float() / 255.0
    img_tensor = img_tensor.unsqueeze(0).to(device)

    pred = model(img_tensor, augment=False)
    pred = non_max_suppression(pred, conf_thres=0.25, iou_thres=0.45)

    for det in pred:
        if len(det):
            det[:, :4] = scale_coords(img_tensor.shape[2:], det[:, :4], img.shape).round()
            for *xyxy, conf, cls in det:
                x1, y1, x2, y2 = map(int, xyxy)
                cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.putText(img, f"Hilal {conf:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
    
    output_path = os.path.join("assets", "detected_"+Path(image_path).name)
    cv2.imwrite(output_path, img)
    return output_path

def detect_video(video_path, model_path="best.pt"):
    device = select_device('')
    model = DetectMultiBackend(model_path, device=device)

    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_path = os.path.join("assets", "detected_"+Path(video_path).name)
    out = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_tensor = torch.from_numpy(img_rgb).permute(2,0,1).float()/255.0
        img_tensor = img_tensor.unsqueeze(0).to(device)

        pred = model(img_tensor, augment=False)
        pred = non_max_suppression(pred, conf_thres=0.25, iou_thres=0.45)

        for det in pred:
            if len(det):
                det[:, :4] = scale_coords(img_tensor.shape[2:], det[:, :4], frame.shape).round()
                for *xyxy, conf, cls in det:
                    x1, y1, x2, y2 = map(int, xyxy)
                    cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0),2)
                    cv2.putText(frame, f"Hilal {conf:.2f}", (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
        
        if out is None:
            out = cv2.VideoWriter(out_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (frame.shape[1], frame.shape[0]))
        out.write(frame)

    cap.release()
    out.release()
    return out_path
