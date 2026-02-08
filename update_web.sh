#!/bin/bash
#
# FB Manager - Auto Update & Deploy Web Interface Script
# Usage: sudo bash update_web.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/fbmanager"
SERVICE_NAME="fbmanager.service"
BACKUP_DIR="/backup/fbmanager"
VENV_DIR="$APP_DIR/venv"
ENV_FILE="$APP_DIR/.env"

# Functions
print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Check if running as root or with sudo
check_privileges() {
    if [ "$EUID" -ne 0 ]; then 
        print_error "Please run as root or with sudo"
        exit 1
    fi
}

# Backup current installation
backup_installation() {
    print_step "[1/10] Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/fbmanager_backup_$TIMESTAMP.tar.gz"
    
    cd /opt
    tar -czf "$BACKUP_FILE" fbmanager/ 2>/dev/null || true
    
    # Keep only last 5 backups
    cd "$BACKUP_DIR"
    ls -t fbmanager_backup_*.tar.gz | tail -n +6 | xargs rm -f 2>/dev/null || true
    
    print_success "Backup created: $BACKUP_FILE"
}

# Stop service
stop_service() {
    print_step "[2/10] Stopping service..."
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        systemctl stop $SERVICE_NAME
        print_success "Service stopped"
    else
        print_warning "Service was not running"
    fi
}

# Pull latest code
pull_code() {
    print_step "[3/10] Pulling latest code from GitHub..."
    
    cd "$APP_DIR"
    
    # Check if there are local changes
    if ! git diff-index --quiet HEAD --; then
        print_warning "Local changes detected, stashing..."
        git stash
    fi
    
    # Pull latest code
    git pull origin main
    print_success "Code updated successfully"
}

# Create virtual environment if not exists
setup_venv() {
    print_step "[4/10] Setting up virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        print_warning "Virtual environment not found, creating..."
        python3.12 -m venv "$VENV_DIR" || python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
}

# Install/Update dependencies
install_dependencies() {
    print_step "[5/10] Installing/Updating dependencies..."
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    
    deactivate
    print_success "Dependencies installed"
}

# Setup environment file
setup_env() {
    print_step "[6/10] Setting up environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        print_warning ".env file not found, creating from .env.example..."
        cp "$APP_DIR/.env.example" "$ENV_FILE"
        
        # Generate random secret key
        SECRET_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
        
        # Update .env with random secret
        sed -i "s/your-random-secret-key-change-in-production/$SECRET_KEY/" "$ENV_FILE"
        
        print_warning "IMPORTANT: Please update the following in $ENV_FILE:"
        echo "  - ADMIN_USER (default: admin)"
        echo "  - ADMIN_PASSWORD (default: change-this-password)"
        echo "  - FB_EMAIL"
        echo "  - FB_PASSWORD"
        
        read -p "Press Enter to edit .env now or Ctrl+C to cancel..."
        nano "$ENV_FILE"
    else
        # Check if new variables need to be added
        if ! grep -q "WEB_HOST" "$ENV_FILE"; then
            print_warning "Adding web interface configuration to .env..."
            echo "" >> "$ENV_FILE"
            echo "# Web Interface Configuration" >> "$ENV_FILE"
            echo "WEB_HOST=0.0.0.0" >> "$ENV_FILE"
            echo "WEB_PORT=8000" >> "$ENV_FILE"
            
            SECRET_KEY=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
            echo "SECRET_KEY=$SECRET_KEY" >> "$ENV_FILE"
            echo "" >> "$ENV_FILE"
            echo "# Admin credentials for web interface" >> "$ENV_FILE"
            echo "ADMIN_USER=admin" >> "$ENV_FILE"
            echo "ADMIN_PASSWORD=change-this-password" >> "$ENV_FILE"
            
            print_warning "Added web interface config. Please update ADMIN_PASSWORD!"
            read -p "Press Enter to edit .env now or Ctrl+C to skip..."
            nano "$ENV_FILE"
        fi
        print_success "Environment configured"
    fi
    
    # Set proper permissions
    chmod 600 "$ENV_FILE"
}

# Create/Update systemd service
setup_service() {
    print_step "[7/10] Setting up systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
    
    # Get current user (the one who ran sudo)
    ACTUAL_USER=${SUDO_USER:-$USER}
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=FB Manager Web Service
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    print_success "Service file created/updated"
}

# Setup firewall
setup_firewall() {
    print_step "[8/10] Configuring firewall..."
    
    # Check if ufw is installed and active
    if command -v ufw &> /dev/null; then
        if ufw status | grep -q "Status: active"; then
            ufw allow 8000/tcp >/dev/null 2>&1
            print_success "Firewall configured (port 8000 opened)"
        else
            print_warning "UFW is installed but not active"
        fi
    else
        print_warning "UFW not installed, skipping firewall setup"
    fi
}

# Start service
start_service() {
    print_step "[9/10] Starting service..."
    
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME >/dev/null 2>&1
    systemctl start $SERVICE_NAME
    
    sleep 2
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_success "Service started successfully"
    else
        print_error "Service failed to start"
        echo "Check logs with: sudo journalctl -u $SERVICE_NAME -n 50"
        exit 1
    fi
}

# Display final information
show_info() {
    print_step "[10/10] Deployment completed!"
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  FB Manager Web Interface Ready!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    echo "📍 Access the web interface at:"
    echo -e "   ${BLUE}http://$SERVER_IP:8000${NC}"
    echo -e "   ${BLUE}http://localhost:8000${NC} (from server)"
    echo ""
    
    echo "🔐 Login credentials:"
    ADMIN_USER=$(grep ADMIN_USER "$ENV_FILE" | cut -d'=' -f2)
    echo "   Username: $ADMIN_USER"
    echo "   Password: (check $ENV_FILE)"
    echo ""
    
    echo "📊 Service status:"
    systemctl status $SERVICE_NAME --no-pager -l
    echo ""
    
    echo "📝 Useful commands:"
    echo "   View logs:     sudo journalctl -u $SERVICE_NAME -f"
    echo "   Restart:       sudo systemctl restart $SERVICE_NAME"
    echo "   Stop:          sudo systemctl stop $SERVICE_NAME"
    echo "   Status:        sudo systemctl status $SERVICE_NAME"
    echo ""
    
    echo "⚠️  Security reminders:"
    echo "   1. Change ADMIN_PASSWORD in $ENV_FILE"
    echo "   2. Setup Nginx reverse proxy for production"
    echo "   3. Enable SSL/HTTPS with Let's Encrypt"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  FB Manager Auto Update & Deploy${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    check_privileges
    backup_installation
    stop_service
    pull_code
    setup_venv
    install_dependencies
    setup_env
    setup_service
    setup_firewall
    start_service
    show_info
}

# Run main function
main
