from django.db.models import Avg, Sum 


class MethodFatigueAnalyzer:
    """Phân tích và dự đoán hiện tượng 'mệt mỏi' của phương pháp dự đoán"""
    
    def __init__(self, fatigue_threshold=19, analysis_period=30):
        """
        Khởi tạo analyzer
        
        Args:
            fatigue_threshold: Ngưỡng số ngày trúng để coi là "mệt mỏi" (thường 19-21 ngày)
            analysis_period: Số ngày phân tích (thường là 1 tháng = 30 ngày)
        """
        self.fatigue_threshold = fatigue_threshold
        self.analysis_period = analysis_period
    
    
    def analyze_method_fatigue(self, method_name, start_date=None, end_date=None):
        """
        Phân tích hiện tượng mệt mỏi của một phương pháp
        
        Args:
            method_name: Tên phương pháp cần phân tích
            start_date: Ngày bắt đầu phân tích (mặc định: 30 ngày trước hiện tại)
            end_date: Ngày kết thúc phân tích (mặc định: ngày hiện tại)
            
        Returns:
            Dict chứa thông tin phân tích mệt mỏi
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Xác định khoảng thời gian phân tích
        if end_date is None:
            end_date = timezone.now().date()
        
        if start_date is None:
            start_date = end_date - timedelta(days=self.analysis_period)
        
        # Lấy dữ liệu hiệu suất của phương pháp
        performance_data = self._get_method_performance(method_name, start_date, end_date)
        
        if not performance_data:
            return {
                'method_name': method_name,
                'analysis_period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_days': 0
                },
                'performance': {
                    'early_period': {'hit_days': 0, 'total_days': 0, 'hit_rate': 0},
                    'mid_period': {'hit_days': 0, 'total_days': 0, 'hit_rate': 0},
                    'late_period': {'hit_days': 0, 'total_days': 0, 'hit_rate': 0},
                    'overall': {'hit_days': 0, 'total_days': 0, 'hit_rate': 0}
                },
                'fatigue_analysis': {
                    'threshold': self.fatigue_threshold,
                    'is_fatigued': False,
                    'fatigue_reached_on': None,
                    'future_hit_probability': 0.5,
                    'remaining_hits': self.fatigue_threshold
                }
            }
        
        # Phân chia thành các giai đoạn (đầu, giữa, cuối tháng)
        period_days = len(performance_data) // 3
        early_period = performance_data[:period_days]
        mid_period = performance_data[period_days:2*period_days]
        late_period = performance_data[2*period_days:]
        
        # Tính hiệu suất cho từng giai đoạn
        early_hits = sum(1 for day in early_period if day['hit'])
        mid_hits = sum(1 for day in mid_period if day['hit'])
        late_hits = sum(1 for day in late_period if day['hit'])
        total_hits = early_hits + mid_hits + late_hits
        
        # Xác định ngày đạt ngưỡng mệt mỏi
        fatigue_reached_on = None
        hit_count = 0
        
        for day_data in performance_data:
            if day_data['hit']:
                hit_count += 1
                if hit_count >= self.fatigue_threshold and fatigue_reached_on is None:
                    fatigue_reached_on = day_data['date']
        
        is_fatigued = total_hits >= self.fatigue_threshold
        
        # Tính xác suất trúng cho các ngày tiếp theo
        future_hit_probability = self._calculate_future_probability(
            total_hits, len(performance_data), self.fatigue_threshold
        )
        
        return {
            'method_name': method_name,
            'analysis_period': {
                'start_date': start_date,
                'end_date': end_date,
                'total_days': len(performance_data)
            },
            'performance': {
                'early_period': {
                    'hit_days': early_hits,
                    'total_days': len(early_period),
                    'hit_rate': early_hits / len(early_period) if early_period else 0
                },
                'mid_period': {
                    'hit_days': mid_hits,
                    'total_days': len(mid_period),
                    'hit_rate': mid_hits / len(mid_period) if mid_period else 0
                },
                'late_period': {
                    'hit_days': late_hits,
                    'total_days': len(late_period),
                    'hit_rate': late_hits / len(late_period) if late_period else 0
                },
                'overall': {
                    'hit_days': total_hits,
                    'total_days': len(performance_data),
                    'hit_rate': total_hits / len(performance_data) if performance_data else 0
                }
            },
            'fatigue_analysis': {
                'threshold': self.fatigue_threshold,
                'is_fatigued': is_fatigued,
                'fatigue_reached_on': fatigue_reached_on,
                'future_hit_probability': future_hit_probability,
                'remaining_hits': max(0, self.fatigue_threshold - total_hits)
            }
        }
    
    def recommend_methods_for_date(self, target_date=None):
        """
        Đề xuất các phương pháp tốt nhất cho một ngày cụ thể
        dựa trên phân tích mệt mỏi
        
        Args:
            target_date: Ngày cần đề xuất (mặc định: ngày hiện tại)
            
        Returns:
            Dict chứa thông tin đề xuất phương pháp
        """
        from django.utils import timezone
        
        if target_date is None:
            target_date = timezone.now().date()
        
        # Xác định vị trí của ngày trong tháng
        day_of_month = target_date.day
        days_in_month = self._get_days_in_month(target_date.year, target_date.month)
        
        if day_of_month <= 10:
            period = 'early'
        elif day_of_month <= 20:
            period = 'mid'
        else:
            period = 'late'
        
        # Phân tích tất cả phương pháp
        all_methods = self.analyze_all_methods(end_date=target_date)
        
        # Sắp xếp phương pháp theo tiềm năng cho giai đoạn hiện tại
        recommendations = []
        
        for method_name, analysis in all_methods.items():
            # Kiểm tra phương pháp đã mệt mỏi chưa
            if analysis['fatigue_analysis']['is_fatigued']:
                recommendation = {
                    'method': method_name,
                    'status': 'fatigued',
                    'confidence': analysis['fatigue_analysis']['future_hit_probability'],
                    'reasoning': f"Đã đạt ngưỡng mệt mỏi ({analysis['fatigue_analysis']['threshold']} ngày) vào {analysis['fatigue_analysis']['fatigue_reached_on']}",
                    'suggested_weight': analysis['fatigue_analysis']['future_hit_probability']
                }
            else:
                # Tính điểm tin cậy dựa trên hiệu suất giai đoạn và số ngày còn lại trước ngưỡng
                period_rate = analysis['performance'][f'{period}_period']['hit_rate']
                remaining_hits = analysis['fatigue_analysis']['remaining_hits']
                
                # Điểm tin cậy cao hơn nếu còn xa ngưỡng mệt mỏi
                confidence = period_rate * (1 + (remaining_hits / self.fatigue_threshold) * 0.5)
                
                recommendation = {
                    'method': method_name,
                    'status': 'active',
                    'confidence': confidence,
                    'reasoning': f"Hiệu suất tốt trong giai đoạn {period} ({period_rate:.2%}) và còn {remaining_hits} ngày trước ngưỡng mệt mỏi",
                    'suggested_weight': min(0.95, confidence)
                }
            
            recommendations.append(recommendation)
        
        # Sắp xếp theo điểm tin cậy giảm dần
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Tính trọng số được chuẩn hóa
        total_confidence = sum(rec['confidence'] for rec in recommendations)
        for rec in recommendations:
            rec['normalized_weight'] = rec['confidence'] / total_confidence if total_confidence > 0 else 0
        
        return {
            'target_date': target_date.strftime('%Y-%m-%d'),
            'month_period': period,
            'day_of_month': day_of_month,
            'days_in_month': days_in_month,
            'recommendations': recommendations,
            'top_methods': [rec['method'] for rec in recommendations[:3]]
        }
    
    def _get_method_performance(self, method_name, start_date, end_date):
        """
        Lấy dữ liệu hiệu suất của phương pháp trong khoảng thời gian
        
        Returns:
            List[Dict]: Danh sách các ngày với thông tin {'hit': bool, 'date': date}
        """
        from results.models import PredictionPerformanceMetrics
        from datetime import timedelta
        
        performance_data = []
        current_date = start_date
        
        while current_date <= end_date:
            try:
                # Kiểm tra có kết quả dự đoán cho ngày này không
                metric = PredictionPerformanceMetrics.objects.filter(
                    method=method_name,
                    target_date=current_date
                ).first()
                
                hit = False
                if metric:
                    # Coi là hit nếu accuracy > 0 hoặc có predicted_numbers trúng
                    hit = metric.accuracy > 0 or metric.predictions_correct > 0
                
                performance_data.append({
                    'hit': hit,
                    'date': current_date,
                    'accuracy': metric.accuracy if metric else 0,
                    'predictions_correct': metric.predictions_correct if metric else 0
                })
                
            except Exception as e:
                # Nếu có lỗi, coi như không hit
                performance_data.append({
                    'hit': False,
                    'date': current_date,
                    'accuracy': 0,
                    'predictions_correct': 0
                })
            
            current_date += timedelta(days=1)
        
        return performance_data
    

    def get_recommendations_for_period(self, target_date=None, period='mid'):
        """
        Đưa ra khuyến nghị phương pháp dự đoán phù hợp cho giai đoạn hiện tại
        
        Args:
            target_date: Ngày cần dự đoán (mặc định: ngày mai)
            period: Giai đoạn trong tháng ('early', 'mid', 'late')
            
        Returns:
            Dict chứa khuyến nghị và trọng số cho từng phương pháp
        """
        from django.utils import timezone
        from datetime import timedelta
        
        if target_date is None:
            target_date = timezone.now().date() + timedelta(days=1)
        
        # Xác định giai đoạn trong tháng nếu không được chỉ định
        if period == 'mid':  # Giữ logic cũ nếu không chỉ định
            day_of_month = target_date.day
            days_in_month = self._get_days_in_month(target_date.year, target_date.month)
            
            if day_of_month <= days_in_month // 3:
                period = 'early'
            elif day_of_month <= 2 * days_in_month // 3:
                period = 'mid'
            else:
                period = 'late'
        
        # Phân tích tất cả phương pháp
        all_methods = self.analyze_all_methods(end_date=target_date)
        
        # Sắp xếp phương pháp theo tiềm năng cho giai đoạn hiện tại
        recommendations = []
        
        for method_name, analysis in all_methods.items():
            if 'error' in analysis:
                continue
                
            # Kiểm tra phương pháp đã mệt mỏi chưa
            if analysis['fatigue_analysis']['is_fatigued']:
                recommendation = {
                    'method': method_name,
                    'status': 'fatigued',
                    'confidence': analysis['fatigue_analysis']['future_hit_probability'],
                    'reasoning': f"Đã đạt ngưỡng mệt mỏi ({analysis['fatigue_analysis']['threshold']} ngày) vào {analysis['fatigue_analysis']['fatigue_reached_on']}",
                    'suggested_weight': analysis['fatigue_analysis']['future_hit_probability']
                }
            else:
                # Tính điểm tin cậy dựa trên hiệu suất giai đoạn và số ngày còn lại trước ngưỡng
                period_rate = analysis['performance'][f'{period}_period']['hit_rate']
                remaining_hits = analysis['fatigue_analysis']['remaining_hits']
                
                # Điểm tin cậy = hiệu suất giai đoạn * hệ số dung lượng còn lại
                capacity_factor = min(1.0, remaining_hits / 10)  # Giảm dần khi gần ngưỡng
                confidence = period_rate * capacity_factor
                
                recommendation = {
                    'method': method_name,
                    'status': 'active',
                    'confidence': confidence,
                    'reasoning': f"Hiệu suất giai đoạn {period}: {period_rate:.2%}, còn lại {remaining_hits} ngày trước ngưỡng mệt mỏi",
                    'suggested_weight': confidence
                }
            
            recommendations.append(recommendation)
        
        # Sắp xếp theo điểm tin cậy giảm dần
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Chuẩn hóa trọng số
        total_confidence = sum(rec['confidence'] for rec in recommendations)
        for rec in recommendations:
            rec['normalized_weight'] = rec['confidence'] / total_confidence if total_confidence > 0 else 0
        
        return {
            'target_date': target_date.strftime('%Y-%m-%d'),
            'month_period': period,
            'day_of_month': target_date.day,
            'days_in_month': self._get_days_in_month(target_date.year, target_date.month),
            'recommendations': recommendations,
            'top_methods': [rec['method'] for rec in recommendations[:3]]
        }
    
    def _get_method_performance_summary(self, method_name, start_date, end_date):
        """Lấy tóm tắt hiệu suất của phương pháp"""
        from results.models import PredictionPerformanceMetrics
        
        metrics = PredictionPerformanceMetrics.objects.filter(
            method=method_name,
            target_date__range=[start_date, end_date]
        )
        
        return {
            'total_predictions': metrics.count(),
            'total_correct': metrics.aggregate(Sum('predictions_correct'))['predictions_correct__sum'] or 0,
            'avg_accuracy': metrics.aggregate(Avg('accuracy'))['accuracy__avg'] or 0,
            'total_predicted': metrics.aggregate(Sum('total_predicted'))['total_predicted__sum'] or 0
        }
    
    def analyze_all_methods(self, methods=None, start_date=None, end_date=None):
        """
        Phân tích hiện tượng mệt mỏi cho tất cả các phương pháp
        
        Args:
            methods: Danh sách tên phương pháp (nếu None, phân tích tất cả phương pháp)
            start_date: Ngày bắt đầu phân tích
            end_date: Ngày kết thúc phân tích
            
        Returns:
            Dict chứa kết quả phân tích cho tất cả phương pháp
        """
        if methods is None:
            methods = self._get_all_method_names()
        
        results = {}
        for method in methods:
            try:
                results[method] = self.analyze_method_fatigue(method, start_date, end_date)
            except Exception as e:
                # Nếu có lỗi với phương pháp nào, tiếp tục với phương pháp khác
                results[method] = {
                    'method_name': method,
                    'error': str(e),
                    'fatigue_analysis': {
                        'is_fatigued': False,
                        'future_hit_probability': 0.5
                    }
                }
        
        return results
    
    def _calculate_future_probability(self, current_hits, total_days, threshold):
        """
        Tính xác suất trúng cho các ngày tiếp theo dựa trên lý thuyết xác suất
        
        Công thức: 
        - Nếu chưa đạt ngưỡng: Giữ nguyên xác suất trúng hiện tại
        - Nếu đã đạt ngưỡng: Giảm xác suất theo hàm logistic
        """
        if current_hits < threshold:
            # Chưa đạt ngưỡng mệt mỏi, giữ nguyên xác suất
            return current_hits / total_days if total_days > 0 else 0.5
        else:
            # Đã đạt ngưỡng, giảm xác suất
            import math
            
            # Tính số ngày vượt quá ngưỡng
            days_over_threshold = current_hits - threshold
            
            # Hàm logistic để giảm xác suất
            base_probability = current_hits / total_days if total_days > 0 else 0.5
            reduction_factor = 1 / (1 + math.exp(0.5 * days_over_threshold))
            
            return base_probability * reduction_factor
        
    def _get_all_method_names(self):
        """Lấy danh sách tất cả phương pháp dự đoán"""
        # Trong thực tế, sẽ truy vấn DB để lấy danh sách phương pháp
        return [
            'predict_frequency',
            'predict_recent',
            'predict_shadow',
            'predict_region',
            'predict_cycle',
            'get_shap_prediction',
            'analyze_frequency_cycles',
            'analyze_number_relationships',
            'analyze_result_patterns',
            'analyze_related_number_sets'
        ]
    
    def _get_days_in_month(self, year, month):
        """Lấy số ngày trong tháng"""
        import calendar
        return calendar.monthrange(year, month)[1]