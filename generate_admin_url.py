#!/usr/bin/env python3
"""
Generate a random secret URL for Django admin panel
Usage: python generate_admin_url.py
"""

import secrets

if __name__ == '__main__':
    # Generate a secure random string
    admin_url = secrets.token_urlsafe(16).replace('_', '-').replace('=', '') + '/'
    
    print("\n" + "="*60)
    print("🔐 Your secret admin URL:")
    print("="*60)
    print(admin_url)
    print("="*60)
    print("\n⚠️  Add this to your .env file:")
    print(f"ADMIN_URL={admin_url}")
    print("\n✅ Your admin panel will be accessible at:")
    print(f"https://yourdomain.com/{admin_url}")
    print("\n⚠️  Save this URL in a password manager!")
    print("⚠️  Never use /admin/ in production!")
    print("="*60 + "\n")
