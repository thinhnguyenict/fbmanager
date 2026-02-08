"""
Routes Module
Flask routes for configuration management
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from pathlib import Path

from .auth import AdminAuth
from .env_handler import EnvHandler
from .forms import LoginForm, ConfigForm

logger = logging.getLogger(__name__)

# Create blueprint
config_bp = Blueprint('config', __name__, 
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/admin')

# Initialize handlers
env_handler = EnvHandler()
admin_auth = AdminAuth()


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('config.login'))
        
        # Check session timeout (30 minutes)
        last_activity = session.get('last_activity')
        if last_activity:
            last_time = datetime.fromisoformat(last_activity)
            if datetime.now() - last_time > timedelta(minutes=30):
                session.clear()
                flash('Session expired. Please log in again.', 'warning')
                return redirect(url_for('config.login'))
        
        # Update last activity
        session['last_activity'] = datetime.now().isoformat()
        return f(*args, **kwargs)
    return decorated_function


def log_config_change(action: str, ip_address: str, details: str = ''):
    """Log configuration changes"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[CONFIG CHANGE] {timestamp} - IP: {ip_address} - Action: {action}"
    if details:
        log_msg += f" - Details: {details}"
    logger.warning(log_msg)


@config_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    # If already logged in, redirect to setup
    if session.get('logged_in'):
        return redirect(url_for('config.setup'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Verify credentials
        if admin_auth.verify_credentials(username, password):
            session['logged_in'] = True
            session['username'] = username
            session['last_activity'] = datetime.now().isoformat()
            
            # Log the login
            ip_address = request.remote_addr
            log_config_change('LOGIN', ip_address, f'User: {username}')
            
            flash('Login successful!', 'success')
            return redirect(url_for('config.setup'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)


@config_bp.route('/logout')
def logout():
    """Admin logout"""
    username = session.get('username', 'unknown')
    ip_address = request.remote_addr
    
    session.clear()
    
    log_config_change('LOGOUT', ip_address, f'User: {username}')
    flash('You have been logged out.', 'info')
    return redirect(url_for('config.login'))


@config_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    """Configuration setup page"""
    form = ConfigForm()
    
    if request.method == 'GET':
        # Load current values from .env
        env_vars = env_handler.read_env()
        
        # Populate form with current values
        form.fb_email.data = env_vars.get('FB_EMAIL', '')
        # Don't populate passwords, but show placeholder if exists
        if env_vars.get('FB_PASSWORD'):
            form.fb_password.render_kw = {'placeholder': '••••••••'}
        
        form.facebook_app_id.data = env_vars.get('FACEBOOK_APP_ID', '')
        if env_vars.get('FACEBOOK_APP_SECRET'):
            form.facebook_app_secret.render_kw = {'placeholder': '••••••••'}
        
        form.facebook_redirect_uri.data = env_vars.get('FACEBOOK_REDIRECT_URI', '')
        
        # Application settings
        form.debug.data = env_vars.get('DEBUG', 'False').lower() == 'true'
        form.log_level.data = env_vars.get('LOG_LEVEL', 'INFO')
        form.log_file.data = env_vars.get('LOG_FILE', '/var/log/fbmanager/app.log')
        
        # Proxy settings
        form.proxy_host.data = env_vars.get('PROXY_HOST', '')
        proxy_port = env_vars.get('PROXY_PORT', '')
        if proxy_port:
            try:
                form.proxy_port.data = int(proxy_port)
            except ValueError:
                pass
        form.proxy_user.data = env_vars.get('PROXY_USER', '')
        if env_vars.get('PROXY_PASS'):
            form.proxy_pass.render_kw = {'placeholder': '••••••••'}
        
        # Browser settings
        form.headless_browser.data = env_vars.get('HEADLESS_BROWSER', 'True').lower() == 'true'
        browser_timeout = env_vars.get('BROWSER_TIMEOUT', '30')
        if browser_timeout:
            try:
                form.browser_timeout.data = int(browser_timeout)
            except ValueError:
                form.browser_timeout.data = 30
    
    if form.validate_on_submit():
        # Prepare environment variables
        env_vars = {}
        
        # Facebook configuration
        env_vars['FB_EMAIL'] = form.fb_email.data
        # Only update password if a new one is provided
        if form.fb_password.data:
            env_vars['FB_PASSWORD'] = form.fb_password.data
        else:
            # Keep existing password
            current_vars = env_handler.read_env()
            env_vars['FB_PASSWORD'] = current_vars.get('FB_PASSWORD', '')
        
        env_vars['FACEBOOK_APP_ID'] = form.facebook_app_id.data or ''
        # Only update app secret if a new one is provided
        if form.facebook_app_secret.data:
            env_vars['FACEBOOK_APP_SECRET'] = form.facebook_app_secret.data
        else:
            current_vars = env_handler.read_env()
            env_vars['FACEBOOK_APP_SECRET'] = current_vars.get('FACEBOOK_APP_SECRET', '')
        
        env_vars['FACEBOOK_REDIRECT_URI'] = form.facebook_redirect_uri.data or ''
        
        # Application configuration
        env_vars['DEBUG'] = 'True' if form.debug.data else 'False'
        env_vars['LOG_LEVEL'] = form.log_level.data
        env_vars['LOG_FILE'] = form.log_file.data
        
        # Proxy configuration
        env_vars['PROXY_HOST'] = form.proxy_host.data or ''
        env_vars['PROXY_PORT'] = str(form.proxy_port.data) if form.proxy_port.data else ''
        env_vars['PROXY_USER'] = form.proxy_user.data or ''
        # Only update proxy password if a new one is provided
        if form.proxy_pass.data:
            env_vars['PROXY_PASS'] = form.proxy_pass.data
        else:
            current_vars = env_handler.read_env()
            env_vars['PROXY_PASS'] = current_vars.get('PROXY_PASS', '')
        
        # Browser settings
        env_vars['HEADLESS_BROWSER'] = 'True' if form.headless_browser.data else 'False'
        env_vars['BROWSER_TIMEOUT'] = str(form.browser_timeout.data) if form.browser_timeout.data else '30'
        
        # Validate
        validation_errors = env_handler.validate_env(env_vars)
        if validation_errors:
            for field, errors in validation_errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
            return render_template('config.html', form=form)
        
        # Save configuration
        try:
            env_handler.write_env(env_vars, create_backup=True)
            
            # Log the change
            ip_address = request.remote_addr
            username = session.get('username', 'unknown')
            log_config_change('CONFIG_UPDATE', ip_address, f'User: {username}')
            
            flash('Configuration saved successfully! A backup has been created.', 'success')
            return redirect(url_for('config.setup'))
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            flash(f'Error saving configuration: {str(e)}', 'danger')
    
    return render_template('config.html', form=form)


@config_bp.route('/backups')
@login_required
def backups():
    """List available backups"""
    try:
        backup_list = env_handler.list_backups()
        return jsonify({
            'success': True,
            'backups': backup_list
        })
    except Exception as e:
        logger.error(f"Error listing backups: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/restore', methods=['POST'])
@login_required
def restore():
    """Restore from backup"""
    backup_name = request.json.get('backup_name')
    
    if not backup_name:
        return jsonify({
            'success': False,
            'error': 'Backup name is required'
        }), 400
    
    try:
        if env_handler.restore_backup(backup_name):
            # Log the restore
            ip_address = request.remote_addr
            username = session.get('username', 'unknown')
            log_config_change('RESTORE_BACKUP', ip_address, 
                            f'User: {username}, Backup: {backup_name}')
            
            return jsonify({
                'success': True,
                'message': f'Successfully restored from {backup_name}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to restore backup'
            }), 500
            
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@config_bp.route('/restart-service', methods=['POST'])
@login_required
def restart_service():
    """Restart the fbmanager service"""
    try:
        # Log the restart request
        ip_address = request.remote_addr
        username = session.get('username', 'unknown')
        log_config_change('RESTART_SERVICE', ip_address, f'User: {username}')
        
        # Try to restart using systemctl
        import subprocess
        result = subprocess.run(
            ['systemctl', 'restart', 'fbmanager'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Service restart initiated successfully'
            })
        else:
            logger.error(f"Service restart failed: {result.stderr}")
            return jsonify({
                'success': False,
                'error': 'Failed to restart service. Check logs for details.'
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Service restart timed out'
        }), 500
    except Exception as e:
        logger.error(f"Error restarting service: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
