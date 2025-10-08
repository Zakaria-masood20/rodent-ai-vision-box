# Production Deployment Guide 🚀

Complete step-by-step guide to deploy the Rodent AI Vision Box system in production.

## Pre-Deployment Checklist

### Hardware Requirements ✅
- [ ] Raspberry Pi 5 (8GB RAM)
- [ ] 64GB MicroSD Card (Class 10 or better)
- [ ] USB-C Power Supply (5V, 3A minimum)
- [ ] Wyze v4 Camera configured and working
- [ ] Ethernet cable or WiFi configured
- [ ] Cooling solution (heatsink/fan)

### Software Requirements ✅
- [ ] Raspberry Pi OS Lite 64-bit (or Ubuntu 22.04)
- [ ] Internet connection configured
- [ ] SSH access enabled
- [ ] EmailJS account created and configured

## Step 1: Prepare Raspberry Pi

### 1.1 Flash OS to SD Card
```bash
# Download Raspberry Pi Imager
# Flash Raspberry Pi OS Lite (64-bit) to SD card
# Enable SSH during setup
# Configure WiFi if needed
```

### 1.2 Initial Setup
```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Set timezone
sudo timedatectl set-timezone America/New_York

# Expand filesystem
sudo raspi-config --expand-rootfs
```

## Step 2: Clone Repository

```bash
# Install git
sudo apt install git -y

# Clone the repository
cd /home/pi
git clone [your-repository-url] rodent-ai-vision-box
cd rodent-ai-vision-box
```

## Step 3: Run Automated Setup

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (this will take 10-15 minutes)
sudo ./setup.sh
```

The setup script will:
- Install system dependencies
- Install Python 3.9+
- Create virtual environment
- Install all Python packages
- Download AI models
- Configure system service
- Set up directories

## Step 4: Configure EmailJS

### 4.1 Create .env File
```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env
```

### 4.2 Add EmailJS Credentials
```env
# EmailJS Configuration (REQUIRED)
EMAILJS_SERVICE_ID=service_2q7m7pm
EMAILJS_TEMPLATE_ID=template_0q4z7y8
EMAILJS_PUBLIC_KEY=Cx4zjcLaDjfhS2ssD
EMAILJS_PRIVATE_KEY=h1bojFisOSGIE9IIF9yhP
EMAILJS_TO_EMAIL=ratproject111@gmail.com

# System Settings
TIMEZONE=America/New_York
USE_ONNX=true
LOG_LEVEL=INFO
```

### 4.3 Test Email Configuration
```bash
# Activate virtual environment
source venv/bin/activate

# Test EmailJS
python test_emailjs.py
```

✅ You should receive a test email at ratproject111@gmail.com

## Step 5: Configure Camera

### 5.1 For SD Card Mode (Recommended)
```bash
# Create mount point
sudo mkdir -p /mnt/wyze_sd

# Mount SD card (replace sdX1 with your device)
sudo mount /dev/sda1 /mnt/wyze_sd

# Add to fstab for auto-mount
echo "/dev/sda1 /mnt/wyze_sd auto defaults 0 0" | sudo tee -a /etc/fstab
```

### 5.2 For RTSP Mode
```yaml
# Edit config/config.yaml
camera:
  source: "rtsp"
  rtsp_url: "rtsp://192.168.1.100:554/live"
```

## Step 6: Start the Service

### 6.1 Enable and Start
```bash
# Enable service for auto-start
sudo systemctl enable rodent-detection

# Start the service
sudo systemctl start rodent-detection

# Check status
sudo systemctl status rodent-detection
```

### 6.2 Verify Operation
```bash
# Watch logs in real-time
sudo journalctl -u rodent-detection -f

# Check application logs
tail -f data/logs/rodent_detection.log
```

## Step 7: Production Configuration

### 7.1 Optimize Performance
```yaml
# Edit config/config.yaml for production

# Adjust detection sensitivity
detection:
  confidence_threshold: 0.30  # Lower = more sensitive
  nms_threshold: 0.45

# Set appropriate cooldown
alerts:
  cooldown_minutes: 10  # Prevent alert spam

# Optimize video processing
video:
  frame_rate: 1  # Process 1 frame per second
  frame_skip: 30  # Skip frames for efficiency
```

### 7.2 Security Hardening
```bash
# Change default password
passwd pi

# Configure firewall
sudo apt install ufw -y
sudo ufw allow ssh
sudo ufw enable

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

## Step 8: Monitoring Setup

### 8.1 System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop -y

# Create monitoring script
cat > ~/monitor.sh << 'EOF'
#!/bin/bash
echo "=== System Status ==="
df -h
echo ""
echo "=== Memory Usage ==="
free -h
echo ""
echo "=== Service Status ==="
systemctl status rodent-detection --no-pager
echo ""
echo "=== Recent Detections ==="
sqlite3 /home/pi/rodent-ai-vision-box/data/detections.db \
  "SELECT datetime, class_name, confidence FROM detections ORDER BY datetime DESC LIMIT 5;"
EOF

