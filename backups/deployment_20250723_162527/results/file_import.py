import csv
from datetime import datetime
from .models import KetQuaXoSo

def import_from_csv(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            KetQuaXoSo.objects.create(
                id=int(row['id']),
                ngay=datetime.strptime(row['ngay'], '%Y-%m-%d').date(),
                thu=row['thu'].strip(),
                giai_db=row['giai_db'],
                giai_1=row['giai_1'],
                giai_2=row['giai_2'],
                giai_3=row['giai_3'],
                giai_4=row['giai_4'],
                giai_5=row['giai_5'],
                giai_6=row['giai_6'],
                giai_7=row['giai_7']
            )

# Sử dụng
import_from_csv('results_ketquaxoso.csv')