#!/usr/bin/env python3
"""
FB Manager - Web Admin Interface
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (replace with proper auth)
        admin_user = os.getenv('ADMIN_USER', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if username == admin_user and password == admin_pass:
            session['logged_in'] = True
            session['username'] = username
            logger.info(f"User {username} logged in successfully")
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"Failed login attempt for user {username}")
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
        with open(log_file, 'r') as f:
            logs = f.readlines()[-100:]  # Last 100 lines
        return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Get config from environment
    host = os.getenv('WEB_HOST', '0.0.0.0')
    port = int(os.getenv('WEB_PORT', 8000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting FB Manager Web Interface on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
