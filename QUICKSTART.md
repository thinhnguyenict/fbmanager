# Quick Start Guide / Hướng dẫn nhanh

## For Ubuntu 24.04.3 LTS with Python 3.12.3

### Option 1: Automated Installation (Recommended)

```bash
# Download and run the deployment script
wget https://raw.githubusercontent.com/thinhnguyenict/fbmanager/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Installation

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y build-essential python3-dev git python3-pip python3-venv

# 3. Create directory
sudo mkdir -p /opt/fbmanager
sudo chown $USER:$USER /opt/fbmanager
cd /opt/fbmanager

# 4. Clone repository
git clone https://github.com/thinhnguyenict/fbmanager.git .

# 5. Setup Python environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure
cp .env.example .env
nano .env  # Edit with your credentials

# 7. Run
python main.py
```

### Common Commands

```bash
# Start application
cd /opt/fbmanager
source venv/bin/activate
python main.py

# As a service
sudo systemctl start fbmanager.service
sudo systemctl status fbmanager.service
sudo journalctl -u fbmanager.service -f

# Update
cd /opt/fbmanager
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fbmanager.service
```

### Need Help?

- **Full Vietnamese Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Full English Guide**: [DEPLOYMENT_EN.md](DEPLOYMENT_EN.md)
- **Issues**: [GitHub Issues](https://github.com/thinhnguyenict/fbmanager/issues)

---

## Cho Ubuntu 24.04.3 LTS với Python 3.12.3

### Cách 1: Cài đặt tự động (Khuyến nghị)

```bash
# Tải và chạy script triển khai
wget https://raw.githubusercontent.com/thinhnguyenict/fbmanager/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### Cách 2: Cài đặt thủ công

```bash
# 1. Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# 2. Cài đặt dependencies
sudo apt install -y build-essential python3-dev git python3-pip python3-venv

# 3. Tạo thư mục
sudo mkdir -p /opt/fbmanager
sudo chown $USER:$USER /opt/fbmanager
cd /opt/fbmanager

# 4. Clone repository
git clone https://github.com/thinhnguyenict/fbmanager.git .

# 5. Thiết lập môi trường Python
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Cấu hình
cp .env.example .env
nano .env  # Sửa với thông tin đăng nhập của bạn

# 7. Chạy
python main.py
```

### Lệnh thường dùng

```bash
# Khởi động ứng dụng
cd /opt/fbmanager
source venv/bin/activate
python main.py

# Dưới dạng service
sudo systemctl start fbmanager.service
sudo systemctl status fbmanager.service
sudo journalctl -u fbmanager.service -f

# Cập nhật
cd /opt/fbmanager
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fbmanager.service
```

### Cần hỗ trợ?

- **Hướng dẫn đầy đủ tiếng Việt**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Hướng dẫn đầy đủ tiếng Anh**: [DEPLOYMENT_EN.md](DEPLOYMENT_EN.md)
- **Báo lỗi**: [GitHub Issues](https://github.com/thinhnguyenict/fbmanager/issues)
