#!/usr/bin/env python3
"""
Test notification services
Usage: python test_notifications.py [sms|email|push|all]
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_manager import ConfigManager
from src.notification_service import NotificationService
from src.alert_engine import AlertEvent
from src.detection_engine import Detection
from datetime import datetime


async def test_sms(notification_service):
    """Test SMS notification"""
    print("\n🔍 Testing SMS notification...")
    
    # Create mock detection
    detection = Detection(
        class_name="rat",
        confidence=0.85,
        bbox=(100, 100, 200, 200),
        timestamp=datetime.now().timestamp()
    )
    
    # Create alert event
    alert_event = AlertEvent(
        detection=detection,
        image_path="test_image.jpg",
        priority="high"
    )
    
    try:
        result = await notification_service.send_sms(alert_event)
        if result:
            print("✅ SMS test successful!")
        else:
            print("❌ SMS test failed - check credentials")
    except Exception as e:
        print(f"❌ SMS test error: {e}")


async def test_email(notification_service):
    """Test email notification"""
    print("\n📧 Testing email notification...")
    
    # Create mock detection
    detection = Detection(
        class_name="rat",
        confidence=0.92,
        bbox=(150, 150, 250, 250),
        timestamp=datetime.now().timestamp()
    )
    
    # Create alert event
    alert_event = AlertEvent(
        detection=detection,
        image_path="test_image.jpg",
        priority="high"
    )
    
    try:
        result = await notification_service.send_email(alert_event)
        if result:
            print("✅ Email test successful!")
        else:
            print("❌ Email test failed - check credentials")
    except Exception as e:
        print(f"❌ Email test error: {e}")


async def test_push(notification_service):
    """Test push notification"""
    print("\n📱 Testing push notification...")
    
    # Create mock detection
    detection = Detection(
        class_name="rat",
        confidence=0.78,
        bbox=(200, 200, 300, 300),
        timestamp=datetime.now().timestamp()
    )
    
    # Create alert event
    alert_event = AlertEvent(
        detection=detection,
        image_path="test_image.jpg",
        priority="high"
    )
    
    try:
        result = await notification_service.send_push(alert_event)
        if result:
            print("✅ Push notification test successful!")
        else:
            print("❌ Push notification test failed - check credentials")
    except Exception as e:
        print(f"❌ Push notification test error: {e}")


async def main():
    """Main test function"""
    print("=" * 50)
    print("NOTIFICATION SERVICE TEST")
    print("=" * 50)
    
    # Get test type from command line
    test_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    # Load configuration
    config = ConfigManager()
    
    # Initialize notification service
    notification_service = NotificationService(config)
    
    # Check which channels are enabled
    enabled_channels = config.get('alerts.enabled_channels', [])
    print(f"\nEnabled channels: {enabled_channels}")
    
    # Run tests based on argument
    if test_type == "sms" or test_type == "all":
        if "sms" in enabled_channels:
            await test_sms(notification_service)
        else:
            print("\n⚠️  SMS not enabled in config")
    
    if test_type == "email" or test_type == "all":
        if "email" in enabled_channels:
            await test_email(notification_service)
        else:
            print("\n⚠️  Email not enabled in config")
    
    if test_type == "push" or test_type == "all":
        if "push" in enabled_channels:
            await test_push(notification_service)
        else:
            print("\n⚠️  Push notifications not enabled in config")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
    
    # Test summary
    print("\nIMPORTANT:")
    print("- If tests failed, check your .env file for correct API credentials")
    print("- Ensure the notification channels are enabled in config.yaml")
    print("- Check network connectivity")
    print("- Verify API account status (credits, limits, etc.)")


if __name__ == "__main__":
    asyncio.run(main())