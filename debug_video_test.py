#!/usr/bin/env python3
"""
Enhanced Video Testing with Debugging for Rodent Detection
Tests with multiple thresholds to find optimal detection settings
"""

import cv2
import numpy as np
import onnxruntime as ort
import json
from pathlib import Path
from datetime import datetime
import time

class EnhancedRodentTester:
    def __init__(self):
        self.model_path = Path("models/best.onnx")
        self.test_videos_dir = Path("/Users/zakariamasoodgosign/Documents/zakaria/Freelance/RAT_Project/Test_videos")
        self.output_dir = Path("test_results") / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Test multiple thresholds
        self.test_thresholds = [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40]
        self.iou_threshold = 0.45
        
        # Expanded class names - checking all possibilities
        self.class_names = ['norway_rat', 'roof_rat', 'mouse', 'rat', 'rodent']
        
        # Load model
        print("Loading ONNX model...")
        self.session = ort.InferenceSession(str(self.model_path))
        print("✅ Model loaded successfully")
        
        # Get model details
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        self.output_shape = self.session.get_outputs()[0].shape
        
        print(f"   Input: {self.input_name}, Shape: {self.input_shape}")
        print(f"   Output Shape: {self.output_shape}")
        
    def preprocess_frame(self, frame):
        """Prepare frame for YOLO model with multiple preprocessing options"""
        # Original preprocessing
        resized = cv2.resize(frame, (640, 640))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        transposed = np.transpose(rgb, (2, 0, 1))
        return np.expand_dims(transposed, axis=0)
    
    def decode_yolo_output(self, output, threshold=0.25):
        """Decode YOLO output with detailed debugging"""
        # YOLO output format: [batch, 6, 8400] where 6 = [x, y, w, h, obj_conf, class_conf]
        
        predictions = output[0]  # Remove batch dimension, shape: (6, 8400)
        print(f"\n   Raw output shape: {predictions.shape}")
        
        # Transpose to get [8400, 6] format for easier processing
        if predictions.shape[0] == 6 and predictions.shape[1] == 8400:
            predictions = predictions.T  # Now shape: (8400, 6)
            print(f"   Transposed to: {predictions.shape}")
        
        detections = []
        max_scores = []
        
        # Process each prediction
        num_predictions = predictions.shape[0]
        print(f"   Processing {num_predictions} predictions")
        
        for i in range(min(num_predictions, 8400)):  # YOLO typically outputs 8400 predictions
            pred = predictions[i]
            
            # Try different YOLO output formats
            # Format 1: [x, y, w, h, obj_conf, class_scores...]
            if len(pred) >= 5:
                obj_conf = pred[4]
                
                # Collect max scores for debugging
                if len(pred) > 5:
                    class_scores = pred[5:]
                    max_class_score = np.max(class_scores)
                    max_scores.append(obj_conf * max_class_score)
                else:
                    max_scores.append(obj_conf)
                
                if obj_conf >= threshold:
                    if len(pred) > 5:
                        class_scores = pred[5:]
                        class_id = np.argmax(class_scores)
                        confidence = obj_conf * class_scores[class_id]
                    else:
                        class_id = 0
                        confidence = obj_conf
                    
                    if confidence >= threshold:
                        cx, cy, w, h = pred[:4]
                        
                        # Convert to absolute coordinates
                        x1 = int((cx - w/2) * 640)
                        y1 = int((cy - h/2) * 640)
                        x2 = int((cx + w/2) * 640)
                        y2 = int((cy + h/2) * 640)
                        
                        # Ensure valid bbox
                        x1 = max(0, min(x1, 640))
                        y1 = max(0, min(y1, 640))
                        x2 = max(0, min(x2, 640))
                        y2 = max(0, min(y2, 640))
                        
                        if x2 > x1 and y2 > y1:
                            class_name = f"class_{class_id}" if class_id >= len(self.class_names) else self.class_names[class_id]
                            detections.append({
                                'class': class_name,
                                'class_id': int(class_id),
                                'confidence': float(confidence),
                                'bbox': [x1, y1, x2, y2],
                                'obj_conf': float(obj_conf)
                            })
        
        # Debug info
        if max_scores:
            top_scores = sorted(max_scores, reverse=True)[:10]
            print(f"   Top 10 scores: {[f'{float(s):.3f}' for s in top_scores]}")
            print(f"   Max score: {float(max(max_scores)):.4f}")
            print(f"   Scores > {threshold}: {sum(1 for s in max_scores if s > threshold)}")
        
        return detections
    
    def test_single_frame(self, frame, frame_idx, video_name):
        """Test a single frame with multiple thresholds"""
        # Preprocess frame
        input_tensor = self.preprocess_frame(frame)
        
        # Run inference
        outputs = self.session.run(None, {self.input_name: input_tensor})
        
        # Test with different thresholds
        results_by_threshold = {}
        
        for threshold in self.test_thresholds:
            detections = self.decode_yolo_output(outputs, threshold)
            if detections:
                results_by_threshold[threshold] = detections
                print(f"\n   🎯 Threshold {threshold:.2f}: {len(detections)} detection(s)")
                for det in detections[:3]:  # Show first 3
                    print(f"      • {det['class']} (conf: {det['confidence']:.3f}, obj: {det['obj_conf']:.3f})")
        
        # Save frame with best detections (lowest threshold with detections)
        if results_by_threshold:
            best_threshold = min(results_by_threshold.keys())
            best_detections = results_by_threshold[best_threshold]
            
            # Draw and save annotated frame
            annotated = self.draw_detections(frame, best_detections, best_threshold)
            output_path = self.output_dir / f"{video_name}_frame_{frame_idx:05d}_thresh_{best_threshold:.2f}.jpg"
            cv2.imwrite(str(output_path), annotated)
            
            return best_detections, best_threshold
        
        return None, None
    
    def draw_detections(self, frame, detections, threshold):
        """Draw bounding boxes with detailed labels"""
        annotated = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            
            # Scale coordinates back to original frame size
            h, w = frame.shape[:2]
            x1 = int(x1 * w / 640)
            y1 = int(y1 * h / 640)
            x2 = int(x2 * w / 640)
            y2 = int(y2 * h / 640)
            
            # Color based on confidence
            conf = det['confidence']
            if conf > 0.5:
                color = (0, 255, 0)  # Green
            elif conf > 0.25:
                color = (0, 165, 255)  # Orange
            else:
                color = (0, 0, 255)  # Red
            
            # Draw box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Detailed label
            label = f"{det['class']}:{det['confidence']:.2f} (obj:{det['obj_conf']:.2f})"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            
            # Draw label background
            cv2.rectangle(annotated, 
                         (x1, y1 - label_size[1] - 4),
                         (x1 + label_size[0], y1),
                         color, -1)
            
            # Draw label text
            cv2.putText(annotated, label,
                       (x1, y1 - 2),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (255, 255, 255), 1)
        
        # Add threshold info
        info_text = f"Threshold: {threshold:.2f}"
        cv2.putText(annotated, info_text,
                   (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, (255, 255, 255), 2)
        
        return annotated
    
    def analyze_video(self, video_path):
        """Analyze video with enhanced debugging"""
        video_name = video_path.stem
        print(f"\n{'='*60}")
        print(f"📹 Analyzing: {video_path.name}")
        print(f"{'='*60}")
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"❌ Failed to open video")
            return None
        
        # Video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Resolution: {width}x{height}, FPS: {fps:.1f}, Frames: {total_frames}")
        
        # Sample frames to test
        frames_to_test = min(20, total_frames)  # Test up to 20 frames
        frame_interval = max(1, total_frames // frames_to_test)
        
        results = {
            'video': video_path.name,
            'resolution': f"{width}x{height}",
            'total_frames': total_frames,
            'frames_tested': 0,
            'detections_by_threshold': {t: 0 for t in self.test_thresholds},
            'best_threshold': None,
            'max_confidence_found': 0,
            'detection_frames': []
        }
        
        frame_idx = 0
        tested_count = 0
        
        print(f"\nTesting frames (every {frame_interval} frames)...")
        
        while cap.isOpened() and tested_count < frames_to_test:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_interval == 0:
                print(f"\n📍 Frame {frame_idx}/{total_frames}:")
                
                detections, threshold = self.test_single_frame(frame, frame_idx, video_name)
                
                if detections:
                    results['frames_tested'] += 1
                    
                    # Update statistics
                    for t in self.test_thresholds:
                        if t >= threshold:
                            results['detections_by_threshold'][t] += len(detections)
                    
                    # Track max confidence
                    max_conf = max(d['confidence'] for d in detections)
                    if max_conf > results['max_confidence_found']:
                        results['max_confidence_found'] = max_conf
                        results['best_threshold'] = threshold
                    
                    # Store detection info
                    results['detection_frames'].append({
                        'frame': frame_idx,
                        'timestamp': frame_idx / fps if fps > 0 else 0,
                        'threshold': threshold,
                        'detections': detections
                    })
                else:
                    print("   No detections at any threshold")
                
                tested_count += 1
            
            frame_idx += 1
        
        cap.release()
        
        # Summary
        print(f"\n{'='*60}")
        print(f"RESULTS for {video_path.name}:")
        print(f"{'='*60}")
        print(f"Frames tested: {tested_count}")
        print(f"Max confidence found: {results['max_confidence_found']:.3f}")
        
        if results['detection_frames']:
            print(f"✅ DETECTIONS FOUND!")
            print(f"Best threshold: {results['best_threshold']}")
            print(f"\nDetections by threshold:")
            for t in self.test_thresholds:
                count = results['detections_by_threshold'][t]
                if count > 0:
                    print(f"  • {t:.2f}: {count} detections")
        else:
            print("❌ No detections found at any threshold")
        
        return results
    
    def run_debug_test(self):
        """Run comprehensive debug test on all videos"""
        video_files = sorted(self.test_videos_dir.glob("*.mp4"))
        
        print("\n" + "="*60)
        print("🔍 ENHANCED RODENT DETECTION DEBUG TEST")
        print("="*60)
        print(f"Videos to test: {len(video_files)}")
        print(f"Testing thresholds: {self.test_thresholds}")
        print(f"Output: {self.output_dir}")
        print("="*60)
        
        all_results = []
        
        for video_file in video_files:
            result = self.analyze_video(video_file)
            if result:
                all_results.append(result)
        
        # Generate comprehensive report
        self.generate_debug_report(all_results)
        
        return all_results
    
    def generate_debug_report(self, results):
        """Generate detailed debug report"""
        report = {
            'test_date': datetime.now().isoformat(),
            'model': str(self.model_path),
            'thresholds_tested': self.test_thresholds,
            'video_results': results
        }
        
        # Save JSON
        json_file = self.output_dir / "debug_report.json"
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print final summary
        print("\n" + "="*60)
        print("🎯 DEBUG TEST COMPLETE")
        print("="*60)
        
        total_detections = sum(
            len(r['detection_frames']) for r in results
        )
        
        if total_detections > 0:
            print(f"✅ DETECTIONS FOUND: {total_detections} frames with rodents")
            
            # Find optimal threshold
            threshold_totals = {}
            for r in results:
                for t, count in r['detections_by_threshold'].items():
                    if t not in threshold_totals:
                        threshold_totals[t] = 0
                    threshold_totals[t] += count
            
            print(f"\n📊 Detection counts by threshold:")
            for t in sorted(threshold_totals.keys()):
                if threshold_totals[t] > 0:
                    print(f"   {t:.2f}: {threshold_totals[t]} total detections")
            
            # Recommend optimal threshold
            optimal = max((t for t in threshold_totals if threshold_totals[t] > 0), 
                         key=lambda t: threshold_totals[t])
            print(f"\n💡 RECOMMENDED THRESHOLD: {optimal}")
            print(f"   This threshold gives the most detections")
            
        else:
            print("❌ No detections found even at lowest threshold (0.01)")
            print("\nPossible issues:")
            print("1. Model may not be trained on this type of footage")
            print("2. Video quality/angle may be different from training data")
            print("3. Model file might be incorrect")
        
        print(f"\n📁 Debug output saved to:")
        print(f"   • Report: {json_file}")
        print(f"   • Annotated frames: {self.output_dir}/*.jpg")
        print("="*60)


def main():
    try:
        tester = EnhancedRodentTester()
        tester.run_debug_test()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()