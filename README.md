# fbmanager
Quản lý FB

## 🚀 Quick Start / Khởi động nhanh

```bash
git clone https://github.com/thinhnguyenict/fbmanager.git
cd fbmanager
chmod +x deploy.sh
./deploy.sh
```

📖 **[Quick Start Guide / Hướng dẫn nhanh](QUICKSTART.md)**

## 🚀 Cập nhật tự động Web Interface

### Cách 1: Sử dụng script tự động (Khuyến nghị)

Script này sẽ tự động:
- ✅ Backup code hiện tại
- ✅ Pull code mới từ GitHub
- ✅ Cài đặt dependencies
- ✅ Cấu hình systemd service
- ✅ Mở firewall port 8000
- ✅ Khởi động web interface

```bash
# SSH vào VPS
ssh user@your-vps-ip

# Di chuyển vào thư mục dự án
cd /opt/fbmanager

# Pull script mới nhất
git pull origin main

# Chạy script tự động
sudo bash update_web.sh
```

Sau khi chạy xong, truy cập: `http://YOUR_VPS_IP:8000`

### Cách 2: Cập nhật thủ công

Xem chi tiết tại [DEPLOYMENT.md](DEPLOYMENT.md)

## 📚 Hướng dẫn triển khai đầy đủ / Full Deployment Guide

Xem hướng dẫn chi tiết để triển khai ứng dụng lên VPS Ubuntu 24.04.3 LTS với Python 3.12.3:

- **[🇻🇳 Tiếng Việt](DEPLOYMENT.md)** - Hướng dẫn triển khai chi tiết
- **[🇬🇧 English](DEPLOYMENT_EN.md)** - Detailed deployment guide

## 🔄 Cập nhật & Deploy lại / Re-deploy & Update

### 1. 🚀 Deploy lại từ đầu (Clean install)

Sử dụng khi cần cài đặt lại hoàn toàn hoặc triển khai lên VPS mới:

```bash
# Xóa thư mục cũ và clone lại
cd ~
rm -rf fbmanager
git clone https://github.com/thinhnguyenict/fbmanager.git
cd fbmanager
chmod +x deploy.sh
./deploy.sh
```

### 2. 📝 Cập nhật code mới (Update)

Sử dụng khi có phiên bản mới từ repository:

```bash
# Pull code mới nhất
cd ~/fbmanager
git pull origin main

# Chạy lại deploy script
./deploy.sh
```

### 3. ⚡ Khởi động lại service

Sử dụng sau khi cập nhật code hoặc cấu hình:

```bash
# Khởi động lại service chính
sudo systemctl restart fbmanager

# Khởi động lại nginx (nếu có sử dụng)
sudo systemctl restart nginx

# Kiểm tra trạng thái service
sudo systemctl status fbmanager
```

### 4. ⚠️ Xem log khi gặp lỗi

Kiểm tra log để debug khi có vấn đề:

```bash
# Xem log real-time của service
sudo journalctl -u fbmanager -f

# Xem 100 dòng log gần nhất
sudo journalctl -u fbmanager -n 100 --no-pager

# Xem log file ứng dụng (nếu có cấu hình)
tail -f /var/log/fbmanager/app.log
```

## 📋 Tính năng / Features

- Quản lý tài khoản Facebook / Facebook account management
- Tự động hóa các tác vụ / Task automation
- Hỗ trợ Python 3.12.3
- Tương thích Ubuntu 24.04.3 LTS
- Dễ dàng triển khai lên VPS / Easy VPS deployment

## 🛠️ Yêu cầu hệ thống / System Requirements

- Ubuntu 24.04.3 LTS x86_64
- Python 3.12.3
- RAM: Tối thiểu 1GB (khuyến nghị 2GB+)
- Ổ cứng: Tối thiểu 10GB / Storage: Minimum 10GB

## 📝 License

MIT License
