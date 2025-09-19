# Changelog

All notable changes to the Rodent AI Vision Box project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-09-19

### Added
- Initial release of Rodent AI Vision Box
- YOLOv8-based rodent detection system
- Support for Norway rat and Roof rat classification
- Real-time video processing from Wyze cameras
- Twilio SMS integration for instant alerts
- 10-minute cooldown between alerts to prevent spam
- ONNX model optimization for edge deployment
- Comprehensive logging system
- Docker containerization support
- Systemd service for auto-start on boot
- Professional CI/CD pipeline with GitHub Actions
- Complete test suite with pytest
- User-friendly documentation for non-technical users
- Quick reference card for daily operations

### Performance
- Norway rat detection: 77.1% mAP
- Roof rat detection: 15.0% mAP (known limitation)
- Overall detection accuracy: 67%
- Processing speed: ~30 FPS on Raspberry Pi 4

### Technical Stack
- Python 3.8+
- YOLOv8 (Ultralytics)
- ONNX Runtime for inference
- OpenCV for video processing
- Twilio for SMS notifications
- PyYAML for configuration
- Docker for containerization

### Documentation
- Complete technical documentation
- Non-technical user guide
- Quick reference card
- API documentation
- Deployment guide

### Known Issues
- Roof rat classification accuracy is limited (15% mAP)
- System works best with good lighting conditions
- Requires stable internet for SMS alerts

## [0.9.0] - 2024-09-01 (Pre-release)

### Added
- Beta testing version
- Initial model training on 2,109 images
- Basic detection functionality
- Preliminary Twilio integration

### Changed
- Improved model architecture
- Enhanced data augmentation

### Fixed
- YOLO annotation format issues
- Video stream stability problems

## [0.5.0] - 2024-08-15 (Alpha)

### Added
- Initial prototype
- Basic YOLOv8 integration
- Simple alert system

### Notes
- Internal testing only
- Limited functionality

---

## Roadmap

### [1.1.0] - Planned
- Improved roof rat detection accuracy
- Web dashboard for monitoring
- Email notification support
- Cloud backup integration

### [1.2.0] - Future
- Multi-camera support
- Advanced analytics dashboard
- Machine learning model updates
- Mobile app integration

### [2.0.0] - Long-term
- AI behavior analysis
- Predictive alerts
- Integration with pest control systems
- Advanced reporting features

---

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Authors

- AI Vision Systems - Initial work

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.