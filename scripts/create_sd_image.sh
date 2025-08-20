#!/bin/bash

echo "=== Create Raspberry Pi SD Card Image ==="
echo "This script creates a ready-to-use SD card image with the Rodent Detection System"

if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo)"
    exit 1
fi

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "This script should be run on a configured Raspberry Pi"
    exit 1
fi

# Create image file
IMAGE_NAME="rodent_detection_$(date +%Y%m%d).img"
echo "Creating SD card image: $IMAGE_NAME"

# Get SD card size (8GB minimum)
SD_SIZE="8G"

# Create sparse image file
dd if=/dev/zero of=$IMAGE_NAME bs=1 count=0 seek=$SD_SIZE

# Create partitions
parted $IMAGE_NAME mklabel msdos
parted $IMAGE_NAME mkpart primary fat32 1MiB 256MiB
parted $IMAGE_NAME mkpart primary ext4 256MiB 100%

# Setup loop device
LOOP_DEV=$(losetup -f --show $IMAGE_NAME)
partprobe $LOOP_DEV

# Format partitions
mkfs.vfat ${LOOP_DEV}p1
mkfs.ext4 ${LOOP_DEV}p2

# Mount partitions
mkdir -p /tmp/img_boot /tmp/img_root
mount ${LOOP_DEV}p1 /tmp/img_boot
mount ${LOOP_DEV}p2 /tmp/img_root

# Copy system files
echo "Copying system files..."
rsync -ax --progress / /tmp/img_root/ --exclude=/tmp --exclude=/proc --exclude=/sys --exclude=/dev --exclude=/run --exclude=/mnt --exclude=/media --exclude="$IMAGE_NAME"

# Copy boot files
rsync -ax --progress /boot/ /tmp/img_boot/

# Create necessary directories
mkdir -p /tmp/img_root/{dev,proc,sys,run,tmp,mnt,media}

# Update fstab
cat > /tmp/img_root/etc/fstab << EOF
proc            /proc           proc    defaults          0       0
/dev/mmcblk0p1  /boot           vfat    defaults          0       2
/dev/mmcblk0p2  /               ext4    defaults,noatime  0       1
EOF

# Cleanup
umount /tmp/img_boot
umount /tmp/img_root
losetup -d $LOOP_DEV
rmdir /tmp/img_boot /tmp/img_root

# Compress image
echo "Compressing image..."
zip ${IMAGE_NAME}.zip $IMAGE_NAME

echo ""
echo "=== SD Card Image Created ==="
echo "Image file: ${IMAGE_NAME}.zip"
echo ""
echo "To write to SD card:"
echo "1. Extract: unzip ${IMAGE_NAME}.zip"
echo "2. Write: sudo dd if=$IMAGE_NAME of=/dev/sdX bs=4M status=progress"
echo "   (Replace /dev/sdX with your SD card device)"
echo ""
echo "The image includes:"
echo "- Raspberry Pi OS Lite"
echo "- Rodent Detection System pre-installed"
echo "- Systemd service configured"
echo "- All dependencies installed"
echo ""
echo "After writing, edit /opt/rodent_detection/.env with your API credentials"