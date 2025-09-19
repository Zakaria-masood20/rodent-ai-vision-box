# 🐀 Rodent Detection System - Simple User Guide

---

## What Is This System?

This is an **automatic rat detector** that watches your camera 24/7 and sends you a text message when it sees a rat. Think of it like a security system, but for rats!

**How it works:**
1. 📹 Your camera records video
2. 🤖 The computer checks the video for rats
3. 📱 You get a text message if a rat is found

---

## Getting Started (15 Minutes)

### What You Need:
- ✅ The black box (Raspberry Pi computer)
- ✅ Your Wyze camera
- ✅ A Twilio account (for sending text messages)
- ✅ Internet connection

---

## Step 1: Get Your Twilio Account (5 minutes)

Twilio is the service that sends text messages to your phone.

### A. Sign Up for Twilio

1. **Go to:** www.twilio.com
2. **Click:** "Sign up" (red button)
3. **Enter:**
   - Your email
   - Create a password
   - Your phone number
4. **Verify:** Check your email and click the link

### B. Get Your Free Phone Number

1. **After signing in**, you'll see "Get a Trial Number"
2. **Click:** "Get a Trial Number"
3. **Write down** this number (looks like: +1-234-567-8900)

### C. Find Your Account Information

1. **Go to:** Console (top menu)
2. **Look for** these two things and **copy them**:

   📝 **Account SID:** (starts with AC...)
   ```
   Example: ACa1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
   ```

   🔑 **Auth Token:** (click to reveal, then copy)
   ```
   Example: 1234567890abcdef1234567890abcdef
   ```

**Save these three things:**
- Your Twilio phone number
- Account SID  
- Auth Token

---

## Step 2: Set Up the Black Box (5 minutes)

### A. Connect Everything

1. **Plug in** the black box (Raspberry Pi) to power
2. **Connect** to your WiFi or ethernet cable
3. **Insert** the SD card from your Wyze camera

### B. Add Your Twilio Information

You need to tell the system your Twilio account details.

**On your computer:**

1. **Open** a text editor (Notepad on Windows, TextEdit on Mac)
2. **Copy** this template:

```
TWILIO_ACCOUNT_SID=paste_your_account_sid_here
TWILIO_AUTH_TOKEN=paste_your_auth_token_here
TWILIO_FROM_NUMBER=paste_your_twilio_number_here
ALERT_PHONE_NUMBER=your_personal_phone_number
```

3. **Replace** with your actual information:
   - Replace `paste_your_account_sid_here` with your Account SID
   - Replace `paste_your_auth_token_here` with your Auth Token
   - Replace `paste_your_twilio_number_here` with your Twilio phone (+1234567890)
   - Replace `your_personal_phone_number` with your cell phone (+1987654321)

4. **Save** this file as `.env` (yes, with the dot in front)
5. **Copy** this file to the black box

---

## Step 3: Start the System (2 minutes)

### Turn It On

1. **Power on** the black box
2. **Wait** 2 minutes for it to start
3. The system starts automatically!

### Test If It's Working

Send yourself a test message:

1. **Press** the test button (if available)
2. **OR** wait for the first detection
3. You should get a text message like:
   ```
   🚨 RODENT ALERT!
   Rat detected at 3:45 PM
   with 85% confidence.
   ```

---

## Daily Use

### What Happens Automatically:

- ✅ **Watches 24/7** - Never stops monitoring
- ✅ **Sends alerts** - Texts you when rats appear
- ✅ **Saves pictures** - Keeps photos of detections
- ✅ **Prevents spam** - Waits 10 minutes between alerts

### What You'll See:

**Normal Text Alert:**
```
🚨 RODENT ALERT!
Norway Rat detected at 3:45 PM
with 85% confidence.
```

**What the message means:**
- **"Norway Rat"** or **"Roof Rat"** = Type of rat (not always accurate)
- **Time** = When it was seen
- **Confidence** = How sure the system is (higher is better)

### Understanding Rat Types:

- **Norway Rat** = Larger, ground-dwelling rat (system is 77% accurate)
- **Roof Rat** = Smaller, climbing rat (system is only 15% accurate)
- **Important:** The system is good at detecting "a rat is there" but may confuse which type

---

## Common Questions

### Q: I'm not getting text messages

**Check these things:**

1. **Is the black box on?** (green light should be on)
2. **Is your phone number correct?** (must have +1 at the start)
3. **Do you have Twilio credits?** (free trial gives you $15)
4. **Is the camera recording?** (check Wyze app)

### Q: I'm getting too many messages

The system waits 10 minutes between alerts. If you want to change this:
- Contact support to adjust the "cooldown time"

### Q: The system says "Roof Rat" but it looks like a Norway Rat

This is normal. The system is still learning the difference. It's better at detecting "there's a rat" than identifying which type.

### Q: How do I turn it off?

Simply unplug the black box. Plug it back in to restart.

### Q: How do I see the pictures?

The system saves pictures of detected rats. Ask your technician how to access them.

---

## Troubleshooting

