#!/usr/bin/env python
"""
Run migration manually
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection

def create_tables_manually():
    """Create tables manually using SQL"""
    
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS results_numberanalysiscache (
            id SERIAL PRIMARY KEY,
            number VARCHAR(2) NOT NULL,
            analysis_date DATE NOT NULL,
            appearances_30d INTEGER DEFAULT 0,
            appearances_total INTEGER DEFAULT 0,
            avg_cycle_days REAL DEFAULT 0,
            median_cycle_days REAL DEFAULT 0,
            current_gan_days INTEGER DEFAULT 0,
            max_gan_days INTEGER DEFAULT 0,
            max_gan_start_date DATE,
            max_gan_end_date DATE,
            probability_next_appearance REAL DEFAULT 0,
            probability_when_max_gan REAL DEFAULT 0,
            weekday_analysis JSONB DEFAULT '{}',
            companion_numbers JSONB DEFAULT '[]',
            max_consecutive_days INTEGER DEFAULT 0,
            consecutive_history JSONB DEFAULT '[]',
            consecutive_probabilities JSONB DEFAULT '{}',
            predecessor_analysis JSONB DEFAULT '[]',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(number, analysis_date)
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_numberanalysiscache_number_date 
        ON results_numberanalysiscache(number, analysis_date);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_numberanalysiscache_updated 
        ON results_numberanalysiscache(updated_at);
        """,
        """
        CREATE TABLE IF NOT EXISTS results_numberanalysisdetail (
            id SERIAL PRIMARY KEY,
            cache_id INTEGER REFERENCES results_numberanalysiscache(id) ON DELETE CASCADE,
            detail_type VARCHAR(20) NOT NULL,
            data JSONB NOT NULL,
            UNIQUE(cache_id, detail_type)
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_numberanalysisdetail_cache_type 
        ON results_numberanalysisdetail(cache_id, detail_type);
        """
    ]
    
    with connection.cursor() as cursor:
        for sql in sql_commands:
            try:
                print(f"Executing: {sql[:50]}...")
                cursor.execute(sql)
                print("✅ Success")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("Tables created successfully!")

if __name__ == "__main__":
    try:
        print("Creating tables manually...")
        create_tables_manually()
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
