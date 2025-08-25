from .performance_evaluator import PerformanceEvaluator
from typing import Dict
import numpy as np


class WeightOptimizer:
    """Tối ưu hóa trọng số dựa trên dữ liệu lịch sử"""
    
    def __init__(self):
        self.evaluator = PerformanceEvaluator()
    
    def optimize_weights(self):
        """
        Tối ưu hóa trọng số dựa trên dữ liệu lịch sử
        
        Returns:
            Dict chứa trọng số tối ưu cho từng phương pháp
        """
        # Phân chia thời gian đánh giá
        evaluation_periods = [
            ('recent', 14),    # 2 tuần gần đây
            ('medium', 30),    # 1 tháng gần đây
            ('long', 90)       # 3 tháng gần đây
        ]
        
        # Đánh giá hiệu suất cho từng khoảng thời gian
        period_results = {}
        for period_name, days in evaluation_periods:
            period_results[period_name] = self.evaluator.evaluate_all_methods(days)
        
        # Kết hợp trọng số với ưu tiên khác nhau
        # - Dữ liệu gần đây: 50%
        # - Dữ liệu trung hạn: 30%
        # - Dữ liệu dài hạn: 20%
        combined_weights = {}
        
        # Lấy danh sách phương pháp từ kết quả gần đây
        methods = period_results['recent']['optimal_weights'].keys()
        
        for method in methods:
            combined_weights[method] = (
                0.5 * period_results['recent']['optimal_weights'].get(method, 0) +
                0.3 * period_results['medium']['optimal_weights'].get(method, 0) +
                0.2 * period_results['long']['optimal_weights'].get(method, 0)
            )
        
        # Chuẩn hóa lại tổng trọng số = 1
        total_weight = sum(combined_weights.values())
        if total_weight > 0:
            for method in combined_weights:
                combined_weights[method] = combined_weights[method] / total_weight
        
        return combined_weights
    
    def save_optimized_weights(self):
        """Lưu trọng số tối ưu vào cơ sở dữ liệu"""
        from django.utils import timezone
        
        # Tối ưu hóa trọng số
        optimal_weights = self.optimize_weights()
        
        # Lưu vào DB
        try:
            from results.models import OptimizedWeights
            
            weights_record = OptimizedWeights(
                calculation_date=timezone.now().date(),
                weights=optimal_weights,
                meta_info={
                    'evaluation_method': 'backtesting',
                    'periods_used': ['recent', 'medium', 'long'],
                    'calculation_timestamp': timezone.now().isoformat()
                }
            )
            weights_record.save()
            
            logger.info(f"Saved optimized weights: {optimal_weights}")
            return True
        except Exception as e:
            logger.error(f"Error saving optimized weights: {e}")
            return False