import cv2
import os
import pandas as pd
from pathlib import Path
from ultralytics import YOLO

# Fix untuk video capture headless
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

def detect_image(image_path, model_path="best.pt"):
    model = YOLO(model_path)
    results = model.predict(source=image_path, imgsz=640, conf=0.25)

    # Save image
    output_dir = Path("assets")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"detected_{Path(image_path).name}"
    results[0].plot(save=True, save_path=str(output_path))

    # Save CSV
    csv_path = output_dir / f"detected_{Path(image_path).stem}.csv"
    if results[0].boxes is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        conf = results[0].boxes.conf.cpu().numpy()
        cls = results[0].boxes.cls.cpu().numpy()
        df = pd.DataFrame({
            "x1": boxes[:,0],
            "y1": boxes[:,1],
            "x2": boxes[:,2],
            "y2": boxes[:,3],
            "conf": conf,
            "class": cls
        })
        df.to_csv(csv_path, index=False)
    else:
        csv_path = None

    return str(output_path), str(csv_path)

def detect_video(video_path, model_path="best.pt"):
    model = YOLO(model_path)
    output_dir = Path("assets")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"detected_{Path(video_path).name}"

    results = model.predict(source=video_path, conf=0.25, save=True, save_path=str(output_path))
    
    # CSV untuk video: ambil frame pertama saja
    csv_path = output_dir / f"detected_{Path(video_path).stem}.csv"
    if results[0].boxes is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        conf = results[0].boxes.conf.cpu().numpy()
        cls = results[0].boxes.cls.cpu().numpy()
        df = pd.DataFrame({
            "x1": boxes[:,0],
            "y1": boxes[:,1],
            "x2": boxes[:,2],
            "y2": boxes[:,3],
            "conf": conf,
            "class": cls
        })
        df.to_csv(csv_path, index=False)
    else:
        csv_path = None

    return str(output_path), str(csv_path) if csv_path else None
