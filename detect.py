import cv2
import os
import pandas as pd
import numpy as np
from pathlib import Path
import math

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

def draw_enhanced_bounding_box(image, x1, y1, x2, y2, confidence, class_name="Hilal", class_id=0):
    """
    Gambar bounding box yang lebih menarik dan visible untuk deteksi hilal
    """
    # Convert coordinates to integers
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
    # Color scheme for different confidence levels
    if confidence > 0.8:
        primary_color = (0, 255, 0)  # Green for high confidence
        glow_color = (0, 255, 100)
    elif confidence > 0.5:
        primary_color = (0, 255, 255)  # Yellow for medium confidence
        glow_color = (100, 255, 255)
    else:
        primary_color = (0, 165, 255)  # Orange for low confidence
        glow_color = (100, 200, 255)
    
    # Calculate box dimensions
    width = x2 - x1
    height = y2 - y1
    
    # Draw main bounding box with thick border
    cv2.rectangle(image, (x1, y1), (x2, y2), primary_color, 3)
    
    # Draw corner decorations (L-shaped corners)
    corner_length = min(20, min(width, height) // 4)
    corner_thickness = 5
    
    # Top-left corner
    cv2.line(image, (x1, y1), (x1 + corner_length, y1), primary_color, corner_thickness)
    cv2.line(image, (x1, y1), (x1, y1 + corner_length), primary_color, corner_thickness)
    
    # Top-right corner
    cv2.line(image, (x2, y1), (x2 - corner_length, y1), primary_color, corner_thickness)
    cv2.line(image, (x2, y1), (x2, y1 + corner_length), primary_color, corner_thickness)
    
    # Bottom-left corner
    cv2.line(image, (x1, y2), (x1 + corner_length, y2), primary_color, corner_thickness)
    cv2.line(image, (x1, y2), (x1, y2 - corner_length), primary_color, corner_thickness)
    
    # Bottom-right corner
    cv2.line(image, (x2, y2), (x2 - corner_length, y2), primary_color, corner_thickness)
    cv2.line(image, (x2, y2), (x2, y2 - corner_length), primary_color, corner_thickness)
    
    # Draw center crosshair
    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
    crosshair_size = min(15, min(width, height) // 6)
    cv2.line(image, 
             (center_x - crosshair_size, center_y), 
             (center_x + crosshair_size, center_y), 
             primary_color, 2)
    cv2.line(image, 
             (center_x, center_y - crosshair_size), 
             (center_x, center_y + crosshair_size), 
             primary_color, 2)
    
    # Create label background
    label_text = f"🌙 {class_name} {confidence*100:.1f}%"
    
    # Calculate text size and position
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_thickness = 2
    
    (text_width, text_height), baseline = cv2.getTextSize(label_text, font_face, font_scale, font_thickness)
    
    # Position label above the box (or below if not enough space)
    label_y = y1 - 10 if y1 - text_height - 20 > 0 else y2 + text_height + 10
    label_x = x1
    
    # Draw label background with rounded corners effect
    padding = 8
    bg_x1, bg_y1 = label_x - padding, label_y - text_height - padding
    bg_x2, bg_y2 = label_x + text_width + padding, label_y + baseline + padding
    
    # Create semi-transparent background
    overlay = image.copy()
    cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), primary_color, -1)
    
    # Apply transparency
    alpha = 0.8
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
    
    # Draw border around label
    cv2.rectangle(image, (bg_x1, bg_y1), (bg_x2, bg_y2), primary_color, 2)
    
    # Draw text
    cv2.putText(image, label_text, (label_x, label_y), font_face, font_scale, (255, 255, 255), font_thickness)
    
    # Add confidence bar
    bar_width = min(100, width - 20)
    bar_height = 6
    bar_x = x1 + 10
    bar_y = y2 - 20
    
    # Background bar
    cv2.rectangle(image, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
    
    # Confidence bar
    conf_width = int(bar_width * confidence)
    cv2.rectangle(image, (bar_x, bar_y), (bar_x + conf_width, bar_y + bar_height), primary_color, -1)
    
    # Add glow effect (optional - creates a subtle outer glow)
    glow_thickness = 1
    for i in range(3):
        alpha_glow = 0.3 - (i * 0.1)
        glow_overlay = image.copy()
        cv2.rectangle(glow_overlay, 
                     (x1 - i - 1, y1 - i - 1), 
                     (x2 + i + 1, y2 + i + 1), 
                     glow_color, glow_thickness)
        cv2.addWeighted(glow_overlay, alpha_glow, image, 1 - alpha_glow, 0, image)
    
    return image

def detect_image(image_path, model_path="best.pt"):
    """
    Deteksi objek pada gambar menggunakan YOLOv5/v8 dengan enhanced bounding boxes
    """
    try:
        if not ULTRALYTICS_AVAILABLE:
            return create_dummy_detection(image_path, "image")
            
        # Load model
        model = YOLO(model_path)
        
        # Load original image
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise ValueError("Could not load image")
        
        # Create output directory
        output_dir = Path("assets")
        output_dir.mkdir(exist_ok=True)
        
        # Predict
        results = model.predict(
            source=image_path, 
            imgsz=640, 
            conf=0.25,
            save=False,
            verbose=False
        )

        # Create annotated image
        annotated_image = original_image.copy()
        detections_data = []
        
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            classes = results[0].boxes.cls.cpu().numpy()
            
            # Get class names if available
            class_names = getattr(model, 'names', {0: 'Hilal'})
            
            for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
                x1, y1, x2, y2 = box
                class_name = class_names.get(int(cls), f'Class_{int(cls)}')
                
                # Draw enhanced bounding box
                annotated_image = draw_enhanced_bounding_box(
                    annotated_image, x1, y1, x2, y2, conf, class_name, int(cls)
                )
                
                # Store detection data
                detections_data.append({
                    'detection_id': i + 1,
                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                    'width': x2 - x1, 'height': y2 - y1,
                    'center_x': (x1 + x2) / 2, 'center_y': (y1 + y2) / 2,
                    'confidence': conf,
                    'class': int(cls),
                    'class_name': class_name,
                    'area': (x2 - x1) * (y2 - y1)
                })
        
        # Add detection summary overlay
        if detections_data:
            summary_text = f"🌙 {len(detections_data)} Hilal Detected"
            avg_conf = np.mean([d['confidence'] for d in detections_data]) * 100
            
            # Add summary at top of image
            cv2.rectangle(annotated_image, (10, 10), (400, 80), (0, 0, 0), -1)
            cv2.rectangle(annotated_image, (10, 10), (400, 80), (0, 255, 255), 2)
            cv2.putText(annotated_image, summary_text, (20, 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(annotated_image, f"Avg Confidence: {avg_conf:.1f}%", (20, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        else:
            # No detections found
            cv2.rectangle(annotated_image, (10, 10), (300, 60), (0, 0, 0), -1)
            cv2.rectangle(annotated_image, (10, 10), (300, 60), (0, 0, 255), 2)
            cv2.putText(annotated_image, "No Hilal Detected", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Save annotated image
        output_path = output_dir / f"detected_{Path(image_path).name}"
        cv2.imwrite(str(output_path), annotated_image)
        
        # Save enhanced CSV
        csv_path = save_enhanced_detection_csv(detections_data, output_dir, Path(image_path).stem)
        
        return str(output_path), str(csv_path) if csv_path else None
        
    except Exception as e:
        print(f"Error in detect_image: {e}")
        return create_dummy_detection(image_path, "image")

def detect_video(video_path, model_path="best.pt"):
    """
    Deteksi objek pada video menggunakan YOLOv5/v8 dengan enhanced bounding boxes
    """
    try:
        if not ULTRALYTICS_AVAILABLE:
            return create_dummy_detection(video_path, "video")
            
        # Load model
        model = YOLO(model_path)
        
        # Create output directory
        output_dir = Path("assets")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"detected_{Path(video_path).name}"

        # Open input video
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        all_detections = []
        frame_count = 0
        
        print(f"Processing {total_frames} frames...")
        
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
            
            # Process detections
            annotated_frame = frame.copy()
            frame_detections = []
            
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                confidences = results[0].boxes.conf.cpu().numpy()
                classes = results[0].boxes.cls.cpu().numpy()
                
                class_names = getattr(model, 'names', {0: 'Hilal'})
                
                for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
                    x1, y1, x2, y2 = box
                    class_name = class_names.get(int(cls), f'Class_{int(cls)}')
                    
                    # Draw enhanced bounding box
                    annotated_frame = draw_enhanced_bounding_box(
                        annotated_frame, x1, y1, x2, y2, conf, class_name, int(cls)
                    )
                    
                    # Store detection for this frame
                    frame_detections.append({
                        'frame': frame_count,
                        'detection_id': i + 1,
                        'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                        'confidence': conf,
                        'class': int(cls),
                        'class_name': class_name
                    })
            
            # Add frame counter and detection info
            info_text = f"Frame: {frame_count+1}/{total_frames}"
            if frame_detections:
                info_text += f" | Detections: {len(frame_detections)}"
            
            cv2.rectangle(annotated_frame, (10, height-60), (400, height-10), (0, 0, 0), -1)
            cv2.putText(annotated_frame, info_text, (20, height-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Write processed frame
            out.write(annotated_frame)
            
            # Store detections
            all_detections.extend(frame_detections)
            
            frame_count += 1
            
            # Progress indicator
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames})")
        
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
        # Save CSV with all detections
        csv_path = save_enhanced_detection_csv(all_detections, output_dir, Path(video_path).stem, is_video=True)
        
        print(f"Video processing complete: {len(all_detections)} total detections")
        
        return str(output_path), str(csv_path) if csv_path else None
        
    except Exception as e:
        print(f"Error in detect_video: {e}")
        return create_dummy_detection(video_path, "video")

def save_enhanced_detection_csv(detections_data, output_dir, filename_stem, is_video=False):
    """
    Simpan hasil deteksi ke CSV dengan informasi yang lebih lengkap
    """
    try:
        csv_path = output_dir / f"detected_{filename_stem}.csv"
        
        if detections_data:
            # Convert to DataFrame
            df = pd.DataFrame(detections_data)
            
            # Add summary statistics for images
            if not is_video:
                # Add relative positions (normalized to 0-1)
                if 'x1' in df.columns:
                    # Assuming standard image dimensions for normalization
                    # In real implementation, you'd get actual image dimensions
                    df['rel_x1'] = df['x1'] / 640  # Normalize by detection image size
                    df['rel_y1'] = df['y1'] / 640
                    df['rel_x2'] = df['x2'] / 640
                    df['rel_y2'] = df['y2'] / 640
                
                # Add detection statistics
                summary_stats = {
                    'total_detections': len(df),
                    'avg_confidence': df['confidence'].mean() if 'confidence' in df else 0,
                    'max_confidence': df['confidence'].max() if 'confidence' in df else 0,
                    'min_confidence': df['confidence'].min() if 'confidence' in df else 0,
                }
                
                # Add summary as comment in CSV
                with open(csv_path, 'w') as f:
                    f.write("# Hilal Detection Results\n")
                    f.write(f"# Total Detections: {summary_stats['total_detections']}\n")
                    f.write(f"# Average Confidence: {summary_stats['avg_confidence']:.3f}\n")
                    f.write(f"# Max Confidence: {summary_stats['max_confidence']:.3f}\n")
                    f.write(f"# Detection Model: YOLOv5/v8\n")
                    f.write(f"# Confidence Threshold: 0.25\n#\n")
                
                # Append DataFrame
                df.to_csv(csv_path, mode='a', index=False)
            else:
                # For video, group by frame
                df['timestamp'] = df['frame'] / 30.0  # Assuming 30fps
                df.to_csv(csv_path, index=False)
                
                # Add video summary
                with open(csv_path.parent / f"video_summary_{filename_stem}.txt", 'w') as f:
                    f.write(f"Video Detection Summary\n")
                    f.write(f"======================\n")
                    f.write(f"Total Frames Processed: {df['frame'].max() + 1 if len(df) > 0 else 0}\n")
                    f.write(f"Total Detections: {len(df)}\n")
                    f.write(f"Frames with Detections: {df['frame'].nunique() if len(df) > 0 else 0}\n")
                    f.write(f"Average Confidence: {df['confidence'].mean():.3f}\n")
            
            return csv_path
        else:
            # No detections - create empty CSV with headers
            if is_video:
                headers = ['frame', 'detection_id', 'x1', 'y1', 'x2', 'y2', 'confidence', 'class', 'class_name', 'timestamp']
            else:
                headers = ['detection_id', 'x1', 'y1', 'x2', 'y2', 'width', 'height', 'center_x', 'center_y', 
                          'confidence', 'class', 'class_name', 'area', 'rel_x1', 'rel_y1', 'rel_x2', 'rel_y2']
            
            df = pd.DataFrame(columns=headers)
            
            with open(csv_path, 'w') as f:
                f.write("# Hilal Detection Results - No Detections Found\n")
                f.write("# Model: YOLOv5/v8\n")
                f.write("# Confidence Threshold: 0.25\n#\n")
            
            df.to_csv(csv_path, mode='a', index=False)
            return csv_path
            
    except Exception as e:
        print(f"Error saving enhanced CSV: {e}")
        return None

def create_dummy_detection(file_path, media_type):
    """
    Buat hasil deteksi dummy jika model tidak tersedia
    """
    try:
        output_dir = Path("assets")
        output_dir.mkdir(exist_ok=True)
        
        if media_type == "image":
            # Load and annotate image with "Model Not Available" message
            try:
                image = cv2.imread(file_path)
                if image is not None:
                    # Add "Model Unavailable" overlay
                    h, w = image.shape[:2]
                    
                    # Semi-transparent overlay
                    overlay = image.copy()
                    cv2.rectangle(overlay, (w//4, h//2-50), (3*w//4, h//2+50), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
                    
                    # Warning text
                    cv2.putText(image, "DETECTION MODEL UNAVAILABLE", 
                               (w//4 + 20, h//2 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.putText(image, "Showing original image", 
                               (w//4 + 20, h//2 + 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    output_path = output_dir / f"detected_{Path(file_path).name}"
                    cv2.imwrite(str(output_path), image)
                else:
                    # Fallback: copy original
                    import shutil
                    output_path = output_dir / f"detected_{Path(file_path).name}"
                    shutil.copy2(file_path, output_path)
            except:
                # Final fallback: copy original
                import shutil
                output_path = output_dir / f"detected_{Path(file_path).name}"
                shutil.copy2(file_path, output_path)
        
        else:  # video
            # Copy original video with warning
            import shutil
            output_path = output_dir / f"detected_{Path(file_path).name}"
            shutil.copy2(file_path, output_path)
        
        # Create empty CSV with explanation
        csv_path = output_dir / f"detected_{Path(file_path).stem}.csv"
        with open(csv_path, 'w') as f:
            f.write("# Detection model not available\n")
            f.write("# No detections performed\n")
            f.write("detection_id,x1,y1,x2,y2,confidence,class,class_name\n")
        
        return str(output_path), str(csv_path)
        
    except Exception as e:
        print(f"Error creating dummy detection: {e}")
        return None, None                     
           
                
                   
                   