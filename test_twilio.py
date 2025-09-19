#!/usr/bin/env python3
"""
Test Twilio SMS sending
Run this to verify your Twilio credentials work
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

def test_twilio_sms():
    """Send a test SMS via Twilio"""
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    to_number = os.getenv("ALERT_PHONE_NUMBER")
    
    # Check credentials
    if not all([account_sid, auth_token, from_number, to_number]):
        print("❌ Missing Twilio credentials in .env file")
        print("\nRequired variables:")
        print("  TWILIO_ACCOUNT_SID")
        print("  TWILIO_AUTH_TOKEN")
        print("  TWILIO_FROM_NUMBER")
        print("  ALERT_PHONE_NUMBER")
        return False
    
    if "your" in account_sid.lower() or "xxx" in account_sid.lower():
        print("❌ Please update TWILIO_ACCOUNT_SID in .env")
        return False
    
    try:
        from twilio.rest import Client
    except ImportError:
        print("❌ Twilio not installed")
        print("Run: pip install twilio")
        return False
    
    print("📱 Sending test SMS...")
    print(f"From: {from_number}")
    print(f"To: {to_number}")
    
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Create test message
        message_body = (
            "🧪 TEST MESSAGE\n"
            f"Rodent AI Vision Box is working!\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "If you receive this, Twilio is configured correctly."
        )
        
        # Send message
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        
        print(f"✅ Message sent successfully!")
        print(f"   Message SID: {message.sid}")
        print(f"   Status: {message.status}")
        print(f"\n📱 Check your phone for the test message!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")
        print("\nCommon issues:")
        print("1. Invalid credentials - check Twilio console")
        print("2. Phone numbers not in E.164 format (+1234567890)")
        print("3. Trial account limitations - verify phone number")
        print("4. No credits - check account balance")
        return False

def simulate_detection_alert():
    """Simulate a rat detection alert"""
    print("\n🐀 Simulating rat detection alert...")
    
    load_dotenv()
    
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    to_number = os.getenv("ALERT_PHONE_NUMBER")
    
    if not all([account_sid, auth_token, from_number, to_number]):
        print("❌ Missing credentials")
        return False
    
    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        
        # Simulate detection message
        message_body = (
            "🚨 RODENT ALERT!\n"
            "Norway Rat detected at "
            f"{datetime.now().strftime('%I:%M %p')} "
            "with 85% confidence.\n"
            "Location: Camera Feed\n"
            "[TEST MESSAGE]"
        )
        
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        
        print("✅ Alert sent!")
        print("This is what you'll receive when a rat is detected.")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    print("=" * 50)
    print("TWILIO SMS TEST")
    print("=" * 50)
    
    # Send test message
    if test_twilio_sms():
        print("\n" + "=" * 50)
        print("Would you like to simulate a detection alert? (y/n)")
        
        response = input("> ").strip().lower()
        if response == 'y':
            simulate_detection_alert()
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()