# FB Manager - Web Interface Documentation

## Tổng quan

FB Manager Web Interface là giao diện quản lý Facebook Fanpage qua trình duyệt web, cung cấp đầy đủ các tính năng để quản lý fanpage, bài viết, tin nhắn và xem thống kê.

## Tính năng chính

### 1. 🔐 Xác thực người dùng
- Đăng nhập an toàn với session management
- Bảo vệ tất cả các routes với authentication
- Logout an toàn

### 2. 📊 Dashboard
- Xem trạng thái hệ thống
- Theo dõi system logs real-time
- Hiển thị cấu hình FB email và debug mode

### 3. 📄 Quản lý Fanpage
- Xem danh sách fanpages
- Thêm fanpage mới với Page ID và Access Token
- Xóa fanpage
- Hiển thị số followers và likes cho mỗi fanpage

### 4. 📝 Quản lý bài viết
- Xem danh sách bài viết
- Tạo bài viết mới
- Lên lịch đăng bài
- Xem thống kê (likes, comments, shares)
- Xóa bài viết

### 5. 💬 Quản lý tin nhắn
- Xem danh sách tin nhắn
- Trả lời tin nhắn
- Đánh dấu đã đọc/chưa đọc
- Real-time updates (refresh mỗi 30 giây)

### 6. 📈 Thống kê & Analytics
- Dashboard với các metrics cards:
  - Tổng số Fanpage
  - Tổng Followers
  - Bài viết hôm nay
  - Tin nhắn chưa đọc
- Biểu đồ tăng trưởng followers (7 ngày qua)
- Biểu đồ engagement rate
- Biểu đồ số lượng bài viết
- Sử dụng Chart.js cho visualization

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

Dependencies được thêm:
- `flask>=3.0.0` - Web framework
- `flask-login>=0.6.3` - User session management
- `sqlalchemy>=2.0.0` - Database ORM
- `requests>=2.31.0` - HTTP requests (đã có sẵn)

### 2. Cấu hình môi trường

Tạo file `.env` trong thư mục gốc:

```bash
# Security
SECRET_KEY=your-secret-key-here-change-in-production

# Server configuration
PORT=5000
DEBUG=True

# Facebook credentials (optional for web interface)
FB_EMAIL=your-facebook-email@example.com
FB_PASSWORD=your-facebook-password

# Logging
LOG_FILE=/var/log/fbmanager/web.log
```

**⚠️ QUAN TRỌNG:** 
- Đổi `SECRET_KEY` trong production
- Không commit file `.env` vào git
- Set `DEBUG=False` trong production

### 3. Tạo thư mục logs

```bash
sudo mkdir -p /var/log/fbmanager
sudo chown $USER:$USER /var/log/fbmanager
```

Hoặc sử dụng thư mục tạm:
```bash
mkdir -p /tmp/fbmanager-logs
```

## Chạy ứng dụng

### Development mode

```bash
python3 app.py
```

Ứng dụng sẽ chạy tại: http://localhost:5000

### Production mode

Sử dụng production WSGI server như Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Hoặc với systemd service (xem DEPLOYMENT.md)

## Đăng nhập

**Default credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Đổi mật khẩu mặc định trong production!**

Để thêm user mới, chỉnh sửa dict `USERS` trong `app.py`:

```python
USERS = {
    'admin': {'password': 'new-secure-password', 'id': '1'},
    'user2': {'password': 'password2', 'id': '2'}
}
```

## Cấu trúc dự án

```
fbmanager/
├── app.py                 # Flask application chính
├── models.py             # Database models (SQLAlchemy)
├── fb_api.py            # Facebook Graph API helper
├── templates/           # HTML templates
│   ├── login.html       # Trang đăng nhập
│   ├── dashboard.html   # Dashboard chính
│   ├── fanpages.html    # Quản lý fanpages
│   ├── posts.html       # Quản lý bài viết
│   ├── messages.html    # Quản lý tin nhắn
│   └── analytics.html   # Thống kê
├── main.py              # Original CLI application
└── requirements.txt     # Python dependencies
```

## API Endpoints

### Authentication
- `GET /` - Redirect to dashboard or login
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout

