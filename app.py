from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
import requests
from config import Config
import urllib.parse

app = Flask(__name__)
app.config.from_object(Config)

# Facebook OAuth URLs
FACEBOOK_OAUTH_URL = "https://www.facebook.com/v18.0/dialog/oauth"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"

@app.route('/')
def index():
    """Home page - shows login or fanpage list"""
    if 'access_token' in session:
        return redirect(url_for('fanpages'))
    return render_template('index.html')

@app.route('/login')
def login():
    """Redirect to Facebook OAuth login"""
    params = {
        'client_id': app.config['FACEBOOK_APP_ID'],
        'redirect_uri': app.config['FACEBOOK_REDIRECT_URI'],
        'scope': 'pages_show_list,pages_read_engagement,pages_manage_posts,pages_read_user_content,read_insights',
        'response_type': 'code'
    }
    auth_url = f"{FACEBOOK_OAUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle Facebook OAuth callback"""
    code = request.args.get('code')
    if not code:
        flash('Đăng nhập thất bại', 'error')
        return redirect(url_for('index'))
    
    # Exchange code for access token
    params = {
        'client_id': app.config['FACEBOOK_APP_ID'],
        'client_secret': app.config['FACEBOOK_APP_SECRET'],
        'redirect_uri': app.config['FACEBOOK_REDIRECT_URI'],
        'code': code
    }
    
    try:
        response = requests.get(FACEBOOK_TOKEN_URL, params=params)
        data = response.json()
        
        if 'access_token' in data:
            session['access_token'] = data['access_token']
            
            # Get user info
            user_response = requests.get(
                f"{app.config['FACEBOOK_GRAPH_API']}/me",
                params={'access_token': session['access_token'], 'fields': 'id,name,email'}
            )
            user_data = user_response.json()
            session['user_name'] = user_data.get('name', 'User')
            session['user_id'] = user_data.get('id')
            
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('fanpages'))
        else:
            flash('Lỗi khi lấy access token', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Đã đăng xuất', 'info')
    return redirect(url_for('index'))

@app.route('/fanpages')
def fanpages():
    """List all fanpages managed by the user"""
    if 'access_token' not in session:
        return redirect(url_for('index'))
    
    try:
        # Get user's pages
        response = requests.get(
            f"{app.config['FACEBOOK_GRAPH_API']}/me/accounts",
            params={
                'access_token': session['access_token'],
                'fields': 'id,name,access_token,category,fan_count,picture'
            }
        )
        data = response.json()
        
        if 'data' in data:
            pages = data['data']
            return render_template('fanpages.html', pages=pages, user_name=session.get('user_name'))
        else:
            flash('Không thể lấy danh sách fanpage', 'error')
            return render_template('fanpages.html', pages=[], user_name=session.get('user_name'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return render_template('fanpages.html', pages=[], user_name=session.get('user_name'))

@app.route('/fanpage/<page_id>')
def fanpage_detail(page_id):
    """Show details and posts for a specific fanpage"""
    if 'access_token' not in session:
        return redirect(url_for('index'))
    
    try:
        # Get page access token
        response = requests.get(
            f"{app.config['FACEBOOK_GRAPH_API']}/me/accounts",
            params={'access_token': session['access_token']}
        )
        pages_data = response.json()
        
        page_access_token = None
        page_info = None
        for page in pages_data.get('data', []):
            if page['id'] == page_id:
                page_access_token = page['access_token']
                page_info = page
                break
        
        if not page_access_token:
            flash('Không tìm thấy fanpage', 'error')
            return redirect(url_for('fanpages'))
        
        # Store page access token in session
        session[f'page_token_{page_id}'] = page_access_token
        
        # Get page details
        page_response = requests.get(
            f"{app.config['FACEBOOK_GRAPH_API']}/{page_id}",
            params={
                'access_token': page_access_token,
                'fields': 'id,name,category,fan_count,picture,about,website'
            }
        )
        page_details = page_response.json()
        
        # Get posts with insights
        posts_response = requests.get(
            f"{app.config['FACEBOOK_GRAPH_API']}/{page_id}/posts",
            params={
                'access_token': page_access_token,
                'fields': 'id,message,created_time,full_picture,permalink_url,type,insights.metric(post_impressions,post_engaged_users,post_clicks),attachments{media_type,type,url,subattachments}'
            }
        )
        posts_data = posts_response.json()
        
        # Get videos
        videos_response = requests.get(
            f"{app.config['FACEBOOK_GRAPH_API']}/{page_id}/videos",
            params={
                'access_token': page_access_token,
                'fields': 'id,title,description,created_time,permalink_url,picture'
            }
        )
        videos_data = videos_response.json()
        
        return render_template(
            'fanpage_detail.html',
            page=page_details,
            posts=posts_data.get('data', []),
            videos=videos_data.get('data', []),
            user_name=session.get('user_name')
        )
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('fanpages'))

@app.route('/fanpage/<page_id>/post/<post_id>')
def post_detail(page_id, post_id):
    """Show detailed analytics for a specific post"""
    if 'access_token' not in session:
        return redirect(url_for('index'))
    
    page_token = session.get(f'page_token_{page_id}')
    if not page_token:
        flash('Không có quyền truy cập fanpage này', 'error')
        return redirect(url_for('fanpages'))
    
    try:
        # Get post details with insights
        response = requests.get(
            f"{app.config['FACEBOOK_GRAPH_API']}/{post_id}",
            params={
                'access_token': page_token,
                'fields': 'id,message,created_time,full_picture,permalink_url,type,insights'
            }
        )
        post_data = response.json()
        
        return render_template('post_detail.html', post=post_data, page_id=page_id, user_name=session.get('user_name'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('fanpage_detail', page_id=page_id))

@app.route('/fanpage/<page_id>/create_post', methods=['GET', 'POST'])
def create_post(page_id):
    """Create a new post on the fanpage"""
    if 'access_token' not in session:
        return redirect(url_for('index'))
    
    page_token = session.get(f'page_token_{page_id}')
    if not page_token:
        flash('Không có quyền truy cập fanpage này', 'error')
        return redirect(url_for('fanpages'))
    
    if request.method == 'GET':
        return render_template('create_post.html', page_id=page_id, user_name=session.get('user_name'))
    
    try:
        message = request.form.get('message')
        link = request.form.get('link')
        
        data = {'access_token': page_token}
        if message:
            data['message'] = message
        if link:
            data['link'] = link
        
        response = requests.post(
            f"{app.config['FACEBOOK_GRAPH_API']}/{page_id}/feed",
            data=data
        )
        result = response.json()
        
        if 'id' in result:
            flash('Đã tạo bài viết thành công!', 'success')
            return redirect(url_for('fanpage_detail', page_id=page_id))
        else:
            flash(f'Lỗi khi tạo bài viết: {result.get("error", {}).get("message", "Unknown error")}', 'error')
            return render_template('create_post.html', page_id=page_id, user_name=session.get('user_name'))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return render_template('create_post.html', page_id=page_id, user_name=session.get('user_name'))

@app.route('/fanpage/<page_id>/edit_post/<post_id>', methods=['GET', 'POST'])
def edit_post(page_id, post_id):
    """Edit an existing post"""
    if 'access_token' not in session:
        return redirect(url_for('index'))
    
    page_token = session.get(f'page_token_{page_id}')
    if not page_token:
        flash('Không có quyền truy cập fanpage này', 'error')
        return redirect(url_for('fanpages'))
    
    if request.method == 'GET':
        # Get current post data
        try:
            response = requests.get(
                f"{app.config['FACEBOOK_GRAPH_API']}/{post_id}",
                params={'access_token': page_token, 'fields': 'message'}
            )
            post_data = response.json()
            return render_template('edit_post.html', post=post_data, page_id=page_id, post_id=post_id, user_name=session.get('user_name'))
        except Exception as e:
            flash(f'Lỗi: {str(e)}', 'error')
            return redirect(url_for('fanpage_detail', page_id=page_id))
    
    try:
        message = request.form.get('message')
        
        response = requests.post(
            f"{app.config['FACEBOOK_GRAPH_API']}/{post_id}",
            data={'access_token': page_token, 'message': message}
        )
        result = response.json()
        
        if result.get('success'):
            flash('Đã cập nhật bài viết thành công!', 'success')
        else:
            flash(f'Lỗi khi cập nhật: {result.get("error", {}).get("message", "Unknown error")}', 'error')
        
        return redirect(url_for('fanpage_detail', page_id=page_id))
    except Exception as e:
        flash(f'Lỗi: {str(e)}', 'error')
        return redirect(url_for('fanpage_detail', page_id=page_id))

@app.route('/fanpage/<page_id>/delete_post/<post_id>', methods=['POST'])
def delete_post(page_id, post_id):
    """Delete a post"""
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    page_token = session.get(f'page_token_{page_id}')
    if not page_token:
        return jsonify({'error': 'No access to this page'}), 403
    
    try:
        response = requests.delete(
            f"{app.config['FACEBOOK_GRAPH_API']}/{post_id}",
            params={'access_token': page_token}
        )
        result = response.json()
        
        if result.get('success'):
            flash('Đã xóa bài viết thành công!', 'success')
            return jsonify({'success': True})
        else:
            return jsonify({'error': result.get('error', {}).get('message', 'Unknown error')}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
