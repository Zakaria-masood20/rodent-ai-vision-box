# Quick Start Guide ⚡

Get the Rodent AI Vision Box up and running in 15 minutes!

## Prerequisites ✅
- Raspberry Pi 5 with Raspberry Pi OS installed
- Internet connection configured
- Wyze camera set up
- SSH access to Raspberry Pi

## 5-Minute Setup 🚀

### Step 1: Clone & Setup (5 minutes)
```bash
# SSH into your Raspberry Pi
ssh pi@raspberrypi.local

# Clone the repository
git clone [repository-url] rodent-ai-vision-box
cd rodent-ai-vision-box

# Run automatic setup
chmod +x setup.sh
sudo ./setup.sh
```

### Step 2: Configure Credentials (2 minutes)
```bash
# Use the production configuration
cp .env.production .env

# Or if you need to edit:
nano .env
```

**The .env.production file already contains:**
- ✅ EmailJS credentials configured
- ✅ Email recipient: ratproject111@gmail.com
- ✅ All system settings optimized

### Step 3: Start the System (1 minute)
```bash
# Enable and start the service
sudo systemctl enable rodent-detection
sudo systemctl start rodent-detection
```

### Step 4: Verify It's Working (2 minutes)
```bash
# Check service status
sudo systemctl status rodent-detection

# Test email notifications
source venv/bin/activate
python test_emailjs.py
```

**You should receive a test email at ratproject111@gmail.com** ✉️

## That's It! 🎉

Your Rodent AI Vision Box is now:
- ✅ Running automatically
- ✅ Monitoring for rodents
- ✅ Sending email alerts
- ✅ Starting on boot

## Monitor the System

### View Live Logs
```bash
sudo journalctl -u rodent-detection -f
```

### Check Recent Detections
```bash
sqlite3 data/detections.db "SELECT datetime, class_name, confidence FROM detections ORDER BY datetime DESC LIMIT 5;"
```

### System Health
```bash
# Quick status check
systemctl is-active rodent-detection
```

## What Happens Next?

1. **Place Camera**: Position Wyze camera at rodent entry points
2. **Wait for Detections**: System processes video at 1 FPS
3. **Receive Alerts**: Get emails when rodents detected
4. **Monitor**: Check logs and adjust sensitivity if needed

## Quick Commands Reference

| Task | Command |
|------|---------|
| Start service | `sudo systemctl start rodent-detection` |
| Stop service | `sudo systemctl stop rodent-detection` |
| Restart service | `sudo systemctl restart rodent-detection` |
| View logs | `sudo journalctl -u rodent-detection -f` |
| Test email | `python test_emailjs.py` |
| Check detections | `ls data/images/` |

## Troubleshooting Quick Fixes

### No Emails?
```bash
python test_emailjs.py
# Check spam folder
# Verify EmailJS dashboard
```

### Service Not Running?
```bash
sudo systemctl restart rodent-detection
journalctl -xe
```

### Camera Issues?
```bash
# For SD card
ls /mnt/wyze_sd

# For RTSP
ping [camera-ip]
```

## Need More Help?

- 📖 [Full Documentation](README.md)
- 🔧 [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- 📧 [EmailJS Setup](docs/EMAILJS_SETUP.md)
- 🚀 [Production Deployment](PRODUCTION_DEPLOYMENT.md)

---

**System is Ready!** The AI is now monitoring for rodents 24/7 and will send instant email alerts to ratproject111@gmail.com 🐀📧