#!/usr/bin/env python3
"""
Real Detection Email Test - Sends actual alerts when rodents are detected
This integrates the working detection with the working email system
"""

import cv2
import numpy as np
import onnxruntime as ort
import requests
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import time

# Load production credentials
load_dotenv('.env.production')

def sigmoid(x):
    """Apply sigmoid activation"""
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

class RealDetectionEmailer:
    def __init__(self):
        # EmailJS configuration (from working test)
        self.service_id = os.getenv('EMAILJS_SERVICE_ID', 'service_2q7m7pm')
        self.template_id = os.getenv('EMAILJS_TEMPLATE_ID', 'template_0q4z7y8')
        self.public_key = os.getenv('EMAILJS_PUBLIC_KEY', 'Cx4zjcLaDjfhS2ssD')
        self.private_key = os.getenv('EMAILJS_PRIVATE_KEY', 'h1bojFisOSGIE9IIF9yhP')
        self.to_email = os.getenv('EMAILJS_TO_EMAIL', 'ratproject111@gmail.com')
        
        # Load model
        self.model_path = Path("models/best.onnx")
        print("Loading detection model...")
        self.session = ort.InferenceSession(str(self.model_path))
        self.input_name = self.session.get_inputs()[0].name
        print("✅ Model loaded")
        
        # Detection settings (tuned for better accuracy)
        self.conf_threshold = 0.45  # Higher threshold to reduce false positives
        self.detections_sent = []  # Track what we've already alerted about
        
    def preprocess_frame(self, frame):
        """Prepare frame for detection"""
        resized = cv2.resize(frame, (640, 640))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0
        transposed = np.transpose(normalized, (2, 0, 1))
        return np.expand_dims(transposed, axis=0)
    
    def detect_rodents_in_frame(self, frame):
        """Run actual detection on a frame"""
        # Preprocess
        input_tensor = self.preprocess_frame(frame)
        
        # Run model
        outputs = self.session.run(None, {self.input_name: input_tensor})
        output = outputs[0]
        
        # Apply sigmoid to get probabilities
        obj_conf = sigmoid(output[0, 4, :])
        
        # Count high-confidence detections
        high_conf_indices = np.where(obj_conf > self.conf_threshold)[0]
        
        if len(high_conf_indices) > 0:
            # Get the highest confidence detection
            max_idx = np.argmax(obj_conf)
            max_conf = float(obj_conf[max_idx])
            
            # Determine rodent type based on class scores
            if output.shape[1] > 5:
                class_scores = sigmoid(output[0, 5:, max_idx])
                if len(class_scores) > 0:
                    rodent_type = "Roof Rat" if class_scores[0] > 0.5 else "Norway Rat"
                else:
                    rodent_type = "Rodent"
            else:
                rodent_type = "Rodent"
            
            # Get location of detection (for reporting)
            x_center = output[0, 0, max_idx]
            y_center = output[0, 1, max_idx]
            
            # Map to frame quadrant
            if x_center < 320:
                location = "left side"
            else:
                location = "right side"
            
            if y_center < 320:
                location = "upper " + location
            else:
                location = "lower " + location
            
            return {
                'detected': True,
                'confidence': max_conf,
                'count': min(len(high_conf_indices), 10),  # Cap at 10 to avoid spam
                'rodent_type': rodent_type,
                'location': location
            }
        
        return {'detected': False}
    
    def send_real_detection_email(self, detection_info, video_name, frame_number):
        """Send email about REAL detection, not test"""
        
        # Prepare real detection data
        timestamp = datetime.now()
        
        template_params = {
            'to_email': self.to_email,
            'from_name': 'Rodent AI Detection System',
            'rodent_type': detection_info['rodent_type'],
            'detection_time': timestamp.strftime('%Y-%m-%d %I:%M:%S %p'),
            'confidence': f"{detection_info['confidence']:.1%}",
            'message': f"🚨 REAL DETECTION: {detection_info['count']} {detection_info['rodent_type']}(s) detected in {video_name} at frame {frame_number}. Location: {detection_info['location']}. This is an actual rodent detection from your video footage, not a test.",
            'image_data': '',
            'image_name': f'{video_name}_frame_{frame_number}.jpg'
        }
        
        # Use working EmailJS configuration
        headers = {
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:3000',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        data = {
            'service_id': self.service_id,
            'template_id': self.template_id,
            'user_id': self.public_key,
            'template_params': template_params,
            'accessToken': self.private_key  # This is crucial
        }
        
        print(f"\n📧 Sending REAL detection alert...")
        print(f"   Video: {video_name}")
        print(f"   Frame: {frame_number}")
        print(f"   Type: {detection_info['rodent_type']}")
        print(f"   Confidence: {detection_info['confidence']:.1%}")
        print(f"   Location: {detection_info['location']}")
        
        try:
            response = requests.post(
                'https://api.emailjs.com/api/v1.0/email/send',
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                print(f"✅ Real detection email sent to {self.to_email}!")
                return True
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def process_video_with_alerts(self, video_path):
        """Process video and send real alerts for detections"""
        video_name = video_path.stem
        
        print(f"\n🎥 Processing: {video_name}")
        print("   Looking for real rodents...")
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print("❌ Cannot open video")
            return
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Process strategically - check every second
        check_interval = max(1, int(fps))
        
        frame_idx = 0
        alerts_sent = 0
        max_alerts = 3  # Limit to 3 alerts per video to avoid spam
        last_alert_frame = -100  # Ensure spacing between alerts
        
        print(f"   Analyzing {total_frames} frames...")
        
        while cap.isOpened() and alerts_sent < max_alerts:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Check this frame if it's time
            if frame_idx % check_interval == 0 and (frame_idx - last_alert_frame) > 30:
                # Run real detection
                detection = self.detect_rodents_in_frame(frame)
                
                if detection['detected']:
                    print(f"\n🎯 REAL RODENT DETECTED at frame {frame_idx}!")
                    
                    # Save detection image
                    output_dir = Path("test_results/real_detections")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    image_file = output_dir / f"{video_name}_frame_{frame_idx}.jpg"
                    cv2.imwrite(str(image_file), frame)
                    
                    # Send real alert email
                    if self.send_real_detection_email(detection, video_name, frame_idx):
                        alerts_sent += 1
                        last_alert_frame = frame_idx
                        print(f"   Alert #{alerts_sent} sent successfully")
                        
                        # Wait a bit before next alert
                        if alerts_sent < max_alerts:
                            print("   Continuing scan...")
                            time.sleep(2)
            
            frame_idx += 1
            
            # Progress indicator
            if frame_idx % 100 == 0:
                progress = (frame_idx / total_frames) * 100
                print(f"   Progress: {progress:.0f}%", end='\r')
        
        cap.release()
        
        print(f"\n   ✅ Completed: {alerts_sent} detection alert(s) sent")
        
        return alerts_sent
    
    def test_all_videos(self):
        """Test all videos and send real alerts"""
        video_dir = Path("/Users/zakariamasoodgosign/Documents/zakaria/Freelance/RAT_Project/Test_videos")
        video_files = sorted(video_dir.glob("*.mp4"))[:3]  # Test first 3 videos
        
        print("\n" + "="*60)
        print("🐀 REAL RODENT DETECTION WITH EMAIL ALERTS")
        print("="*60)
        print(f"Testing {len(video_files)} videos for actual rodents")
        print(f"Email alerts will be sent to: {self.to_email}")
        print(f"Detection threshold: {self.conf_threshold:.0%}")
        print("="*60)
        
        total_alerts = 0
        
        for i, video_file in enumerate(video_files, 1):
            print(f"\n[Video {i}/{len(video_files)}]")
            alerts = self.process_video_with_alerts(video_file)
            total_alerts += alerts
            
            if alerts > 0:
                print(f"   📧 {alerts} email(s) sent for this video")
        
        print("\n" + "="*60)
        print("DETECTION COMPLETE")
        print("="*60)
        
        if total_alerts > 0:
            print(f"✅ SUCCESS! Sent {total_alerts} real detection alerts!")
            print(f"\n📧 CHECK YOUR EMAIL:")
            print(f"   • Inbox: {self.to_email}")
            print(f"   • Subject: 'Rodent Detection Alert'")
            print(f"   • These are REAL detections from your videos")
            print(f"   • Not test messages!")
        else:
            print("❌ No high-confidence rodent detections found")
            print("   The threshold may be too high for these videos")
        
        print("\n💾 Detection images saved in: test_results/real_detections/")
        print("="*60)


def main():
    print("🚀 Starting Real Rodent Detection Email Test")
    print("This will analyze your videos and send REAL alerts")
    print("Not test messages - actual detection results!")
    
    try:
        detector = RealDetectionEmailer()
        detector.test_all_videos()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test complete. Check your email for real detection alerts!")


if __name__ == "__main__":
    main()