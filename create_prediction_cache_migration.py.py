#!/usr/bin/env python
"""
Script tạo migration cho PredictionCache model
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

def create_migration():
    """Tạo migration cho PredictionCache model"""
    try:
        # Tạo migration
        execute_from_command_line(['manage.py', 'makemigrations', 'results'])
        print("✓ Đã tạo migration cho PredictionCache model")
        
        # Chạy migration
        execute_from_command_line(['manage.py', 'migrate', 'results'])
        print("✓ Đã chạy migration thành công")
        
    except Exception as e:
        print(f"✗ Lỗi khi tạo/chạy migration: {e}")

if __name__ == "__main__":
    create_migration()