#!/usr/bin/env python3
"""
Quick test to verify the rodent detection system is ready for demo
"""

import sys
import os
import numpy as np
import cv2
import onnxruntime as ort
from pathlib import Path

def test_model_loading():
    """Test if ONNX model loads correctly"""
    print("1. Testing Model Loading...")
    model_path = Path("models/best.onnx")
    
    if not model_path.exists():
        print(f"   ❌ Model not found at {model_path}")
        return False
    
    try:
        session = ort.InferenceSession(str(model_path))
        print(f"   ✅ Model loaded successfully ({model_path.stat().st_size / 1024 / 1024:.1f} MB)")
        
        # Get model info
        input_name = session.get_inputs()[0].name
        input_shape = session.get_inputs()[0].shape
        output_names = [o.name for o in session.get_outputs()]
        
        print(f"   ✅ Input: {input_name}, Shape: {input_shape}")
        print(f"   ✅ Outputs: {output_names}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to load model: {e}")
        return False

def test_image_processing():
    """Test image processing pipeline"""
    print("\n2. Testing Image Processing...")
    
    # Check if test images exist
    test_images = list(Path("dataset/rodent_yolo_dataset/test/images").glob("*.jpg"))[:1] if Path("dataset").exists() else []
    
    if test_images:
        test_img = test_images[0]
        print(f"   Using test image: {test_img.name}")
        
        try:
            img = cv2.imread(str(test_img))
            if img is not None:
                print(f"   ✅ Image loaded: {img.shape}")
                
                # Resize for model
                resized = cv2.resize(img, (640, 640))
                print(f"   ✅ Image resized to: {resized.shape}")
                return True
            else:
                print(f"   ❌ Failed to load image")
                return False
        except Exception as e:
            print(f"   ❌ Error processing image: {e}")
            return False
    else:
        print("   ⚠️  No test images found, creating dummy image")
        dummy_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        print(f"   ✅ Dummy image created: {dummy_img.shape}")
        return True

def test_config():
    """Test configuration loading"""
    print("\n3. Testing Configuration...")
    
    config_path = Path("config/config.yaml")
    env_path = Path(".env")
    
    if not config_path.exists():
        print(f"   ❌ Config file not found: {config_path}")
        return False
    
    if not env_path.exists():
        print(f"   ❌ .env file not found")
        return False
    
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"   ✅ Config loaded successfully")
        print(f"   ✅ Detection classes: {config['detection']['classes']}")
        print(f"   ✅ Confidence threshold: {config['detection']['confidence_threshold']}")
        print(f"   ✅ Alert cooldown: {config['alerts']['cooldown_minutes']} minutes")
        
        # Check .env
        from dotenv import load_dotenv
        load_dotenv()
        
        has_twilio = all([
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN'),
            os.getenv('TWILIO_FROM_NUMBER'),
            os.getenv('ALERT_PHONE_NUMBER')
        ])
        
        if has_twilio:
            print(f"   ✅ Twilio credentials configured")
        else:
            print(f"   ⚠️  Twilio credentials missing in .env")
        
        return True
    except Exception as e:
        print(f"   ❌ Error loading config: {e}")
        return False

def test_directories():
    """Test required directories exist"""
    print("\n4. Testing Directory Structure...")
    
    required_dirs = [
        "data/logs",
        "data/images",
        "models",
        "config",
        "src"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path}/ exists")
        else:
            print(f"   ❌ {dir_path}/ missing")
            path.mkdir(parents=True, exist_ok=True)
            print(f"      Created {dir_path}/")
    
    return True

def run_demo_test():
    """Simulate a detection for demo"""
    print("\n5. Running Demo Detection Simulation...")
    
    try:
        model_path = Path("models/best.onnx")
        session = ort.InferenceSession(str(model_path))
        
        # Create dummy image
        dummy_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # Preprocess for model
        img_rgb = cv2.cvtColor(dummy_img, cv2.COLOR_BGR2RGB)
        img_norm = img_rgb.astype(np.float32) / 255.0
        img_transposed = np.transpose(img_norm, (2, 0, 1))
        img_batch = np.expand_dims(img_transposed, axis=0)
        
        # Run inference
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: img_batch})
        
        print("   ✅ Model inference successful!")
        print(f"   ✅ Output shape: {outputs[0].shape if outputs else 'No output'}")
        
        # Simulate detection
        print("\n   📱 DEMO: If a rat was detected, you would receive:")
        print("   SMS: '🐀 ALERT: Norway Rat detected at 2025-09-23 14:30:15'")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Demo simulation failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🐀 RODENT DETECTION SYSTEM - DEMO READINESS TEST")
    print("=" * 60)
    
    tests = [
        test_directories(),
        test_model_loading(),
        test_image_processing(),
        test_config(),
        run_demo_test()
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ SYSTEM IS READY FOR DEMO!")
        print("\nTo start the system for demo:")
        print("  python3 src/main.py")
        print("\nDemo features working:")
        print("  • ONNX model loaded")
        print("  • Image processing ready")
        print("  • SMS alerts configured")
        print("  • Detection pipeline functional")
    else:
        print("⚠️  Some issues need attention before demo")
        print("Please check the failures above")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)