### Dashboard
- `GET /dashboard` - Main dashboard
- `GET /api/status` - System status
- `GET /api/logs` - Recent logs

### Fanpages
- `GET /fanpages` - Fanpage management page
- `GET /api/fanpages` - Get list of fanpages
- `POST /api/fanpages` - Add new fanpage
- `DELETE /api/fanpages/<id>` - Delete fanpage

### Posts
- `GET /posts` - Posts management page
- `GET /api/posts` - Get list of posts
- `POST /api/posts` - Create new post
- `DELETE /api/posts/<id>` - Delete post

### Messages
- `GET /messages` - Messages page
- `GET /api/messages` - Get list of messages
- `POST /api/messages/<id>/reply` - Reply to message

### Analytics
- `GET /analytics` - Analytics dashboard
- `GET /api/analytics/overview` - Overview metrics
- `GET /api/analytics/chart` - Chart data

## Database

### Khởi tạo database

```python
from models import init_db, get_session

# Initialize database (tạo tables)
engine = init_db('sqlite:///fbmanager.db')

# Get session để làm việc với database
session = get_session(engine)
```

### Database Models

**Fanpage:**
- id, name, page_id, access_token
- followers, likes, status
- created_at

**Post:**
- id, fanpage_id, content
- status (draft/scheduled/published)
- scheduled_time, published_time
- likes, comments, shares

**Message:**
- id, fanpage_id, sender_id, sender_name
- message, status (unread/read/replied)
- created_at

## Facebook Graph API

File `fb_api.py` cung cấp wrapper cho Facebook Graph API v18.0:

```python
from fb_api import FacebookAPI

# Initialize với access token
fb = FacebookAPI(access_token='your-page-access-token')

# Get page info
info = fb.get_page_info(page_id='123456789')

# Create post
result = fb.create_post(page_id='123456789', message='Hello World!')

# Get posts
posts = fb.get_posts(page_id='123456789', limit=25)

# Get conversations
convos = fb.get_conversations(page_id='123456789')

# Send message
fb.send_message(recipient_id='user-id', message='Thanks!')
```

## Security Features

1. **Secret Key Validation:** Kiểm tra SECRET_KEY trong production
2. **Path Traversal Prevention:** Bảo vệ khi đọc log files
3. **XSS Prevention:** Sử dụng textContent trong JavaScript
4. **Log Injection Prevention:** Sanitize username khi log
5. **Authentication:** Tất cả routes được bảo vệ với @login_required
6. **Session Management:** Secure session với Flask-Login

## Responsive Design

Giao diện được thiết kế responsive, hoạt động tốt trên:
- Desktop (1200px+)
- Tablet (768px - 1200px)  
- Mobile (< 768px)

## Tùy chỉnh

### Thay đổi màu sắc chính

Chỉnh sửa CSS trong các template files:

```css
/* Màu primary */
.navbar { background: #667eea; }  /* Purple gradient */
.sidebar-menu a.active { color: #667eea; }

/* Thay đổi thành màu khác, ví dụ blue */
.navbar { background: #4285f4; }
.sidebar-menu a.active { color: #4285f4; }
```

### Thêm tính năng mới

1. Thêm route trong `app.py`
2. Tạo template HTML mới
3. Thêm link vào sidebar menu
4. Implement API endpoint nếu cần

## Troubleshooting

### Port đã được sử dụng
```bash
# Tìm process đang dùng port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Permission denied khi tạo log file
```bash
# Sử dụng thư mục tmp thay vì /var/log
LOG_FILE=/tmp/fbmanager-logs/web.log
```

### Chart.js không load
- Kiểm tra internet connection
- Kiểm tra ad blocker có block CDN không
- Download Chart.js local nếu cần

### Database errors
```bash
# Xóa database và tạo lại
rm fbmanager.db
python3 -c "from models import init_db; init_db()"
```

## Roadmap

- [ ] Implement database persistence (thay mock data)
- [ ] Real Facebook API integration
- [ ] User management UI
- [ ] Auto-reply với keyword matching
- [ ] Scheduled posts với APScheduler
- [ ] Export analytics to CSV/PDF
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Push notifications cho tin nhắn mới

## License

MIT License - Xem file LICENSE để biết thêm chi tiết
