#!/usr/bin/env python3
"""
FB Manager - Flask Web Application
Configuration management web interface
"""

import os
import sys
from pathlib import Path
from flask import Flask
from config_manager.routes import config_bp
from config_manager.auth import AdminAuth, generate_secret_key

# Add parent directory to path to import from main module
sys.path.insert(0, str(Path(__file__).parent))


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__, 
                template_folder='config_manager/templates',
                static_folder='config_manager/static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', generate_secret_key())
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
    
    # Register blueprints
    app.register_blueprint(config_bp)
    
    # Initialize admin credentials if not exists
    admin_auth = AdminAuth()
    if not admin_auth.credentials_exist():
        password = admin_auth.initialize_default_credentials()
        if password:
            print("=" * 60)
            print("ADMIN CREDENTIALS GENERATED")
            print("=" * 60)
            print(f"Username: admin")
            print(f"Password: {password}")
            print("=" * 60)
            print("PLEASE SAVE THIS PASSWORD - IT WILL NOT BE SHOWN AGAIN!")
            print("=" * 60)
    
    # Root redirect
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('config.login'))
    
    return app


def main():
    """Run Flask application"""
    app = create_app()
    
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("FB Manager - Configuration Interface")
    print("=" * 60)
    print(f"Starting web server on http://{host}:{port}")
    print(f"Access the admin panel at: http://{host}:{port}/admin/login")
    print("=" * 60)
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
