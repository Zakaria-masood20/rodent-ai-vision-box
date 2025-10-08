#!/usr/bin/env python3
"""
Video Testing Script for Rodent Detection System
Tests detection on pre-recorded video files using ONNX model
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import onnxruntime as ort
import numpy as np

# Try to import OpenCV, fall back to basic testing if not available
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("⚠️  OpenCV not available. Will perform basic testing only.")

class VideoDetectionTester:
    def __init__(self):
        self.model_path = Path("models/best.onnx")
        self.test_videos_path = Path("../Test_videos")
        self.output_dir = Path("test_results") / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Detection settings
        self.conf_threshold = 0.25
        self.iou_threshold = 0.45
        self.class_names = ['norway_rat', 'roof_rat']
        
        # Load ONNX model
        self.session = None
        self.load_model()
        
    def load_model(self):
        """Load the ONNX model"""
        if not self.model_path.exists():
            print(f"❌ Model file not found: {self.model_path}")
            return False
            
        try:
            self.session = ort.InferenceSession(str(self.model_path))
            print(f"✅ Model loaded successfully from {self.model_path}")
            
            # Get model info
            input_info = self.session.get_inputs()[0]
            output_info = self.session.get_outputs()[0]
            
            print(f"   Input shape: {input_info.shape}")
            print(f"   Output shape: {output_info.shape}")
            
            return True
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False
    
    def preprocess_image(self, img):
        """Preprocess image for YOLO model"""
        # Resize to 640x640
        img_resized = cv2.resize(img, (640, 640))
        
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0,1]
        img_normalized = img_rgb.astype(np.float32) / 255.0
        
        # Transpose to CHW format
        img_chw = np.transpose(img_normalized, (2, 0, 1))
        
        # Add batch dimension
        img_batch = np.expand_dims(img_chw, axis=0)
        
        return img_batch
    
    def postprocess_predictions(self, output, img_shape):
        """Process YOLO model output"""
        predictions = output[0][0]  # Remove batch dimension
        
        detections = []
        
        # YOLO output format: [x, y, w, h, obj_conf, class_scores...]
        for i in range(predictions.shape[1]):
            pred = predictions[:, i]
            
            # Get object confidence
            obj_conf = pred[4]
            
            if obj_conf < self.conf_threshold:
                continue
            
            # Get class scores
            class_scores = pred[5:]
            class_id = np.argmax(class_scores)
            class_conf = class_scores[class_id]
            
            # Combined confidence
            confidence = obj_conf * class_conf
            
            if confidence < self.conf_threshold:
                continue
            
            # Get bounding box (convert from center format to corner format)
            cx, cy, w, h = pred[:4]
            x1 = int((cx - w/2) * img_shape[1] / 640)
            y1 = int((cy - h/2) * img_shape[0] / 640)
            x2 = int((cx + w/2) * img_shape[1] / 640)
            y2 = int((cy + h/2) * img_shape[0] / 640)
            
            # Ensure valid bbox
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(img_shape[1], x2)
            y2 = min(img_shape[0], y2)
            
            if class_id < len(self.class_names):
                detection = {
                    'class_id': class_id,
                    'class_name': self.class_names[class_id],
                    'confidence': float(confidence),
                    'bbox': [x1, y1, x2, y2]
                }
                detections.append(detection)
        
        # Apply NMS if needed
        detections = self.apply_nms(detections)
        
        return detections
    
    def apply_nms(self, detections):
        """Apply Non-Maximum Suppression"""
        if len(detections) <= 1:
            return detections
        
        # Sort by confidence
        detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        
        keep = []
        while detections:
            current = detections.pop(0)
            keep.append(current)
            
            # Remove overlapping detections
            detections = [d for d in detections 
                         if self.calculate_iou(current['bbox'], d['bbox']) < self.iou_threshold
                         or current['class_id'] != d['class_id']]
        
        return keep
    
    def calculate_iou(self, box1, box2):
        """Calculate Intersection over Union"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Calculate intersection
        inter_xmin = max(x1_min, x2_min)
        inter_ymin = max(y1_min, y2_min)
        inter_xmax = min(x1_max, x2_max)
        inter_ymax = min(y1_max, y2_max)
        
        if inter_xmax < inter_xmin or inter_ymax < inter_ymin:
            return 0.0
        
        inter_area = (inter_xmax - inter_xmin) * (inter_ymax - inter_ymin)
        
        # Calculate union
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
    
    def process_video(self, video_path):
        """Process a single video file"""
        if not OPENCV_AVAILABLE:
            print(f"⚠️  Cannot process video without OpenCV: {video_path}")
            return None
        
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"❌ Video not found: {video_path}")
            return None
        
        print(f"\n📹 Processing: {video_path.name}")
        print("-" * 40)
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"❌ Failed to open video: {video_path}")
            return None
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"   FPS: {fps:.2f}")
        print(f"   Total frames: {frame_count}")
        
        # Process frames
        results = {
            'video': video_path.name,
            'fps': fps,
            'frame_count': frame_count,
            'detections': [],
            'summary': {
                'total_detections': 0,
                'frames_with_detections': 0,
                'detections_by_class': {}
            }
        }
        
        frame_idx = 0
        frames_to_process = min(100, frame_count)  # Process max 100 frames for testing
        frame_skip = max(1, frame_count // frames_to_process)
        
        print(f"   Processing every {frame_skip} frame(s)...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_skip == 0:
                # Preprocess frame
                input_tensor = self.preprocess_image(frame)
                
                # Run inference
                try:
                    outputs = self.session.run(None, {self.session.get_inputs()[0].name: input_tensor})
                    
                    # Process predictions
                    detections = self.postprocess_predictions(outputs, frame.shape)
                    
                    if detections:
                        results['summary']['frames_with_detections'] += 1
                        results['summary']['total_detections'] += len(detections)
                        
                        for det in detections:
                            class_name = det['class_name']
                            if class_name not in results['summary']['detections_by_class']:
                                results['summary']['detections_by_class'][class_name] = 0
                            results['summary']['detections_by_class'][class_name] += 1
                            
                            # Add frame info
                            det['frame'] = frame_idx
                            det['timestamp'] = frame_idx / fps if fps > 0 else 0
                            results['detections'].append(det)
                            
                            print(f"   Frame {frame_idx}: {class_name} ({det['confidence']:.2%})")
                        
                        # Save annotated frame
                        self.save_detection_frame(frame, detections, video_path.stem, frame_idx)
                    
                except Exception as e:
                    print(f"   ⚠️  Error processing frame {frame_idx}: {e}")
            
            frame_idx += 1
            
            # Show progress
            if frame_idx % 30 == 0:
                progress = (frame_idx / frame_count) * 100
                print(f"   Progress: {progress:.1f}%")
        
        cap.release()
        
        print(f"   ✅ Completed: {results['summary']['total_detections']} detections")
        
        return results
    
    def save_detection_frame(self, frame, detections, video_name, frame_idx):
        """Save frame with detection annotations"""
        annotated = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            color = (0, 255, 0) if det['confidence'] > 0.5 else (0, 165, 255)
            
            # Draw bbox
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det['class_name']}: {det['confidence']:.2%}"
            cv2.putText(annotated, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Save frame
        output_path = self.output_dir / f"{video_name}_frame_{frame_idx:06d}.jpg"
        cv2.imwrite(str(output_path), annotated)
    
    def test_all_videos(self):
        """Test all videos in the Test_videos directory"""
        if not self.session:
            print("❌ Model not loaded. Cannot proceed with testing.")
            return
        
        video_files = list(self.test_videos_path.glob("*.mp4"))
        
        if not video_files:
            print(f"❌ No video files found in {self.test_videos_path}")
            return
        
        print(f"\n{'='*60}")
        print(f"RODENT DETECTION VIDEO TEST")
        print(f"{'='*60}")
        print(f"Videos to test: {len(video_files)}")
        print(f"Model: {self.model_path.name}")
        print(f"Confidence threshold: {self.conf_threshold}")
        print(f"Output directory: {self.output_dir}")
        print(f"{'='*60}")
        
        all_results = []
        
        for video_file in sorted(video_files):
            results = self.process_video(video_file)
            if results:
                all_results.append(results)
        
        # Generate report
        self.generate_report(all_results)
    
    def generate_report(self, all_results):
        """Generate test report"""
        report = {
            'test_date': datetime.now().isoformat(),
            'model': str(self.model_path),
            'confidence_threshold': self.conf_threshold,
            'videos_tested': len(all_results),
            'total_detections': sum(r['summary']['total_detections'] for r in all_results),
            'video_results': all_results
        }
        
        # Save JSON report
        report_file = self.output_dir / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"TEST COMPLETE")
        print(f"{'='*60}")
        print(f"Videos tested: {report['videos_tested']}")
        print(f"Total detections: {report['total_detections']}")
        
        for result in all_results:
            print(f"\n{result['video']}:")
            print(f"  • Detections: {result['summary']['total_detections']}")
            if result['summary']['detections_by_class']:
                for class_name, count in result['summary']['detections_by_class'].items():
                    print(f"    - {class_name}: {count}")
        
        print(f"\n📁 Results saved to: {self.output_dir}")
        print(f"📄 Report: {report_file}")
        print(f"{'='*60}\n")
    
    def test_without_opencv(self):
        """Basic testing without video processing"""
        print("\n⚠️  Running basic test without video processing...")
        
        if not self.session:
            print("❌ Model not loaded.")
            return
        
        # Create dummy image
        dummy_input = np.random.randn(1, 3, 640, 640).astype(np.float32)
        
        try:
            outputs = self.session.run(None, {self.session.get_inputs()[0].name: dummy_input})
            print(f"✅ Model inference successful!")
            print(f"   Output shape: {outputs[0].shape}")
            
            # List video files
            video_files = list(self.test_videos_path.glob("*.mp4"))
            print(f"\n📹 Found {len(video_files)} video files:")
            for vf in sorted(video_files):
                size_mb = vf.stat().st_size / (1024*1024)
                print(f"   • {vf.name}: {size_mb:.2f} MB")
            
            print("\n⚠️  To fully test videos, install OpenCV:")
            print("   pip3 install opencv-python")
            
        except Exception as e:
            print(f"❌ Model inference failed: {e}")


def main():
    """Main function"""
    tester = VideoDetectionTester()
    
    if OPENCV_AVAILABLE:
        tester.test_all_videos()
    else:
        tester.test_without_opencv()
        print("\nInstall dependencies to run full video testing:")
        print("  pip3 install opencv-python numpy")


if __name__ == "__main__":
    main()