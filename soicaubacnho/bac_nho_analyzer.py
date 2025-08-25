# bac_nho_analyzer.py
from datetime import datetime, timedelta, date
import json
from collections import defaultdict
import numpy as np
from django.utils import timezone
from django.db.models import Avg, Sum, Count, F, Q
import logging

from results.models import KetQuaXoSo
from .models import SoiCauBacNho, ThongKeHieuQua, QuyLuatBacNho

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)
    
class BacNhoAnalyzer:
    """Lớp phân tích và dự đoán theo phương pháp Bạc Nhớ"""
    
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
        
        # Danh sách quy tắc soi cầu theo ngày
        self.ngay_rules = [
            # Format: (điều kiện (list cặp số), kết quả (list cặp số))
            (['01', '10'], ['06', '60', '89', '98']),
            (['24', '42'], ['27', '72']),
            (['87', '78'], ['48', '84']),
            (['48', '84'], ['46', '64', '05', '50']),
            (['36', '63'], ['38', '83']),
            (['38', '83'], ['67', '76']),
            (['99'], ['99']),
            (['68'], ['86']),
            (['17'], ['85']),
            (['05', '50'], ['26', '62']),
            (['69', '96'], ['71']),
            (['57', '75'], ['85', '58']),
            (['41', '14'], ['16', '61', '18', '81']),
            (['45', '54'], ['56', '65']),
            (['47', '74'], ['79', '97']),
            (['79', '97'], ['37', '73']),
            (['23', '32'], ['34', '43']),
        ]
        
        # Quy tắc soi cầu theo tổng giải đặc biệt
        self.tong_db_rules = {
            0: 1, 1: 7, 2: 9, 3: 0, 4: 3, 5: 4, 6: 8, 7: 2, 8: 7, 9: 5
        }
        
        # Quy tắc soi cầu theo thứ trong tuần
        self.thu_rules = {
            # Format: {thứ: [số thường về]}
            (3, 5): ['97'],  # Thứ 5 và thứ 7
            (5, 6): ['89', '98'],  # Thứ 7 và CN
            (3, 6): ['56'],  # Thứ 5 và CN
            (5, 6, 0, 1): ['33'],  # Thứ 7, CN, T2, T3
            (2, 3, 4): ['66'],  # Thứ 4, T5, T6
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
            '68': '86', '86': '68',
            '58': '63',
            '22': '00',
            '76': '47',
            '94': '34',
            '29': '24',
            '06': '63',
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
        
        # Quy tắc đuôi câm (có vẻ có lỗi trong quy tắc gốc, tôi giả định mỗi đuôi câm khác nhau)
        self.duoi_cam_rules = {
            # Format: {đuôi câm: [số thường về ngày mai]}
            '0': ['00', '20', '80'],
            '1': ['21', '41'],
            '2': ['22', '52', '82'],
            '3': ['73', '83'],
            '4': ['64', '84'],
            '5': ['55', '85', '95'],
            '6': ['06', '16', '56'],
            '7': ['17', '47', '67'],
            '8': ['08', '18', '88'],
            '9': ['29', '39', '59', '99'],
        }
    
    def analyze_and_predict(self):
        """
        Phân tích dữ liệu và dự đoán kết quả cho ngày target_date
        
        Returns:
            Dict chứa kết quả dự đoán từ tất cả các phương pháp
        """
        # Lấy kết quả xổ số gần nhất (ngày hôm qua)
        source_result = self._get_xoso_result(self.source_date)
        if not source_result:
            logger.warning(f"Không tìm thấy kết quả xổ số cho ngày {self.source_date}")
            return {'error': f'Không có dữ liệu cho ngày {self.source_date}'}
        
        # Lấy tất cả số 2 chữ số từ kết quả gần nhất
        source_numbers = self._get_all_2digit_numbers(source_result)
        if not source_numbers:
            logger.warning(f"Không tìm thấy số 2 chữ số trong kết quả ngày {self.source_date}")
            return {'error': f'Không thể xác định số 2 chữ số từ kết quả ngày {self.source_date}'}
        
        # Tính toán dự đoán theo tất cả các phương pháp
        results = {
            'target_date': self.target_date,
            'source_date': self.source_date,
            'source_numbers': source_numbers,
            'predictions': {}
        }
        
        # 1. Dự đoán theo ngày
        theo_ngay_result = self.predict_theo_ngay(source_numbers)
        results['predictions']['theo_ngay'] = theo_ngay_result
        
        # 2. Dự đoán theo tổng giải đặc biệt
        db_number = source_result.giai_db[-2:] if hasattr(source_result, 'giai_db') else None
        if db_number:
            theo_tong_db_result = self.predict_theo_tong_db(db_number)
            results['predictions']['theo_tong_db'] = theo_tong_db_result
        
        # 3. Dự đoán theo thứ
        weekday = self.target_date.weekday()
        theo_thu_result = self.predict_theo_thu(weekday)
        results['predictions']['theo_thu'] = theo_thu_result
        
        # 4. Dự đoán theo cặp số đi kèm
        theo_cap_kem_result = self.predict_theo_cap_kem(source_numbers)
        results['predictions']['theo_cap_kem'] = theo_cap_kem_result
        
        # 5. Dự đoán theo lô
        theo_lo_result = self.predict_theo_lo(source_numbers)
        results['predictions']['theo_lo'] = theo_lo_result
        
        # 6. Dự đoán theo đầu câm và đuôi câm
        dau_cam_list, duoi_cam_list = self._find_dau_duoi_cam(source_numbers)
        
        theo_dau_cam_result = self.predict_theo_dau_cam(dau_cam_list)
        results['predictions']['theo_dau_cam'] = theo_dau_cam_result
        
        theo_duoi_cam_result = self.predict_theo_duoi_cam(duoi_cam_list)
        results['predictions']['theo_duoi_cam'] = theo_duoi_cam_result
        
        # 7. Tích hợp các phương pháp bổ sung
        
        # 7.1. Dự đoán với quy luật đã phát hiện
        discovered_rules_result = self.predict_with_discovered_rules(source_numbers)
        results['predictions']['discovered_rules'] = discovered_rules_result
        
        # 7.2. Dự đoán với mô hình học máy
        ml_result = self.predict_with_machine_learning(source_numbers)
        results['predictions']['machine_learning'] = ml_result
        
        # 7.3. Phát hiện và sử dụng quy luật chu kỳ
        cyclical_patterns = self.discover_cyclical_patterns()
        # Lọc các mẫu chu kỳ dự đoán cho ngày target_date
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
        
        # 7.4. Phân tích chu kỳ mệt mỏi để điều chỉnh trọng số
        method_cycles = self.analyze_method_fatigue_cycles()
        results['method_cycles'] = method_cycles
        
        # 7.5. Tối ưu hóa trọng số
        optimized_weights = None
        try:
            optimized_weights = self.optimize_method_weights()
        except Exception as e:
            logger.error(f"Lỗi khi tối ưu hóa trọng số: {e}")
            optimized_weights = self._get_historical_method_weights()
        
        # 8. Kết hợp tất cả các phương pháp với trọng số tối ưu
        combined_result = self.combine_predictions_with_weights(results['predictions'], optimized_weights)
        results['predictions']['ket_hop'] = combined_result
        
        # 9. Lưu kết quả phân tích và dự đoán
        self._save_predictions(results)
        
        return results
    
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

    def analyze_method_fatigue_cycles(self):
        """
        Phân tích chu kỳ mệt mỏi của các phương pháp dự đoán
        Các phương pháp thường có chu kỳ hiệu quả cao và thấp xen kẽ
        Returns:
            Dict chứa thông tin chu kỳ mệt mỏi của các phương pháp
        """
        try:
            # Lấy thống kê hiệu quả trong 45 ngày gần nhất
            end_date = self.source_date
            start_date = end_date - timedelta(days=45)
            
            # Các phương pháp cần phân tích
            methods = [m for m, _ in SoiCauBacNho.PREDICTION_METHODS if m != 'ket_hop']
            
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
                if predictions.count() < 10:
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
                
                # Tính hiệu suất gần đây (10 ngày gần nhất)
                recent_results = daily_results[-10:] if len(daily_results) >= 10 else daily_results
                recent_success = sum(1 for r in recent_results if r['success'])
                recent_performance = (recent_success / len(recent_results)) * 100 if recent_results else 0
                
                # Phân tích xu hướng hiệu suất
                trend = "stable"
                if len(daily_results) >= 20:
                    first_half = daily_results[-20:-10]
                    second_half = daily_results[-10:]
                    
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
                    
                    # Tính hệ số tương quan
                    try:
                        # Kiểm tra nếu tất cả giá trị trong mảng đều giống nhau
                        if len(set(results1)) == 1 or len(set(results2)) == 1:
                            correlations[method1][method2] = 0  # Gán giá trị mặc định nếu một trong hai mảng là hằng số
                        else:
                            corr, _ = pearsonr(results1, results2)
                            correlations[method1][method2] = corr
                    except Exception as e:
                        logger.warning(f"Lỗi khi tính hệ số tương quan: {e}")
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
        
        # Đánh giá độ tin cậy
        confidence = min(100, len(matched_rules) * 20)  # 20% cho mỗi quy tắc khớp, tối đa 100%
        
        return {
            'predicted_numbers': [num for num, _ in sorted_predictions[:10]],  # Top 10 số
            'confidence': confidence,
            'matched_rules': matched_rules,
            'method': 'theo_ngay'
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
                'discovered_rules': 0.8,
                'machine_learning': 0.9,
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
                    adjusted_weights[method] *= 0.7  # Giảm 30%
                
                # Tăng trọng số cho phương pháp có hiệu suất tốt gần đây
                elif cycle_data.get('recent_performance', 0) > 70:
                    adjusted_weights[method] *= 1.2  # Tăng 20%
        
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
        
        # Lấy top 5 số có điểm cao nhất
        top_numbers = sorted_numbers[:8]
        
        return {
            'predicted_numbers': [num for num, _ in top_numbers],
            'confidence': 85,  # Độ tin cậy của phương pháp kết hợp
            'number_scores': dict(sorted_numbers[:10]),  # Top 10 số với điểm
            'method_weights': adjusted_weights,
            'method': 'ket_hop'
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
        
        # Tạo tất cả các cặp số có tổng bằng predicted_sum
        predicted_numbers = []
        for i in range(10):
            j = (predicted_sum - i) % 10
            if 0 <= j < 10:
                predicted_numbers.append(f"{i}{j}")
        
        return {
            'predicted_numbers': predicted_numbers,
            'confidence': 70,  # Độ tin cậy mặc định cho phương pháp này
            'source_sum': db_sum % 10,
            'predicted_sum': predicted_sum,
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
        
        # Kiểm tra các quy tắc theo thứ
        for days, numbers in self.thu_rules.items():
            if weekday in days:
                predictions.extend(numbers)
        
        # Loại bỏ trùng lặp
        unique_predictions = list(set(predictions))
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': 65,  # Độ tin cậy mặc định cho phương pháp này
            'weekday': weekday,
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
        
        # Đánh giá độ tin cậy
        confidence = min(100, len(matched_rules) * 25)  # 25% cho mỗi quy tắc khớp, tối đa 100%
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': confidence,
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
        
        # Đánh giá độ tin cậy
        confidence = min(100, len(matched_rules) * 20)  # 20% cho mỗi quy tắc khớp, tối đa 100%
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': confidence,
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
        
        # Đánh giá độ tin cậy
        confidence = min(100, len(matched_rules) * 15)  # 15% cho mỗi quy tắc khớp, tối đa 100%
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': confidence,
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
        
        # Đánh giá độ tin cậy
        confidence = min(100, len(matched_rules) * 15)  # 15% cho mỗi quy tắc khớp, tối đa 100%
        
        return {
            'predicted_numbers': unique_predictions,
            'confidence': confidence,
            'duoi_cam': duoi_cam_list,
            'matched_rules': matched_rules,
            'method': 'theo_duoi_cam'
        }
    
    def combine_predictions(self, predictions_dict):
        """
        Kết hợp các phương pháp dự đoán để đưa ra kết quả cuối cùng
        
        Args:
            predictions_dict: Dict chứa kết quả dự đoán từ các phương pháp
            
        Returns:
            Dict chứa kết quả dự đoán kết hợp
        """
        # Tính điểm cho mỗi số dự đoán
        number_scores = defaultdict(float)
        method_weights = {
            'theo_ngay': 1.0,
            'theo_tong_db': 0.8,
            'theo_thu': 0.7,
            'theo_cap_kem': 0.9,
            'theo_lo': 1.0,
            'theo_dau_cam': 0.6,
            'theo_duoi_cam': 0.6
        }
        
        # Cập nhật trọng số dựa trên hiệu quả lịch sử
        historical_weights = self._get_historical_method_weights()
        method_weights.update(historical_weights)
        
        # Tính điểm cho mỗi số
        for method, pred in predictions_dict.items():
            if method == 'ket_hop':  # Bỏ qua phương pháp kết hợp
                continue
                
            weight = method_weights.get(method, 0.5)
            confidence = pred.get('confidence', 50) / 100
            
            for number in pred.get('predicted_numbers', []):
                # Điểm = trọng số phương pháp * độ tin cậy
                number_scores[number] += weight * confidence
        
        # Sắp xếp theo điểm giảm dần
        sorted_numbers = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Lấy top 5 số có điểm cao nhất
        top_numbers = sorted_numbers[:5]
        
        return {
            'predicted_numbers': [num for num, _ in top_numbers],
            'confidence': 85,  # Độ tin cậy của phương pháp kết hợp
            'number_scores': dict(sorted_numbers[:10]),  # Top 10 số với điểm
            'method_weights': method_weights,
            'method': 'ket_hop'
        }
    
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
        dau_cam = all_dau - dau_appeared
        duoi_cam = all_duoi - duoi_appeared
        
        return list(dau_cam), list(duoi_cam)
    
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
                    }, cls=DateTimeEncoder)
                elif method == 'machine_learning':
                    soi_cau.ghi_chu = json.dumps({
                        'all_predictions': prediction.get('all_predictions', [])
                    }, cls=DateTimeEncoder)
                elif method == 'discovered_rules':
                    soi_cau.ghi_chu = json.dumps({
                        'matched_rules': prediction.get('matched_rules', [])
                    })
                elif method == 'cyclical':
                    # Lưu thông tin về các mẫu chu kỳ được sử dụng
                    cyclical_patterns = [
                        pattern for pattern in self.discover_cyclical_patterns()
                        if pattern['predicted_next_date'] == self.target_date.strftime('%Y-%m-%d')
                    ]
                    soi_cau.ghi_chu = json.dumps({
                        'cyclical_patterns': cyclical_patterns
                    })
                else:
                    soi_cau.ghi_chu = json.dumps({
                        'matched_rules': prediction.get('matched_rules', [])
                    })
                
                # Lưu vào DB
                soi_cau.save()
                logger.info(f"Đã lưu dự đoán {method} cho ngày {self.target_date}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu kết quả dự đoán: {e}")
            

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
            for method, _ in SoiCauBacNho.PREDICTION_METHODS:
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
                        'du_doan_theo_ngay': json.dumps(daily_stats)
                    }
                )
                
                logger.info(f"Đã cập nhật thống kê hiệu quả cho phương pháp {method}")
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
            # Lấy dữ liệu lịch sử 90 ngày gần nhất
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=90)
            
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
            
            # Lưu các quy luật mới vào cơ sở dữ liệu
            self._save_discovered_patterns(ngay_patterns, thu_patterns, lo_patterns)
            
            return {
                'status': 'success',
                'ngay_patterns': ngay_patterns,
                'thu_patterns': thu_patterns,
                'lo_patterns': lo_patterns,
                'message': f'Đã phát hiện {len(ngay_patterns) + len(thu_patterns) + len(lo_patterns)} quy luật mới'
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
                    # Ví dụ: 35 -> 46 (tăng 1 ở mỗi chữ số)
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
                condition_result = '_'.join(parts[1:]).split('_')
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
            
            # Chỉ lấy các số xuất hiện ít nhất 2 lần
            for num, count in sorted_counts:
                if count >= 2:
                    patterns.append({
                        'weekday': weekday,
                        'number': num,
                        'count': count,
                        'total_days': sum(1 for result in results if result.ngay.weekday() == weekday)
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
        
        # Gộp các mẫu giống nhau và đếm tần suất
        merged_patterns = defaultdict(int)
        for pattern in patterns:
            key = f"{pattern['type']}_{pattern['number']}"
            merged_patterns[key] += 1
        
        # Chuyển về format cuối cùng và chỉ giữ các mẫu xuất hiện ít nhất 2 lần
        final_patterns = []
        for key, count in merged_patterns.items():
            if count >= 2:
                # Phân tích key để lấy lại thông tin
                parts = key.split('_')
                pattern_type = parts[0]
                number = parts[1]
                
                final_patterns.append({
                    'number': number,
                    'type': pattern_type,
                    'count': count
                })
        
        # Sắp xếp theo số lần xuất hiện giảm dần
        return sorted(final_patterns, key=lambda x: x['count'], reverse=True)
    
    def _save_discovered_patterns(self, ngay_patterns, thu_patterns, lo_patterns):
        """
        Lưu các quy luật mới phát hiện vào cơ sở dữ liệu
        
        Args:
            ngay_patterns: List quy luật theo ngày
            thu_patterns: List quy luật theo thứ
            lo_patterns: List quy luật theo lô
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
            
            logger.info(f"Đã lưu {len(ngay_patterns) + len(thu_patterns) + len(lo_patterns)} quy luật mới")
        except Exception as e:
            logger.error(f"Lỗi khi lưu quy luật mới: {e}")

    def predict_with_machine_learning(self, source_numbers):
        """
        Sử dụng học máy để dự đoán kết quả
        
        Args:
            source_numbers: Danh sách số 2 chữ số từ kết quả hôm trước
            
        Returns:
            Dict chứa kết quả dự đoán
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
            import numpy as np
            
            # Lấy dữ liệu lịch sử cho huấn luyện
            end_date = self.source_date
            start_date = end_date - timedelta(days=365)  # Lấy dữ liệu 1 năm
            
            # Lấy tất cả kết quả xổ số trong khoảng thời gian
            results = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by('ngay')
            
            # Tạo dữ liệu huấn luyện
            X = []  # Features
            y = []  # Labels (các số 2 chữ số)
            
            for i in range(len(results) - 1):
                current_result = results[i]
                next_result = results[i + 1]
                
                # Lấy các số 2 chữ số từ kết quả hiện tại
                current_numbers = self._get_all_2digit_numbers(current_result)
                
                # Lấy các số 2 chữ số từ kết quả tiếp theo
                next_numbers = self._get_all_2digit_numbers(next_result)
                
                # Tạo features
                features = [
                    current_result.ngay.weekday(),  # Thứ trong tuần
                    current_result.ngay.day,  # Ngày trong tháng
                    current_result.ngay.month,  # Tháng
                    len(current_numbers),  # Số lượng số 2 chữ số
                ]
                
                # Thêm thông tin về sự xuất hiện của các số từ 00-99
                for i in range(100):
                    num = f"{i:02d}"
                    features.append(1 if num in current_numbers else 0)
                
                # Thêm vào dữ liệu huấn luyện
                for next_num in next_numbers:
                    X.append(features)
                    y.append(int(next_num))
            
            # Kiểm tra dữ liệu huấn luyện
            if not X or not y:
                return {
                    'predicted_numbers': [],
                    'confidence': 0,
                    'method': 'machine_learning'
                }
            
            # Huấn luyện mô hình
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Tạo features cho dự đoán
            predict_features = [
                self.source_date.weekday(),  # Thứ trong tuần
                self.source_date.day,  # Ngày trong tháng
                self.source_date.month,  # Tháng
                len(source_numbers),  # Số lượng số 2 chữ số
            ]
            
            # Thêm thông tin về sự xuất hiện của các số từ 00-99
            for i in range(100):
                num = f"{i:02d}"
                predict_features.append(1 if num in source_numbers else 0)
            
            # Dự đoán xác suất cho tất cả các số
            proba = model.predict_proba([predict_features])[0]
            
            # Lấy top 10 số có xác suất cao nhất
            top_indices = np.argsort(proba)[-10:][::-1]
            top_numbers = [f"{idx:02d}" for idx in top_indices]
            top_probas = [proba[idx] for idx in top_indices]
            
            # Tính độ tin cậy dựa trên xác suất trung bình của top 5 số
            confidence = min(100, sum(top_probas[:5]) * 100)
            
            return {
                'predicted_numbers': top_numbers[:5],  # Top 5 số
                'confidence': confidence,
                'all_predictions': list(zip(top_numbers, [p * 100 for p in top_probas])),
                'method': 'machine_learning'
            }
        except Exception as e:
            logger.error(f"Lỗi khi dự đoán bằng học máy: {e}")
            return {
                'predicted_numbers': [],
                'confidence': 0,
                'error': str(e),
                'method': 'machine_learning'
            }

    def predict_with_machine_learning(self, source_numbers):
        """
        Sử dụng học máy để dự đoán kết quả
        
        Args:
            source_numbers: Danh sách số 2 chữ số từ kết quả hôm trước
            
        Returns:
            Dict chứa kết quả dự đoán
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
            import numpy as np
            
            # Lấy dữ liệu lịch sử cho huấn luyện
            end_date = self.source_date
            start_date = end_date - timedelta(days=365)  # Lấy dữ liệu 1 năm
            
            # Lấy tất cả kết quả xổ số trong khoảng thời gian
            results = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by('ngay')
            
            # Tạo dữ liệu huấn luyện
            X = []  # Features
            y = []  # Labels (các số 2 chữ số)
            
            for i in range(len(results) - 1):
                current_result = results[i]
                next_result = results[i + 1]
                
                # Lấy các số 2 chữ số từ kết quả hiện tại
                current_numbers = self._get_all_2digit_numbers(current_result)
                
                # Lấy các số 2 chữ số từ kết quả tiếp theo
                next_numbers = self._get_all_2digit_numbers(next_result)
                
                # Tạo features
                features = [
                    current_result.ngay.weekday(),  # Thứ trong tuần
                    current_result.ngay.day,  # Ngày trong tháng
                    current_result.ngay.month,  # Tháng
                    len(current_numbers),  # Số lượng số 2 chữ số
                ]
                
                # Thêm thông tin về sự xuất hiện của các số từ 00-99
                for i in range(100):
                    num = f"{i:02d}"
                    features.append(1 if num in current_numbers else 0)
                
                # Thêm vào dữ liệu huấn luyện
                for next_num in next_numbers:
                    X.append(features)
                    y.append(int(next_num))
            
            # Kiểm tra dữ liệu huấn luyện
            if not X or not y:
                return {
                    'predicted_numbers': [],
                    'confidence': 0,
                    'method': 'machine_learning'
                }
            
            # Huấn luyện mô hình
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Tạo features cho dự đoán
            predict_features = [
                self.source_date.weekday(),  # Thứ trong tuần
                self.source_date.day,  # Ngày trong tháng
                self.source_date.month,  # Tháng
                len(source_numbers),  # Số lượng số 2 chữ số
            ]
            
            # Thêm thông tin về sự xuất hiện của các số từ 00-99
            for i in range(100):
                num = f"{i:02d}"
                predict_features.append(1 if num in source_numbers else 0)
            
            # Dự đoán xác suất cho tất cả các số
            proba = model.predict_proba([predict_features])[0]
            
            # Lấy top 10 số có xác suất cao nhất
            top_indices = np.argsort(proba)[-10:][::-1]
            top_numbers = [f"{idx:02d}" for idx in top_indices]
            top_probas = [proba[idx] for idx in top_indices]
            
            # Tính độ tin cậy dựa trên xác suất trung bình của top 5 số
            confidence = min(100, sum(top_probas[:5]) * 100)
            
            return {
                'predicted_numbers': top_numbers[:5],  # Top 5 số
                'confidence': confidence,
                'all_predictions': list(zip(top_numbers, [p * 100 for p in top_probas])),
                'method': 'machine_learning'
            }
        except Exception as e:
            logger.error(f"Lỗi khi dự đoán bằng học máy: {e}")
            return {
                'predicted_numbers': [],
                'confidence': 0,
                'error': str(e),
                'method': 'machine_learning'
            }
        
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
            
            # Lấy các ngày có đủ dự đoán từ tất cả các phương pháp
            dates_with_predictions = []
            
            for date in (start_date + timedelta(days=i) for i in range((end_date - start_date).days)):
                # Kiểm tra xem có dự đoán từ tất cả các phương pháp không
                method_count = SoiCauBacNho.objects.filter(
                    ngay_du_doan=date,
                    ket_qua_thuc_te__isnull=False
                ).exclude(phuong_phap='ket_hop').count()
                
                # Nếu có ít nhất 5 phương pháp
                if method_count >= 5:
                    dates_with_predictions.append(date)
            
            # Nếu không đủ dữ liệu, trả về trọng số mặc định
            if len(dates_with_predictions) < 10:
                return self._get_historical_method_weights()
            
            # Chuẩn bị dữ liệu cho tối ưu hóa
            method_names = [m for m, _ in SoiCauBacNho.PREDICTION_METHODS if m != 'ket_hop']
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
                
                # Chỉ thêm ngày có dữ liệu từ tất cả các phương pháp
                if len(date_data['methods']) == len(method_names):
                    data.append(date_data)
            
            # Nếu không đủ dữ liệu, trả về trọng số mặc định
            if len(data) < 10:
                return self._get_historical_method_weights()
            
            # Hàm mục tiêu cho tối ưu hóa: tối đa hóa số lần trúng
            def objective_function(weights):
                # Chuẩn hóa trọng số
                weights = weights / np.sum(weights)
                
                total_hits = 0
                
                for date_data in data:
                    # Tính điểm cho mỗi số
                    number_scores = defaultdict(float)
                    
                    for i, method in enumerate(method_names):
                        if method in date_data['methods']:
                            for number in date_data['methods'][method]:
                                number_scores[number] += weights[i]
                    
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
            
            # Ràng buộc: các trọng số >= 0.1 và <= 1
            bounds = [(0.1, 1.0) for _ in method_names]
            
            # Trọng số ban đầu: đều nhau
            initial_weights = np.ones(len(method_names)) / len(method_names)
            
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
            # Lấy dữ liệu lịch sử 180 ngày gần nhất
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=180)
            
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
                
                # Chỉ giữ các mẫu có độ lệch chuẩn thấp (chu kỳ ổn định)
                if std_interval <= avg_interval / 3 and 7 <= avg_interval <= 30:
                    # Dự đoán ngày xuất hiện tiếp theo
                    last_date = dates[-1]
                    next_date = last_date + timedelta(days=round(avg_interval))
                    
                    cyclical_patterns.append({
                        'number': num,
                        'avg_interval': avg_interval,
                        'std_interval': std_interval,
                        'appearances': len(dates),
                        'last_date': last_date.strftime('%Y-%m-%d'),
                        'predicted_next_date': next_date.strftime('%Y-%m-%d'),
                        'confidence': 100 - (std_interval / avg_interval) * 100
                    })
            
            # Sắp xếp theo độ tin cậy giảm dần
            return sorted(cyclical_patterns, key=lambda x: x['confidence'], reverse=True)
        except Exception as e:
            logger.error(f"Lỗi khi phát hiện quy luật chu kỳ: {e}")
            return []    