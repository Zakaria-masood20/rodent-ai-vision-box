# 🔧 SMS Fix Instructions - URGENT for Demo

## Problem Identified
Your Twilio number +18337214724 is a TOLL-FREE number (833 prefix) that requires verification to send SMS.

## Quick Fix (5 minutes)

### Step 1: Buy a Local Number
1. Login to https://console.twilio.com
2. Go to: Phone Numbers → Manage → Buy a Number
3. Filter by:
   - Country: United States
   - Type: **Local** (NOT Toll-Free)
   - Capabilities: SMS ✓
4. Choose any number with area code like:
   - 213 (Los Angeles)
   - 415 (San Francisco)  
   - 646 (New York)
   - 312 (Chicago)
5. Click "Buy" ($1.15/month)

### Step 2: Update Configuration
Replace the toll-free number in .env:

```bash
# OLD (Toll-Free - Not Working)
TWILIO_FROM_NUMBER=+18337214724

# NEW (Local Number - Will Work)
TWILIO_FROM_NUMBER=+1XXXXXXXXXX  # Your new local number
```

### Step 3: Test Again
```bash
python3 test_twilio.py
```

## Alternative: Verify Toll-Free (Takes 3-5 days)
If you want to keep the toll-free number:
1. Go to: Messaging → Toll-Free Verification
2. Submit verification request
3. Wait 3-5 business days

## Why This Happened
- Toll-free numbers (800, 833, 844, etc.) need special verification
- Local numbers work immediately for SMS
- This is a Twilio policy to prevent spam

## For Tomorrow's Demo
**GET A LOCAL NUMBER NOW** - It will work immediately!