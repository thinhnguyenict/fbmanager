"""
Forms Module
WTForms for configuration and authentication
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, URL, NumberRange, ValidationError


class LoginForm(FlaskForm):
    """Admin login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class ConfigForm(FlaskForm):
    """Configuration form for .env settings"""
    
    # Facebook Configuration
    fb_email = StringField('Facebook Email', 
                          validators=[DataRequired(), Email()],
                          render_kw={'placeholder': 'your_email@example.com'})
    fb_password = PasswordField('Facebook Password', 
                               validators=[DataRequired()],
                               render_kw={'placeholder': 'Your Facebook password'})
    facebook_app_id = StringField('Facebook App ID', 
                                  validators=[Optional()],
                                  render_kw={'placeholder': 'Optional'})
    facebook_app_secret = PasswordField('Facebook App Secret', 
                                       validators=[Optional()],
                                       render_kw={'placeholder': 'Optional'})
    facebook_redirect_uri = StringField('Facebook Redirect URI', 
                                       validators=[Optional(), URL()],
                                       render_kw={'placeholder': 'https://example.com/callback'})
    
    # Application Configuration
    debug = BooleanField('Debug Mode', default=False)
    log_level = SelectField('Log Level', 
                           choices=[
                               ('DEBUG', 'DEBUG'),
                               ('INFO', 'INFO'),
                               ('WARNING', 'WARNING'),
                               ('ERROR', 'ERROR'),
                               ('CRITICAL', 'CRITICAL')
                           ],
                           default='INFO')
    log_file = StringField('Log File Path', 
                          validators=[Optional()],
                          default='/var/log/fbmanager/app.log',
                          render_kw={'placeholder': '/var/log/fbmanager/app.log'})
    
    # Proxy Configuration
    proxy_host = StringField('Proxy Host', 
                            validators=[Optional()],
                            render_kw={'placeholder': 'proxy.example.com'})
    proxy_port = IntegerField('Proxy Port', 
                             validators=[Optional(), NumberRange(min=1, max=65535)],
                             render_kw={'placeholder': '8080'})
    proxy_user = StringField('Proxy Username', 
                            validators=[Optional()],
                            render_kw={'placeholder': 'Optional'})
    proxy_pass = PasswordField('Proxy Password', 
                              validators=[Optional()],
                              render_kw={'placeholder': 'Optional'})
    
    # Browser Settings
    headless_browser = BooleanField('Headless Browser', default=True)
    browser_timeout = IntegerField('Browser Timeout (seconds)', 
                                  validators=[Optional(), NumberRange(min=1, max=300)],
                                  default=30,
                                  render_kw={'placeholder': '30'})
