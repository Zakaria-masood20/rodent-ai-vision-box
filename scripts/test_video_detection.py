#!/usr/bin/env python3
"""
Video Detection Test Script
Tests the rodent detection system on real CCTV videos
"""

import sys
import os
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_manager import ConfigManager
from src.detection_engine import RodentDetectionEngine
from src.logger import setup_logger


class VideoDetectionTester:
    def __init__(self):
        self.config = ConfigManager()
        self.logger = setup_logger(self.config)
        self.detection_engine = RodentDetectionEngine(self.config)
        
        # Create output directory
        self.output_dir = Path("video_detection_results")
        self.output_dir.mkdir(exist_ok=True)
        
    def process_video(self, video_path, output_name=None):
        """Process a video file and detect rats"""
        video_path = Path(video_path)
        if not video_path.exists():
            self.logger.error(f"Video file not found: {video_path}")
            return False
            
        if not output_name:
            output_name = video_path.stem
            
        self.logger.info(f"Processing video: {video_path.name}")
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            self.logger.error(f"Failed to open video: {video_path}")
            return False
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        self.logger.info(f"Video info: {width}x{height}, {fps}fps, {duration:.1f}s, {total_frames} frames")
        
        # Setup output video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_video_path = self.output_dir / f"{output_name}_detected.mp4"
        out = cv2.VideoWriter(str(output_video_path), fourcc, fps, (width, height))
        
        # Process frames
        frame_count = 0
        detection_count = 0
        detections_log = []
        process_every_n_frames = max(1, fps // 2)  # Process 2 times per second
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            timestamp = frame_count / fps
            
            # Process every N frames for detection
            if frame_count % process_every_n_frames == 0:
                # Run detection
                detections = self.detection_engine.detect(frame, time.time())
                
                if detections:
                    detection_count += len(detections)
                    self.logger.info(f"Frame {frame_count}: Found {len(detections)} rat(s) at {timestamp:.1f}s")
                    
                    # Log detections
                    for detection in detections:
                        detections_log.append({
                            'frame': frame_count,
                            'time': f"{timestamp:.1f}s",
                            'class': detection.class_name,
                            'confidence': f"{detection.confidence:.2f}",
                            'bbox': detection.bbox
                        })
                    
                    # Draw detections on frame
                    frame = self.detection_engine.draw_detections(frame, detections)
                    
                    # Save detection image
                    detection_img_path = self.output_dir / f"{output_name}_detection_{frame_count:06d}.jpg"
                    cv2.imwrite(str(detection_img_path), frame)
            
            # Write frame to output video
            out.write(frame)
            
            # Progress indicator
            if frame_count % (fps * 10) == 0:  # Every 10 seconds
                progress = (frame_count / total_frames) * 100
                self.logger.info(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")
        
        # Cleanup
        cap.release()
        out.release()
        
        # Summary
        self.logger.info(f"Processing complete!")
        self.logger.info(f"Total frames processed: {frame_count}")
        self.logger.info(f"Total detections: {detection_count}")
        self.logger.info(f"Output video: {output_video_path}")
        
        # Save detection log
        if detections_log:
            log_path = self.output_dir / f"{output_name}_detections.log"
            with open(log_path, 'w') as f:
                f.write(f"Video: {video_path.name}\n")
                f.write(f"Total Detections: {detection_count}\n")
                f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 50 + "\n")
                
                for detection in detections_log:
                    f.write(f"Frame {detection['frame']:6d} | ")
                    f.write(f"Time {detection['time']:>8s} | ")
                    f.write(f"{detection['class']} ({detection['confidence']}) | ")
                    f.write(f"BBox: {detection['bbox']}\n")
            
            self.logger.info(f"Detection log saved: {log_path}")
        
        return True
    
    def create_summary_report(self):
        """Create a summary report of all processed videos"""
        report_path = self.output_dir / "detection_summary.md"
        
        with open(report_path, 'w') as f:
            f.write("# Video Detection Test Results\n\n")
            f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # List all processed videos
            video_files = list(self.output_dir.glob("*_detected.mp4"))
            log_files = list(self.output_dir.glob("*_detections.log"))
            image_files = list(self.output_dir.glob("*_detection_*.jpg"))
            
            f.write(f"## Summary\n")
            f.write(f"- **Videos Processed:** {len(video_files)}\n")
            f.write(f"- **Detection Images:** {len(image_files)}\n")
            f.write(f"- **Log Files:** {len(log_files)}\n\n")
            
            f.write("## Results\n\n")
            for log_file in log_files:
                with open(log_file, 'r') as log:
                    lines = log.readlines()
                    if len(lines) >= 2:
                        video_name = lines[0].replace("Video: ", "").strip()
                        total_detections = lines[1].replace("Total Detections: ", "").strip()
                        f.write(f"### {video_name}\n")
                        f.write(f"- **Total Detections:** {total_detections}\n")
                        f.write(f"- **Output Video:** {log_file.stem.replace('_detections', '_detected.mp4')}\n\n")
        
        self.logger.info(f"Summary report created: {report_path}")


def main():
    """Main test function"""
    print("=" * 60)
    print("RODENT DETECTION - VIDEO TEST")
    print("=" * 60)
    
    tester = VideoDetectionTester()
    
    # Find test videos
    test_videos_dir = Path("tests")
    video_files = list(test_videos_dir.glob("*.mp4"))
    
    if not video_files:
        print("No MP4 video files found in tests/ directory")
        return
    
    print(f"Found {len(video_files)} video(s) to process:")
    for video in video_files:
        print(f"  - {video.name} ({video.stat().st_size / 1024 / 1024:.1f} MB)")
    
    print()
    
    # Process each video
    success_count = 0
    for i, video_path in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] Processing: {video_path.name}")
        print("-" * 40)
        
        try:
            success = tester.process_video(video_path)
            if success:
                success_count += 1
                print(f"✅ Successfully processed {video_path.name}")
            else:
                print(f"❌ Failed to process {video_path.name}")
        except Exception as e:
            print(f"❌ Error processing {video_path.name}: {e}")
    
    # Create summary
    tester.create_summary_report()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print(f"Successfully processed: {success_count}/{len(video_files)} videos")
    print(f"Results saved to: video_detection_results/")
    print(f"Check detection_summary.md for complete report")
    
    # Show output directory contents
    output_files = list(Path("video_detection_results").glob("*"))
    if output_files:
        print(f"\nGenerated files:")
        for file in sorted(output_files):
            if file.is_file():
                size = file.stat().st_size
                if size > 1024 * 1024:
                    size_str = f"{size / 1024 / 1024:.1f} MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size} bytes"
                print(f"  - {file.name} ({size_str})")


if __name__ == "__main__":
    main()