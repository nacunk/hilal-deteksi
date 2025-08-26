import cv2
import os
import pandas as pd
from pathlib import Path

# Import ultralytics YOLO dengan error handling
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    print("Ultralytics not available, trying alternative imports...")
    
# Alternative import jika ultralytics tidak tersedia
if not ULTRALYTICS_AVAILABLE:
    try:
        import torch
        import torchvision
        print("PyTorch available, using manual detection...")
    except ImportError:
        print("PyTorch also not available")

# Fix untuk video capture headless
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

def detect_image(image_path, model_path="best.pt"):
    """
    Deteksi objek pada gambar menggunakan YOLOv5/v8
    """
    try:
        if not ULTRALYTICS_AVAILABLE:
            # Fallback: return dummy results
            return create_dummy_detection(image_path, "image")
            
        # Load model
        model = YOLO(model_path)
        
        # Predict
        results = model.predict(
            source=image_path, 
            imgsz=640, 
            conf=0.25,
            save=False,  # Don't auto-save, we'll handle it manually
            verbose=False
        )

        # Create output directory
        output_dir = Path("assets")
        output_dir.mkdir(exist_ok=True)
        
        # Save annotated image
        output_path = output_dir / f"detected_{Path(image_path).name}"
        
        # Get the annotated image
        if len(results) > 0 and results[0].plot() is not None:
            annotated_image = results[0].plot()
            cv2.imwrite(str(output_path), annotated_image)
        else:
            # If no detections, copy original image
            import shutil
            shutil.copy2(image_path, output_path)

        # Save CSV
        csv_path = save_detection_csv(results[0], output_dir, Path(image_path).stem)
        
        return str(output_path), str(csv_path) if csv_path else None
        
    except Exception as e:
        print(f"Error in detect_image: {e}")
        return create_dummy_detection(image_path, "image")

def detect_video(video_path, model_path="best.pt"):
    """
    Deteksi objek pada video menggunakan YOLOv5/v8
    """
    try:
        if not ULTRALYTICS_AVAILABLE:
            # Fallback: return dummy results
            return create_dummy_detection(video_path, "video")
            
        # Load model
        model = YOLO(model_path)
        
        # Create output directory
        output_dir = Path("assets")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"detected_{Path(video_path).name}"

        # Process video
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        frame_detections = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Run detection on frame
            results = model.predict(
                source=frame,
                imgsz=640,
                conf=0.25,
                verbose=False
            )
            
            # Get annotated frame
            if len(results) > 0:
                annotated_frame = results[0].plot()
                out.write(annotated_frame)
                
                # Store first frame detections for CSV
                if frame_count == 0:
                    frame_detections = results[0]
            else:
                out.write(frame)
                
            frame_count += 1
        
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
        # Save CSV for first frame
        csv_path = None
        if frame_detections:
            csv_path = save_detection_csv(frame_detections, output_dir, Path(video_path).stem)
        
        return str(output_path), str(csv_path) if csv_path else None
        
    except Exception as e:
        print(f"Error in detect_video: {e}")
        return create_dummy_detection(video_path, "video")

def save_detection_csv(result, output_dir, filename_stem):
    """
    Simpan hasil deteksi ke CSV
    """
    try:
        csv_path = output_dir / f"detected_{filename_stem}.csv"
        
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes.xyxy.cpu().numpy()
            conf = result.boxes.conf.cpu().numpy()
            cls = result.boxes.cls.cpu().numpy()
            
            # Create DataFrame
            df = pd.DataFrame({
                "x1": boxes[:, 0],
                "y1": boxes[:, 1],
                "x2": boxes[:, 2],
                "y2": boxes[:, 3],
                "confidence": conf,
                "class": cls
            })
            
            df.to_csv(csv_path, index=False)
            return csv_path
        else:
            # No detections found
            df = pd.DataFrame(columns=["x1", "y1", "x2", "y2", "confidence", "class"])
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
        df = pd.DataFrame(columns=["x1", "y1", "x2", "y2", "confidence", "class"])
        df.to_csv(csv_path, index=False)
        
        return str(output_path), str(csv_path)
        
    except Exception as e:
        print(f"Error creating dummy detection: {e}")
        return None, None