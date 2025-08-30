import torch
import cv2
import os

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='models/best.pt', source='local')

def detect_image(image_path, save_path='outputs/'):
    img = cv2.imread(image_path)
    results = model(img)
    results.save(save_path)
    return results
