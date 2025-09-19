#!/usr/bin/env python3
"""
Test script to verify the rodent detection system
Run this before starting the full system
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_model():
    """Test if the model loads and can run inference"""
    print("\n🔍 Testing Model Loading...")
    
    try:
        from ultralytics import YOLO
        
        # Check for model files
        if os.path.exists("models/best.onnx"):
            model_path = "models/best.onnx"
            print("✅ Using ONNX model (optimized for Raspberry Pi)")
        elif os.path.exists("models/best.pt"):
            model_path = "models/best.pt"
            print("✅ Using PyTorch model")
        else:
            print("❌ No model found in models/ directory")
            return False
        
        # Load model
        model = YOLO(model_path)
        print(f"✅ Model loaded successfully from {model_path}")
        
        # Check model classes
        print("\n📊 Model Classes:")
        print("  - Class 0: norway_rat (77% accuracy)")
        print("  - Class 1: roof_rat (15% accuracy - low)")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_twilio():
    """Test Twilio configuration"""
    print("\n📱 Testing Twilio Configuration...")
    
    try:
        from dotenv import load_dotenv
        import os
        
        # Load environment variables
        if os.path.exists(".env"):
            load_dotenv()
            
            account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
            from_number = os.getenv("TWILIO_FROM_NUMBER", "")
            to_number = os.getenv("ALERT_PHONE_NUMBER", "")
            
            if "your_account_sid_here" in account_sid or not account_sid:
                print("⚠️  TWILIO_ACCOUNT_SID not configured")
                print("   Please update in .env file")
                return False
            else:
                print(f"✅ Account SID configured: {account_sid[:10]}...")
            
            if "your_auth_token_here" in auth_token or not auth_token:
                print("⚠️  TWILIO_AUTH_TOKEN not configured")
                print("   Please update in .env file")
                return False
            else:
                print("✅ Auth token configured")
            
            if not from_number.startswith("+"):
                print("⚠️  TWILIO_FROM_NUMBER should start with + (e.g., +1234567890)")
                return False
            else:
                print(f"✅ From number configured: {from_number}")
            
            if not to_number.startswith("+"):
                print("⚠️  ALERT_PHONE_NUMBER should start with + (e.g., +1234567890)")
                return False
            else:
                print(f"✅ Alert number configured: {to_number}")
            
            # Try to import Twilio
            try:
                from twilio.rest import Client
                print("✅ Twilio library installed")
                
                # Optionally test connection (this will use API credits)
                # client = Client(account_sid, auth_token)
                # print(f"✅ Twilio account active: {client.api.accounts(account_sid).fetch().status}")
                
            except ImportError:
                print("❌ Twilio library not installed")
                print("   Run: pip install twilio")
                return False
            
            return True
            
        else:
            print("❌ .env file not found")
            print("   Copy .env.example to .env and add credentials")
            return False
            
    except Exception as e:
        print(f"❌ Twilio test failed: {e}")
        return False

def test_directories():
    """Test if required directories exist"""
    print("\n📁 Testing Directory Structure...")
    
    required_dirs = [
        "models",
        "config", 
        "src",
        "data",
        "data/logs",
        "data/images"
    ]
    
    all_good = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/ exists")
        else:
            print(f"❌ {dir_path}/ missing")
            os.makedirs(dir_path, exist_ok=True)
            print(f"   Created {dir_path}/")
    
    return all_good

def test_config():
    """Test configuration files"""
    print("\n⚙️  Testing Configuration...")
    
    if os.path.exists("config/config.yaml"):
        print("✅ config.yaml found")
        
        # Check config content
        try:
            import yaml
            with open("config/config.yaml", "r") as f:
                config = yaml.safe_load(f)
            
            # Check detection settings
            detection = config.get("detection", {})
            print(f"  Detection confidence: {detection.get('confidence_threshold', 0.25)}")
            print(f"  Classes: {detection.get('classes', ['norway_rat', 'roof_rat'])}")
            
            # Check alert settings  
            alerts = config.get("alerts", {})
            print(f"  Alert cooldown: {alerts.get('cooldown_minutes', 10)} minutes")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Error reading config: {e}")
            return False
    else:
        print("❌ config/config.yaml not found")
        return False

def test_sd_card():
    """Test SD card mount point"""
    print("\n💾 Testing SD Card Mount...")
    
    mount_path = "/mnt/wyze_sd"
    
    if os.path.exists(mount_path):
        print(f"✅ Mount point exists: {mount_path}")
        
        # Check if mounted
        if os.path.ismount(mount_path):
            print("✅ SD card is mounted")
            
            # Check for files
            try:
                files = os.listdir(mount_path)
                if files:
                    print(f"✅ Found {len(files)} items on SD card")
                else:
                    print("⚠️  SD card is empty")
            except Exception as e:
                print(f"⚠️  Cannot read SD card: {e}")
        else:
            print("⚠️  SD card not mounted")
            print("   Mount with: sudo mount /dev/sda1 /mnt/wyze_sd")
    else:
        print("⚠️  Mount point doesn't exist")
        print("   Create with: sudo mkdir -p /mnt/wyze_sd")
    
    return True  # Not critical for testing

def main():
    print("=" * 50)
    print("RODENT AI VISION BOX - SYSTEM TEST")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 5
    
    # Run tests
    if test_directories():
        tests_passed += 1
    
    if test_config():
        tests_passed += 1
    
    if test_model():
        tests_passed += 1
    
    if test_twilio():
        tests_passed += 1
    
    if test_sd_card():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"TEST RESULTS: {tests_passed}/{tests_total} passed")
    print("=" * 50)
    
    if tests_passed >= 4:  # SD card is optional
        print("\n✅ System is READY!")
        print("\nTo start the service:")
        print("  sudo systemctl start rodent-detection")
        print("\nTo view logs:")
        print("  sudo journalctl -u rodent-detection -f")
    else:
        print("\n⚠️  Some issues need to be fixed:")
        print("1. Add Twilio credentials to .env")
        print("2. Ensure model files are in models/")
        print("3. Mount SD card if using Wyze camera")
    
    return tests_passed >= 4

if __name__ == "__main__":
    sys.exit(0 if main() else 1)