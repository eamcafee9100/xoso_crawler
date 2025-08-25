import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import importlib
import inspect
import pkgutil
import logging
from typing import List, Dict, Any

# Import models
from lokhung.models import PhuongPhapTinhToan
from results.models import KetQuaXoSo

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Tự động nạp các phương pháp dự đoán từ package method vào database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Ghi đè các phương pháp đã tồn tại',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Chỉ hiển thị các phương pháp sẽ được nạp, không lưu vào database',
        )
        parser.add_argument(
            '--method-path',
            type=str,
            default='lokhung/methods',
            help='Đường dẫn đến thư mục chứa các phương pháp (mặc định: method)',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            default=1,
            help='ID của user sẽ là chủ sở hữu các phương pháp (mặc định: 1)',
        )
    
    def handle(self, *args, **options):
        self.force = options['force']
        self.test_mode = options['test']
        self.method_path = options['method_path']
        self.user_id = options['user_id']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🚀 Bắt đầu nạp phương pháp dự đoán từ thư mục "{self.method_path}"'
            )
        )
        
        try:
            # Thêm thư mục method vào Python path
            method_dir = os.path.join(os.getcwd(), self.method_path)
            print(f'📂 Đường dẫn thư mục phương pháp: {method_dir}')
            if not os.path.exists(method_dir):
                raise CommandError(f'❌ Không tìm thấy thư mục "{method_dir}"')
            
            if method_dir not in sys.path:
                sys.path.insert(0, method_dir)
            
            # Lấy danh sách các phương pháp
            methods = self.discover_methods_from_directory(method_dir)
            
            if not methods:
                self.stdout.write(
                    self.style.WARNING('⚠️  Không tìm thấy phương pháp nào trong thư mục')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(f'📋 Tìm thấy {len(methods)} phương pháp:')
            )
            
            # Hiển thị danh sách phương pháp
            for i, method in enumerate(methods, 1):
                self.stdout.write(f'   {i}. {method.get_name()} ({method.get_code()})')
            
            if self.test_mode:
                self.stdout.write(
                    self.style.WARNING('🧪 Chế độ test - không lưu vào database')
                )
                return
            
            # Lưu vào database
            saved_count, updated_count = self.save_methods(methods)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Hoàn thành! Đã lưu {saved_count} phương pháp mới, '
                    f'cập nhật {updated_count} phương pháp cũ'
                )
            )
            
            # Test một phương pháp nếu có dữ liệu
            self.test_methods(methods[:1])  # Test phương pháp đầu tiên
            
        except Exception as e:
            raise CommandError(f'❌ Lỗi không mong muốn: {e}')
    
    def discover_methods_from_directory(self, method_dir):
        """
        Tự động phát hiện các phương pháp dự đoán trong thư mục
        """
        methods = []
        
        try:
            # Import base module từ thư mục method
            base_module_path = os.path.join(method_dir, 'base.py')
            if not os.path.exists(base_module_path):
                raise ImportError('Không tìm thấy file base.py trong thư mục method')
            
            # Import base module
            spec = importlib.util.spec_from_file_location("lokhung.method.base", base_module_path)
            base_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(base_module)
            
            BasePredictionMethod = getattr(base_module, 'BasePredictionMethod')
            
        except Exception as e:
            raise CommandError(f'❌ Không thể import BasePredictionMethod từ {method_dir}/base.py: {e}')
        
        # Duyệt qua tất cả file Python trong thư mục
        for filename in os.listdir(method_dir):
            if filename.startswith("btl_") and filename.endswith("_method.py"):
                try:
                    module_path = os.path.join(method_dir, filename)
                    module_name = filename[:-3]  # Bỏ .py
                    # Import module
                    spec = importlib.util.spec_from_file_location(f"lokhung.methods.{module_name}", module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Tìm tất cả class kế thừa BasePredictionMethod
                    for name, cls in inspect.getmembers(module, inspect.isclass):
                        if (hasattr(cls, '__bases__') and 
                            any(base.__name__ == 'BasePredictionMethod' for base in cls.__bases__) and 
                            cls.__name__ != 'BasePredictionMethod'):
                            
                            try:
                                # Khởi tạo instance
                                instance = cls()
                                methods.append(instance)
                                
                                self.stdout.write(
                                    f'   ✓ Tìm thấy: {instance.get_name()}'
                                )
                                
                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(
                                        f'   ✗ Lỗi khởi tạo {name}: {e}'
                                    )
                                )
                                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'   ✗ Lỗi import file {filename}: {e}'
                        )
                    )
        
        return methods
    
    def save_methods(self, methods):
        """
        Lưu các phương pháp vào database
        """
        saved_count = 0
        updated_count = 0
        
        # Lấy user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            raise CommandError(f'❌ Không tìm thấy user với ID {self.user_id}')
        
        with transaction.atomic():
            for method in methods:
                try:
                    # Chuẩn bị dữ liệu
                    method_data = self.prepare_method_data(method, user)
                    
                    # Kiểm tra xem đã tồn tại chưa dựa trên tên
                    existing = PhuongPhapTinhToan.objects.filter(
                        ten_phuong_phap=method_data['ten_phuong_phap']
                    ).first()
                    
                    if existing:
                        if self.force:
                            # Cập nhật
                            for key, value in method_data.items():
                                if key != 'nguoi_tao':  # Không thay đổi người tạo
                                    setattr(existing, key, value)
                            existing.save()
                            updated_count += 1
                            
                            self.stdout.write(
                                f'   🔄 Cập nhật: {method.get_name()}'
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'   ⚠️  Bỏ qua (đã tồn tại): {method.get_name()}'
                                )
                            )
                    else:
                        # Tạo mới
                        PhuongPhapTinhToan.objects.create(**method_data)
                        saved_count += 1
                        
                        self.stdout.write(
                            f'   ✅ Tạo mới: {method.get_name()}'
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'   ❌ Lỗi lưu {method.get_name()}: {e}'
                        )
                    )
        
        return saved_count, updated_count
    
    def prepare_method_data(self, method, user):
        """
        Chuẩn bị dữ liệu để lưu vào model PhuongPhapTinhToan
        """
        # Tạo tham số cấu hình từ method
        tham_so_config = {
            'method_code': method.get_code(),
            'method_class': method.__class__.__name__,
            'module_file': method.__class__.__module__,
            'auto_generated': True,
            'calculation_type': 'bach_thu_lo',
            'import_source': 'method_package',
        }
        
        # Tạo công thức mô tả
        cong_thuc = f"""
# Phương pháp: {method.get_name()}
# Mã: {method.get_code()}
# Mô tả: {method.get_description()}

# Đây là phương pháp được tự động import từ package method
# Class: {method.__class__.__name__}
# Module: {method.__class__.__module__}

def calculate(data):
    '''
    Phương pháp này sử dụng thuật toán đã được định nghĩa sẵn
    trong class {method.__class__.__name__}
    
    Args:
        data: Dictionary chứa dữ liệu kết quả xổ số
        
    Returns:
        Dictionary chứa số dự đoán
    '''
    # Implementation được xử lý tự động bởi MethodExecutor
    pass
        """.strip()
        
        return {
            'ten_phuong_phap': method.get_name(),
            'loai_phuong_phap': 'bach_thu',  # Vì là bạch thủ lô
            'mo_ta': method.get_description(),
            'tham_so_config': tham_so_config,
            'cong_thuc': cong_thuc,
            'trong_so': 1.0,
            'do_tin_cay': 0.7,  # 70% tin cậy mặc định
            'trang_thai': 'testing',  # Đặt ở chế độ thử nghiệm
            'nguoi_tao': user,
        }
    
    def test_methods(self, methods):
        """
        Test một vài phương pháp với dữ liệu mẫu
        """
        if not methods:
            return
        
        self.stdout.write(
            self.style.SUCCESS('\n🧪 Đang test phương pháp với dữ liệu mẫu...')
        )
        
        # Lấy kết quả xổ số gần nhất
        try:
            latest_result = KetQuaXoSo.objects.latest('ngay')
            data = self.prepare_test_data(latest_result)
            
            for method in methods:
                try:
                    self.stdout.write(f'\n📊 Test phương pháp: {method.get_name()}')
                    
                    # Chạy phương pháp
                    result = method.calculate(data)
                    
                    self.stdout.write(f'   Input date: {latest_result.ngay}')
                    self.stdout.write(f'   Kết quả: {result}')
                    
                    # Hiển thị một số dữ liệu input để debug
                    sample_data = {k: v for k, v in list(data.items())[:5]}
                    self.stdout.write(f'   Sample input: {sample_data}')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'   ❌ Lỗi test {method.get_name()}: {e}'
                        )
                    )
                    
        except KetQuaXoSo.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Không có dữ liệu kết quả xổ số để test'
                )
            )
    
    def prepare_test_data(self, result):
        """
        Chuẩn bị dữ liệu test từ kết quả xổ số
        """
        return {
            'giai_db': result.giai_db or '',
            'giai_1': result.giai_1 or '',
            'giai_2_1': result.giai_2_1 or '',
            'giai_2_2': result.giai_2_2 or '',
            'giai_3_1': result.giai_3_1 or '',
            'giai_3_2': result.giai_3_2 or '',
            'giai_3_3': result.giai_3_3 or '',
            'giai_3_4': result.giai_3_4 or '',
            'giai_3_5': result.giai_3_5 or '',
            'giai_3_6': result.giai_3_6 or '',
            'giai_4_1': result.giai_4_1 or '',
            'giai_4_2': result.giai_4_2 or '',
            'giai_4_3': result.giai_4_3 or '',
            'giai_4_4': result.giai_4_4 or '',
            'giai_5_1': result.giai_5_1 or '',
            'giai_5_2': result.giai_5_2 or '',
            'giai_5_3': result.giai_5_3 or '',
            'giai_5_4': result.giai_5_4 or '',
            'giai_5_5': result.giai_5_5 or '',
            'giai_5_6': result.giai_5_6 or '',
            'giai_6_1': result.giai_6_1 or '',
            'giai_6_2': result.giai_6_2 or '',
            'giai_6_3': result.giai_6_3 or '',
            'giai_7_1': result.giai_7_1 or '',
            'giai_7_2': result.giai_7_2 or '',
            'giai_7_3': result.giai_7_3 or '',
            'giai_7_4': result.giai_7_4 or '',
        }