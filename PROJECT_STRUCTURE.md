# Rodent AI Vision Box - Project Structure

## 📁 Directory Layout

```
rodent-ai-vision-box/
│
├── 📄 Core Files
│   ├── README.md               # Main documentation
│   ├── QUICK_START.md         # 15-minute setup guide
│   ├── LICENSE                # MIT License
│   ├── requirements.txt       # Python dependencies
│   ├── setup.sh              # Automated setup script
│   └── .env.production       # Production credentials
│
├── 📦 src/                   # Main application code
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── config_manager.py    # Configuration handling
│   ├── video_ingestion.py   # Camera/video processing
│   ├── detection_engine.py  # AI rodent detection
│   ├── alert_engine.py      # Alert logic and cooldown
│   ├── notification_service.py # Email notifications
│   ├── database.py          # SQLite storage
│   └── logger.py            # Logging system
│
├── 🎯 models/               # AI Models
│   └── best.onnx           # Optimized YOLO model (98MB)
│
├── ⚙️ config/               # Configuration
│   └── config.yaml         # System settings
│
├── 🔧 scripts/              # Deployment scripts
│   ├── setup_raspberry_pi.sh    # Pi setup
│   ├── deploy.sh                # Deployment helper
│   ├── rodent-detection.service # Systemd service
│   └── create_sd_image.sh      # SD card prep
│
├── 📊 data/                 # Runtime data
│   ├── logs/               # System logs
│   ├── images/             # Detection images
│   └── detections/         # Detection database
│
├── 📚 docs/                 # Documentation
│   ├── DEPLOYMENT.md       # Deployment guide
│   ├── TROUBLESHOOTING.md  # Problem solving
│   ├── EMAILJS_SETUP.md    # Email configuration
│   └── USER_GUIDE_SIMPLE.md # User manual
│
├── 🧪 utils/                # Utilities
│   ├── test_system.py      # System verification
│   └── test_email.py       # Email testing
│
└── 📦 archive/              # Archived test files
    ├── test_scripts/       # Development test scripts
    └── test_results/       # Test outputs
```

## 🚀 Key Files

### Production Files
- `src/main.py` - Main application entry point
- `.env.production` - EmailJS credentials (DO NOT COMMIT)
- `config/config.yaml` - Detection and system settings
- `models/best.onnx` - Trained rodent detection model

### Setup Files
- `setup.sh` - One-click installation script
- `scripts/setup_raspberry_pi.sh` - Raspberry Pi configuration
- `scripts/rodent-detection.service` - Auto-start service

### Testing Files
- `utils/test_system.py` - Verify system components
- `utils/test_email.py` - Test email notifications

## 🎯 Clean Structure Benefits

1. **Organized** - Clear separation of concerns
2. **Production-Ready** - No test clutter in main directories
3. **Maintainable** - Easy to find and update files
4. **Deployable** - Clean structure for client handover
5. **Professional** - Industry-standard layout

## 📋 File Count

- **Core Python modules**: 8 files
- **Configuration files**: 3 files
- **Documentation**: 8 files
- **Scripts**: 5 files
- **Total production files**: ~25 files (excluding archives)

## 🔐 Security Notes

- `.env.production` contains sensitive credentials
- Never commit credentials to version control
- Use `.gitignore` to exclude sensitive files
- Archive contains test files (can be deleted)

## 🏃 Quick Commands

```bash
# Run the system
python3 src/main.py

# Test email
python3 utils/test_email.py

# Check system
python3 utils/test_system.py

# Start service
sudo systemctl start rodent-detection

# View logs
sudo journalctl -u rodent-detection -f
```

## ✅ Ready for Deployment

The project is now:
- Clean and organized
- Production-ready
- Well-documented
- Easy to deploy
- Professional presentation