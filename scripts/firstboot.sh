#!/bin/bash
# =============================================================================
# Rodent AI Vision Box - First Boot Auto-Setup
# =============================================================================
# This script runs ONCE on first boot and sets up everything automatically
# Place this in /boot/firmware/ as firstboot.sh
# =============================================================================

LOG_FILE="/var/log/rodent-setup.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=============================================="
echo "🐀 Rodent AI Vision Box - First Boot Setup"
echo "Started: $(date)"
echo "=============================================="

# Wait for network
echo "[1/8] Waiting for network..."
sleep 30
until ping -c1 google.com &>/dev/null; do
    echo "Waiting for internet..."
    sleep 5
done
echo "✅ Network connected"

# Update system
echo "[2/8] Updating system packages..."
apt update && apt upgrade -y

# Install Docker
echo "[3/8] Installing Docker..."
curl -fsSL https://get.docker.com | sh
usermod -aG docker pi

# Install dependencies
echo "[4/8] Installing system dependencies..."
apt install -y git python3 python3-pip python3-venv python3-opencv \
    libatlas-base-dev libhdf5-dev ffmpeg

# Clone/copy project
echo "[5/8] Setting up project..."
cd /home/pi

if [ -d "/boot/firmware/rodent-ai-vision-box" ]; then
    cp -r /boot/firmware/rodent-ai-vision-box /home/pi/
else
    echo "Project files not found in /boot/firmware/, please copy manually"
fi

cd /home/pi/rodent-ai-vision-box

# Setup Python environment
echo "[6/8] Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Setup systemd service
echo "[7/8] Configuring auto-start service..."
cat > /etc/systemd/system/rodent-detection.service << EOF
[Unit]
Description=Rodent AI Vision Box
After=network.target docker.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rodent-ai-vision-box
ExecStartPre=/usr/bin/docker compose up -d
ExecStart=/home/pi/rodent-ai-vision-box/venv/bin/python -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable rodent-detection

# Fix permissions
echo "[8/8] Setting permissions..."
chown -R pi:pi /home/pi/rodent-ai-vision-box

# Cleanup - remove this script from running again
rm /etc/rc.local.d/firstboot.sh 2>/dev/null
systemctl disable firstboot 2>/dev/null

echo ""
echo "=============================================="
echo "✅ SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Edit /home/pi/rodent-ai-vision-box/.env with your Wyze credentials"
echo "2. Reboot: sudo reboot"
echo ""
echo "The system will start automatically after reboot."
echo "=============================================="
echo "Finished: $(date)"

# Optionally reboot
# reboot
