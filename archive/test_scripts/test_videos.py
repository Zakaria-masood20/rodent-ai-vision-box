#!/usr/bin/env python3
"""
Test Script for Rodent Detection System
Tests the detection engine with recorded video files
"""

import cv2
import numpy as np
import time
import json
from pathlib import Path
from datetime import datetime
import sys
import os

sys.path.append(str(Path(__file__).parent))

from src.config_manager import ConfigManager
from src.detection_engine import RodentDetectionEngine
from src.logger import setup_logger

class VideoTester:
    def __init__(self, video_path):
        self.video_path = Path(video_path)
        self.config = ConfigManager()
        self.logger = setup_logger(self.config)
        self.detection_engine = RodentDetectionEngine(self.config)
        
        # Create output directories
        self.output_dir = Path("test_results") / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.frames_dir = self.output_dir / "detection_frames"
        self.frames_dir.mkdir(exist_ok=True)
        
        self.results = {
            "video": str(video_path),
            "test_date": datetime.now().isoformat(),
            "total_frames": 0,
            "frames_with_detections": 0,
            "total_detections": 0,
            "detections_by_class": {},
            "confidence_scores": [],
            "processing_time": 0,
            "fps": 0,
            "detection_details": []
        }
        
    def process_video(self):
        """Process a single video file"""
        if not self.video_path.exists():
            self.logger.error(f"Video file not found: {self.video_path}")
            return None
            
        self.logger.info(f"Processing video: {self.video_path}")
        
        # Open video file
        cap = cv2.VideoCapture(str(self.video_path))
        if not cap.isOpened():
            self.logger.error(f"Failed to open video: {self.video_path}")
            return None
            
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.logger.info(f"Video properties: {width}x{height} @ {fps} fps, {total_frames} frames")
        
        frame_count = 0
        start_time = time.time()
        
        # Process every Nth frame to speed up testing
        frame_skip = max(1, int(fps / 2))  # Process 2 frames per second
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            
            # Skip frames for faster processing
            if frame_count % frame_skip != 0:
                continue
                
            # Run detection
            timestamp = datetime.now()
            detections = self.detection_engine.detect(frame, timestamp)
            
            self.results["total_frames"] += 1
            
            if detections:
                self.results["frames_with_detections"] += 1
                self.results["total_detections"] += len(detections)
                
                # Process each detection
                for detection in detections:
                    # Update class counts
                    class_name = detection.class_name
                    if class_name not in self.results["detections_by_class"]:
                        self.results["detections_by_class"][class_name] = 0
                    self.results["detections_by_class"][class_name] += 1
                    
                    # Store confidence scores
                    self.results["confidence_scores"].append(detection.confidence)
                    
                    # Save detection details
                    detail = {
                        "frame": frame_count,
                        "timestamp": timestamp.isoformat(),
                        "class": class_name,
                        "confidence": detection.confidence,
                        "bbox": detection.bbox
                    }
                    self.results["detection_details"].append(detail)
                
                # Save frame with detections
                output_frame = self.draw_detections(frame.copy(), detections)
                frame_filename = self.frames_dir / f"frame_{frame_count:06d}.jpg"
                cv2.imwrite(str(frame_filename), output_frame)
                
                self.logger.info(f"Frame {frame_count}: {len(detections)} detection(s)")
                for det in detections:
                    self.logger.info(f"  - {det.class_name}: {det.confidence:.2%}")
        
        cap.release()
        
        # Calculate statistics
        end_time = time.time()
        self.results["processing_time"] = end_time - start_time
        self.results["fps"] = self.results["total_frames"] / self.results["processing_time"] if self.results["processing_time"] > 0 else 0
        
        if self.results["confidence_scores"]:
            self.results["avg_confidence"] = np.mean(self.results["confidence_scores"])
            self.results["min_confidence"] = min(self.results["confidence_scores"])
            self.results["max_confidence"] = max(self.results["confidence_scores"])
        
        return self.results
    
    def draw_detections(self, frame, detections):
        """Draw bounding boxes and labels on frame"""
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            
            # Draw bounding box
            color = (0, 255, 0) if detection.confidence > 0.5 else (0, 165, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{detection.class_name}: {detection.confidence:.2%}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            label_y = y1 - 10 if y1 - 10 > 10 else y1 + label_size[1] + 10
            
            cv2.rectangle(frame, (x1, label_y - label_size[1] - 10), 
                         (x1 + label_size[0], label_y), color, -1)
            cv2.putText(frame, label, (x1, label_y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def save_results(self):
        """Save test results to JSON file"""
        results_file = self.output_dir / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.logger.info(f"Results saved to: {results_file}")
        return results_file


def test_all_videos():
    """Test all videos in the Test_videos directory"""
    test_dir = Path("/Users/zakariamasoodgosign/Documents/zakaria/Freelance/RAT_Project/Test_videos")
    
    if not test_dir.exists():
        print(f"Error: Test videos directory not found: {test_dir}")
        return
    
    video_files = list(test_dir.glob("*.mp4"))
    if not video_files:
        print(f"No MP4 files found in {test_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"RODENT DETECTION SYSTEM - VIDEO TEST")
    print(f"{'='*60}")
    print(f"Found {len(video_files)} test videos")
    print(f"Output directory: test_results/")
    print(f"{'='*60}\n")
    
    all_results = {
        "test_session": datetime.now().isoformat(),
        "videos_tested": len(video_files),
        "total_detections": 0,
        "video_results": []
    }
    
    for i, video_file in enumerate(sorted(video_files), 1):
        print(f"\n[{i}/{len(video_files)}] Testing: {video_file.name}")
        print("-" * 40)
        
        tester = VideoTester(video_file)
        results = tester.process_video()
        
        if results:
            tester.save_results()
            all_results["video_results"].append(results)
            all_results["total_detections"] += results["total_detections"]
            
            # Print summary for this video
            print(f"\n✅ Results for {video_file.name}:")
            print(f"   - Frames processed: {results['total_frames']}")
            print(f"   - Frames with detections: {results['frames_with_detections']}")
            print(f"   - Total detections: {results['total_detections']}")
            
            if results['detections_by_class']:
                print(f"   - Detections by class:")
                for class_name, count in results['detections_by_class'].items():
                    print(f"     • {class_name}: {count}")
            
            if results.get('avg_confidence'):
                print(f"   - Average confidence: {results['avg_confidence']:.2%}")
                print(f"   - Confidence range: {results['min_confidence']:.2%} - {results['max_confidence']:.2%}")
            
            print(f"   - Processing speed: {results['fps']:.2f} fps")
        else:
            print(f"❌ Failed to process {video_file.name}")
    
    # Save combined results
    summary_file = Path("test_results") / "test_summary.json"
    summary_file.parent.mkdir(exist_ok=True)
    with open(summary_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Print final summary
    print(f"\n{'='*60}")
    print(f"TEST COMPLETE")
    print(f"{'='*60}")
    print(f"Videos tested: {all_results['videos_tested']}")
    print(f"Total detections: {all_results['total_detections']}")
    print(f"Results saved to: test_results/")
    print(f"Summary file: {summary_file}")
    print(f"{'='*60}\n")
    
    # Generate HTML report
    generate_html_report(all_results)


def generate_html_report(results):
    """Generate an HTML report of the test results"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Rodent Detection Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }}
        .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .video-result {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .success {{ color: #27ae60; font-weight: bold; }}
        .warning {{ color: #f39c12; font-weight: bold; }}
        .error {{ color: #e74c3c; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #34495e; color: white; }}
        .chart {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🐀 Rodent Detection System - Test Report</h1>
        <p>Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Test Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Videos Tested</td>
                <td>{results['videos_tested']}</td>
            </tr>
            <tr>
                <td>Total Detections</td>
                <td class="{'success' if results['total_detections'] > 0 else 'warning'}">{results['total_detections']}</td>
            </tr>
        </table>
    </div>
    
    <div class="summary">
        <h2>🎥 Video Test Results</h2>
"""
    
    for video_result in results['video_results']:
        video_name = Path(video_result['video']).name
        status_class = 'success' if video_result['total_detections'] > 0 else 'warning'
        
        html_content += f"""
        <div class="video-result">
            <h3>{video_name}</h3>
            <table>
                <tr>
                    <td><strong>Frames Processed:</strong></td>
                    <td>{video_result['total_frames']}</td>
                    <td><strong>Processing Speed:</strong></td>
                    <td>{video_result['fps']:.2f} fps</td>
                </tr>
                <tr>
                    <td><strong>Total Detections:</strong></td>
                    <td class="{status_class}">{video_result['total_detections']}</td>
                    <td><strong>Frames with Detections:</strong></td>
                    <td>{video_result['frames_with_detections']}</td>
                </tr>
"""
        
        if video_result.get('avg_confidence'):
            html_content += f"""
                <tr>
                    <td><strong>Avg Confidence:</strong></td>
                    <td>{video_result['avg_confidence']:.2%}</td>
                    <td><strong>Confidence Range:</strong></td>
                    <td>{video_result['min_confidence']:.2%} - {video_result['max_confidence']:.2%}</td>
                </tr>
"""
        
        if video_result['detections_by_class']:
            html_content += """
                <tr>
                    <td colspan="4"><strong>Detections by Class:</strong></td>
                </tr>
"""
            for class_name, count in video_result['detections_by_class'].items():
                html_content += f"""
                <tr>
                    <td colspan="2">• {class_name}</td>
                    <td colspan="2">{count} detections</td>
                </tr>
"""
        
        html_content += """
            </table>
        </div>
"""
    
    html_content += """
    </div>
    
    <div class="summary">
        <h2>✅ Test Status</h2>
        <p>All tests completed successfully. Detection frames saved in test_results directory.</p>
    </div>
</body>
</html>
"""
    
    report_file = Path("test_results") / "test_report.html"
    with open(report_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML report generated: {report_file}")


if __name__ == "__main__":
    test_all_videos()