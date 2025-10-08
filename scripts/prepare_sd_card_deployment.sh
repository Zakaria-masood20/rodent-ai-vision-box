#!/bin/bash

# =============================================================================
# SD Card Preparation Script for Non-Technical Client Deployment
# Run this on your Mac to prepare everything for the client
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Rodent AI Vision Box - Client Deployment Kit      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to get user input
get_input() {
    local prompt="$1"
    local var_name="$2"
    local default="$3"
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        input="${input:-$default}"
    else
        read -p "$prompt: " input
    fi
    
    eval "$var_name='$input'"
}

# Step 1: Collect client information
echo -e "${GREEN}Step 1: Client Information${NC}"
echo "Please provide the following information:"
echo ""

get_input "Client's WiFi Network Name (SSID)" WIFI_SSID ""
get_input "Client's WiFi Password" WIFI_PASS ""
get_input "Client's Email for alerts" CLIENT_EMAIL "ratproject111@gmail.com"
get_input "Client's Timezone (e.g., America/New_York)" TIMEZONE "America/New_York"
get_input "Client's Name" CLIENT_NAME "Client"

echo ""
echo -e "${GREEN}Step 2: Preparing Deployment Package${NC}"
echo ""

# Create deployment directory
DEPLOY_DIR="client_deployment_$(date +%Y%m%d)"
mkdir -p "$DEPLOY_DIR"

# Step 3: Create customized configuration
echo -e "${YELLOW}Creating customized configuration...${NC}"

# Create custom .env file
cat > "$DEPLOY_DIR/.env.production" << EOF
# Rodent AI Vision Box - Production Configuration
# Configured for: $CLIENT_NAME
# Date: $(date +%Y-%m-%d)

# EmailJS Configuration
EMAILJS_SERVICE_ID=service_2q7m7pm
EMAILJS_TEMPLATE_ID=template_0q4z7y8
EMAILJS_PUBLIC_KEY=Cx4zjcLaDjfhS2ssD
EMAILJS_PRIVATE_KEY=h1bojFisOSGIE9IIF9yhP
EMAILJS_TO_EMAIL=$CLIENT_EMAIL

# System Configuration
TIMEZONE=$TIMEZONE
USE_ONNX=true
LOG_LEVEL=INFO
DEBUG=False

# Performance Settings
AUTO_RESTART=true
HEALTH_CHECK_INTERVAL=300
STARTUP_DELAY=10
EOF

# Step 4: Create WiFi configuration
echo -e "${YELLOW}Creating WiFi configuration...${NC}"

cat > "$DEPLOY_DIR/wpa_supplicant.conf" << EOF
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="$WIFI_SSID"
    psk="$WIFI_PASS"
    key_mgmt=WPA-PSK
}
EOF

# Step 5: Create first-boot setup script
echo -e "${YELLOW}Creating automated setup script...${NC}"

cat > "$DEPLOY_DIR/first_boot_setup.sh" << 'EOF'
#!/bin/bash

# First Boot Setup Script
LOG_FILE="/home/pi/first_boot_setup.log"

echo "$(date): Starting first boot setup" > $LOG_FILE

# Update system
echo "$(date): Updating system..." >> $LOG_FILE
apt-get update >> $LOG_FILE 2>&1
apt-get upgrade -y >> $LOG_FILE 2>&1

# Install dependencies
echo "$(date): Installing dependencies..." >> $LOG_FILE
apt-get install -y \
    python3-pip \
    python3-venv \
    git \
    ffmpeg \
    python3-opencv \
    sqlite3 \
    libatlas-base-dev \
    libgfortran5 >> $LOG_FILE 2>&1

# Clone repository
echo "$(date): Cloning repository..." >> $LOG_FILE
cd /home/pi
git clone https://github.com/yourusername/rodent-ai-vision-box.git >> $LOG_FILE 2>&1
cd rodent-ai-vision-box

# Copy production environment
cp /boot/firmware/.env.production .env

# Create virtual environment
echo "$(date): Creating virtual environment..." >> $LOG_FILE
su - pi -c "cd /home/pi/rodent-ai-vision-box && python3 -m venv venv" >> $LOG_FILE 2>&1

# Install Python packages
echo "$(date): Installing Python packages..." >> $LOG_FILE
su - pi -c "cd /home/pi/rodent-ai-vision-box && source venv/bin/activate && pip install -r requirements.txt" >> $LOG_FILE 2>&1

# Set up service
echo "$(date): Setting up service..." >> $LOG_FILE
cp scripts/rodent-detection.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable rodent-detection
systemctl start rodent-detection

# Create mount point for camera SD
mkdir -p /mnt/wyze_sd
echo '/dev/sda1 /mnt/wyze_sd auto defaults,nofail 0 0' >> /etc/fstab

