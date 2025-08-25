import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

# Import and run migrations
from django.core.management import execute_from_command_line

print("Running makemigrations...")
try:
    execute_from_command_line(['manage.py', 'makemigrations', 'results'])
    print("Migrations created successfully!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
