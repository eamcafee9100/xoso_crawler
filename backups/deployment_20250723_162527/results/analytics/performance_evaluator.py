import logging
from datetime import datetime, timedelta
from django.utils import timezone
from collections import defaultdict
import numpy as np
import json

from results.models import KetQuaXoSo, PredictionStatistic, NumberFrequencyStats, AdvancedAnalysisResult
from results.analytics.predictors import BachThuLoPredictor

logger = logging.getLogger(__name__)

class PerformanceEvaluator:
    """
    Lớp đánh giá hiệu suất các phương pháp dự đoán
    Kết hợp tính năng của cả hai phiên bản và mở rộng thêm
    """
    
    def __init__(self, target_date=None, historical_days=90,force_evaluation=False):
        """
        Khởi tạo đánh giá hiệu suất
        Args:
            target_date: Ngày mục tiêu để đánh giá (mặc định là hôm nay)
            historical_days: Số ngày lịch sử để đánh giá
        """
        self.historical_days = historical_days
        self.target_date = target_date or timezone.now().date()
        self.db_cache = {}  # Cache kết quả từ DB để giảm truy vấn
        self.force_evaluation = force_evaluation  # Lưu tham số force_evaluation
    def run_historical_evaluation(self, end_date=None, days=None):
        """
        Chạy đánh giá hiệu suất trên dữ liệu lịch sử
        
        Args:
            end_date: Ngày kết thúc đánh giá (mặc định là hôm qua)
            days: Số ngày để đánh giá tính từ end_date
            
        Returns:
            Dict với kết quả đánh giá
        """
        if end_date is None:
            end_date = timezone.now().date() - timedelta(days=1)
        
        if days is None:
            days = self.historical_days
            
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Chạy đánh giá hiệu suất từ {start_date} đến {end_date}")
        
        # Lấy tất cả các ngày trong khoảng
        evaluation_dates = []
        current_date = start_date
        while current_date <= end_date:
            evaluation_dates.append(current_date)
            current_date += timedelta(days=1)
            
        # Chạy đánh giá cho từng ngày
        results = {}
        for date in evaluation_dates:
            try:
                date_results = self.evaluate_single_date(date)
                results[date.strftime('%Y-%m-%d')] = date_results
                logger.info(f"Hoàn thành đánh giá cho ngày {date}")
            except Exception as e:
                logger.error(f"Lỗi khi đánh giá ngày {date}: {e}", exc_info=True)
                
        # Tính toán thống kê tổng quan
        overall_stats = self.calculate_overall_statistics(results)
        
        # Cập nhật trọng số phương pháp dựa trên đánh giá
        self.update_method_weights(overall_stats)
        
        # Cập nhật NumberFrequencyStats cho tất cả các ngày đã đánh giá
        self.update_number_frequency_stats(evaluation_dates)
        
        return {
            'results': results,
            'overall_stats': overall_stats,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'days_analyzed': days
        }
    
    def evaluate_single_date(self, target_date):
        """
        Đánh giá dự đoán cho một ngày cụ thể
        
        Args:
            target_date: Ngày cần đánh giá
            
        Returns:
            Dict với kết quả đánh giá cho ngày này
        """
        # Kiểm tra xem đã có thống kê cho ngày này chưa
        existing_stats = PredictionStatistic.objects.filter(date=target_date)
        if existing_stats.exists() and not self.force_evaluation:
            logger.info(f"Đã có thống kê dự đoán cho ngày {target_date}, bỏ qua")
            
            # Trả về kết quả từ thống kê đã có
            method_results = {}
            for stat in existing_stats:
                method_results[stat.method] = {
                    'predictions': json.loads(stat.predictions) if hasattr(stat, 'predictions') and stat.predictions else [],
                    'hits': [],  # Không có thông tin về hits cụ thể
                    'hit_rate': stat.hit_rate if hasattr(stat, 'hit_rate') else stat.accuracy,
                    'days_since_last_hit': stat.days_since_last_hit if hasattr(stat, 'days_since_last_hit') else 0,
                    'is_tired': getattr(stat, 'is_tired', False)
                }
                
            return {
                'target_date': target_date.strftime('%Y-%m-%d'),
                'actual_numbers': [],  # Không có thông tin về actual_numbers cụ thể
                'method_results': method_results,
                'from_cache': True
            }
        
        # Nếu force_evaluation và có dữ liệu cũ, xóa dữ liệu cũ
        if existing_stats.exists() and self.force_evaluation:
            logger.info(f"Xóa thống kê cũ cho ngày {target_date} để đánh giá lại")
            existing_stats.delete()
        
        # Lấy kết quả thực tế cho target_date
        actual_result = self._get_actual_result(target_date)
        if not actual_result:
            logger.warning(f"Không tìm thấy kết quả thực tế cho {target_date}")
            return {'error': 'Không tìm thấy kết quả thực tế'}    
        actual_numbers = self._get_2digit_numbers(actual_result)
        
        # Lấy dữ liệu lịch sử đến ngày trước target_date
        historical_data = KetQuaXoSo.objects.filter(
            ngay__lt=target_date
        ).order_by('-ngay')[:90]  # Sử dụng 90 ngày lịch sử
        
        if len(historical_data) < 7:
            logger.warning(f"Không đủ dữ liệu lịch sử cho {target_date}")
            return {'error': 'Không đủ dữ liệu lịch sử'}
            
        # Khởi tạo predictor với ngày trước target_date
        selected_date = target_date - timedelta(days=1)
        predictor = BachThuLoPredictor(
            target_date=target_date,
            history_days=min(90, len(historical_data)),
            selected_date=selected_date
        )
        
        # Thiết lập dữ liệu lịch sử để tránh truy vấn database
        predictor.historical_data = historical_data
        
        # Kiểm tra tất cả các phương pháp dự đoán
        methods_to_evaluate = {
            'predict_frequency': 'tan_so_cao',
            'predict_recent': 'lap_lai_gan_nhat',
            'predict_shadow': 'bong_so',
            'predict_region': 'khu_vuc',
            'predict_cycle': 'chu_ky'
        }
        
        # Thêm các phương pháp nâng cao nếu có
        for method_name in dir(predictor):
            if method_name.startswith('predict_') and method_name not in methods_to_evaluate:
                # Thêm phương pháp mới với key dựa trên tên phương pháp
                method_key = method_name.replace('predict_', '')
                methods_to_evaluate[method_name] = method_key
        
        method_results = {}
        for method_name, method_key in methods_to_evaluate.items():
            if hasattr(predictor, method_name):
                try:
                    # Lấy dự đoán
                    predictions = getattr(predictor, method_name)()
                    
                    if not predictions:
                        logger.warning(f"Phương pháp {method_name} không trả về dự đoán cho {target_date}")
                        continue
                        
                    # Chuẩn hóa dự đoán
                    standardized_predictions = []
                    for num in predictions:
                        try:
                            standardized_predictions.append(str(num).zfill(2))
                        except Exception:
                            pass
                    
                    if not standardized_predictions:
                        continue
                        
                    # Tính số trúng
                    hits = [num for num in standardized_predictions if num in actual_numbers]
                    hit_rate = len(hits) / len(standardized_predictions) if standardized_predictions else 0
                    
                    # Lưu thống kê vào database
                    self._store_prediction_statistic(
                        target_date,
                        method_key,
                        standardized_predictions,
                        actual_numbers,
                        len(hits),
                        len(standardized_predictions)
                    )
                    
                    # Tính số ngày từ lần trúng cuối cùng
                    days_since_last_hit = self._calculate_days_since_last_hit(method_key, target_date)
                    
                    # Lưu kết quả cho phương pháp này
                    method_results[method_key] = {
                        'predictions': standardized_predictions,
                        'hits': hits,
                        'hit_rate': hit_rate * 100,
                        'days_since_last_hit': days_since_last_hit,
                        'is_tired': days_since_last_hit >= 19
                    }
                    
                except Exception as e:
                    logger.error(f"Lỗi khi đánh giá phương pháp {method_name} cho {target_date}: {e}", exc_info=True)
        
        return {
            'target_date': target_date.strftime('%Y-%m-%d'),
            'actual_numbers': actual_numbers,
            'method_results': method_results
        }
    
    def _calculate_days_since_last_hit(self, method_name, target_date):
        """Tính số ngày từ lần cuối phương pháp có trúng"""
        # Lấy lần trúng gần nhất trước target_date từ thống kê dự đoán
        last_hit = PredictionStatistic.objects.filter(
            method=method_name,
            date__lt=target_date,
            total_hit__gt=0
        ).order_by('-date').first()
        
        if last_hit:
            return (target_date - last_hit.date).days
        
        # Nếu không tìm thấy lần trúng trước đó, kiểm tra dữ liệu lịch sử thủ công
        historical_data = KetQuaXoSo.objects.filter(
            ngay__lt=target_date
        ).order_by('-ngay')[:30]  # Kiểm tra 30 ngày gần nhất
        
        if not historical_data or len(historical_data) < 7:
            return 0
            
        # Khởi tạo predictor để kiểm tra
        predictor = BachThuLoPredictor(
            target_date=target_date,
            history_days=min(90, len(historical_data)),
            selected_date=target_date - timedelta(days=1)
        )
        
        # Kiểm tra 30 ngày gần nhất
        days_to_check = min(30, len(historical_data))
        
        for i in range(days_to_check):
            check_date = target_date - timedelta(days=i+1)
            
            # Lấy kết quả thực tế cho ngày này
            result = next((r for r in historical_data if r.ngay == check_date), None)
            
            if not result or not hasattr(result, 'get_all_2digit_numbers'):
                continue
                
            actual_numbers = result.get_all_2digit_numbers()
            
            if not actual_numbers:
                continue
                
            # Kiểm tra xem phương pháp có trúng vào ngày này không
            method_func_name = f"predict_{method_name}" if not method_name.startswith("predict_") else method_name
            if hasattr(predictor, method_func_name):
                try:
                    method_func = getattr(predictor, method_func_name)
                    predictions = method_func()
                    
                    if predictions:
                        standardized_predictions = [str(num).zfill(2) for num in predictions]
                        hits = [num for num in standardized_predictions if num in actual_numbers]
                        
                        if hits:
                            return i + 1
                except:
                    pass
        
        # Nếu không tìm thấy lần trúng trong khoảng kiểm tra
        return days_to_check
    
    def _store_prediction_statistic(self, date, method, predictions, actual_numbers, hits, total):
        """Lưu thống kê dự đoán vào database"""
        try:
            # Tính tỷ lệ trúng
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            # Lưu vào database
            PredictionStatistic.objects.update_or_create(
                date=date,
                method=method,
                defaults={
                    'total_predicted': total,
                    'total_hit': hits,
                    'hit_rate': hit_rate,
                    'predictions': json.dumps(predictions),
                    'actual_numbers': json.dumps(actual_numbers)
                }
            )
        except Exception as e:
            logger.error(f"Lỗi khi lưu thống kê dự đoán: {e}", exc_info=True)
    
    def update_number_frequency_stats(self, dates):
        """
        Cập nhật thống kê tần suất số cho nhiều ngày
        
        Args:
            dates: Danh sách các ngày cần cập nhật
        """
        try:
            for date in dates:
                # Kiểm tra nếu đã có dữ liệu cho ngày này
                existing = NumberFrequencyStats.objects.filter(date=date).exists()
                # Sửa lại điều kiện kiểm tra
                if existing and not self.force_evaluation:
                    logger.info(f"Đã có thống kê tần suất cho ngày {date}, bỏ qua")
                    continue
                elif existing and self.force_evaluation:
                    # Nếu force evaluation, xóa thống kê cũ
                    logger.info(f"Xóa thống kê cũ cho ngày {date} để đánh giá lại")
                    NumberFrequencyStats.objects.filter(date=date).delete()
                
                # Lấy kết quả xổ số cho ngày này
                result = self._get_actual_result(date)
                if not result:
                    logger.warning(f"Không tìm thấy kết quả xổ số cho ngày {date}")
                    continue
                
                # Lấy tất cả các số 2 chữ số từ kết quả
                all_numbers = self._get_2digit_numbers(result)
                if not all_numbers:
                    logger.warning(f"Không tìm thấy số 2 chữ số cho ngày {date}")
                    continue
                
                # Lấy số từ các giải cụ thể nếu có
                special_prize = result.giai_db[-2:] if hasattr(result, 'giai_db') and result.giai_db else None
                first_prize = result.giai_1[-2:] if hasattr(result, 'giai_1') and result.giai_1 else None
                
                # Tạo bản ghi cho tất cả các số từ 00-99
                frequency_records = []
                for i in range(100):
                    number = f"{i:02d}"
                    appeared = number in all_numbers
                    appeared_in_special = number == special_prize if special_prize else False
                    appeared_in_first = number == first_prize if first_prize else False
                    appeared_in_other = appeared and not (appeared_in_special or appeared_in_first)
                    
                    # Tính số ngày từ lần xuất hiện cuối
                    days_since_last = self._calculate_days_since_last_appearance(number, date)
                    
                    # Thêm vào danh sách
                    frequency_records.append(NumberFrequencyStats(
                        number=number,
                        date=date,
                        appeared_in_special=appeared_in_special,
                        appeared_in_first=appeared_in_first,
                        appeared_in_other=appeared_in_other,
                        day_of_week=date.weekday(),
                        day_of_month=date.day,
                        week_of_month=(date.day - 1) // 7 + 1,
                        month=date.month,
                        year=date.year
                    ))
                
                # Lưu hàng loạt vào database
                NumberFrequencyStats.objects.bulk_create(frequency_records)
                logger.info(f"Đã cập nhật thống kê tần suất cho {len(frequency_records)} số vào ngày {date}")
                
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật thống kê tần suất: {e}", exc_info=True)
    
    def _calculate_days_since_last_appearance(self, number, date):
        """Tính số ngày từ lần xuất hiện cuối cùng của một số"""
        try:
            # Tìm lần xuất hiện gần nhất trước ngày này
            last_appearance = NumberFrequencyStats.objects.filter(
                number=number,
                date__lt=date,
                appeared_in_special=True
            ).order_by('-date').first()
            
            if not last_appearance:
                # Tìm trong giải nhất nếu không có trong giải đặc biệt
                last_appearance = NumberFrequencyStats.objects.filter(
                    number=number,
                    date__lt=date,
                    appeared_in_first=True
                ).order_by('-date').first()
            
            if not last_appearance:
                # Tìm trong bất kỳ giải nào
                last_appearance = NumberFrequencyStats.objects.filter(
                    number=number,
                    date__lt=date,
                    appeared_in_other=True
                ).order_by('-date').first()
            
            if last_appearance:
                return (date - last_appearance.date).days
            
            return 0  # Không có dữ liệu trước đó
            
        except Exception as e:
            logger.error(f"Lỗi khi tính ngày từ lần xuất hiện cuối: {e}", exc_info=True)
            return 0
    
    def calculate_overall_statistics(self, results):
        """Tính toán thống kê tổng thể từ kết quả đánh giá"""
        method_stats = defaultdict(lambda: {
            'total_predictions': 0,
            'correct_predictions': 0,
            'hit_days': 0,
            'evaluated_days': 0,
            'tired_days': 0
        })
        
        # Tổng hợp thống kê
        for date_str, date_results in results.items():
            if 'error' in date_results:
                continue
                
            for method_key, method_result in date_results.get('method_results', {}).items():
                method_stats[method_key]['total_predictions'] += len(method_result.get('predictions', []))
                method_stats[method_key]['correct_predictions'] += len(method_result.get('hits', []))
                method_stats[method_key]['evaluated_days'] += 1
                
                if len(method_result.get('hits', [])) > 0:
                    method_stats[method_key]['hit_days'] += 1
                    
                if method_result.get('is_tired', False):
                    method_stats[method_key]['tired_days'] += 1
        
        # Tính tỷ lệ và trung bình
        for method_key, stats in method_stats.items():
            if stats['total_predictions'] > 0:
                stats['hit_rate'] = (stats['correct_predictions'] / stats['total_predictions']) * 100
            else:
                stats['hit_rate'] = 0
                
            if stats['evaluated_days'] > 0:
                stats['day_hit_rate'] = (stats['hit_days'] / stats['evaluated_days']) * 100
                stats['tired_rate'] = (stats['tired_days'] / stats['evaluated_days']) * 100
            else:
                stats['day_hit_rate'] = 0
                stats['tired_rate'] = 0
                
            # Thêm phân tích xu hướng
            stats['trend'] = self.analyze_performance_trend(method_key, results)
        
        return {
            'method_stats': dict(method_stats),
            'analysis_date': timezone.now().strftime('%Y-%m-%d'),
            'days_analyzed': len(results)
        }
    
    def analyze_performance_trend(self, method_key, results):
        """
        Phân tích xu hướng hiệu suất của một phương pháp
        
        Args:
            method_key: Tên phương pháp
            results: Kết quả đánh giá theo ngày
            
        Returns:
            Dict chứa thông tin xu hướng
        """
        # Sắp xếp kết quả theo ngày
        sorted_results = sorted(results.items(), key=lambda x: x[0])
        
        # Trích xuất tỷ lệ trúng theo ngày
        daily_rates = []
        for date_str, date_result in sorted_results:
            if 'error' in date_result:
                continue
                
            method_result = date_result.get('method_results', {}).get(method_key)
            if method_result:
                hit_rate = method_result.get('hit_rate', 0)
                daily_rates.append(hit_rate)
        
        if not daily_rates or len(daily_rates) < 7:
            return {'direction': 'unknown', 'strength': 0}
            
        # Tính xu hướng (so sánh nửa đầu và nửa sau)
        mid_point = len(daily_rates) // 2
        first_half_avg = sum(daily_rates[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(daily_rates[mid_point:]) / (len(daily_rates) - mid_point) if len(daily_rates) > mid_point else 0
        diff = second_half_avg - first_half_avg
        
        # Xác định hướng và độ mạnh của xu hướng
        if diff > 5:  # Tăng hơn 5% được coi là xu hướng đi lên
            direction = 'up'
            strength = min(1.0, diff / 20)  # Chuẩn hóa về khoảng [0, 1]
        elif diff < -5:  # Giảm hơn 5% được coi là xu hướng đi xuống
            direction = 'down'
            strength = min(1.0, abs(diff) / 20)
        else:
            direction = 'stable'
            strength = 0
            
        return {
            'direction': direction,
            'strength': strength,
            'first_half_avg': first_half_avg,
            'second_half_avg': second_half_avg,
            'diff': diff,
            'data_points': len(daily_rates)
        }
    
    def update_method_weights(self, overall_stats):
        """Cập nhật trọng số phương pháp dựa trên kết quả đánh giá"""
        from results.models import MethodWeight  # Giả định model này đã tồn tại hoặc sẽ được tạo
        
        method_stats = overall_stats.get('method_stats', {})
        effective_date = timezone.now().date() + timedelta(days=1)  # Có hiệu lực từ ngày mai
        
        for method_key, stats in method_stats.items():
            if stats.get('evaluated_days', 0) < 7:
                logger.warning(f"Không đủ dữ liệu để cập nhật trọng số cho {method_key}")
                continue
                
            # Tính trọng số dựa trên tỷ lệ trúng và tỷ lệ mệt mỏi
            hit_rate = stats.get('hit_rate', 0)
            day_hit_rate = stats.get('day_hit_rate', 0)
            tired_rate = stats.get('tired_rate', 0)
            
            # Công thức: 70% tỷ lệ trúng + 30% tỷ lệ ngày trúng, giảm bởi tỷ lệ mệt mỏi
            base_weight = (0.7 * hit_rate/100) + (0.3 * day_hit_rate/100)
            tired_penalty = 1 - (tired_rate/100) * 0.5  # Giảm tối đa 50% dựa trên tỷ lệ mệt mỏi
            
            final_weight = base_weight * tired_penalty
            
            # Đảm bảo trọng số nằm trong khoảng hợp lý
            final_weight = max(0.1, min(0.95, final_weight))
            
            # Điều chỉnh thêm dựa trên xu hướng
            trend = stats.get('trend', {})
            trend_direction = trend.get('direction')
            trend_strength = trend.get('strength', 0)
            
            if trend_direction == 'up':
                # Tăng trọng số thêm nếu xu hướng đang đi lên
                final_weight = min(0.95, final_weight * (1 + trend_strength * 0.2))
            elif trend_direction == 'down':
                # Giảm trọng số nếu xu hướng đang đi xuống
                final_weight = max(0.1, final_weight * (1 - trend_strength * 0.2))
            
            # Lưu vào database
            try:
                MethodWeight.objects.create(
                    effective_date=effective_date,
                    method_name=method_key,
                    method_version="1.0",  # Phiên bản mặc định
                    weight=final_weight,
                    calculation_basis='historical',
                    days_analyzed=overall_stats.get('days_analyzed', 30),
                    hit_rate=hit_rate,
                    day_hit_rate=day_hit_rate,
                    tired_rate=tired_rate,
                    trend_direction=trend_direction,
                    trend_strength=trend_strength
                )
                
                logger.info(f"Đã cập nhật trọng số cho {method_key} thành {final_weight:.2f} (có hiệu lực từ {effective_date})")
            except Exception as e:
                logger.error(f"Lỗi khi lưu trọng số cho {method_key}: {e}", exc_info=True)
    
    def get_current_method_weights(self):
        """Lấy trọng số phương pháp hiện tại để dự đoán"""
        from results.models import MethodWeight  # Giả định model này đã tồn tại hoặc sẽ được tạo
        
        today = timezone.now().date()
        
        # Lấy trọng số gần nhất cho mỗi phương pháp
        method_weights = {}
        
        try:
            # Sử dụng distinct để lấy trọng số mới nhất cho mỗi phương pháp
            latest_weights = MethodWeight.objects.filter(
                effective_date__lte=today
            ).order_by('method_name', '-effective_date').distinct('method_name')
            
            for weight in latest_weights:
                method_weights[weight.method_name] = weight.weight
        except Exception as e:
            logger.error(f"Lỗi khi lấy trọng số phương pháp: {e}", exc_info=True)
        
        # Nếu không tìm thấy trọng số cho một số phương pháp, sử dụng giá trị mặc định
        default_methods = {
            'tan_so_cao': 0.54,
            'lap_lai_gan_nhat': 0.80,
            'bong_so': 0.85,
            'khu_vuc': 0.75,
            'chu_ky': 0.85
        }
        
        for method, default_weight in default_methods.items():
            if method not in method_weights:
                method_weights[method] = default_weight
        
        return method_weights
    
    def analyze_number_patterns(self, days=30):
        """
        Phân tích mẫu trong tần suất số
        
        Args:
            days: Số ngày để phân tích
            
        Returns:
            Dict với phân tích mẫu
        """
        today = timezone.now().date()
        start_date = today - timedelta(days=days)
        
        # Lấy tất cả các bản ghi tần suất cho giai đoạn
        frequency_entries = NumberFrequencyStats.objects.filter(
            date__gte=start_date,
            date__lt=today
        ).order_by('date', 'number')
        
        if not frequency_entries:
            logger.warning(f"Không tìm thấy dữ liệu tần suất cho giai đoạn phân tích")
            return {}
        
        # Đếm số lần xuất hiện theo các yếu tố khác nhau
        number_counts = defaultdict(int)
        weekday_counts = defaultdict(lambda: defaultdict(int))
        month_phase_counts = defaultdict(lambda: defaultdict(int))
        interval_patterns = defaultdict(list)
        special_prize_counts = defaultdict(int)
        first_prize_counts = defaultdict(int)
        
        for entry in frequency_entries:
            # Đếm tổng số lần xuất hiện
            if entry.appeared_in_special or entry.appeared_in_first or entry.appeared_in_other:
                number_counts[entry.number] += 1
                
                # Đếm theo thứ trong tuần
                weekday_counts[entry.day_of_week][entry.number] += 1
                
                # Đếm theo giai đoạn trong tháng
                month_phase = 1
                if entry.day_of_month > 10 and entry.day_of_month <= 20:
                    month_phase = 2
                elif entry.day_of_month > 20:
                    month_phase = 3
                month_phase_counts[month_phase][entry.number] += 1
                
                # Theo dõi giải đặc biệt và giải nhất
                if entry.appeared_in_special:
                    special_prize_counts[entry.number] += 1
                if entry.appeared_in_first:
                    first_prize_counts[entry.number] += 1
        
        # Tìm số nóng và số lạnh
        hot_numbers = sorted(
            [(num, count) for num, count in number_counts.items() if count >= 2],
            key=lambda x: x[1],
            reverse=True
        )[:15]
        
        cold_numbers = []
        for i in range(100):
            num = f"{i:02d}"
            if num not in number_counts:
                cold_numbers.append((num, 0))
            elif number_counts[num] <= 1:
                cold_numbers.append((num, number_counts[num]))
        
        # Tìm mẫu theo thứ trong tuần
        weekday_popular = {}
        for day, counts in weekday_counts.items():
            top_numbers = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
            weekday_popular[day] = top_numbers
        
        # Tìm mẫu theo giai đoạn trong tháng
        phase_popular = {}
        for phase, counts in month_phase_counts.items():
            top_numbers = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
            phase_popular[phase] = top_numbers
        
        # Tìm các số phổ biến trong giải đặc biệt và giải nhất
        top_special = sorted(special_prize_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_first = sorted(first_prize_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Tìm các cặp số liên quan
        related_pairs = self._find_related_number_pairs(frequency_entries)
        
        # Tìm mẫu đầu số và đuôi số
        first_digit_patterns = defaultdict(int)
        last_digit_patterns = defaultdict(int)
        
        for num, count in number_counts.items():
            if len(num) == 2:
                first_digit_patterns[num[0]] += count
                last_digit_patterns[num[1]] += count
        
        sorted_first_digits = sorted(first_digit_patterns.items(), key=lambda x: x[1], reverse=True)
        sorted_last_digits = sorted(last_digit_patterns.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'hot_numbers': hot_numbers,
            'cold_numbers': cold_numbers[:15],
            'weekday_popular': weekday_popular,
            'phase_popular': phase_popular,
            'top_special_prize': top_special,
            'top_first_prize': top_first,
            'related_pairs': related_pairs[:20],
            'first_digit_patterns': sorted_first_digits,
            'last_digit_patterns': sorted_last_digits,
            'analysis_period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': today.strftime('%Y-%m-%d'),
                'days': days
            }
        }
    
    def _find_related_number_pairs(self, frequency_entries):
        """Tìm các cặp số có mối liên hệ"""
        from collections import Counter
        
        # Nhóm các số xuất hiện cùng ngày
        daily_numbers = defaultdict(list)
        
        for entry in frequency_entries:
            if entry.appeared_in_special or entry.appeared_in_first or entry.appeared_in_other:
                daily_numbers[entry.date].append(entry.number)
        
        # Tìm các cặp số xuất hiện cùng nhau
        pair_counter = Counter()
        
        for date, numbers in daily_numbers.items():
            # Nếu có nhiều số trong cùng một ngày
            if len(numbers) > 1:
                # Tạo tất cả các cặp có thể
                for i in range(len(numbers)):
                    for j in range(i+1, len(numbers)):
                        # Sắp xếp để đảm bảo cùng một cặp
                        pair = tuple(sorted([numbers[i], numbers[j]]))
                        pair_counter[pair] += 1
        
        # Trả về các cặp phổ biến nhất
        return [(pair[0], pair[1], count) for pair, count in pair_counter.most_common(20)]
    
    def evaluate_method_performance(self, date_range=30):
        """
        Đánh giá hiệu suất của các phương pháp dự đoán trong khoảng thời gian
        Args:
            date_range: Số ngày để đánh giá (mặc định 30 ngày)
        Returns:
            Dict chứa thông tin hiệu suất của từng phương pháp
        """
        try:
            from results.models import PredictionStatistic
            end_date = self.target_date - timedelta(days=1)
            start_date = end_date - timedelta(days=date_range)
            
            # Lấy thống kê dự đoán đã lưu
            statistics = PredictionStatistic.objects.filter(
                date__range=(start_date, end_date)
            ).order_by('date')
            
            # Nếu không có đủ dữ liệu thống kê, chạy đánh giá mới
            if len(statistics) < date_range * 0.8:  # Yêu cầu ít nhất 80% ngày có thống kê
                logger.info(f"Không đủ dữ liệu thống kê, đánh giá lại...")
                self.run_historical_evaluation(end_date=end_date, days=date_range)
                
                # Lấy lại thống kê sau khi đánh giá
                statistics = PredictionStatistic.objects.filter(
                    date__range=(start_date, end_date)
                ).order_by('date')
            
            # Phân tích hiệu suất
            performance = {}
            
            # Gom nhóm thống kê theo phương pháp
            method_stats = defaultdict(list)
            for stat in statistics:
                method_stats[stat.method].append(stat)
            
            # Tính hiệu suất cho từng phương pháp
            for method, stats in method_stats.items():
                total_predicted = sum(stat.total_predicted for stat in stats)
                total_hit = sum(stat.total_hit for stat in stats)
                
                if total_predicted > 0:
                    accuracy = (total_hit / total_predicted) * 100
                else:
                    accuracy = 0
                
                # Phân tích xu hướng
                trend = self._analyze_statistic_trend(stats)
                
                # Tính trạng thái mệt mỏi
                is_tired = self._check_method_fatigue(method, self.target_date)
                days_since_last_hit = self._calculate_days_since_last_hit(method, self.target_date)
                
                performance[method] = {
                    'total_days': len(stats),
                    'total_predicted': total_predicted,
                    'total_hit': total_hit,
                    'accuracy': accuracy,
                    'trend': trend,
                    'is_tired': is_tired,
                    'days_since_last_hit': days_since_last_hit
                }
            
            return performance
            
        except Exception as e:
            logger.error(f"Lỗi khi đánh giá hiệu suất: {e}", exc_info=True)
            return {}
    
    def _analyze_statistic_trend(self, statistics):
        """
        Phân tích xu hướng dựa trên thống kê
        Args:
            statistics: Danh sách các thống kê dự đoán
        Returns:
            Dict chứa thông tin xu hướng
        """
        if not statistics or len(statistics) < 7:
            return {'direction': 'unknown', 'strength': 0}
        
        # Sắp xếp theo ngày
        sorted_stats = sorted(statistics, key=lambda x: x.date)
        
        # Tính độ chính xác theo ngày
        daily_accuracy = []
        for stat in sorted_stats:
            if stat.total_predicted > 0:
                daily_accuracy.append(stat.total_hit / stat.total_predicted)
            else:
                daily_accuracy.append(0)
        
        # Tính xu hướng (so sánh nửa đầu và nửa sau)
        mid_point = len(daily_accuracy) // 2
        first_half_avg = sum(daily_accuracy[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(daily_accuracy[mid_point:]) / (len(daily_accuracy) - mid_point) if len(daily_accuracy) > mid_point else 0
        diff = second_half_avg - first_half_avg
        
        # Xác định hướng và độ mạnh của xu hướng
        if diff > 0.05:
            direction = 'up'
            strength = min(1.0, diff * 5)  # Chuẩn hóa về khoảng [0, 1]
        elif diff < -0.05:
            direction = 'down'
            strength = min(1.0, abs(diff) * 5)
        else:
            direction = 'stable'
            strength = 0
        
        return {
            'direction': direction,
            'strength': strength,
            'first_half_avg': first_half_avg,
            'second_half_avg': second_half_avg,
            'diff': diff
        }
    
    def _check_method_fatigue(self, method_name, target_date):
        """Kiểm tra xem phương pháp có đang trong trạng thái mệt mỏi không"""
        days_since_last_hit = self._calculate_days_since_last_hit(method_name, target_date)
        return days_since_last_hit >= 19  # Ngưỡng mệt mỏi 19 ngày
    
    def _get_actual_result(self, date):
        """Lấy kết quả thực tế cho một ngày"""
        # Sử dụng cache để giảm truy vấn DB
        if date in self.db_cache:
            return self.db_cache[date]
        
        try:
            result = KetQuaXoSo.objects.get(ngay=date)
            self.db_cache[date] = result
            return result
        except KetQuaXoSo.DoesNotExist:
            return None
    
    def _get_2digit_numbers(self, result):
        """Lấy tất cả các số 2 chữ số từ kết quả"""
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
        return list(set(numbers))
    
    def save_analysis_result(self, all_predictions, final_predictions):
        """
        Lưu kết quả phân tích vào cơ sở dữ liệu
        Args:
            all_predictions: Tất cả các dự đoán từ các phương pháp
            final_predictions: Danh sách 27 số cuối cùng với trọng số
        """
        try:
            # Kiểm tra nếu đã có phân tích cho ngày này
            existing = AdvancedAnalysisResult.objects.filter(
                analysis_date=timezone.now().date(),
                target_date=self.target_date
            ).first()
            
            # Chuẩn bị dữ liệu lưu trữ
            analysis_data = {
                'analysis_date': timezone.now().date(),
                'target_date': self.target_date,
                'frequency_cycle_analysis': all_predictions.get('advanced', {}).get('frequency_cycles', []),
                'number_relationship_analysis': all_predictions.get('advanced', {}).get('relationships', []),
                'pattern_analysis': all_predictions.get('advanced', {}).get('patterns', []),
                'related_set_analysis': all_predictions.get('advanced', {}).get('related_sets', []),
                'spectral_analysis': all_predictions.get('advanced', {}).get('spectral', []),
                'graph_analysis': all_predictions.get('advanced', {}).get('graph', []),
                'shap_prediction': all_predictions.get('ml_models', {}).get('shap', {}),
                'lstm_prediction': all_predictions.get('ml_models', {}).get('lstm', {}),
                'rl_prediction': all_predictions.get('ml_models', {}).get('rl', {}),
                'combined_predictions': final_predictions,
                'prediction_weights': all_predictions.get('basic', {}).get('method_weights', {})
            }
            
            # Cập nhật hoặc tạo mới
            if existing:
                for key, value in analysis_data.items():
                    if key != 'analysis_date' and key != 'target_date':
                        setattr(existing, key, value)
                existing.save()
                logger.info(f"Đã cập nhật kết quả phân tích cho ngày {self.target_date}")
            else:
                result = AdvancedAnalysisResult.objects.create(**analysis_data)
                logger.info(f"Đã lưu kết quả phân tích mới cho ngày {self.target_date}")
                
        except Exception as e:
            logger.error(f"Lỗi khi lưu kết quả phân tích: {e}", exc_info=True)
    
    def evaluate_all_methods(self, evaluation_period=30):
        """
        Đánh giá hiệu suất của tất cả các phương pháp
        Args:
            evaluation_period: Số ngày trong quá khứ để đánh giá
        Returns:
            Dict chứa thông tin hiệu suất của tất cả phương pháp
        """
        try:
            # Tạo danh sách ngày đánh giá
            end_date = timezone.now().date() - timedelta(days=1)  # Trừ 1 ngày để đảm bảo có kết quả
            start_date = end_date - timedelta(days=evaluation_period)
            
            # Sử dụng phương thức run_historical_evaluation để đánh giá
            evaluation_results = self.run_historical_evaluation(end_date=end_date, days=evaluation_period)
            
            # Chuyển đổi kết quả sang định dạng trả về
            method_performance = {}
            
            for method_key, stats in evaluation_results.get('overall_stats', {}).get('method_stats', {}).items():
                method_performance[method_key] = {
                    'hit_rate': stats.get('hit_rate', 0),
                    'day_hit_rate': stats.get('day_hit_rate', 0),
                    'total_hits': stats.get('correct_predictions', 0),
                    'total_predictions': stats.get('total_predictions', 0),
                    'is_tired': stats.get('tired_rate', 0) > 50,  # Mệt mỏi nếu tỷ lệ mệt mỏi > 50%
                    'trend': stats.get('trend', {})
                }
            
            # Tính toán trọng số tối ưu
            method_performance['optimal_weights'] = self._calculate_optimal_weights(method_performance)
            
            return method_performance
            
        except Exception as e:
            logger.error(f"Lỗi khi đánh giá tất cả phương pháp: {e}", exc_info=True)
            return {}
    
    def _calculate_optimal_weights(self, performance_results):
        """
        Tính toán trọng số tối ưu dựa trên hiệu suất
        Công thức: Trọng số = (Tỷ lệ trúng + Điểm Wilson) / Tổng điểm của tất cả phương pháp
        """
        from math import sqrt
        
        def wilson_score(hits, total, z=1.96):
            """Tính điểm Wilson score"""
            if total == 0:
                return 0
            p = hits / total
            denominator = 1 + z*z/total
            centre_adjusted_probability = (p + z*z/(2*total))/denominator
            adjusted_standard_deviation = sqrt((p*(1-p)+z*z/(4*total))/total)/denominator
            lower_bound = centre_adjusted_probability - adjusted_standard_deviation
            return max(0, lower_bound)
        
        weights = {}
        total_score = 0
        
        # Tính điểm cho từng phương pháp
        for method, data in performance_results.items():
            if method == 'optimal_weights':
                continue
                
            hit_rate = data.get('hit_rate', 0)
            hits = data.get('total_hits', 0)
            total = data.get('total_predictions', 0)
            is_tired = data.get('is_tired', False)
            
            # Tính Wilson score
            wilson = wilson_score(hits, total) * 100  # Nhân 100 để cùng thang đo với hit_rate
            
            # Điểm tổng hợp (50% hit_rate + 50% wilson)
            score = (hit_rate + wilson) / 2
            
            # Giảm điểm nếu phương pháp đang mệt mỏi
            if is_tired:
                score *= 0.7  # Giảm 30% nếu mệt mỏi
                
            weights[method] = score
            total_score += score
        
        # Chuẩn hóa trọng số
        if total_score > 0:
            for method in weights:
                weights[method] = weights[method] / total_score
        else:
            # Trọng số đồng đều nếu không có đủ dữ liệu
            for method in weights:
                weights[method] = 1.0 / len(weights)
                
        return weights