# 🐀 Rodent Detector - Simple Setup Guide

**No technical knowledge required! Just follow these simple steps.**

---

## 📦 What You Received

You should have:
1. **One SD Card** (64GB) - Already set up with the rodent detector software
2. **This guide** - Keep it handy
3. **Email notifications** will go to: **ratproject111@gmail.com**

---

## 🔌 What You Need to Provide

- [ ] **Raspberry Pi 5** (small computer, looks like a credit card)
- [ ] **Power adapter** for Raspberry Pi (USB-C, like a phone charger but stronger)
- [ ] **Wyze v4 Camera** (you probably already have this)
- [ ] **USB SD Card Reader** (to connect Wyze camera's SD card to Raspberry Pi)
- [ ] **Internet connection** (WiFi or Ethernet cable)

---

## 📋 Setup Steps (One Time Only)

### Step 1: Insert SD Card into Raspberry Pi
1. Take the **64GB SD card** (the one we prepared for you)
2. Find the SD card slot on the Raspberry Pi (underneath)
3. Gently slide the SD card in until it clicks
   - The metal contacts should face up
   - Label side should face down

### Step 2: Connect Wyze Camera SD Card
1. Remove the small SD card from your **Wyze camera**
2. Put it in the **USB SD card reader**
3. Plug the USB reader into any **blue USB port** on the Raspberry Pi
   - Blue ports are faster than black ports

### Step 3: Connect to Internet

#### Option A: Ethernet Cable (Easier)
- Simply plug an ethernet cable from your router to the Raspberry Pi
- No configuration needed!

#### Option B: WiFi (Needs one-time setup)
- The SD card is pre-configured for WiFi
- If WiFi doesn't work, you'll need to update the WiFi password (see troubleshooting)

### Step 4: Power On
1. Plug in the power adapter to the Raspberry Pi
2. **Red light** = Power is on ✓
3. **Green light blinking** = System is starting ✓
4. Wait **15 minutes** for first-time setup (only happens once)

---

## ✅ How to Know It's Working

After 15 minutes, the system should be running automatically.

### Check Your Email
- You should get a **test email** at **ratproject111@gmail.com**
- Check spam/junk folder if you don't see it
- Subject will be: "🚨 Rodent Alert: Norway Rat Detected"

### The Lights
- **Red LED**: Always on = Power OK
- **Green LED**: Occasional blinks = System running

### Camera Placement
- Place Wyze camera where rodents might appear
- Make sure area has some light (or use night vision)
- Camera should face downward at floor level

---

## 📧 What Happens When a Rodent is Detected

1. **Camera sees movement** → System checks if it's a rodent
2. **If it's a rat or mouse** → Takes a picture
3. **Sends email** to ratproject111@gmail.com
4. **Email contains**:
   - Type of rodent (Norway Rat or Roof Rat)
   - Time of detection
   - Confidence level (how sure the system is)
5. **Waits 10 minutes** before next alert (to avoid spam)

---

## 🔴 Simple Troubleshooting

### No Emails?
1. **Check spam/junk folder** first
2. **Check green light** on Raspberry Pi is blinking
3. **Check internet** - Can you browse web on your phone/computer?
4. **Wait 30 minutes** - System might still be starting

### No Lights on Raspberry Pi?
1. **Check power cable** is fully plugged in
2. **Try different outlet**
3. **Check power adapter** is the right one (5V, 3A minimum)

### Want to Check Status?
If you're comfortable using a computer:
1. Open web browser
2. Type: `http://rodent-detector.local`
3. You'll see the status page (if on same network)

---

## 📞 When to Get Help

Contact support if:
- No emails after 24 hours
- Red light won't turn on
- Raspberry Pi gets very hot
- You see smoke (unplug immediately!)

---

## 🔄 Daily Use

**You don't need to do anything!** The system runs 24/7 automatically.

- **System starts automatically** when powered on
- **Restarts itself** if there's a problem
- **Cleans up old data** automatically
- **Sends emails** whenever rodents detected

### Optional: Checking the Camera SD Card
Every few weeks:
1. Stop the Wyze camera recording
2. Remove its SD card
3. Plug into USB reader
4. Connect to Raspberry Pi
5. System will scan for rodent videos

---

## 💡 Tips for Best Results

### Camera Placement
- ✅ **DO**: Place at floor level
- ✅ **DO**: Point at areas where you've seen droppings
- ✅ **DO**: Ensure decent lighting
- ❌ **DON'T**: Point at pets' areas
- ❌ **DON'T**: Face windows (too much light change)

### Best Detection Areas
- Along walls (rodents run along edges)
- Near food sources
- Dark corners
- Behind appliances

### Email Management
- Add **ratproject111@gmail.com** to your phone
- Create a folder for rodent alerts
- Check daily for new detections

---

## 🛑 Safety First

- Keep Raspberry Pi in ventilated area
- Don't touch while operating (it gets warm)
- Keep away from water
- Use only the provided power adapter
- Don't remove SD card while system is on

---

## 📊 Understanding Email Alerts

You'll receive emails like this:

```
Subject: 🚨 Rodent Alert: Norway Rat Detected

Rodent Detection Alert
Type: Norway Rat
Detection Time: 2025-10-06 03:45:23 PM
Confidence Level: 95%
Message: 🚨 RODENT ALERT! Norway Rat detected at 3:45 PM with 95% confidence.
```

**Confidence Level** means:
- **90-100%**: Definitely a rodent
- **70-89%**: Probably a rodent
- **Below 70%**: Might be something else

---

## 🔧 Power Outage?

Don't worry! When power returns:
1. System starts automatically
2. Takes about 5 minutes to resume
3. No action needed from you
4. All settings are saved

---

## 📝 Quick Reference Card

| Problem | Solution |
|---------|----------|
| No emails | Check spam folder, wait 30 minutes |
| No lights | Check power connection |
| Too many emails | Normal - means rodents are active |
| System seems slow | Normal - it's processing video |
| Want to turn off | Just unplug power (safe to do) |
| Want to restart | Unplug for 10 seconds, plug back in |

---

## ✨ Remember

- **You don't need to do anything daily**
- **System runs automatically**
- **Emails come to ratproject111@gmail.com**
- **Check emails to know about rodent activity**
- **Keep this guide handy**

---

## 🎯 Success Checklist

After setup, you should have:
- [ ] Raspberry Pi powered on (red light on)
- [ ] Green light blinking occasionally
- [ ] Camera positioned in target area
- [ ] Received test email
- [ ] Know how to check ratproject111@gmail.com

**That's it! Your rodent detector is working!** 🎉

---

*If you need help, save this information:*
- System: Rodent AI Vision Box v1.0
- Email: ratproject111@gmail.com
- Device: Raspberry Pi 5
- Camera: Wyze v4