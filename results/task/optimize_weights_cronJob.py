# Cài đặt cron job hoặc scheduled task
from django_cron import CronJobBase, Schedule

class OptimizeWeightsCronJob(CronJobBase):
    """Tác vụ định kỳ tối ưu hóa trọng số"""
    RUN_EVERY_DAYS = 7  # Chạy hàng tuần
    
    schedule = Schedule(run_every_mins=RUN_EVERY_DAYS * 24 * 60)
    code = 'prediction.optimize_weights'
    
    def do(self):
        optimizer = WeightOptimizer()
        success = optimizer.save_optimized_weights()
        
        if success:
            # Cập nhật thống kê
            self._update_performance_stats()
        
        return success
    
    def _update_performance_stats(self):
        """Cập nhật thống kê hiệu suất"""
        evaluator = PerformanceEvaluator()
        stats = evaluator.evaluate_all_methods(evaluation_period=90)
        
        # Lưu thống kê vào DB
        from results.models import PerformanceStats
        
        stats_record = PerformanceStats(
            calculation_date=timezone.now().date(),
            stats=stats,
            meta_info={
                'evaluation_period': 90,
                'calculation_timestamp': timezone.now().isoformat()
            }
        )
        stats_record.save()