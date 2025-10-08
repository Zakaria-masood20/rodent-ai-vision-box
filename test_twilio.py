#!/usr/bin/env python3
"""
Twilio SMS Test Script
Tests if Twilio credentials are working correctly
"""

import os
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime

# Load environment variables
load_dotenv()

def test_twilio_connection():
    """Test Twilio SMS functionality"""
    
    # Get credentials from .env file
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_FROM_NUMBER')
    to_number = os.getenv('ALERT_PHONE_NUMBER')
    
    # Check if credentials exist
    if not all([account_sid, auth_token, from_number, to_number]):
        print("❌ Missing Twilio credentials in .env file!")
        print("\nPlease ensure these are set in .env:")
        print("  - TWILIO_ACCOUNT_SID")
        print("  - TWILIO_AUTH_TOKEN")
        print("  - TWILIO_FROM_NUMBER")
        print("  - ALERT_PHONE_NUMBER")
        return False
    
    try:
        # Initialize Twilio client
        print("📱 Connecting to Twilio...")
        client = Client(account_sid, auth_token)
        
        # Send test message
        print(f"📤 Sending test SMS from {from_number} to {to_number}...")
        
        message = client.messages.create(
            body=f"🐀 Rodent Detection System Test\n"
                 f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"Status: System is working correctly! ✅",
            from_=from_number,
            to=to_number
        )
        
        print(f"✅ SMS sent successfully!")
        print(f"   Message SID: {message.sid}")
        print(f"   Status: {message.status}")
        print(f"\n📲 Check {to_number} for the test message!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send SMS: {str(e)}")
        print("\nPossible issues:")
        print("  1. Invalid Account SID or Auth Token")
        print("  2. Phone numbers not in correct format (+1234567890)")
        print("  3. No Twilio credit balance")
        print("  4. Phone number not verified (for trial accounts)")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🐀 RODENT DETECTION SYSTEM - TWILIO TEST")
    print("=" * 50)
    
    success = test_twilio_connection()
    
    print("=" * 50)
    if success:
        print("✅ Twilio is configured correctly!")
        print("The system will send alerts when rats are detected.")
    else:
        print("⚠️  Please fix the issues above before running the system.")
    print("=" * 50)