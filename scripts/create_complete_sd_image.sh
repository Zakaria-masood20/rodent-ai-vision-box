#!/bin/bash

# =============================================================================
# Complete SD Card Image Creator for Rodent AI Vision Box
# This script creates a fully configured SD card image ready for the client
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Rodent AI Vision Box - SD Card Image Creator ${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo -e "${RED}Please run as root (use sudo)${NC}"
   exit 1
fi

# Configuration
WORK_DIR="/tmp/rodent_ai_sd"
IMAGE_SIZE="16G"  # Size of the SD card image
IMAGE_NAME="rodent_ai_vision_box_$(date +%Y%m%d).img"
HOSTNAME="rodent-detector"

# Clean up function
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    umount ${WORK_DIR}/boot 2>/dev/null || true
    umount ${WORK_DIR}/root 2>/dev/null || true
    losetup -d /dev/loop0 2>/dev/null || true
    rm -rf ${WORK_DIR}
}

# Set up cleanup on exit
trap cleanup EXIT

# Step 1: Create working directory
echo -e "${GREEN}[1/10] Creating working directory...${NC}"
rm -rf ${WORK_DIR}
mkdir -p ${WORK_DIR}
cd ${WORK_DIR}

# Step 2: Download Raspberry Pi OS
echo -e "${GREEN}[2/10] Downloading Raspberry Pi OS Lite (64-bit)...${NC}"
if [ ! -f "raspios_lite_arm64.img.xz" ]; then
    wget -O raspios_lite_arm64.img.xz \
        https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2023-12-11/2023-12-11-raspios-bookworm-arm64-lite.img.xz
fi

echo -e "${GREEN}[3/10] Extracting OS image...${NC}"
xz -d -k raspios_lite_arm64.img.xz
mv raspios_lite_arm64.img base.img

# Step 4: Resize image to fit our software
echo -e "${GREEN}[4/10] Resizing image to ${IMAGE_SIZE}...${NC}"
qemu-img resize base.img ${IMAGE_SIZE}

# Step 5: Set up loop device and mount
echo -e "${GREEN}[5/10] Mounting image...${NC}"
losetup -P /dev/loop0 base.img
mkdir -p ${WORK_DIR}/boot ${WORK_DIR}/root

# Wait for partitions to appear
sleep 2

# Mount partitions
mount /dev/loop0p1 ${WORK_DIR}/boot
mount /dev/loop0p2 ${WORK_DIR}/root

# Step 6: Enable SSH and configure network
echo -e "${GREEN}[6/10] Configuring SSH and network...${NC}"

# Enable SSH
touch ${WORK_DIR}/boot/ssh

# Create default user (pi/raspberry)
echo 'pi:$6$rBoByrWRKMYSWHTc$Ho.LISmmiSVkEeVXPmYYPtLC7u7z2YFmVTiRFp7PJuSXBexYmfZhHKFUID4GciWDXKJW1fkqE0p6KqWTZYiXk/' > ${WORK_DIR}/boot/userconf.txt

# Configure WiFi (client will need to update this)
cat > ${WORK_DIR}/boot/wpa_supplicant.conf << 'EOF'
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOUR_WIFI_NAME"
    psk="YOUR_WIFI_PASSWORD"
    key_mgmt=WPA-PSK
}
EOF

# Step 7: Copy Rodent AI Vision Box software
echo -e "${GREEN}[7/10] Installing Rodent AI Vision Box...${NC}"

# Create directory structure
mkdir -p ${WORK_DIR}/root/home/pi/rodent-ai-vision-box

