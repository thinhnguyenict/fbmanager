# Giao diện Quản lý Cấu hình - FB Manager

## Giới thiệu

FB Manager cung cấp một giao diện web hiện đại để quản lý cấu hình ứng dụng thay vì phải SSH vào VPS và chỉnh sửa file `.env` thủ công. Giao diện này được xây dựng với Flask và Bootstrap 5, cung cấp trải nghiệm người dùng thân thiện và an toàn.

## Tính năng

### ✅ Bảo mật
- ✓ Xác thực admin với mật khẩu được mã hóa bcrypt
- ✓ Session-based authentication với timeout 30 phút
- ✓ CSRF protection trên tất cả form
- ✓ File .env được chmod 600 (chỉ owner đọc/ghi)
- ✓ Ghi log mọi thay đổi cấu hình với timestamp và IP

### ✅ Quản lý Cấu hình
- ✓ Form nhập liệu trực quan cho tất cả cài đặt
- ✓ Validation client-side và server-side
- ✓ Hiển thị giá trị hiện tại (mật khẩu hiển thị dạng ***)
- ✓ Confirmation dialog trước khi lưu thay đổi

### ✅ Backup & Restore
- ✓ Tự động backup file .env trước khi thay đổi
- ✓ Backup file đặt tên theo format: `.env.backup.YYYYMMDD_HHMMSS`
- ✓ Xem danh sách tất cả backup
- ✓ Khôi phục từ backup bất kỳ

### ✅ Giao diện
- ✓ Responsive design với Bootstrap 5
- ✓ Mobile-friendly
- ✓ Tooltips giải thích từng trường
- ✓ Visual feedback cho validation errors
- ✓ Loading spinner khi xử lý

## Cài đặt

### 1. Cài đặt dependencies

```bash
cd /opt/fbmanager
source venv/bin/activate
pip install flask flask-login flask-wtf wtforms bcrypt
```

### 2. Tạo admin credentials

Chạy script setup để tạo tài khoản admin:

```bash
python3 setup_admin.py
```

Script sẽ hỏi:
- Username (mặc định: admin)
- Password (để trống để tự động generate)

**Lưu ý:** Mật khẩu chỉ hiển thị một lần duy nhất, hãy lưu lại!

### 3. Khởi động web server

```bash
python3 app.py
```

Mặc định server chạy trên `http://127.0.0.1:5000`

Để thay đổi host/port, set biến môi trường:

```bash
FLASK_HOST=0.0.0.0 FLASK_PORT=8080 python3 app.py
```

## Sử dụng

### Đăng nhập

1. Mở trình duyệt và truy cập: `http://localhost:5000/admin/login`
2. Nhập username và password đã tạo
3. Click "Đăng nhập"

### Cấu hình

Sau khi đăng nhập, bạn sẽ thấy form cấu hình với các section:

#### 1. Cấu hình Facebook
- **Facebook Email** (*): Email đăng nhập Facebook
- **Facebook Password** (*): Mật khẩu Facebook
- **Facebook App ID**: ID ứng dụng Facebook (tùy chọn)
- **Facebook App Secret**: Secret key ứng dụng (tùy chọn)
- **Facebook Redirect URI**: URL callback cho OAuth (tùy chọn)

#### 2. Cấu hình Ứng dụng
- **Debug Mode**: Bật/tắt chế độ debug
- **Log Level**: Mức độ chi tiết log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Log File Path**: Đường dẫn file log

#### 3. Cấu hình Proxy (Tùy chọn)
- **Proxy Host**: Địa chỉ proxy server
- **Proxy Port**: Cổng proxy (1-65535)
- **Proxy Username**: Username cho proxy authentication
- **Proxy Password**: Password cho proxy authentication

#### 4. Cấu hình Trình duyệt
- **Headless Browser**: Chạy trình duyệt ở chế độ ẩn
- **Browser Timeout**: Thời gian chờ tối đa (giây)

### Lưu cấu hình

1. Điền các thông tin cần thay đổi
2. Click "Lưu cấu hình"
3. Xác nhận trong dialog
4. Hệ thống sẽ:
   - Tạo backup file .env hiện tại
   - Validate dữ liệu nhập
   - Lưu cấu hình mới
   - Ghi log thay đổi

### Backup & Khôi phục

1. Click "Sao lưu & Khôi phục"
2. Xem danh sách các backup có sẵn
3. Click "Khôi phục" trên backup muốn restore
4. Xác nhận để khôi phục

### Khởi động lại Service

Sau khi thay đổi cấu hình, click "Khởi động lại dịch vụ" để áp dụng:

1. Click "Khởi động lại dịch vụ"
2. Xác nhận
3. Hệ thống sẽ restart fbmanager service

**Lưu ý:** Chức năng này yêu cầu systemd service đã được cấu hình.

## API Endpoints

Các endpoint có sẵn:

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/` | Redirect đến login |
| GET | `/admin/login` | Trang đăng nhập |
| POST | `/admin/login` | Xử lý đăng nhập |
| GET | `/admin/logout` | Đăng xuất |
| GET | `/admin/setup` | Form cấu hình (yêu cầu đăng nhập) |
| POST | `/admin/setup` | Lưu cấu hình (yêu cầu đăng nhập) |
| GET | `/admin/backups` | Lấy danh sách backup (JSON) |
| POST | `/admin/restore` | Khôi phục từ backup |
| POST | `/admin/restart-service` | Khởi động lại service |

## Bảo mật

### File permissions

Sau khi cài đặt, kiểm tra quyền file:

```bash
# Credentials file
chmod 600 .admin_credentials

