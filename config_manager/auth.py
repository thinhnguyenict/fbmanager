"""
Authentication Module
Handles admin authentication and session management
"""

import os
import bcrypt
import secrets
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AdminAuth:
    """Handles admin authentication"""
    
    def __init__(self, credentials_path: str = '.admin_credentials'):
        """
        Initialize AdminAuth
        
        Args:
            credentials_path: Path to the admin credentials file
        """
        self.credentials_path = Path(credentials_path)
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """
        Verify admin credentials
        
        Args:
            username: Admin username
            password: Admin password (plain text)
            
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            stored_username, stored_hash = self._load_credentials()
            
            if not stored_username or not stored_hash:
                logger.error("No admin credentials found")
                return False
            
            # Check username
            if username != stored_username:
                logger.warning(f"Invalid username attempt: {username}")
                return False
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                logger.info(f"Successful login for user: {username}")
                return True
            else:
                logger.warning(f"Invalid password for user: {username}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying credentials: {e}")
            return False
    
    def _load_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Load admin credentials from file
        
        Returns:
            Tuple of (username, password_hash)
        """
        if not self.credentials_path.exists():
            logger.warning(f"Credentials file not found: {self.credentials_path}")
            return None, None
        
        try:
            username = None
            password_hash = None
            
            with open(self.credentials_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('ADMIN_USERNAME='):
                        username = line.split('=', 1)[1]
                    elif line.startswith('ADMIN_PASSWORD_HASH='):
                        password_hash = line.split('=', 1)[1]
            
            return username, password_hash
            
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return None, None
    
    def create_credentials(self, username: str, password: str) -> bool:
        """
        Create or update admin credentials
        
        Args:
            username: Admin username
            password: Admin password (plain text)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Hash the password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            # Write to file
            with open(self.credentials_path, 'w', encoding='utf-8') as f:
                f.write(f'ADMIN_USERNAME={username}\n')
                f.write(f'ADMIN_PASSWORD_HASH={password_hash.decode("utf-8")}\n')
            
            # Set secure permissions
            os.chmod(self.credentials_path, 0o600)
            
            logger.info(f"Created admin credentials for user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating credentials: {e}")
            return False
    
    def generate_random_password(self, length: int = 16) -> str:
        """
        Generate a secure random password
        
        Args:
            length: Length of the password
            
        Returns:
            Random password string
        """
        # Use a mix of characters for a strong password
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def credentials_exist(self) -> bool:
        """
        Check if admin credentials exist
        
        Returns:
            True if credentials file exists, False otherwise
        """
        return self.credentials_path.exists()
    
    def initialize_default_credentials(self) -> Optional[str]:
        """
        Initialize with default admin credentials if none exist
        
        Returns:
            Generated password if created, None if already exists
        """
        if self.credentials_exist():
            logger.info("Admin credentials already exist")
            return None
        
        # Generate random password
        password = self.generate_random_password()
        
        # Create credentials with default username
        if self.create_credentials('admin', password):
            logger.info("Created default admin credentials")
            return password
        else:
            logger.error("Failed to create default admin credentials")
            return None


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a secure secret key for Flask sessions
    
    Args:
        length: Length of the secret key in bytes
        
    Returns:
        Hex-encoded secret key
    """
    return secrets.token_hex(length)
