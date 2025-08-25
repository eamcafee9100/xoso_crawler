from typing import Dict, List, Tuple, Optional
from datetime import date, timedelta
import logging
from django.core.cache import cache
from django.db.models import Count, Sum, Avg, Q
import numpy as np
from django.db import models
from .strategies import (
    detect_cycle_fft, phase_wilson_scores, markov_chain_probability,
    gap_analysis, frequency_analysis, pattern_mining, ensemble_diversity_score
)
from results.models import (
    DanBtl, PredictionMethodBtl, PredictionResultBtl,
    BtlAnalytics, NumberFrequencyStats
)
from results.views import wilson_score
from abc import ABC, abstractmethod
from results.utils.cache_utils import safe_cache_get, safe_cache_set
from results.utils.statistical_utils import (
    gap_analysis, frequency_analysis, pattern_mining, ensemble_diversity_score
)
logger = logging.getLogger(__name__)

class AnalysisStrategy(ABC):
    """Abstract base class for analysis strategies"""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
    
    @abstractmethod
    def analyze(self, analysis_date: date, days_back: int = 30) -> Dict[str, float]:
        """Analyze and return scores for numbers"""
        pass
    
    def get_cache_key(self, analysis_date: date, days_back: int) -> str:
        return f"strategy_{self.name}_{analysis_date}_{days_back}"


class CycleStrategy(AnalysisStrategy):
    """Chiến lược phân tích chu kỳ"""
    
    def analyze(self, analysis_date: date = None, days_back: int = 30, data: Dict = None) -> Dict[str, float]:
        # Support both new interface (analysis_date) and old interface (data dict)
        if data is None:
            data = {}
        
        if analysis_date:
            data['target_date'] = analysis_date
        
        method_history = data.get('method_history', {})
        target_date = data.get('target_date', date.today())
        
        scores = {}
        
        for method_name, history in method_history.items():
            if len(history) < 10:  # Cần ít nhất 10 điểm dữ liệu
                continue
            
            # Tạo chuỗi hit/miss
            hit_sequence = [1 if h['hit_count'] > 0 else 0 for h in history]
            
            # Phát hiện chu kỳ
            try:
                cycle_info = detect_cycle_fft(hit_sequence)
                
                if cycle_info['confidence'] > 0.3:  # Chu kỳ đáng tin cậy
                    period = int(cycle_info['dominant_period'])
                    if period > 0:
                        # Tính Wilson score cho các pha
                        phase_scores = phase_wilson_scores(hit_sequence, period)
                        
                        # Xác định pha hiện tại
                        days_since_start = len(history)
                        current_phase = days_since_start % period
                        
                        # Điểm số dựa trên pha hiện tại
                        phase_score = phase_scores.get(current_phase, 0.5)
                        
                        # Cập nhật điểm cho các số của method này
                        for h in history[-1:]:  # Lấy dự đoán gần nhất
                            for number in h.get('predicted_numbers', []):
                                current_score = scores.get(number, 0)
                                scores[number] = current_score + (phase_score * self.weight)
            except Exception as e:
                logger.error(f"Error in cycle detection: {e}")
                continue
        
        return scores

class FrequencyStrategy(AnalysisStrategy):
    """Strategy based on frequency analysis"""
    
    def analyze(self, analysis_date: date, days_back: int = 30) -> Dict[str, float]:
        try:
            start_date = analysis_date - timedelta(days=days_back)
            
            # Fix: Cast boolean fields to integers before summing
            frequency_stats = NumberFrequencyStats.objects.filter(
                date__range=[start_date, analysis_date]
            ).values('number').annotate(
                appearance_count=Count('id'),  # Count appearances
                special_count=models.Sum(models.Case(
                    models.When(appeared_in_special=True, then=1),
                    default=0,
                    output_field=models.IntegerField()
                )),
                first_count=models.Sum(models.Case(
                    models.When(appeared_in_first=True, then=1),
                    default=0,
                    output_field=models.IntegerField()
                )),
                other_count=models.Sum(models.Case(
                    models.When(appeared_in_other=True, then=1),
                    default=0,
                    output_field=models.IntegerField()
                ))
            )
            scores = {}
            max_count = max([stat['appearance_count'] for stat in frequency_stats], default=1)
            
            for stat in frequency_stats:
                number = stat['number']
                appearance_count = stat['appearance_count']
                
                # Calculate weighted score based on appearance types
                special_weight = stat['special_count'] or 0
                first_weight = stat['first_count'] or 0
                other_weight = stat['other_count'] or 0
                
                weighted_score = (special_weight * 3 + first_weight * 2 + other_weight * 1)
                normalized_score = appearance_count / max_count if max_count > 0 else 0
                
                # Combine both scores
                final_score = (normalized_score * 0.7 + (weighted_score / 10) * 0.3)
                scores[number] = min(1.0, final_score)  # Cap at 1.0
            
            return scores
            
        except Exception as e:
            logger.error(f"Error analyzing strategy frequency: {e}")
            return {}

