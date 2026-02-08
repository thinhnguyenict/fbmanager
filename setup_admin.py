#!/usr/bin/env python3
"""
Setup Admin Credentials
Utility script to create or update admin credentials
"""

import sys
import getpass
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config_manager.auth import AdminAuth


def main():
    """Main function to setup admin credentials"""
    print("=" * 60)
    print("FB Manager - Admin Credentials Setup")
    print("=" * 60)
    
    auth = AdminAuth()
    
    # Check if credentials already exist
    if auth.credentials_exist():
        print("\nWarning: Admin credentials already exist!")
        response = input("Do you want to update them? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Setup cancelled.")
            return
    
    # Get username
    print("\nEnter admin username (default: admin):")
    username = input("> ").strip()
    if not username:
        username = 'admin'
    
    # Get password
    print("\nEnter admin password (leave empty to generate random):")
    password = getpass.getpass("> ")
    
    if not password:
        # Generate random password
        password = auth.generate_random_password()
        print(f"\nGenerated random password: {password}")
        print("PLEASE SAVE THIS PASSWORD - IT WILL NOT BE SHOWN AGAIN!")
    else:
        # Confirm password
        print("\nConfirm password:")
        confirm = getpass.getpass("> ")
        if password != confirm:
            print("\nError: Passwords do not match!")
            return
    
    # Create credentials
    if auth.create_credentials(username, password):
        print("\n" + "=" * 60)
        print("SUCCESS: Admin credentials created!")
        print("=" * 60)
        print(f"Username: {username}")
        print(f"Credentials file: {auth.credentials_path}")
        print("=" * 60)
    else:
        print("\nError: Failed to create credentials!")
        sys.exit(1)


if __name__ == '__main__':
    main()
