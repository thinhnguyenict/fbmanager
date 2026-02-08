# Hướng dẫn triển khai FB Manager trên VPS Ubuntu

## ⚡ Cập nhật nhanh với Script tự động

Nếu bạn muốn cập nhật nhanh web interface, sử dụng script tự động:

```bash
cd /opt/fbmanager
git pull origin main
sudo bash update_web.sh
```

Script sẽ tự động thực hiện tất cả các bước cần thiết.

---

## 📖 Hướng dẫn chi tiết từng bước

## Yêu cầu hệ thống

- **Hệ điều hành**: Ubuntu 24.04.3 LTS x86_64
- **Python**: Python 3.12.3
- **RAM**: Tối thiểu 1GB (khuyến nghị 2GB+)
- **Ổ cứng**: Tối thiểu 10GB dung lượng trống
- **Quyền truy cập**: Root hoặc sudo

## Bước 1: Cập nhật hệ thống

Đầu tiên, kết nối vào VPS qua SSH và cập nhật hệ thống:

```bash
sudo apt update && sudo apt upgrade -y
```

## Bước 2: Cài đặt các gói cần thiết

Cài đặt các công cụ và thư viện cơ bản:

```bash
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev \
    git curl wget software-properties-common \
    python3-pip python3-venv
```

## Bước 3: Cài đặt Python 3.12.3

### Kiểm tra phiên bản Python hiện tại

```bash
python3 --version
```

Nếu hệ thống đã có Python 3.12.3, bạn có thể bỏ qua bước này. Nếu không:

### Cài đặt Python 3.12.3 từ source (nếu cần)

```bash
cd /tmp
wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tgz
tar -xf Python-3.12.3.tgz
cd Python-3.12.3
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall
```

Xác nhận cài đặt:

```bash
python3.12 --version
```

## Bước 4: Tạo thư mục cho ứng dụng

Tạo thư mục để chứa ứng dụng:

```bash
sudo mkdir -p /opt/fbmanager
sudo chown $USER:$USER /opt/fbmanager
cd /opt/fbmanager
```

## Bước 5: Clone repository

Clone mã nguồn từ GitHub:

```bash
git clone https://github.com/thinhnguyenict/fbmanager.git .
```

## Bước 6: Tạo môi trường ảo Python

Tạo và kích hoạt môi trường ảo:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

## Bước 7: Cài đặt dependencies

Cài đặt các thư viện Python cần thiết:

```bash
# Nếu có file requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

# Hoặc cài đặt thủ công các thư viện phổ biến cho Facebook automation
pip install selenium requests beautifulsoup4 lxml
```

## Bước 8: Cấu hình ứng dụng

### Tạo file cấu hình

Tạo file `.env` hoặc `config.py` để lưu cấu hình:

```bash
nano .env
```

Thêm các cấu hình cần thiết:

```env
# Cấu hình Facebook
FB_EMAIL=your_email@example.com
FB_PASSWORD=your_password

# Cấu hình ứng dụng
DEBUG=False
LOG_LEVEL=INFO
LOG_FILE=/var/log/fbmanager/app.log

# Cấu hình proxy (nếu cần)
PROXY_HOST=
PROXY_PORT=
PROXY_USER=
PROXY_PASS=
```

### Tạo thư mục logs

```bash
sudo mkdir -p /var/log/fbmanager
sudo chown $USER:$USER /var/log/fbmanager
```

## Bước 9: Cài đặt ChromeDriver (cho Selenium)

Nếu ứng dụng sử dụng Selenium để tự động hóa trình duyệt:

### Cách 1: Sử dụng webdriver-manager (Khuyến nghị)

```bash
# Cài đặt Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
rm google-chrome-stable_current_amd64.deb

# ChromeDriver sẽ được quản lý tự động bởi webdriver-manager
# (đã được cài đặt trong requirements.txt)
```

### Cách 2: Cài đặt ChromeDriver thủ công

```bash
# Tải phiên bản ChromeDriver tương thích
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d'.' -f1)

# Tải ChromeDriver cho Chrome phiên bản tương ứng
# Xem: https://googlechromelabs.github.io/chrome-for-testing/
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm -rf chromedriver-linux64*

# Xác nhận cài đặt
chromedriver --version
```

**Lưu ý**: webdriver-manager tự động tải và quản lý ChromeDriver phù hợp với phiên bản Chrome của bạn.

## Bước 10: Thiết lập systemd service (chạy tự động)

Tạo file service để ứng dụng chạy như một dịch vụ:

```bash
sudo nano /etc/systemd/system/fbmanager.service
```

Thêm nội dung sau:

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

