# Troubleshooting Guide 🔧

Comprehensive guide to diagnose and fix common issues with the Rodent AI Vision Box.

## Table of Contents
1. [Email Notification Issues](#email-notification-issues)
2. [Service & Startup Problems](#service--startup-problems)
3. [Camera Connection Issues](#camera-connection-issues)
4. [Detection Problems](#detection-problems)
5. [Performance Issues](#performance-issues)
6. [System Errors](#system-errors)
7. [Database Issues](#database-issues)
8. [Network Problems](#network-problems)

---

## Email Notification Issues

### ❌ Problem: No emails being received

#### Diagnosis:
```bash
# Test EmailJS directly
python test_emailjs.py

# Check EmailJS credentials
grep EMAILJS .env

# Check service logs for email errors
grep -i "email" data/logs/rodent_detection.log
```

#### Solutions:

1. **Verify EmailJS Credentials**
   ```bash
   # Check if credentials are set
   cat .env | grep EMAILJS
   
   # Ensure no extra spaces or quotes
   EMAILJS_SERVICE_ID=service_2q7m7pm  # ✅ Correct
   EMAILJS_SERVICE_ID="service_2q7m7pm"  # ❌ Wrong (no quotes needed)
   ```

2. **Check EmailJS Dashboard**
   - Login to [emailjs.com](https://www.emailjs.com)
   - Check "Email History" for failed attempts
   - Verify monthly quota (200 free emails)
   - Check if service is active

3. **Verify Email Template**
   - Ensure template variables match:
     - `{{rodent_type}}`
     - `{{detection_time}}`
     - `{{confidence}}`
     - `{{message}}`

4. **Check Spam Folder**
   - Emails might be in spam/junk folder
   - Add sender to contacts/whitelist

5. **Test Internet Connection**
   ```bash
   ping -c 4 api.emailjs.com
   curl -I https://api.emailjs.com
   ```

### ❌ Problem: EmailJS API Error 403 (Forbidden)

#### Solution:
This error occurs when EmailJS detects non-browser requests. The system should handle this automatically, but if not:

1. Update notification service
2. Ensure headers are set correctly in the code
3. Check EmailJS service settings

### ❌ Problem: EmailJS Quota Exceeded

#### Solution:
```bash
# Check detection frequency
sqlite3 data/detections.db "SELECT COUNT(*) FROM detections WHERE datetime > datetime('now', '-1 day');"

# Increase cooldown period
# Edit config/config.yaml
alerts:
  cooldown_minutes: 30  # Increase from 10 to 30
```

---

## Service & Startup Problems

### ❌ Problem: Service won't start

#### Diagnosis:
```bash
# Check service status
sudo systemctl status rodent-detection

# Check detailed logs
journalctl -xe -u rodent-detection

# Check if Python environment exists
ls -la /home/pi/rodent-ai-vision-box/venv/
```

#### Solutions:

1. **Reinstall Dependencies**
   ```bash
   cd /home/pi/rodent-ai-vision-box
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Check File Permissions**
   ```bash
   # Fix ownership
   sudo chown -R pi:pi /home/pi/rodent-ai-vision-box
   
   # Fix permissions
   chmod +x setup.sh
   chmod 755 src/*.py
   ```

3. **Verify Service File**
   ```bash
   cat /etc/systemd/system/rodent-detection.service
   
   # Reload if modified
   sudo systemctl daemon-reload
   ```

### ❌ Problem: Service starts but crashes immediately

#### Diagnosis:
```bash
# Watch logs in real-time
journalctl -fu rodent-detection

# Check Python errors
cd /home/pi/rodent-ai-vision-box
source venv/bin/activate
python src/main.py  # Run manually to see errors
```

#### Common Causes:
- Missing .env file
- Invalid configuration
- Camera not connected
- Model file missing

---

## Camera Connection Issues

### ❌ Problem: SD Card not detected

#### Diagnosis:
```bash
# List USB devices
lsusb

# Check block devices
lsblk

# Check mount points
mount | grep wyze
```

#### Solutions:

1. **Manual Mount**
   ```bash
   # Create mount point
   sudo mkdir -p /mnt/wyze_sd
   
   # Find device (usually /dev/sda1)
   sudo fdisk -l
   
   # Mount manually
   sudo mount /dev/sda1 /mnt/wyze_sd
   
   # Verify files
   ls /mnt/wyze_sd
   ```

2. **Auto-Mount Configuration**
   ```bash
   # Add to /etc/fstab
   echo "/dev/sda1 /mnt/wyze_sd auto defaults,nofail 0 0" | sudo tee -a /etc/fstab
   ```

### ❌ Problem: RTSP stream not working

#### Diagnosis:
```bash
# Test RTSP connection
ffmpeg -i rtsp://camera_ip:554/live -frames:v 1 test.jpg

# Check network connectivity
ping camera_ip
```

#### Solutions:

1. **Enable RTSP on Wyze Camera**
   - Use Wyze app
   - Settings → Advanced Settings → RTSP
   - Generate RTSP URL

2. **Update Configuration**
   ```yaml
   # config/config.yaml
   camera:
     source: "rtsp"
     rtsp_url: "rtsp://username:password@192.168.1.100:554/live"
   ```

---

## Detection Problems

### ❌ Problem: No detections occurring

#### Diagnosis:
```bash
# Check if model is loaded
grep -i "model loaded" data/logs/rodent_detection.log

# Check frame processing
grep -i "processing frame" data/logs/rodent_detection.log

# Test detection manually
python test_detection.py
```

#### Solutions:

1. **Lower Confidence Threshold**
   ```yaml
   # config/config.yaml
   detection:
     confidence_threshold: 0.20  # Lower from 0.25
   ```

2. **Check Model File**
   ```bash
   # Verify model exists
   ls -la models/
   
   # Should see:
   # best.pt or best.onnx
   
   # If missing, download model
   wget [model_url] -O models/best.onnx
   ```

3. **Improve Lighting**
   - Ensure adequate lighting in monitored area
   - Consider IR illuminator for night vision

### ❌ Problem: Too many false positives

#### Solutions:

1. **Increase Confidence Threshold**
   ```yaml
   detection:
     confidence_threshold: 0.40  # Increase from 0.25
     nms_threshold: 0.50  # Increase from 0.45
   ```

2. **Adjust Camera Position**
   - Avoid areas with moving shadows
   - Position at rodent height
   - Minimize background movement

---

## Performance Issues

### ❌ Problem: High CPU usage (>80%)

#### Diagnosis:
```bash
# Monitor CPU
htop

# Check temperature
vcgencmd measure_temp

# Check process details
ps aux | grep python
```

#### Solutions:

1. **Enable ONNX Optimization**
   ```bash
   # Edit .env
   USE_ONNX=true
   
   # Restart service
   sudo systemctl restart rodent-detection
   ```

2. **Reduce Processing Frequency**
   ```yaml
   # config/config.yaml
   video:
     frame_rate: 0.5  # Process every 2 seconds
     frame_skip: 60   # Skip more frames
   ```

3. **Add Cooling**
   ```bash
   # Check temperature
   while true; do vcgencmd measure_temp; sleep 5; done
   
   # If > 70°C, add heatsink/fan
   ```

### ❌ Problem: High memory usage

#### Diagnosis:
```bash
# Check memory
free -h

# Check for memory leaks
ps aux --sort=-%mem | head
```

#### Solutions:

1. **Restart Service Periodically**
   ```bash
   # Add to crontab
   0 3 * * * sudo systemctl restart rodent-detection
   ```

2. **Clear Old Data**
   ```bash
   # Remove old images
   find data/images -mtime +7 -delete
   
   # Vacuum database
   sqlite3 data/detections.db "VACUUM;"
   ```

---

## System Errors

### ❌ Problem: "Module not found" errors

#### Solution:
```bash
cd /home/pi/rodent-ai-vision-box
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ Problem: Permission denied errors

#### Solution:
```bash
# Fix ownership
sudo chown -R pi:pi /home/pi/rodent-ai-vision-box

# Fix permissions
chmod 755 src/*.py
chmod 600 .env  # Secure credentials
```

### ❌ Problem: Disk full

#### Diagnosis:
```bash
df -h
du -sh data/*
```

#### Solution:
```bash
# Clear old detection images
find data/images -mtime +3 -delete

# Clear logs
echo "" > data/logs/rodent_detection.log

# Remove test files
rm -rf test_env/
```

---

## Database Issues

### ❌ Problem: Database locked

#### Solution:
```bash
# Stop service
sudo systemctl stop rodent-detection

# Backup database
cp data/detections.db data/detections_backup.db

# Fix database
sqlite3 data/detections.db "PRAGMA integrity_check;"

# Restart service
sudo systemctl start rodent-detection
```

### ❌ Problem: Database corrupted

#### Solution:
```bash
# Restore from backup
cp data/detections_backup.db data/detections.db

# Or create new database
rm data/detections.db
python -c "from src.database import init_db; init_db()"
```

---

## Network Problems

### ❌ Problem: No internet connection

#### Diagnosis:
```bash
# Test connectivity
ping -c 4 google.com
ping -c 4 8.8.8.8

# Check network interface
ip addr show
```

#### Solutions:

1. **WiFi Issues**
   ```bash
   # Check WiFi status
   iwconfig
   
   # Reconnect WiFi
   sudo nmcli device wifi connect "SSID" password "password"
   ```

2. **Ethernet Issues**
   ```bash
   # Restart network
   sudo systemctl restart networking
   
   # Check cable connection
   ethtool eth0
   ```

---

## Quick Diagnostic Commands

### System Health Check
```bash
#!/bin/bash
echo "=== System Status ==="
systemctl status rodent-detection --no-pager
echo ""
echo "=== CPU & Memory ==="
top -bn1 | head -5
echo ""
echo "=== Disk Usage ==="
df -h /
echo ""
echo "=== Temperature ==="
vcgencmd measure_temp
echo ""
echo "=== Recent Errors ==="
journalctl -u rodent-detection -p err -n 10 --no-pager
echo ""
echo "=== EmailJS Test ==="
python test_emailjs.py
```

### Log Analysis
```bash
# Check for errors
grep -i error data/logs/rodent_detection.log | tail -20

# Check email sending
grep -i "email\|notification" data/logs/rodent_detection.log | tail -20

# Check detections
grep -i "detected\|confidence" data/logs/rodent_detection.log | tail -20
```

---

## Emergency Recovery

### Complete System Reset
```bash
# Stop service
sudo systemctl stop rodent-detection

# Backup data
tar -czf backup_$(date +%Y%m%d).tar.gz .env data/

# Clean and reinstall
git pull origin main
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Restore configuration
cp .env.backup .env

# Restart
sudo systemctl start rodent-detection
```

---

## Still Having Issues?

If problems persist:

1. **Collect System Information**
   ```bash
   uname -a > system_info.txt
   python3 --version >> system_info.txt
   pip freeze >> system_info.txt
   systemctl status rodent-detection >> system_info.txt
   journalctl -u rodent-detection -n 100 >> system_info.txt
   ```

2. **Check Documentation**
   - [README.md](../README.md)
   - [EmailJS Setup](EMAILJS_SETUP.md)
   - [Production Deployment](../PRODUCTION_DEPLOYMENT.md)

3. **Common Quick Fixes**
   - Restart service: `sudo systemctl restart rodent-detection`
   - Reboot system: `sudo reboot`
   - Check credentials: `grep -E "EMAILJS|TOKEN" .env`
   - Test components: `python test_emailjs.py`

---

**Remember**: Most issues are related to:
- 📧 EmailJS configuration (check credentials)
- 📷 Camera connection (check mounting/network)
- 🔧 Permissions (run setup.sh)
- 🌐 Network connectivity (check internet)
- 💾 Disk space (clear old files)