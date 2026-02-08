#!/bin/bash

# FB Manager - Quick Deployment Script for Ubuntu 24.04.3 LTS
# This script automates the deployment process

set -e

echo "========================================="
echo "FB Manager Deployment Script"
echo "Ubuntu 24.04.3 LTS with Python 3.12.3"
echo "========================================="
echo ""

# Check if running as root and set USE_SUDO accordingly
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  Running as root user"
    echo "   File permissions will be set to root:root"
    echo "   Consider running as a non-root user for better security"
    USE_SUDO=""
    CURRENT_USER="root"
else
    echo "✓ Running as non-root user: $USER"
    USE_SUDO="sudo"
    CURRENT_USER="$USER"
fi
echo ""

# Check if running on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
    echo "⚠️  This script is designed for Ubuntu"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1: Updating system packages..."
$USE_SUDO apt update && $USE_SUDO apt upgrade -y

echo ""
echo "Step 2: Installing required packages..."
$USE_SUDO apt install -y build-essential libssl-dev libffi-dev python3-dev \
    git curl wget software-properties-common \
    python3-pip python3-venv

echo ""
echo "Step 3: Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Current Python version: $PYTHON_VERSION"

# Check if Python 3.12 is available
if ! command -v python3.12 &> /dev/null; then
    echo "⚠️  Python 3.12 not found"
    read -p "Install Python 3.12.3 from source? This may take 10-15 minutes (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing Python 3.12.3..."
        cd /tmp
        wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tgz
        tar -xf Python-3.12.3.tgz
        cd Python-3.12.3
        ./configure --enable-optimizations
        make -j $(nproc)
        $USE_SUDO make altinstall
        cd ~
        echo "✓ Python 3.12.3 installed successfully"
    else
        echo "Using system Python..."
        PYTHON_CMD=python3
    fi
else
    echo "✓ Python 3.12 found"
    PYTHON_CMD=python3.12
fi

echo ""
echo "Step 4: Creating application directory..."
INSTALL_DIR="/opt/fbmanager"
if [ -d "$INSTALL_DIR" ]; then
    echo "⚠️  Directory $INSTALL_DIR already exists"
    read -p "Remove and reinstall? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $USE_SUDO rm -rf $INSTALL_DIR
    else
        echo "Keeping existing directory"
    fi
fi

$USE_SUDO mkdir -p $INSTALL_DIR
$USE_SUDO chown $CURRENT_USER:$CURRENT_USER $INSTALL_DIR

echo ""
echo "Step 5: Cloning repository..."
cd $INSTALL_DIR
if [ -d ".git" ]; then
    echo "Repository already exists, pulling latest changes..."
    git pull origin main || git pull origin master || echo "Using existing code"
else
    git clone https://github.com/thinhnguyenict/fbmanager.git .
fi

echo ""
echo "Step 6: Creating Python virtual environment..."
$PYTHON_CMD -m venv venv
source venv/bin/activate

echo ""
echo "Step 7: Installing Python dependencies..."
pip install --upgrade pip

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found"
    echo "Installing common dependencies for Facebook automation..."
    pip install selenium requests beautifulsoup4 lxml python-dotenv
fi

echo ""
echo "Step 8: Creating log directory..."
$USE_SUDO mkdir -p /var/log/fbmanager
$USE_SUDO chown $CURRENT_USER:$CURRENT_USER /var/log/fbmanager

echo ""
echo "Step 9: Creating configuration file..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# Facebook Configuration
FB_EMAIL=
FB_PASSWORD=

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
LOG_FILE=/var/log/fbmanager/app.log

# Proxy Configuration (if needed)
PROXY_HOST=
PROXY_PORT=
PROXY_USER=
PROXY_PASS=
EOF
    chmod 600 .env
    echo "✓ Created .env file (please edit with your credentials)"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "Step 10: Installing Chrome and ChromeDriver (optional)..."
read -p "Install Chrome and ChromeDriver for Selenium? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Install Chrome
    if ! command -v google-chrome &> /dev/null; then
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        $USE_SUDO apt install ./google-chrome-stable_current_amd64.deb -y
        rm google-chrome-stable_current_amd64.deb
    fi
    
    # Install ChromeDriver using webdriver-manager (recommended approach)
    echo "Installing ChromeDriver via webdriver-manager..."
    source $INSTALL_DIR/venv/bin/activate
    pip install webdriver-manager
    echo "✓ webdriver-manager installed (ChromeDriver will be managed automatically)"
    echo "  Note: ChromeDriver will be downloaded on first use"
    deactivate
fi

echo ""
echo "Step 11: Creating systemd service..."
read -p "Create systemd service for auto-start? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Find main Python file
    MAIN_FILE="main.py"
    if [ ! -f "$MAIN_FILE" ]; then
        if [ -f "app.py" ]; then
            MAIN_FILE="app.py"
        elif [ -f "run.py" ]; then
            MAIN_FILE="run.py"
        fi
    fi
    
    $USE_SUDO tee /etc/systemd/system/fbmanager.service > /dev/null << EOF
[Unit]
Description=FB Manager Service
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python $MAIN_FILE
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    $USE_SUDO systemctl daemon-reload
    $USE_SUDO systemctl enable fbmanager.service
    echo "✓ Systemd service created and enabled"
    echo ""
    echo "To start the service: sudo systemctl start fbmanager.service"
    echo "To check status: sudo systemctl status fbmanager.service"
    echo "To view logs: sudo journalctl -u fbmanager.service -f"
fi

echo ""
echo "========================================="
echo "✓ Deployment completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit configuration: nano $INSTALL_DIR/.env"
echo "2. Activate virtual environment: cd $INSTALL_DIR && source venv/bin/activate"
echo "3. Run application manually: python main.py"
echo "   OR"
echo "   Start as service: sudo systemctl start fbmanager.service"
echo ""
echo "For detailed documentation, see:"
echo "- Vietnamese: $INSTALL_DIR/DEPLOYMENT.md"
echo "- English: $INSTALL_DIR/DEPLOYMENT_EN.md"
echo ""
echo "========================================="