# Send test email
echo "$(date): Sending test email..." >> $LOG_FILE
su - pi -c "cd /home/pi/rodent-ai-vision-box && source venv/bin/activate && python test_emailjs.py" >> $LOG_FILE 2>&1

echo "$(date): Setup complete!" >> $LOG_FILE

# Create success indicator
touch /home/pi/.setup_complete

# Reboot
sleep 10
reboot
EOF

chmod +x "$DEPLOY_DIR/first_boot_setup.sh"

# Step 6: Create simple status checker
echo -e "${YELLOW}Creating status check script...${NC}"

cat > "$DEPLOY_DIR/check_status.sh" << 'EOF'
#!/bin/bash

clear
echo "╔════════════════════════════════════════════╗"
echo "║        RODENT DETECTOR STATUS CHECK       ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check service
if systemctl is-active --quiet rodent-detection; then
    echo "✅ Detector: RUNNING"
else
    echo "❌ Detector: NOT RUNNING"
fi

# Check internet
if ping -c 1 google.com >/dev/null 2>&1; then
    echo "✅ Internet: CONNECTED"
else
    echo "❌ Internet: NOT CONNECTED"
fi

# Check camera SD
if [ -d "/mnt/wyze_sd" ] && [ "$(ls -A /mnt/wyze_sd 2>/dev/null)" ]; then
    echo "✅ Camera SD: DETECTED"
else
    echo "❌ Camera SD: NOT FOUND"
fi

echo ""
echo "Recent detections:"
if [ -f "/home/pi/rodent-ai-vision-box/data/detections.db" ]; then
    sqlite3 /home/pi/rodent-ai-vision-box/data/detections.db \
        "SELECT datetime, class_name FROM detections ORDER BY datetime DESC LIMIT 3;" 2>/dev/null || echo "None yet"
else
    echo "None yet"
fi

echo ""
echo "════════════════════════════════════════════"
echo "Email alerts go to: $CLIENT_EMAIL"
echo "════════════════════════════════════════════"
EOF

chmod +x "$DEPLOY_DIR/check_status.sh"

# Step 7: Create client documentation
echo -e "${YELLOW}Creating client documentation...${NC}"

# Copy simple guide
cp CLIENT_SIMPLE_GUIDE.md "$DEPLOY_DIR/"

# Create quick reference card
cat > "$DEPLOY_DIR/QUICK_REFERENCE.txt" << EOF
╔════════════════════════════════════════════╗
║        RODENT DETECTOR QUICK GUIDE        ║
╠════════════════════════════════════════════╣
║                                            ║
║  CONFIGURED FOR: $CLIENT_NAME             ║
║  EMAIL ALERTS: $CLIENT_EMAIL              ║
║                                            ║
║  NORMAL OPERATION:                        ║
║  • Red Light = Power ON ✓                 ║
║  • Green Light Blinks = Working ✓         ║
║                                            ║
║  IF NO EMAILS:                           ║
║  1. Check spam folder                     ║
║  2. Check green light                     ║
║  3. Wait 30 minutes                       ║
║                                            ║
║  TO RESTART:                             ║
║  1. Unplug power                          ║
║  2. Wait 10 seconds                       ║
║  3. Plug back in                          ║
║                                            ║
║  SUPPORT:                                ║
║  Save this info when calling for help:    ║
║  - Device: Raspberry Pi 5                 ║
║  - System: Rodent AI Vision Box           ║
║  - Email: $CLIENT_EMAIL                   ║
║                                            ║
╚════════════════════════════════════════════╝
EOF

# Step 8: Create SD card flashing instructions
echo -e "${YELLOW}Creating SD card instructions...${NC}"

cat > "$DEPLOY_DIR/SD_CARD_SETUP.md" << EOF
# SD Card Setup Instructions

## You will need:
- Raspberry Pi Imager (download from raspberrypi.com)
- 64GB SD Card
- The files in this folder

## Steps:

1. **Open Raspberry Pi Imager**

2. **Choose OS:**
   - Click "Choose OS"
   - Select "Raspberry Pi OS (other)"
   - Select "Raspberry Pi OS Lite (64-bit)"

3. **Choose Storage:**
   - Select your 64GB SD card

4. **Advanced Settings (gear icon ⚙️):**
   - Set hostname: rodent-detector
   - Enable SSH: ✓
   - Username: pi
   - Password: RodentDetector2025!
   - Configure wireless LAN:
     - SSID: $WIFI_SSID
     - Password: [already configured]
   - Set locale:
     - Time zone: $TIMEZONE

5. **Write the image**

