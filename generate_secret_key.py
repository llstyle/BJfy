#!/usr/bin/env python3
"""
Generate a new Django SECRET_KEY
Usage: python generate_secret_key.py
"""

from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("\n" + "="*60)
    print("🔐 Your new SECRET_KEY:")
    print("="*60)
    print(secret_key)
    print("="*60)
    print("\n⚠️  Add this to your .env file:")
    print(f"SECRET_KEY={secret_key}")
    print("\n⚠️  Never commit this key to Git!")
    print("="*60 + "\n")
