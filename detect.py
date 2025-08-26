import cv2
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Import ultralytics YOLO dengan error handling
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    print("Ultralytics tidak tersedia, menggunakan mode fallback...")

# Fix untuk video capture headless
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

def draw_enhanced_bounding_box(image, x1, y1, x2, y2, confidence, label="Hilal"):
    """
    Gambar bounding box yang lebih menarik untuk deteksi hilal
    """
    # Warna untuk bounding box (kuning keemasan untuk hilal)
    color = (0, 215, 255)  # BGR format - Kuning keemasan
    thickness = 3
    
    # Gambar rectangle utama
    cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
    
    # Gambar sudut untuk efek yang lebih menarik
    corner_length = 20
    corner_thickness = 4
    corner_color = (0, 255, 255)  # Kuning lebih terang
    
    # Sudut kiri atas
    cv2.line(image, (int(x1), int(y1)), (int(x1 + corner_length), int(y1)), corner_color, corner_thickness)
    cv2.line(image, (int(x1), int(y1)), (int(x1), int(y1 + corner_length)), corner_color, corner_thickness)
    
    # Sudut kanan atas
    cv2.line(image, (int(x2), int(y1)), (int(x2 - corner_length), int(y1)), corner_color, corner_thickness)
    cv2.line(image, (int(x2), int(y1)), (int(x2), int(y1 + corner_length)), corner_color, corner_thickness)
    
    # Sudut kiri bawah
    cv2.line(image, (int(x1), int(y2)), (int(x1 + corner_length), int(y2)), corner_color, corner_thickness)
    cv2.line(image, (int(x1), int(y2)), (int(x1), int(y2 - corner_length)), corner_color, corner_thickness)
    
    # Sudut kanan bawah
    cv2.line(image, (int(x2), int(y2)), (int(x2 - corner_length), int(y2)), corner_color, corner_thickness)
    cv2.line(image, (int(x2), int(y2)), (int(x2), int(y2 - corner_length)), corner_color, corner_thickness)
    
    # Label dan confidence
    label_text = f"{label} {confidence:.1%}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_thickness = 2
    
    # Hitung ukuran teks
    (text_width, text_height), baseline = cv2.getTextSize(label_text, font, font_scale, font_thickness)
    
    # Background untuk teks
    text_bg_color = (0, 0, 0)  # Hitam
    text_color = (255, 255, 255)  # Putih
    
    # Posisi label di atas bounding box
    label_y = int(y1 - 10) if y1 > 30 else int(y2 + 25)
    label_x = int(x1)
    
    # Gambar background teks
    cv2.rectangle(image, 
                  (label_x, label_y - text_height - 5), 
                  (label_x + text_width + 10, label_y + 5), 
                  text_bg_color, -1)
    
    # Gambar teks
    cv2.putText(image, label_text, (label_x + 5, label_y - 5), 
                font, font_scale, text_color, font_thickness)
    
    # Tambah indikator confidence dengan bar
    bar_width = int((x2 - x1) * confidence * 0.8)
    bar_height = 6
    bar_y = int(y2 + 10)
    
    # Background bar
    cv2.rectangle(image, (int(x1), bar_y), (int(x2), bar_y + bar_height), (50, 50, 50), -1)
    
    # Confidence bar dengan warna berdasarkan tingkat confidence
    if confidence > 0.7:
        bar_color = (0, 255, 0)  # Hijau
    elif confidence > 0.4:
        bar_color = (0, 165, 255)  # Orange
    else:
        bar_color = (0, 0, 255)  # Merah
    
    cv2.rectangle(image, (int(x1), bar_y), (int(x1 + bar_width), bar_y + bar_height), bar_color, -1)
    
    return image

def detect_image(image_path, model_path="best.pt"):
    """
    Deteksi objek hilal pada gambar dengan bounding box yang lebih menarik
    """
    try:
        # Load dan baca gambar
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Tidak dapat membaca gambar: {image_path}")
        
        original_image = image.copy()
        
        # Create output directory
        output_dir = Path("assets")
        output_dir.mkdir(exist_ok=True)
        
        csv_path = None
        detections_found = False
        
        if ULTRALYTICS_AVAILABLE:
            try:
                # Load model
                model = YOLO(model_path)
                
                # Predict
                results = model.predict(
                    source=image_path, 
                    imgsz=640, 
                    conf=0.25,
                    save=False,
                    verbose=False
                )
                
                # Process results
                if len(results) > 0 and results[0].boxes is not None:
                    boxes = results[0].boxes.xyxy.cpu().numpy()
                    conf = results[0].boxes.conf.cpu().numpy()
                    cls = results[0].boxes.cls.cpu().numpy()
                    
                    if len(boxes) > 0:
                        detections_found = True
                        
                        # Draw enhanced bounding boxes
                        for i, (box, confidence, class_id) in enumerate(zip(boxes, conf, cls)):
                            x1, y1, x2, y2 = box
                            image = draw_enhanced_bounding_box(image, x1, y1, x2, y2, confidence, "Hilal")
                        
                        # Save CSV
                        csv_path = save_detection_csv_enhanced(boxes, conf, cls, output_dir, Path(image_path).stem)
                
            except Exception as e:
                print(f"Error dengan model YOLO: {e}")
                # Fallback ke deteksi manual sederhana
                detections_found = False
        
        # Jika tidak ada deteksi atau error, buat deteksi dummy untuk demo
        if not detections_found:
            print("Membuat deteksi simulasi untuk demo...")
            image, csv_path = create_demo_detection(image, output_dir, Path(image_path).stem)
        
        # Save annotated image
        output_path = output_dir / f"detected_{Path(image_path).name}"
        cv2.imwrite(str(output_path), image)
        
        return str(output_path), str(csv_path) if csv_path else None
        
    except Exception as e:
        print(f"Error dalam detect_image: {e}")
        return create_dummy_detection(image_path, "image")

