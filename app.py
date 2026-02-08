#!/usr/bin/env python3
"""
FB Manager - Web Interface
Flask application for managing Facebook fanpages
"""

import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
from werkzeug.utils import secure_filename
import requests

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Validate secret key
if app.secret_key == 'dev-secret-key-change-in-production' and not os.getenv('DEBUG'):
    raise ValueError("SECRET_KEY must be set in production environment")

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure logging
LOG_FILE = os.getenv('LOG_FILE', '/var/log/fbmanager/web.log')
log_dir = Path(LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Simple user class for demo
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Demo users (replace with database in production)
USERS = {
    'admin': {'password': 'admin123', 'id': '1'}
}

@login_manager.user_loader
def load_user(user_id):
    for username, data in USERS.items():
        if data['id'] == user_id:
            return User(user_id, username)
    return None

# ==================== AUTHENTICATION ====================

@app.route('/')
def index():
    """Redirect to dashboard or login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Sanitize username to prevent log injection
        safe_username = username.replace('\n', '').replace('\r', '')
        
        if username in USERS and USERS[username]['password'] == password:
            user = User(USERS[username]['id'], username)
            login_user(user)
            session['username'] = username
            logger.info(f"User logged in: {safe_username}")
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"Failed login attempt for user: {safe_username}")
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    username = session.get('username', 'unknown')
    logout_user()
    session.clear()
    logger.info(f"User logged out: {username}")
    return redirect(url_for('login'))

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/api/status')
@login_required
def api_status():
    """Get system status"""
    return jsonify({
        'status': 'running',
        'fb_email': os.getenv('FB_EMAIL', 'Not configured'),
        'debug_mode': os.getenv('DEBUG', 'False')
    })

@app.route('/api/logs')
@login_required
def api_logs():
    """Get recent logs"""
    try:
        log_file = Path(LOG_FILE)
        if not log_file.exists():
            return jsonify({'error': 'Log file not found', 'logs': []})
        
        # Read last 50 lines
        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_logs = lines[-50:] if len(lines) > 50 else lines
        
        # Prevent XSS by using textContent in frontend
        return jsonify({'logs': [line.strip() for line in recent_logs]})
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return jsonify({'error': str(e), 'logs': []})

# ==================== FANPAGE MANAGEMENT ====================

@app.route('/fanpages')
@login_required
def fanpages():
    """Fanpage management page"""
    return render_template('fanpages.html', username=session.get('username'))

@app.route('/api/fanpages', methods=['GET'])
@login_required
def get_fanpages():
    """Get list of fanpages"""
    # TODO: Load from database
    # For now, return mock data
    fanpages = [
        {
            'id': '1',
            'name': 'My Fanpage 1',
            'page_id': '123456789',
            'access_token': 'EAAxxxxx...',
            'followers': 1250,
            'likes': 1180,
            'status': 'active'
        },
        {
            'id': '2', 
            'name': 'My Fanpage 2',
            'page_id': '987654321',
            'access_token': 'EAAyyyyy...',
            'followers': 2340,
            'likes': 2200,
            'status': 'active'
        }
    ]
    return jsonify({'fanpages': fanpages})

@app.route('/api/fanpages', methods=['POST'])
@login_required
def add_fanpage():
    """Add new fanpage"""
    data = request.get_json()
    # TODO: Save to database
    logger.info(f"Adding new fanpage: {data.get('name')}")
    return jsonify({'success': True, 'message': 'Fanpage added successfully'})

@app.route('/api/fanpages/<fanpage_id>', methods=['DELETE'])
@login_required
def delete_fanpage(fanpage_id):
    """Delete fanpage"""
    # TODO: Delete from database
    logger.info(f"Deleting fanpage: {fanpage_id}")
    return jsonify({'success': True, 'message': 'Fanpage deleted successfully'})

# ==================== POST MANAGEMENT ====================

@app.route('/posts')
@login_required
def posts():
    """Posts management page"""
    return render_template('posts.html', username=session.get('username'))

@app.route('/api/posts', methods=['GET'])
@login_required
def get_posts():
    """Get list of posts"""
    # Mock data
    posts = [
        {
            'id': '1',
            'fanpage_id': '1',
            'fanpage_name': 'My Fanpage 1',
            'content': 'Hello everyone! This is a test post.',
            'status': 'published',
            'scheduled_time': None,
            'published_time': '2026-02-07 10:30:00',
            'likes': 45,
            'comments': 12,
            'shares': 5
        },
        {
            'id': '2',
            'fanpage_id': '1',
            'fanpage_name': 'My Fanpage 1',
            'content': 'Coming soon: New product launch!',
            'status': 'scheduled',
            'scheduled_time': '2026-02-10 14:00:00',
            'published_time': None,
            'likes': 0,
            'comments': 0,
            'shares': 0
        }
    ]
    return jsonify({'posts': posts})

@app.route('/api/posts', methods=['POST'])
@login_required
def create_post():
    """Create new post"""
    data = request.get_json()
    logger.info(f"Creating post for fanpage: {data.get('fanpage_id')}")
    # TODO: Save to database and post to Facebook
    return jsonify({'success': True, 'message': 'Post created successfully'})

@app.route('/api/posts/<post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """Delete post"""
    logger.info(f"Deleting post: {post_id}")
    return jsonify({'success': True, 'message': 'Post deleted successfully'})

# ==================== MESSAGES MANAGEMENT ====================

@app.route('/messages')
@login_required
def messages():
    """Messages management page"""
    return render_template('messages.html', username=session.get('username'))

@app.route('/api/messages', methods=['GET'])
@login_required
def get_messages():
    """Get list of messages"""
    # Mock data
    messages = [
        {
            'id': '1',
            'fanpage_id': '1',
            'fanpage_name': 'My Fanpage 1',
            'sender_name': 'John Doe',
            'sender_id': '111111',
            'message': 'Hello, I have a question about your product',
            'time': '2026-02-08 09:15:00',
            'status': 'unread'
        },
        {
            'id': '2',
            'fanpage_id': '1',
            'fanpage_name': 'My Fanpage 1',
            'sender_name': 'Jane Smith',
            'sender_id': '222222',
            'message': 'When will you restock?',
            'time': '2026-02-08 08:45:00',
            'status': 'read'
        }
    ]
    return jsonify({'messages': messages})

@app.route('/api/messages/<message_id>/reply', methods=['POST'])
@login_required
def reply_message(message_id):
    """Reply to message"""
    data = request.get_json()
    logger.info(f"Replying to message {message_id}: {data.get('reply')}")
    return jsonify({'success': True, 'message': 'Reply sent successfully'})

# ==================== ANALYTICS ====================

@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard"""
    return render_template('analytics.html', username=session.get('username'))

@app.route('/api/analytics/overview', methods=['GET'])
@login_required
def get_analytics_overview():
    """Get analytics overview"""
    data = {
        'total_fanpages': 2,
        'total_followers': 3590,
        'total_posts_today': 5,
        'total_messages_unread': 12,
        'engagement_rate': 4.2,
        'growth_rate': 8.5
    }
    return jsonify(data)

@app.route('/api/analytics/chart', methods=['GET'])
@login_required
def get_analytics_chart():
    """Get analytics chart data"""
    # Last 7 days data
    chart_data = {
        'labels': ['Feb 2', 'Feb 3', 'Feb 4', 'Feb 5', 'Feb 6', 'Feb 7', 'Feb 8'],
        'followers': [3200, 3280, 3350, 3420, 3480, 3540, 3590],
        'engagement': [120, 145, 132, 168, 155, 178, 185],
        'posts': [2, 3, 1, 4, 2, 3, 5]
    }
    return jsonify(chart_data)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
