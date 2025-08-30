import cv2
import os
import pandas as pd
import numpy as np
from pathlib import Path
import math
import json
import time
from datetime import datetime

# Import ultralytics YOLO dengan error handling
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    print("Ultralytics not available, using fallback detection...")

# Fix untuk video capture headless
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

class EnhancedHilalDetector:
    """
    Enhanced hilal detection system for research purposes
    """
    
    def __init__(self, model_path="best.pt", confidence_threshold=0.25):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.detection_history = []
        
        if ULTRALYTICS_AVAILABLE:
            try:
                self.model = YOLO(model_path)
                print(f"✅ Model loaded successfully: {model_path}")
            except Exception as e:
                print(f"❌ Model loading failed: {e}")
                self.model = None
        else:
            print("⚠️ YOLO not available, using research simulation mode")
    
    def detect_with_research_metrics(self, image_path, save_annotations=True):
        """
        Enhanced detection with comprehensive research metrics
        """
        start_time = time.time()
        
        try:
            # Load original image
            original_image = cv2.imread(image_path)
            if original_image is None:
                raise ValueError("Could not load image")
            
            image_height, image_width = original_image.shape[:2]
            
            # Create output directory
            output_dir = Path("assets")
            output_dir.mkdir(exist_ok=True)
            
            detection_results = {
                'image_path': image_path,
                'image_width': image_width,
                'image_height': image_height,
                'model_confidence_threshold': self.confidence_threshold,
                'processing_start_time': datetime.now().isoformat(),
                'detections': [],
                'summary_statistics': {},
                'research_metrics': {}
            }
            
            if self.model is not None:
                # Real YOLO detection
                results = self.model.predict(
                    source=image_path,
                    imgsz=640,
                    conf=self.confidence_threshold,
                    save=False,
                    verbose=False
                )
                
                # Process real detections
                annotated_image = original_image.copy()
                
                if len(results) > 0 and results[0].boxes is not None:
                    boxes = results[0].boxes.xyxy.cpu().numpy()
                    confidences = results[0].boxes.conf.cpu().numpy()
                    classes = results[0].boxes.cls.cpu().numpy()
                    
                    class_names = getattr(self.model, 'names', {0: 'Hilal'})
                    
                    for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
                        x1, y1, x2, y2 = box
                        class_name = class_names.get(int(cls), f'Class_{int(cls)}')
                        
                        # Enhanced bounding box with research annotations
                        annotated_image = self.draw_research_bounding_box(
                            annotated_image, x1, y1, x2, y2, conf, class_name, i+1
                        )
                        
                        # Comprehensive detection data for research
                        detection_data = self.calculate_detection_metrics(
                            x1, y1, x2, y2, conf, class_name, image_width, image_height
                        )
                        detection_data['detection_id'] = i + 1
                        detection_results['detections'].append(detection_data)
                
                # Calculate summary statistics
                detection_results['summary_statistics'] = self.calculate_summary_statistics(
                    detection_results['detections'], image_width, image_height
                )
                
            else:
                # Simulation mode for research when model unavailable
                detection_results = self.simulate_research_detection(
                    original_image, image_width, image_height
                )
                annotated_image = self.add_simulation_overlay(original_image)
            
            # Add research-specific overlays
            annotated_image = self.add_research_overlays(
                annotated_image, detection_results
            )
            
            # Save annotated image
            output_path = output_dir / f"research_detected_{Path(image_path).name}"
            cv2.imwrite(str(output_path), annotated_image)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            detection_results['processing_time_seconds'] = round(processing_time, 3)
            detection_results['processing_end_time'] = datetime.now().isoformat()
            
            # Save comprehensive detection data
            json_path = output_dir / f"research_data_{Path(image_path).stem}.json"
            with open(json_path, 'w') as f:
                json.dump(detection_results, f, indent=2)
            
            # Save CSV for compatibility
            csv_path = self.save_research_csv(detection_results, output_dir, Path(image_path).stem)
            
            return str(output_path), str(csv_path), detection_results
            
        except Exception as e:
            print(f"Detection error: {e}")
            return self.create_error_output(image_path, str(e))
    
    def draw_research_bounding_box(self, image, x1, y1, x2, y2, confidence, class_name, detection_id):
        """
        Draw enhanced bounding box with research annotations
        """
        # Convert coordinates to integers
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        
        # Research color scheme based on confidence
        if confidence > 0.8:
            primary_color = (0, 255, 0)  # Green - high confidence
            secondary_color = (100, 255, 100)
        elif confidence > 0.6:
            primary_color = (0, 255, 255)  # Yellow - medium confidence
            secondary_color = (100, 255, 255)
        elif confidence > 0.4:
            primary_color = (0, 165, 255)  # Orange - low confidence
            secondary_color = (100, 200, 255)
        else:
            primary_color = (0, 100, 255)  # Red - very low confidence
            secondary_color = (100, 150, 255)
        
        # Main detection box
        cv2.rectangle(image, (x1, y1), (x2, y2), primary_color, 3)
        
        # Research ID and metrics overlay
        width = x2 - x1
        height = y2 - y1
        area = width * height
        aspect_ratio = width / height if height > 0 else 0
        
        # Enhanced corner markers
        corner_size = min(25, min(width, height) // 3)
        thickness = 4
        
        # Draw L-shaped corners
        corners = [
            (x1, y1, x1 + corner_size, y1, x1, y1 + corner_size),  # Top-left
            (x2 - corner_size, y1, x2, y1, x2, y1 + corner_size),  # Top-right
            (x1, y2 - corner_size, x1, y2, x1 + corner_size, y2),  # Bottom-left
            (x2 - corner_size, y2, x2, y2, x2, y2 - corner_size)   # Bottom-right
        ]
        
        for corner in corners:
            cv2.line(image, (corner[0], corner[1]), (corner[2], corner[3]), primary_color, thickness)
            cv2.line(image, (corner[0], corner[1]), (corner[4], corner[5]), primary_color, thickness)
        
        # Central crosshair with ID
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        crosshair_size = min(20, min(width, height) // 4)
        
        cv2.line(image, (center_x - crosshair_size, center_y), 
                (center_x + crosshair_size, center_y), primary_color, 2)
        cv2.line(image, (center_x, center_y - crosshair_size), 
                (center_x, center_y + crosshair_size), primary_color, 2)
        
        # Detection ID circle
        cv2.circle(image, (center_x, center_y), 15, primary_color, -1)
        cv2.putText(image, str(detection_id), (center_x - 5, center_y + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Research information panel
        panel_width = 280
        panel_height = 120
        panel_x = max(10, min(x1, image.shape[1] - panel_width - 10))
        panel_y = max(10, y1 - panel_height - 10) if y1 > panel_height + 20 else y2 + 10
        
        # Semi-transparent background
        overlay = image.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, image, 0.2, 0, image)
        
        # Panel border
        cv2.rectangle(image, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     primary_color, 2)
        
        # Research annotations
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1
        line_height = 20
        
        annotations = [
            f"ID: {detection_id} | {class_name}",
            f"Confidence: {confidence*100:.1f}%",
            f"Size: {width}x{height}px (Area: {area})",
            f"Aspect Ratio: {aspect_ratio:.2f}",
            f"Center: ({center_x}, {center_y})"
        ]
        
        for i, text in enumerate(annotations):
            y_pos = panel_y + 20 + (i * line_height)
            cv2.putText(image, text, (panel_x + 10, y_pos), 
                       font, font_scale, (255, 255, 255), font_thickness)
        
        # Confidence bar
        bar_width = 200
        bar_height = 8
        bar_x = panel_x + 10
        bar_y = panel_y + panel_height - 20
        
        # Background bar
        cv2.rectangle(image, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                     (50, 50, 50), -1)
        
        # Confidence fill
        conf_width = int(bar_width * confidence)
        cv2.rectangle(image, (bar_x, bar_y), (bar_x + conf_width, bar_y + bar_height), 
                     primary_color, -1)
        
        return image
    
    def calculate_detection_metrics(self, x1, y1, x2, y2, confidence, class_name, img_width, img_height):
        """
        Calculate comprehensive metrics for research analysis
        """
        width = x2 - x1
        height = y2 - y1
        area = width * height
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Normalized coordinates (0-1)
        norm_x1 = x1 / img_width
        norm_y1 = y1 / img_height
        norm_x2 = x2 / img_width
        norm_y2 = y2 / img_height
        norm_center_x = center_x / img_width
        norm_center_y = center_y / img_height
        
        # Additional research metrics
        aspect_ratio = width / height if height > 0 else 0
        area_percentage = (area / (img_width * img_height)) * 100
        
        # Position analysis
        distance_from_center = math.sqrt(
            (center_x - img_width/2)**2 + (center_y - img_height/2)**2
        ) / (img_width/2)  # Normalized distance from image center
        
        # Shape analysis
        bounding_box_ratio = area / (width * height) if (width * height) > 0 else 0
        
        return {
            'class_name': class_name,
            'confidence': float(confidence),
            'confidence_category': self.categorize_confidence(confidence),
            
            # Absolute coordinates
            'x1': float(x1), 'y1': float(y1), 'x2': float(x2), 'y2': float(y2),
            'width': float(width), 'height': float(height),
            'center_x': float(center_x), 'center_y': float(center_y),
            'area': float(area),
            
            # Normalized coordinates (for research consistency)
            'norm_x1': float(norm_x1), 'norm_y1': float(norm_y1),
            'norm_x2': float(norm_x2), 'norm_y2': float(norm_y2),
            'norm_center_x': float(norm_center_x), 'norm_center_y': float(norm_center_y),
            
            # Shape and position metrics
            'aspect_ratio': float(aspect_ratio),
            'area_percentage': float(area_percentage),
            'distance_from_center': float(distance_from_center),
            'bounding_box_efficiency': float(bounding_box_ratio),
            
            # Research categorizations
            'size_category': self.categorize_detection_size(area_percentage),
            'position_category': self.categorize_position(norm_center_x, norm_center_y),
            
            # Quality metrics
            'detection_quality_score': self.calculate_quality_score(confidence, area_percentage, aspect_ratio)
        }
    
    def categorize_confidence(self, confidence):
        """Categorize confidence levels for research"""
        if confidence >= 0.8:
            return "Very High"
        elif confidence >= 0.6:
            return "High"
        elif confidence >= 0.4:
            return "Medium"
        elif confidence >= 0.25:
            return "Low"
        else:
            return "Very Low"
    
    def categorize_detection_size(self, area_percentage):
        """Categorize detection size relative to image"""
        if area_percentage > 10:
            return "Large"
        elif area_percentage > 5:
            return "Medium"
        elif area_percentage > 1:
            return "Small"
        else:
            return "Very Small"
    
    def categorize_position(self, norm_x, norm_y):
        """Categorize detection position in image"""
        # Define image regions
        if 0.3 <= norm_x <= 0.7 and 0.3 <= norm_y <= 0.7:
            return "Center"
        elif norm_x < 0.3:
            return "Left"
        elif norm_x > 0.7:
            return "Right"
        elif norm_y < 0.3:
            return "Top"
        elif norm_y > 0.7:
            return "Bottom"
        else:
            return "Off-Center"
    
    def calculate_quality_score(self, confidence, area_percentage, aspect_ratio):
        """Calculate overall detection quality score for research"""
        # Weighted quality score
        confidence_score = confidence * 0.5
        size_score = min(1.0, area_percentage / 10) * 0.3  # Optimal around 10%
        aspect_score = min(1.0, 1 / (abs(aspect_ratio - 1.5) + 0.1)) * 0.2  # Prefer ~1.5 ratio
        
        return confidence_score + size_score + aspect_score
    
    def calculate_summary_statistics(self, detections, img_width, img_height):
        """Calculate summary statistics for research analysis"""
        if not detections:
            return {
                'detection_count': 0,
                'avg_confidence': 0,
                'max_confidence': 0,
                'min_confidence': 0,
                'total_detected_area': 0,
                'coverage_percentage': 0
            }
        
        confidences = [d['confidence'] for d in detections]
        areas = [d['area'] for d in detections]
        
        total_image_area = img_width * img_height
        total_detected_area = sum(areas)
        
        return {
            'detection_count': len(detections),
            'avg_confidence': float(np.mean(confidences)),
            'max_confidence': float(np.max(confidences)),
            'min_confidence': float(np.min(confidences)),
            'std_confidence': float(np.std(confidences)),
            'total_detected_area': float(total_detected_area),
            'coverage_percentage': float(total_detected_area / total_image_area * 100),
            'avg_detection_size': float(np.mean(areas)),
            'size_distribution': {
                'large': len([d for d in detections if d['size_category'] == 'Large']),}}