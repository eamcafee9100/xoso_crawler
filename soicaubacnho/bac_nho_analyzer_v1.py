# bac_nho_analyzer_v1.py
from datetime import datetime, timedelta, date
import json
from collections import defaultdict
import numpy as np
from django.utils import timezone
from django.db.models import Avg, Sum, Count, F, Q, Min, Max

from results.models import KetQuaXoSo
from .models import SoiCauBacNho, ThongKeHieuQua, QuyLuatBacNho, LichSuSoiCau
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from scipy.stats import pearsonr
import pandas as pd
import math
import random
import logging
logger = logging.getLogger(__name__)
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)
class BacNhoAnalyzer_v1:
    """Lớp phân tích và dự đoán theo phương pháp Bạc Nhớ phiên bản nâng cấp"""
    
    def __init__(self, target_date=None):
        """
        Khởi tạo BacNhoAnalyzer
        Args:
            target_date: Ngày cần dự đoán, mặc định là ngày mai
        """
        today = timezone.now().date()
        self.target_date = target_date or (today + timedelta(days=1))
        self.source_date = self.target_date - timedelta(days=1)
        self.db_cache = {}  # Cache kết quả DB để giảm truy vấn
        self.ml_models = {}  # Cache các mô hình ML
        
        # Danh sách quy tắc soi cầu theo ngày
        self.ngay_rules = [
            # Format: (điều kiện (list cặp số), kết quả (list cặp số))
            (['01', '10'], ['06', '60', '89', '98']),
            (['24', '42'], ['27', '72']),
            (['56', '65'], ['59', '95']),
            (['87', '78'], ['48', '84']),
            (['48', '84'], ['46', '64', '05', '50']),
            (['36', '63'], ['38', '83']),
            (['38', '83'], ['67', '76']),
            (['99'], ['99']),
            (['68'], ['86']),
            (['17'], ['85']),
            (['05', '50'], ['26', '62']),
            (['69', '96'], ['71', '17']),
            (['57', '75'], ['85', '58']),
            (['41', '14'], ['16', '61', '18', '81']),
            (['45', '54'], ['56', '65']),
            (['47', '74'], ['79', '97']),
            (['79', '97'], ['37', '73']),
            (['23', '32'], ['34', '43']),
            (['02', '20'], ['26', '62']),
            (['08', '80'], ['08', '80']),
            (['18', '81'], ['97', '99']),
            (['03', '30'], ['01', '10']),
            (['28', '82'], ['23', '32']),
            (['58', '85'], ['38', '83']),
        ]
        
        # Quy tắc soi cầu theo tổng giải đặc biệt
        self.tong_db_rules = {
            0: 1, 1: 7, 2: 9, 3: 0, 4: 3, 5: 4, 6: 8, 7: 2, 8: [0, 7], 9: 5
        }
        
        # Quy tắc soi cầu theo thứ trong tuần
        self.thu_rules = {
            # Format: {thứ: [số thường về]}
            (0, 1, 5, 6): ['32'],  # Thứ 2, thứ 3, thứ 7 và chủ nhật
            (3, 6): ['39'],        # Thứ 5 và CN
            (2, 3, 4): ['69'],     # Thứ 4, thứ 5 và thứ 6
            (5, 6): ['79', '99'],  # Thứ 7 và CN
            (3, 5): ['97'],        # Thứ 5 và thứ 7
        }
        
        # Quy tắc cặp số đi kèm
        self.cap_kem_rules = {
            # Format: {cặp số: [số đi kèm]}
            ('37', '73'): ['10', '01'],
            ('25', '52'): ['22'],
            '76': ['47'],
            '11': ['44'],
            '66': ['33'],
            ('77', '44'): ['55'],
            '77': ['44'],
            '49': ['23'],
        }
        
        # Quy tắc theo lô
        self.lo_rules = {
            # Format: {số hôm nay: số ngày mai}
            '66': '66',
            '45': '09',
            '58': '63',
            '68': '86', 
            '86': '68',
            '22': '00',
            '76': '47',
            '94': '34',
            '29': '24',
            '06': '09',
            '98': '01',
            '05': '95',
            '49': '23',
            '74': '92',
            '89': '92',
            '78': '72',
        }
        
        # Quy tắc khi giải đặc biệt về kép
        self.kep_rules = {
            '00': '99',
            '77': '22',
            '88': '22',
            '11': '88',
            '55': ['55', '11'],
            '44': '66',
            'no_kep': ['99', '00'],  # Nếu hôm nay không có kết quả kép
            '3_kep': '33',           # Nếu hôm nay có 3 kép
        }
        
        # Quy tắc đầu câm
        self.dau_cam_rules = {
            # Format: {đầu câm: [số thường về ngày mai]}
            '0': ['04', '06', '09'],
            '1': ['16', '17'],
            '2': ['21', '25', '29'],
            '3': ['30', '36', '39'],
            '4': ['40', '44', '45'],
            '5': ['54', '59'],
            '6': ['61', '63'],
            '7': ['70', '71', '73', '75'],
            '8': ['80', '82', '89'],
            '9': ['95', '92'],
        }
        
        # Quy tắc đuôi câm
        self.duoi_cam_rules = {
            # Format: {đuôi câm: [số thường về ngày mai]}
            '0': ['00', '20', '80'],
            '1': ['21', '41'],
            '2': ['22', '52', '82'],
            '3': ['30', '36', '39'],
            '4': ['64', '84'],
            '5': ['55', '85', '95'],
            '6': ['06', '16', '56'],
            '7': ['17', '47', '67'],
            '8': ['08', '18', '88'],
            '9': ['29', '39', '59', '99'],
        }
        
        # Thêm quy tắc đầu đuôi câm
        self.dau_duoi_cam_rules = {
            # 1 chữ số câm (X)
            'single': lambda x: [f"{x}0", f"0{x}"],
            # 2 chữ số câm (X, Y)
            'double': lambda x, y: [f"{x}0", f"{x}{x}", f"{y}0", f"{y}{y}", f"{x}{y}", f"{y}{x}"],
            # 3 chữ số câm (X, Y, Z)
            'triple': lambda x, y, z: [f"{x}{y}", f"{y}{x}", f"{y}{z}", f"{z}{y}"]
        }
        
        # Cấu hình mô hình học máy
        self.ml_config = {
            'random_forest': {
                'n_estimators': 200,
                'max_depth': 10,
                'min_samples_split': 5,
                'random_state': 42
            },
            'xgboost': {
                'n_estimators': 100,
                'max_depth': 5,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            },
            'lightgbm': {
                'n_estimators': 100,
                'max_depth': 5,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            }
        }

    def analyze_and_predict(self):
        """
        Phân tích dữ liệu và dự đoán kết quả cho ngày target_date
        Returns:
            Dict chứa kết quả dự đoán từ tất cả các phương pháp
        """
        print(f"===== BẮT ĐẦU PHÂN TÍCH VÀ DỰ ĐOÁN CHO NGÀY {self.target_date} =====")
        
        try:
            # Lấy kết quả xổ số gần nhất (ngày hôm qua)
            print(f"Lấy kết quả xổ số cho ngày nguồn {self.source_date}...")
            source_result = self._get_xoso_result(self.source_date)
            
            if not source_result:
                logger.error(f"❌ Không tìm thấy kết quả xổ số cho ngày {self.source_date}")
                return {'error': f'Không có dữ liệu cho ngày {self.source_date}'}
            
            print(f"✅ Đã lấy được kết quả xổ số cho ngày {self.source_date}")
            
            # Lấy tất cả số 2 chữ số từ kết quả gần nhất
            print(f"Trích xuất số 2 chữ số từ kết quả ngày {self.source_date}...")
            source_numbers = self._get_all_2digit_numbers(source_result)
            
            if not source_numbers:
                logger.error(f"❌ Không tìm thấy số 2 chữ số trong kết quả ngày {self.source_date}")
                return {'error': f'Không thể xác định số 2 chữ số từ kết quả ngày {self.source_date}'}
            
            print(f"✅ Đã trích xuất được {len(source_numbers)} số 2 chữ số: {', '.join(source_numbers)}")
            
            # Tính toán dự đoán theo tất cả các phương pháp
            results = {
                'target_date': self.target_date,
                'source_date': self.source_date,
                'source_numbers': source_numbers,
                'predictions': {}
            }
            
            # Log thông tin cơ bản
            print(f"Ngày dự đoán: {self.target_date}, Ngày nguồn: {self.source_date}")
            print(f"Số nguồn: {source_numbers}")
            
            # 1. Dự đoán theo ngày
            print("1. Bắt đầu dự đoán theo ngày...")
            try:
                theo_ngay_result = self.predict_theo_ngay(source_numbers)
                results['predictions']['theo_ngay'] = theo_ngay_result
                print(f"✅ Dự đoán theo ngày: {theo_ngay_result.get('predicted_numbers', [])} (Độ tin cậy: {theo_ngay_result.get('confidence', 0)}%)")
            except Exception as e:
                logger.error(f"❌ Lỗi khi dự đoán theo ngày: {e}")
                logger.error(traceback.format_exc())
            
            # 2. Dự đoán theo tổng giải đặc biệt
            print("2. Bắt đầu dự đoán theo tổng giải đặc biệt...")
            try:
                db_number = source_result.giai_db[-2:] if hasattr(source_result, 'giai_db') and source_result.giai_db else None
                if db_number:
                    print(f"Số giải đặc biệt: {db_number}")
                    theo_tong_db_result = self.predict_theo_tong_db(db_number)
                    results['predictions']['theo_tong_db'] = theo_tong_db_result
                    print(f"✅ Dự đoán theo tổng giải đặc biệt: {theo_tong_db_result.get('predicted_numbers', [])} (Độ tin cậy: {theo_tong_db_result.get('confidence', 0)}%)")
                else:
                    logger.warning("⚠️ Không có số giải đặc biệt để dự đoán")
            except Exception as e:
                logger.error(f"❌ Lỗi khi dự đoán theo tổng giải đặc biệt: {e}")
                logger.error(traceback.format_exc())
            
            # 3. Dự đoán theo thứ
            print("3. Bắt đầu dự đoán theo thứ...")
            try:
                weekday = self.target_date.weekday()
                weekday_names = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']
                print(f"Thứ trong tuần: {weekday_names[weekday]} ({weekday})")
                theo_thu_result = self.predict_theo_thu(weekday)
                results['predictions']['theo_thu'] = theo_thu_result
                print(f"✅ Dự đoán theo thứ: {theo_thu_result.get('predicted_numbers', [])} (Độ tin cậy: {theo_thu_result.get('confidence', 0)}%)")
            except Exception as e:
                logger.error(f"❌ Lỗi khi dự đoán theo thứ: {e}")
                logger.error(traceback.format_exc())
            
            # 4. Dự đoán theo cặp số đi kèm
            print("4. Bắt đầu dự đoán theo cặp số đi kèm...")
            try:
                theo_cap_kem_result = self.predict_theo_cap_kem(source_numbers)
                results['predictions']['theo_cap_kem'] = theo_cap_kem_result
                print(f"✅ Dự đoán theo cặp số đi kèm: {theo_cap_kem_result.get('predicted_numbers', [])} (Độ tin cậy: {theo_cap_kem_result.get('confidence', 0)}%)")
            except Exception as e:
                logger.error(f"❌ Lỗi khi dự đoán theo cặp số đi kèm: {e}")
                logger.error(traceback.format_exc())
            
            # 5. Dự đoán theo lô
            print("5. Bắt đầu dự đoán theo lô...")
            try:
                theo_lo_result = self.predict_theo_lo(source_numbers)
                results['predictions']['theo_lo'] = theo_lo_result
                print(f"✅ Dự đoán theo lô: {theo_lo_result.get('predicted_numbers', [])} (Độ tin cậy: {theo_lo_result.get('confidence', 0)}%)")
            except Exception as e:
                logger.error(f"❌ Lỗi khi dự đoán theo lô: {e}")
                logger.error(traceback.format_exc())
            
            # 6. Dự đoán theo đầu câm và đuôi câm
            print("6. Bắt đầu dự đoán theo đầu câm và đuôi câm...")
            try:
                dau_cam_list, duoi_cam_list = self._find_dau_duoi_cam(source_numbers)
                print(f"Đầu câm: {dau_cam_list}, Đuôi câm: {duoi_cam_list}")
                
                # 6.1 Dự đoán theo đầu câm
                theo_dau_cam_result = self.predict_theo_dau_cam(dau_cam_list)
                results['predictions']['theo_dau_cam'] = theo_dau_cam_result
                print(f"✅ Dự đoán theo đầu câm: {theo_dau_cam_result.get('predicted_numbers', [])} (Độ tin cậy: {theo_dau_cam_result.get('confidence', 0)}%)")
                
                # 6.2 Dự đoán theo đuôi câm
                theo_duoi_cam_result = self.predict_theo_duoi_cam(duoi_cam_list)
                results['predictions']['theo_duoi_cam'] = theo_duoi_cam_result
                print(f"✅ Dự đoán theo đuôi câm: {theo_duoi_cam_result.get('predicted_numbers', [])} (Độ tin cậy: {theo_duoi_cam_result.get('confidence', 0)}%)")
            except Exception as e:
                logger.error(f"❌ Lỗi khi dự đoán theo đầu câm và đuôi câm: {e}")
                logger.error(traceback.format_exc())
            
            # 7. Dự đoán theo phương pháp đầu đuôi câm mới
            print("7. Bắt đầu dự đoán theo phương pháp đầu đuôi câm mới...")
            try:
                theo_dau_duoi_cam_result = self.predict_theo_dau_duoi_cam(dau_cam_list, duoi_cam_list)
                results['predictions']['theo_dau_duoi_cam'] = theo_dau_duoi_cam_result
                print(f"✅ Dự đoán theo đầu đuôi câm mới: {theo_dau_duoi_cam_result.get('predicted_numbers', [])} (Độ tin cậy: {theo_dau_duoi_cam_result.get('confidence', 0)}%)")
            except Exception as e:
                logger.error(f"❌ Lỗi khi dự đoán theo đầu đuôi câm mới: {e}")
                logger.error(traceback.format_exc())
            
            # 8. Dự đoán theo kép
            print("8. Bắt đầu dự đoán theo kép...")
            try:
                kep_list = self._find_kep_numbers(source_numbers)
                print(f"Số kép: {kep_list}")
                theo_kep_result = self.predict_theo_kep(kep_list)
                results['predictions']['theo_kep'] = theo_kep_result
                print(f"✅ Dự đoán theo kép: {theo_kep_result.get('predicted_numbers', [])} (Độ tin cậy: {theo_kep_result.get('confidence', 0)}%)")
            except Exception as e:
                logger.error(f"❌ Lỗi khi dự đoán theo kép: {e}")
                logger.error(traceback.format_exc())
            
            # 9. Dự đoán với quy luật đã phát hiện
            print("9. Bắt đầu dự đoán với quy luật đã phát hiện...")
            try:
                discovered_rules_result = self.predict_with_discovered_rules(source_numbers)
                results['predictions']['discovered_rules'] = discovered_rules_result
                print(f"✅ Dự đoán với quy luật đã phát hiện: {discovered_rules_result.get('predicted_numbers', [])} (Độ tin cậy: {discovered_rules_result.get('confidence', 0)}%)")
                if 'matched_rules' in discovered_rules_result:
                    print(f"Số quy luật khớp: {len(discovered_rules_result['matched_rules'])}")
            except Exception as e:
                logger.error(f"❌ Lỗi khi dự đoán với quy luật đã phát hiện: {e}")
                logger.error(traceback.format_exc())
            
            # 10. Dự đoán với mô hình học máy nâng cao
            print("10. Bắt đầu dự đoán với mô hình học máy nâng cao...")
            try:
                ml_result = self.predict_with_advanced_ml(source_numbers)
                results['predictions']['ml_advanced'] = ml_result
                print(f"✅ Dự đoán với mô hình học máy nâng cao: {ml_result.get('predicted_numbers', [])} (Độ tin cậy: {ml_result.get('confidence', 0)}%)")
            except Exception as e:
                logger.error(f"❌ Lỗi khi dự đoán với mô hình học máy nâng cao: {e}")
                logger.error(traceback.format_exc())
            
            # 11. Dự đoán với phương pháp ensemble
            print("11. Bắt đầu dự đoán với phương pháp ensemble...")
            try:
                ensemble_result = self.predict_with_ensemble(source_numbers)
                results['predictions']['ensemble'] = ensemble_result
                print(f"✅ Dự đoán với phương pháp ensemble: {ensemble_result.get('predicted_numbers', [])} (Độ tin cậy: {ensemble_result.get('confidence', 0)}%)")
            except Exception as e:
                logger.error(f"❌ Lỗi khi dự đoán với phương pháp ensemble: {e}")
                logger.error(traceback.format_exc())
            
            # 12. Phát hiện và sử dụng quy luật chu kỳ
            print("12. Bắt đầu phát hiện và sử dụng quy luật chu kỳ...")
            try:
                cyclical_patterns = self.discover_cyclical_patterns()
                print(f"Số mẫu chu kỳ phát hiện được: {len(cyclical_patterns)}")
                
                target_date_str = self.target_date.strftime('%Y-%m-%d')
                cyclical_predictions = [
                    pattern['number'] for pattern in cyclical_patterns
                    if pattern['predicted_next_date'] == target_date_str and pattern['confidence'] >= 60
                ]
                results['predictions']['cyclical'] = {
                    'predicted_numbers': cyclical_predictions,
                    'confidence': 70 if cyclical_predictions else 0,
                    'method': 'cyclical'
                }
                print(f"✅ Dự đoán với quy luật chu kỳ: {cyclical_predictions} (Độ tin cậy: {70 if cyclical_predictions else 0}%)")
            except Exception as e:
                logger.error(f"❌ Lỗi khi phát hiện và sử dụng quy luật chu kỳ: {e}")
                logger.error(traceback.format_exc())
            
            # 13. Phân tích xu hướng thị trường
            print("13. Bắt đầu phân tích xu hướng thị trường...")
            try:
                market_trend_result = self.analyze_market_trend()
                results['predictions']['market_trend'] = market_trend_result
                print(f"✅ Phân tích xu hướng thị trường: {market_trend_result.get('predicted_numbers', [])} (Độ tin cậy: {market_trend_result.get('confidence', 0)}%)")
                if 'hot_numbers' in market_trend_result:
                    print(f"Số nóng: {market_trend_result['hot_numbers']}")
                if 'cold_numbers' in market_trend_result:
                    print(f"Số lạnh: {market_trend_result['cold_numbers']}")
            except Exception as e:
                logger.error(f"❌ Lỗi khi phân tích xu hướng thị trường: {e}")
                logger.error(traceback.format_exc())
            
            # 14. Phân tích chu kỳ mệt mỏi để điều chỉnh trọng số
            print("14. Bắt đầu phân tích chu kỳ mệt mỏi...")
            try:
                method_cycles = self.analyze_method_fatigue_cycles()
                results['method_cycles'] = method_cycles
                
                # Log các phương pháp mệt mỏi
                tired_methods = [method for method, data in method_cycles.items() if data.get('is_tired', False)]
                print(f"Phương pháp mệt mỏi: {tired_methods}")
                
                # Log hiệu suất gần đây của các phương pháp
                for method, data in method_cycles.items():
                    print(f"Hiệu suất gần đây của {method}: {data.get('recent_performance', 0)}% - Xu hướng: {data.get('performance_trend', 'stable')}")
            except Exception as e:
                logger.error(f"❌ Lỗi khi phân tích chu kỳ mệt mỏi: {e}")
                logger.error(traceback.format_exc())
            
            # 15. Tối ưu hóa trọng số
            print("15. Bắt đầu tối ưu hóa trọng số...")
            optimized_weights = None
            try:
                optimized_weights = self.optimize_method_weights()
                print(f"✅ Tối ưu hóa trọng số thành công: {optimized_weights}")
            except Exception as e:
                logger.error(f"❌ Lỗi khi tối ưu hóa trọng số: {e}")
                logger.error(traceback.format_exc())
                print("Sử dụng trọng số lịch sử thay thế...")
                optimized_weights = self._get_historical_method_weights()
                print(f"Trọng số lịch sử: {optimized_weights}")
            
            # 16. Kết hợp tất cả các phương pháp với trọng số tối ưu
            print("16. Bắt đầu kết hợp tất cả các phương pháp...")
            try:
                combined_result = self.combine_predictions_with_weights(results['predictions'], optimized_weights)
                results['predictions']['ket_hop'] = combined_result
                print(f"✅ Kết hợp tất cả các phương pháp: {combined_result.get('predicted_numbers', [])} (Độ tin cậy: {combined_result.get('confidence', 0)}%)")
                print(f"Điểm số của các số: {combined_result.get('number_scores', {})}")
            except Exception as e:
                logger.error(f"❌ Lỗi khi kết hợp tất cả các phương pháp: {e}")
                logger.error(traceback.format_exc())
            
            # 17. Đánh giá độ tin cậy tổng thể
            print("17. Bắt đầu đánh giá độ tin cậy tổng thể...")
            try:
                overall_confidence = self.calculate_overall_confidence(results['predictions'])
                results['overall_confidence'] = overall_confidence
                print(f"✅ Độ tin cậy tổng thể: {overall_confidence.get('overall_confidence', 0)}%")
                print(f"Mức độ đồng thuận: {overall_confidence.get('consensus_level', 'Không xác định')}")
                print(f"Số đồng thuận mạnh: {overall_confidence.get('strong_consensus_numbers', [])}")
            except Exception as e:
                logger.error(f"❌ Lỗi khi đánh giá độ tin cậy tổng thể: {e}")
                logger.error(traceback.format_exc())
            
            # 18. Lưu kết quả phân tích và dự đoán
            print("18. Bắt đầu lưu kết quả phân tích và dự đoán...")
            print("18. Bắt đầu lưu kết quả phân tích và dự đoán...")
            try:
                self._save_predictions(results)
                print("✅ Đã lưu kết quả phân tích và dự đoán vào cơ sở dữ liệu")
            except Exception as e:
                logger.error(f"❌ Lỗi khi lưu kết quả phân tích và dự đoán: {e}")
                logger.error(traceback.format_exc())
            
            print(f"===== KẾT THÚC PHÂN TÍCH VÀ DỰ ĐOÁN CHO NGÀY {self.target_date} =====")
            
            return results
        
        except Exception as e:
            logger.error(f"❌❌❌ LỖI NGHIÊM TRỌNG TRONG QUÁ TRÌNH PHÂN TÍCH: {e}")
            logger.error(traceback.format_exc())
            return {'error': f'Lỗi trong quá trình phân tích: {str(e)}'}

    def predict_theo_ngay(self, source_numbers):
        """
        Dự đoán theo quy tắc ngày
        Args:
            source_numbers: Danh sách số 2 chữ số từ kết quả hôm trước
        Returns:
            Dict chứa kết quả dự đoán
        """
        predictions = []
        matched_rules = []
        
        for rule in self.ngay_rules:
            conditions, results = rule
            # Kiểm tra điều kiện
            matched = False
            if isinstance(conditions, list):
                # Nếu điều kiện là một danh sách các số cần xuất hiện cùng nhau
                matched = all(condition in source_numbers for condition in conditions)
            else:
                # Nếu điều kiện là một số duy nhất
                matched = conditions in source_numbers
            
            if matched:
                matched_rules.append((conditions, results))
                predictions.extend(results)
        
        # Loại bỏ trùng lặp và tính tần suất
        prediction_counts = defaultdict(int)
        for num in predictions:
            prediction_counts[num] += 1
        
        # Sắp xếp theo tần suất giảm dần
        sorted_predictions = sorted(prediction_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Đánh giá độ tin cậy và điều chỉnh dựa trên hiệu quả lịch sử
        base_confidence = min(100, len(matched_rules) * 20)  # 20% cho mỗi quy tắc khớp, tối đa 100%
        historical_performance = self._get_historical_method_performance('theo_ngay')
        adjusted_confidence = self._adjust_confidence_by_history(base_confidence, historical_performance)
        
        return {
            'predicted_numbers': [num for num, _ in sorted_predictions[:12]],  # Top 12 số
            'frequency': {num: count for num, count in sorted_predictions[:12]},
            'confidence': adjusted_confidence,
            'matched_rules': matched_rules,
            'method': 'theo_ngay'
        }

    def predict_theo_tong_db(self, db_number):
        """
        Dự đoán theo tổng giải đặc biệt
        Args:
            db_number: Hai số cuối của giải đặc biệt hôm trước
        Returns:
            Dict chứa kết quả dự đoán
        """
        # Tính tổng 2 số cuối của giải đặc biệt
        db_sum = sum(int(digit) for digit in db_number)
        
        # Dự đoán tổng đề ngày mai dựa trên quy tắc
        predicted_sum = self.tong_db_rules.get(db_sum % 10, None)
        
        if predicted_sum is None:
            return {
                'predicted_numbers': [],
                'confidence': 0,
                'source_sum': db_sum % 10,
                'predicted_sum': None,
                'method': 'theo_tong_db'
            }
        
        # Xử lý trường hợp predicted_sum là một list
        predicted_sums = [predicted_sum] if not isinstance(predicted_sum, list) else predicted_sum
        
        # Tạo tất cả các cặp số có tổng bằng predicted_sum
        predicted_numbers = []
        for predicted_sum in predicted_sums:
            for i in range(10):
                j = (predicted_sum - i) % 10
                if 0 <= j < 10:
                    predicted_numbers.append(f"{i}{j}")
        
        # Đánh giá độ tin cậy và điều chỉnh dựa trên hiệu quả lịch sử
        base_confidence = 70  # Độ tin cậy mặc định cho phương pháp này
        historical_performance = self._get_historical_method_performance('theo_tong_db')
        adjusted_confidence = self._adjust_confidence_by_history(base_confidence, historical_performance)
        
        return {
            'predicted_numbers': predicted_numbers,
            'confidence': adjusted_confidence,
            'source_sum': db_sum % 10,
            'predicted_sum': predicted_sums,
            'method': 'theo_tong_db'
        }

    def predict_theo_thu(self, weekday):
        """
        Dự đoán theo thứ trong tuần
        Args:
            weekday: Thứ trong tuần (0-6, thứ 2 đến chủ nhật)
        Returns:
            Dict chứa kết quả dự đoán
        """
        predictions = []
        matched_rules = []
        
        # Kiểm tra các quy tắc theo thứ
        for days, numbers in self.thu_rules.items():
            if weekday in days:
                predictions.extend(numbers)
                matched_rules.append((days, numbers))
        
        # Loại bỏ trùng lặp
        unique_predictions = list(set(predictions))
        
        # Đánh giá độ tin cậy và điều chỉnh dựa trên hiệu quả lịch sử
        base_confidence = min(100, len(matched_rules) * 25)  # 25% cho mỗi quy tắc khớp, tối đa 100%
        historical_performance = self._get_historical_method_performance('theo_thu')
        adjusted_confidence = self._adjust_confidence_by_history(base_confidence, historical_performance)
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': adjusted_confidence,
            'weekday': weekday,
            'weekday_name': self._get_weekday_name(weekday),
            'matched_rules': matched_rules,
            'method': 'theo_thu'
        }

    def predict_theo_cap_kem(self, source_numbers):
        """
        Dự đoán theo cặp số đi kèm
        Args:
            source_numbers: Danh sách số 2 chữ số từ kết quả hôm trước
        Returns:
            Dict chứa kết quả dự đoán
        """
        predictions = []
        matched_rules = []
        
        # Kiểm tra từng quy tắc
        for condition, results in self.cap_kem_rules.items():
            # Xử lý điều kiện là cặp số hoặc số đơn
            if isinstance(condition, tuple):
                matched = all(c in source_numbers for c in condition)
            else:
                matched = condition in source_numbers
            
            if matched:
                matched_rules.append((condition, results))
                predictions.extend(results)
        
        # Loại bỏ trùng lặp
        unique_predictions = list(set(predictions))
        
        # Đánh giá độ tin cậy và điều chỉnh dựa trên hiệu quả lịch sử
        base_confidence = min(100, len(matched_rules) * 25)  # 25% cho mỗi quy tắc khớp, tối đa 100%
        historical_performance = self._get_historical_method_performance('theo_cap_kem')
        adjusted_confidence = self._adjust_confidence_by_history(base_confidence, historical_performance)
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': adjusted_confidence,
            'matched_rules': matched_rules,
            'method': 'theo_cap_kem'
        }

    def predict_theo_lo(self, source_numbers):
        """
        Dự đoán theo lô
        Args:
            source_numbers: Danh sách số 2 chữ số từ kết quả hôm trước
        Returns:
            Dict chứa kết quả dự đoán
        """
        predictions = []
        matched_rules = []
        
        # Kiểm tra từng quy tắc
        for number in source_numbers:
            if number in self.lo_rules:
                predicted = self.lo_rules[number]
                predictions.append(predicted)
                matched_rules.append((number, predicted))
        
        # Loại bỏ trùng lặp
        unique_predictions = list(set(predictions))
        
        # Đánh giá độ tin cậy và điều chỉnh dựa trên hiệu quả lịch sử
        base_confidence = min(100, len(matched_rules) * 20)  # 20% cho mỗi quy tắc khớp, tối đa 100%
        historical_performance = self._get_historical_method_performance('theo_lo')
        adjusted_confidence = self._adjust_confidence_by_history(base_confidence, historical_performance)
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': adjusted_confidence,
            'matched_rules': matched_rules,
            'method': 'theo_lo'
        }

    def predict_theo_dau_cam(self, dau_cam_list):
        """
        Dự đoán theo đầu câm
        Args:
            dau_cam_list: Danh sách các đầu câm
        Returns:
            Dict chứa kết quả dự đoán
        """
        predictions = []
        matched_rules = []
        
        # Kiểm tra từng đầu câm
        for dau in dau_cam_list:
            if dau in self.dau_cam_rules:
                predicted_numbers = self.dau_cam_rules[dau]
                predictions.extend(predicted_numbers)
                matched_rules.append((dau, predicted_numbers))
        
        # Loại bỏ trùng lặp
        unique_predictions = list(set(predictions))
        
        # Đánh giá độ tin cậy và điều chỉnh dựa trên hiệu quả lịch sử
        base_confidence = min(100, len(matched_rules) * 15)  # 15% cho mỗi quy tắc khớp, tối đa 100%
        historical_performance = self._get_historical_method_performance('theo_dau_cam')
        adjusted_confidence = self._adjust_confidence_by_history(base_confidence, historical_performance)
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': adjusted_confidence,
            'dau_cam': dau_cam_list,
            'matched_rules': matched_rules,
            'method': 'theo_dau_cam'
        }

    def predict_theo_duoi_cam(self, duoi_cam_list):
        """
        Dự đoán theo đuôi câm
        Args:
            duoi_cam_list: Danh sách các đuôi câm
        Returns:
            Dict chứa kết quả dự đoán
        """
        predictions = []
        matched_rules = []
        
        # Kiểm tra từng đuôi câm
        for duoi in duoi_cam_list:
            if duoi in self.duoi_cam_rules:
                predicted_numbers = self.duoi_cam_rules[duoi]
                predictions.extend(predicted_numbers)
                matched_rules.append((duoi, predicted_numbers))
        
        # Loại bỏ trùng lặp
        unique_predictions = list(set(predictions))
        
        # Đánh giá độ tin cậy và điều chỉnh dựa trên hiệu quả lịch sử
        base_confidence = min(100, len(matched_rules) * 15)  # 15% cho mỗi quy tắc khớp, tối đa 100%
        historical_performance = self._get_historical_method_performance('theo_duoi_cam')
        adjusted_confidence = self._adjust_confidence_by_history(base_confidence, historical_performance)
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': adjusted_confidence,
            'duoi_cam': duoi_cam_list,
            'matched_rules': matched_rules,
            'method': 'theo_duoi_cam'
        }

    def predict_theo_dau_duoi_cam(self, dau_cam_list, duoi_cam_list):
        """
        Dự đoán theo phương pháp đầu đuôi câm mới
        Args:
            dau_cam_list: Danh sách các đầu câm
            duoi_cam_list: Danh sách các đuôi câm
        Returns:
            Dict chứa kết quả dự đoán
        """
        predictions = []
        matched_rules = []
        
        # Áp dụng các quy tắc dựa trên số lượng chữ số câm
        # 1. Nếu có 1 chữ số câm
        if len(dau_cam_list) == 1:
            x = dau_cam_list[0]
            rule_results = self.dau_duoi_cam_rules['single'](x)
            predictions.extend(rule_results)
            matched_rules.append(('single', x, rule_results))
        
        # 2. Nếu có 2 chữ số câm ở đầu
        if len(dau_cam_list) == 2:
            x, y = dau_cam_list
            rule_results = self.dau_duoi_cam_rules['double'](x, y)
            predictions.extend(rule_results)
            matched_rules.append(('double', (x, y), rule_results))
        
        # 3. Nếu có 3 chữ số câm ở đầu
        if len(dau_cam_list) == 3:
            # Sắp xếp theo thứ tự tăng dần
            x, y, z = sorted(dau_cam_list)
            rule_results = self.dau_duoi_cam_rules['triple'](x, y, z)
            predictions.extend(rule_results)
            matched_rules.append(('triple', (x, y, z), rule_results))
        
        # 4. Nếu có 1 chữ số câm ở đuôi
        if len(duoi_cam_list) == 1:
            x = duoi_cam_list[0]
            rule_results = self.dau_duoi_cam_rules['single'](x)
            predictions.extend(rule_results)
            matched_rules.append(('single_duoi', x, rule_results))
        
        # 5. Trường hợp đặc biệt: Đầu 3 câm và đuôi 7 câm
        if '3' in dau_cam_list and '7' in duoi_cam_list:
            predictions.append('73')
            matched_rules.append(('special', ('3', '7'), ['73']))
        
        # Loại bỏ trùng lặp
        unique_predictions = list(set(predictions))
        
        # Đánh giá độ tin cậy
        base_confidence = min(100, len(matched_rules) * 20)  # 20% cho mỗi quy tắc khớp, tối đa 100%
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': base_confidence,
            'dau_cam': dau_cam_list,
            'duoi_cam': duoi_cam_list,
            'matched_rules': matched_rules,
            'method': 'theo_dau_duoi_cam'
        }

    def predict_theo_kep(self, kep_list):
        """
        Dự đoán theo kép
        Args:
            kep_list: Danh sách các số kép xuất hiện
        Returns:
            Dict chứa kết quả dự đoán
        """
        predictions = []
        matched_rules = []
        
        # Nếu không có kép nào
        if not kep_list:
            predicted = self.kep_rules.get('no_kep', [])
            if isinstance(predicted, list):
                predictions.extend(predicted)
            else:
                predictions.append(predicted)
            matched_rules.append(('no_kep', predicted))
        # Nếu có 3 kép
        elif len(kep_list) == 3:
            predicted = self.kep_rules.get('3_kep', [])
            if isinstance(predicted, list):
                predictions.extend(predicted)
            else:
                predictions.append(predicted)
            matched_rules.append(('3_kep', predicted))
        # Xử lý từng kép
        else:
            for kep in kep_list:
                if kep in self.kep_rules:
                    predicted = self.kep_rules[kep]
                    if isinstance(predicted, list):
                        predictions.extend(predicted)
                    else:
                        predictions.append(predicted)
                    matched_rules.append((kep, predicted))
        
        # Loại bỏ trùng lặp
        unique_predictions = list(set(predictions))
        
        # Đánh giá độ tin cậy
        base_confidence = min(100, len(matched_rules) * 25)  # 25% cho mỗi quy tắc khớp, tối đa 100%
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': base_confidence,
            'kep_list': kep_list,
            'matched_rules': matched_rules,
            'method': 'theo_kep'
        }

    def predict_with_discovered_rules(self, source_numbers):
        """
        Dự đoán dựa trên các quy luật đã phát hiện từ dữ liệu lịch sử
        Args:
            source_numbers: Danh sách số 2 chữ số từ kết quả hôm trước
        Returns:
            Dict chứa kết quả dự đoán
        """
        try:
            # Lấy các quy luật đã phát hiện từ cơ sở dữ liệu
            discovered_rules = QuyLuatBacNho.objects.filter(
                he_so_tin_cay__gte=50  # Chỉ lấy các quy luật có độ tin cậy cao
            ).order_by('-he_so_tin_cay')
            
            # Nếu không có quy luật nào, trả về kết quả trống
            if not discovered_rules.exists():
                return {
                    'predicted_numbers': [],
                    'confidence': 0,
                    'matched_rules': [],
                    'method': 'discovered_rules'
                }
            
            predictions = []
            matched_rules = []
            
            # Áp dụng các quy luật theo ngày
            for rule in discovered_rules.filter(loai_quy_luat='theo_ngay'):
                try:
                    # Lấy điều kiện và kết quả
                    conditions = json.loads(rule.dieu_kien)
                    results = json.loads(rule.ket_qua)
                    
                    # Kiểm tra điều kiện
                    if all(condition in source_numbers for condition in conditions):
                        matched_rules.append({
                            'id': rule.id,
                            'mo_ta': rule.mo_ta,
                            'he_so_tin_cay': rule.he_so_tin_cay
                        })
                        predictions.extend(results)
                except Exception as e:
                    logger.error(f"Lỗi khi áp dụng quy luật theo ngày: {e}")
                    continue
            
            # Áp dụng các quy luật theo thứ
            weekday = self.target_date.weekday()
            for rule in discovered_rules.filter(loai_quy_luat='theo_thu'):
                try:
                    condition = json.loads(rule.dieu_kien)
                    results = json.loads(rule.ket_qua)
                    
                    # Kiểm tra điều kiện thứ
                    if condition.get('weekday') == weekday:
                        matched_rules.append({
                            'id': rule.id,
                            'mo_ta': rule.mo_ta,
                            'he_so_tin_cay': rule.he_so_tin_cay
                        })
                        predictions.extend(results)
                except Exception as e:
                    logger.error(f"Lỗi khi áp dụng quy luật theo thứ: {e}")
                    continue
            
            # Áp dụng các quy luật theo lô
            for rule in discovered_rules.filter(loai_quy_luat='theo_lo'):
                try:
                    conditions = json.loads(rule.dieu_kien)
                    results = json.loads(rule.ket_qua)
                    
                    # Kiểm tra điều kiện
                    if isinstance(conditions, list):
                        if any(condition in source_numbers for condition in conditions):
                            matched_rules.append({
                                'id': rule.id,
                                'mo_ta': rule.mo_ta,
                                'he_so_tin_cay': rule.he_so_tin_cay
                            })
                            predictions.extend(results)
                except Exception as e:
                    logger.error(f"Lỗi khi áp dụng quy luật theo lô: {e}")
                    continue
            
            # Loại bỏ trùng lặp
            unique_predictions = list(set(predictions))
            
            # Tính độ tin cậy trung bình của các quy luật khớp
            avg_confidence = 0
            if matched_rules:
                avg_confidence = sum(rule['he_so_tin_cay'] for rule in matched_rules) / len(matched_rules)
            
            # Giới hạn số lượng dự đoán
            if len(unique_predictions) > 10:
                # Đếm tần suất xuất hiện của mỗi số trong các dự đoán
                prediction_counts = defaultdict(int)
                for num in predictions:
                    prediction_counts[num] += 1
                
                # Sắp xếp theo tần suất giảm dần
                sorted_predictions = sorted(prediction_counts.items(), key=lambda x: x[1], reverse=True)
                unique_predictions = [num for num, _ in sorted_predictions[:10]]
            
            return {
                'predicted_numbers': unique_predictions[:5],  # Top 5 số
                'confidence': min(100, avg_confidence),
                'matched_rules': matched_rules,
                'method': 'discovered_rules'
            }
        except Exception as e:
            logger.error(f"Lỗi khi dự đoán với quy luật đã phát hiện: {e}")
            return {
                'predicted_numbers': [],
                'confidence': 0,
                'error': str(e),
                'method': 'discovered_rules'
            }

    def predict_with_advanced_ml(self, source_numbers):
        """
        Sử dụng học máy nâng cao để dự đoán kết quả
        Args:
            source_numbers: Danh sách số 2 chữ số từ kết quả hôm trước
        Returns:
            Dict chứa kết quả dự đoán
        """
        try:
            print("Bắt đầu dự đoán với học máy nâng cao...")
            
            # Kiểm tra nếu đã có mô hình được huấn luyện
            if 'random_forest' in self.ml_models and 'gradient_boosting' in self.ml_models:
                print("Sử dụng mô hình ML đã cache")
                rf_model = self.ml_models['random_forest']
                xgb_model = self.ml_models.get('xgboost')
                lgbm_model = self.ml_models.get('lightgbm')
            else:
                print("Huấn luyện mô hình ML mới...")
                # Lấy dữ liệu lịch sử cho huấn luyện
                end_date = self.source_date
                start_date = end_date - timedelta(days=730)  # Lấy dữ liệu 2 năm
                print(f"Lấy dữ liệu từ {start_date} đến {end_date}")
                
                # Lấy tất cả kết quả xổ số trong khoảng thời gian
                results = KetQuaXoSo.objects.filter(
                    ngay__range=(start_date, end_date)
                ).order_by('ngay')
                
                print(f"Tìm thấy {len(results)} kết quả xổ số")
                
                if len(results) < 10:
                    logger.warning("Không đủ dữ liệu để huấn luyện mô hình ML")
                    return {
                        'predicted_numbers': [],
                        'confidence': 0,
                        'method': 'ml_advanced'
                    }
                
                # Tạo dữ liệu huấn luyện
                X = []  # Features
                y = []  # Labels (các số 2 chữ số)
                
                print("Bắt đầu tạo features từ dữ liệu...")
                for i in range(len(results) - 1):
                    try:
                        current_result = results[i]
                        next_result = results[i + 1]
                        
                        # Lấy các số 2 chữ số từ kết quả hiện tại
                        current_numbers = self._get_all_2digit_numbers(current_result)
                        
                        # Lấy các số 2 chữ số từ kết quả tiếp theo
                        next_numbers = self._get_all_2digit_numbers(next_result)
                        
                        # Tạo features
                        features = self._create_ml_features(current_result, current_numbers)
                        
                        # Thêm vào dữ liệu huấn luyện
                        for next_num in next_numbers:
                            X.append(features)
                            y.append(int(next_num))
                    except Exception as e:
                        logger.error(f"Lỗi khi xử lý kết quả thứ {i}: {e}")
                
                print(f"Đã tạo {len(X)} mẫu huấn luyện, {len(y)} nhãn")
                
                # Kiểm tra dữ liệu huấn luyện
                if not X or not y:
                    logger.warning("Không tạo được dữ liệu huấn luyện")
                    return {
                        'predicted_numbers': [],
                        'confidence': 0,
                        'method': 'ml_advanced'
                    }
                
                # Chia dữ liệu thành tập huấn luyện và tập kiểm thử
                print("Chia dữ liệu thành tập huấn luyện và tập kiểm thử...")
                try:
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.2, random_state=42
                    )
                    print(f"Tập huấn luyện: {len(X_train)} mẫu, Tập kiểm thử: {len(X_test)} mẫu")
                except Exception as e:
                    logger.error(f"Lỗi khi chia dữ liệu: {e}")
                    raise
                
                # Kiểm tra ml_config
                if not hasattr(self, 'ml_config') or not self.ml_config:
                    logger.warning("Không tìm thấy ml_config, sử dụng cấu hình mặc định")
                    
                    self.ml_config = {
                        'random_forest': {
                            'n_estimators': 100,
                            'max_depth': 10,
                            'random_state': 42
                        },
                        'xgboost': {
                            'n_estimators': 100,
                            'max_depth': 5,
                            'learning_rate': 0.1,
                            'subsample': 0.8,
                            'colsample_bytree': 0.8,
                            'random_state': 42
                        },
                        'lightgbm': {
                            'n_estimators': 100,
                            'max_depth': 5,
                            'learning_rate': 0.1,
                            'subsample': 0.8,
                            'colsample_bytree': 0.8,
                            'random_state': 42
                        }
                }
                
                
                # Huấn luyện mô hình Random Forest
                print("Huấn luyện mô hình Random Forest...")
                try:
                    rf_model = RandomForestClassifier(**self.ml_config['random_forest'])
                    rf_model.fit(X_train, y_train)
                    print("Huấn luyện Random Forest thành công")
                except Exception as e:
                    logger.error(f"Lỗi khi huấn luyện Random Forest: {e}")
                    raise
                
                # Khởi tạo xgb_model và lgbm_model là None
                xgb_model = None
                lgbm_model = None
                
                # Huấn luyện mô hình XGBoost
                print("Huấn luyện mô hình XGBoost...")
                try:
                    import xgboost as xgb
                    xgb_model = xgb.XGBClassifier(**self.ml_config['xgboost'])
                    xgb_model.fit(X_train, y_train)
                    print("Huấn luyện XGBoost thành công")
                except ImportError:
                    print("Thư viện XGBoost không được cài đặt. Bỏ qua mô hình XGBoost.")
                except MemoryError:
                    print("Lỗi bộ nhớ khi huấn luyện XGBoost. Bỏ qua mô hình XGBoost.")
                except Exception as e:
                    print(f"Lỗi khi huấn luyện XGBoost: {e}")
                    print(traceback.format_exc())
                
                # Huấn luyện mô hình LightGBM
                print("Huấn luyện mô hình LightGBM...")
                try:
                    import lightgbm as lgb
                    lgbm_model = lgb.LGBMClassifier(**self.ml_config['lightgbm'])
                    lgbm_model.fit(X_train, y_train)
                    print("Huấn luyện LightGBM thành công")
                except ImportError:
                    print("Thư viện LightGBM không được cài đặt. Bỏ qua mô hình LightGBM.")
                except MemoryError:
                    print("Lỗi bộ nhớ khi huấn luyện LightGBM. Bỏ qua mô hình LightGBM.")
                except Exception as e:
                    print(f"Lỗi khi huấn luyện LightGBM: {e}")
                    print(traceback.format_exc())
                
                # Đánh giá mô hình
                print("Đánh giá mô hình...")
                try:
                    rf_preds = rf_model.predict(X_test)
                    rf_accuracy = accuracy_score(y_test, rf_preds)
                    print(f"Random Forest accuracy: {rf_accuracy:.4f}")
                    
                    if xgb_model:
                        xgb_preds = xgb_model.predict(X_test)
                        xgb_accuracy = accuracy_score(y_test, xgb_preds)
                        print(f"XGBoost accuracy: {xgb_accuracy:.4f}")
                    
                    if lgbm_model:
                        lgbm_preds = lgbm_model.predict(X_test)
                        lgbm_accuracy = accuracy_score(y_test, lgbm_preds)
                        print(f"LightGBM accuracy: {lgbm_accuracy:.4f}")
                except Exception as e:
                    print(f"Lỗi khi đánh giá mô hình: {e}")
                
                # Lưu mô hình vào cache
                print("Lưu mô hình vào cache...")
                self.ml_models = {
                    'random_forest': rf_model
                }
                if xgb_model:
                    self.ml_models['xgboost'] = xgb_model
                
                if lgbm_model:
                    self.ml_models['lightgbm'] = lgbm_model
            
            # Tạo features cho dự đoán
            print("Tạo features cho dự đoán...")
            try:
                source_result = self._get_xoso_result(self.source_date)
                predict_features = self._create_ml_features(source_result, source_numbers)
            except Exception as e:
                print(f"Lỗi khi tạo features cho dự đoán: {e}")
                raise
            
            # Dự đoán xác suất cho tất cả các số
            print("Dự đoán xác suất...")
            try:
                rf_proba = rf_model.predict_proba([predict_features])[0]
                # Khởi tạo các mảng xác suất từ các mô hình khác
                xgb_proba = None
                lgbm_proba = None
                if 'xgboost' in self.ml_models and self.ml_models['xgboost']:
                    xgb_proba = self.ml_models['xgboost'].predict_proba([predict_features])[0]
                
                if 'lightgbm' in self.ml_models and self.ml_models['lightgbm']:
                    lgbm_proba = self.ml_models['lightgbm'].predict_proba([predict_features])[0]
                
                # Kết hợp xác suất từ cả hai mô hình (weighted average)
                if xgb_proba is not None and lgbm_proba is not None:
                    # Nếu có cả XGBoost và LightGBM
                    combined_proba = rf_proba * 0.4 + xgb_proba * 0.3 + lgbm_proba * 0.3
                elif xgb_proba is not None:
                    # Nếu chỉ có XGBoost
                    combined_proba = rf_proba * 0.5 + xgb_proba * 0.5
                elif lgbm_proba is not None:
                    # Nếu chỉ có LightGBM
                    combined_proba = rf_proba * 0.5 + lgbm_proba * 0.5
                else:
                    # Nếu chỉ có Random Forest
                    combined_proba = rf_proba
            except Exception as e:
                print(f"Lỗi khi dự đoán xác suất: {e}")
                raise
            
            # Lấy top 15 số có xác suất cao nhất
            print("Xử lý kết quả dự đoán...")
            try:
                import numpy as np
                top_indices = np.argsort(combined_proba)[-15:][::-1]
                top_numbers = [f"{idx:02d}" for idx in top_indices]
                top_probas = [combined_proba[idx] for idx in top_indices]
                
                # Tính độ tin cậy dựa trên xác suất trung bình của top 5 số
                confidence = min(100, sum(top_probas[:5]) * 200)  # Nhân 2 để scale lên
                print(f"Top 8 số dự đoán: {top_numbers[:8]}")
                print(f"Độ tin cậy: {confidence}%")
            except Exception as e:
                print(f"Lỗi khi xử lý kết quả dự đoán: {e}")
                raise
            
            return {
                'predicted_numbers': top_numbers[:8],  # Top 8 số
                'confidence': confidence,
                'all_predictions': list(zip(top_numbers, [p * 100 for p in top_probas])),
                'method': 'ml_advanced'
            }
        except Exception as e:
            print(f"Lỗi khi dự đoán bằng học máy nâng cao: {e}")
            print(traceback.format_exc())  # In ra stack trace đầy đủ
            return {
                'predicted_numbers': [],
                'confidence': 0,
                'error': str(e),
                'method': 'ml_advanced'
            }

            
    def predict_with_ensemble(self, source_numbers):
        """
        Dự đoán sử dụng phương pháp ensemble (kết hợp nhiều mô hình)
        Args:
            source_numbers: Danh sách số 2 chữ số từ kết quả hôm trước
        Returns:
            Dict chứa kết quả dự đoán
        """
        try:
            # Sử dụng các phương pháp cơ bản để tạo bộ dự đoán ban đầu
            base_predictions = {
                'theo_ngay': self.predict_theo_ngay(source_numbers),
                'theo_lo': self.predict_theo_lo(source_numbers),
                'theo_dau_cam': self.predict_theo_dau_cam(self._find_dau_duoi_cam(source_numbers)[0]),
                'theo_duoi_cam': self.predict_theo_duoi_cam(self._find_dau_duoi_cam(source_numbers)[1])
            }
            
            # Kết hợp các dự đoán
            all_numbers = []
            for method, pred in base_predictions.items():
                all_numbers.extend(pred['predicted_numbers'])
            
            # Đếm tần suất xuất hiện
            number_counts = defaultdict(int)
            for num in all_numbers:
                number_counts[num] += 1
            
            # Phân tích xu hướng chung
            trend_numbers = self._analyze_recent_trends(5)  # 5 ngày gần nhất
            
            # Tăng trọng số cho các số có xu hướng mạnh
            for num in trend_numbers:
                number_counts[num] += 2
            
            # Sắp xếp theo tần suất giảm dần
            sorted_numbers = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Thêm các số từ xu hướng thị trường
            market_trend = self.analyze_market_trend()
            market_numbers = market_trend.get('predicted_numbers', [])
            
            # Kết hợp các số từ xu hướng thị trường
            final_numbers = [num for num, _ in sorted_numbers[:6]]  # Top 6 từ tần suất
            for num in market_numbers:
                if num not in final_numbers:
                    final_numbers.append(num)
                    if len(final_numbers) >= 10:  # Giới hạn tổng số là 10
                        break
            
            return {
                'predicted_numbers': final_numbers[:8],  # Top 8 số
                'confidence': 75,  # Độ tin cậy mặc định cho phương pháp ensemble
                'base_methods': list(base_predictions.keys()),
                'method': 'ensemble'
            }
        except Exception as e:
            print(f"Lỗi khi dự đoán bằng phương pháp ensemble: {e}")
            return {
                'predicted_numbers': [],
                'confidence': 0,
                'error': str(e),
                'method': 'ensemble'
            }

    def analyze_market_trend(self):
        """
        Phân tích xu hướng thị trường
        Returns:
            Dict chứa kết quả phân tích
        """
        try:
            # Lấy dữ liệu 30 ngày gần nhất
            end_date = self.source_date
            start_date = end_date - timedelta(days=30)
            
            # Lấy tất cả kết quả xổ số trong khoảng thời gian
            results = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by('ngay')
            
            if not results:
                return {
                    'predicted_numbers': [],
                    'confidence': 0,
                    'method': 'market_trend'
                }
            
            # Tập hợp tất cả các số 2 chữ số
            all_numbers = []
            for result in results:
                numbers = self._get_all_2digit_numbers(result)
                all_numbers.extend(numbers)
            
            # Đếm tần suất xuất hiện
            number_freq = defaultdict(int)
            for num in all_numbers:
                number_freq[num] += 1
            
            # Tìm các số có tần suất cao
            high_freq_nums = []
            for num, freq in number_freq.items():
                if freq >= 3:  # Xuất hiện ít nhất 3 lần trong 30 ngày
                    high_freq_nums.append((num, freq))
            
            # Sắp xếp theo tần suất giảm dần
            high_freq_nums.sort(key=lambda x: x[1], reverse=True)
            
            # Phân tích giai đoạn "nóng" và "lạnh" của các số
            hot_numbers = []  # Các số đang trong giai đoạn nóng
            cold_numbers = []  # Các số đang trong giai đoạn lạnh
            
            # Xem xét 10 ngày gần nhất
            recent_results = results.filter(ngay__gte=end_date - timedelta(days=10))
            recent_numbers = []
            for result in recent_results:
                numbers = self._get_all_2digit_numbers(result)
                recent_numbers.extend(numbers)
            
            # Xác định các số nóng và lạnh
            for num, freq in high_freq_nums:
                if num in recent_numbers:
                    # Nếu số xuất hiện trong 10 ngày gần đây, coi là nóng
                    hot_numbers.append(num)
                else:
                    # Nếu số không xuất hiện trong 10 ngày gần đây, coi là lạnh
                    cold_numbers.append(num)
            
            # Ưu tiên dự đoán các số đang trong giai đoạn lạnh với tần suất cao
            predicted_numbers = cold_numbers[:5]  # Top 5 số lạnh
            
            # Thêm một số số nóng
            predicted_numbers.extend(hot_numbers[:3])  # Top 3 số nóng
            
            return {
                'predicted_numbers': predicted_numbers[:8],  # Giới hạn 8 số
                'confidence': 65,  # Độ tin cậy mặc định
                'hot_numbers': hot_numbers[:5],
                'cold_numbers': cold_numbers[:5],
                'method': 'market_trend'
            }
        except Exception as e:
            print(f"Lỗi khi phân tích xu hướng thị trường: {e}")
            return {
                'predicted_numbers': [],
                'confidence': 0,
                'error': str(e),
                'method': 'market_trend'
            }

    def combine_predictions_with_weights(self, predictions_dict, method_weights=None):
        """
        Kết hợp các phương pháp dự đoán với trọng số tối ưu
        Args:
            predictions_dict: Dict chứa kết quả dự đoán từ các phương pháp
            method_weights: Dict trọng số cho các phương pháp
        Returns:
            Dict chứa kết quả dự đoán kết hợp
        """
        # Nếu không có trọng số, sử dụng mặc định
        if not method_weights:
            method_weights = {
                'theo_ngay': 1.0,
                'theo_tong_db': 0.8,
                'theo_thu': 0.7,
                'theo_cap_kem': 0.9,
                'theo_lo': 1.0,
                'theo_dau_cam': 0.6,
                'theo_duoi_cam': 0.6,
                'theo_dau_duoi_cam': 0.8,
                'theo_kep': 0.7,
                'discovered_rules': 0.8,
                'ml_advanced': 0.9,
                'ensemble': 0.9,
                'market_trend': 0.7,
                'cyclical': 0.7
            }
        
        # Tính điểm cho mỗi số dự đoán
        number_scores = defaultdict(float)
        
        # Cập nhật trọng số dựa trên chu kỳ mệt mỏi
        method_cycles = getattr(self, 'method_cycles', {})
        adjusted_weights = method_weights.copy()
        
        for method, cycle_data in method_cycles.items():
            if method in adjusted_weights:
                # Giảm trọng số cho phương pháp đang trong chu kỳ mệt mỏi
                if cycle_data.get('is_tired', False):
                    factor = 1.0 - (cycle_data.get('fatigue_level', 0) / 100) * 0.5
                    adjusted_weights[method] *= max(0.5, factor)  # Giảm tối đa 50%
                
                # Tăng trọng số cho phương pháp có hiệu suất tốt gần đây
                elif cycle_data.get('recent_performance', 0) > 70:
                    performance_bonus = (cycle_data.get('recent_performance', 0) - 70) / 30
                    adjusted_weights[method] *= (1.0 + performance_bonus * 0.3)  # Tăng tối đa 30%
                
                # Điều chỉnh theo xu hướng hiệu suất
                trend = cycle_data.get('performance_trend', 'stable')
                if trend == 'up':
                    adjusted_weights[method] *= 1.1  # Tăng 10%
                elif trend == 'down':
                    adjusted_weights[method] *= 0.9  # Giảm 10%
        
        # Tính điểm cho mỗi số
        for method, pred in predictions_dict.items():
            if method == 'ket_hop':  # Bỏ qua phương pháp kết hợp
                continue
            
            weight = adjusted_weights.get(method, 0.5)
            confidence = pred.get('confidence', 50) / 100
            
            for number in pred.get('predicted_numbers', []):
                # Điểm = trọng số phương pháp * độ tin cậy
                number_scores[number] += weight * confidence
        
        # Sắp xếp theo điểm giảm dần
        sorted_numbers = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Lấy top 8 số có điểm cao nhất
        top_numbers = sorted_numbers[:8]
        
        # Đánh giá độ tin cậy tổng thể
        overall_confidence = self._calculate_combined_confidence(sorted_numbers, method_cycles)
        
        return {
            'predicted_numbers': [num for num, _ in top_numbers],
            'confidence': overall_confidence,
            'number_scores': dict(sorted_numbers[:12]),  # Top 12 số với điểm
            'method_weights': adjusted_weights,
            'method': 'ket_hop'
        }

    def _calculate_combined_confidence(self, sorted_numbers, method_cycles):
        """
        Tính độ tin cậy tổng thể cho phương pháp kết hợp
        Args:
            sorted_numbers: Danh sách số được sắp xếp theo điểm
            method_cycles: Thông tin chu kỳ của các phương pháp
        Returns:
            Độ tin cậy tổng thể
        """
        # Cơ bản: 85% độ tin cậy
        base_confidence = 85
        
        # Kiểm tra số lượng phương pháp đang mệt mỏi
        tired_methods = sum(1 for _, data in method_cycles.items() if data.get('is_tired', False))
        
        # Điều chỉnh dựa trên số lượng phương pháp mệt mỏi
        if tired_methods >= 3:
            base_confidence -= tired_methods * 2  # Giảm 2% cho mỗi phương pháp mệt mỏi
        
        # Kiểm tra sự chênh lệch điểm giữa các số top
        if len(sorted_numbers) >= 3:
            top1_score = sorted_numbers[0][1]
            top3_avg_score = sum(score for _, score in sorted_numbers[:3]) / 3
            
            # Nếu top 1 có điểm vượt trội so với trung bình top 3
            if top1_score > top3_avg_score * 1.5:
                base_confidence += 5  # Tăng 5% độ tin cậy
        
        # Giới hạn trong khoảng 60-95%
        return max(60, min(95, base_confidence))

    def calculate_overall_confidence(self, predictions_dict):
        """
        Đánh giá độ tin cậy tổng thể của các dự đoán
        Args:
            predictions_dict: Dict chứa kết quả dự đoán từ các phương pháp
        Returns:
            Dict chứa thông tin độ tin cậy tổng thể
        """
        # Tính trung bình độ tin cậy của các phương pháp
        confidences = []
        for method, pred in predictions_dict.items():
            if method != 'ket_hop' and 'confidence' in pred:
                confidences.append(pred['confidence'])
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Đếm số lượng số dự đoán trùng lặp giữa các phương pháp
        number_counts = defaultdict(int)
        for method, pred in predictions_dict.items():
            if method != 'ket_hop':
                for number in pred.get('predicted_numbers', []):
                    number_counts[number] += 1
        
        # Số lượng phương pháp
        method_count = len([m for m in predictions_dict if m != 'ket_hop'])
        
        # Tìm các số được dự đoán bởi nhiều phương pháp (> 50% phương pháp)
        strong_consensus = [num for num, count in number_counts.items() 
                          if count > method_count * 0.5]
        
        # Tính điểm tổng hợp
        consensus_score = len(strong_consensus) * 10  # 10 điểm cho mỗi số đồng thuận mạnh
        
        # Đánh giá sự đồng thuận
        if len(strong_consensus) >= 3:
            consensus_level = "Cao"
        elif len(strong_consensus) >= 1:
            consensus_level = "Trung bình"
        else:
            consensus_level = "Thấp"
        
        # Điều chỉnh độ tin cậy dựa trên sự đồng thuận
        adjusted_confidence = (avg_confidence * 0.7) + (consensus_score * 0.3)
        adjusted_confidence = min(95, adjusted_confidence)  # Giới hạn tối đa 95%
        
        return {
            'overall_confidence': adjusted_confidence,
            'average_method_confidence': avg_confidence,
            'consensus_level': consensus_level,
            'strong_consensus_numbers': strong_consensus,
            'analysis': f"Độ tin cậy tổng thể: {adjusted_confidence:.1f}%, Mức độ đồng thuận: {consensus_level}"
        }

    def _create_ml_features(self, result, numbers):
        """
        Tạo features cho mô hình học máy
        Args:
            result: Đối tượng KetQuaXoSo
            numbers: Danh sách số 2 chữ số
        Returns:
            List features
        """
        try:
            # Features cơ bản
            features = [
                result.ngay.weekday(),          # Thứ trong tuần
                result.ngay.day,                # Ngày trong tháng
                result.ngay.month,              # Tháng
                len(numbers),                   # Số lượng số 2 chữ số
            ]
            
            # Thêm thông tin về sự xuất hiện của các số từ 00-99
            for i in range(100):
                num = f"{i:02d}"
                features.append(1 if num in numbers else 0)
            
            # Thêm thông tin về tổng chữ số
            if hasattr(result, 'giai_db') and result.giai_db:
                try:
                    db_sum = sum(int(digit) for digit in result.giai_db[-2:])
                    # One-hot encoding cho tổng
                    for i in range(10):
                        features.append(1 if db_sum % 10 == i else 0)
                except (ValueError, TypeError, IndexError):
                    # Nếu không thể tính tổng, thêm 10 giá trị 0
                    features.extend([0] * 10)
            else:
                # Nếu không có giải đặc biệt, thêm 10 giá trị 0
                features.extend([0] * 10)
            
            return features
        except Exception as e:
            logger.error(f"Lỗi khi tạo features: {e}")
            # Trả về features mặc định nếu có lỗi
            default_features = [0] * 114  # 4 + 100 + 10
            return default_features

    def _find_kep_numbers(self, numbers):
        """
        Tìm các số kép trong danh sách số
        Args:
            numbers: Danh sách số 2 chữ số
        Returns:
            List các số kép
        """
        kep_numbers = []
        for num in numbers:
            if len(num) == 2 and num[0] == num[1]:  # Số kép
                kep_numbers.append(num)
        return kep_numbers

    def _analyze_recent_trends(self, days=5):
        """
        Phân tích xu hướng gần đây
        Args:
            days: Số ngày cần phân tích
        Returns:
            List các số có xu hướng mạnh
        """
        try:
            # Lấy kết quả xổ số trong số ngày gần đây
            end_date = self.source_date
            start_date = end_date - timedelta(days=days)
            
            results = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by('ngay')
            
            # Nếu không đủ dữ liệu, trả về list rỗng
            if results.count() < days // 2:
                return []
            
            # Lấy tất cả các số 2 chữ số
            all_numbers = []
            for result in results:
                numbers = self._get_all_2digit_numbers(result)
                all_numbers.extend(numbers)
            
            # Đếm tần suất
            number_counts = defaultdict(int)
            for num in all_numbers:
                number_counts[num] += 1
            
            # Lấy các số xuất hiện nhiều hơn 1 lần
            trend_numbers = [num for num, count in number_counts.items() if count > 1]
            
            return trend_numbers
        except Exception as e:
            logger.error(f"Lỗi khi phân tích xu hướng gần đây: {e}")
            return []

    def _get_historical_method_performance(self, method):
        """
        Lấy hiệu suất lịch sử của một phương pháp
        Args:
            method: Tên phương pháp
        Returns:
            Dict thông tin hiệu suất
        """
        try:
            # Lấy thống kê hiệu quả gần nhất
            stat = ThongKeHieuQua.objects.filter(
                phuong_phap=method,
                ngay_ket_thuc__lte=self.source_date
            ).order_by('-ngay_ket_thuc').first()
            
            if not stat:
                return {
                    'success_rate': 50,  # Giá trị mặc định
                    'trend': 'stable'
                }
            
            # Lấy thông tin xu hướng
            trend = stat.xu_huong if hasattr(stat, 'xu_huong') else 'stable'
            
            return {
                'success_rate': stat.ty_le_trung,
                'trend': trend
            }
        except Exception as e:
            logger.error(f"Lỗi khi lấy hiệu suất lịch sử của phương pháp {method}: {e}")
            return {
                'success_rate': 50,
                'trend': 'stable'
            }

    def _adjust_confidence_by_history(self, base_confidence, historical_performance):
        """
        Điều chỉnh độ tin cậy dựa trên hiệu suất lịch sử
        Args:
            base_confidence: Độ tin cậy cơ bản
            historical_performance: Thông tin hiệu suất lịch sử
        Returns:
            Độ tin cậy đã điều chỉnh
        """
        success_rate = historical_performance.get('success_rate', 50)
        trend = historical_performance.get('trend', 'stable')
        
        # Điều chỉnh dựa trên tỷ lệ thành công
        if success_rate > 70:
            adjustment = (success_rate - 70) * 0.5  # Tăng tối đa 15% (nếu success_rate = 100%)
        elif success_rate < 30:
            adjustment = (success_rate - 30) * 0.5  # Giảm tối đa 15% (nếu success_rate = 0%)
        else:
            adjustment = 0
        
        # Điều chỉnh thêm dựa trên xu hướng
        if trend == 'up':
            adjustment += 5  # Tăng thêm 5%
        elif trend == 'down':
            adjustment -= 5  # Giảm thêm 5%
        
        # Áp dụng điều chỉnh và giới hạn trong khoảng 0-100%
        adjusted_confidence = max(0, min(100, base_confidence + adjustment))
        
        return adjusted_confidence

    def _get_weekday_name(self, weekday):
        """
        Lấy tên thứ trong tuần
        Args:
            weekday: Số thứ tự ngày trong tuần (0-6)
        Returns:
            Tên thứ
        """
        weekday_names = {
            0: "Thứ Hai",
            1: "Thứ Ba",
            2: "Thứ Tư",
            3: "Thứ Năm",
            4: "Thứ Sáu",
            5: "Thứ Bảy",
            6: "Chủ Nhật"
        }
        return weekday_names.get(weekday, f"Ngày {weekday}")

    def _find_dau_duoi_cam(self, source_numbers):
        """
        Tìm các đầu câm và đuôi câm từ kết quả
        Args:
            source_numbers: Danh sách số 2 chữ số từ kết quả hôm trước
        Returns:
            Tuple (đầu câm, đuôi câm)
        """
        # Tạo danh sách tất cả các đầu và đuôi có thể
        all_dau = set(str(i) for i in range(10))
        all_duoi = set(str(i) for i in range(10))
        
        # Đánh dấu các đầu và đuôi đã xuất hiện
        dau_appeared = set()
        duoi_appeared = set()
        
        for num in source_numbers:
            if len(num) == 2:
                dau_appeared.add(num[0])
                duoi_appeared.add(num[1])
        
        # Đầu câm và đuôi câm là những số không xuất hiện
        dau_cam = list(all_dau - dau_appeared)
        duoi_cam = list(all_duoi - duoi_appeared)
        
        return dau_cam, duoi_cam

    def _get_xoso_result(self, date):
        """
        Lấy kết quả xổ số cho một ngày cụ thể
        Args:
            date: Ngày cần lấy kết quả
        Returns:
            Đối tượng KetQuaXoSo hoặc None nếu không tìm thấy
        """
        if date in self.db_cache:
            return self.db_cache[date]
        
        try:
            result = KetQuaXoSo.objects.get(ngay=date)
            self.db_cache[date] = result
            return result
        except KetQuaXoSo.DoesNotExist:
            return None

    def _get_all_2digit_numbers(self, result):
        """
        Lấy tất cả các số 2 chữ số từ kết quả xổ số
        Args:
            result: Đối tượng KetQuaXoSo
        Returns:
            List các số 2 chữ số
        """
        if not result:
            return []
            
        if hasattr(result, 'get_all_2digit_numbers'):
            return result.get_all_2digit_numbers()
        
        # Fallback nếu không có phương thức get_all_2digit_numbers
        numbers = []
        for field in ['giai_db', 'giai_1', 'giai_2', 'giai_3', 'giai_4', 'giai_5', 'giai_6', 'giai_7']:
            if hasattr(result, field):
                value = getattr(result, field)
                if isinstance(value, str) and len(value) >= 2:
                    numbers.append(value[-2:])
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and len(item) >= 2:
                            numbers.append(item[-2:])
        
        # Loại bỏ trùng lặp
        return list(set(numbers))

    def _get_historical_method_weights(self):
        """
        Lấy trọng số của các phương pháp dựa trên hiệu quả lịch sử
        Returns:
            Dict trọng số các phương pháp
        """
        from .models import MethodWeight, ThongKeHieuQua
        
        # Ưu tiên lấy trọng số từ model MethodWeight
        method_weights = MethodWeight.get_latest_weights()
        
        # Nếu không có trọng số nào trong MethodWeight, sử dụng logic cũ
        if not method_weights:
            method_weights = {}
            try:
                # Lấy thống kê hiệu quả gần nhất
                latest_stats = ThongKeHieuQua.objects.filter(
                    ngay_ket_thuc__lte=self.source_date
                ).order_by('-ngay_ket_thuc', 'phuong_phap').values('phuong_phap', 'ty_le_trung')
                
                for stat in latest_stats:
                    method = stat['phuong_phap']
                    hit_rate = stat['ty_le_trung'] / 100  # Chuyển về tỷ lệ 0-1
                    
                    # Chỉ cập nhật trọng số nếu có dữ liệu lịch sử
                    if hit_rate > 0:
                        # Trọng số = 0.5 + hit_rate/2 (tối đa 1.0)
                        method_weights[method] = min(1.0, 0.5 + hit_rate/2)
            except Exception as e:
                logger.error(f"Lỗi khi lấy trọng số lịch sử: {e}")
        
        return method_weights

    def _save_predictions(self, results):
        """
        Lưu kết quả dự đoán vào cơ sở dữ liệu
        Args:
            results: Dict chứa kết quả dự đoán
        """
        try:
            for method, prediction in results['predictions'].items():
                # Kiểm tra xem có dự đoán không
                if not prediction or 'predicted_numbers' not in prediction:
                    continue
                
                # Tạo đối tượng SoiCauBacNho
                soi_cau = SoiCauBacNho(
                    ngay_du_doan=self.target_date,
                    ngay_phan_tich=timezone.now().date(),
                    phuong_phap=method,
                    ket_qua_ngay_truoc=','.join(results['source_numbers']),
                    thu_trong_tuan=self.target_date.weekday(),
                    ty_le_tin_cay=prediction.get('confidence', 0)
                )
                
                # Lưu kết quả dự đoán
                soi_cau.set_ket_qua_du_doan(prediction['predicted_numbers'])
                
                # Lưu thông tin bổ sung
                if method == 'ket_hop':
                    soi_cau.ghi_chu = json.dumps({
                        'number_scores': prediction.get('number_scores', {}),
                        'method_weights': prediction.get('method_weights', {}),
                        'method_cycles': results.get('method_cycles', {})
                    }, cls=DateEncoder)
                elif method == 'ml_advanced':
                    soi_cau.ghi_chu = json.dumps({
                        'all_predictions': prediction.get('all_predictions', [])
                    }, cls=DateEncoder)
                elif method == 'discovered_rules':
                    soi_cau.ghi_chu = json.dumps({
                        'matched_rules': prediction.get('matched_rules', [])
                    }, cls=DateEncoder)
                elif method == 'cyclical':
                    # Lưu thông tin về các mẫu chu kỳ được sử dụng
                    cyclical_patterns = [
                        pattern for pattern in self.discover_cyclical_patterns()
                        if pattern['predicted_next_date'] == self.target_date.strftime('%Y-%m-%d')
                    ]
                    soi_cau.ghi_chu = json.dumps({
                        'cyclical_patterns': cyclical_patterns
                    }, cls=DateEncoder)
                elif method == 'market_trend':
                    soi_cau.ghi_chu = json.dumps({
                        'hot_numbers': prediction.get('hot_numbers', []),
                        'cold_numbers': prediction.get('cold_numbers', [])
                    }, cls=DateEncoder)
                else:
                    soi_cau.ghi_chu = json.dumps({
                        'matched_rules': prediction.get('matched_rules', [])
                    })
                
                # Lưu vào DB
                soi_cau.save()
                
                # Lưu thêm vào bảng lịch sử soi cầu mới
                self._save_to_history(soi_cau, prediction)
                
                print(f"Đã lưu dự đoán {method} cho ngày {self.target_date}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu kết quả dự đoán: {e}")

    def _save_to_history(self, soi_cau, prediction):
        """
        Lưu kết quả dự đoán vào bảng lịch sử mới
        Args:
            soi_cau: Đối tượng SoiCauBacNho
            prediction: Dict kết quả dự đoán
        """
        try:
            # Kiểm tra xem có model LichSuSoiCau không
            if not hasattr(self, 'LichSuSoiCau'):
                return
                
            # Tạo bản ghi lịch sử
            history = LichSuSoiCau(
                soi_cau=soi_cau,
                thoi_gian=timezone.now(),
                doi_tuong_id=soi_cau.id,
                loai_soi_cau=soi_cau.phuong_phap,
                ket_qua=json.dumps(prediction),
                trang_thai='chua_kiem_tra'
            )
            
            # Lưu vào DB
            history.save()
        except Exception as e:
            logger.error(f"Lỗi khi lưu vào lịch sử soi cầu: {e}")

    def analyze_method_fatigue_cycles(self):
        """
        Phân tích chu kỳ mệt mỏi của các phương pháp dự đoán
        Returns:
            Dict chứa thông tin chu kỳ mệt mỏi của các phương pháp
        """
        try:
            # Lấy thống kê hiệu quả trong 60 ngày gần nhất
            end_date = self.source_date
            start_date = end_date - timedelta(days=60)
            
            # Các phương pháp cần phân tích
            methods = [m for m, _ in SoiCauBacNho.PREDICTION_METHODS if m != 'ket_hop']
            methods.extend(['theo_dau_duoi_cam', 'theo_kep', 'ml_advanced', 'ensemble', 'market_trend'])
            
            # Kết quả phân tích
            method_cycles = {}
            
            for method in methods:
                # Lấy các dự đoán đã có kết quả thực tế
                predictions = SoiCauBacNho.objects.filter(
                    phuong_phap=method,
                    ngay_du_doan__range=(start_date, end_date),
                    ket_qua_thuc_te__isnull=False
                ).order_by('ngay_du_doan')
                
                # Nếu không đủ dữ liệu, bỏ qua
                if predictions.count() < 15:
                    method_cycles[method] = {
                        'is_tired': False,
                        'recent_performance': 0,
                        'cycle_length': 0,
                        'days_in_current_cycle': 0,
                        'fatigue_level': 0
                    }
                    continue
                
                # Phân tích kết quả theo ngày
                daily_results = []
                for pred in predictions:
                    daily_results.append({
                        'date': pred.ngay_du_doan,
                        'success': pred.ket_qua_trung,
                        'confidence': pred.ty_le_tin_cay
                    })
                
                # Phân tích chu kỳ thành công/thất bại
                current_streak = 1  # Số ngày liên tiếp cùng kết quả
                streaks = []  # Danh sách các chuỗi
                
                for i in range(1, len(daily_results)):
                    if daily_results[i]['success'] == daily_results[i-1]['success']:
                        current_streak += 1
                    else:
                        streaks.append({
                            'success': daily_results[i-1]['success'],
                            'length': current_streak,
                            'end_date': daily_results[i-1]['date']
                        })
                        current_streak = 1
                
                # Thêm chuỗi cuối cùng
                if daily_results:
                    streaks.append({
                        'success': daily_results[-1]['success'],
                        'length': current_streak,
                        'end_date': daily_results[-1]['date']
                    })
                
                # Tính độ dài chu kỳ trung bình
                success_streaks = [s['length'] for s in streaks if s['success']]
                failure_streaks = [s['length'] for s in streaks if not s['success']]
                
                avg_success_streak = sum(success_streaks) / len(success_streaks) if success_streaks else 0
                avg_failure_streak = sum(failure_streaks) / len(failure_streaks) if failure_streaks else 0
                
                # Ước tính độ dài chu kỳ
                cycle_length = round(avg_success_streak + avg_failure_streak)
                
                # Kiểm tra xem phương pháp đang ở trạng thái mệt mỏi không
                is_tired = False
                days_in_current_cycle = 0
                fatigue_level = 0
                
                if streaks:
                    latest_streak = streaks[-1]
                    days_in_current_cycle = latest_streak['length']
                    
                    # Nếu đang trong chuỗi thất bại, phương pháp đang mệt mỏi
                    if not latest_streak['success']:
                        is_tired = True
                        fatigue_level = min(100, (days_in_current_cycle / avg_failure_streak) * 100)
                    
                    # Nếu chuỗi thành công đã kéo dài quá lâu, có thể sắp mệt mỏi
                    elif latest_streak['success'] and days_in_current_cycle > avg_success_streak * 1.5:
                        is_tired = True
                        fatigue_level = min(100, (days_in_current_cycle - avg_success_streak) * 20)
                
                # Tính hiệu suất gần đây (15 ngày gần nhất)
                recent_results = daily_results[-15:] if len(daily_results) >= 15 else daily_results
                recent_success = sum(1 for r in recent_results if r['success'])
                recent_performance = (recent_success / len(recent_results)) * 100 if recent_results else 0
                
                # Phân tích xu hướng hiệu suất
                trend = "stable"
                if len(daily_results) >= 30:
                    first_half = daily_results[-30:-15]
                    second_half = daily_results[-15:]
                    
                    first_half_success = sum(1 for r in first_half if r['success'])
                    second_half_success = sum(1 for r in second_half if r['success'])
                    
                    first_half_rate = (first_half_success / len(first_half)) * 100 if first_half else 0
                    second_half_rate = (second_half_success / len(second_half)) * 100 if second_half else 0
                    
                    diff = second_half_rate - first_half_rate
                    if diff > 15:
                        trend = "up"
                    elif diff < -15:
                        trend = "down"
                
                # Lưu kết quả phân tích
                method_cycles[method] = {
                    'is_tired': is_tired,
                    'fatigue_level': fatigue_level,
                    'cycle_length': cycle_length,
                    'days_in_current_cycle': days_in_current_cycle,
                    'avg_success_streak': avg_success_streak,
                    'avg_failure_streak': avg_failure_streak,
                    'recent_performance': recent_performance,
                    'performance_trend': trend,
                    'streaks': streaks[-5:] if streaks else []  # 5 chuỗi gần nhất
                }
            
            # Phân tích tương quan giữa các phương pháp
            method_correlations = self._analyze_method_correlations(methods, start_date, end_date)
            
            # Thêm thông tin tương quan vào kết quả
            for method, data in method_cycles.items():
                if method in method_correlations:
                    data['correlations'] = method_correlations[method]
            
            return method_cycles
        except Exception as e:
            logger.error(f"Lỗi khi phân tích chu kỳ mệt mỏi: {e}")
            return {}

    def _analyze_method_correlations(self, methods, start_date, end_date):
        """
        Phân tích tương quan giữa các phương pháp dự đoán
        Args:
            methods: Danh sách các phương pháp
            start_date: Ngày bắt đầu
            end_date: Ngày kết thúc
        Returns:
            Dict chứa thông tin tương quan
        """
        try:
            import numpy as np
            from scipy.stats import pearsonr
            import warnings
            
            # Lấy tất cả các ngày có dự đoán
            dates = SoiCauBacNho.objects.filter(
                ngay_du_doan__range=(start_date, end_date),
                ket_qua_thuc_te__isnull=False
            ).values_list('ngay_du_doan', flat=True).distinct().order_by('ngay_du_doan')
            
            # Tạo ma trận kết quả
            method_results = {}
            for method in methods:
                method_results[method] = {}
                # Lấy kết quả dự đoán của phương pháp
                predictions = SoiCauBacNho.objects.filter(
                    phuong_phap=method,
                    ngay_du_doan__in=dates,
                    ket_qua_thuc_te__isnull=False
                ).values_list('ngay_du_doan', 'ket_qua_trung')
                
                # Chuyển thành dict cho dễ tra cứu
                for date, success in predictions:
                    method_results[method][date] = 1 if success else 0
            
            # Tính tương quan giữa các phương pháp
            correlations = {}
            for method1 in methods:
                correlations[method1] = {}
                for method2 in methods:
                    if method1 == method2:
                        correlations[method1][method2] = 1.0
                        continue
                    
                    # Tìm các ngày cả hai phương pháp đều có dự đoán
                    common_dates = set(method_results[method1].keys()) & set(method_results[method2].keys())
                    if len(common_dates) < 10:
                        correlations[method1][method2] = 0
                        continue
                    
                    # Tạo hai mảng kết quả
                    results1 = []
                    results2 = []
                    for date in sorted(common_dates):
                        results1.append(method_results[method1][date])
                        results2.append(method_results[method2][date])
                    
                    # Kiểm tra xem các mảng có phải là hằng số không
                    if len(set(results1)) <= 1 or len(set(results2)) <= 1:
                        # Nếu một trong hai mảng là hằng số, đặt tương quan là 0
                        correlations[method1][method2] = 0
                        continue
                    
                    # Tính hệ số tương quan
                    try:
                        # Tắt cảnh báo ConstantInputWarning
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            corr, _ = pearsonr(results1, results2)
                        correlations[method1][method2] = corr
                    except Exception as e:
                        logger.warning(f"Lỗi khi tính tương quan giữa {method1} và {method2}: {e}")
                        correlations[method1][method2] = 0
            
            # Tìm các phương pháp có tương quan âm mạnh (bổ trợ tốt cho nhau)
            complementary_methods = {}
            for method in methods:
                negative_corrs = [(other, corr) for other, corr in correlations[method].items()
                                if other != method and corr < -0.3]
                if negative_corrs:
                    complementary_methods[method] = sorted(negative_corrs, key=lambda x: x[1])
            
            # Tổng hợp kết quả
            method_correlation_info = {}
            for method in methods:
                # Tìm 2 phương pháp bổ trợ tốt nhất
                top_complements = []
                if method in complementary_methods:
                    top_complements = complementary_methods[method][:2]
                
                # Tìm 2 phương pháp cạnh tranh (tương quan dương cao)
                competing_methods = [(other, corr) for other, corr in correlations[method].items()
                                    if other != method and corr > 0.5]
                top_competing = sorted(competing_methods, key=lambda x: x[1], reverse=True)[:2]
                
                method_correlation_info[method] = {
                    'complementary': top_complements,
                    'competing': top_competing
                }
            
            return method_correlation_info
        
        except Exception as e:
            logger.error(f"Lỗi khi phân tích tương quan giữa các phương pháp: {e}")
            return {}

    def optimize_method_weights(self):
        """
        Tối ưu hóa trọng số của các phương pháp dựa trên kết quả lịch sử
        Returns:
            Dict trọng số tối ưu
        """
        try:
            from scipy.optimize import minimize
            import numpy as np
            
            # Lấy dữ liệu dự đoán trong 90 ngày gần nhất
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=90)
            
            # Lấy các ngày có đủ dự đoán từ các phương pháp chính
            dates_with_predictions = []
            
            for date in (start_date + timedelta(days=i) for i in range((end_date - start_date).days)):
                # Kiểm tra xem có dự đoán từ các phương pháp chính không
                method_count = SoiCauBacNho.objects.filter(
                    ngay_du_doan=date,
                    ket_qua_thuc_te__isnull=False,
                    phuong_phap__in=['theo_ngay', 'theo_lo', 'theo_dau_cam', 'theo_duoi_cam']
                ).count()
                
                # Nếu có ít nhất 3 phương pháp chính
                if method_count >= 3:
                    dates_with_predictions.append(date)
            
            # Nếu không đủ dữ liệu, trả về trọng số mặc định
            if len(dates_with_predictions) < 10:
                return self._get_historical_method_weights()
            
            # Chuẩn bị dữ liệu cho tối ưu hóa
            method_names = [
                'theo_ngay', 'theo_tong_db', 'theo_thu', 'theo_cap_kem',
                'theo_lo', 'theo_dau_cam', 'theo_duoi_cam', 'discovered_rules'
            ]
            
            # Thêm các phương pháp mới nếu có dữ liệu
            for method in ['theo_dau_duoi_cam', 'theo_kep', 'ml_advanced', 'ensemble', 'market_trend']:
                if SoiCauBacNho.objects.filter(phuong_phap=method).exists():
                    method_names.append(method)
            
            data = []
            
            for date in dates_with_predictions:
                date_data = {'date': date, 'methods': {}}
                
                # Lấy kết quả thực tế
                actual_result = KetQuaXoSo.objects.filter(ngay=date).first()
                if not actual_result:
                    continue
                
                actual_numbers = self._get_all_2digit_numbers(actual_result)
                if not actual_numbers:
                    continue
                
                date_data['actual'] = actual_numbers
                
                # Lấy dự đoán từ các phương pháp
                for method in method_names:
                    prediction = SoiCauBacNho.objects.filter(
                        ngay_du_doan=date,
                        phuong_phap=method
                    ).first()
                    
                    if prediction:
                        predicted_numbers = prediction.get_ket_qua_du_doan()
                        date_data['methods'][method] = predicted_numbers
                
                # Chỉ thêm ngày có dữ liệu từ ít nhất 4 phương pháp
                if len(date_data['methods']) >= 4:
                    data.append(date_data)
            
            # Nếu không đủ dữ liệu, trả về trọng số mặc định
            if len(data) < 10:
                return self._get_historical_method_weights()
            
            # Hàm mục tiêu cho tối ưu hóa: tối đa hóa số lần trúng
            def objective_function(weights):
                # Chuẩn hóa trọng số
                normalized_weights = weights / np.sum(weights)
                total_hits = 0
                
                for date_data in data:
                    # Tính điểm cho mỗi số
                    number_scores = defaultdict(float)
                    
                    for i, method in enumerate(method_names):
                        if method in date_data['methods']:
                            for number in date_data['methods'][method]:
                                number_scores[number] += normalized_weights[i]
                    
                    # Lấy top 5 số có điểm cao nhất
                    top_numbers = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)[:5]
                    top_numbers = [num for num, _ in top_numbers]
                    
                    # Kiểm tra kết quả
                    hits = [num for num in top_numbers if num in date_data['actual']]
                    if hits:
                        total_hits += 1
                
                # Mục tiêu là tối đa hóa số lần trúng, nên trả về giá trị âm
                return -total_hits
            
            # Ràng buộc: tổng trọng số = 1
            constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
            
            # Ràng buộc: các trọng số >= 0.2 và <= 1.2
            bounds = [(0.2, 1.2) for _ in method_names]
            
            # Trọng số ban đầu: điều chỉnh dựa trên hiệu suất lịch sử
            initial_weights = []
            historical_weights = self._get_historical_method_weights()
            
            for method in method_names:
                initial_weights.append(historical_weights.get(method, 0.5))
            
            # Chuẩn hóa trọng số ban đầu
            initial_weights = np.array(initial_weights) / np.sum(initial_weights)
            
            # Tối ưu hóa
            result = minimize(
                objective_function,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            # Chuẩn hóa trọng số kết quả
            optimized_weights = result.x / np.sum(result.x)
            
            # Chuyển về dict
            weight_dict = {method: float(weight) for method, weight in zip(method_names, optimized_weights)}
            
            return weight_dict
        except Exception as e:
            logger.error(f"Lỗi khi tối ưu hóa trọng số: {e}")
            return self._get_historical_method_weights()

    def discover_cyclical_patterns(self):
        """
        Phát hiện các quy luật lặp lại theo chu kỳ
        Returns:
            List các quy luật chu kỳ
        """
        try:
            # Lấy dữ liệu lịch sử 240 ngày gần nhất
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=240)
            
            # Lấy tất cả kết quả xổ số trong khoảng thời gian
            results = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by('ngay')
            
            # Tạo danh sách các cặp (ngày, số)
            days_numbers = []
            for result in results:
                numbers = self._get_all_2digit_numbers(result)
                days_numbers.append((result.ngay, numbers))
            
            # Phát hiện chu kỳ xuất hiện của mỗi số
            number_appearances = defaultdict(list)
            for date, numbers in days_numbers:
                for num in numbers:
                    number_appearances[num].append(date)
            
            # Phân tích chu kỳ
            cyclical_patterns = []
            
            for num, dates in number_appearances.items():
                if len(dates) < 3:
                    continue
                
                # Tính khoảng cách giữa các lần xuất hiện
                intervals = []
                for i in range(1, len(dates)):
                    interval = (dates[i] - dates[i-1]).days
                    intervals.append(interval)
                
                # Nếu không đủ khoảng cách, bỏ qua
                if len(intervals) < 2:
                    continue
                
                # Tính khoảng cách trung bình và độ lệch chuẩn
                avg_interval = sum(intervals) / len(intervals)
                std_interval = (sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)) ** 0.5
                
                # Kiểm tra xem có chu kỳ rõ ràng không
                has_pattern = False
                pattern_type = "irregular"
                
                # Phát hiện các chu kỳ cụ thể
                # 1. Chu kỳ ổn định (độ lệch chuẩn thấp)
                if std_interval <= avg_interval / 3 and 7 <= avg_interval <= 30:
                    has_pattern = True
                    pattern_type = "stable"
                
                # 2. Chu kỳ tuần (7 ngày)
                elif 6.5 <= avg_interval <= 7.5 and std_interval <= 1.5:
                    has_pattern = True
                    pattern_type = "weekly"
                
                # 3. Chu kỳ nửa tháng (15 ngày)
                elif 14 <= avg_interval <= 16 and std_interval <= 2:
                    has_pattern = True
                    pattern_type = "biweekly"
                
                # 4. Chu kỳ tháng (28-31 ngày)
                elif 27 <= avg_interval <= 32 and std_interval <= 3:
                    has_pattern = True
                    pattern_type = "monthly"
                
                if has_pattern:
                    # Dự đoán ngày xuất hiện tiếp theo
                    last_date = dates[-1]
                    next_date = last_date + timedelta(days=round(avg_interval))
                    
                    # Tính độ tin cậy
                    confidence = 100 - min(50, (std_interval / avg_interval) * 100)
                    
                    # Kiểm tra xem chu kỳ có ổn định không dựa trên 3 lần xuất hiện gần nhất
                    if len(intervals) >= 3:
                        recent_intervals = intervals[-3:]
                        recent_avg = sum(recent_intervals) / len(recent_intervals)
                        recent_std = (sum((x - recent_avg) ** 2 for x in recent_intervals) / len(recent_intervals)) ** 0.5
                        
                        # Nếu các khoảng gần đây ổn định hơn, tăng độ tin cậy
                        if recent_std < std_interval:
                            confidence += 10
                        else:
                            confidence -= 10
                    
                    cyclical_patterns.append({
                        'number': num,
                        'avg_interval': avg_interval,
                        'std_interval': std_interval,
                        'appearances': len(dates),
                        'pattern_type': pattern_type,
                        'last_date': last_date.strftime('%Y-%m-%d'),
                        'predicted_next_date': next_date.strftime('%Y-%m-%d'),
                        'confidence': min(95, max(50, confidence))
                    })
            
            # Sắp xếp theo độ tin cậy giảm dần
            return sorted(cyclical_patterns, key=lambda x: x['confidence'], reverse=True)
        except Exception as e:
            logger.error(f"Lỗi khi phát hiện quy luật chu kỳ: {e}")
            return []

    def update_prediction_results(self):
        """
        Cập nhật kết quả thực tế cho các dự đoán đã lưu
        Returns:
            Dict thông tin cập nhật
        """
        try:
            # Lấy tất cả các dự đoán chưa có kết quả thực tế
            pending_predictions = SoiCauBacNho.objects.filter(
                ket_qua_thuc_te__isnull=True
            )
            
            updated_count = 0
            for prediction in pending_predictions:
                # Kiểm tra xem đã có kết quả thực tế chưa
                actual_result = self._get_xoso_result(prediction.ngay_du_doan)
                if not actual_result:
                    continue
                
                # Lấy các số 2 chữ số từ kết quả thực tế
                actual_numbers = self._get_all_2digit_numbers(actual_result)
                if not actual_numbers:
                    continue
                
                # Cập nhật kết quả thực tế
                prediction.set_ket_qua_thuc_te(actual_numbers)
                
                # Kiểm tra kết quả dự đoán có trúng không
                predicted_numbers = prediction.get_ket_qua_du_doan()
                prediction.ket_qua_trung = any(num in actual_numbers for num in predicted_numbers)
                
                # Lưu cập nhật
                prediction.save()
                updated_count += 1
            
            # Cập nhật thống kê hiệu quả
            self._update_performance_statistics()
            
            return {
                'updated_count': updated_count,
                'status': 'success',
                'message': f'Đã cập nhật {updated_count} dự đoán'
            }
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật kết quả dự đoán: {e}")
            return {
                'status': 'error',
                'message': f'Lỗi: {str(e)}'
            }

    def _update_performance_statistics(self):
        """
        Cập nhật thống kê hiệu quả của các phương pháp
        """
        try:
            # Lấy ngày bắt đầu và kết thúc thống kê
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)  # Thống kê 30 ngày gần nhất
            
            # Tính hiệu quả cho từng phương pháp
            methods = set()
            for method, _ in SoiCauBacNho.PREDICTION_METHODS:
                methods.add(method)
            
            # Thêm các phương pháp mới
            methods.update(['theo_dau_duoi_cam', 'theo_kep', 'ml_advanced', 'ensemble', 'market_trend'])
            
            for method in methods:
                # Lấy các dự đoán đã có kết quả thực tế
                predictions = SoiCauBacNho.objects.filter(
                    phuong_phap=method,
                    ngay_du_doan__range=(start_date, end_date),
                    ket_qua_thuc_te__isnull=False
                )
                
                # Nếu không có dữ liệu, bỏ qua
                if not predictions.exists():
                    continue
                
                # Tính tổng số dự đoán và số lần trúng
                total_predictions = predictions.count()
                correct_predictions = predictions.filter(ket_qua_trung=True).count()
                
                # Tính tỷ lệ trúng
                hit_rate = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
                
                # Thêm chi tiết dự đoán theo ngày
                daily_stats = {}
                for pred in predictions:
                    date_str = pred.ngay_du_doan.strftime('%Y-%m-%d')
                    daily_stats[date_str] = {
                        'trung': pred.ket_qua_trung,
                        'ti_le_tin_cay': pred.ty_le_tin_cay,
                        'so_du_doan': len(pred.get_ket_qua_du_doan())
                    }
                
                # Phân tích xu hướng
                trend_direction, trend_strength = self._analyze_performance_trend(daily_stats)
                
                # Cập nhật hoặc tạo mới thống kê
                ThongKeHieuQua.objects.update_or_create(
                    phuong_phap=method,
                    ngay_bat_dau=start_date,
                    ngay_ket_thuc=end_date,
                    defaults={
                        'tong_so_du_doan': total_predictions,
                        'so_lan_trung': correct_predictions,
                        'ty_le_trung': hit_rate,
                        'xu_huong': trend_direction,
                        'do_manh_xu_huong': trend_strength,
                        'du_doan_theo_ngay': json.dumps(daily_stats)
                    }
                )
                
                print(f"Đã cập nhật thống kê hiệu quả cho phương pháp {method}")
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật thống kê hiệu quả: {e}")

    def _analyze_performance_trend(self, daily_stats):
        """
        Phân tích xu hướng hiệu quả
        Args:
            daily_stats: Dict thống kê theo ngày
        Returns:
            Tuple (direction, strength)
        """
        if not daily_stats:
            return 'stable', 0
        
        # Sắp xếp theo ngày
        sorted_days = sorted(daily_stats.keys())
        
        # Nếu không đủ dữ liệu, không tính xu hướng
        if len(sorted_days) < 10:
            return 'stable', 0
        
        # Chia thành 2 nửa: trước và sau
        mid_point = len(sorted_days) // 2
        first_half = sorted_days[:mid_point]
        second_half = sorted_days[mid_point:]
        
        # Tính tỷ lệ trúng của từng nửa
        first_half_hits = sum(1 for day in first_half if daily_stats[day]['trung'])
        second_half_hits = sum(1 for day in second_half if daily_stats[day]['trung'])
        
        first_half_rate = (first_half_hits / len(first_half)) * 100 if first_half else 0
        second_half_rate = (second_half_hits / len(second_half)) * 100 if second_half else 0
        
        # Tính chênh lệch
        diff = second_half_rate - first_half_rate
        
        # Xác định xu hướng
        if diff > 10:
            direction = 'up'
            strength = min(1.0, diff / 30)  # Chuẩn hóa về 0-1
        elif diff < -10:
            direction = 'down'
            strength = min(1.0, abs(diff) / 30)
        else:
            direction = 'stable'
            strength = 0
        
        return direction, strength

    def discover_new_patterns(self):
        """
        Phát hiện các quy luật mới từ dữ liệu lịch sử
        Returns:
            Dict chứa các quy luật mới phát hiện
        """
        try:
            # Lấy dữ liệu lịch sử 120 ngày gần nhất
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=120)
            
            # Lấy tất cả kết quả xổ số trong khoảng thời gian
            results = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by('ngay')
            
            # Nếu không đủ dữ liệu, không phát hiện quy luật mới
            if results.count() < 30:
                return {
                    'status': 'error',
                    'message': 'Không đủ dữ liệu lịch sử để phát hiện quy luật mới'
                }
            
            # Phát hiện quy luật theo ngày
            ngay_patterns = self._discover_day_patterns(results)
            
            # Phát hiện quy luật theo thứ
            thu_patterns = self._discover_weekday_patterns(results)
            
            # Phát hiện quy luật theo lô
            lo_patterns = self._discover_lo_patterns(results)
            
            # Phát hiện quy luật theo kép
            kep_patterns = self._discover_kep_patterns(results)
            
            # Phát hiện quy luật theo đầu đuôi câm
            cam_patterns = self._discover_cam_patterns(results)
            
            # Lưu các quy luật mới vào cơ sở dữ liệu
            self._save_discovered_patterns(ngay_patterns, thu_patterns, lo_patterns, kep_patterns, cam_patterns)
            
            return {
                'status': 'success',
                'ngay_patterns': ngay_patterns,
                'thu_patterns': thu_patterns,
                'lo_patterns': lo_patterns,
                'kep_patterns': kep_patterns,
                'cam_patterns': cam_patterns,
                'message': f'Đã phát hiện {len(ngay_patterns) + len(thu_patterns) + len(lo_patterns) + len(kep_patterns) + len(cam_patterns)} quy luật mới'
            }
        except Exception as e:
            logger.error(f"Lỗi khi phát hiện quy luật mới: {e}")
            return {
                'status': 'error',
                'message': f'Lỗi: {str(e)}'
            }

    def _discover_day_patterns(self, results):
        """
        Phát hiện quy luật theo ngày
        Args:
            results: QuerySet kết quả xổ số
        Returns:
            List các quy luật mới
        """
        patterns = []
        
        # Tạo danh sách các cặp (ngày, số)
        days_numbers = []
        for result in results:
            numbers = self._get_all_2digit_numbers(result)
            days_numbers.append((result.ngay, numbers))
        
        # Tìm các mối liên hệ giữa ngày kề nhau
        for i in range(len(days_numbers) - 1):
            day1, numbers1 = days_numbers[i]
            day2, numbers2 = days_numbers[i + 1]
            
            # Kiểm tra xem ngày 2 có liền kề ngày 1 không
            if (day2 - day1).days != 1:
                continue
            
            # Tìm các mối liên hệ
            for num1 in numbers1:
                for num2 in numbers2:
                    # Một số quy luật có thể tìm thấy
                    # 1. Đảo số: 12 -> 21
                    if num1[0] == num2[1] and num1[1] == num2[0]:
                        patterns.append({
                            'condition': [num1],
                            'result': [num2],
                            'type': 'dao_so',
                            'count': 1
                        })
                    
                    # 2. Tăng/giảm 1 đơn vị ở mỗi chữ số
                    try:
                        if int(num2[0]) == (int(num1[0]) + 1) % 10 and int(num2[1]) == (int(num1[1]) + 1) % 10:
                            patterns.append({
                                'condition': [num1],
                                'result': [num2],
                                'type': 'tang_1',
                                'count': 1
                            })
                    except ValueError:
                        pass
        
        # Tìm các mẫu phức tạp hơn giữa các cặp số
        for i in range(len(days_numbers) - 1):
            day1, numbers1 = days_numbers[i]
            day2, numbers2 = days_numbers[i + 1]
            
            # Kiểm tra xem ngày 2 có liền kề ngày 1 không
            if (day2 - day1).days != 1:
                continue
            
            # Tìm các cặp số
            for num1 in numbers1:
                if num1[0] == num1[1]:  # Số kép
                    for num2 in numbers2:
                        patterns.append({
                            'condition': [num1],
                            'result': [num2],
                            'type': 'kep_to_number',
                            'count': 1
                        })
            
            # Tìm các cặp số đặc biệt
            special_pairs = [
                ('01', '10'), ('02', '20'), ('03', '30'), ('13', '31'),
                ('24', '42'), ('37', '73'), ('48', '84'), ('56', '65'),
                ('69', '96'), ('78', '87'), ('89', '98')
            ]
            
            for pair in special_pairs:
                num1, num2 = pair
                if num1 in numbers1 and num2 in numbers2:
                    patterns.append({
                        'condition': [num1],
                        'result': [num2],
                        'type': 'special_pair',
                        'count': 1
                    })
        
        # Gộp các mẫu giống nhau và đếm tần suất
        merged_patterns = defaultdict(int)
        for pattern in patterns:
            key = f"{pattern['type']}_{','.join(pattern['condition'])}_{','.join(pattern['result'])}"
            merged_patterns[key] += 1
        
        # Chuyển về format cuối cùng và chỉ giữ các mẫu xuất hiện ít nhất 2 lần
        final_patterns = []
        for key, count in merged_patterns.items():
            if count >= 2:
                # Phân tích key để lấy lại thông tin
                parts = key.split('_')
                pattern_type = parts[0]
                
                # Xử lý trường hợp đặc biệt
                if len(parts) >= 3:
                    condition_result = '_'.join(parts[1:]).split('_')
                    if len(condition_result) >= 2:
                        condition = condition_result[0].split(',')
                        result = condition_result[1].split(',')
                        
                        final_patterns.append({
                            'condition': condition,
                            'result': result,
                            'type': pattern_type,
                            'count': count
                        })
        
        # Sắp xếp theo số lần xuất hiện giảm dần
        return sorted(final_patterns, key=lambda x: x['count'], reverse=True)

    def _discover_weekday_patterns(self, results):
        """
        Phát hiện quy luật theo thứ trong tuần
        Args:
            results: QuerySet kết quả xổ số
        Returns:
            List các quy luật mới
        """
        # Thống kê số lượng xuất hiện theo thứ
        weekday_numbers = defaultdict(lambda: defaultdict(int))
        
        for result in results:
            weekday = result.ngay.weekday()
            numbers = self._get_all_2digit_numbers(result)
            
            for num in numbers:
                weekday_numbers[weekday][num] += 1
        
        # Tìm các số xuất hiện nhiều nhất cho mỗi thứ
        patterns = []
        
        for weekday, counts in weekday_numbers.items():
            # Sắp xếp theo số lần xuất hiện giảm dần
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            
            # Đếm tổng số ngày cho mỗi thứ
            total_days = sum(1 for result in results if result.ngay.weekday() == weekday)
            
            # Chỉ lấy các số xuất hiện ít nhất 2 lần
            for num, count in sorted_counts:
                if count >= 2:
                    patterns.append({
                        'weekday': weekday,
                        'number': num,
                        'count': count,
                        'total_days': total_days
                    })
        
        # Tính tỷ lệ xuất hiện và lọc các mẫu có tỷ lệ cao
        final_patterns = []
        
        for pattern in patterns:
            # Tỷ lệ = số lần xuất hiện / tổng số ngày của thứ đó
            rate = pattern['count'] / pattern['total_days'] if pattern['total_days'] > 0 else 0
            
            # Chỉ giữ các mẫu có tỷ lệ xuất hiện cao (>= 30%)
            if rate >= 0.3:
                final_patterns.append({
                    'weekday': pattern['weekday'],
                    'number': pattern['number'],
                    'count': pattern['count'],
                    'rate': rate * 100  # Chuyển về phần trăm
                })
        
        # Sắp xếp theo tỷ lệ giảm dần
        return sorted(final_patterns, key=lambda x: x['rate'], reverse=True)

    def _discover_lo_patterns(self, results):
        """
        Phát hiện quy luật theo lô
        Args:
            results: QuerySet kết quả xổ số
        Returns:
            List các quy luật mới
        """
        patterns = []
        
        # Tạo danh sách các cặp (ngày, số)
        days_numbers = []
        for result in results:
            numbers = self._get_all_2digit_numbers(result)
            days_numbers.append((result.ngay, numbers))
        
        # Tìm các mối liên hệ giữa ngày kề nhau
        for i in range(len(days_numbers) - 1):
            day1, numbers1 = days_numbers[i]
            day2, numbers2 = days_numbers[i + 1]
            
            # Kiểm tra xem ngày 2 có liền kề ngày 1 không
            if (day2 - day1).days != 1:
                continue
            
            # Tìm các số xuất hiện ở cả hai ngày liên tiếp
            common_numbers = set(numbers1).intersection(set(numbers2))
            
            for num in common_numbers:
                patterns.append({
                    'number': num,
                    'from_date': day1,
                    'to_date': day2,
                    'type': 'lap_lai'
                })
            
            # Tìm các số có mối liên hệ đặc biệt
            for num1 in numbers1:
                # Kiểm tra nếu số ngược xuất hiện ngày hôm sau
                num1_rev = num1[1] + num1[0]
                if num1_rev in numbers2:
                    patterns.append({
                        'number': num1,
                        'result': num1_rev,
                        'from_date': day1,
                        'to_date': day2,
                        'type': 'dao_nguoc'
                    })
        
        # Gộp các mẫu giống nhau và đếm tần suất
        merged_patterns = defaultdict(int)
        
        for pattern in patterns:
            if pattern['type'] == 'lap_lai':
                key = f"{pattern['type']}_{pattern['number']}"
                merged_patterns[key] += 1
            elif pattern['type'] == 'dao_nguoc':
                key = f"{pattern['type']}_{pattern['number']}_{pattern['result']}"
                merged_patterns[key] += 1
        
        # Chuyển về format cuối cùng và chỉ giữ các mẫu xuất hiện ít nhất 2 lần
        final_patterns = []
        
        for key, count in merged_patterns.items():
            if count >= 2:
                # Phân tích key để lấy lại thông tin
                parts = key.split('_')
                pattern_type = parts[0]
                
                if pattern_type == 'lap_lai':
                    number = parts[1]
                    final_patterns.append({
                        'number': number,
                        'type': pattern_type,
                        'count': count
                    })
                elif pattern_type == 'dao_nguoc':
                    number = parts[1]
                    result = parts[2]
                    final_patterns.append({
                        'number': number,
                        'result': result,
                        'type': pattern_type,
                        'count': count
                    })
        
        # Sắp xếp theo số lần xuất hiện giảm dần
        return sorted(final_patterns, key=lambda x: x['count'], reverse=True)

    def _discover_kep_patterns(self, results):
        """
        Phát hiện quy luật theo kép
        Args:
            results: QuerySet kết quả xổ số
        Returns:
            List các quy luật mới
        """
        patterns = []
        
        # Tạo danh sách các cặp (ngày, số)
        days_numbers = []
        for result in results:
            numbers = self._get_all_2digit_numbers(result)
            days_numbers.append((result.ngay, numbers, self._find_kep_numbers(numbers)))
        
        # Tìm các mối liên hệ giữa ngày kề nhau
        for i in range(len(days_numbers) - 1):
            day1, numbers1, kep1 = days_numbers[i]
            day2, numbers2, kep2 = days_numbers[i + 1]
            
            # Kiểm tra xem ngày 2 có liền kề ngày 1 không
            if (day2 - day1).days != 1:
                continue
            
            # Trường hợp 1: Không có kép hôm nay
            if not kep1:
                patterns.append({
                    'condition': 'no_kep',
                    'numbers': numbers2,
                    'from_date': day1,
                    'to_date': day2,
                    'type': 'no_kep'
                })
            
            # Trường hợp 2: Có 3 kép trở lên hôm nay
            elif len(kep1) >= 3:
                patterns.append({
                    'condition': '3_kep',
                    'numbers': numbers2,
                    'kep_count': len(kep1),
                    'from_date': day1,
                    'to_date': day2,
                    'type': '3_kep'
                })
            
            # Trường hợp 3: Các trường hợp kép cụ thể
            else:
                for kep in kep1:
                    patterns.append({
                        'condition': kep,
                        'numbers': numbers2,
                        'from_date': day1,
                        'to_date': day2,
                        'type': 'kep_specific'
                    })
        
        # Phân tích các mẫu để tìm quy luật
        kep_rules = defaultdict(list)
        
        for pattern in patterns:
            if pattern['type'] == 'no_kep':
                for num in pattern['numbers']:
                    kep_rules['no_kep'].append(num)
            elif pattern['type'] == '3_kep':
                for num in pattern['numbers']:
                    kep_rules['3_kep'].append(num)
            elif pattern['type'] == 'kep_specific':
                for num in pattern['numbers']:
                    kep_rules[pattern['condition']].append(num)
        
        # Tìm các số xuất hiện nhiều nhất sau mỗi điều kiện kép
        final_patterns = []
        
        for condition, numbers in kep_rules.items():
            # Đếm tần suất xuất hiện
            counter = defaultdict(int)
            for num in numbers:
                counter[num] += 1
            
            # Lấy các số xuất hiện nhiều nhất
            if counter:
                sorted_counts = sorted(counter.items(), key=lambda x: x[1], reverse=True)
                top_numbers = [num for num, count in sorted_counts[:3] if count >= 2]
                
                if top_numbers:
                    final_patterns.append({
                        'condition': condition,
                        'result': top_numbers,
                        'count': sum(counter[num] for num in top_numbers),
                        'type': 'kep_rule'
                    })
        
        # Sắp xếp theo số lần xuất hiện giảm dần
        return sorted(final_patterns, key=lambda x: x['count'], reverse=True)

    def _discover_cam_patterns(self, results):
        """
        Phát hiện quy luật theo đầu đuôi câm
        Args:
            results: QuerySet kết quả xổ số
        Returns:
            List các quy luật mới
        """
        patterns = []
        
        # Tạo danh sách các cặp (ngày, số)
        days_numbers = []
        for result in results:
            numbers = self._get_all_2digit_numbers(result)
            dau_cam, duoi_cam = self._find_dau_duoi_cam(numbers)
            days_numbers.append((result.ngay, numbers, dau_cam, duoi_cam))
        
        # Tìm các mối liên hệ giữa ngày kề nhau
        for i in range(len(days_numbers) - 1):
            day1, numbers1, dau_cam1, duoi_cam1 = days_numbers[i]
            day2, numbers2, _, _ = days_numbers[i + 1]
            
            # Kiểm tra xem ngày 2 có liền kề ngày 1 không
            if (day2 - day1).days != 1:
                continue
            
            # Phân tích theo số lượng đầu câm
            if len(dau_cam1) == 1:
                patterns.append({
                    'condition': f"dau_cam_1_{dau_cam1[0]}",
                    'numbers': numbers2,
                    'from_date': day1,
                    'to_date': day2,
                    'type': 'dau_cam'
                })
            elif len(dau_cam1) == 2:
                patterns.append({
                    'condition': f"dau_cam_2_{','.join(sorted(dau_cam1))}",
                    'numbers': numbers2,
                    'from_date': day1,
                    'to_date': day2,
                    'type': 'dau_cam'
                })
            elif len(dau_cam1) == 3:
                patterns.append({
                    'condition': f"dau_cam_3_{','.join(sorted(dau_cam1))}",
                    'numbers': numbers2,
                    'from_date': day1,
                    'to_date': day2,
                    'type': 'dau_cam'
                })
            
            # Phân tích theo số lượng đuôi câm
            if len(duoi_cam1) == 1:
                patterns.append({
                    'condition': f"duoi_cam_1_{duoi_cam1[0]}",
                    'numbers': numbers2,
                    'from_date': day1,
                    'to_date': day2,
                    'type': 'duoi_cam'
                })
            elif len(duoi_cam1) == 2:
                patterns.append({
                    'condition': f"duoi_cam_2_{','.join(sorted(duoi_cam1))}",
                    'numbers': numbers2,
                    'from_date': day1,
                    'to_date': day2,
                    'type': 'duoi_cam'
                })
            elif len(duoi_cam1) == 3:
                patterns.append({
                    'condition': f"duoi_cam_3_{','.join(sorted(duoi_cam1))}",
                    'numbers': numbers2,
                    'from_date': day1,
                    'to_date': day2,
                    'type': 'duoi_cam'
                })
            
            # Trường hợp đặc biệt: Đầu 3 câm và đuôi 7 câm
            if '3' in dau_cam1 and '7' in duoi_cam1:
                patterns.append({
                    'condition': "dau_3_duoi_7",
                    'numbers': numbers2,
                    'from_date': day1,
                    'to_date': day2,
                    'type': 'dau_duoi_cam'
                })
        
        # Phân tích các mẫu để tìm quy luật
        cam_rules = defaultdict(list)
        
        for pattern in patterns:
            for num in pattern['numbers']:
                cam_rules[pattern['condition']].append(num)
        
        # Tìm các số xuất hiện nhiều nhất sau mỗi điều kiện câm
        final_patterns = []
        
        for condition, numbers in cam_rules.items():
            # Đếm tần suất xuất hiện
            counter = defaultdict(int)
            for num in numbers:
                counter[num] += 1
            
            # Lấy các số xuất hiện nhiều nhất
            if counter:
                sorted_counts = sorted(counter.items(), key=lambda x: x[1], reverse=True)
                top_numbers = [num for num, count in sorted_counts[:3] if count >= 2]
                
                if top_numbers:
                    final_patterns.append({
                        'condition': condition,
                        'result': top_numbers,
                        'count': sum(counter[num] for num in top_numbers),
                        'type': 'cam_rule'
                    })
        
        # Sắp xếp theo số lần xuất hiện giảm dần
        return sorted(final_patterns, key=lambda x: x['count'], reverse=True)

    def _save_discovered_patterns(self, ngay_patterns, thu_patterns, lo_patterns, kep_patterns, cam_patterns):
        """
        Lưu các quy luật mới phát hiện vào cơ sở dữ liệu
        Args:
            ngay_patterns: List quy luật theo ngày
            thu_patterns: List quy luật theo thứ
            lo_patterns: List quy luật theo lô
            kep_patterns: List quy luật theo kép
            cam_patterns: List quy luật theo đầu đuôi câm
        """
        try:
            # Lưu quy luật theo ngày
            for pattern in ngay_patterns:
                QuyLuatBacNho.objects.update_or_create(
                    loai_quy_luat='theo_ngay',
                    mo_ta=f"Nếu hôm nay có {', '.join(pattern['condition'])} thì ngày mai sẽ có {', '.join(pattern['result'])}",
                    dieu_kien=json.dumps(pattern['condition']),
                    ket_qua=json.dumps(pattern['result']),
                    defaults={
                        'so_lan_ap_dung': pattern['count'],
                        'ty_le_trung': 0,  # Sẽ cập nhật khi đánh giá hiệu quả
                        'he_so_tin_cay': 50
                    }
                )
            
            # Lưu quy luật theo thứ
            weekday_names = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']
            for pattern in thu_patterns:
                QuyLuatBacNho.objects.update_or_create(
                    loai_quy_luat='theo_thu',
                    mo_ta=f"{weekday_names[pattern['weekday']]} thường ra số {pattern['number']} ({pattern['rate']:.1f}%)",
                    dieu_kien=json.dumps({'weekday': pattern['weekday']}),
                    ket_qua=json.dumps([pattern['number']]),
                    defaults={
                        'so_lan_ap_dung': pattern['count'],
                        'ty_le_trung': pattern['rate'],
                        'he_so_tin_cay': min(100, pattern['rate'] + 20)  # Tăng 20% để đảm bảo có hệ số tin cậy hợp lý
                    }
                )
            
            # Lưu quy luật theo lô
            for pattern in lo_patterns:
                if pattern['type'] == 'lap_lai':
                    QuyLuatBacNho.objects.update_or_create(
                        loai_quy_luat='theo_lo',
                        mo_ta=f"Nếu hôm nay có {pattern['number']} thì ngày mai sẽ có {pattern['number']} (lặp lại)",
                        dieu_kien=json.dumps([pattern['number']]),
                        ket_qua=json.dumps([pattern['number']]),
                        defaults={
                            'so_lan_ap_dung': pattern['count'],
                            'ty_le_trung': 0,  # Sẽ cập nhật khi đánh giá hiệu quả
                            'he_so_tin_cay': 60
                        }
                    )
                elif pattern['type'] == 'dao_nguoc':
                    QuyLuatBacNho.objects.update_or_create(
                        loai_quy_luat='theo_lo',
                        mo_ta=f"Nếu hôm nay có {pattern['number']} thì ngày mai sẽ có {pattern['result']} (đảo ngược)",
                        dieu_kien=json.dumps([pattern['number']]),
                        ket_qua=json.dumps([pattern['result']]),
                        defaults={
                            'so_lan_ap_dung': pattern['count'],
                            'ty_le_trung': 0,
                            'he_so_tin_cay': 55
                        }
                    )
            
            # Lưu quy luật theo kép
            for pattern in kep_patterns:
                condition = pattern['condition']
                mo_ta = ""
                
                if condition == 'no_kep':
                    mo_ta = f"Nếu hôm nay không có số kép nào, thì ngày mai sẽ có {', '.join(pattern['result'])}"
                elif condition == '3_kep':
                    mo_ta = f"Nếu hôm nay có 3 kép trở lên, thì ngày mai sẽ có {', '.join(pattern['result'])}"
                else:
                    mo_ta = f"Nếu hôm nay có kép {condition}, thì ngày mai sẽ có {', '.join(pattern['result'])}"
                
                QuyLuatBacNho.objects.update_or_create(
                    loai_quy_luat='theo_kep',
                    mo_ta=mo_ta,
                    dieu_kien=json.dumps(condition),
                    ket_qua=json.dumps(pattern['result']),
                    defaults={
                        'so_lan_ap_dung': pattern['count'],
                        'ty_le_trung': 0,
                        'he_so_tin_cay': 55
                    }
                )
            
            # Lưu quy luật theo đầu đuôi câm
            for pattern in cam_patterns:
                condition = pattern['condition']
                mo_ta = ""
                
                if condition.startswith('dau_cam_'):
                    parts = condition.split('_')
                    if len(parts) >= 3:
                        so_luong = parts[2]
                        dau_cam = parts[3] if len(parts) > 3 else ""
                        mo_ta = f"Nếu hôm nay có {so_luong} đầu câm {dau_cam}, thì ngày mai sẽ có {', '.join(pattern['result'])}"
                elif condition.startswith('duoi_cam_'):
                    parts = condition.split('_')
                    if len(parts) >= 3:
                        so_luong = parts[2]
                        duoi_cam = parts[3] if len(parts) > 3 else ""
                        mo_ta = f"Nếu hôm nay có {so_luong} đuôi câm {duoi_cam}, thì ngày mai sẽ có {', '.join(pattern['result'])}"
                elif condition == 'dau_3_duoi_7':
                    mo_ta = f"Nếu hôm nay có đầu 3 câm và đuôi 7 câm, thì ngày mai sẽ có {', '.join(pattern['result'])}"
                
                QuyLuatBacNho.objects.update_or_create(
                    loai_quy_luat='theo_dau_duoi_cam',
                    mo_ta=mo_ta,
                    dieu_kien=json.dumps(condition),
                    ket_qua=json.dumps(pattern['result']),
                    defaults={
                        'so_lan_ap_dung': pattern['count'],
                        'ty_le_trung': 0,
                        'he_so_tin_cay': 55
                    }
                )
            
            logger.info(f"Đã lưu {len(ngay_patterns) + len(thu_patterns) + len(lo_patterns) + len(kep_patterns) + len(cam_patterns)} quy luật mới")
        except Exception as e:
            logger.error(f"Lỗi khi lưu quy luật mới: {e}")