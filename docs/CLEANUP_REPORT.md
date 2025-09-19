# Project Cleanup Report - Rodent AI Vision Box

## ✅ **ESSENTIAL FILES (KEEP)**

### Core Application Files
- `src/main.py` - Main application entry point
- `src/detection_engine.py` - YOLOv8 detection logic
- `src/notification_service.py` - Twilio SMS service
- `src/alert_engine.py` - Alert cooldown logic
- `src/video_ingestion.py` - Wyze SD card monitoring
- `src/config_manager.py` - Configuration loader
- `src/database.py` - Detection logging
- `src/logger.py` - Logging setup
- `src/__init__.py` - Package initialization

### Configuration
- `config/config.yaml` - System configuration
- `.env.example` - Twilio credentials template
- `requirements.txt` - Python dependencies

### Models
- `models/best.pt` - Trained PyTorch model
- `models/best.onnx` - Optimized ONNX model

### Scripts
- `setup.sh` - Installation script
- `scripts/rodent-detection.service` - Systemd service
- `test_detection.py` - System verification
- `test_twilio.py` - SMS testing

### Documentation
- `README.md` - Project documentation
- `QUICK_START.md` - Quick setup guide

## 🗑️ **OPTIONAL/REMOVABLE FILES**

### Can Remove (Not Essential):
1. **`src/detection_engine_multispecies.py`** - Alternative detection engine (not used)
   - Remove if only detecting rats

2. **`src/commercial/license_manager.py`** - Commercial licensing (not needed)
   - Remove entire `commercial/` folder

3. **`scripts/test_notifications.py`** - Redundant (we have test_twilio.py)
   
4. **`scripts/test_video_detection.py`** - Testing script (not needed for production)

5. **`docker-compose.yml` & `Dockerfile`** - Docker files (not using Docker)
   - Remove if deploying directly on Raspberry Pi

6. **`tests/` folder** - Unit tests (optional for production)

7. **`docs/` folder** - Additional documentation (optional)

8. **`.gitignore.recommended`** - Duplicate gitignore file

9. **`.DS_Store`** - macOS system file (auto-generated)

10. **`data/` folder contents** - Will be created automatically
    - Keep the folder, but can clear contents

## 📝 **CLEANUP COMMANDS**

To remove unnecessary files:

```bash
# Remove optional files
rm -f src/detection_engine_multispecies.py
rm -rf src/commercial/
rm -f scripts/test_notifications.py
rm -f scripts/test_video_detection.py
rm -f docker-compose.yml Dockerfile
rm -rf tests/
rm -rf docs/
rm -f .gitignore.recommended
rm -f .DS_Store

# Clear data folder but keep structure
rm -f data/logs/*
rm -f data/images/*
```

## 📦 **MINIMAL DEPLOYMENT PACKAGE**

For the cleanest deployment, you only need:

```
rodent-ai-vision-box/
├── models/
│   ├── best.pt
│   └── best.onnx
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── detection_engine.py
│   ├── notification_service.py
│   ├── alert_engine.py
│   ├── video_ingestion.py
│   ├── config_manager.py
│   ├── database.py
│   └── logger.py
├── config/
│   └── config.yaml
├── scripts/
│   └── rodent-detection.service
├── data/               # Empty folders
│   ├── logs/
│   └── images/
├── .env.example
├── requirements.txt
├── setup.sh
├── test_detection.py
├── test_twilio.py
├── README.md
└── QUICK_START.md
```

## 💡 **RECOMMENDATION**

Keep all files for now - they don't affect performance. After successful deployment and testing, you can remove the optional files listed above to reduce clutter.

**Total size reduction if cleaned: ~10-15MB** (mostly from removing docs and tests)