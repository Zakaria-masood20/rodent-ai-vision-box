# 📦 Preparing Everything for Your Non-Technical Client

## Complete Preparation Checklist

Since your client is non-technical, you'll need to prepare EVERYTHING for them. Here's exactly what to do:

---

## 🎯 What the Client Needs (Shopping List)

Send this list to your client to purchase:

### Required Hardware:
1. **Raspberry Pi 5** (8GB RAM) - [$80]
   - Buy from: [raspberrypi.com](https://www.raspberrypi.com/products/raspberry-pi-5/)
   
2. **Official Raspberry Pi 5 Power Supply** - [$12]
   - Must be 27W USB-C Power Supply
   - Don't use phone chargers!

3. **64GB MicroSD Card** - [$15]
   - Brand: SanDisk or Samsung recommended
   - Class 10 or better

4. **USB SD Card Reader** - [$10]
   - Any USB 3.0 card reader works
   - Needed to read Wyze camera's SD card

5. **Raspberry Pi Case with Fan** - [$15]
   - Official Raspberry Pi 5 case recommended
   - Must have cooling fan

6. **Ethernet Cable** (optional but recommended) - [$5]
   - For reliable internet connection
   - Any length that reaches their router

**Total Cost: ~$137**

---

## 👨‍💻 What YOU Need to Prepare

### Step 1: Create the Pre-Configured SD Card Image

#### On Your Mac:
```bash
# 1. Install required tools
brew install raspberry-pi-imager
brew install qemu
brew install wget

# 2. Download Raspberry Pi OS
cd /tmp
wget https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2024-07-04/2024-07-04-raspios-bookworm-arm64-lite.img.xz

# 3. Extract the image
unxz 2024-07-04-raspios-bookworm-arm64-lite.img.xz
```

#### Flash and Configure the SD Card:

1. **Insert 64GB SD card into your Mac**

2. **Open Raspberry Pi Imager**

3. **Configure OS Settings:**
   - Click gear icon ⚙️
   - Set hostname: `rodent-detector`
   - Enable SSH: ✅
   - Username: `pi`
   - Password: `RodentDetector2025!`
   - Configure WiFi (get from client):
     - SSID: [Client's WiFi Name]
     - Password: [Client's WiFi Password]
   - Locale: Set to client's timezone

4. **Flash the SD Card**

5. **After flashing, mount the SD card again**

6. **Copy the project files:**
```bash
# Mount the SD card (it should appear as /Volumes/bootfs and /Volumes/rootfs)

# Create setup script on boot partition
cat > /Volumes/bootfs/first_run.sh << 'EOF'
#!/bin/bash

# This script runs on first boot
apt-get update
apt-get install -y git python3-pip python3-venv

# Clone the repository
cd /home/pi
git clone https://github.com/yourusername/rodent-ai-vision-box.git
cd rodent-ai-vision-box

# Copy production environment
cp .env.production .env

# Run setup
chmod +x setup.sh
./setup.sh

# Enable service
systemctl enable rodent-detection
systemctl start rodent-detection

# Send test email
su - pi -c "cd /home/pi/rodent-ai-vision-box && source venv/bin/activate && python test_emailjs.py"
EOF

chmod +x /Volumes/bootfs/first_run.sh
```

### Step 2: Create a Physical Setup Kit

Prepare a physical package with:

1. **The configured SD card** (in a labeled case)
2. **Printed simple guide** (CLIENT_SIMPLE_GUIDE.md)
3. **Quick reference card** (laminated)
4. **Labels for the Raspberry Pi ports:**
   - "POWER" arrow pointing to USB-C
   - "CAMERA SD CARD" arrow for USB port
   - "INTERNET" arrow for Ethernet

### Step 3: Pre-Configuration Checklist

Before giving to client, ensure:

- [ ] SD card has Raspberry Pi OS with:
  - [ ] SSH enabled
  - [ ] WiFi configured (if client provided credentials)
  - [ ] Hostname set to `rodent-detector`
  - [ ] Default user: pi / RodentDetector2025!

- [ ] Project repository contains:
  - [ ] `.env.production` with EmailJS credentials
  - [ ] All required files
  - [ ] Test scripts working

- [ ] Documentation printed:
  - [ ] Simple setup guide
  - [ ] Quick reference card
  - [ ] Contact information

---

## 📝 One-Page Quick Reference for Client

Create this as a laminated card:

```
╔════════════════════════════════════════════╗
║        RODENT DETECTOR QUICK GUIDE        ║
╠════════════════════════════════════════════╣
║                                            ║
║  NORMAL OPERATION:                        ║
║  • Red Light = Power ON ✓                 ║
║  • Green Light Blinks = Working ✓         ║
║  • Emails go to: ratproject111@gmail.com  ║
║                                            ║
║  IF NO EMAILS:                           ║
║  1. Check spam folder                     ║
║  2. Check green light blinking            ║
║  3. Wait 30 minutes                       ║
║                                            ║
║  TO RESTART:                             ║
║  1. Unplug power cable                    ║
║  2. Wait 10 seconds                       ║
║  3. Plug back in                          ║
║  4. Wait 5 minutes                        ║
║                                            ║
║  CAMERA PLACEMENT:                        ║
║  • Floor level                            ║
║  • Along walls                            ║
║  • Near food areas                        ║
║                                            ║
║  NEED HELP?                              ║
║  Email: your-support@email.com           ║
║  Include: "Rodent Detector Help"          ║
║                                            ║
╚════════════════════════════════════════════╝
```

---

## 🚀 Alternative: Full SD Card Image

If you want to create a complete image:

```bash
# On your Mac, after setting everything up on a Raspberry Pi:

# 1. Create image from configured SD card
sudo dd if=/dev/disk4 of=~/rodent_detector_complete.img bs=4M status=progress

# 2. Compress it
zip rodent_detector_complete.zip rodent_detector_complete.img

# 3. This image can be flashed to any SD card
```

---

## 📋 Client Handover Checklist

When delivering to client:

### Physical Items:
- [ ] Configured 64GB SD card (in case)
- [ ] Printed simple guide
- [ ] Laminated quick reference card
- [ ] Port labels/stickers

### Verbal Instructions (keep it simple):
1. "This SD card goes in the Raspberry Pi"
2. "Connect your camera's SD card with the USB reader"
3. "Plug in the ethernet cable or use WiFi"
4. "Plug in power - wait 15 minutes first time"
5. "You'll get emails when rats are detected"
6. "Check spam folder for emails"

### Demonstrate (if possible):
- Show them how to insert SD card
- Show them which ports to use
- Show them what the lights mean
- Show them an example email

---

## 🔧 Remote Support Setup

For easier support, set up remote access:

1. **Install VNC on the Raspberry Pi:**
```bash
sudo apt-get install realvnc-vnc-server
sudo systemctl enable vncserver-x11-serviced
```

2. **Install Dataplicity (for remote access):**
```bash
curl -s https://www.dataplicity.com/install.sh | sudo sh
```

3. **Give client the Dataplicity URL** for remote support

---

## 📱 Client's Phone Setup

Help them set up email on their phone:

1. Add `ratproject111@gmail.com` to their email app
2. Create a folder called "Rodent Alerts"
3. Set up a filter to move rodent emails to this folder
4. Enable notifications for this folder
5. Test with `python test_emailjs.py`

---

## 🎁 What to Tell the Client

Keep it simple:

> "I've set up everything for you. Just:
> 1. Put this SD card in the Raspberry Pi
> 2. Connect your camera's SD card
> 3. Plug in power
> 4. Wait 15 minutes
> 5. You'll get emails when rats are detected
> 
> That's it! It runs by itself. Check your email daily.
> If no emails after 24 hours, call me."

---

## 💡 Final Tips

1. **Test everything before delivery**
   - Boot the SD card in a Raspberry Pi
   - Verify EmailJS sends test email
   - Check service starts automatically

2. **Keep a backup image**
   - Save a copy of the configured SD card image
   - You can quickly make another if needed

3. **Document client's setup**
   - WiFi name (not password)
   - Email address for alerts
   - Date of installation

4. **Follow up**
   - Call after 24 hours
   - Check if they received emails
   - Adjust sensitivity if needed remotely

---

## 🆘 Emergency Support Script

Create this for the client to run if issues:

Save as `help.sh` on the SD card:
```bash
#!/bin/bash
echo "Collecting system information..."
echo "Date: $(date)" > /home/pi/support_info.txt
echo "Service Status:" >> /home/pi/support_info.txt
systemctl status rodent-detection >> /home/pi/support_info.txt
echo "Recent Logs:" >> /home/pi/support_info.txt
journalctl -u rodent-detection -n 50 >> /home/pi/support_info.txt
echo "Network Status:" >> /home/pi/support_info.txt
ip addr >> /home/pi/support_info.txt
echo "Support file created: support_info.txt"
echo "Email this file to support"
```

---

**Remember: The simpler you make it, the more successful the deployment will be!**