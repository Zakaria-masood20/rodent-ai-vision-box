# Rodent AI Vision Box - User Manual

## Table of Contents
1. [System Overview](#system-overview)
2. [Getting Started](#getting-started)
3. [Daily Operation](#daily-operation)
4. [Understanding Alerts](#understanding-alerts)
5. [Viewing Detection History](#viewing-detection-history)
6. [Configuration Settings](#configuration-settings)
7. [Maintenance](#maintenance)
8. [FAQ](#faq)

---

## System Overview

The Rodent AI Vision Box is an automated detection system that monitors your premises for rodent activity 24/7. Using advanced AI technology, it:

- ✅ Detects rats and mice in real-time
- ✅ Sends instant alerts to your phone/email
- ✅ Saves images of detections for review
- ✅ Filters out false alarms (pets, humans, etc.)
- ✅ Maintains detection history and statistics

### How It Works

1. **Camera Monitoring**: Wyze camera records video to SD card
2. **AI Analysis**: System processes video to detect rodents
3. **Smart Filtering**: Only rodent movements trigger alerts
4. **Instant Alerts**: Notifications sent via SMS/Email/Push
5. **Evidence Collection**: Images saved with timestamps

---

## Getting Started

### Initial Power On

1. **Connect Power**: Plug in the USB-C power adapter to Raspberry Pi
2. **Wait for Boot**: System takes 2-3 minutes to start
3. **Check Status LED** (if available):
   - 🟢 Green: System running normally
   - 🟡 Yellow: System starting up
   - 🔴 Red: Error (check troubleshooting)

### First-Time Setup Checklist

- [ ] System powered on and connected to network
- [ ] Wyze camera recording to SD card
- [ ] Alert notifications configured
- [ ] Test alert received successfully

### Verifying System Operation

Check if the system is running:

```bash
# Via SSH (if you have access):
ssh pi@rodentdetector.local
sudo systemctl status rodent-detection
```

Or check for these indicators:
- Recent images in detection folder
- Alert notifications being received
- Database file growing in size

---

## Daily Operation

### Normal Operation Mode

The system runs automatically 24/7 without user intervention:

1. **Continuous Monitoring**: Processes camera footage automatically
2. **Smart Detection**: AI identifies rodents only
3. **Alert Management**: Sends notifications with 10-minute cooldown
4. **Auto-Cleanup**: Removes old data after 30 days

### What You Need to Do

**Daily**: Nothing! The system runs automatically.

**Weekly**:
- Check that you're receiving alerts (test mode available)
- Verify camera is still recording

**Monthly**:
- Review detection statistics
- Clear false positives if any
- Check storage space

### Camera SD Card Management

#### Option A: Physical SD Card Swap

1. **Remove SD Card** from Wyze camera
2. **Insert into Raspberry Pi** USB reader
3. System automatically processes new footage
4. **Return SD Card** to camera when done

#### Option B: Network Streaming (if configured)

- No manual intervention needed
- System pulls footage automatically

---

## Understanding Alerts

### Alert Format

When a rodent is detected, you'll receive:

```
🐀 RODENT DETECTED
Location: [Camera Name]
Time: 2025-08-20 10:30 PM
Confidence: 85%
Type: Rat
[View Image]
```

### Alert Channels

Depending on configuration, alerts arrive via:

- **SMS**: Text message to configured phone
- **Email**: Message with attached image
- **Push**: Notification to mobile app

### Alert Cooldown

- **Default**: 10 minutes between alerts
- **Purpose**: Prevents notification spam
- **Adjustable**: Can be changed in settings

### What to Do When You Get an Alert

1. **Review the Image**: Check the attached/linked image
2. **Verify Detection**: Confirm it's a rodent
3. **Take Action**: 
   - Set traps in detected area
   - Schedule pest control
   - Check for entry points
4. **Monitor Frequency**: Track if detections increase

---

## Viewing Detection History

### Via Database Query

```bash
# Connect via SSH
ssh pi@rodentdetector.local

# View last 10 detections
sqlite3 data/detections.db "SELECT * FROM detections ORDER BY timestamp DESC LIMIT 10;"

# Count total detections
sqlite3 data/detections.db "SELECT COUNT(*) FROM detections;"

# Detections by date
sqlite3 data/detections.db "SELECT DATE(timestamp), COUNT(*) FROM detections GROUP BY DATE(timestamp);"
```

### Via Image Files

Detection images are saved in: `data/images/`

Format: `detection_YYYYMMDD_HHMMSS.jpg`

Each image shows:
- Rodent with bounding box
- Confidence percentage
- Timestamp
- Detection type

### Statistics Dashboard (if web interface enabled)

Access at: `http://rodentdetector.local:5000`

Shows:
- Total detections
- Detection trends
- Recent images
- System health

---

## Configuration Settings

### Adjustable Parameters

Located in `config/config.yaml`:

#### Detection Sensitivity

```yaml
detection:
  confidence_threshold: 0.55  # Lower = more sensitive (0.3-0.8)
```

- **0.3-0.4**: Very sensitive (more false positives)
- **0.5-0.6**: Balanced (recommended)
- **0.7-0.8**: Less sensitive (may miss some detections)

#### Alert Frequency

```yaml
alerts:
  cooldown_minutes: 10  # Minutes between alerts (5-60)
```

- **5 min**: Frequent updates
- **10 min**: Default balance
- **30-60 min**: Minimal notifications

#### Processing Speed

```yaml
video:
  frame_rate: 1  # Frames per second to analyze
  frame_skip: 30  # Process every Nth frame
```

- Lower values = Less CPU usage
- Higher values = More thorough detection

### Changing Notification Methods

Edit in `config/config.yaml`:

```yaml
alerts:
  enabled_channels:
    - "sms"     # Enable/disable by commenting
    - "email"   
    # - "push"  # Commented = disabled
```

### Time Zone Setting

In `.env` file:
```bash
TIMEZONE=America/New_York  # Your local timezone
```

---

## Maintenance

### Regular Maintenance Tasks

#### Weekly
- **Check Alerts**: Ensure you're receiving notifications
- **Verify Camera**: Confirm recording is active
- **Review Logs**: Check for any errors

#### Monthly
- **Storage Check**: 
  ```bash
  df -h  # Check disk space
  ```
- **Database Cleanup** (automatic, but can force):
  ```bash
  sqlite3 data/detections.db "DELETE FROM detections WHERE timestamp < datetime('now', '-30 days');"
  ```
- **Update Check**: Look for system updates

#### Quarterly
- **Full Backup**: Create system backup
- **Performance Review**: Check detection accuracy
- **Clean Hardware**: Dust off Raspberry Pi

### System Commands

#### Start/Stop System

```bash
# Stop detection
sudo systemctl stop rodent-detection

# Start detection
sudo systemctl start rodent-detection

# Restart system
sudo systemctl restart rodent-detection
```

#### View Logs

```bash
# Recent system logs
sudo journalctl -u rodent-detection -n 50

# Follow live logs
sudo journalctl -u rodent-detection -f

# Check for errors
sudo journalctl -u rodent-detection | grep ERROR
```

#### System Health Check

```bash
# Check service status
sudo systemctl status rodent-detection

# Check CPU/Memory usage
htop

# Check disk space
df -h

# Check detection count
sqlite3 data/detections.db "SELECT COUNT(*) FROM detections WHERE timestamp > datetime('now', '-24 hours');"
```

---

## FAQ

### Q: I'm not receiving alerts

**A:** Check these items:
1. Service is running: `sudo systemctl status rodent-detection`
2. Notifications enabled in config
3. API credentials are correct
4. Network connection is active
5. Cooldown period hasn't blocked alerts

### Q: Too many false alerts

**A:** Adjust settings:
1. Increase confidence threshold (0.6-0.7)
2. Check camera positioning
3. Ensure good lighting
4. Remove moving objects from view

### Q: System is running slow

**A:** Optimize performance:
1. Increase frame_skip value
2. Use ONNX model instead of PyTorch
3. Reduce video resolution
4. Add cooling to Raspberry Pi

### Q: How do I know it's working?

**A:** Check these indicators:
1. Green status in service check
2. Recent entries in database
3. Images being saved to data/images
4. Test mode shows detections

### Q: Can I test the system?

**A:** Yes! Run test mode:
```bash
cd /home/pi/projects/rodent-ai-vision-box
source venv/bin/activate
python scripts/test_detection.py
```

### Q: Storage is full

**A:** Clean up old data:
```bash
# Remove old images
find data/images -type f -mtime +30 -delete

# Clean database
sqlite3 data/detections.db "DELETE FROM detections WHERE timestamp < datetime('now', '-30 days');"

# Check what's using space
du -h --max-depth=1 /home/pi/
```

### Q: How accurate is detection?

**A:** Current performance:
- **Detection Rate**: 85-95% of actual rodents
- **False Positive Rate**: <5% with proper settings
- **Processing Speed**: 1-3 seconds per frame

### Q: Can it detect mice AND rats?

**A:** Yes, the system detects both:
- Large rodents (rats)
- Small rodents (mice)
- Currently grouped as "rat" class
- Species differentiation coming in future update

### Q: What about other animals?

**A:** The AI is trained to ignore:
- Cats and dogs
- Birds
- Humans
- Insects
- Moving shadows

### Q: Power outage recovery?

**A:** System automatically:
- Restarts on power restoration
- Resumes monitoring
- Preserves detection history
- No manual intervention needed

---

## Quick Reference Card

### Essential Commands

```bash
# SERVICE CONTROL
sudo systemctl start rodent-detection    # Start
sudo systemctl stop rodent-detection     # Stop
sudo systemctl restart rodent-detection  # Restart
sudo systemctl status rodent-detection   # Check status

# MONITORING
sudo journalctl -u rodent-detection -f   # Watch logs
htop                                      # System resources
df -h                                     # Disk space

# DATABASE
sqlite3 data/detections.db ".tables"     # List tables
sqlite3 data/detections.db "SELECT COUNT(*) FROM detections;"  # Count

# TESTING
python test_system.py                    # Run tests
python scripts/test_notification.py      # Test alerts
```

### Status Indicators

- ✅ **Running**: Service active, logs updating
- ⚠️ **Warning**: High CPU, low disk space
- ❌ **Error**: Service stopped, no detections

### Support Contacts

- **Technical Issues**: Check logs first
- **Hardware Problems**: Verify connections
- **Detection Issues**: Adjust sensitivity
- **Alert Problems**: Check credentials

---

## Safety & Best Practices

1. **Keep System Updated**: Regular software updates
2. **Secure Access**: Change default passwords
3. **Regular Backups**: Monthly configuration backup
4. **Monitor Performance**: Weekly health checks
5. **Clean Camera Lens**: Monthly cleaning
6. **Check Mounting**: Ensure camera is secure
7. **Protect from Elements**: Keep electronics dry
8. **Professional Pest Control**: Use detections to guide treatment

---

## Appendix: Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| E001 | Camera not found | Check SD card mount |
| E002 | Model load failed | Verify model file exists |
| E003 | Network error | Check internet connection |
| E004 | Database error | Check disk space |
| E005 | Notification failed | Verify API credentials |
| E006 | High temperature | Add cooling to Pi |
| E007 | Low memory | Restart service |
| E008 | Disk full | Clean old files |

---

*User Manual Version 1.0 - August 2025*
*For Rodent AI Vision Box System*