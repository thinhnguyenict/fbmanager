# fbmanager
Quản lý FB

## 🚀 Quick Start / Khởi động nhanh

```bash
wget https://raw.githubusercontent.com/thinhnguyenict/fbmanager/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

📖 **[Quick Start Guide / Hướng dẫn nhanh](QUICKSTART.md)**

## 🌐 Web Admin Interface

Sau khi deployment, bạn có thể truy cập giao diện quản lý web tại:

```
http://YOUR_VPS_IP:8000
```

**Đăng nhập mặc định:**
- Username: `admin`
- Password: (xem trong file `.env`)

**⚠️ Lưu ý bảo mật:**
- Đổi `ADMIN_PASSWORD` trong file `.env` ngay sau khi cài đặt
- Đổi `SECRET_KEY` thành giá trị ngẫu nhiên
- Cân nhắc thiết lập SSL/HTTPS cho production

### Chạy web interface

```bash
cd /opt/fbmanager
source venv/bin/activate
python app.py
```

Hoặc sử dụng systemd service (xem DEPLOYMENT.md)

## 📚 Hướng dẫn triển khai đầy đủ / Full Deployment Guide

Xem hướng dẫn chi tiết để triển khai ứng dụng lên VPS Ubuntu 24.04.3 LTS với Python 3.12.3:

- **[🇻🇳 Tiếng Việt](DEPLOYMENT.md)** - Hướng dẫn triển khai chi tiết
- **[🇬🇧 English](DEPLOYMENT_EN.md)** - Detailed deployment guide

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
