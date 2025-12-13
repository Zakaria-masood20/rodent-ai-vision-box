"""Quick test script to check if the ONNX model can detect rodents in test video."""
import cv2
from pathlib import Path
from ultralytics import YOLO

# Load the ONNX model
print("Loading ONNX model...")
model = YOLO("models/best.onnx", task='detect')

# Open test video
video_path = "/Users/zakariamasoodgosign/Documents/zakaria/Freelance/RAT_Project/Test_videos/T1.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"ERROR: Could not open video: {video_path}")
    exit(1)

print(f"Video opened: {video_path}")
print(f"Total frames: {int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}")
print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
print()

# Process every 10th frame with very low threshold
frame_count = 0
detection_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_count += 1
    
    # Only process every 10th frame
    if frame_count % 10 != 0:
        continue
    
    # Run detection with very low confidence threshold
    results = model(frame, conf=0.05, verbose=False)  # 5% threshold to see ANY detection
    
    for result in results:
        if result.boxes is not None and len(result.boxes) > 0:
            detection_count += 1
            print(f"\n=== DETECTION at frame {frame_count} ===")
            for box in result.boxes:
                class_id = int(box.cls)
                confidence = float(box.conf)
                class_name = model.names.get(class_id, f"class_{class_id}")
                print(f"  Class: {class_name} (ID: {class_id})")
                print(f"  Confidence: {confidence:.2%}")
                print(f"  BBox: {box.xyxy[0].cpu().numpy()}")
    
    if frame_count % 100 == 0:
        print(f"Processed {frame_count} frames, {detection_count} detections so far...")

cap.release()

print()
print("=" * 50)
print(f"SUMMARY: Processed {frame_count} frames")
print(f"Total detections found: {detection_count}")

# Also print model info
print()
print("MODEL INFO:")
print(f"  Model names: {model.names}")
