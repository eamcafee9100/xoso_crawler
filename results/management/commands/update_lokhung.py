from django.core.management.base import BaseCommand
from django.utils import timezone
from results.models import LoKhung2Ngay
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Tự động cập nhật dữ liệu lô khung 2 ngày hàng ngày'

    def handle(self, *args, **options):
        try:
            count = LoKhung2Ngay.update_latest_lokhung_data()
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f'Đã cập nhật {count} bản ghi lô khung mới'))
            else:
                self.stdout.write('Không có dữ liệu mới để cập nhật')
        except Exception as e:
            logger.error(f"Lỗi khi chạy lệnh update_lokhung: {str(e)}", exc_info=True)
            self.stdout.write(self.style.ERROR('Đã xảy ra lỗi khi cập nhật dữ liệu'))