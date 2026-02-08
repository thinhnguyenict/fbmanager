# FB Manager VPS Deployment Guide for Ubuntu

## System Requirements

- **Operating System**: Ubuntu 24.04.3 LTS x86_64
- **Python**: Python 3.12.3
- **RAM**: Minimum 1GB (recommended 2GB+)
- **Storage**: Minimum 10GB free space
- **Access**: Root or sudo privileges

## Step 1: Update System

First, connect to your VPS via SSH and update the system:

```bash
sudo apt update && sudo apt upgrade -y
```

## Step 2: Install Required Packages

Install basic tools and libraries:

```bash
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev \
    git curl wget software-properties-common \
    python3-pip python3-venv
```

## Step 3: Install Python 3.12.3

### Check Current Python Version

```bash
python3 --version
```

If the system already has Python 3.12.3, you can skip this step. Otherwise:

### Install Python 3.12.3 from Source (if needed)

```bash
cd /tmp
wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tgz
tar -xf Python-3.12.3.tgz
cd Python-3.12.3
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall
```

Verify installation:

```bash
python3.12 --version
```

## Step 4: Create Application Directory

Create a directory for the application:

```bash
sudo mkdir -p /opt/fbmanager
sudo chown $USER:$USER /opt/fbmanager
cd /opt/fbmanager
```

## Step 5: Clone Repository

Clone the source code from GitHub:

```bash
git clone https://github.com/thinhnguyenict/fbmanager.git .
```

## Step 6: Create Python Virtual Environment

Create and activate virtual environment:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

## Step 7: Install Dependencies

Install required Python libraries:

```bash
# If requirements.txt exists
pip install --upgrade pip
pip install -r requirements.txt

# Or manually install common libraries for Facebook automation
pip install selenium requests beautifulsoup4 lxml
```

## Step 8: Configure Application

### Create Configuration File

Create `.env` or `config.py` file to store configuration:

```bash
nano .env
```

Add necessary configuration:

```env
# Facebook Configuration
FB_EMAIL=your_email@example.com
FB_PASSWORD=your_password

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
LOG_FILE=/var/log/fbmanager/app.log

# Proxy Configuration (if needed)
PROXY_HOST=
PROXY_PORT=
PROXY_USER=
PROXY_PASS=
```

### Create Logs Directory

```bash
sudo mkdir -p /var/log/fbmanager
sudo chown $USER:$USER /var/log/fbmanager
```

## Step 9: Install ChromeDriver (for Selenium)

If the application uses Selenium for browser automation:

```bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y

# Install ChromeDriver
CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -N https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip
```

## Step 10: Setup systemd Service (Auto-start)

Create a service file to run the application as a service:

```bash
sudo nano /etc/systemd/system/fbmanager.service
```

Add the following content:

```ini
[Unit]
Description=FB Manager Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/opt/fbmanager
Environment="PATH=/opt/fbmanager/venv/bin"
ExecStart=/opt/fbmanager/venv/bin/python main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Note**: Replace `your_username` with your actual username and adjust the Python file path (main.py) if needed.

### Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable fbmanager.service
sudo systemctl start fbmanager.service
```

### Check Service Status

```bash
sudo systemctl status fbmanager.service
```

### View Service Logs

```bash
sudo journalctl -u fbmanager.service -f
```

## Step 11: Setup Firewall (Optional)

If the application needs to open ports (e.g., web interface):

```bash
sudo ufw allow 8000/tcp  # Replace 8000 with your port
sudo ufw enable
sudo ufw status
```

## Step 12: Setup Nginx Reverse Proxy (if web interface exists)

### Install Nginx

```bash
sudo apt install nginx -y
```

### Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/fbmanager
```

Add configuration:

```nginx
server {
    listen 80;
    server_name your_domain.com;  # Replace with your domain

    location / {
        proxy_pass http://127.0.0.1:8000;  # Change port if needed
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable configuration:

```bash
sudo ln -s /etc/nginx/sites-available/fbmanager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 13: Setup SSL with Let's Encrypt (Recommended)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain.com
```

## Application Management

### Restart Application

```bash
sudo systemctl restart fbmanager.service
```

### Stop Application

```bash
sudo systemctl stop fbmanager.service
```

### Disable Auto-start

```bash
sudo systemctl disable fbmanager.service
```

### Update Code

```bash
cd /opt/fbmanager
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fbmanager.service
```

## Troubleshooting

### Check Logs

```bash
# systemd logs
sudo journalctl -u fbmanager.service -n 100 --no-pager

# Application logs
tail -f /var/log/fbmanager/app.log
```

### Check Used Ports

```bash
sudo netstat -tulpn | grep :8000
```

### Check Permissions

```bash
ls -la /opt/fbmanager
```

### Module Not Found Error

```bash
cd /opt/fbmanager
source venv/bin/activate
pip list  # Check installed packages
pip install -r requirements.txt  # Reinstall if needed
```

### Chrome/ChromeDriver Errors

```bash
google-chrome --version
chromedriver --version
# Ensure compatible versions
```

## Security

### 1. Create Dedicated User for Application

```bash
sudo useradd -r -s /bin/false fbmanager
sudo chown -R fbmanager:fbmanager /opt/fbmanager
```

Update service file to use new user:

```bash
sudo nano /etc/systemd/system/fbmanager.service
# Change User=your_username to User=fbmanager
```

### 2. Protect Configuration Files

```bash
chmod 600 /opt/fbmanager/.env
```

### 3. Regular System Updates

```bash
sudo apt update && sudo apt upgrade -y
```

### 4. Setup fail2ban (Optional)

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Backup

### Create Backup Script

```bash
nano /opt/fbmanager/backup.sh
```

Content:

```bash
#!/bin/bash
BACKUP_DIR="/backup/fbmanager"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/fbmanager_$DATE.tar.gz /opt/fbmanager
find $BACKUP_DIR -name "fbmanager_*.tar.gz" -mtime +7 -delete
```

Set permissions and add to crontab:

```bash
chmod +x /opt/fbmanager/backup.sh
crontab -e
# Add line: 0 2 * * * /opt/fbmanager/backup.sh
```

## Monitoring

### Setup Resource Monitoring

```bash
# Check CPU and RAM
htop

# Check disk usage
df -h

# Check processes
ps aux | grep fbmanager
```

## Conclusion

You have successfully deployed FB Manager on Ubuntu 24.04.3 LTS VPS with Python 3.12.3. The application will automatically start when the VPS reboots.

For more information or if you encounter issues, please create an issue on the GitHub repository.

## References

- [Python Documentation](https://docs.python.org/3.12/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [systemd Documentation](https://systemd.io/)
- [Nginx Documentation](https://nginx.org/en/docs/)
