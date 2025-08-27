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
    print("Ultralytics not available")

# Fix untuk video capture headless
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

def draw_minimal_bounding_box(image, boxes, confidences, classes):
    """
    Gambar bounding box minimal dan akurat untuk hilal
    """
    if len(boxes) == 0:
        return image
    
    height, width = image.shape[:2]
    
    for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
        x1, y1, x2, y2 = box.astype(int)
        
        # Pastikan koordinat dalam batas gambar
        x1 = max(0, min(x1, width-1))
        y1 = max(0, min(y1, height-1))
        x2 = max(0, min(x2, width-1))
        y2 = max(0, min(y2, height-1))
        
        # Hitung ukuran bounding box
        box_width = x2 - x1
        box_height = y2 - y1
        
        # Pilih warna berdasarkan confidence
        if conf > 0.8:
            color = (0, 255, 0)  # Hijau untuk confidence tinggi
            thickness = 3
        elif conf > 0.5:
            color = (0, 165, 255)  # Orange untuk confidence sedang
            thickness = 2
        else:
            color = (0, 255, 255)  # Kuning untuk confidence rendah
            thickness = 2
        
        # Gambar bounding box yang lebih tipis dan presisi
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
        
        # Tambahkan corner indicators untuk presisi lebih tinggi
        corner_length = min(box_width, box_height) // 8
        corner_length = max(10, min(corner_length, 25))
        
        # Corner kiri atas
        cv2.line(image, (x1, y1), (x1 + corner_length, y1), color, thickness + 1)
        cv2.line(image, (x1, y1), (x1, y1 + corner_length), color, thickness + 1)
        
        # Corner kanan atas
        cv2.line(image, (x2, y1), (x2 - corner_length, y1), color, thickness + 1)
        cv2.line(image, (x2, y1), (x2, y1 + corner_length), color, thickness + 1)
        
        # Corner kiri bawah
        cv2.line(image, (x1, y2), (x1 + corner_length, y2), color, thickness + 1)
        cv2.line(image, (x1, y2), (x1, y2 - corner_length), color, thickness + 1)
        
        # Corner kanan bawah
        cv2.line(image, (x2, y2), (x2 - corner_length, y2), color, thickness + 1)
        cv2.line(image, (x2, y2), (x2, y2 - corner_length), color, thickness + 1)
        
        # Label dengan background semi-transparan
        label = f"Hilal: {conf:.1%}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        
        # Posisi label yang tidak menutupi objek
        label_y = y1 - 10 if y1 > 30 else y2 + 25
        label_x = x1
        
        # Background untuk label
        cv2.rectangle(image, 
                     (label_x, label_y - label_size[1] - 5), 
                     (label_x + label_size[0] + 10, label_y + 5), 
                     (0, 0, 0), 
                     -1)
        
        # Text label
        cv2.putText(image, label, 
                   (label_x + 5, label_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                   (255, 255, 255), 2)
        
        # Tambahkan crosshair di tengah objek untuk presisi
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        crosshair_size = 10
        
        # Crosshair horizontal
        cv2.line(image, 
                (center_x - crosshair_size, center_y), 
                (center_x + crosshair_size, center_y), 
                color, 1)
        
        # Crosshair vertical
        cv2.line(image, 
                (center_x, center_y - crosshair_size), 
                (center_x, center_y + crosshair_size), 
                color, 1)
        
        # Tambahkan ID detection
        cv2.putText(image, f"#{i+1}", 
                   (x2 - 30, y1 + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                   color, 2)
    
    return image

def detect_image(image_path, model_path="best.pt"):
    """
    Deteksi objek hilal pada gambar dengan bounding box yang presisi
    """
    try:
        if not ULTRALYTICS_AVAILABLE:
            return create_dummy_detection(image_path, "image")
            
        # Check if model exists
        if not os.path.exists(model_path):
            print(f"Model file {model_path} not found, using dummy detection")
            return create_dummy_detection(image_path, "image")
            
        # Load model
        model = YOLO(model_path)
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Tidak dapat membaca gambar: {image_path}")
        
        original_image = image.copy()
        
        # Predict
        results = model.predict(
            source=image,
            imgsz=640,
            conf=0.25,
            iou=0.45,
            save=False,
            verbose=False
        )

        # Create output directory
        output_dir = Path("assets")
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f"detected_{Path(image_path).name}"
        
        # Process detections
        boxes = np.array([])
        confidences = np.array([])
        classes = np.array([])
        
        if len(results) > 0 and results[0].boxes is not None and len(results[0].boxes) > 0:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            classes = results[0].boxes.cls.cpu().numpy()
            
            # Filter detections dengan confidence tinggi
            high_conf_mask = confidences > 0.3
            boxes = boxes[high_conf_mask]
            confidences = confidences[high_conf_mask]
            classes = classes[high_conf_mask]
        
        if len(boxes) > 0:
            # Gambar bounding box custom
            annotated_image = draw_minimal_bounding_box(
                original_image, boxes, confidences, classes
            )
            
            # Tambahkan info detection di pojok
            info_text = f"Terdeteksi: {len(boxes)} Hilal"
            cv2.putText(annotated_image, info_text,
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                       (0, 255, 0), 2)
        else:
            annotated_image = original_image
        
        # Save annotated image
        cv2.imwrite(str(output_path), annotated_image)
        
        # Save CSV
        csv_path = save_detection_csv(boxes, confidences, classes, output_dir, Path(image_path).stem)
        
        return str(output_path), str(csv_path) if csv_path else None
        
    except Exception as e:
        print(f"Error in detect_image: {e}")
        return create_dummy_detection(image_path, "image")

def detect_video(video_path, model_path="best.pt"):
    """
    Deteksi objek hilal pada video dengan bounding box yang presisi
    """
    try:
        if not ULTRALYTICS_AVAILABLE:
            return create_dummy_detection(video_path, "video")
            
        if not os.path.exists(model_path):
            print(f"Model file {model_path} not found, using dummy detection")
            return create_dummy_detection(video_path, "video")
            
        # Load model
        model = YOLO(model_path)
        
        # Create output directory
        output_dir = Path("assets")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"detected_{Path(video_path).name}"

        # Process video
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
        
        frame_detections = None
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Run detection every 5th frame untuk performance
            if frame_count % 5 == 0:
                try:
                    results = model.predict(
                        source=frame,
                        imgsz=640,
                        conf=0.25,
                        iou=0.45,
                        verbose=False
                    )
                    
                    # Process frame
                    if len(results) > 0 and results[0].boxes is not None and len(results[0].boxes) > 0:
                        boxes = results[0].boxes.xyxy.cpu().numpy()
                        confidences = results[0].boxes.conf.cpu().numpy()
                        classes = results[0].boxes.cls.cpu().numpy()
                        
                        # Filter high confidence detections
                        high_conf_mask = confidences > 0.3
                        filtered_boxes = boxes[high_conf_mask]
                        filtered_confidences = confidences[high_conf_mask]
                        filtered_classes = classes[high_conf_mask]
                        
                        if len(filtered_boxes) > 0:
                            # Draw bounding boxes
                            annotated_frame = draw_minimal_bounding_box(
                                frame.copy(), filtered_boxes, filtered_confidences, filtered_classes
                            )
                            
                            # Store first significant detection for CSV
                            if frame_detections is None:
                                frame_detections = (filtered_boxes, filtered_confidences, filtered_classes)
                        else:
                            annotated_frame = frame
                    else:
                        annotated_frame = frame
                except:
                    annotated_frame = frame
            else:
                annotated_frame = frame
                
            out.write(annotated_frame)
            frame_count += 1
        
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
        # Save CSV for best frame
        csv_path = None
        if frame_detections:
            boxes, confidences, classes = frame_detections
            csv_path = save_detection_csv(boxes, confidences, classes, output_dir, Path(video_path).stem)
        
        return str(output_path), str(csv_path) if csv_path else None
        
    except Exception as e:
        print(f"Error in detect_video: {e}")
        return create_dummy_detection(video_path, "video")

def save_detection_csv(boxes, confidences, classes, output_dir, filename_stem):
    """
    Simpan hasil deteksi ke CSV dengan informasi lengkap
    """
    try:
        csv_path = output_dir / f"detected_{filename_stem}.csv"
        
        if len(boxes) > 0:
            # Hitung informasi tambahan
            widths = boxes[:, 2] - boxes[:, 0]
            heights = boxes[:, 3] - boxes[:, 1]
            centers_x = (boxes[:, 0] + boxes[:, 2]) / 2
            centers_y = (boxes[:, 1] + boxes[:, 3]) / 2
            areas = widths * heights
            
            # Create comprehensive DataFrame
            df = pd.DataFrame({
                "detection_id": range(1, len(boxes) + 1),
                "x1": boxes[:, 0].round(2),
                "y1": boxes[:, 1].round(2),
                "x2": boxes[:, 2].round(2),
                "y2": boxes[:, 3].round(2),
                "center_x": centers_x.round(2),
                "center_y": centers_y.round(2),
                "width": widths.round(2),
                "height": heights.round(2),
                "area": areas.round(2),
                "confidence": confidences.round(4),
                "class": classes.astype(int),
                "class_name": ["hilal"] * len(boxes)
            })
            
            # Sort by confidence descending
            df = df.sort_values('confidence', ascending=False).reset_index(drop=True)
            df.to_csv(csv_path, index=False)
            return csv_path
        else:
            # No detections found
            df = pd.DataFrame(columns=[
                "detection_id", "x1", "y1", "x2", "y2", 
                "center_x", "center_y", "width", "height", "area",
                "confidence", "class", "class_name"
            ])
            df.to_csv(csv_path, index=False)
            return csv_path
            
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return None

def create_dummy_detection(file_path, media_type):
    """
    Buat hasil deteksi dummy jika model tidak tersedia
    """
    try:
        output_dir = Path("assets")
        output_dir.mkdir(exist_ok=True)
        
        if media_type == "image":
            # Copy original image
            output_path = output_dir / f"detected_{Path(file_path).name}"
            import shutil
            shutil.copy2(file_path, output_path)
        else:  # video
            # Copy original video
            output_path = output_dir / f"detected_{Path(file_path).name}"
            import shutil
            shutil.copy2(file_path, output_path)
        
        # Create empty CSV
        csv_path = output_dir / f"detected_{Path(file_path).stem}.csv"
        df = pd.DataFrame(columns=[
            "detection_id", "x1", "y1", "x2", "y2", 
            "center_x", "center_y", "width", "height", "area",
            "confidence", "class", "class_name"
        ])
        df.to_csv(csv_path, index=False)
        
        return str(output_path), str(csv_path)
        
    except Exception as e:
        print(f"Error creating dummy detection: {e}")
        return None, None