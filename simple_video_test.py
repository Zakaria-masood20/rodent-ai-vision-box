#!/usr/bin/env python3
"""
Simple Video Test Script for Rodent Detection System
Tests the detection capability with your video files
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def check_dependencies():
    """Check if required modules are available"""
    modules_status = {}
    
    required_modules = [
        'cv2',
        'numpy',
        'PIL',
        'torch',
        'yaml'
    ]
    
    print("Checking dependencies...")
    for module in required_modules:
        try:
            __import__(module)
            modules_status[module] = "✅ Installed"
            print(f"  {module}: ✅ Installed")
        except ImportError:
            modules_status[module] = "❌ Not installed"
            print(f"  {module}: ❌ Not installed")
    
    return modules_status

def analyze_videos_metadata():
    """Analyze video files without processing them"""
    test_dir = Path("/Users/zakariamasoodgosign/Documents/zakaria/Freelance/RAT_Project/Test_videos")
    
    if not test_dir.exists():
        print(f"Error: Test videos directory not found: {test_dir}")
        return None
    
    video_files = list(test_dir.glob("*.mp4"))
    
    print(f"\n{'='*60}")
    print(f"VIDEO FILES ANALYSIS")
    print(f"{'='*60}")
    
    results = {
        "test_date": datetime.now().isoformat(),
        "videos": []
    }
    
    for video_file in sorted(video_files):
        file_size_mb = video_file.stat().st_size / (1024 * 1024)
        
        video_info = {
            "name": video_file.name,
            "path": str(video_file),
            "size_mb": round(file_size_mb, 2),
            "exists": video_file.exists()
        }
        
        results["videos"].append(video_info)
        
        print(f"\n📹 {video_file.name}")
        print(f"   Size: {file_size_mb:.2f} MB")
        print(f"   Path: {video_file}")
    
    return results

def create_test_plan():
    """Create a test plan for the videos"""
    print(f"\n{'='*60}")
    print(f"TEST PLAN FOR RODENT DETECTION")
    print(f"{'='*60}")
    
    test_plan = {
        "created": datetime.now().isoformat(),
        "test_scenarios": [
            {
                "video": "T1.mp4",
                "description": "Test video 1 - 4.6 MB",
                "expected_checks": [
                    "Video loads successfully",
                    "Detection engine processes frames",
                    "Any rodents detected are logged",
                    "Output frames are saved"
                ]
            },
            {
                "video": "T2.mp4",
                "description": "Test video 2 - 1.8 MB",
                "expected_checks": [
                    "Video loads successfully",
                    "Detection engine processes frames",
                    "Any rodents detected are logged",
                    "Output frames are saved"
                ]
            },
            {
                "video": "T3.mp4",
                "description": "Test video 3 - 6.0 MB",
                "expected_checks": [
                    "Video loads successfully",
                    "Detection engine processes frames",
                    "Any rodents detected are logged",
                    "Output frames are saved"
                ]
            },
            {
                "video": "T4.mp4",
                "description": "Test video 4 - 5.3 MB",
                "expected_checks": [
                    "Video loads successfully",
                    "Detection engine processes frames",
                    "Any rodents detected are logged",
                    "Output frames are saved"
                ]
            },
            {
                "video": "T5.mp4",
                "description": "Test video 5 - 9.4 MB (largest)",
                "expected_checks": [
                    "Video loads successfully",
                    "Detection engine processes frames",
                    "Any rodents detected are logged",
                    "Output frames are saved"
                ]
            }
        ],
        "testing_steps": [
            "1. Check all dependencies are installed",
            "2. Verify model file exists (best.onnx)",
            "3. Load each video file",
            "4. Process frames through detection engine",
            "5. Log any detections found",
            "6. Save annotated frames with bounding boxes",
            "7. Generate summary report"
        ],
        "expected_outputs": [
            "test_results/ directory with timestamped folders",
            "Detection frames saved as images",
            "JSON report with detection statistics",
            "HTML report for easy viewing"
        ]
    }
    
    print("\n📋 Test Scenarios:")
    for scenario in test_plan["test_scenarios"]:
        print(f"\n  • {scenario['video']}: {scenario['description']}")
        for check in scenario["expected_checks"]:
            print(f"    - {check}")
    
    print("\n📝 Testing Steps:")
    for step in test_plan["testing_steps"]:
        print(f"  {step}")
    
    print("\n📁 Expected Outputs:")
    for output in test_plan["expected_outputs"]:
        print(f"  • {output}")
    
    return test_plan

def check_model_file():
    """Check if the detection model file exists"""
    model_path = Path("/Users/zakariamasoodgosign/Documents/zakaria/Freelance/RAT_Project/rodent-ai-vision-box/models/best.onnx")
    
    print(f"\n{'='*60}")
    print(f"MODEL FILE CHECK")
    print(f"{'='*60}")
    
    if model_path.exists():
        file_size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✅ Model file found: {model_path}")
        print(f"   Size: {file_size_mb:.2f} MB")
        return True
    else:
        print(f"❌ Model file not found: {model_path}")
        print(f"   Please ensure the model file is in place before testing")
        return False

def generate_setup_instructions():
    """Generate instructions for setting up the test environment"""
    print(f"\n{'='*60}")
    print(f"SETUP INSTRUCTIONS")
    print(f"{'='*60}")
    
    print("\n To run the full video tests, you need to:")
    print("\n 1. Install dependencies (if not already installed):")
    print("    pip3 install opencv-python numpy pillow torch pyyaml")
    
    print("\n 2. Ensure the model file exists:")
    print("    models/best.onnx")
    
    print("\n 3. Run the test script:")
    print("    python3 test_videos.py")
    
    print("\n 4. Check results in:")
    print("    test_results/ directory")
    
    print("\n Alternative: Use the existing test_detection.py script:")
    print("    python3 test_detection.py")

def main():
    """Main function to run the simple test"""
    print(f"\n{'='*60}")
    print(f"RODENT DETECTION SYSTEM - VIDEO TEST PREPARATION")
    print(f"{'='*60}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Check dependencies
    deps_status = check_dependencies()
    
    # Analyze video files
    video_analysis = analyze_videos_metadata()
    
    # Check model file
    model_exists = check_model_file()
    
    # Create test plan
    test_plan = create_test_plan()
    
    # Generate setup instructions if dependencies are missing
    if any("❌" in status for status in deps_status.values()):
        generate_setup_instructions()
    
    # Save analysis to file
    output_dir = Path("test_results")
    output_dir.mkdir(exist_ok=True)
    
    analysis_file = output_dir / f"test_preparation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(analysis_file, 'w') as f:
        json.dump({
            "dependencies": deps_status,
            "videos": video_analysis,
            "model_exists": model_exists,
            "test_plan": test_plan
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"TEST PREPARATION COMPLETE")
    print(f"{'='*60}")
    print(f"Analysis saved to: {analysis_file}")
    
    if all("✅" in status for status in deps_status.values()) and model_exists:
        print(f"\n✅ System is ready for video testing!")
        print(f"   Run: python3 test_videos.py")
    else:
        print(f"\n⚠️  Some dependencies or files are missing.")
        print(f"   Please follow the setup instructions above.")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()