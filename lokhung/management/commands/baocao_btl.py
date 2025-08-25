from django.core.management.base import BaseCommand
from django.db import transaction
from lokhung.models import PredictionMethodBtl, DanBtl, PredictionResultBtl

class Command(BaseCommand):
    help = 'Tối ưu hóa database và cập nhật thống kê'
    
    def add_arguments(self, parser):
        parser.add_argument('--rebuild-stats', action='store_true', 
                          help='Xây dựng lại tất cả thống kê')
        parser.add_argument('--days', type=int, default=365,
                          help='Số ngày để xử lý (mặc định: 365)')
    
    def handle(self, *args, **options):
        self.stdout.write("Bắt đầu tối ưu hóa database...")
        
        if options['rebuild_stats']:
            self.rebuild_all_statistics(options['days'])
        
        self.create_missing_indexes()
        self.cleanup_old_data()
        
        self.stdout.write(self.style.SUCCESS("Hoàn thành tối ưu hóa database!"))
    
    def rebuild_all_statistics(self, days):
        """Xây dựng lại tất cả thống kê"""
        from datetime import timedelta
        from django.utils import timezone
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Cập nhật thống kê cho methods
        methods = PredictionMethodBtl.objects.all()
        for method in methods:
            method.update_statistics()
            self.stdout.write(f"✓ Cập nhật thống kê cho {method.name}")
        
        # Cập nhật thống kê cho dan_btl
        dan_btls = DanBtl.objects.filter(analysis_date__gte=start_date)
        for dan_btl in dan_btls:
            dan_btl.update_statistics()
            
        self.stdout.write(f"✓ Cập nhật thống kê cho {dan_btls.count()} ngày")