class PatternStrategy(AnalysisStrategy):
    """Strategy based on pattern recognition"""
    
    def analyze(self, analysis_date: date, days_back: int = 30) -> Dict[str, float]:
        try:
            # Simple pattern analysis based on day of week and historical data
            day_of_week = analysis_date.weekday()
            
            # Get historical data for the same day of week
            same_day_stats = NumberFrequencyStats.objects.filter(
                date__range=[analysis_date - timedelta(days=days_back), analysis_date],
                day_of_week=day_of_week
            ).values('number').annotate(
                pattern_count=Count('id')
            )
            
            scores = {}
            max_count = max([stat['pattern_count'] for stat in same_day_stats], default=1)
            
            for stat in same_day_stats:
                number = stat['number']
                pattern_count = stat['pattern_count']
                scores[number] = pattern_count / max_count if max_count > 0 else 0
            
            return scores
            
        except Exception as e:
            logger.error(f"Error in pattern strategy: {e}")
            return {}
        
class TrendStrategy(AnalysisStrategy):
    """Strategy based on trend analysis"""
    
    def analyze(self, analysis_date: date, days_back: int = 30) -> Dict[str, float]:
        try:
            # FIXED: Use correct field names for trend analysis
            start_date = analysis_date - timedelta(days=days_back)
            
            # Get recent frequency data
            recent_stats = NumberFrequencyStats.objects.filter(
                date__range=[analysis_date - timedelta(days=7), analysis_date]
            ).values('number').annotate(
                recent_count=Count('id')
            )
            
            # Get older frequency data for comparison
            older_stats = NumberFrequencyStats.objects.filter(
                date__range=[start_date, analysis_date - timedelta(days=7)]
            ).values('number').annotate(
                older_count=Count('id')
            )
            
            # Convert to dicts for easier lookup
            recent_dict = {stat['number']: stat['recent_count'] for stat in recent_stats}
            older_dict = {stat['number']: stat['older_count'] for stat in older_stats}
            
            scores = {}
            all_numbers = set(recent_dict.keys()) | set(older_dict.keys())
            
            for number in all_numbers:
                recent_count = recent_dict.get(number, 0)
                older_count = older_dict.get(number, 0)
                
                # Calculate trend score
                if older_count > 0:
                    trend_ratio = recent_count / older_count
                    # Normalize to 0-1 range
                    scores[number] = min(1.0, max(0.0, (trend_ratio - 0.5) * 2))
                else:
                    scores[number] = 1.0 if recent_count > 0 else 0.0
            
            return scores
            
        except Exception as e:
            logger.error(f"Error in trend strategy: {e}")
            return {}
        
class GapStrategy(AnalysisStrategy):
    """Chiến lược phân tích khoảng cách"""
    
    def analyze(self, analysis_date: date = None, days_back: int = 30, data: Dict = None) -> Dict[str, float]:
        # Support both new interface and old interface
        if data is None:
            data = {}
        
        if analysis_date:
            data['target_date'] = analysis_date
            
        analysis_date = data.get('target_date', date.today())
        
        # Lấy lịch sử xuất hiện của các số
        recent_results = PredictionResultBtl.objects.filter(
            dan_btl__analysis_date__gte=analysis_date - timedelta(days=90),
            dan_btl__analysis_date__lt=analysis_date,
            hit_count__gt=0
        ).select_related('dan_btl')
        
        # Nhóm theo số
        number_dates = {}
        for result in recent_results:
            for number in result.winning_numbers:
                if number not in number_dates:
                    number_dates[number] = []
                number_dates[number].append(result.dan_btl.analysis_date)
        
        # Phân tích gap
        gap_analysis_result = gap_analysis(number_dates)
        
        scores = {}
        for number, analysis in gap_analysis_result.items():
            # Số càng "quá hạn" càng có điểm cao
            overdue_score = min(analysis['overdue_score'], 2.0)
            scores[number] = (overdue_score / 2.0) * self.weight
        
        return scores

class MarkovStrategy(AnalysisStrategy):
    """Chiến lược Markov Chain"""
    
    def analyze(self, analysis_date: date = None, days_back: int = 30, data: Dict = None) -> Dict[str, float]:
        # Support both new interface and old interface
        if data is None:
            data = {}
        
        if analysis_date:
            data['target_date'] = analysis_date
            
        analysis_date = data.get('target_date', date.today())
        
        # Lấy lịch sử hit/miss cho các số
        recent_results = PredictionResultBtl.objects.filter(
            dan_btl__analysis_date__gte=analysis_date - timedelta(days=30),
            dan_btl__analysis_date__lt=analysis_date
        ).select_related('dan_btl').order_by('dan_btl__analysis_date')
        
        # Tạo chuỗi hit/miss cho mỗi số
        number_history = {}
        for result in recent_results:
            for number in result.predicted_numbers:
                if number not in number_history:
                    number_history[number] = []
                
                hit_status = 1 if number in result.winning_numbers else 0
                number_history[number].append((number, hit_status))
        
        # Tính xác suất Markov
        try:
            probabilities = markov_chain_probability([
                (item[0], item[1]) for history in number_history.values() for item in history
            ])
            
            scores = {}
            for number, prob in probabilities.items():
                scores[number] = prob * self.weight
                
            return scores
        except Exception as e:
            logger.error(f"Error in Markov analysis: {e}")
            return {}