### Problem: No Power / Won't Turn On
- ✅ Check power cable is plugged in
- ✅ Try a different outlet
- ✅ Make sure power adapter is 5V 3A

### Problem: Not Detecting Rats (but you saw one)
- ✅ Make sure camera is recording
- ✅ Check camera isn't blocked
- ✅ Ensure good lighting (system needs to "see" the rat)

### Problem: False Alarms (detecting things that aren't rats)
- ✅ This can happen with shadows or other animals
- ✅ Contact support to adjust sensitivity

### Problem: Camera Not Working
- ✅ Check Wyze app - can you see video there?
- ✅ Make sure SD card is inserted properly
- ✅ Try formatting SD card in Wyze app

---

## Monthly Maintenance

### Once a Month:
1. **Check** that you're still getting alerts (do a test)
2. **Clear** old pictures if storage is full
3. **Clean** camera lens with soft cloth
4. **Verify** Twilio account has credits

### Every 3 Months:
1. **Restart** the system (unplug for 10 seconds, plug back in)
2. **Update** your phone number if changed
3. **Check** for software updates (ask technician)

---

## What the Lights Mean

🟢 **Green Light** = System is running normally
🟡 **Yellow Light** = Processing/Detecting something
🔴 **Red Light** = Error - check connections
No lights = Not powered on

---

## Cost Information

### One-Time Costs:
- ✅ System hardware: Already paid
- ✅ Setup: Already done

### Monthly Costs:
- 📱 **Twilio texts**: About $0.01 per text message
  - 100 alerts = $1.00
  - 500 alerts = $5.00
- 💳 **Twilio phone number**: $1.00/month

### Free Trial:
- Twilio gives $15 free credit to start
- This is enough for ~1,500 text messages

---

## Quick Reference Card

### Important Information to Keep:

| Item | Your Information |
|------|-----------------|
| **Twilio Account SID** | AC_________________ |
| **Twilio Phone Number** | +1-___-___-____ |
| **Your Alert Phone** | +1-___-___-____ |
| **System Location** | _________________ |
| **WiFi Name** | _________________ |
| **Support Contact** | _________________ |

### Quick Commands:

| To Do This | Do This |
|------------|---------|
| **Start System** | Plug in power |
| **Stop System** | Unplug power |
| **Test Alert** | Wait for detection |
| **Check Status** | Look for green light |
| **Get Help** | Contact support |

---

## Getting Help

### Before Calling Support:

1. **Check** the power is on
2. **Verify** internet is working
3. **Confirm** camera is recording
4. **Note** what lights you see
5. **Know** when problem started

### Information to Have Ready:
- Your Twilio account email
- When you last received an alert
- What lights are showing
- Any error messages

---

## Privacy & Security

### What the System Does:
- ✅ Processes video locally (on your premises)
- ✅ Only sends text alerts (no video sent)
- ✅ Saves pictures only on your device
- ✅ Doesn't share data with anyone

### What the System Doesn't Do:
- ❌ Doesn't upload video to cloud
- ❌ Doesn't share your location
- ❌ Doesn't store personal information
- ❌ Doesn't work without your camera

---

## Success Tips

### For Best Detection:
1. **Good lighting** - System needs to see clearly
2. **Clear view** - Don't block the camera
3. **Stable camera** - Mount securely, avoid shaking
4. **Regular checks** - Test monthly
5. **Keep it simple** - Don't change settings unless needed

### What to Expect:
- **First Week**: Might get more alerts as system adjusts
- **After 2 Weeks**: Should stabilize with fewer false alarms
- **Long Term**: Reliable detection with occasional updates needed

---

## Summary

### Your Rat Detection System:
- 📹 Watches your camera 24/7
- 🤖 Uses AI to spot rats
- 📱 Texts you immediately
- 🛡️ Works automatically
- 💰 Costs pennies per alert

### Remember:
- The system is **great at detecting rats** (67% accurate)
- It's **good at identifying Norway rats** (77% accurate)  
- It's **not good at identifying Roof rats** (15% accurate)
- But it **will alert you when any rat appears**!

### Three Main Steps:
1. **Set up Twilio** (one time)
2. **Add your phone numbers** (one time)
3. **Let it run** (automatic)

---

## Contact Information

**For Technical Support:**
- Check this guide first
- Note error messages or unusual behavior
- Contact your installer

**For Twilio Issues:**
- Website: www.twilio.com/support
- Check your account balance
- Verify phone numbers are correct

**For Camera Issues:**
- Check Wyze app
- Ensure SD card is working
- Verify camera has power

---

*System Version: 1.0*  
*Last Updated: September 2024*  
*Designed for: Automatic Rodent Detection*

---

## Quick Start Reminder

**Every Day, Your System:**
1. ✅ Watches for rats
2. ✅ Sends you texts
3. ✅ Keeps you informed
4. ✅ Works automatically

**You Just Need To:**
1. ✅ Keep it plugged in
2. ✅ Keep internet connected
3. ✅ Keep Twilio account active
4. ✅ Check your texts!

---

**That's it! Your rat detection system is now protecting your property 24/7!** 🛡️