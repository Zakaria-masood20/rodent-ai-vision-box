#!/usr/bin/env python3
"""
Corrected Video Testing with Proper Sigmoid Activation
This version correctly processes YOLO output with sigmoid activation
"""

import cv2
import numpy as np
import onnxruntime as ort
import json
from pathlib import Path
from datetime import datetime

def sigmoid(x):
    """Apply sigmoid activation"""
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))  # Clip to prevent overflow

class CorrectedRodentTester:
    def __init__(self):
        self.model_path = Path("models/best.onnx")
        self.test_videos_dir = Path("/Users/zakariamasoodgosign/Documents/zakaria/Freelance/RAT_Project/Test_videos")
        self.output_dir = Path("test_results") / f"corrected_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Detection parameters
        self.conf_threshold = 0.25  # Standard threshold
        self.iou_threshold = 0.45
        
        # Class names
        self.class_names = ['norway_rat', 'roof_rat']
        
        # Load model
        print("Loading ONNX model...")
        self.session = ort.InferenceSession(str(self.model_path))
        self.input_name = self.session.get_inputs()[0].name
        print("✅ Model loaded successfully")
        
    def preprocess_frame(self, frame):
        """Preprocess frame for model"""
        resized = cv2.resize(frame, (640, 640))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0
        transposed = np.transpose(normalized, (2, 0, 1))
        batch = np.expand_dims(transposed, axis=0)
        return batch
    
    def decode_output(self, output, frame_shape):
        """Decode YOLO output with sigmoid activation"""
        # Output shape: [1, 6, 8400]
        output = output[0]  # Shape: [1, 6, 8400]
        
        # Extract components
        coords = output[0, :4, :]  # x, y, w, h (already in pixel coordinates)
        obj_conf_raw = output[0, 4, :]  # objectness (needs sigmoid)
        class_scores_raw = output[0, 5:, :]  # class scores (needs sigmoid)
        
        # Apply sigmoid to confidence scores
        obj_conf = sigmoid(obj_conf_raw)
        
        # For single class output, we might have only one score
        if class_scores_raw.shape[0] == 1:
            # Binary classification: rat or not rat
            class_probs = sigmoid(class_scores_raw[0])
            # Create two-class probabilities
            class_scores = np.stack([1 - class_probs, class_probs])
        else:
            class_scores = sigmoid(class_scores_raw)
        
        # Find valid detections
        valid_indices = np.where(obj_conf > self.conf_threshold)[0]
        
        detections = []
        
        for idx in valid_indices:
            # Get confidence scores
            obj = obj_conf[idx]
            
            # Get class prediction
            if class_scores.shape[0] == 1:
                # Single class
                class_prob = class_scores[0, idx]
                class_id = 0
            else:
                # Multi-class
                class_probs_idx = class_scores[:, idx]
                class_id = np.argmax(class_probs_idx)
                class_prob = class_probs_idx[class_id]
            
            # Combined confidence
            confidence = obj * class_prob
            
            if confidence > self.conf_threshold:
                # Get box coordinates (already in pixel space)
                x_center = coords[0, idx]
                y_center = coords[1, idx]
                width = coords[2, idx]
                height = coords[3, idx]
                
                # Convert to corner format
                x1 = int(x_center - width/2)
                y1 = int(y_center - height/2)
                x2 = int(x_center + width/2)
                y2 = int(y_center + height/2)
                
                # Clamp to image boundaries
                x1 = max(0, min(x1, 640))
                y1 = max(0, min(y1, 640))
                x2 = max(0, min(x2, 640))
                y2 = max(0, min(y2, 640))
                
                # Scale to original frame size
                h_orig, w_orig = frame_shape[:2]
                x1_scaled = int(x1 * w_orig / 640)
                y1_scaled = int(y1 * h_orig / 640)
                x2_scaled = int(x2 * w_orig / 640)
                y2_scaled = int(y2 * h_orig / 640)
                
                if x2_scaled > x1_scaled and y2_scaled > y1_scaled:
                    class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"rodent_{class_id}"
                    
                    detections.append({
                        'class': class_name,
                        'confidence': float(confidence),
                        'obj_conf': float(obj),
                        'class_prob': float(class_prob),
                        'bbox': [x1_scaled, y1_scaled, x2_scaled, y2_scaled]
                    })
        
        # Apply NMS
        if len(detections) > 1:
            detections = self.apply_nms(detections)
        
        return detections
    
    def apply_nms(self, detections):
        """Apply Non-Maximum Suppression"""
        if not detections:
            return detections
        
        # Sort by confidence
        detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        
        keep = []
        while detections:
            current = detections.pop(0)
            keep.append(current)
            
            # Remove overlapping
            detections = [d for d in detections 
                         if self.calculate_iou(current['bbox'], d['bbox']) < self.iou_threshold]
        
        return keep
    
    def calculate_iou(self, box1, box2):
        """Calculate IoU"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        inter_xmin = max(x1_min, x2_min)
        inter_ymin = max(y1_min, y2_min)
        inter_xmax = min(x1_max, x2_max)
        inter_ymax = min(y1_max, y2_max)
        
        if inter_xmax <= inter_xmin or inter_ymax <= inter_ymin:
            return 0.0
        
        inter_area = (inter_xmax - inter_xmin) * (inter_ymax - inter_ymin)
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
    
    def draw_detections(self, frame, detections):
        """Draw detections on frame"""
        annotated = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            
            # Choose color
            if conf > 0.5:
                color = (0, 255, 0)  # Green
            elif conf > 0.3:
                color = (0, 165, 255)  # Orange
            else:
                color = (255, 0, 0)  # Blue
            
            # Draw box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{det['class']}: {conf:.2%}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            cv2.rectangle(annotated,
                         (x1, y1 - label_size[1] - 4),
                         (x1 + label_size[0], y1),
                         color, -1)
            
            cv2.putText(annotated, label,
                       (x1, y1 - 2),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.6, (255, 255, 255), 2)
        
        return annotated
    
    def process_video(self, video_path):
        """Process video file"""
        video_name = video_path.stem
        print(f"\n📹 Processing: {video_path.name}")
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"❌ Failed to open video")
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Process every second
        sample_interval = max(1, int(fps))
        
        results = {
            'video': video_path.name,
            'frames_processed': 0,
            'total_detections': 0,
            'max_confidence': 0,
            'detections': []
        }
        
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % sample_interval == 0:
                # Preprocess
                input_tensor = self.preprocess_frame(frame)
                
                # Inference
                outputs = self.session.run(None, {self.input_name: input_tensor})
                
                # Decode
                detections = self.decode_output(outputs, frame.shape)
                
                results['frames_processed'] += 1
                
                if detections:
                    results['total_detections'] += len(detections)
                    
                    max_conf = max(d['confidence'] for d in detections)
                    if max_conf > results['max_confidence']:
                        results['max_confidence'] = max_conf
                    
                    print(f"   Frame {frame_idx}: {len(detections)} detection(s)")
                    for det in detections:
                        print(f"      • {det['class']}: {det['confidence']:.3f}")
                    
                    # Save frame
                    annotated = self.draw_detections(frame, detections)
                    output_path = self.output_dir / f"{video_name}_frame_{frame_idx:05d}.jpg"
                    cv2.imwrite(str(output_path), annotated)
                    
                    results['detections'].append({
                        'frame': frame_idx,
                        'count': len(detections),
                        'details': detections
                    })
            
            frame_idx += 1
        
        cap.release()
        
        print(f"   ✅ Processed {results['frames_processed']} frames")
        print(f"   • Total detections: {results['total_detections']}")
        
        return results
    
    def test_all_videos(self):
        """Test all videos"""
        video_files = sorted(self.test_videos_dir.glob("*.mp4"))[:2]  # Test first 2 videos for speed
        
        print("\n" + "="*60)
        print("🐀 CORRECTED RODENT DETECTION TEST")
        print("="*60)
        print(f"Testing first 2 videos with sigmoid activation")
        print(f"Threshold: {self.conf_threshold}")
        print("="*60)
        
        all_results = []
        total_detections = 0
        
        for video_file in video_files:
            result = self.process_video(video_file)
            if result:
                all_results.append(result)
                total_detections += result['total_detections']
        
        # Summary
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        
        if total_detections > 0:
            print(f"✅ FOUND {total_detections} RODENT DETECTIONS!")
            for r in all_results:
                if r['total_detections'] > 0:
                    print(f"   • {r['video']}: {r['total_detections']} detections")
        else:
            print("❌ No detections found")
            print("\nThe model may need:")
            print("• Training on similar video footage")
            print("• Different preprocessing approach")
            print("• Lower confidence threshold")
        
        # Save report
        report = {
            'test_date': datetime.now().isoformat(),
            'total_detections': total_detections,
            'video_results': all_results
        }
        
        report_file = self.output_dir / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📁 Results: {self.output_dir}")
        print("="*60)
        
        return total_detections > 0


def main():
    try:
        tester = CorrectedRodentTester()
        success = tester.test_all_videos()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()