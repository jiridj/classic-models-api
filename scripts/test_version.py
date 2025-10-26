#!/usr/bin/env python3
"""
Test script to verify version detection works locally.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from config.settings.base import get_version

if __name__ == "__main__":
    version = get_version()
    print(f"Current API version: {version}")
    
    # Test different scenarios
    print("\nTesting version detection:")
    
    # Test with environment variable
    os.environ['API_VERSION'] = 'v2.0.0'
    version_env = get_version()
    print(f"With API_VERSION=v2.0.0: {version_env}")
    
    # Clear environment variable
    if 'API_VERSION' in os.environ:
        del os.environ['API_VERSION']
    
    # Test git detection
    version_git = get_version()
    print(f"From git: {version_git}")
    
    print(f"\nFinal version that will be used in API docs: {version_git}")