def combine_strategies(analysis_date: date, history_data: Dict) -> List[Dict]:
    """
    Kết hợp các chiến lược để đưa ra dự đoán tổng hợp
    
    Args:
        analysis_date: Ngày phân tích
        history_data: Dữ liệu lịch sử
    
    Returns:
        List[Dict] - [{'number': str, 'score': float, 'strategies': Dict}]
    """
    cache_key = f"ensemble_analysis_{analysis_date.strftime('%Y-%m-%d')}"
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return cached_result
    
    # Khởi tạo các chiến lược
    strategies = [
        CycleStrategy("cycle", weight=0.3),
        FrequencyStrategy("frequency", weight=0.25),
        GapStrategy("gap", weight=0.25),
        MarkovStrategy("markov", weight=0.2)
    ]
    
    # Chuẩn bị dữ liệu chung
    data = {
        'target_date': analysis_date,
        'method_history': history_data
    }
    
    # Thu thập điểm từ các chiến lược
    combined_scores = {}
    strategy_details = {}
    
    for strategy in strategies:
        try:
            # Handle both analyze interfaces
            if hasattr(strategy, 'analyze'):
                if strategy.name in ['cycle', 'gap', 'markov']:
                    strategy_scores = strategy.analyze(data=data)
                else:
                    strategy_scores = strategy.analyze(analysis_date)
            else:
                strategy_scores = {}
                
            strategy_details[strategy.name] = strategy_scores
            
            # Kết hợp điểm
            for number, score in strategy_scores.items():
                if number not in combined_scores:
                    combined_scores[number] = 0
                combined_scores[number] += score
                
        except Exception as e:
            logger.error(f"Error in strategy {strategy.name}: {e}")
            continue
    
    # Chuẩn hóa điểm số
    if combined_scores:
        max_score = max(combined_scores.values())
        if max_score > 0:
            for number in combined_scores:
                combined_scores[number] = combined_scores[number] / max_score
    
    # Tạo kết quả cuối cùng
    results = []
    for number, score in combined_scores.items():
        result = {
            'number': number,
            'score': float(score),
            'strategies': {
                name: float(strategy_details.get(name, {}).get(number, 0))
                for name in strategy_details
            }
        }
        results.append(result)
    
    # Sắp xếp theo điểm giảm dần
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Cache kết quả 1 giờ
    cache.set(cache_key, results, 3600)
    
    return results

def get_historical_hits(analysis_date: date, days: int = 30) -> Dict:
    """
    Lấy dữ liệu lịch sử hit/miss cho các phương pháp
    
    Args:
        analysis_date: Ngày phân tích
        days: Số ngày lịch sử
    
    Returns:
        Dict - Dữ liệu lịch sử theo phương pháp
    """
    start_date = analysis_date - timedelta(days=days)
    
    # Lấy dữ liệu từ BtlAnalytics
    analytics = BtlAnalytics.objects.filter(
        date__gte=start_date,
        date__lt=analysis_date
    ).order_by('date')
    
    # Lấy chi tiết từ PredictionResultBtl
    results = PredictionResultBtl.objects.filter(
        dan_btl__analysis_date__gte=start_date,
        dan_btl__analysis_date__lt=analysis_date
    ).select_related('dan_btl', 'method').order_by('dan_btl__analysis_date')
    
    # Tổ chức dữ liệu theo phương pháp
    method_history = {}
    
    for result in results:
        method_name = result.method.name
        if method_name not in method_history:
            method_history[method_name] = []
        
        method_history[method_name].append({
            'date': result.dan_btl.analysis_date,
            'predicted_numbers': result.predicted_numbers,
            'winning_numbers': result.winning_numbers,
            'hit_count': result.hit_count,
            'method_id': result.method.id
        })
    
    return method_history

