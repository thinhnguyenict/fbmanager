# Facebook Fanpage Manager

Ứng dụng quản lý các fanpage của Facebook chạy trên web server, cho phép người dùng quản lý bài viết, xem thống kê và nhiều tính năng khác.

## Tính năng

- ✅ Đăng nhập bằng tài khoản Facebook cá nhân
- ✅ Xem danh sách các fanpage đang quản lý
- ✅ Xem chi tiết bài viết, video, và link của fanpage
- ✅ Hiển thị thống kê chi tiết: reach, engagement, click rate
- ✅ Tạo bài viết mới
- ✅ Chỉnh sửa bài viết
- ✅ Xóa bài viết
- ✅ Giao diện responsive, thân thiện với người dùng

## Công nghệ sử dụng

- **Backend**: Python Flask
- **Frontend**: Bootstrap 5, Font Awesome
- **API**: Facebook Graph API v18.0
- **Authentication**: Facebook OAuth 2.0

## Yêu cầu hệ thống

- Python 3.8 trở lên
- Tài khoản Facebook Developer
- Facebook App với quyền truy cập Pages API

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/thinhnguyenict/fbmanager.git
cd fbmanager
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Tạo Facebook App

1. Truy cập [Facebook Developers](https://developers.facebook.com/)
2. Tạo một App mới
3. Thêm "Facebook Login" product
4. Cấu hình Valid OAuth Redirect URIs: `http://localhost:5000/callback`
5. Lấy App ID và App Secret

### 4. Cấu hình môi trường

Tạo file `.env` từ file mẫu:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:

```
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_REDIRECT_URI=http://localhost:5000/callback
SECRET_KEY=your_secret_key_here
```

### 5. Chạy ứng dụng

```bash
python app.py
```

Ứng dụng sẽ chạy tại `http://localhost:5000`

## Sử dụng

### Đăng nhập

1. Truy cập trang chủ
2. Click "Đăng nhập với Facebook"
3. Cho phép ứng dụng truy cập thông tin fanpage

### Quản lý Fanpage

1. Sau khi đăng nhập, bạn sẽ thấy danh sách các fanpage
2. Click vào fanpage để xem chi tiết
3. Xem bài viết, video và thống kê
4. Tạo, sửa, xóa bài viết

### Quyền truy cập cần thiết

Ứng dụng yêu cầu các quyền sau:
- `pages_show_list`: Xem danh sách fanpage
- `pages_read_engagement`: Đọc thống kê engagement
- `pages_manage_posts`: Quản lý bài viết
- `pages_read_user_content`: Đọc nội dung
- `read_insights`: Đọc thông tin thống kê

## Cấu trúc thư mục

```
fbmanager/
├── app.py                 # File chính của ứng dụng Flask
├── config.py              # Cấu hình ứng dụng
├── requirements.txt       # Dependencies Python
├── .env.example          # File mẫu cấu hình
├── .gitignore            # Git ignore file
├── README.md             # Tài liệu này
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── fanpages.html
│   ├── fanpage_detail.html
│   ├── post_detail.html
│   ├── create_post.html
│   └── edit_post.html
└── static/               # Static files
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

## Lưu ý bảo mật

- ⚠️ Không commit file `.env` lên Git
- ⚠️ Sử dụng HTTPS khi deploy production
- ⚠️ Thay đổi `SECRET_KEY` thành một giá trị ngẫu nhiên mạnh
- ⚠️ Kiểm tra và cập nhật quyền truy cập API thường xuyên

## Troubleshooting

### Lỗi OAuth Redirect URI

Đảm bảo URL trong `.env` khớp với URL trong Facebook App Settings.

### Không lấy được danh sách fanpage

- Kiểm tra quyền truy cập của App
- Đảm bảo tài khoản Facebook có quyền quản lý fanpage
- Xem lại App Review status trong Facebook Developers

### Lỗi khi tạo/sửa/xóa bài viết

- Kiểm tra quyền `pages_manage_posts`
- Đảm bảo App đã được approve các quyền cần thiết

## Phát triển thêm

Các tính năng có thể thêm vào:
- Upload ảnh/video khi tạo bài viết
- Lên lịch đăng bài
- Trả lời bình luận
- Quản lý tin nhắn inbox
- Báo cáo thống kê nâng cao
- Export dữ liệu

## Giấy phép

MIT License

## Liên hệ

- GitHub: [thinhnguyenict](https://github.com/thinhnguyenict)

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo Pull Request hoặc Issue để đóng góp.
