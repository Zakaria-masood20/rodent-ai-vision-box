# 🐀 Creating a Plug-and-Play SD Card for Raspberry Pi

This guide shows how to create an SD card that auto-configures everything when David first boots the Pi.

---

## What You'll Need

- 64GB MicroSD Card (Class 10 or better)
- Computer with SD card reader
- The `rodent-ai-vision-box-production` folder

---

## Step 1: Flash Raspberry Pi OS

1. Download **Raspberry Pi Imager**: https://www.raspberrypi.com/software/

2. Open Raspberry Pi Imager and configure:
   - **Device**: Raspberry Pi 5
   - **OS**: Raspberry Pi OS Lite (64-bit)
   - **Storage**: Your SD card

3. Click the **gear icon ⚙️** and configure:
   ```
   ✅ Enable SSH (Use password authentication)
   
   Username: pi
   Password: rodent2025!
   
   ✅ Configure WiFi
   SSID: [David's WiFi name]
   Password: [David's WiFi password]
   
   Locale: America/New_York
   Keyboard: US
   ```

4. Click **Save** then **Write**

---

## Step 2: Copy Project Files to SD Card

After flashing, the SD card will have a `bootfs` partition:

1. Open the SD card's `bootfs` in Finder
2. Create a folder called `rodent-ai-vision-box`
3. Copy ALL contents from `rodent-ai-vision-box-production/` into it:
   - `src/`
   - `models/`
   - `config/`
   - `scripts/`
   - `docs/`
   - `utils/`
   - `requirements.txt`
   - `setup.sh`
   - `docker-compose.yml`
   - `.env` (with David's credentials pre-filled!)

---

## Step 3: Pre-Configure Credentials

**IMPORTANT**: Edit the `.env` file BEFORE copying to SD card:

```env
WYZE_EMAIL=travismorrey@gmail.com
WYZE_API_KEY=[David's API Key]
WYZE_API_ID=[David's API ID]

EMAILJS_SERVICE_ID=service_2q7m7pm
EMAILJS_TEMPLATE_ID=template_0q4z7y8
EMAILJS_PUBLIC_KEY=Cx4zjcLaDjfhS2ssD
EMAILJS_PRIVATE_KEY=h1bojFisOSGIE9IIF9yhP
EMAILJS_TO_EMAIL=ratproject111@gmail.com
```

---

## Step 4: Enable Auto-Setup on First Boot

Copy `scripts/firstboot.sh` to the SD card's boot partition.

Then create a file called `firstrun.sh` in the boot partition:

```bash
#!/bin/bash
sudo bash /boot/firmware/rodent-ai-vision-box/scripts/firstboot.sh
```

---

## Step 5: What David Does

1. **Insert SD card** into Raspberry Pi
2. **Connect power** (USB-C)
3. **Wait 15-20 minutes** (first boot installs everything)
4. **Done!** System runs automatically

---

## To Check If It's Working

David can:
1. Open http://raspberrypi.local:5001 in browser to see cameras
2. Check email for test alert
3. Wave something in front of camera to trigger detection

---

## Troubleshooting

If it doesn't work, David can:
1. Connect a monitor + keyboard
2. Login: `pi` / `rodent2025!`
3. Run: `sudo journalctl -u rodent-detection -f` to see logs

---
