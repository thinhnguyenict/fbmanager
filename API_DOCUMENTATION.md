# API Documentation

## Facebook Graph API Integration

Ứng dụng này sử dụng Facebook Graph API v18.0 để tương tác với fanpages.

## Endpoints sử dụng

### 1. User Authentication

**Endpoint:** `/me`
- **Mục đích:** Lấy thông tin user sau khi đăng nhập
- **Fields:** `id`, `name`, `email`

### 2. Get User's Pages

**Endpoint:** `/me/accounts`
- **Mục đích:** Lấy danh sách fanpage mà user quản lý
- **Fields:** `id`, `name`, `access_token`, `category`, `fan_count`, `picture`

### 3. Get Page Details

**Endpoint:** `/{page_id}`
- **Mục đích:** Lấy thông tin chi tiết của fanpage
- **Fields:** `id`, `name`, `category`, `fan_count`, `picture`, `about`, `website`

### 4. Get Page Posts

**Endpoint:** `/{page_id}/posts`
- **Mục đích:** Lấy danh sách bài viết của fanpage
- **Fields:** 
  - `id`, `message`, `created_time`, `full_picture`
  - `permalink_url`, `type`
  - `insights.metric(post_impressions,post_engaged_users,post_clicks)`
  - `attachments{media_type,type,url,subattachments}`

### 5. Get Page Videos

**Endpoint:** `/{page_id}/videos`
- **Mục đích:** Lấy danh sách video của fanpage
- **Fields:** `id`, `title`, `description`, `created_time`, `permalink_url`, `picture`

### 6. Get Post Details

**Endpoint:** `/{post_id}`
- **Mục đích:** Lấy thông tin chi tiết của một bài viết
- **Fields:** `id`, `message`, `created_time`, `full_picture`, `permalink_url`, `type`, `insights`

### 7. Create Post

**Endpoint:** `/{page_id}/feed` (POST)
- **Mục đích:** Tạo bài viết mới
- **Parameters:**
  - `message`: Nội dung bài viết (bắt buộc)
  - `link`: URL để chia sẻ (tùy chọn)
  - `access_token`: Page access token

### 8. Update Post

**Endpoint:** `/{post_id}` (POST)
- **Mục đích:** Cập nhật bài viết
- **Parameters:**
  - `message`: Nội dung mới
  - `access_token`: Page access token

### 9. Delete Post

**Endpoint:** `/{post_id}` (DELETE)
- **Mục đích:** Xóa bài viết
- **Parameters:**
  - `access_token`: Page access token

## Permissions (Quyền truy cập)

### Quyền cần thiết

1. **pages_show_list**
   - Cho phép xem danh sách fanpage

2. **pages_read_engagement**
   - Cho phép đọc thông tin engagement (likes, comments, shares)

3. **pages_manage_posts**
   - Cho phép tạo, sửa, xóa bài viết

4. **pages_read_user_content**
   - Cho phép đọc nội dung của fanpage

5. **read_insights**
   - Cho phép đọc insights và thống kê

## Insights Metrics

### Post Insights

Các metric có thể lấy cho bài viết:

1. **post_impressions**
   - Số lần bài viết được hiển thị
   - Tương đương "Reach"

2. **post_engaged_users**
   - Số người tương tác với bài viết
   - Bao gồm: likes, comments, shares, clicks

3. **post_clicks**
   - Số lượt click vào bài viết
   - Bao gồm clicks vào links, photos, etc.

4. **post_reactions_by_type_total**
   - Phân loại reactions (like, love, wow, etc.)

5. **post_video_views** (cho video)
   - Số lượt xem video

## Response Examples

### Get Pages Response

```json
{
  "data": [
    {
      "id": "123456789",
      "name": "My Fanpage",
      "access_token": "page_access_token_here",
      "category": "Brand",
      "fan_count": 10000,
      "picture": {
        "data": {
          "url": "https://..."
        }
      }
    }
  ]
}
```

### Get Posts Response

```json
{
  "data": [
    {
      "id": "123456789_987654321",
      "message": "Hello world!",
      "created_time": "2024-01-01T10:00:00+0000",
      "full_picture": "https://...",
      "permalink_url": "https://facebook.com/...",
      "type": "photo",
      "insights": {
        "data": [
          {
            "name": "post_impressions",
            "values": [
              {
                "value": 5000
              }
            ]
          }
        ]
      }
    }
  ]
}
```

## Error Handling

### Common Errors

1. **OAuthException**
   - Token hết hạn hoặc không hợp lệ
   - Solution: Đăng nhập lại

2. **Insufficient permissions**
   - Thiếu quyền truy cập
   - Solution: Cấp thêm quyền trong Facebook App

3. **Invalid parameter**
   - Tham số không hợp lệ
   - Solution: Kiểm tra lại tham số gửi đi

4. **Rate limit exceeded**
   - Gọi API quá nhiều
   - Solution: Thêm delay, implement caching

## Rate Limits

Facebook có giới hạn số lượng API calls:

- **User-level:** 200 calls/hour
- **Page-level:** Varies by page size
- **App-level:** Varies by app tier

### Best Practices

1. Cache kết quả khi có thể
2. Batch requests khi có thể
3. Sử dụng webhooks thay vì polling
4. Implement exponential backoff

## Testing

### Testing with Graph API Explorer

1. Truy cập [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Chọn app của bạn
3. Generate access token với quyền cần thiết
4. Test các endpoints

### Example Test Calls

```bash
# Get user info
curl -G "https://graph.facebook.com/v18.0/me" \
  -d "access_token=YOUR_TOKEN" \
  -d "fields=id,name,email"

# Get pages
curl -G "https://graph.facebook.com/v18.0/me/accounts" \
  -d "access_token=YOUR_TOKEN"

# Get page posts
curl -G "https://graph.facebook.com/v18.0/PAGE_ID/posts" \
  -d "access_token=PAGE_TOKEN" \
  -d "fields=message,created_time"
```

## Troubleshooting

### Cannot get insights

- Insights chỉ available sau 24h của bài viết
- Một số metrics cần quyền đặc biệt
- Page phải đủ lượng follower

### Token expires

- User token: Hết hạn sau 60 ngày
- Page token: Không hết hạn nếu là long-lived token
- Solution: Implement token refresh

### Missing data

- Một số fields require extra permissions
- Kiểm tra App Review status
- Verify permissions được granted

## Resources

- [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api/)
- [Facebook for Developers](https://developers.facebook.com/)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
