# Rodent Detection System

An AI-powered rodent detection system using YOLOv5 on Raspberry Pi to monitor Wyze camera feeds and send real-time alerts.

## Features

- Real-time rodent detection (Roof Rats, Norway Rats, Mice)
- Wyze camera integration (SD card, RTSP, Cloud API)
- Multi-channel notifications (SMS, Email, Push)
- Intelligent alert cooldown to prevent spam
- Detection logging with SQLite database
- Automatic cleanup of old data
- Headless operation on Raspberry Pi

## System Requirements

### Hardware
- Raspberry Pi 5 (8GB RAM recommended)
- MicroSD card (64GB minimum)
- Wyze v4 camera
- Stable internet connection

### Software
- Raspberry Pi OS Lite (64-bit)
- Python 3.9+
- CUDA support (optional, for GPU acceleration)

## Quick Start

### 1. Hardware Setup

1. Flash Raspberry Pi OS to SD card
2. Connect Raspberry Pi to network
3. SSH into Raspberry Pi

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/rodent-detection.git
cd rodent-ai-vision-box

# Run setup script
chmod +x scripts/setup_raspberry_pi.sh
./scripts/setup_raspberry_pi.sh
```

### 3. Configuration

1. Copy environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_FROM_NUMBER=+1234567890
ALERT_PHONE_NUMBER=+0987654321
```

3. Configure camera source in `config/config.yaml`:
```yaml
camera:
  source: "sd_card"  # or "rtsp" or "cloud_api"
  sd_mount_path: "/mnt/wyze_sd"
```

### 4. Start the System

```bash
# Start the service
sudo systemctl start rodent-detection

# Check status
sudo systemctl status rodent-detection

# View logs
sudo journalctl -u rodent-detection -f
```

## Configuration Options

### Camera Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `camera.type` | Camera model | wyze_v4 |
| `camera.source` | Video source | sd_card |
| `camera.sd_mount_path` | SD card mount point | /mnt/wyze_sd |

### Detection Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `detection.confidence_threshold` | Minimum confidence | 0.55 |
| `detection.nms_threshold` | Non-max suppression | 0.4 |
| `detection.classes` | Target classes | [roof_rat, norway_rat, mouse] |

### Alert Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `alerts.cooldown_minutes` | Minutes between alerts | 10 |
| `alerts.enabled_channels` | Active notification channels | [sms] |

## API Credentials

### Twilio (SMS)
1. Sign up at https://www.twilio.com
2. Get Account SID and Auth Token
3. Purchase a phone number
4. Add credentials to `.env`

### Pushover (Push Notifications)
1. Sign up at https://pushover.net
2. Create an application
3. Get API token and user key
4. Add credentials to `.env`

### Email (SMTP)
1. Enable 2FA on your email account
2. Generate app-specific password
3. Add SMTP settings to `.env`

## Monitoring

### System Status
```bash
# Check service status
sudo systemctl status rodent-detection

# View real-time logs
sudo journalctl -u rodent-detection -f

# Check detection statistics
sqlite3 data/detections.db "SELECT class_name, COUNT(*) FROM detections GROUP BY class_name;"
```

### Detection Images
Detection images are saved to `data/images/` with timestamps and bounding boxes.

## Troubleshooting

### Camera Not Found
1. Check SD card is mounted: `ls /mnt/wyze_sd`
2. Verify mount permissions: `sudo chmod 755 /mnt/wyze_sd`

### No Detections
1. Check camera feed is working
2. Verify model is loaded: Check logs for "Model loaded"
3. Adjust confidence threshold in config

### Alerts Not Sending
1. Verify API credentials in `.env`
2. Check network connectivity
3. Review notification logs

## Model Training

To train a custom rodent detection model:

1. Collect rodent images (500+ per class)
2. Label using Roboflow or CVAT
3. Train with YOLOv5:
```bash
python train.py --data rodent.yaml --weights yolov5s.pt --epochs 100
```
4. Replace model in `models/yolov5s_rodent.pt`

## Development

### Project Structure
```
rodent_detection/
├── src/
│   ├── main.py              # Main application
│   ├── config_manager.py    # Configuration handling
│   ├── video_ingestion.py   # Video processing
│   ├── detection_engine.py  # YOLOv5 detection
│   ├── alert_engine.py      # Alert logic
│   ├── notification_service.py # Notifications
│   └── database.py          # Database models
├── config/
│   └── config.yaml          # Configuration file
├── scripts/
│   ├── setup_raspberry_pi.sh
│   └── download_model.sh
├── data/
│   ├── logs/               # Log files
│   └── images/             # Detection images
└── models/                 # YOLOv5 models
```

## 🧪 Testing

### Test Components
```bash
# Test email notifications
python test_emailjs.py

# Test detection on sample image
python test_detection.py

# Run all tests
python -m pytest tests/
```

## License

MIT License - see LICENSE file

## Support

For issues and feature requests, please open a GitHub issue.
