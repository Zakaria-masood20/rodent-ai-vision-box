#!/usr/bin/env python3
"""
Test Rodent Detection with Email Notification
This script tests the full pipeline: detection + email alert
"""

import os
import sys
import cv2
import numpy as np
import onnxruntime as ort
import requests
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import time
import base64

# Load production environment
load_dotenv('.env.production')

class RodentDetectionWithEmail:
    def __init__(self):
        # EmailJS configuration
        self.emailjs_service_id = os.getenv('EMAILJS_SERVICE_ID', 'service_2q7m7pm')
        self.emailjs_template_id = os.getenv('EMAILJS_TEMPLATE_ID', 'template_0q4z7y8')
        self.emailjs_public_key = os.getenv('EMAILJS_PUBLIC_KEY', 'Cx4zjcLaDjfhS2ssD')
        self.emailjs_to_email = os.getenv('EMAILJS_TO_EMAIL', 'ratproject111@gmail.com')
        
        # Model setup
        self.model_path = Path("models/best.onnx")
        self.conf_threshold = 0.35  # Higher threshold to reduce false positives
        
        # Load model
        print("Loading ONNX model...")
        self.session = ort.InferenceSession(str(self.model_path))
        self.input_name = self.session.get_inputs()[0].name
        print("✅ Model loaded")
        
        # Email sending cooldown (prevent spam)
        self.last_email_time = 0
        self.email_cooldown = 60  # 1 minute between emails
        
    def sigmoid(self, x):
        """Apply sigmoid activation"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def preprocess_frame(self, frame):
        """Preprocess frame for model"""
        resized = cv2.resize(frame, (640, 640))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0
        transposed = np.transpose(normalized, (2, 0, 1))
        batch = np.expand_dims(transposed, axis=0)
        return batch
    
    def detect_rodents(self, frame):
        """Run detection on frame"""
        # Preprocess
        input_tensor = self.preprocess_frame(frame)
        
        # Run inference
        outputs = self.session.run(None, {self.input_name: input_tensor})
        
        # Decode output
        output = outputs[0]
        
        # Extract components and apply sigmoid
        obj_conf = self.sigmoid(output[0, 4, :])
        
        # Find high confidence detections
        valid_indices = np.where(obj_conf > self.conf_threshold)[0]
        
        if len(valid_indices) > 0:
            # We have detections!
            max_conf = np.max(obj_conf[valid_indices])
            num_detections = len(valid_indices)
            return True, num_detections, float(max_conf)
        
        return False, 0, 0.0
    
    def send_email_alert(self, num_detections, confidence, image_path=None):
        """Send email alert using EmailJS"""
        
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_email_time < self.email_cooldown:
            print(f"⏳ Email cooldown active. Wait {self.email_cooldown - (current_time - self.last_email_time):.0f}s")
            return False
        
        print("\n📧 Sending email alert...")
        
        # Prepare email data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        template_params = {
            "to_email": self.emailjs_to_email,
            "detection_time": timestamp,
            "rodent_type": "Roof Rat",
            "confidence": f"{confidence:.1%}",
            "num_detections": str(num_detections),
            "location": "Test Video",
            "message": f"🐀 ALERT: {num_detections} rodent(s) detected at {timestamp}",
            "subject": f"🚨 Rodent Detection Alert - {timestamp}"
        }
        
        # If we have an image, encode it
        if image_path and Path(image_path).exists():
            try:
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                    # EmailJS has size limits, so we'll just mention image was captured
                    template_params["image_captured"] = "Yes - View in system logs"
            except:
                template_params["image_captured"] = "Failed to capture"
        else:
            template_params["image_captured"] = "No image available"
        
        # Send via EmailJS API
        url = "https://api.emailjs.com/api/v1.0/email/send"
        
        data = {
            "service_id": self.emailjs_service_id,
            "template_id": self.emailjs_template_id,
            "user_id": self.emailjs_public_key,
            "template_params": template_params
        }
        
        try:
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                print(f"✅ Email sent successfully to {self.emailjs_to_email}")
                print(f"   Subject: {template_params['subject']}")
                print(f"   Detections: {num_detections}")
                print(f"   Confidence: {confidence:.1%}")
                self.last_email_time = current_time
                return True
            else:
                print(f"❌ Email failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
    
    def test_with_video(self, video_path):
        """Test detection and email with video"""
        print(f"\n📹 Testing with video: {video_path}")
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print("❌ Failed to open video")
            return
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"   Total frames: {total_frames}")
        print(f"   Testing first few frames for detections...")
        
        frame_idx = 0
        email_sent = False
        
        # Test first 10 frames
        while frame_idx < min(10, total_frames) and not email_sent:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run detection
            detected, num_detections, confidence = self.detect_rodents(frame)
            
            if detected:
                print(f"\n🎯 Frame {frame_idx}: RODENT DETECTED!")
                print(f"   Detections: {num_detections}")
                print(f"   Max confidence: {confidence:.1%}")
                
                # Save detection frame
                output_dir = Path("test_results")
                output_dir.mkdir(exist_ok=True)
                image_path = output_dir / f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(str(image_path), frame)
                print(f"   Image saved: {image_path}")
                
                # Send email alert
                if self.send_email_alert(num_detections, confidence, image_path):
                    email_sent = True
                    print("\n✅ Email notification sent! Check ratproject111@gmail.com")
                    break
            else:
                print(f"   Frame {frame_idx}: No detection")
            
            frame_idx += 1
        
        cap.release()
        
        if not email_sent:
            print("\n⚠️  No detections found in first 10 frames")
            print("   Trying with lower threshold...")
            
            # Try once more with very low threshold
            self.conf_threshold = 0.1
            print(f"   Lowered threshold to {self.conf_threshold}")
            
            # Reopen video
            cap = cv2.VideoCapture(str(video_path))
            ret, frame = cap.read()
            if ret:
                detected, num_detections, confidence = self.detect_rodents(frame)
                if detected:
                    print(f"\n🎯 RODENT DETECTED with lower threshold!")
                    self.send_email_alert(num_detections, confidence)
            cap.release()
    
    def test_with_dummy_detection(self):
        """Force a test email with dummy detection data"""
        print("\n🧪 Testing email system with dummy detection...")
        
        # Create a dummy detection
        num_detections = 1
        confidence = 0.85
        
        # Send test email
        if self.send_email_alert(num_detections, confidence):
            print("\n✅ Test email sent successfully!")
            print("   Check inbox: ratproject111@gmail.com")
            return True
        else:
            print("\n❌ Test email failed")
            return False


def main():
    print("="*60)
    print("🐀 RODENT DETECTION WITH EMAIL NOTIFICATION TEST")
    print("="*60)
    print("This test will:")
    print("1. Run rodent detection on your video")
    print("2. Send email alert if rodents are detected")
    print("3. Email will go to: ratproject111@gmail.com")
    print("="*60)
    
    tester = RodentDetectionWithEmail()
    
    # Test with actual video
    video_path = Path("/Users/zakariamasoodgosign/Documents/zakaria/Freelance/RAT_Project/Test_videos/T1.mp4")
    
    if video_path.exists():
        print(f"\n✅ Found test video: {video_path.name}")
        tester.test_with_video(video_path)
    else:
        print(f"\n⚠️  Video not found: {video_path}")
        print("   Running dummy detection test instead...")
        tester.test_with_dummy_detection()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\n📧 IMPORTANT:")
    print("   • Check ratproject111@gmail.com for alert email")
    print("   • Email subject: 'Rodent Detection Alert'")
    print("   • May take 1-2 minutes to arrive")
    print("   • Check spam folder if not in inbox")
    print("="*60)


if __name__ == "__main__":
    main()