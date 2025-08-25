from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Xóa toàn bộ bảng database bao gồm django_migrations'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                self.stdout.write(self.style.SUCCESS(f'Đã xóa bảng {table}'))
            cursor.execute("SET FOREIGN_KEY_CHECKS=1;")