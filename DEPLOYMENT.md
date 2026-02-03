# Hướng dẫn triển khai Production

## Triển khai lên các nền tảng phổ biến

### 1. Heroku

#### Bước 1: Tạo file Procfile

```
web: gunicorn app:app
```

#### Bước 2: Cập nhật requirements.txt

Thêm `gunicorn` vào file requirements.txt:

```
Flask==3.0.0
requests==2.31.0
python-dotenv==1.0.0
Werkzeug==3.0.1
gunicorn==21.2.0
```

#### Bước 3: Deploy

```bash
# Đăng nhập Heroku
heroku login

# Tạo app mới
heroku create your-app-name

# Set environment variables
heroku config:set FACEBOOK_APP_ID=your_app_id
heroku config:set FACEBOOK_APP_SECRET=your_app_secret
heroku config:set FACEBOOK_REDIRECT_URI=https://your-app-name.herokuapp.com/callback
heroku config:set SECRET_KEY=your_random_secret_key

# Deploy
git push heroku main

# Mở app
heroku open
```

### 2. Railway

#### Bước 1: Tạo tài khoản trên Railway.app

#### Bước 2: Kết nối GitHub repository

#### Bước 3: Thiết lập biến môi trường trong Railway dashboard

```
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_REDIRECT_URI=https://your-app.railway.app/callback
SECRET_KEY=your_random_secret_key
```

#### Bước 4: Deploy tự động

Railway sẽ tự động deploy khi có commit mới.

### 3. PythonAnywhere

#### Bước 1: Upload code lên PythonAnywhere

```bash
# SSH vào PythonAnywhere
ssh username@ssh.pythonanywhere.com

# Clone repository
git clone https://github.com/thinhnguyenict/fbmanager.git

# Tạo virtualenv
mkvirtualenv --python=/usr/bin/python3.10 fbmanager

# Cài đặt dependencies
cd fbmanager
pip install -r requirements.txt
```

#### Bước 2: Cấu hình Web App trong dashboard

- Web framework: Flask
- Python version: 3.10
- Source code: /home/username/fbmanager
- WSGI file: /var/www/username_pythonanywhere_com_wsgi.py

#### Bước 3: Chỉnh sửa WSGI file

```python
import sys
import os

project_home = '/home/username/fbmanager'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from dotenv import load_dotenv
project_folder = os.path.expanduser(project_home)
load_dotenv(os.path.join(project_folder, '.env'))

from app import app as application
```

### 4. DigitalOcean App Platform

#### Bước 1: Tạo app.yaml

```yaml
name: fbmanager
services:
- name: web
  github:
    repo: thinhnguyenict/fbmanager
    branch: main
  run_command: gunicorn app:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: FACEBOOK_APP_ID
    scope: RUN_TIME
    value: ${FACEBOOK_APP_ID}
  - key: FACEBOOK_APP_SECRET
    scope: RUN_TIME
    value: ${FACEBOOK_APP_SECRET}
  - key: FACEBOOK_REDIRECT_URI
    scope: RUN_TIME
    value: ${FACEBOOK_REDIRECT_URI}
  - key: SECRET_KEY
    scope: RUN_TIME
    value: ${SECRET_KEY}
```

## Bảo mật Production

### 1. Tạo SECRET_KEY mạnh

```python
import secrets
print(secrets.token_hex(32))
```

### 2. Sử dụng HTTPS

Đảm bảo ứng dụng chạy trên HTTPS trong production. Cập nhật `FACEBOOK_REDIRECT_URI` thành `https://`.

### 3. Cập nhật Facebook App Settings

- Thêm production domain vào "App Domains"
- Cập nhật "Valid OAuth Redirect URIs" với production URL
- Tắt "Development Mode" khi sẵn sàng

### 4. Environment Variables

Không bao giờ commit file `.env` vào Git. Sử dụng biến môi trường của platform để lưu trữ thông tin nhạy cảm.

### 5. Rate Limiting

Cân nhắc thêm rate limiting để tránh abuse:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## Monitoring và Logging

### 1. Logging

Thêm logging trong production:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('fbmanager.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('FB Manager startup')
```

### 2. Error Tracking

Cân nhắc sử dụng Sentry cho error tracking:

```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
)
```

## Performance Optimization

### 1. Caching

Sử dụng Flask-Caching để cache dữ liệu từ Facebook API:

```bash
pip install Flask-Caching
```

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/fanpages')
@cache.cached(timeout=300)  # Cache 5 phút
def fanpages():
    # ...
```

### 2. Database

Nếu cần lưu trữ dữ liệu lâu dài, cân nhắc thêm database:

```bash
pip install Flask-SQLAlchemy
```

## Backup và Recovery

- Backup thường xuyên biến môi trường
- Giữ bản copy của Facebook App ID và Secret
- Document quá trình recovery trong trường hợp mất access

## Checklist Deploy

- [ ] Đã thiết lập tất cả biến môi trường
- [ ] Đã cập nhật FACEBOOK_REDIRECT_URI với production URL
- [ ] Đã cập nhật Facebook App settings
- [ ] Đã tạo SECRET_KEY ngẫu nhiên mạnh
- [ ] Đã enable HTTPS
- [ ] Đã test OAuth flow hoàn chỉnh
- [ ] Đã thiết lập logging
- [ ] Đã thiết lập monitoring
- [ ] Đã test tất cả tính năng CRUD
- [ ] Đã review và test bảo mật