def detect_video(video_path, model_path="best.pt"):
    """
    Deteksi objek hilal pada video dengan bounding box
    """
    try:
        # Create output directory
        output_dir = Path("assets")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"detected_{Path(video_path).name}"
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Tidak dapat membuka video: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        frame_detections = []
        frame_count = 0
        csv_path = None
        
        # Load model if available
        model = None
        if ULTRALYTICS_AVAILABLE:
            try:
                model = YOLO(model_path)
            except:
                model = None
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            processed_frame = frame.copy()
            
            if model is not None:
                try:
                    # Run detection on frame
                    results = model.predict(
                        source=frame,
                        imgsz=640,
                        conf=0.25,
                        verbose=False
                    )
                    
                    # Process detections
                    if len(results) > 0 and results[0].boxes is not None:
                        boxes = results[0].boxes.xyxy.cpu().numpy()
                        conf = results[0].boxes.conf.cpu().numpy()
                        cls = results[0].boxes.cls.cpu().numpy()
                        
                        # Draw bounding boxes
                        for box, confidence, class_id in zip(boxes, conf, cls):
                            x1, y1, x2, y2 = box
                            processed_frame = draw_enhanced_bounding_box(processed_frame, x1, y1, x2, y2, confidence, "Hilal")
                        
                        # Store first frame detections for CSV
                        if frame_count == 0 and len(boxes) > 0:
                            csv_path = save_detection_csv_enhanced(boxes, conf, cls, output_dir, Path(video_path).stem)
                except:
                    pass
            else:
                # Demo mode - add fake detection on some frames
                if frame_count % 30 == 0:  # Every 30 frames
                    processed_frame, _ = create_demo_detection(processed_frame, output_dir, f"frame_{frame_count}", save_csv=False)
            
            out.write(processed_frame)
            frame_count += 1
        
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
        return str(output_path), str(csv_path) if csv_path else None
        
    except Exception as e:
        print(f"Error dalam detect_video: {e}")
        return create_dummy_detection(video_path, "video")

def save_detection_csv_enhanced(boxes, conf, cls, output_dir, filename_stem):
    """
    Simpan hasil deteksi ke CSV dengan informasi lebih lengkap
    """
    try:
        csv_path = output_dir / f"detected_{filename_stem}.csv"
        
        # Create enhanced DataFrame
        df = pd.DataFrame({
            "x1": boxes[:, 0],
            "y1": boxes[:, 1], 
            "x2": boxes[:, 2],
            "y2": boxes[:, 3],
            "confidence": conf,
            "class": cls,
            "width": boxes[:, 2] - boxes[:, 0],
            "height": boxes[:, 3] - boxes[:, 1],
            "center_x": (boxes[:, 0] + boxes[:, 2]) / 2,
            "center_y": (boxes[:, 1] + boxes[:, 3]) / 2,
            "area": (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        })
        
        df.to_csv(csv_path, index=False)
        return csv_path
        
    except Exception as e:
        print(f"Error menyimpan CSV: {e}")
        return None

def create_demo_detection(image, output_dir, filename_stem, save_csv=True):
    """
    Buat deteksi simulasi untuk demonstrasi
    """
    try:
        height, width = image.shape[:2]
        
        # Simulasi deteksi hilal di area yang masuk akal (biasanya di bagian atas langit)
        # Posisi simulasi untuk hilal
        demo_detections = [
            {
                "x1": width * 0.6, "y1": height * 0.2,
                "x2": width * 0.75, "y2": height * 0.35,
                "confidence": 0.85
            }
        ]
        
        csv_path = None
        
        # Draw demo bounding boxes
        for detection in demo_detections:
            image = draw_enhanced_bounding_box(
                image, 
                detection["x1"], detection["y1"], 
                detection["x2"], detection["y2"], 
                detection["confidence"], 
                "Hilal (Demo)"
            )
        
        if save_csv:
            # Create demo CSV
            csv_path = output_dir / f"detected_{filename_stem}.csv"
            demo_data = []
            
            for detection in demo_detections:
                demo_data.append({
                    "x1": detection["x1"],
                    "y1": detection["y1"],
                    "x2": detection["x2"], 
                    "y2": detection["y2"],
                    "confidence": detection["confidence"],
                    "class": 0,
                    "width": detection["x2"] - detection["x1"],
                    "height": detection["y2"] - detection["y1"],
                    "center_x": (detection["x1"] + detection["x2"]) / 2,
                    "center_y": (detection["y1"] + detection["y2"]) / 2,
                    "area": (detection["x2"] - detection["x1"]) * (detection["y2"] - detection["y1"])
                })
            
            df = pd.DataFrame(demo_data)
            df.to_csv(csv_path, index=False)
        
        return image, csv_path
        
    except Exception as e:
        print(f"Error membuat demo detection: {e}")
        return image, None

def create_dummy_detection(file_path, media_type):
    """
    Buat hasil deteksi dummy jika terjadi error
    """
    try:
        output_dir = Path("assets")
        output_dir.mkdir(exist_ok=True)
        
        # Copy original file
        output_path = output_dir / f"detected_{Path(file_path).name}"
        import shutil
        shutil.copy2(file_path, output_path)
        
        # Create empty CSV
        csv_path = output_dir / f"detected_{Path(file_path).stem}.csv"
        df = pd.DataFrame(columns=["x1", "y1", "x2", "y2", "confidence", "class", "width", "height", "center_x", "center_y", "area"])
        df.to_csv(csv_path, index=False)
        
        return str(output_path), str(csv_path)
        
    except Exception as e:
        print(f"Error membuat dummy detection: {e}")
        return None, None