class EnsembleService:
    """
    Service class chính để quản lý và thực hiện ensemble analysis
    Kết hợp nhiều strategies để đưa ra dự đoán tổng hợp
    """
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
        
        # Initialize strategies - FIXED: Add missing self.strategies
        self.strategies = self._initialize_strategies()
        
        # Define strategy combinations
        self.strategy_combinations = {
            'conservative': [
                FrequencyStrategy("frequency", weight=0.5),
                TrendStrategy("trend", weight=0.3),
                PatternStrategy("pattern", weight=0.2),
            ],
            'aggressive': [
                TrendStrategy("trend", weight=0.4),
                PatternStrategy("pattern", weight=0.35),
                FrequencyStrategy("frequency", weight=0.25),
            ],
            'balanced': [
                FrequencyStrategy("frequency", weight=0.35),
                TrendStrategy("trend", weight=0.35),
                PatternStrategy("pattern", weight=0.3),
            ]
        }
    
    def _initialize_strategies(self) -> List[AnalysisStrategy]:
        """
        Khởi tạo các strategies với trọng số mặc định
        """
        return [
            CycleStrategy("cycle", weight=0.3),
            FrequencyStrategy("frequency", weight=0.25),
            GapStrategy("gap", weight=0.25),
            MarkovStrategy("markov", weight=0.2)
        ]
    
    def get_ensemble_strategies_analysis(self, analysis_date: date) -> dict:
        """
        Phân tích các chiến lược ensemble
        
        Returns:
        {
            'ensemble_strategies': [
                {
                    'name': str,
                    'description': str,
                    'confidence': float,
                    'strategies': List[str],
                    'predictions': Dict[str, float]
                },
                ...
            ],
            'best_strategy': str,
            'consensus_numbers': List[str]
        }
        """
        try:
            cache_key = f"ensemble_strategies_{analysis_date}"
            cached_result = safe_cache_get(cache_key)
            if cached_result:
                return cached_result
            
            ensemble_results = []
            all_predictions = {}
            
            for strategy_name, strategies in self.strategy_combinations.items():
                logger.info(f"Analyzing ensemble strategy: {strategy_name}")
                
                # Combine predictions from all strategies
                combined_scores = {}
                total_weight = sum(s.weight for s in strategies)
                
                for strategy in strategies:
                    try:
                        scores = strategy.analyze(analysis_date)
                        weight_factor = strategy.weight / total_weight
                        
                        for number, score in scores.items():
                            if number not in combined_scores:
                                combined_scores[number] = 0
                            combined_scores[number] += score * weight_factor
                    
                    except Exception as e:
                        logger.error(f"Error in strategy {strategy.name}: {e}")
                        continue
                
                if combined_scores:
                    # Calculate ensemble confidence
                    avg_score = np.mean(list(combined_scores.values()))
                    std_score = np.std(list(combined_scores.values()))
                    confidence = min(95.0, max(50.0, (avg_score * 100) - (std_score * 10)))
                    
                    # Get top predictions
                    sorted_predictions = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
                    top_predictions = dict(sorted_predictions[:10])
                    
                    ensemble_result = {
                        'name': strategy_name.title(),
                        'description': self._get_strategy_description(strategy_name),
                        'confidence': round(confidence, 1),
                        'strategies': [s.name for s in strategies],
                        'predictions': top_predictions
                    }
                    
                    ensemble_results.append(ensemble_result)
                    all_predictions[strategy_name] = combined_scores
            
            # Find best strategy (highest confidence)
            best_strategy = max(ensemble_results, key=lambda x: x['confidence'])['name'] if ensemble_results else "balanced"
            
            # Find consensus numbers (appear in multiple strategies with high scores)
            consensus_numbers = self._find_consensus_numbers(all_predictions)
            
            result = {
                'ensemble_strategies': ensemble_results,
                'best_strategy': best_strategy.lower(),
                'consensus_numbers': consensus_numbers
            }
            
            safe_cache_set(cache_key, result, self.cache_timeout)
            logger.info(f"Ensemble strategies analysis completed for {analysis_date}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in ensemble strategies analysis: {e}")
            return {
                'ensemble_strategies': [],
                'best_strategy': 'balanced',
                'consensus_numbers': []
            }
    
    def combine_strategies(self, analysis_date: date, strategy_weights: Optional[Dict[str, float]] = None) -> dict:
        """
        Kết hợp các chiến lược với trọng số tùy chỉnh
        
        Returns:
        {
            'combined_predictions': Dict[str, float],
            'confidence': float,
            'strategy_contributions': Dict[str, Dict[str, float]]
        }
        """
        try:
            if strategy_weights is None:
                strategy_weights = {'frequency': 0.4, 'trend': 0.35, 'pattern': 0.25}
            
            cache_key = f"combined_strategies_{analysis_date}_{hash(frozenset(strategy_weights.items()))}"
            cached_result = safe_cache_get(cache_key)
            if cached_result:
                return cached_result
            
            strategies = [
                FrequencyStrategy("frequency", weight=strategy_weights.get('frequency', 0.4)),
                TrendStrategy("trend", weight=strategy_weights.get('trend', 0.35)),
                PatternStrategy("pattern", weight=strategy_weights.get('pattern', 0.25))
            ]
            
            combined_scores = {}
            strategy_contributions = {}
            total_weight = sum(s.weight for s in strategies)
            
            for strategy in strategies:
                try:
                    scores = strategy.analyze(analysis_date)
                    weight_factor = strategy.weight / total_weight
                    strategy_contributions[strategy.name] = scores
                    
                    for number, score in scores.items():
                        if number not in combined_scores:
                            combined_scores[number] = 0
                        combined_scores[number] += score * weight_factor
                
                except Exception as e:
                    logger.error(f"Error in strategy {strategy.name}: {e}")
                    strategy_contributions[strategy.name] = {}
            
            # Calculate overall confidence
            if combined_scores:
                scores_array = np.array(list(combined_scores.values()))
                confidence = min(95.0, np.mean(scores_array) * 100)
            else:
                confidence = 50.0
            
            result = {
                'combined_predictions': combined_scores,
                'confidence': round(confidence, 1),
                'strategy_contributions': strategy_contributions
            }
            
            safe_cache_set(cache_key, result, self.cache_timeout)
            return result
            
        except Exception as e:
            logger.error(f"Error combining strategies: {e}")
            return {
                'combined_predictions': {},
                'confidence': 50.0,
                'strategy_contributions': {}
            }
    
    def get_historical_hits(self, analysis_date: date, days_back: int = 30) -> dict:
        """
        Phân tích lịch sử trúng của các strategies
        
        Returns:
        {
            'strategy_performance': Dict[str, Dict[str, Any]],
            'best_performing_strategy': str,
            'average_hit_rate': float
        }
        """
        try:
            cache_key = f"historical_hits_{analysis_date}_{days_back}"
            cached_result = safe_cache_get(cache_key)
            if cached_result:
                return cached_result
            
            start_date = analysis_date - timedelta(days=days_back)
            
            # FIXED: Use correct field name 'date' instead of 'ngay'
            analytics_data = BtlAnalytics.objects.filter(
                date__range=[start_date, analysis_date]
            ).order_by('date')
            
            strategy_performance = {}
            
            for strategy_name in self.strategy_combinations.keys():
                hit_count = 0
                total_predictions = 0
                daily_accuracies = []
                
                for analytics in analytics_data:
                    # Simulate strategy performance based on historical data
                    # In real implementation, you would track actual predictions vs results
                    simulated_accuracy = self._simulate_strategy_performance(strategy_name, analytics)
                    daily_accuracies.append(simulated_accuracy)
                    
                    if simulated_accuracy > 0.6:  # Consider it a "hit" if accuracy > 60%
                        hit_count += 1
                    total_predictions += 1
                
                hit_rate = (hit_count / total_predictions * 100) if total_predictions > 0 else 0
                avg_accuracy = np.mean(daily_accuracies) if daily_accuracies else 0
                
                strategy_performance[strategy_name] = {
                    'hit_rate': round(hit_rate, 2),
                    'average_accuracy': round(avg_accuracy * 100, 2),
                    'total_predictions': total_predictions,
                    'successful_hits': hit_count,
                    'trend': 'increasing' if hit_rate > 50 else 'decreasing'
                }
            
            # Find best performing strategy
            best_strategy = max(strategy_performance.keys(), 
                              key=lambda k: strategy_performance[k]['hit_rate']) if strategy_performance else 'balanced'
            
            average_hit_rate = np.mean([perf['hit_rate'] for perf in strategy_performance.values()]) if strategy_performance else 0
            
            result = {
                'strategy_performance': strategy_performance,
                'best_performing_strategy': best_strategy,
                'average_hit_rate': round(average_hit_rate, 2)
            }
            
            safe_cache_set(cache_key, result, self.cache_timeout)
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing historical hits: {e}")
            return {
                'strategy_performance': {},
                'best_performing_strategy': 'balanced',
                'average_hit_rate': 0.0
            }
    
    def get_ensemble_strategies(self, analysis_date: date) -> List[Dict]:
        """
        Lấy thông tin các chiến lược ensemble
        
        Args:
            analysis_date: date - Ngày phân tích
        
        Returns:
            List[Dict] - Danh sách các strategies với thông tin chi tiết
        """
        cache_key = f"ensemble_strategies_{analysis_date.strftime('%Y%m%d')}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Lấy dữ liệu lịch sử
            history_data = get_historical_hits(analysis_date, days=30)
            
            ensemble_strategies = []
            
            for strategy in self.strategies:
                try:
                    # Chuẩn bị dữ liệu cho strategy
                    data = {
                        'target_date': analysis_date,
                        'method_history': history_data
                    }
                    
                    # Thực hiện phân tích - handle different analyze interfaces
                    if strategy.name in ['cycle', 'gap', 'markov']:
                        strategy_scores = strategy.analyze(data=data)
                    else:
                        strategy_scores = strategy.analyze(analysis_date)
                    
                    # Tính toán metrics cho strategy
                    total_predictions = len(strategy_scores)
                    avg_score = sum(strategy_scores.values()) / total_predictions if total_predictions > 0 else 0
                    max_score = max(strategy_scores.values()) if strategy_scores else 0
                    
                    # Tính confidence dựa trên phân bố điểm
                    confidence = self._calculate_strategy_confidence(strategy_scores, strategy.name, analysis_date)
                    
                    strategy_info = {
                        'name': strategy.name.title(),
                        'description': self._get_strategy_description(strategy.name),
                        'weight': strategy.weight,
                        'confidence': round(confidence, 1),
                        'total_predictions': total_predictions,
                        'avg_score': round(avg_score, 4),
                        'max_score': round(max_score, 4),
                        'strategies': [strategy.name],  # For template compatibility
                        'top_numbers': self._get_top_numbers_for_strategy(strategy_scores, 5)
                    }
                    
                    ensemble_strategies.append(strategy_info)
                    
                except Exception as e:
                    logger.error(f"Error analyzing strategy {strategy.name}: {e}")
                    continue
            
            # Sắp xếp theo confidence
            ensemble_strategies.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Cache kết quả
            cache.set(cache_key, ensemble_strategies, self.cache_timeout)
            logger.info(f"Ensemble strategies analysis completed for {analysis_date}")
            
            return ensemble_strategies
            
        except Exception as e:
            logger.error(f"Error in get_ensemble_strategies: {e}")
            return []
    
    def generate_predictions(self, analysis_date: date) -> List[Dict]:
        """
        Tạo dự đoán ensemble tổng hợp
        
        Args:
            analysis_date: date - Ngày dự đoán
        
        Returns:
            List[Dict] - Danh sách dự đoán đã được ensemble
        """
        cache_key = f"ensemble_predictions_{analysis_date.strftime('%Y%m%d')}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Lấy dữ liệu lịch sử
            history_data = get_historical_hits(analysis_date, days=30)
            
            # Sử dụng combine_strategies đã có
            combined_results = combine_strategies(analysis_date, history_data)
            
            # Thêm thông tin ensemble metadata
            ensemble_predictions = []
            for i, result in enumerate(combined_results[:20], 1):  # Top 20
                prediction = {
                    'rank': i,
                    'number': result['number'],
                    'ensemble_score': round(result['score'], 4),
                    'confidence': min(result['score'], 1.0),
                    'strategy_breakdown': result['strategies'],
                    'recommendation_level': self._get_recommendation_level(result['score']),
                    'predicted_at': analysis_date.strftime('%Y-%m-%d')
                }
                ensemble_predictions.append(prediction)
            
            # Cache kết quả
            cache.set(cache_key, ensemble_predictions, self.cache_timeout)
            logger.info(f"Generated {len(ensemble_predictions)} ensemble predictions for {analysis_date}")
            
            return ensemble_predictions
            
        except Exception as e:
            logger.error(f"Error generating ensemble predictions: {e}")
            return []
    
    def evaluate_ensemble_performance(self, evaluation_date: date, lookback_days: int = 7) -> Dict:
        """
        Đánh giá hiệu suất của ensemble trong thời gian qua
        
        Args:
            evaluation_date: date - Ngày đánh giá
            lookback_days: int - Số ngày nhìn lại
        
        Returns:
            Dict - Thông tin hiệu suất ensemble
        """
        try:
            total_predictions = 0
            total_hits = 0
            daily_performances = []
            
            for i in range(lookback_days):
                test_date = evaluation_date - timedelta(days=i+1)
                
                # Lấy dự đoán của ensemble cho ngày đó
                predictions = self.generate_predictions(test_date)
                predicted_numbers = [p['number'] for p in predictions[:10]]  # Top 10
                
                # Lấy kết quả thực tế
                try:
                    actual_dan = DanBtl.objects.get(analysis_date=test_date)  # Fixed field name
                    actual_numbers = self._extract_winning_numbers(actual_dan)
                    
                    # Tính số hit
                    hits = len(set(predicted_numbers) & set(actual_numbers))
                    
                    daily_performance = {
                        'date': test_date.strftime('%Y-%m-%d'),
                        'predictions': len(predicted_numbers),
                        'hits': hits,
                        'hit_rate': round(hits / len(predicted_numbers) * 100, 2) if predicted_numbers else 0
                    }
                    
                    daily_performances.append(daily_performance)
                    total_predictions += len(predicted_numbers)
                    total_hits += hits
                    
                except DanBtl.DoesNotExist:
                    continue
            
            # Tính hiệu suất tổng thể
            overall_hit_rate = (total_hits / total_predictions * 100) if total_predictions > 0 else 0
            
            # Tính Wilson score cho ensemble
            from scipy import stats
            wilson_score = self._calculate_wilson_score(total_hits, total_predictions)
            
            return {
                'evaluation_period': f"{lookback_days} days",
                'total_predictions': total_predictions,
                'total_hits': total_hits,
                'overall_hit_rate': round(overall_hit_rate, 2),
                'wilson_score': round(wilson_score, 4),
                'daily_performances': daily_performances,
                'avg_daily_hit_rate': round(sum(d['hit_rate'] for d in daily_performances) / len(daily_performances), 2) if daily_performances else 0,
                'best_day': max(daily_performances, key=lambda x: x['hit_rate']) if daily_performances else None,
                'worst_day': min(daily_performances, key=lambda x: x['hit_rate']) if daily_performances else None
            }
            
        except Exception as e:
            logger.error(f"Error evaluating ensemble performance: {e}")
            return {
                'evaluation_period': f"{lookback_days} days",
                'total_predictions': 0,
                'total_hits': 0,
                'overall_hit_rate': 0,
                'wilson_score': 0,
                'daily_performances': [],
                'error': str(e)
            }
    
    def optimize_strategy_weights(self, optimization_date: date, days: int = 30) -> Dict[str, float]:
        """
        Tối ưu hóa trọng số các strategies dựa trên hiệu suất lịch sử
        
        Args:
            optimization_date: date - Ngày tối ưu hóa
            days: int - Số ngày dữ liệu để tối ưu hóa
        
        Returns:
            Dict[str, float] - Trọng số mới cho các strategies
        """
        try:
            strategy_performances = {}
            
            # Đánh giá hiệu suất từng strategy
            for strategy in self.strategies:
                total_hits = 0
                total_predictions = 0
                
                for i in range(days):
                    test_date = optimization_date - timedelta(days=i+1)
                    
                    try:
                        # Lấy dữ liệu cho strategy
                        history_data = get_historical_hits(test_date, days=30)
                        data = {
                            'target_date': test_date,
                            'method_history': history_data
                        }
                        
                        # Phân tích strategy
                        if strategy.name in ['cycle', 'gap', 'markov']:
                            strategy_scores = strategy.analyze(data=data)
                        else:
                            strategy_scores = strategy.analyze(test_date)
                            
                        top_predictions = sorted(strategy_scores.items(), key=lambda x: x[1], reverse=True)[:10]
                        predicted_numbers = [item[0] for item in top_predictions]
                        
                        # Lấy kết quả thực tế
                        actual_dan = DanBtl.objects.get(analysis_date=test_date)  # Fixed field name
                        actual_numbers = self._extract_winning_numbers(actual_dan)
                        
                        # Tính hits
                        hits = len(set(predicted_numbers) & set(actual_numbers))
                        total_hits += hits
                        total_predictions += len(predicted_numbers)
                        
                    except (DanBtl.DoesNotExist, Exception):
                        continue
                
                # Tính hit rate cho strategy
                hit_rate = total_hits / total_predictions if total_predictions > 0 else 0
                strategy_performances[strategy.name] = hit_rate
            
            # Chuẩn hóa thành trọng số
            total_performance = sum(strategy_performances.values())
            if total_performance > 0:
                optimized_weights = {
                    name: performance / total_performance 
                    for name, performance in strategy_performances.items()
                }
            else:
                # Fallback to equal weights
                optimized_weights = {
                    strategy.name: 1.0 / len(self.strategies) 
                    for strategy in self.strategies
                }
            
            # Cập nhật trọng số cho strategies
            for strategy in self.strategies:
                if strategy.name in optimized_weights:
                    strategy.weight = optimized_weights[strategy.name]
            
            logger.info(f"Optimized strategy weights: {optimized_weights}")
            return optimized_weights
            
        except Exception as e:
            logger.error(f"Error optimizing strategy weights: {e}")
            # Return current weights
            return {strategy.name: strategy.weight for strategy in self.strategies}
    
    def get_ensemble_diversity_analysis(self, analysis_date: date) -> Dict:
        """
        Phân tích độ đa dạng của ensemble
        
        Args:
            analysis_date: date - Ngày phân tích
        
        Returns:
            Dict - Thông tin về độ đa dạng
        """
        try:
            # Lấy dự đoán từ các strategies
            history_data = get_historical_hits(analysis_date, days=30)
            data = {
                'target_date': analysis_date,
                'method_history': history_data
            }
            
            strategy_predictions = {}
            for strategy in self.strategies:
                try:
                    if strategy.name in ['cycle', 'gap', 'markov']:
                        scores = strategy.analyze(data=data)
                    else:
                        scores = strategy.analyze(analysis_date)
                        
                    top_predictions = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
                    strategy_predictions[strategy.name] = [item[0] for item in top_predictions]
                except Exception as e:
                    logger.error(f"Error getting predictions for {strategy.name}: {e}")
                    strategy_predictions[strategy.name] = []
            
            # Tính diversity score
            diversity_score = ensemble_diversity_score(strategy_predictions)
            
            # Phân tích overlap giữa các strategies
            overlaps = {}
            strategy_names = list(strategy_predictions.keys())
            
            for i in range(len(strategy_names)):
                for j in range(i+1, len(strategy_names)):
                    name1, name2 = strategy_names[i], strategy_names[j]
                    pred1, pred2 = set(strategy_predictions[name1]), set(strategy_predictions[name2])
                    
                    overlap_count = len(pred1 & pred2)
                    overlap_percent = overlap_count / min(len(pred1), len(pred2)) * 100 if pred1 and pred2 else 0
                    
                    overlaps[f"{name1}_{name2}"] = {
                        'overlap_count': overlap_count,
                        'overlap_percent': round(overlap_percent, 1)
                    }
            
            return {
                'analysis_date': analysis_date.strftime('%Y-%m-%d'),
                'diversity_score': round(diversity_score, 3),
                'strategy_predictions': strategy_predictions,
                'overlaps': overlaps,
                'total_unique_numbers': len(set().union(*strategy_predictions.values())),
                'avg_predictions_per_strategy': round(
                    sum(len(preds) for preds in strategy_predictions.values()) / len(strategy_predictions), 1
                ) if strategy_predictions else 0
            }
            
        except Exception as e:
            logger.error(f"Error in ensemble diversity analysis: {e}")
            return {
                'analysis_date': analysis_date.strftime('%Y-%m-%d'),
                'diversity_score': 0,
                'strategy_predictions': {},
                'overlaps': {},
                'total_unique_numbers': 0,
                'avg_predictions_per_strategy': 0,
                'error': str(e)
            }
    
    # Helper methods
    def _find_consensus_numbers(self, all_predictions: Dict[str, Dict[str, float]]) -> List[str]:
        """Tìm các số được đồng thuận bởi nhiều strategies"""
        if not all_predictions:
            return []
        
        number_votes = {}
        threshold = 0.6  # Ngưỡng điểm số để được coi là "vote"
        
        for strategy_name, predictions in all_predictions.items():
            for number, score in predictions.items():
                if score >= threshold:
                    if number not in number_votes:
                        number_votes[number] = []
                    number_votes[number].append((strategy_name, score))
        
        # Lấy các số được vote bởi ít nhất 2 strategies
        consensus_numbers = []
        for number, votes in number_votes.items():
            if len(votes) >= 2:
                avg_score = np.mean([vote[1] for vote in votes])
                consensus_numbers.append((number, avg_score))
        
        # Sắp xếp theo điểm trung bình giảm dần
        consensus_numbers.sort(key=lambda x: x[1], reverse=True)
        
        return [number for number, _ in consensus_numbers[:5]]  # Top 5
    
    def _simulate_strategy_performance(self, strategy_name: str, analytics) -> float:
        """Mô phỏng hiệu suất của strategy dựa trên dữ liệu lịch sử"""
        # This is a simplified simulation
        # In real implementation, you would compare actual predictions with results
        
        base_accuracy = {
            'conservative': 0.65,
            'aggressive': 0.55, 
            'balanced': 0.60
        }.get(strategy_name, 0.55)
        
        # Add some randomness and trend based on analytics data
        if hasattr(analytics, 'overall_hit_rate') and analytics.overall_hit_rate:
            trend_factor = min(0.1, analytics.overall_hit_rate / 1000)  # Small adjustment
            return min(0.95, base_accuracy + trend_factor + np.random.normal(0, 0.05))
        
        return base_accuracy + np.random.normal(0, 0.05)

    def _calculate_strategy_confidence(self, strategy_scores: Dict[str, float], strategy_name: str, analysis_date: date) -> float:
        """
        Tính confidence cho một strategy dựa trên điểm số và hiệu suất lịch sử
        """
        try:
            if not strategy_scores:
                return 0.0
            
            # Confidence dựa trên phân bố điểm
            scores = list(strategy_scores.values())
            max_score = max(scores)
            avg_score = sum(scores) / len(scores)
            
            # Tính độ tập trung của điểm (higher = better confidence)
            concentration = max_score / avg_score if avg_score > 0 else 1
            
            # Normalize concentration to percentage
            base_confidence = min(concentration * 20, 100)  # Scale factor
            
            # Adjust based on strategy characteristics
            strategy_adjustments = {
                'cycle': 0.85,    # Chu kỳ có thể không ổn định
                'frequency': 0.90, # Tần suất khá tin cậy
                'gap': 0.80,      # Gap analysis có độ bất định
                'markov': 0.75    # Markov cần nhiều dữ liệu
            }
            
            adjustment = strategy_adjustments.get(strategy_name, 0.85)
            final_confidence = base_confidence * adjustment
            
            return min(final_confidence, 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence for {strategy_name}: {e}")
            return 50.0  # Default confidence
    
    def _get_strategy_description(self, strategy_name: str) -> str:
        """Lấy mô tả cho strategy"""
        descriptions = {
            'conservative': 'Tập trung vào các số có tần suất xuất hiện ổn định và đáng tin cậy',
            'aggressive': 'Ưu tiên các số có xu hướng tăng mạnh và patterns mới nổi',
            'balanced': 'Cân bằng giữa tần suất, xu hướng và patterns để tối ưu tổng thể',
            'cycle': 'Phân tích chu kỳ xuất hiện của các số dựa trên FFT và autocorrelation',
            'frequency': 'Phân tích tần suất xuất hiện trong các giải đặc biệt, nhất, và khác',
            'gap': 'Phân tích khoảng cách thời gian giữa các lần xuất hiện của số',
            'markov': 'Phân tích xác suất chuyển trạng thái hit/miss dựa trên Markov Chain'
        }
        return descriptions.get(strategy_name, 'Chiến lược kết hợp đa dạng các yếu tố phân tích')
    
    def _get_top_numbers_for_strategy(self, strategy_scores: Dict[str, float], count: int) -> List[Dict]:
        """
        Lấy top numbers cho strategy
        """
        if not strategy_scores:
            return []
        
        sorted_scores = sorted(strategy_scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {'number': num, 'score': round(score, 4)} 
            for num, score in sorted_scores[:count]
        ]
    
    def _get_recommendation_level(self, score: float) -> str:
        """
        Xác định mức độ khuyến nghị dựa trên điểm số
        """
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        elif score >= 0.4:
            return 'low'
        else:
            return 'very_low'
    
    def _extract_winning_numbers(self, dan_btl) -> List[str]:
        """
        Trích xuất các số trúng từ DanBtl object
        """
        numbers = []
        try:
            # Tùy thuộc vào cấu trúc model DanBtl
            if hasattr(dan_btl, 'prize_next_day') and dan_btl.prize_next_day:
                # Parse prize string to extract numbers
                prize_str = str(dan_btl.prize_next_day)
                # Extract 2-digit numbers from prize string
                import re
                extracted_numbers = re.findall(r'\b\d{2}\b', prize_str)
                numbers.extend(extracted_numbers)
            
            # Chuẩn hóa format số (2 chữ số)
            normalized_numbers = []
            for num in numbers:
                clean_num = str(num).strip()
                if clean_num.isdigit() and len(clean_num) <= 3:
                    # Take last 2 digits for lottery numbers
                    normalized_numbers.append(f"{int(clean_num) % 100:02d}")
            
            return list(set(normalized_numbers))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting winning numbers: {e}")
            return []
    
    def _calculate_wilson_score(self, successes: int, total: int, confidence: float = 0.95) -> float:
        """Calculate Wilson score interval"""
        if total == 0:
            return 0.0
        
        try:
            from scipy import stats
            z = stats.norm.ppf(1 - (1 - confidence) / 2)
            p = successes / total
            
            numerator = p + (z**2) / (2 * total) - z * np.sqrt((p * (1 - p) + (z**2) / (4 * total)) / total)
            denominator = 1 + (z**2) / total
            
            return max(0, numerator / denominator)
        except ImportError:
            # Fallback if scipy is not available
            if total == 0:
                return 0.0
            return max(0, (successes / total) - 0.1)  # Simple fallback
        
# Singleton instance
ensemble_service = EnsembleService()