6. **After writing completes:**
   - Copy these files to the boot drive:
     - wpa_supplicant.conf
     - first_boot_setup.sh
     - .env.production
     - check_status.sh

7. **Eject SD card and insert into Raspberry Pi**

8. **Power on and wait 15-20 minutes for setup**

The system will automatically:
- Connect to WiFi
- Download the software
- Configure everything
- Start detecting rodents
- Send a test email to $CLIENT_EMAIL
EOF

# Step 9: Create deployment summary
echo -e "${YELLOW}Creating deployment summary...${NC}"

cat > "$DEPLOY_DIR/DEPLOYMENT_INFO.txt" << EOF
=====================================
RODENT AI VISION BOX - DEPLOYMENT KIT
=====================================

Prepared for: $CLIENT_NAME
Date: $(date +%Y-%m-%d)
Email alerts will go to: $CLIENT_EMAIL

This package contains:
1. Configuration files (WiFi, EmailJS)
2. Setup scripts (automatic installation)
3. Client documentation (simple guide)
4. Quick reference card (for daily use)
5. SD card setup instructions

NEXT STEPS FOR YOU:
1. Flash SD card using Raspberry Pi Imager
2. Copy all files to the boot partition
3. Give SD card to client
4. Client just needs to insert and power on

The system will automatically:
- Connect to their WiFi
- Install all software
- Configure email alerts
- Start detecting rodents
- Send test email to confirm

Support Information:
- Setup takes 15-20 minutes first time
- Check $CLIENT_EMAIL for test email
- System runs 24/7 automatically
- No daily maintenance needed

=====================================
EOF

# Step 10: Create a deployment checklist
echo -e "${YELLOW}Creating deployment checklist...${NC}"

cat > "$DEPLOY_DIR/DEPLOYMENT_CHECKLIST.md" << EOF
# Deployment Checklist

## Before giving to client:

### SD Card Preparation:
- [ ] Flash Raspberry Pi OS Lite (64-bit) to SD card
- [ ] Copy configuration files to boot partition
- [ ] Label SD card clearly
- [ ] Put in protective case

### Documentation:
- [ ] Print CLIENT_SIMPLE_GUIDE.md
- [ ] Print QUICK_REFERENCE.txt (laminate if possible)
- [ ] Include your contact information

### Hardware Check:
- [ ] Raspberry Pi 5 (8GB)
- [ ] Official power supply
- [ ] Case with cooling
- [ ] USB SD card reader
- [ ] Ethernet cable (optional)

### Configuration Verification:
- [ ] WiFi credentials: $WIFI_SSID
- [ ] Email destination: $CLIENT_EMAIL
- [ ] Timezone: $TIMEZONE
- [ ] EmailJS configured

## When delivering to client:

### Explain:
- [ ] Where SD card goes
- [ ] How to connect power
- [ ] Where to put camera SD card
- [ ] What lights mean
- [ ] Check email for alerts

### Demonstrate:
- [ ] SD card insertion
- [ ] Power connection
- [ ] USB reader connection
- [ ] Show example email

### Leave with client:
- [ ] Configured SD card
- [ ] Printed simple guide
- [ ] Quick reference card
- [ ] Your contact info

## Follow-up:
- [ ] Call after 24 hours
- [ ] Verify emails received
- [ ] Adjust if needed
EOF

# Final step: Package everything
echo ""
echo -e "${GREEN}Step 3: Creating deployment package${NC}"

# Create zip file
zip -r "${DEPLOY_DIR}.zip" "$DEPLOY_DIR" >/dev/null 2>&1

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              Deployment Kit Complete!                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Created deployment kit in: ${DEPLOY_DIR}/${NC}"
echo ""
echo "Contents:"
echo "  • .env.production (EmailJS configured)"
echo "  • wpa_supplicant.conf (WiFi configured)"
echo "  • first_boot_setup.sh (Auto-setup script)"
echo "  • check_status.sh (Status checker)"
echo "  • CLIENT_SIMPLE_GUIDE.md (User manual)"
echo "  • QUICK_REFERENCE.txt (Quick guide)"
echo "  • SD_CARD_SETUP.md (Your instructions)"
echo "  • DEPLOYMENT_CHECKLIST.md (Don't forget anything)"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Flash Raspberry Pi OS to a 64GB SD card"
echo "2. Copy all files from ${DEPLOY_DIR}/ to the boot partition"
echo "3. Give SD card to client with printed guides"
echo "4. Client inserts SD card and powers on"
echo "5. System auto-configures in 15-20 minutes"
echo ""
echo -e "${GREEN}Client will receive test email at: ${CLIENT_EMAIL}${NC}"
echo ""
echo -e "${BLUE}Good luck with the deployment!${NC}"