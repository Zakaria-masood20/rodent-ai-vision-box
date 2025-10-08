#!/usr/bin/env python3
"""
Test script for EmailJS notification service.
This script tests the EmailJS integration for the Rodent Detection System.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

def test_emailjs_direct():
    """Test EmailJS API directly without using the notification service."""
    
    print("=" * 60)
    print("EmailJS Direct API Test")
    print("=" * 60)
    
    # Get EmailJS credentials from environment
    service_id = os.getenv('EMAILJS_SERVICE_ID')
    template_id = os.getenv('EMAILJS_TEMPLATE_ID')
    public_key = os.getenv('EMAILJS_PUBLIC_KEY')
    private_key = os.getenv('EMAILJS_PRIVATE_KEY')
    to_email = os.getenv('EMAILJS_TO_EMAIL')
    
    # Check if credentials are set
    if not all([service_id, template_id, public_key]):
        print("❌ EmailJS credentials not found in .env file!")
        print("\nPlease set the following environment variables:")
        print("  - EMAILJS_SERVICE_ID")
        print("  - EMAILJS_TEMPLATE_ID")
        print("  - EMAILJS_PUBLIC_KEY")
        print("  - EMAILJS_TO_EMAIL")
        return False
    
    print(f"Service ID: {service_id}")
    print(f"Template ID: {template_id}")
    print(f"Public Key: {public_key[:10]}..." if public_key else "Not set")
    print(f"Private Key: {'Set' if private_key else 'Not set'}")
    print(f"To Email: {to_email}")
    print()
    
    # Prepare test data
    template_params = {
        'to_email': to_email,
        'from_name': 'Rodent Detection System (Test)',
        'rodent_type': 'Norway Rat',
        'detection_time': datetime.now().strftime('%Y-%m-%d %I:%M:%S %p'),
        'confidence': '95%',
        'message': '🚨 TEST ALERT: This is a test of the EmailJS notification system. If you received this email, the integration is working correctly!',
        'image_data': '',  # No image for test
        'image_name': ''
    }
    
    # Send request to EmailJS with browser-like headers
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:3000',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    data = {
        'service_id': service_id,
        'template_id': template_id,
        'user_id': public_key,
        'template_params': template_params
    }
    
    # Add private key if available
    if private_key:
        data['accessToken'] = private_key
    
    print("Sending test email via EmailJS...")
    
    try:
        response = requests.post(
            'https://api.emailjs.com/api/v1.0/email/send',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            print("✅ Email sent successfully!")
            print(f"   Response: {response.text}")
            return True
        else:
            print(f"❌ Failed to send email!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


async def test_emailjs_with_service():
    """Test EmailJS using the notification service."""
    
    print("\n" + "=" * 60)
    print("EmailJS Notification Service Test")
    print("=" * 60)
    
    try:
        # Add src to path to import modules
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from src.notification_service import EmailJSNotification
        from src.alert_engine import AlertEvent, Detection
        
        # Create mock detection
        detection = Detection(
            class_name='norway_rat',
            confidence=0.92,
            bbox=[100, 100, 200, 200],
            timestamp=datetime.now().timestamp(),
            datetime=datetime.now()
        )
        
        # Create mock alert event
        alert_event = AlertEvent(
            detection=detection,
            image_path='data/images/test_image.jpg'  # This doesn't need to exist for testing
        )
        
        # Load EmailJS config
        config = {
            'service_id': os.getenv('EMAILJS_SERVICE_ID'),
            'template_id': os.getenv('EMAILJS_TEMPLATE_ID'),
            'public_key': os.getenv('EMAILJS_PUBLIC_KEY'),
            'private_key': os.getenv('EMAILJS_PRIVATE_KEY'),
            'to_email': os.getenv('EMAILJS_TO_EMAIL'),
            'from_name': 'Rodent Detection System'
        }
        
        # Create EmailJS notification instance
        emailjs = EmailJSNotification(config)
        
        print("Sending alert via EmailJS notification service...")
        success = await emailjs.send_alert(alert_event)
        
        if success:
            print("✅ Alert sent successfully via notification service!")
            return True
        else:
            print("❌ Failed to send alert via notification service!")
            return False
            
    except ImportError as e:
        print(f"⚠️  Could not import notification service modules: {e}")
        print("   Skipping service test...")
        return False
    except Exception as e:
        print(f"❌ Error in service test: {e}")
        return False


async def main():
    """Main test function."""
    
    print("\n🔬 Testing EmailJS Integration for Rodent Detection System\n")
    
    # Test 1: Direct API test
    direct_success = test_emailjs_direct()
    
    # Test 2: Service integration test
    service_success = await test_emailjs_with_service()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Direct API Test: {'✅ Passed' if direct_success else '❌ Failed'}")
    print(f"Service Integration Test: {'✅ Passed' if service_success else '❌ Failed'}")
    
    if direct_success:
        print("\n✅ EmailJS is working! Check your email inbox.")
        print("\n📝 Next steps:")
        print("1. Create an email template on EmailJS dashboard with these variables:")
        print("   - {{to_email}}")
        print("   - {{from_name}}")
        print("   - {{rodent_type}}")
        print("   - {{detection_time}}")
        print("   - {{confidence}}")
        print("   - {{message}}")
        print("2. Update your .env file with the correct credentials")
        print("3. Enable 'emailjs' in config.yaml under alerts.enabled_channels")
        print("4. Run the main detection system to test with real detections")
    else:
        print("\n❌ EmailJS test failed. Please check:")
        print("1. Your EmailJS credentials in the .env file")
        print("2. Your EmailJS service and template are properly configured")
        print("3. Your internet connection is working")


if __name__ == "__main__":
    asyncio.run(main())