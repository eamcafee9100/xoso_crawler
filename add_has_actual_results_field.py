#!/usr/bin/env python
"""
Script thêm field has_actual_results vào PredictionPerformanceMetrics
"""

import os
import sys
import django
from django.conf import settings

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

def add_field():
    """Thêm field has_actual_results"""
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            # Kiểm tra xem field đã tồn tại chưa (dành cho PostgreSQL)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'results_predictionperformancemetrics' 
                AND column_name = 'has_actual_results'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Thêm field mới
                cursor.execute("""
                    ALTER TABLE results_predictionperformancemetrics 
                    ADD COLUMN has_actual_results BOOLEAN DEFAULT FALSE
                """)
                print("✓ Đã thêm field has_actual_results")
                
                # Update các records cũ
                cursor.execute("""
                    UPDATE results_predictionperformancemetrics 
                    SET has_actual_results = (actual_numbers IS NOT NULL AND actual_numbers != '')
                """)
                print("✓ Đã update các records cũ")
            else:
                print("✓ Field has_actual_results đã tồn tại")
                
    except Exception as e:
        print(f"✗ Lỗi khi thêm field: {e}")

if __name__ == "__main__":
    add_field()