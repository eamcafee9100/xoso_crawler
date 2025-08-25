from django.db.models import Count, Avg
from datetime import timedelta
from collections import defaultdict
from results.models import KetQuaXoSo
class MethodEvaluator:
    def __init__(self, target_date):
        self.target_date = target_date
        self.method_weights = self._calculate_method_weights()
        self.historical_data = KetQuaXoSo.objects.filter(
            ngay__lt=self.target_date
        ).order_by('-ngay')[:180]
    def get_method_weight(self, method_name):
        return self.method_weights.get(method_name, 0.5)
    
    def _calculate_method_weights(self):
        """Tính trọng số phương pháp dựa trên hiệu suất 90 ngày"""
        from results.models import MethodPerformance
        weights = {}
        
        for method in MethodPerformance.objects.all():
            min_success = 0.3  # Tỷ lệ thành công tối thiểu
            adjusted_rate = max(method.success_rate - min_success, 0)
            weights[method.method_name] = 0.5 + (adjusted_rate / 140)  # Chuẩn hóa về 0.5-1.0
        
        return weights
    
    def get_training_data(self, lookback_days=180):
        """Chuẩn bị dữ liệu training cho model"""
        data = []
        
        # Lấy dữ liệu lịch sử
        historical_results = KetQuaXoSo.objects.filter(
            ngay__lt=self.target_date,
            ngay__gte=self.target_date - timedelta(days=lookback_days)
        ).order_by('ngay')
        
        # Tính các chỉ số
        for i in range(10, len(historical_results)):
            current = historical_results[i]
            prev_results = historical_results[:i]
            
            # Tính các đặc trưng
            features = {
                'special_sum': sum(int(d) for d in current.giai_db),
                'repeat_days': self._calculate_repeat_days(current, prev_results),
                'freq_30': self._calculate_frequency(current, prev_results, 30),
                'freq_90': self._calculate_frequency(current, prev_results, 90),
                'position': self._calculate_position(current),
                'weekday': current.ngay.weekday(),
                'is_hit': self._check_hit(current, historical_results[i+1] if i+1 < len(historical_results) else None)
            }
            
            data.append(features)
        
        return data
    
    # ... (triển khai các phương thức helper)