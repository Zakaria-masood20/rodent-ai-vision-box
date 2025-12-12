#!/bin/bash
# =============================================================================
# Rodent AI Vision Box - One-Click Setup Script
# =============================================================================
# This script automates the entire setup process on a fresh Raspberry Pi
# Run with: curl -fsSL https://your-url/install.sh | sudo bash
# =============================================================================

set -e

echo "=============================================="
echo "🐀 Rodent AI Vision Box - Automated Setup"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root (use sudo)"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER=${SUDO_USER:-pi}
USER_HOME="/home/$ACTUAL_USER"
PROJECT_DIR="$USER_HOME/rodent-ai-vision-box"

log_info "Setting up for user: $ACTUAL_USER"

# =============================================================================
# Step 1: System Update
# =============================================================================
log_info "Step 1/6: Updating system packages..."
apt update && apt upgrade -y

# =============================================================================
# Step 2: Install Docker
# =============================================================================
log_info "Step 2/6: Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker $ACTUAL_USER
    log_info "Docker installed successfully"
else
    log_info "Docker already installed"
fi

# =============================================================================
# Step 3: Install System Dependencies
# =============================================================================
log_info "Step 3/6: Installing system dependencies..."
apt install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    python3-opencv \
    libatlas-base-dev \
    libhdf5-dev \
    libopenblas-dev \
    libjpeg-dev \
    zlib1g-dev \
    ffmpeg

# =============================================================================
# Step 4: Clone Repository
# =============================================================================
log_info "Step 4/6: Setting up project..."
cd $USER_HOME

if [ -d "$PROJECT_DIR" ]; then
    log_warn "Project directory exists, pulling latest changes..."
    cd $PROJECT_DIR
    git pull
else
    log_info "Cloning repository..."
    # If you have a git repo, uncomment and update this:
    # git clone https://github.com/YOUR_USERNAME/rodent-ai-vision-box.git
    
    # For now, assume project files are already on the SD card
    log_warn "Please ensure project files are in $PROJECT_DIR"
fi

# =============================================================================
# Step 5: Python Environment Setup
# =============================================================================
log_info "Step 5/6: Setting up Python environment..."
cd $PROJECT_DIR

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Deactivate
deactivate

# =============================================================================
# Step 6: Configure System Service
# =============================================================================
log_info "Step 6/6: Configuring system service..."

# Create systemd service file
cat > /etc/systemd/system/rodent-detection.service << EOF
[Unit]
Description=Rodent AI Vision Box Detection Service
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStartPre=/bin/sleep 10
ExecStart=$PROJECT_DIR/venv/bin/python -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload
systemctl enable rodent-detection

# =============================================================================
# Create directories
# =============================================================================
log_info "Creating data directories..."
mkdir -p $PROJECT_DIR/data/images
mkdir -p $PROJECT_DIR/data/logs
chown -R $ACTUAL_USER:$ACTUAL_USER $PROJECT_DIR

# =============================================================================
# Setup Complete
# =============================================================================
echo ""
echo "=============================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Edit your Wyze credentials:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2. Start Wyze Bridge:"
echo "   cd $PROJECT_DIR && docker-compose up -d"
echo ""
echo "3. Start detection service:"
echo "   sudo systemctl start rodent-detection"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status rodent-detection"
echo ""
echo "For logs: sudo journalctl -u rodent-detection -f"
echo "=============================================="
