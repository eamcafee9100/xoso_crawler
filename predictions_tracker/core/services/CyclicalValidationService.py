import logging
import numpy as np
from datetime import date, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
from django.db.models import Count, Avg
from django.utils import timezone

from predictions_tracker.models import (
    CyclicalContextEngine,
    MethodCycleSyncMatrix, 
    CyclicalNumberPredictor,
    PredictionMethod
)
from results.models import KetQuaXoSo, NumberFrequencyStats

logger = logging.getLogger(__name__)


class CyclicalValidationService:
    """Service for cyclical approach validation and backtesting"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def validate_cyclical_approach(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Validate cyclical approach với historical data
        
        Args:
            start_date: Ngày bắt đầu validation
            end_date: Ngày kết thúc validation
            
        Returns:
            dict: {
                "validation_period": dict,
                "overall_metrics": dict,
                "daily_results": list,
                "performance_analysis": dict,
                "comparison_baseline": dict
            }
        """
        try:
            self.logger.info(f"🔍 Starting validation from {start_date} to {end_date}")
            
            # 1. Generate validation results
            daily_results = self._generate_validation_results(start_date, end_date)
            
            # 2. Calculate overall metrics
            overall_metrics = self._calculate_overall_metrics(daily_results)
            
            # 3. Performance analysis
            performance_analysis = self._analyze_performance_patterns(daily_results)
            
            # 4. Compare with baseline (random/naive approach)
            comparison_baseline = self._compare_with_baseline(daily_results)
            
            validation_result = {
                "validation_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_days": len(daily_results),
                    "successful_predictions": len([r for r in daily_results if r["success"]])
                },
                "overall_metrics": overall_metrics,
                "daily_results": daily_results,
                "performance_analysis": performance_analysis,
                "comparison_baseline": comparison_baseline,
                "validation_timestamp": timezone.now().isoformat()
            }
            
            self.logger.info(f"✅ Validation completed. Overall accuracy: {overall_metrics.get('accuracy', 0):.1%}")
            return validation_result
            
        except Exception as e:
            self.logger.error(f"❌ Validation failed: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "validation_period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
            }
    
    def _generate_validation_results(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Generate validation results for each day
        
        Returns:
            list: [{"analysis_date": date, "predictions": list, "actual": list, "metrics": dict}, ...]
        """
        results = []
        current_date = start_date
        
        while current_date <= end_date:
            try:
                # Skip weekends if no lottery data
                if current_date.weekday() >= 5:  # Saturday, Sunday
                    current_date += timedelta(days=1)
                    continue
                
                result = self._validate_single_day(current_date)
                if result:
                    results.append(result)
                    
            except Exception as e:
                self.logger.warning(f"❌ Failed to validate {current_date}: {str(e)}")
                
            current_date += timedelta(days=1)
        
        return results
    
    def _validate_single_day(self, analysis_date: date) -> Dict[str, Any]:
        """
        Validate cyclical approach for single day
        
        Returns:
            dict: {
                "analysis_date": str,
                "target_date": str,
                "success": bool,
                "predictions": list,
                "actual_numbers": list,
                "metrics": dict,
                "cyclical_data": dict
            }
        """
        target_date = analysis_date + timedelta(days=1)
        
        # Get actual results for target date
        actual_numbers = self._get_actual_numbers(target_date)
        if not actual_numbers:
            return None
        
        # Generate cyclical predictions for analysis_date
        cyclical_predictions = self._generate_cyclical_predictions_for_validation(analysis_date)
        if not cyclical_predictions:
            return None
        
        # Calculate metrics
        metrics = self._calculate_single_day_metrics(cyclical_predictions, actual_numbers)
        
        # Get cyclical context data
        cyclical_data = self._get_cyclical_context_data(analysis_date)
        
        return {
            "analysis_date": analysis_date.isoformat(),
            "target_date": target_date.isoformat(),
            "success": metrics["hit_count"] > 0,
            "predictions": cyclical_predictions,
            "actual_numbers": actual_numbers,
            "metrics": metrics,
            "cyclical_data": cyclical_data
        }
    
    def _get_actual_numbers(self, target_date: date) -> List[str]:
        """Get actual lottery numbers for target date"""
        try:
            ketqua = KetQuaXoSo.objects.get(ngay=target_date)
            return list(ketqua.get_all_2digit_numbers())
        except KetQuaXoSo.DoesNotExist:
            return []
    
    def _generate_cyclical_predictions_for_validation(self, analysis_date: date) -> List[str]:
        """Generate cyclical predictions for validation"""
        try:
            # Use CyclicalNumberPredictor
            predictor = CyclicalNumberPredictor.predict_numbers_by_frequency_cycles(analysis_date)
            
            # Extract top predicted numbers
            predictions = []
            for item in predictor.predicted_numbers[:15]:  # Top 15
                if isinstance(item, dict) and "number" in item:
                    predictions.append(item["number"])
            
            return predictions
            
        except Exception as e:
            self.logger.warning(f"❌ Failed to generate predictions for {analysis_date}: {str(e)}")
            return []
    
    def _calculate_single_day_metrics(self, predictions: List[str], actual: List[str]) -> Dict[str, Any]:
        """
        Calculate metrics for single day validation
        
        Returns:
            dict: {
                "total_predictions": int,
                "total_actual": int,
                "hit_count": int,
                "accuracy": float,
                "precision": float,
                "recall": float
            }
        """
        predictions_set = set(predictions)
        actual_set = set(actual)
        
        hit_count = len(predictions_set & actual_set)
        total_predictions = len(predictions)
        total_actual = len(actual)
        
        accuracy = hit_count / total_predictions if total_predictions > 0 else 0
        precision = hit_count / total_predictions if total_predictions > 0 else 0
        recall = hit_count / total_actual if total_actual > 0 else 0
        
        return {
            "total_predictions": total_predictions,
            "total_actual": total_actual,
            "hit_count": hit_count,
            "accuracy": round(accuracy, 3),
            "precision": round(precision, 3),
            "recall": round(recall, 3)
        }
    
    def _get_cyclical_context_data(self, analysis_date: date) -> Dict[str, Any]:
        """Get cyclical context data for analysis"""
        try:
            context = CyclicalContextEngine.objects.get(analysis_date=analysis_date)
            return {
                "day_of_month_phase": context.day_of_month_phase,
                "week_phase": context.week_phase,
                "cycle_strength": context.cycle_strength,
                "month_trend": context.month_trend
            }
        except CyclicalContextEngine.DoesNotExist:
            return {
                "day_of_month_phase": "unknown",
                "week_phase": "unknown", 
                "cycle_strength": 0.0,
                "month_trend": "unknown"
            }
    
    def _calculate_overall_metrics(self, daily_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall validation metrics
        
        Returns:
            dict: {
                "accuracy": float,
                "total_days": int,
                "successful_days": int,
                "avg_hits_per_day": float,
                "best_day": dict,
                "worst_day": dict
            }
        """
        if not daily_results:
            return {}
        
        total_days = len(daily_results)
        successful_days = sum(1 for result in daily_results if result["success"])
        total_hits = sum(result["metrics"]["hit_count"] for result in daily_results)
        
        accuracy = successful_days / total_days if total_days > 0 else 0
        avg_hits_per_day = total_hits / total_days if total_days > 0 else 0
        
        # Find best and worst days
        best_day = max(daily_results, key=lambda x: x["metrics"]["hit_count"])
        worst_day = min(daily_results, key=lambda x: x["metrics"]["hit_count"])
        
        return {
            "accuracy": round(accuracy, 3),
            "total_days": total_days,
            "successful_days": successful_days,
            "total_hits": total_hits,
            "avg_hits_per_day": round(avg_hits_per_day, 2),
            "best_day": {
                "date": best_day["analysis_date"],
                "hits": best_day["metrics"]["hit_count"]
            },
            "worst_day": {
                "date": worst_day["analysis_date"], 
                "hits": worst_day["metrics"]["hit_count"]
            }
        }
    
    def _analyze_performance_patterns(self, daily_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze performance patterns
        
        Returns:
            dict: {
                "by_phase": dict,
                "by_weekday": dict,
                "by_cycle_strength": dict,
                "trends": dict
            }
        """
        # Performance by month phase
        by_phase = defaultdict(list)
        for result in daily_results:
            phase = result["cyclical_data"]["day_of_month_phase"]
            by_phase[phase].append(result["metrics"]["hit_count"])
        
        phase_performance = {
            phase: {
                "avg_hits": round(np.mean(hits), 2),
                "total_days": len(hits),
                "success_rate": round(sum(1 for h in hits if h > 0) / len(hits), 3)
            }
            for phase, hits in by_phase.items()
        }
        
        # Performance by weekday
        by_weekday = defaultdict(list)
        for result in daily_results:
            analysis_date = date.fromisoformat(result["analysis_date"])
            weekday = analysis_date.weekday()
            by_weekday[weekday].append(result["metrics"]["hit_count"])
        
        weekday_performance = {
            weekday: {
                "avg_hits": round(np.mean(hits), 2),
                "total_days": len(hits),
                "success_rate": round(sum(1 for h in hits if h > 0) / len(hits), 3)
            }
            for weekday, hits in by_weekday.items()
        }
        
        # Performance by cycle strength
        high_strength_hits = []
        low_strength_hits = []
        
        for result in daily_results:
            cycle_strength = result["cyclical_data"]["cycle_strength"]
            hits = result["metrics"]["hit_count"]
            
            if cycle_strength > 0.6:
                high_strength_hits.append(hits)
            else:
                low_strength_hits.append(hits)
        
        strength_performance = {
            "high_strength": {
                "avg_hits": round(np.mean(high_strength_hits), 2) if high_strength_hits else 0,
                "total_days": len(high_strength_hits),
                "success_rate": round(sum(1 for h in high_strength_hits if h > 0) / len(high_strength_hits), 3) if high_strength_hits else 0
            },
            "low_strength": {
                "avg_hits": round(np.mean(low_strength_hits), 2) if low_strength_hits else 0,
                "total_days": len(low_strength_hits), 
                "success_rate": round(sum(1 for h in low_strength_hits if h > 0) / len(low_strength_hits), 3) if low_strength_hits else 0
            }
        }
        
        return {
            "by_phase": phase_performance,
            "by_weekday": weekday_performance, 
            "by_cycle_strength": strength_performance,
            "trends": self._calculate_performance_trends(daily_results)
        }
    
    def _calculate_performance_trends(self, daily_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(daily_results) < 7:
            return {"trend": "insufficient_data"}
        
        # Sort by date
        sorted_results = sorted(daily_results, key=lambda x: x["analysis_date"])
        
        # Calculate moving average (7-day window)
        moving_avg = []
        for i in range(6, len(sorted_results)):
            window_hits = [r["metrics"]["hit_count"] for r in sorted_results[i-6:i+1]]
            moving_avg.append(np.mean(window_hits))
        
        # Calculate trend
        if len(moving_avg) >= 2:
            trend_slope = np.polyfit(range(len(moving_avg)), moving_avg, 1)[0]
            trend_direction = "improving" if trend_slope > 0.01 else "declining" if trend_slope < -0.01 else "stable"
        else:
            trend_direction = "stable"
            trend_slope = 0
        
        return {
            "trend": trend_direction,
            "slope": round(trend_slope, 4),
            "moving_average": [round(avg, 2) for avg in moving_avg[-10:]]  # Last 10 points
        }
    
    def _compare_with_baseline(self, daily_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare cyclical approach with baseline methods
        
        Returns:
            dict: {
                "random_baseline": dict,
                "naive_baseline": dict,
                "improvement": dict
            }
        """
        # Random baseline: random 15 numbers
        random_baseline = self._simulate_random_baseline(daily_results)
        
        # Naive baseline: most frequent numbers  
        naive_baseline = self._simulate_naive_baseline(daily_results)
        
        # Calculate improvement
        cyclical_accuracy = np.mean([r["metrics"]["hit_count"] for r in daily_results])
        random_accuracy = random_baseline["avg_hits"]
        naive_accuracy = naive_baseline["avg_hits"]
        
        improvement = {
            "vs_random": {
                "absolute": round(cyclical_accuracy - random_accuracy, 2),
                "relative": round((cyclical_accuracy / random_accuracy - 1) * 100, 1) if random_accuracy > 0 else 0
            },
            "vs_naive": {
                "absolute": round(cyclical_accuracy - naive_accuracy, 2), 
                "relative": round((cyclical_accuracy / naive_accuracy - 1) * 100, 1) if naive_accuracy > 0 else 0
            }
        }
        
        return {
            "random_baseline": random_baseline,
            "naive_baseline": naive_baseline,
            "improvement": improvement
        }
    
    def _simulate_random_baseline(self, daily_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate random number selection baseline"""
        import random
        
        total_hits = 0
        successful_days = 0
        
        for result in daily_results:
            # Generate random 15 numbers (00-99)
            random_predictions = [f"{i:02d}" for i in random.sample(range(100), 15)]
            actual_numbers = result["actual_numbers"]
            
            hits = len(set(random_predictions) & set(actual_numbers))
            total_hits += hits
            if hits > 0:
                successful_days += 1
        
        total_days = len(daily_results)
        return {
            "avg_hits": round(total_hits / total_days, 2) if total_days > 0 else 0,
            "success_rate": round(successful_days / total_days, 3) if total_days > 0 else 0,
            "total_days": total_days
        }
    
    def _simulate_naive_baseline(self, daily_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate naive frequent numbers baseline"""
        # Get most frequent numbers from historical data
        end_date = date.fromisoformat(daily_results[0]["analysis_date"])
        start_date = end_date - timedelta(days=180)
        
        frequent_numbers = NumberFrequencyStats.objects.filter(
            date__range=[start_date, end_date]
        ).values('number').annotate(
            count=Count('number')
        ).order_by('-count')[:15]
        
        naive_predictions = [stat['number'] for stat in frequent_numbers]
        
        total_hits = 0
        successful_days = 0
        
        for result in daily_results:
            actual_numbers = result["actual_numbers"]
            hits = len(set(naive_predictions) & set(actual_numbers))
            total_hits += hits
            if hits > 0:
                successful_days += 1
        
        total_days = len(daily_results)
        return {
            "avg_hits": round(total_hits / total_days, 2) if total_days > 0 else 0,
            "success_rate": round(successful_days / total_days, 3) if total_days > 0 else 0,
            "total_days": total_days,
            "predictions": naive_predictions
        }


# Service instance
cyclical_validation_service = CyclicalValidationService()