# Env file
chmod 600 .env

# Backup directory
chmod 700 backups/
```

### Firewall

**Khuyến nghị:** Chỉ cho phép truy cập từ localhost hoặc IP whitelist.

Để chặn truy cập từ bên ngoài:

```bash
# Chỉ bind vào localhost
FLASK_HOST=127.0.0.1 python3 app.py
```

Hoặc dùng firewall:

```bash
# Chỉ cho phép local access
sudo ufw deny 5000
```

### Session Security

- Session timeout: 30 phút không hoạt động
- CSRF token được validate trên mọi form
- Session cookie có HttpOnly flag
- SameSite=Lax để chống CSRF

### Logging

Mọi thay đổi cấu hình được ghi log với:
- Timestamp
- IP address
- Username
- Action type
- Chi tiết thay đổi

Xem log:

```bash
sudo journalctl -u fbmanager -f | grep "CONFIG CHANGE"
```

## Production Deployment

### Sử dụng WSGI Server

**Không nên** dùng Flask development server trong production. Sử dụng Gunicorn hoặc uWSGI:

```bash
# Cài đặt Gunicorn
pip install gunicorn

# Chạy với Gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:create_app()
```

### Nginx Reverse Proxy

Cấu hình Nginx để reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /admin {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Systemd Service

Tạo service riêng cho web interface:

```bash
sudo nano /etc/systemd/system/fbmanager-web.service
```

```ini
[Unit]
Description=FB Manager Web Interface
After=network.target

[Service]
Type=simple
User=fbmanager
WorkingDirectory=/opt/fbmanager
Environment="PATH=/opt/fbmanager/venv/bin"
Environment="FLASK_HOST=127.0.0.1"
Environment="FLASK_PORT=5000"
ExecStart=/opt/fbmanager/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:create_app()
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable fbmanager-web
sudo systemctl start fbmanager-web
```

## Troubleshooting

### 1. Không thể đăng nhập

**Kiểm tra credentials:**
```bash
ls -la .admin_credentials
cat .admin_credentials
```

**Tạo lại credentials:**
```bash
rm .admin_credentials
python3 setup_admin.py
```

### 2. Lỗi "Permission denied" khi lưu .env

**Kiểm tra quyền file:**
```bash
ls -la .env
```

**Sửa quyền:**
```bash
chmod 600 .env
chown $USER:$USER .env
```

### 3. Session timeout quá nhanh

Thay đổi timeout trong `app.py`:

```python
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 giờ
```

### 4. Port đã được sử dụng

```bash
# Kiểm tra process đang dùng port
lsof -i :5000

# Dừng process
kill <PID>

# Hoặc dùng port khác
FLASK_PORT=8080 python3 app.py
```

## Cấu trúc Code

```
/opt/fbmanager/
├── app.py                      # Main Flask application
├── setup_admin.py             # Admin credentials setup
├── config_manager/
│   ├── __init__.py
│   ├── auth.py                # Authentication logic
│   ├── env_handler.py         # .env file operations
│   ├── forms.py               # WTForms definitions
│   ├── routes.py              # Flask routes
│   ├── templates/
│   │   ├── base.html          # Base template
│   │   ├── login.html         # Login page
│   │   └── config.html        # Configuration form
│   └── static/
│       ├── css/
│       │   └── config.css     # Custom styles
│       └── js/
│           └── config.js      # Client-side logic
└── backups/                   # Backup directory
    └── .env.backup.*
```

## Phát triển

### Thêm field mới

1. Thêm vào `.env.example`:
```bash
NEW_FIELD=default_value
```

2. Thêm vào `forms.py`:
```python
new_field = StringField('New Field', validators=[Optional()])
```

3. Thêm vào `config.html`:
```html
<div class="mb-3">
    {{ form.new_field.label(class="form-label") }}
    {{ form.new_field(class="form-control") }}
</div>
```

4. Xử lý trong `routes.py`:
```python
env_vars['NEW_FIELD'] = form.new_field.data or ''
```

### Chạy tests

```bash
cd /opt/fbmanager
python3 -m pytest tests/
```

## Changelog

### v1.0.0 (2024-02-08)
- ✓ Initial release
- ✓ Admin authentication
- ✓ Configuration management
- ✓ Backup/restore functionality
- ✓ Responsive UI with Bootstrap 5
- ✓ CSRF protection
- ✓ Session management
- ✓ Validation

## License

MIT License - See LICENSE file for details

## Support

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra phần Troubleshooting ở trên
2. Xem log: `sudo journalctl -u fbmanager -f`
3. Tạo issue trên GitHub

---

**Lưu ý Bảo mật:** Giao diện cấu hình có quyền ghi file .env nên cực kỳ nhạy cảm. Chỉ cho phép truy cập từ localhost hoặc IP whitelist, và luôn sử dụng mật khẩu mạnh cho admin.
