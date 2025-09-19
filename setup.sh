#!/bin/bash

# =====================================================
# Rodent AI Vision Box - Setup Script
# =====================================================
# This script sets up the complete system on Raspberry Pi
# =====================================================

set -e

echo "======================================"
echo "RODENT AI VISION BOX - SETUP"
echo "======================================"

# Check if running on Raspberry Pi
if [[ ! -f /proc/device-tree/model ]]; then
    echo "⚠️  Warning: Not running on Raspberry Pi"
fi

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev

# Create project directory
PROJECT_DIR="$HOME/rodent-ai-vision-box"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📁 Creating project directory..."
    mkdir -p "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install --no-cache-dir \
    ultralytics \
    opencv-python-headless \
    numpy \
    Pillow \
    twilio \
    pyyaml \
    python-dotenv \
    requests \
    aiofiles \
    sqlalchemy \
    tqdm

# Install ONNX Runtime for ARM64 (Raspberry Pi)
if [[ $(uname -m) == "aarch64" ]]; then
    echo "🚀 Installing ONNX Runtime for ARM64..."
    pip install onnxruntime
fi

# Create directory structure
echo "📂 Creating directory structure..."
mkdir -p models
mkdir -p data/logs
mkdir -p data/images
mkdir -p config
mkdir -p scripts

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Please edit .env file with your Twilio credentials"
    fi
fi

# Set up SD card mount point
echo "💾 Setting up SD card mount point..."
sudo mkdir -p /mnt/wyze_sd
echo "Note: You'll need to mount your Wyze SD card to /mnt/wyze_sd"

# Install systemd service
echo "🚀 Installing systemd service..."
sudo cp scripts/rodent-detection.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rodent-detection.service

# Set permissions
echo "🔐 Setting permissions..."
chmod +x setup.sh
chmod +x scripts/*.sh

# Create test script
cat > test_system.py << 'EOF'
#!/usr/bin/env python3
"""Test script to verify system setup"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import cv2
        print("✅ OpenCV imported")
    except ImportError:
        print("❌ OpenCV not found")
        return False
    
    try:
        from ultralytics import YOLO
        print("✅ Ultralytics YOLO imported")
    except ImportError:
        print("❌ Ultralytics not found")
        return False
    
    try:
        from twilio.rest import Client
        print("✅ Twilio imported")
    except ImportError:
        print("❌ Twilio not found")
        return False
    
    try:
        import onnxruntime
        print("✅ ONNX Runtime imported")
    except ImportError:
        print("⚠️  ONNX Runtime not found (optional)")
    
    return True

def test_models():
    """Test if models are present"""
    print("\nTesting models...")
    
    if os.path.exists("models/best.pt"):
        print("✅ PyTorch model found")
    else:
        print("❌ PyTorch model not found")
        
    if os.path.exists("models/best.onnx"):
        print("✅ ONNX model found")
    else:
        print("⚠️  ONNX model not found (optional)")
    
    return os.path.exists("models/best.pt") or os.path.exists("models/best.onnx")

def test_config():
    """Test if configuration files exist"""
    print("\nTesting configuration...")
    
    if os.path.exists(".env"):
        print("✅ .env file found")
        # Check for Twilio credentials
        with open(".env", "r") as f:
            content = f.read()
            if "your_account_sid_here" in content:
                print("⚠️  Please update Twilio credentials in .env")
            else:
                print("✅ Twilio credentials appear to be set")
    else:
        print("❌ .env file not found")
        return False
    
    if os.path.exists("config/config.yaml"):
        print("✅ config.yaml found")
    else:
        print("❌ config.yaml not found")
        return False
    
    return True

def main():
    print("====================================")
    print("SYSTEM TEST")
    print("====================================")
    
    all_good = True
    
    if not test_imports():
        all_good = False
    
    if not test_models():
        all_good = False
    
    if not test_config():
        all_good = False
    
    print("\n====================================")
    if all_good:
        print("✅ System is ready!")
        print("Start with: sudo systemctl start rodent-detection")
    else:
        print("❌ Some issues found. Please fix them before starting.")
    print("====================================")

if __name__ == "__main__":
    main()
EOF

echo ""
echo "======================================"
echo "✅ SETUP COMPLETE!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Twilio credentials:"
echo "   nano .env"
echo ""
echo "2. Copy your trained models to the models/ directory:"
echo "   - models/best.pt (required)"
echo "   - models/best.onnx (optional, for better performance)"
echo ""
echo "3. Mount Wyze SD card to /mnt/wyze_sd"
echo ""
echo "4. Test the system:"
echo "   python test_system.py"
echo ""
echo "5. Start the service:"
echo "   sudo systemctl start rodent-detection"
echo ""
echo "6. Check logs:"
echo "   sudo journalctl -u rodent-detection -f"
echo ""
echo "======================================"