# Copy all project files (assuming script is run from project directory)
cp -r ../../* ${WORK_DIR}/root/home/pi/rodent-ai-vision-box/ 2>/dev/null || true

# Copy production .env file
cp ../../.env.production ${WORK_DIR}/root/home/pi/rodent-ai-vision-box/.env

# Set correct permissions
chroot ${WORK_DIR}/root chown -R 1000:1000 /home/pi/rodent-ai-vision-box

# Step 8: Create first-boot setup script
echo -e "${GREEN}[8/10] Creating first-boot configuration...${NC}"

cat > ${WORK_DIR}/root/etc/rc.local << 'EOF'
#!/bin/bash

# First boot setup for Rodent AI Vision Box
FIRST_BOOT_FLAG="/home/pi/.first_boot_done"

if [ ! -f "$FIRST_BOOT_FLAG" ]; then
    # Expand filesystem
    raspi-config --expand-rootfs
    
    # Set hostname
    hostnamectl set-hostname rodent-detector
    
    # Update system
    apt-get update
    
    # Install dependencies
    apt-get install -y python3-pip python3-venv git ffmpeg python3-opencv \
                       sqlite3 libatlas-base-dev libgfortran5
    
    # Set up Rodent AI Vision Box
    cd /home/pi/rodent-ai-vision-box
    
    # Create virtual environment
    su - pi -c "cd /home/pi/rodent-ai-vision-box && python3 -m venv venv"
    
    # Install Python packages
    su - pi -c "cd /home/pi/rodent-ai-vision-box && source venv/bin/activate && pip install -r requirements.txt"
    
    # Install and enable service
    cp /home/pi/rodent-ai-vision-box/scripts/rodent-detection.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable rodent-detection
    
    # Create mount point for Wyze camera SD card
    mkdir -p /mnt/wyze_sd
    
    # Add auto-mount for USB devices
    echo '/dev/sda1 /mnt/wyze_sd auto defaults,nofail,x-systemd.device-timeout=5 0 0' >> /etc/fstab
    
    # Create flag file
    touch "$FIRST_BOOT_FLAG"
    
    # Start the service
    systemctl start rodent-detection
    
    # Reboot to apply all changes
    sleep 10
    reboot
fi

exit 0
EOF

chmod +x ${WORK_DIR}/root/etc/rc.local

# Step 9: Create simple status check script
echo -e "${GREEN}[9/10] Creating user-friendly scripts...${NC}"

cat > ${WORK_DIR}/root/home/pi/check_status.sh << 'EOF'
#!/bin/bash

echo "====================================="
echo "   RODENT DETECTOR STATUS CHECK     "
echo "====================================="
echo ""

# Check if service is running
if systemctl is-active --quiet rodent-detection; then
    echo "✓ Rodent Detector: RUNNING"
else
    echo "✗ Rodent Detector: NOT RUNNING"
    echo "  To start: sudo systemctl start rodent-detection"
fi

echo ""

# Check internet connection
if ping -c 1 google.com > /dev/null 2>&1; then
    echo "✓ Internet: CONNECTED"
else
    echo "✗ Internet: NOT CONNECTED"
    echo "  Check WiFi settings"
fi

echo ""

# Check for camera SD card
if [ -d "/mnt/wyze_sd" ] && [ "$(ls -A /mnt/wyze_sd 2>/dev/null)" ]; then
    echo "✓ Camera SD Card: DETECTED"
else
    echo "✗ Camera SD Card: NOT FOUND"
    echo "  Insert Wyze camera SD card into USB reader"
fi

echo ""

# Show recent detections
echo "Recent Detections:"
if [ -f "/home/pi/rodent-ai-vision-box/data/detections.db" ]; then
    sqlite3 /home/pi/rodent-ai-vision-box/data/detections.db \
        "SELECT datetime, class_name FROM detections ORDER BY datetime DESC LIMIT 5;" 2>/dev/null || echo "  No detections yet"
else
    echo "  No detections yet"
fi

echo ""
echo "====================================="
echo "For help, check the user guide"
echo "====================================="
EOF

chmod +x ${WORK_DIR}/root/home/pi/check_status.sh

# Step 10: Unmount and finalize
echo -e "${GREEN}[10/10] Finalizing SD card image...${NC}"

# Clean up
umount ${WORK_DIR}/boot
umount ${WORK_DIR}/root
losetup -d /dev/loop0

# Rename final image
mv base.img ${IMAGE_NAME}

# Compress the image
echo -e "${GREEN}Compressing image (this may take a while)...${NC}"
zip ${IMAGE_NAME}.zip ${IMAGE_NAME}

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}       SD Card Image Creation Complete!        ${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${GREEN}Image created: ${IMAGE_NAME}.zip${NC}"
echo -e "${GREEN}Size: $(du -h ${IMAGE_NAME}.zip | cut -f1)${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Flash ${IMAGE_NAME} to a 64GB SD card using Raspberry Pi Imager"
echo "2. Edit the WiFi settings in /boot/wpa_supplicant.conf if needed"
echo "3. Insert SD card into Raspberry Pi 5"
echo "4. Connect Wyze camera SD card via USB reader"
echo "5. Power on the Raspberry Pi"
echo "6. System will auto-configure on first boot (takes ~15 minutes)"
echo ""
echo -e "${GREEN}The system will automatically start detecting rodents!${NC}"