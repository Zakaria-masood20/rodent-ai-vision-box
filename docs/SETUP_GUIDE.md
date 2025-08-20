# Rodent AI Vision Box - Complete Setup Guide

## Table of Contents
1. [Hardware Requirements](#hardware-requirements)
2. [Pre-Installation Checklist](#pre-installation-checklist)
3. [Raspberry Pi Setup](#raspberry-pi-setup)
4. [Software Installation](#software-installation)
5. [Wyze Camera Integration](#wyze-camera-integration)
6. [Configuration](#configuration)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Hardware Requirements

### Required Components:
- **Raspberry Pi 5** (8GB RAM recommended)
- **MicroSD Card** (64GB minimum, Class 10 or better)
- **Power Supply** (USB-C, 5V/3A minimum)
- **Wyze Cam v4** with SD card installed
- **Cooling** (Heatsink or fan recommended)
- **Network Connection** (WiFi or Ethernet)

### Optional Components:
- USB SD card reader (for direct SD card access)
- HDMI cable and monitor (for initial setup)
- Keyboard (for initial setup)

---

## Pre-Installation Checklist

Before starting, ensure you have:

- [ ] All hardware components listed above
- [ ] A computer with SD card reader
- [ ] Raspberry Pi Imager software installed
- [ ] Stable internet connection
- [ ] API credentials ready (or use dummy credentials initially)
- [ ] Wyze camera configured and recording to SD card

---

## Raspberry Pi Setup

### Step 1: Prepare the SD Card

1. Download Raspberry Pi Imager:
   ```
   https://www.raspberrypi.com/software/
   ```

2. Insert your MicroSD card into your computer

3. Open Raspberry Pi Imager and select:
   - **OS**: Raspberry Pi OS Lite (64-bit)
   - **Storage**: Your SD card

4. Click the gear icon for advanced options:
   - Set hostname: `rodentdetector`
   - Enable SSH
   - Set username: `pi`
   - Set password: (choose a secure password)
   - Configure WiFi (if using WiFi)
   - Set locale settings

5. Write the image to the SD card

### Step 2: First Boot

1. Insert the SD card into Raspberry Pi
2. Connect power supply
3. Wait 2-3 minutes for first boot
4. Find your Pi's IP address:
   ```bash
   # From your computer, scan network:
   arp -a | grep rodentdetector
   # Or check your router's DHCP client list
   ```

### Step 3: SSH Connection

```bash
ssh pi@rodentdetector.local
# Or use IP address:
ssh pi@192.168.1.XXX
```

---

## Software Installation

### Step 1: System Update

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    wget \
    curl \
    ffmpeg \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libopenblas-dev \
    libjpeg-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    sqlite3

# Install development tools
sudo apt install -y build-essential cmake pkg-config
```

### Step 2: Clone the Repository

```bash
# Create project directory
mkdir -p ~/projects
cd ~/projects

# Clone the rodent detection system
git clone https://github.com/yourusername/rodent-ai-vision-box.git
cd rodent-ai-vision-box
```

### Step 3: Python Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# For ARM optimization (Raspberry Pi):
pip install onnxruntime
```

### Step 4: Model Setup

The models are already included in the `models/` directory:
- `best.pt` - PyTorch YOLOv8 model
- `best.onnx` - ONNX optimized model (faster on Pi)

Verify models are present:
```bash
ls -la models/
```

### Step 5: Create Required Directories

```bash
# Create data directories
mkdir -p data/logs
mkdir -p data/images
mkdir -p data/videos

# Set permissions
chmod -R 755 data/
```

---

## Wyze Camera Integration

### Option 1: SD Card Access (Recommended)

#### Physical SD Card Removal:
1. Remove SD card from Wyze camera periodically
2. Insert into USB SD card reader
3. Connect to Raspberry Pi

#### Mounting SD Card:
```bash
# Find the SD card device
sudo fdisk -l

# Create mount point
sudo mkdir -p /mnt/wyze_sd

# Mount SD card (replace sdX1 with your device)
sudo mount /dev/sdX1 /mnt/wyze_sd

# Add to fstab for auto-mount
echo "UUID=$(sudo blkid -s UUID -o value /dev/sdX1) /mnt/wyze_sd vfat defaults,nofail 0 0" | sudo tee -a /etc/fstab
```

### Option 2: Network Access (RTSP)

If your Wyze camera supports RTSP:

1. Enable RTSP in Wyze app:
   - Open Wyze app
   - Select your camera
   - Settings → Advanced Settings → RTSP
   - Enable and note the URL

2. Update configuration:
   ```yaml
   camera:
     source: "rtsp"
     rtsp_url: "rtsp://username:password@camera_ip/live"
   ```

### Option 3: Wyze Bridge (Docker)

For continuous streaming without RTSP:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Run Wyze Bridge
docker run -d \
  --name wyze-bridge \
  -p 1935:1935 -p 8554:8554 -p 8888:8888 \
  -e WYZE_EMAIL=your_email \
  -e WYZE_PASSWORD=your_password \
  mrlt8/wyze-bridge:latest
```

---

## Configuration

### Step 1: Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

Update the following in `.env`:
```bash
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+1234567890
ALERT_PHONE_NUMBER=+0987654321

# Email Configuration
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com
ALERT_EMAIL=recipient@example.com

# Pushover Configuration
PUSHOVER_API_TOKEN=your_api_token_here
PUSHOVER_USER_KEY=your_user_key_here

# System Configuration
TIMEZONE=America/New_York
DEBUG=False
```

### Step 2: System Configuration

Edit `config/config.yaml`:

```bash
nano config/config.yaml
```

Key settings to verify:
```yaml
camera:
  source: "sd_card"  # or "rtsp" or "wyze_bridge"
  sd_mount_path: "/mnt/wyze_sd"
  
detection:
  model_path: "models/best.onnx"  # Use ONNX for better Pi performance
  confidence_threshold: 0.55
  
alerts:
  cooldown_minutes: 10
  enabled_channels:
    - "sms"  # Enable desired channels
```

---

## System Service Setup

### Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/rodent-detection.service
```

Add the following content:
```ini
[Unit]
Description=Rodent Detection System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/projects/rodent-ai-vision-box
Environment="PATH=/home/pi/projects/rodent-ai-vision-box/venv/bin"
ExecStart=/home/pi/projects/rodent-ai-vision-box/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable rodent-detection.service

# Start the service
sudo systemctl start rodent-detection.service

# Check service status
sudo systemctl status rodent-detection.service

# View logs
sudo journalctl -u rodent-detection.service -f
```

---

## Testing

### Step 1: Test Detection Engine

```bash
# Activate virtual environment
source venv/bin/activate

# Run test script
python test_system.py
```

Expected output:
- All 7 tests should pass
- Model should load successfully
- Detection should work on test images

### Step 2: Test with Sample Video

```bash
# Place a test video in data/videos/
# Run detection on video
python scripts/test_video.py data/videos/sample.mp4
```

### Step 3: Test Notifications

```bash
# Test SMS notification
python scripts/test_notifications.py sms

# Test email notification
python scripts/test_notifications.py email

# Test push notification
python scripts/test_notifications.py push
```

### Step 4: Monitor System

```bash
# Watch real-time logs
sudo journalctl -u rodent-detection.service -f

# Check detection statistics
sqlite3 data/detections.db "SELECT * FROM detections ORDER BY timestamp DESC LIMIT 10;"

# Monitor system resources
htop
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Service Won't Start
```bash
# Check service logs
sudo journalctl -u rodent-detection.service -n 50

# Check Python path
which python3

# Verify virtual environment
source venv/bin/activate
which python
```

#### 2. Camera Not Found
```bash
# Check SD card mount
ls -la /mnt/wyze_sd/

# Check mount status
mount | grep wyze

# Remount if needed
sudo umount /mnt/wyze_sd
sudo mount /dev/sdX1 /mnt/wyze_sd
```

#### 3. Model Loading Error
```bash
# Check model files
ls -la models/

# Test model loading
python -c "from ultralytics import YOLO; model = YOLO('models/best.pt'); print('Model loaded')"

# For ONNX issues
pip install --upgrade onnxruntime
```

#### 4. Notification Failures
```bash
# Check environment variables
cat .env

# Test API connectivity
curl -X POST https://api.twilio.com/2010-04-01/Accounts/YOUR_SID/Messages.json \
  --data-urlencode "Body=Test" \
  --data-urlencode "From=+1234567890" \
  --data-urlencode "To=+0987654321" \
  -u YOUR_SID:YOUR_AUTH_TOKEN
```

#### 5. High CPU Usage
```bash
# Adjust frame processing rate in config.yaml
video:
  frame_rate: 0.5  # Process every 2 seconds instead of every second
  frame_skip: 60   # Process every 60th frame
```

#### 6. Storage Issues
```bash
# Check disk space
df -h

# Clean old detections
sqlite3 data/detections.db "DELETE FROM detections WHERE timestamp < datetime('now', '-30 days');"

# Remove old images
find data/images -type f -mtime +30 -delete
```

---

## Performance Optimization

### For Raspberry Pi 5:

1. **Use ONNX Model**:
   ```yaml
   detection:
     model_path: "models/best.onnx"
   ```

2. **Enable GPU Memory Split**:
   ```bash
   sudo raspi-config
   # Advanced Options → Memory Split → 256
   ```

3. **Overclock (Optional)**:
   ```bash
   sudo nano /boot/config.txt
   # Add:
   over_voltage=6
   arm_freq=2400
   ```

4. **Use Swap File**:
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # Set CONF_SWAPSIZE=2048
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

---

## Security Recommendations

1. **Change Default Passwords**:
   ```bash
   passwd  # Change pi user password
   ```

2. **Configure Firewall**:
   ```bash
   sudo apt install ufw
   sudo ufw allow ssh
   sudo ufw enable
   ```

3. **Secure SSH**:
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   # Use SSH keys instead
   ```

4. **Regular Updates**:
   ```bash
   # Create update script
   sudo crontab -e
   # Add: 0 2 * * 0 apt update && apt upgrade -y
   ```

---

## Backup and Recovery

### Create System Backup:
```bash
# Stop service
sudo systemctl stop rodent-detection.service

# Backup database
cp data/detections.db data/detections_backup_$(date +%Y%m%d).db

# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/ .env

# Restart service
sudo systemctl start rodent-detection.service
```

### Create SD Card Image:
```bash
# From another Linux machine:
sudo dd if=/dev/sdX of=rodent_detection_image.img bs=4M status=progress
```

---

## Support

For issues or questions:
1. Check the logs: `sudo journalctl -u rodent-detection.service -n 100`
2. Review this guide's troubleshooting section
3. Check system resources: `htop`
4. Verify all connections and configurations

---

## Quick Start Commands Reference

```bash
# Service management
sudo systemctl start rodent-detection.service
sudo systemctl stop rodent-detection.service
sudo systemctl restart rodent-detection.service
sudo systemctl status rodent-detection.service

# Logs
sudo journalctl -u rodent-detection.service -f
tail -f data/logs/rodent_detection.log

# Database
sqlite3 data/detections.db ".tables"
sqlite3 data/detections.db "SELECT COUNT(*) FROM detections;"

# Testing
python test_system.py
python scripts/test_video.py

# Monitoring
htop
df -h
```

---

*Setup Guide Version 1.0 - August 2025*