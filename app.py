#!/usr/bin/env python3
"""
FB Manager - Web Admin Interface
"""

import os
import re
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)

# Validate SECRET_KEY is configured
secret_key = os.getenv('SECRET_KEY')
if not secret_key or secret_key == 'your-secret-key-change-this' or len(secret_key) < 16:
    raise ValueError("SECRET_KEY must be set in environment with at least 16 characters. "
                     "Please configure SECRET_KEY in your .env file.")
app.secret_key = secret_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MAX_LOG_LINES = 100  # Maximum number of log lines to return

# Simple authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Sanitize username for logging (alphanumeric, dash, underscore, dot only)
        safe_username = re.sub(r'[^a-zA-Z0-9._@-]', '', username)[:50]
        
        # Validate credentials from environment
        admin_user = os.getenv('ADMIN_USER')
        admin_pass = os.getenv('ADMIN_PASSWORD')
        
        if not admin_user or not admin_pass:
            logger.error("ADMIN_USER or ADMIN_PASSWORD not configured in environment")
            return render_template('login.html', error='Cấu hình hệ thống không đúng!')
        
        if username == admin_user and password == admin_pass:
            session['logged_in'] = True
            session['username'] = safe_username
            logger.info(f"User {safe_username} logged in successfully")
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"Failed login attempt for user {safe_username}")
            return render_template('login.html', error='Sai username hoặc password!')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html', username=session.get('username'))


@app.route('/api/status')
@login_required
def api_status():
    """API endpoint to get system status"""
    return jsonify({
        'status': 'running',
        'fb_email': os.getenv('FB_EMAIL', 'Not configured'),
        'debug_mode': os.getenv('DEBUG', 'False')
    })


@app.route('/api/logs')
@login_required
def api_logs():
    """API endpoint to get recent logs"""
    try:
        log_file = os.getenv('LOG_FILE', '/var/log/fbmanager/app.log')
        
        # Validate log file path to prevent path traversal
        log_path = Path(log_file).resolve()
        allowed_base = Path('/var/log/fbmanager').resolve()
        
        # For development/testing, also allow /tmp/fbmanager
        allowed_tmp = Path('/tmp/fbmanager').resolve()
        
        if not (str(log_path).startswith(str(allowed_base)) or str(log_path).startswith(str(allowed_tmp))):
            logger.error(f"Invalid log file path attempted: {log_file}")
            return jsonify({'error': 'Invalid log file path'}), 403
        
        if not log_path.exists():
            return jsonify({'logs': ['Log file not found']})
        
        with open(log_path, 'r') as f:
            logs = f.readlines()[-MAX_LOG_LINES:]  # Last N lines
        return jsonify({'logs': logs})
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Get config from environment
    host = os.getenv('WEB_HOST', '0.0.0.0')
    port = int(os.getenv('WEB_PORT', 8000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting FB Manager Web Interface on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
