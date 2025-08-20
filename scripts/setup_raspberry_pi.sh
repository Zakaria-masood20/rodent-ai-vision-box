#!/bin/bash

echo "=== Rodent Detection System - Raspberry Pi Setup ==="
echo "This script will install all required dependencies on your Raspberry Pi"

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    ffmpeg \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libjpeg-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libcanberra-gtk3-module \
    libatlas-base-dev \
    gfortran \
    wget \
    unzip

# Create application directory
APP_DIR="/opt/rodent_detection"
echo "Creating application directory at $APP_DIR..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files
echo "Copying application files..."
cp -r ../rodent_detection/* $APP_DIR/

# Create virtual environment
echo "Creating Python virtual environment..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install --upgrade pip wheel setuptools

# Install PyTorch for Raspberry Pi
echo "Installing PyTorch for ARM architecture..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
pip install -r requirements.txt

# Create data directories
echo "Creating data directories..."
mkdir -p data/{logs,images}

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/rodent-detection.service > /dev/null <<EOF
[Unit]
Description=Rodent Detection System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set up environment file
echo "Setting up environment configuration..."
cp .env.example .env
echo ""
echo "IMPORTANT: Please edit $APP_DIR/.env and add your API credentials"
echo ""

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable rodent-detection.service

# Mount point for Wyze SD card
echo "Creating mount point for Wyze SD card..."
sudo mkdir -p /mnt/wyze_sd
echo ""
echo "To auto-mount the Wyze SD card, add this line to /etc/fstab:"
echo "UUID=YOUR-SD-CARD-UUID /mnt/wyze_sd vfat defaults,auto,users,rw,nofail 0 0"
echo ""

# Setup complete
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit $APP_DIR/.env with your API credentials"
echo "2. Configure SD card auto-mount in /etc/fstab"
echo "3. Start the service: sudo systemctl start rodent-detection"
echo "4. Check logs: sudo journalctl -u rodent-detection -f"
echo ""
echo "To download a pre-trained rodent model, run:"
echo "cd $APP_DIR && ./scripts/download_model.sh"