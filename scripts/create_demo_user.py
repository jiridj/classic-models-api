#!/usr/bin/env python
"""
Script to create a demo user for testing the API
Run this after the Django application is set up
"""
import os
import sys

import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.contrib.auth.models import User


def create_demo_user():
    """Create a demo user for testing"""
    username = "demo"
    email = "demo@classicmodels.com"
    password = "demo123"

    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists")
        return

    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name="Demo",
        last_name="User",
    )

    print("Demo user created successfully!")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")


if __name__ == "__main__":
    create_demo_user()
