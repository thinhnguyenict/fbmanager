"""
Environment File Handler
Handles reading, writing, and backing up .env files
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class EnvHandler:
    """Handles .env file operations with backup support"""
    
    def __init__(self, env_path: str = '.env'):
        """
        Initialize EnvHandler
        
        Args:
            env_path: Path to the .env file
        """
        self.env_path = Path(env_path)
        self.backup_dir = self.env_path.parent / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
    
    def read_env(self) -> Dict[str, str]:
        """
        Read environment variables from .env file
        
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        
        if not self.env_path.exists():
            logger.warning(f".env file not found at {self.env_path}")
            return env_vars
        
        try:
            with open(self.env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE pairs
                    match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$', line)
                    if match:
                        key, value = match.groups()
                        # Remove quotes if present
                        value = value.strip('"').strip("'")
                        env_vars[key] = value
            
            logger.info(f"Read {len(env_vars)} variables from .env file")
            return env_vars
            
        except Exception as e:
            logger.error(f"Error reading .env file: {e}")
            raise
    
    def write_env(self, env_vars: Dict[str, str], create_backup: bool = True) -> bool:
        """
        Write environment variables to .env file
        
        Args:
            env_vars: Dictionary of environment variables
            create_backup: Whether to create a backup before writing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup if file exists
            if create_backup and self.env_path.exists():
                self.create_backup()
            
            # Read the template or existing file to preserve structure
            template = self._read_template()
            
            # Write new .env file
            with open(self.env_path, 'w', encoding='utf-8') as f:
                for line in template:
                    # Check if this is a variable line
                    match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=', line)
                    if match:
                        key = match.group(1)
                        if key in env_vars:
                            # Replace with new value
                            value = env_vars[key]
                            # Quote value if it contains spaces
                            if ' ' in value:
                                f.write(f'{key}="{value}"\n')
                            else:
                                f.write(f'{key}={value}\n')
                        else:
                            # Keep original line
                            f.write(line + '\n')
                    else:
                        # Keep comments and empty lines
                        f.write(line + '\n')
                
                # Add any new variables that weren't in template
                template_keys = set()
                for line in template:
                    match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=', line)
                    if match:
                        template_keys.add(match.group(1))
                
                new_vars = set(env_vars.keys()) - template_keys
                if new_vars:
                    f.write('\n# Additional variables\n')
                    for key in sorted(new_vars):
                        value = env_vars[key]
                        if ' ' in value:
                            f.write(f'{key}="{value}"\n')
                        else:
                            f.write(f'{key}={value}\n')
            
            # Set secure permissions (owner read/write only)
            os.chmod(self.env_path, 0o600)
            
            logger.info(f"Successfully wrote {len(env_vars)} variables to .env file")
            return True
            
        except Exception as e:
            logger.error(f"Error writing .env file: {e}")
            # Try to restore from backup if write failed
            if create_backup:
                self._restore_latest_backup()
            raise
    
    def _read_template(self) -> List[str]:
        """Read template structure from existing .env or .env.example"""
        template = []
        
        # Try to read from existing .env first
        if self.env_path.exists():
            try:
                with open(self.env_path, 'r', encoding='utf-8') as f:
                    template = [line.rstrip() for line in f]
            except Exception:
                pass
        
        # If no .env, try .env.example
        if not template:
            example_path = self.env_path.parent / '.env.example'
            if example_path.exists():
                try:
                    with open(example_path, 'r', encoding='utf-8') as f:
                        template = [line.rstrip() for line in f]
                except Exception:
                    pass
        
        # If still no template, create a basic one
        if not template:
            template = [
                '# FB Manager Configuration',
                '# Generated by Config Manager',
                ''
            ]
        
        return template
    
    def create_backup(self) -> Optional[Path]:
        """
        Create a backup of the current .env file
        
        Returns:
            Path to the backup file, or None if failed
        """
        if not self.env_path.exists():
            logger.warning("No .env file to backup")
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'.env.backup.{timestamp}'
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(self.env_path, backup_path)
            os.chmod(backup_path, 0o600)
            
            logger.info(f"Created backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def list_backups(self) -> List[Dict[str, any]]:
        """
        List all available backups
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        if not self.backup_dir.exists():
            return backups
        
        try:
            for backup_file in sorted(self.backup_dir.glob('.env.backup.*'), reverse=True):
                stat = backup_file.stat()
                backups.append({
                    'name': backup_file.name,
                    'path': str(backup_file),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'timestamp': backup_file.name.replace('.env.backup.', '')
                })
            
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def restore_backup(self, backup_name: str) -> bool:
        """
        Restore from a specific backup
        
        Args:
            backup_name: Name of the backup file
            
        Returns:
            True if successful, False otherwise
        """
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_name}")
            return False
        
        try:
            # Create a backup of current file before restoring
            if self.env_path.exists():
                self.create_backup()
            
            # Restore from backup
            shutil.copy2(backup_path, self.env_path)
            os.chmod(self.env_path, 0o600)
            
            logger.info(f"Restored from backup: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def _restore_latest_backup(self) -> bool:
        """Restore from the most recent backup"""
        backups = self.list_backups()
        if not backups:
            logger.error("No backups available for restore")
            return False
        
        latest = backups[0]
        return self.restore_backup(latest['name'])
    
    def validate_env(self, env_vars: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Validate environment variables
        
        Args:
            env_vars: Dictionary of environment variables
            
        Returns:
            Dictionary of validation errors (empty if valid)
        """
        errors = {}
        
        # Required fields
        if not env_vars.get('FB_EMAIL'):
            errors.setdefault('FB_EMAIL', []).append('Email is required')
        elif '@' not in env_vars.get('FB_EMAIL', ''):
            errors.setdefault('FB_EMAIL', []).append('Invalid email format')
        
        if not env_vars.get('FB_PASSWORD'):
            errors.setdefault('FB_PASSWORD', []).append('Password is required')
        
        # Validate proxy port if provided
        proxy_port = env_vars.get('PROXY_PORT', '').strip()
        if proxy_port:
            try:
                port = int(proxy_port)
                if port < 1 or port > 65535:
                    errors.setdefault('PROXY_PORT', []).append('Port must be between 1 and 65535')
            except ValueError:
                errors.setdefault('PROXY_PORT', []).append('Port must be a number')
        
        # Validate URL format for redirect URI if provided
        redirect_uri = env_vars.get('FACEBOOK_REDIRECT_URI', '').strip()
        if redirect_uri:
            if not redirect_uri.startswith(('http://', 'https://')):
                errors.setdefault('FACEBOOK_REDIRECT_URI', []).append('Must be a valid URL starting with http:// or https://')
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        log_level = env_vars.get('LOG_LEVEL', 'INFO').upper()
        if log_level not in valid_log_levels:
            errors.setdefault('LOG_LEVEL', []).append(f'Must be one of: {", ".join(valid_log_levels)}')
        
        return errors