**Lưu ý**: Thay `your_username` bằng username thực tế của bạn và điều chỉnh đường dẫn file Python chính (main.py) nếu cần.

### Kích hoạt và khởi động service

```bash
sudo systemctl daemon-reload
sudo systemctl enable fbmanager.service
sudo systemctl start fbmanager.service
```

### Kiểm tra trạng thái service

```bash
sudo systemctl status fbmanager.service
```

### Xem logs của service

```bash
sudo journalctl -u fbmanager.service -f
```

## Bước 11: Thiết lập Firewall (tùy chọn)

Nếu ứng dụng cần mở port (ví dụ: web interface):

```bash
sudo ufw allow 8000/tcp  # Thay 8000 bằng port của bạn
sudo ufw enable
sudo ufw status
```

## Bước 12: Thiết lập Nginx reverse proxy (nếu có web interface)

### Cài đặt Nginx

```bash
sudo apt install nginx -y
```

### Cấu hình Nginx

```bash
sudo nano /etc/nginx/sites-available/fbmanager
```

Thêm cấu hình:

```nginx
server {
    listen 80;
    server_name your_domain.com;  # Thay bằng domain của bạn

    location / {
        proxy_pass http://127.0.0.1:8000;  # Thay port nếu cần
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Kích hoạt cấu hình:

```bash
sudo ln -s /etc/nginx/sites-available/fbmanager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Bước 13: Thiết lập SSL với Let's Encrypt (khuyến nghị)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain.com
```

## Quản lý ứng dụng

### Khởi động lại ứng dụng

```bash
sudo systemctl restart fbmanager.service
```

### Dừng ứng dụng

```bash
sudo systemctl stop fbmanager.service
```

### Vô hiệu hóa auto-start

```bash
sudo systemctl disable fbmanager.service
```

### Cập nhật code

```bash
cd /opt/fbmanager
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fbmanager.service
```

## Xử lý sự cố (Troubleshooting)

### Kiểm tra logs

```bash
# Logs của systemd
sudo journalctl -u fbmanager.service -n 100 --no-pager

# Logs ứng dụng
tail -f /var/log/fbmanager/app.log
```

### Kiểm tra port đang sử dụng

```bash
sudo netstat -tulpn | grep :8000
```

### Kiểm tra quyền truy cập

```bash
ls -la /opt/fbmanager
```

### Lỗi không tìm thấy module

```bash
cd /opt/fbmanager
source venv/bin/activate
pip list  # Kiểm tra các package đã cài
pip install -r requirements.txt  # Cài lại nếu cần
```

### Lỗi Chrome/ChromeDriver

```bash
google-chrome --version
chromedriver --version
# Đảm bảo phiên bản tương thích
```

## Bảo mật

### 1. Tạo user riêng cho ứng dụng

```bash
sudo useradd -r -s /bin/false fbmanager
sudo chown -R fbmanager:fbmanager /opt/fbmanager
```

Cập nhật file service để sử dụng user mới:

```bash
sudo nano /etc/systemd/system/fbmanager.service
# Thay User=your_username thành User=fbmanager
```

### 2. Bảo vệ file cấu hình

```bash
chmod 600 /opt/fbmanager/.env
```

### 3. Cập nhật hệ thống thường xuyên

```bash
sudo apt update && sudo apt upgrade -y
```

### 4. Thiết lập fail2ban (tùy chọn)

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Backup

### Tạo script backup

```bash
nano /opt/fbmanager/backup.sh
```

Nội dung:

```bash
#!/bin/bash
BACKUP_DIR="/backup/fbmanager"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/fbmanager_$DATE.tar.gz /opt/fbmanager
find $BACKUP_DIR -name "fbmanager_*.tar.gz" -mtime +7 -delete
```

Phân quyền và thêm vào crontab:

```bash
chmod +x /opt/fbmanager/backup.sh
crontab -e
# Thêm dòng: 0 2 * * * /opt/fbmanager/backup.sh
```

## Monitoring

### Thiết lập giám sát tài nguyên

```bash
# Kiểm tra CPU và RAM
htop

# Kiểm tra dung lượng đĩa
df -h

# Kiểm tra tiến trình
ps aux | grep fbmanager
```

## Kết luận

Bạn đã hoàn thành việc triển khai FB Manager trên VPS Ubuntu 24.04.3 LTS với Python 3.12.3. Ứng dụng sẽ tự động khởi động khi VPS khởi động lại.

Để biết thêm thông tin hoặc gặp vấn đề, vui lòng tạo issue trên GitHub repository.

## Tài liệu tham khảo

- [Python Documentation](https://docs.python.org/3.12/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [systemd Documentation](https://systemd.io/)
- [Nginx Documentation](https://nginx.org/en/docs/)
