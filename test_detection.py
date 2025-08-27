#!/usr/bin/env python3
"""
Script untuk testing dan debugging deteksi hilal
"""
import os
import sys
from pathlib import Path

def check_environment():
    """
    Cek environment dan dependencies
    """
    print("🔍 DEBUGGING HILAL DETECTION")
    print("=" * 50)
    
    print("1. 📁 Checking files...")
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"   Current directory: {current_dir}")
    
    # Check important files
    files_to_check = [
        "app.py",
        "detect.py", 
        "utils.py",
        "best.pt",
        "requirements.txt"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} ({size:,} bytes)")
        else:
            print(f"   ❌ {file} - NOT FOUND")
    
    print("\n2. 🐍 Checking Python packages...")
    
    packages_to_check = [
        "streamlit",
        "ultralytics", 
        "cv2",
        "numpy",
        "pandas",
        "torch"
    ]
    
    for package in packages_to_check:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
    
    print("\n3. 🤖 Testing YOLO...")
    
    try:
        from ultralytics import YOLO
        
        # Try to load model
        if os.path.exists("best.pt"):
            print("   📥 Loading model...")
            model = YOLO("best.pt")
            print("   ✅ Model loaded successfully")
            
            # Get model info
            print(f"   📊 Model info:")
            print(f"       - Task: {getattr(model, 'task', 'unknown')}")
            print(f"       - Classes: {len(getattr(model.model, 'names', {}))}")
            
        else:
            print("   ❌ best.pt not found")
            
    except Exception as e:
        print(f"   ❌ YOLO error: {e}")
    
    print("\n4. 📷 Testing OpenCV...")
    
    try:
        import cv2
        print(f"   ✅ OpenCV version: {cv2.__version__}")
        
        # Test basic operations
        import numpy as np
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        success = cv2.imwrite("test.jpg", test_img)
        
        if success and os.path.exists("test.jpg"):
            print("   ✅ Image write/read test passed")
            os.remove("test.jpg")
        else:
            print("   ❌ Image write/read test failed")
            
    except Exception as e:
        print(f"   ❌ OpenCV error: {e}")

def test_detection():
    """
    Test detection dengan gambar dummy
    """
    print("\n" + "=" * 50)
    print("🧪 TESTING DETECTION")
    print("=" * 50)
    
    try:
        # Create test image
        import cv2
        import numpy as np
        
        # Buat gambar test 640x480 dengan lingkaran (simulasi hilal)
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Background gradient (simulasi langit)
        for y in range(480):
            intensity = int(20 + (y / 480) * 50)
            test_image[y, :] = [intensity, intensity, intensity + 10]
        
        # Gambar crescent moon shape (simulasi hilal)
        center = (320, 240)
        
        # Outer circle
        cv2.circle(test_image, center, 40, (200, 200, 150), -1)
        
        # Inner circle untuk membuat crescent
        cv2.circle(test_image, (center[0] + 15, center[1]), 35, (20, 25, 30), -1)
        
        # Save test image
        test_path = "test_hilal.jpg"
        cv2.imwrite(test_path, test_image)
        print(f"📷 Test image created: {test_path}")
        
        # Import detection function
        from detect import detect_image
        
        print("🔍 Running detection on test image...")
        result_path, csv_path = detect_image(test_path, "best.pt")
        
        if result_path and os.path.exists(result_path):
            print(f"✅ Detection completed!")
            print(f"   📁 Result image: {result_path}")
            print(f"   📄 CSV file: {csv_path}")
            
            # Check if bounding boxes were drawn
            result_img = cv2.imread(result_path)
            original_img = cv2.imread(test_path)
            
            # Compare images to see if annotations were added
            if not np.array_equal(result_img, original_img):
                print("✅ Bounding boxes detected in result image!")
            else:
                print("⚠️ No visual differences - bounding boxes might not be drawn")
                
        else:
            print("❌ Detection failed or no output generated")
        
        # Cleanup
        if os.path.exists(test_path):
            os.remove(test_path)
            
    except Exception as e:
        print(f"❌ Test detection failed: {e}")
        import traceback
        traceback.print_exc()

def check_model_classes():
    """
    Cek classes yang bisa dideteksi oleh model
    """
    print("\n" + "=" * 50)
    print("📋 MODEL CLASS INFORMATION")
    print("=" * 50)
    
    try:
        from ultralytics import YOLO
        
        if os.path.exists("best.pt"):
            model = YOLO("best.pt")
            
            if hasattr(model, 'names'):
                print("🏷️ Model classes:")
                for idx, name in model.names.items():
                    print(f"   {idx}: {name}")
            else:
                print("⚠️ No class names found in model")
                
            if hasattr(model, 'model'):
                print(f"📊 Model architecture: {type(model.model).__name__}")
                
        else:
            print("❌ Model file best.pt not found")
            
    except Exception as e:
        print(f"❌ Error checking model: {e}")

def generate_report():
    """
    Generate debugging report
    """
    print("\n" + "=" * 50)
    print("📋 DEBUGGING REPORT")
    print("=" * 50)
    
    issues = []
    solutions = []
    
    # Check common issues
    if not os.path.exists("best.pt"):
        issues.append("❌ Model file 'best.pt' tidak ditemukan")
        solutions.append("💡 Download model YOLOv5/v8 yang sudah dilatih untuk hilal")
    
    try:
        from ultralytics import YOLO
    except ImportError:
        issues.append("❌ Ultralytics package tidak terinstall")
        solutions.append("💡 Install dengan: pip install ultralytics")
    
    try:
        import cv2
    except ImportError:
        issues.append("❌ OpenCV tidak terinstall")
        solutions.append("💡 Install dengan: pip install opencv-python")
    
    if issues:
        print("🚨 ISSUES DETECTED:")
        for issue in issues:
            print(f"   {issue}")
        
        print("\n🔧 SUGGESTED SOLUTIONS:")
        for solution in solutions:
            print(f"   {solution}")
    else:
        print("✅ No critical issues detected!")
    
    print("\n🎯 TROUBLESHOOTING BOUNDING BOX:")
    print("   1. Pastikan model 'best.pt' ada dan valid")
    print("   2. Cek confidence threshold (default: 0.25)")
    print("   3. Pastikan gambar mengandung objek yang bisa dideteksi")
    print("   4. Periksa logs untuk error messages")
    print("   5. Test dengan gambar yang jelas mengandung hilal")

if __name__ == "__main__":
    print("🌙 HILAL DETECTION DEBUG TOOL")
    print("Developed for troubleshooting bounding box issues\n")
    
    # Run all checks
    check_environment()
    check_model_classes()
    test_detection()
    generate_report()
    
    print("\n" + "=" * 50)
    print("✅ DEBUG COMPLETE")
    print("Check the output above for issues and solutions")
    print("=" * 50)