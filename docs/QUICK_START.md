# 🚀 Quick Start Guide - Rodent AI Vision Box

## ✅ Your System is Ready!

The trained YOLOv8 model is already in the `models/` directory:
- `best.pt` - PyTorch model (52MB)
- `best.onnx` - ONNX model (99MB) for better Raspberry Pi performance

## 📋 Setup Steps (5 minutes)

### 1️⃣ Add Twilio Credentials

Copy `.env.example` to `.env` and add your Twilio credentials:

```bash
cp .env.example .env
nano .env
```

**Required fields to update:**
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+1234567890  # Your Twilio number
ALERT_PHONE_NUMBER=+0987654321  # Your phone to receive alerts
```

### 2️⃣ Install on Raspberry Pi

Transfer this folder to your Raspberry Pi and run:

```bash
# On Raspberry Pi
cd rodent-ai-vision-box
chmod +x setup.sh
./setup.sh
```

### 3️⃣ Mount Wyze SD Card

```bash
# Create mount point
sudo mkdir -p /mnt/wyze_sd

# Mount SD card (replace /dev/sda1 with your SD card device)
sudo mount /dev/sda1 /mnt/wyze_sd

# Make it permanent (optional)
echo "/dev/sda1 /mnt/wyze_sd auto defaults 0 0" | sudo tee -a /etc/fstab
```

### 4️⃣ Start the System

```bash
# Start the service
sudo systemctl start rodent-detection

# Enable auto-start on boot
sudo systemctl enable rodent-detection

# Check status
sudo systemctl status rodent-detection
```

### 5️⃣ Monitor Logs

```bash
# View real-time logs
sudo journalctl -u rodent-detection -f
```

## 📱 Alert Format

When a rat is detected, you'll receive an SMS:

```
🚨 RODENT ALERT! Norway Rat detected 
at 3:45 PM with 85% confidence.
```

**Note:** Roof rat detection has lower accuracy (15%) due to training data limitations.

## 🔧 Configuration

### Adjust Detection Sensitivity

Edit `config/config.yaml`:
```yaml
detection:
  confidence_threshold: 0.25  # Lower = more sensitive (more detections)
```

### Change Alert Cooldown

To prevent spam, alerts have a 10-minute cooldown. Change in `config/config.yaml`:
```yaml
alerts:
  cooldown_minutes: 10  # Minutes between alerts
```

## 🐀 Model Performance

- **Overall Detection:** Good (67% recall)
- **Norway Rats:** Excellent (77% accuracy) ✅
- **Roof Rats:** Poor (15% accuracy) ⚠️
- **Best Use:** General rat presence detection

The model reliably detects when rats are present but may confuse the specific type.

## 🆘 Troubleshooting

### No Detections
1. Check SD card is mounted: `ls /mnt/wyze_sd`
2. Lower confidence threshold in config
3. Check logs: `sudo journalctl -u rodent-detection -f`

### Twilio Not Sending
1. Verify credentials in `.env`
2. Check account balance at console.twilio.com
3. Verify phone numbers are in E.164 format (+1234567890)

### Service Won't Start
1. Check Python packages: `source venv/bin/activate && python test_system.py`
2. Verify model files exist: `ls models/`
3. Check permissions: `chmod -R 755 .`

## 📊 System Requirements

- Raspberry Pi 4/5 (4GB+ RAM recommended)
- 64GB SD card
- Wyze camera with SD card recording
- Internet connection for Twilio

## 🎯 What Happens

1. System monitors Wyze SD card for new video/images
2. Runs YOLOv8 model on each frame
3. When rat detected:
   - Saves annotated image with bounding box
   - Sends Twilio SMS alert
   - Waits 10 minutes before next alert (cooldown)
4. Continues monitoring 24/7

## ✨ Ready to Go!

Once you add Twilio credentials and start the service, the system will:
- ✅ Monitor continuously
- ✅ Detect rats with 67% accuracy
- ✅ Send SMS alerts via Twilio
- ✅ Save detection images
- ✅ Auto-start on boot

**Support:** Check logs with `sudo journalctl -u rodent-detection -f` for any issues.