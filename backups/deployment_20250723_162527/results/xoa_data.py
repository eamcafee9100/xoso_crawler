import os
import sys
import django
from django.db import connection

# Thêm thư mục gốc vào sys.path
sys.path.append('C:\\Users\\n2t\\Documents\\xoso_crawler')

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

def truncate_tables():
    with connection.cursor() as cursor:
        # Tắt ràng buộc khóa ngoại tạm thời (nếu dùng PostgreSQL)
        cursor.execute('SET CONSTRAINTS ALL DEFERRED;')
        
        # Xóa dữ liệu từ các bảng
        cursor.execute('TRUNCATE TABLE results_predictionresultbtl CASCADE;')
        cursor.execute('TRUNCATE TABLE results_danbtl CASCADE;')
        cursor.execute('TRUNCATE TABLE results_predictionmethodbtl CASCADE;')

        # Đặt lại trình tự ID (nếu cần, với PostgreSQL)
        cursor.execute("ALTER SEQUENCE results_predictionresultbtl_id_seq RESTART WITH 1;")
        cursor.execute("ALTER SEQUENCE results_danbtl_id_seq RESTART WITH 1;")
        cursor.execute("ALTER SEQUENCE results_predictionmethodbtl_id_seq RESTART WITH 1;")

        # Bật lại ràng buộc khóa ngoại
        cursor.execute('SET CONSTRAINTS ALL IMMEDIATE;')

if __name__ == '__main__':
    truncate_tables()
    print("Đã xóa dữ liệu thành công!")