chmod +x ~/monitor.sh
```

### 8.2 Log Rotation
```bash
# Configure log rotation
sudo tee /etc/logrotate.d/rodent-detection << EOF
/home/pi/rodent-ai-vision-box/data/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 pi pi
    postrotate
        systemctl reload rodent-detection
    endscript
}
EOF
```

## Step 9: Testing & Validation

### 9.1 Test Detection
```bash
# Test with sample image
cd /home/pi/rodent-ai-vision-box
source venv/bin/activate
python test_detection.py
```

### 9.2 Simulate Detection
```bash
# Place test images in camera directory
# Monitor for email alerts
# Check detection logs
```

### 9.3 Performance Testing
```bash
# Monitor CPU usage
htop

# Check memory
free -h

# Monitor disk I/O
iotop

# Check temperature
vcgencmd measure_temp
```

## Step 10: Backup & Recovery

### 10.1 Create System Backup
```bash
# Backup configuration
tar -czf config_backup.tar.gz .env config/

# Backup database
cp data/detections.db data/detections_backup.db

# Create full backup
sudo dd if=/dev/mmcblk0 of=/path/to/backup.img bs=4M
```

### 10.2 Recovery Procedure
```bash
# Restore configuration
tar -xzf config_backup.tar.gz

# Restore database
cp data/detections_backup.db data/detections.db

# Restart service
sudo systemctl restart rodent-detection
```

## Maintenance Tasks

### Daily
- Check email alerts are working
- Monitor disk space: `df -h`
- Check service status: `sudo systemctl status rodent-detection`

### Weekly
- Review detection logs
- Check for false positives
- Clear old detection images: `find data/images -mtime +7 -delete`

### Monthly
- Update system: `sudo apt update && sudo apt upgrade`
- Backup database
- Review EmailJS usage (200 email limit)
- Check camera positioning

## Troubleshooting Quick Reference

### Service Won't Start
```bash
sudo systemctl status rodent-detection
journalctl -xe
# Check Python dependencies
source venv/bin/activate
python -c "import cv2, torch"
```

### No Email Alerts
```bash
# Test EmailJS
python test_emailjs.py
# Check credentials
grep EMAILJS .env
# Verify internet
ping google.com
```

### High CPU Usage
```bash
# Enable ONNX optimization
echo "USE_ONNX=true" >> .env
# Reduce frame rate in config
# Check temperature
vcgencmd measure_temp
```

### Camera Issues
```bash
# SD card mode
ls /mnt/wyze_sd
# RTSP mode
ffmpeg -i rtsp://camera_ip -frames:v 1 test.jpg
```

## Production Metrics

### Expected Performance
- **CPU Usage**: 40-60% with ONNX
- **RAM Usage**: 1.5-2GB
- **Disk Usage**: ~100MB/day for images
- **Detection Time**: ~120ms per frame
- **Alert Latency**: < 5 seconds
- **Uptime Target**: 99.9%

### Key Indicators
- Detection count per day
- False positive rate (target < 5%)
- Email delivery success rate
- System uptime
- Resource utilization

## Security Considerations

1. **Network Security**
   - Use strong WiFi password
   - Enable firewall
   - Disable unnecessary ports

2. **Access Control**
   - Change default passwords
   - Use SSH keys instead of passwords
   - Limit sudo access

3. **Data Protection**
   - Encrypt sensitive data
   - Secure .env file permissions: `chmod 600 .env`
   - Regular backups

4. **Monitoring**
   - Set up fail2ban for SSH
   - Monitor system logs
   - Alert on suspicious activity

## Rollback Procedure

If issues occur after deployment:

1. **Stop Service**
   ```bash
   sudo systemctl stop rodent-detection
   ```

2. **Restore Previous Version**
   ```bash
   git checkout previous-version-tag
   ```

3. **Restore Configuration**
   ```bash
   cp .env.backup .env
   ```

4. **Restart Service**
   ```bash
   sudo systemctl start rodent-detection
   ```

## Contact & Support

### For Issues:
1. Check logs: `journalctl -u rodent-detection -n 100`
2. Review [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
3. Test components individually
4. Contact development team with:
   - Error messages
   - Log files
   - System configuration

### System Information to Provide:
```bash
# Collect system info
uname -a
python3 --version
systemctl status rodent-detection
df -h
free -h
```

## Final Verification

### Production Readiness Checklist:
- [ ] EmailJS tested and working
- [ ] Service running and enabled
- [ ] Camera feed accessible
- [ ] Detection working (test image)
- [ ] Logs being generated
- [ ] Disk space adequate (>10GB free)
- [ ] CPU temperature normal (<70°C)
- [ ] Network stable
- [ ] Backup created
- [ ] Monitoring configured

## Success Indicators

Your system is ready when:
- ✅ Service starts automatically on boot
- ✅ Email alerts arrive within 5 seconds of detection
- ✅ CPU usage stays below 70%
- ✅ System runs 24/7 without intervention
- ✅ Logs show successful detections

---

**Congratulations! Your Rodent AI Vision Box is now deployed in production!** 🎉

Monitor the system for the first 24-48 hours to ensure stable operation.