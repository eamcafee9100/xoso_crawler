"""
Utility functions để thực thi các phương pháp dự đoán đã được import
"""
import os
import sys
import importlib.util
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from lokhung.models import PhuongPhapTinhToan, DuDoan
from results.models import KetQuaXoSo

logger = logging.getLogger(__name__)

class MethodExecutor:
    """
    Class để thực thi các phương pháp dự đoán được import từ package method
    """
    
    def __init__(self):
        self.loaded_methods = {}
        self.method_path = 'lokhung/methods'  # Thư mục chứa các phương pháp
    
    def get_method_instance(self, phuong_phap: PhuongPhapTinhToan):
        """
        Lấy instance của phương pháp từ cấu hình
        """
        try:
            tham_so = phuong_phap.tham_so_config
            
            if not isinstance(tham_so, dict) or not tham_so.get('auto_generated'):
                return None
            
            method_class = tham_so.get('method_class')
            method_code = tham_so.get('method_code')
            
            if not method_class or not method_code:
                return None
            
            # Cache để tránh import lại
            cache_key = f"{method_code}_{method_class}"
            if cache_key in self.loaded_methods:
                return self.loaded_methods[cache_key]
            
            # Tìm file chứa method này
            method_file = self._find_method_file(method_code)
            if not method_file:
                logger.error(f"Không tìm thấy file cho method {method_code}")
                return None
            
            # Import method class
            instance = self._import_method_class(method_file, method_class)
            if instance:
                # Cache lại
                self.loaded_methods[cache_key] = instance
                return instance
            
            return None
            
        except Exception as e:
            logger.error(f"Lỗi khi load method instance cho {phuong_phap.ten_phuong_phap}: {e}")
            return None
    
    def _find_method_file(self, method_code):
        """
        Tìm file Python chứa method với code cụ thể
        """
        method_dir = os.path.join(os.getcwd(), self.method_path)
        print(f"📂 Đang tìm method trong thư mục: {method_dir}")
        if not os.path.exists(method_dir):
            return None
        
        # Duyệt qua tất cả file có pattern btl_*_method.py
        for filename in os.listdir(method_dir):
            if filename.startswith("btl_") and filename.endswith("_method.py"):
                file_path = os.path.join(method_dir, filename)
                
                # Đọc file để tìm method_code
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if f'get_code(self): return "{method_code}"' in content:
                            return file_path
                except Exception:
                    continue
        
        return None
    
    def _import_method_class(self, file_path, class_name):
        """
        Import class từ file Python
        """
        try:
            # Import base module trước
            base_path = os.path.join(os.path.dirname(file_path), 'base.py')
            if os.path.exists(base_path):
                spec = importlib.util.spec_from_file_location("method.base", base_path)
                base_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(base_module)
                
                # Thêm vào globals để class có thể kế thừa
                sys.modules['method.base'] = base_module
            
            # Import method module
            module_name = f"method.{os.path.basename(file_path)[:-3]}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Lấy class và khởi tạo
            cls = getattr(module, class_name, None)
            if cls:
                return cls()
            
            return None
            
        except Exception as e:
            logger.error(f"Lỗi import method class {class_name} từ {file_path}: {e}")
            return None
    
    def execute_method(self, phuong_phap: PhuongPhapTinhToan, analysis_date) -> Optional[Dict]:
        """
        Thực thi phương pháp dự đoán cho ngày cụ thể
        """
        try:
            # Lấy instance phương pháp
            method_instance = self.get_method_instance(phuong_phap)
            if not method_instance:
                logger.warning(f"Không thể load method instance cho {phuong_phap.ten_phuong_phap}")
                return None
            
            # Lấy dữ liệu kết quả xổ số
            result = KetQuaXoSo.objects.get(ngay=analysis_date)
            data = self.prepare_input_data(result)
            
            # Thực thi phương pháp
            prediction_result = method_instance.calculate(data)
            
            logger.info(f"Đã thực thi {phuong_phap.ten_phuong_phap} cho ngày {analysis_date}")
            
            return {
                'success': True,
                'data': prediction_result,
                'method_code': method_instance.get_code(),
                'analysis_date': analysis_date,
            }
            
        except KetQuaXoSo.DoesNotExist:
            logger.error(f"Không tìm thấy kết quả xổ số cho ngày {analysis_date}")
            return None
        except Exception as e:
            logger.error(f"Lỗi khi thực thi {phuong_phap.ten_phuong_phap}: {e}")
            return None
    
    def prepare_input_data(self, result: KetQuaXoSo) -> Dict[str, str]:
        """
        Chuẩn bị dữ liệu input từ kết quả xổ số
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
    
    def create_predictions_from_method(self, phuong_phap: PhuongPhapTinhToan, 
                                     analysis_date, prediction_date, user):
        """
        Tạo dự đoán từ kết quả thực thi phương pháp
        """
        try:
            # Thực thi phương pháp
            execution_result = self.execute_method(phuong_phap, analysis_date)
            
            if not execution_result or not execution_result['success']:
                return []
            
            created_predictions = []
            prediction_data = execution_result['data']
            
            # Xử lý từng loại dự đoán
            for prediction_type, numbers in prediction_data.items():
                if not numbers:
                    continue
                
                # Xác định loại số
                if 'two_digits' in prediction_type.lower():
                    loai_so = '2d'
                elif 'three_digits' in prediction_type.lower():
                    loai_so = '3d'
                else:
                    loai_so = 'bach_thu'  # Mặc định cho bạch thủ lô
                
                for number in numbers:
                    # Tính điểm tin cậy dựa trên phương pháp
                    diem_tin_cay = self.calculate_confidence_score(
                        phuong_phap, number, prediction_type
                    )
                    
                    # Tạo dự đoán
                    du_doan = DuDoan.objects.create(
                        phuong_phap=phuong_phap,
                        ngay_phan_tich=analysis_date,
                        ngay_du_doan=prediction_date,
                        so_du_doan=number,
                        loai_so=loai_so,
                        diem_tin_cay=diem_tin_cay,
                        xac_suat=diem_tin_cay / 100.0,
                        ghi_chu=f"Tự động tạo từ phương pháp {phuong_phap.ten_phuong_phap}",
                        chi_tiet_phan_tich={
                            'method_code': execution_result['method_code'],
                            'prediction_type': prediction_type,
                            'auto_generated': True,
                            'analysis_date': str(analysis_date),
                        },
                        nguoi_tao=user,
                    )
                    
                    created_predictions.append(du_doan)
            
            logger.info(f"Đã tạo {len(created_predictions)} dự đoán từ {phuong_phap.ten_phuong_phap}")
            return created_predictions
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo dự đoán từ {phuong_phap.ten_phuong_phap}: {e}")
            return []
    
    def calculate_confidence_score(self, phuong_phap, number, prediction_type):
        """
        Tính điểm tin cậy cho số dự đoán
        """
        base_confidence = phuong_phap.do_tin_cay * 100
        
        # Điều chỉnh dựa trên loại dự đoán
        if 'two_digits' in prediction_type.lower():
            # Số 2D thường có độ tin cậy cao hơn
            return min(95, base_confidence + 10)
        elif 'three_digits' in prediction_type.lower():
            # Số 3D có độ tin cậy thấp hơn
            return max(30, base_confidence - 10)
        
        return base_confidence

# Global instance
method_executor = MethodExecutor()