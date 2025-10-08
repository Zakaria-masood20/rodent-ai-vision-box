# 🚀 Quick Start Guide - 15 Minutes to Deployment

Get your Rodent AI Vision Box running in 15 minutes or less.

## Prerequisites ✅

- Raspberry Pi 5 (8GB RAM)
- MicroSD card (64GB) with Raspberry Pi OS
- Camera (Wyze or USB)
- Internet connection
- SSH access to your Pi

## Step 1: Clone & Setup (3 minutes)

```bash
# SSH into your Raspberry Pi
ssh pi@[your-pi-ip]

# Clone the repository
git clone [repository-url]
cd rodent-ai-vision-box

# Run automated setup
sudo ./setup.sh
```

The setup script will:
- Install Python 3.9+
- Install all dependencies
- Configure system services
- Set up directories

## Step 2: Configure Credentials (2 minutes)

```bash
# Copy production credentials
cp .env.production .env

# Verify EmailJS settings (already configured)
cat .env | grep EMAILJS
```

Your `.env` should contain:
```
EMAILJS_SERVICE_ID=service_2q7m7pm
EMAILJS_TEMPLATE_ID=template_0q4z7y8
EMAILJS_PUBLIC_KEY=Cx4zjcLaDjfhS2ssD
EMAILJS_TO_EMAIL=ratproject111@gmail.com
```

## Step 3: Configure Camera (3 minutes)

Edit the configuration file:
```bash
nano config/config.yaml
```

Choose your camera source:
```yaml
camera:
  # Option 1: SD Card
  source: "sd_card"
  sd_mount_path: "/mnt/wyze_sd"
  
  # Option 2: RTSP Stream
  # source: "rtsp"
  # rtsp_url: "rtsp://192.168.1.100:554/live"
  
  # Option 3: USB Camera
  # source: "usb"
  # device_id: 0
```

## Step 4: Test Components (2 minutes)

```bash
# Test detection system
python3 utils/test_system.py

# Test email notifications
python3 utils/test_email.py
```

You should see:
```
✅ Model loaded successfully
✅ Detection engine ready
✅ Email sent successfully
```

## Step 5: Start the Service (2 minutes)

```bash
# Enable auto-start on boot
sudo systemctl enable rodent-detection

# Start the service
sudo systemctl start rodent-detection

# Verify it's running
sudo systemctl status rodent-detection
```

You should see: `Active: active (running)`

## Step 6: Verify Operation (3 minutes)

```bash
# Watch live logs
sudo journalctl -u rodent-detection -f

# Check for detections (after a few minutes)
ls -la data/images/

# Test with a video (optional)
python3 src/main.py --test-video Test_videos/T1.mp4
```

## 🎉 Success Indicators

✅ Service shows "active (running)"  
✅ Logs show "Rodent Detection System started"  
✅ Email test sends successfully  
✅ No error messages in logs  

## 📧 What to Expect

When a rodent is detected:
1. System captures the frame
2. AI analyzes for rodents
3. If confidence > 45%, alert triggers
4. Email sent to ratproject111@gmail.com
5. Image saved in data/images/
6. Detection logged in database

## ⚡ Quick Commands

```bash
# Stop system
sudo systemctl stop rodent-detection

# Restart system
sudo systemctl restart rodent-detection

# View last 50 log entries
sudo journalctl -u rodent-detection -n 50

# Check detection count
sqlite3 data/detections.db "SELECT COUNT(*) FROM detections;"
```

## 🔧 Quick Adjustments

### Too many false alerts?
Edit `config/config.yaml`:
```yaml
detection:
  confidence_threshold: 0.55  # Increase from 0.45
```

### Not detecting rodents?
```yaml
detection:
  confidence_threshold: 0.35  # Decrease from 0.45
```

### Too many emails?
```yaml
alerts:
  cooldown_minutes: 30  # Increase from 10
```

## ❓ Need Help?

1. Check logs: `sudo journalctl -u rodent-detection -n 100`
2. Test components: `python3 utils/test_system.py`
3. Review [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
4. Check [Full Documentation](README.md)

---

**Time to deployment: 15 minutes**  
**Current status: Production Ready**  
**Email alerts going to: ratproject111@gmail.com**