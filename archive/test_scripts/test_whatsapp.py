#!/usr/bin/env python3
"""
Test WhatsApp messaging via Twilio (more reliable than SMS)
"""

import os
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime

load_dotenv()

def test_whatsapp():
    """Test WhatsApp message sending"""
    
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    # WhatsApp requires 'whatsapp:' prefix
    from_whatsapp = 'whatsapp:+14155238886'  # Twilio Sandbox number
    to_whatsapp = 'whatsapp:+18184028681'    # David's number
    
    try:
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=f"🐀 Rodent Detection Alert!\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nRat detected by AI system",
            from_=from_whatsapp,
            to=to_whatsapp
        )
        
        print(f"✅ WhatsApp message sent! SID: {message.sid}")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing WhatsApp messaging...")
    test_whatsapp()