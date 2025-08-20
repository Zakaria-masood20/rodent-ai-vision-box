# Rodent Detection System - Complete Setup Guide

## Table of Contents
1. [Hardware Setup](#hardware-setup)
2. [Software Installation](#software-installation)
3. [Camera Configuration](#camera-configuration)
4. [API Setup](#api-setup)
5. [System Configuration](#system-configuration)
6. [Testing & Validation](#testing--validation)
7. [Production Deployment](#production-deployment)

## Hardware Setup

### Required Components
- Raspberry Pi 5 (8GB RAM)
- 64GB MicroSD Card (Class 10 or better)
- USB-C Power Supply (5V, 3A minimum)
- Wyze Cam v4
- Ethernet cable or WiFi setup
- Heatsink/cooling fan (recommended)

### Assembly Steps

1. **Install Heatsink**
   ```
   - Clean the CPU surface with isopropyl alcohol
   - Remove adhesive backing from heatsink
   - Press firmly onto CPU for 30 seconds
   ```

2. **Connect Camera**
   - Position Wyze camera in target area
   - Configure camera using Wyze app
   - Enable local recording to SD card

3. **Prepare Raspberry Pi**
   - Insert MicroSD card
   - Connect to network (Ethernet preferred)
   - Connect power supply

## Software Installation

### 1. Flash Raspberry Pi OS

Download Raspberry Pi Imager: https://www.raspberrypi.com/software/

```bash
# Configure before writing:
- OS: Raspberry Pi OS Lite (64-bit)
- Enable SSH
- Set username/password
- Configure WiFi (if needed)
```

### 2. Initial System Setup

SSH into your Raspberry Pi:
```bash
ssh pi@raspberrypi.local
```

Update system:
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Install Rodent Detection System

```bash
# Download the system
git clone https://github.com/yourusername/rodent-detection.git
cd rodent-detection

# Run automated setup
chmod +x scripts/setup_raspberry_pi.sh
./scripts/setup_raspberry_pi.sh
```

## Camera Configuration

### Option 1: SD Card Access

1. **Mount Wyze SD Card**
   ```bash
   # Find SD card device
   sudo fdisk -l
   
   # Create mount point
   sudo mkdir -p /mnt/wyze_sd
   
   # Mount manually (replace sdX1 with your device)
   sudo mount /dev/sdX1 /mnt/wyze_sd
   ```

2. **Auto-mount Configuration**
   ```bash
   # Get SD card UUID
   sudo blkid /dev/sdX1
   
   # Edit fstab
   sudo nano /etc/fstab
   
   # Add line:
   UUID=YOUR-UUID /mnt/wyze_sd vfat defaults,auto,users,rw,nofail 0 0
   ```

### Option 2: RTSP Stream

1. **Enable RTSP on Wyze Camera**
   - Open Wyze app
   - Settings → Advanced Settings → RTSP
   - Generate RTSP URL

2. **Update Configuration**
   ```yaml
   camera:
     source: "rtsp"
     rtsp_url: "rtsp://user:pass@camera_ip/live"
   ```

## API Setup

### Twilio (SMS Alerts)

1. **Create Account**
   - Visit https://www.twilio.com/try-twilio
   - Sign up for free account
   - Verify your phone number

2. **Get Credentials**
   - Dashboard → Account SID
   - Dashboard → Auth Token
   - Phone Numbers → Buy a Number

3. **Configure**
   ```bash
   nano /opt/rodent_detection/.env
   ```
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_FROM_NUMBER=+1234567890
   ALERT_PHONE_NUMBER=+0987654321
   ```

### Email Setup (Gmail)

1. **Enable 2-Factor Authentication**
   - Google Account → Security → 2-Step Verification

2. **Generate App Password**
   - Security → App passwords
   - Select "Mail" and generate

3. **Configure**
   ```
   EMAIL_USERNAME=your.email@gmail.com
   EMAIL_PASSWORD=your-app-password
   FROM_EMAIL=alerts@rodentdetection.com
   ALERT_EMAIL=recipient@example.com
   ```

### Pushover (Push Notifications)

1. **Create Account**
   - Visit https://pushover.net/
   - Download mobile app

2. **Create Application**
   - Login → Create Application
   - Note API Token

3. **Configure**
   ```
   PUSHOVER_API_TOKEN=azxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   PUSHOVER_USER_KEY=uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

## System Configuration

### 1. Edit Main Configuration

```bash
nano /opt/rodent_detection/config/config.yaml
```

Key settings to adjust:
```yaml
# Adjust detection sensitivity
detection:
  confidence_threshold: 0.55  # Lower = more sensitive
  
# Set alert cooldown
alerts:
  cooldown_minutes: 10  # Prevent alert spam
  
# Choose notification channels
alerts:
  enabled_channels:
    - "sms"
    - "email"
    - "push"
```

### 2. Performance Tuning

For Raspberry Pi 5:
```yaml
video:
  frame_skip: 30  # Process every 30th frame
  resize_width: 640
  resize_height: 480
```

## Testing & Validation

### 1. Test Detection Engine

```bash
cd /opt/rodent_detection
source venv/bin/activate

# Test with sample video
python -m src.test_detection --video samples/test_video.mp4
```

### 2. Test Notifications

```bash
# Test SMS
python -m src.test_notifications --channel sms

# Test Email
python -m src.test_notifications --channel email
```

### 3. Monitor System

```bash
# Start in debug mode
python src/main.py --debug

# Watch logs
tail -f data/logs/rodent_detection.log
```

## Production Deployment

### 1. Enable Service

```bash
# Enable auto-start
sudo systemctl enable rodent-detection

# Start service
sudo systemctl start rodent-detection

# Check status
sudo systemctl status rodent-detection
```

### 2. Configure Monitoring

```bash
# Set up log rotation
sudo nano /etc/logrotate.d/rodent-detection
```

Add:
```
/opt/rodent_detection/data/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 3. Security Hardening

```bash
# Restrict permissions
sudo chmod 600 /opt/rodent_detection/.env
sudo chown pi:pi /opt/rodent_detection/.env

# Configure firewall
sudo ufw allow ssh
sudo ufw enable
```

### 4. Backup Configuration

Create backup script:
```bash
#!/bin/bash
# /opt/rodent_detection/scripts/backup.sh

BACKUP_DIR="/home/pi/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup config and database
tar -czf $BACKUP_DIR/rodent_backup_$DATE.tar.gz \
    /opt/rodent_detection/config \
    /opt/rodent_detection/.env \
    /opt/rodent_detection/data/detections.db

# Keep only last 7 backups
ls -t $BACKUP_DIR/rodent_backup_*.tar.gz | tail -n +8 | xargs -r rm
```

Add to crontab:
```bash
crontab -e
# Add: 0 2 * * * /opt/rodent_detection/scripts/backup.sh
```

## Maintenance

### Daily Tasks
- Check system status: `sudo systemctl status rodent-detection`
- Review recent detections in logs

### Weekly Tasks
- Check disk space: `df -h`
- Review detection accuracy
- Clean old images if needed

### Monthly Tasks
- Update system: `sudo apt update && sudo apt upgrade`
- Review and adjust detection thresholds
- Check camera positioning

## Troubleshooting

### Service Won't Start
```bash
# Check detailed logs
sudo journalctl -u rodent-detection -n 100

# Common fixes:
# - Verify .env file exists and has correct permissions
# - Check camera is accessible
# - Ensure all Python dependencies installed
```

### False Positives
- Increase `confidence_threshold` in config
- Ensure camera is stable (not moving)
- Check for reflections or shadows

### Missed Detections
- Decrease `confidence_threshold`
- Ensure adequate lighting
- Check camera focus

## Support Resources

- GitHub Issues: [your-repo-url]/issues
- Documentation: [your-repo-url]/wiki
- Model Training Guide: docs/training.md