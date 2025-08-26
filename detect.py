import torch

# load model sekali saja, tidak perlu setiap fungsi
model = torch.hub.load("ultralytics/yolov5", "custom", path="best.pt", source="local")

def detect_image(img_path, model_path="best.pt"):
    results = model(img_path)
    save_path = "assets/result_image.jpg"
    results.save(save_dir="assets")  # otomatis save
    return save_path

def detect_video(video_path, model_path="best.pt"):
    results = model(video_path)
    # YOLOv5 sudah mendukung langsung input video
    results.save(save_dir="assets")
    return "assets"
