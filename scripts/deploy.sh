#!/bin/bash

# Rodent Detection System - Quick Deploy Script
# One-command deployment for production

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Rodent Detection System - Quick Deploy${NC}"
echo "======================================"

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Please don't run as root. Script will use sudo when needed."
   exit 1
fi

# Install system dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
sudo apt update
sudo apt install -y python3-pip python3-venv git ffmpeg sqlite3

# Create virtual environment
echo -e "${YELLOW}Setting up Python environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Install ONNX runtime for ARM
pip install onnxruntime

# Setup directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p data/{logs,images,videos}
sudo mkdir -p /mnt/wyze_sd

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}Created .env file - please add your API credentials${NC}"
fi

# Create systemd service
echo -e "${YELLOW}Installing service...${NC}"
sudo cp scripts/rodent-detection.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rodent-detection

echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials: nano .env"
echo "2. Start service: sudo systemctl start rodent-detection"
echo "3. Check status: sudo systemctl status rodent-detection"
echo "4. View logs: sudo journalctl -u rodent-detection -f"