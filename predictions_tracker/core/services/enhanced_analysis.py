import logging
import numpy as np
from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional
from django.db.models import Avg, Count, Q
from predictions_tracker.models import TrackingEvaluation, PredictionMethod, DailyTrackingSession

logger = logging.getLogger(__name__)

# ✅ CONFIGURATION BASED ON YOUR REQUIREMENTS
class EnhancedAnalysisConfig:
    # Business Logic Thresholds
    GOOD_HIT_RATE_THRESHOLD = 50.0  # >50% is good
    MIN_DATA_POINTS = 30  # Minimum 30 data points for reliability
    SUSPICIOUS_LOW_HIT_RATE = 20.0  # <20% is suspicious
    
    # Enhanced Scoring Weights
    DATA_QUALITY_WEIGHT = 0.30
    RECENT_RELEVANCE_WEIGHT = 0.25
    PATTERN_CONSISTENCY_WEIGHT = 0.20
    RISK_ASSESSMENT_WEIGHT = 0.15
    WILSON_SCORE_WEIGHT = 0.10
    
    # Confidence Levels
    HIGH_CONFIDENCE_THRESHOLD = 0.7
    MEDIUM_CONFIDENCE_THRESHOLD = 0.5
    LOW_CONFIDENCE_THRESHOLD = 0.3

class EnhancedMethodAnalyzer:
    """
    ✅ ENHANCED METHOD ANALYZER - Song song với existing system
    """
    
    def __init__(self):
        self.config = EnhancedAnalysisConfig()
        
    def analyze_methods_enhanced(self, start_date: date, end_date: date, 
                                target_limit: int = 15) -> Dict:
        """
        ✅ MAIN ENHANCED ANALYSIS FUNCTION
        """
        try:
            # Step 1: Get historical data from TrackingEvaluation
            historical_data = self._build_historical_data(start_date, end_date)
            
            # Step 2: Enhanced method selection
            qualified_methods = self._enhanced_method_selection(
                historical_data, end_date, target_limit
            )
            
            # Step 3: Detailed analysis for qualified methods
            analysis_results = self._detailed_method_analysis(qualified_methods, end_date)
            
            return {
                'enhanced_analysis': analysis_results,
                'metadata': {
                    'total_methods_analyzed': len(historical_data),
                    'qualified_methods': len(qualified_methods),
                    'analysis_date': end_date.isoformat(),
                    'data_range': f"{start_date} to {end_date}"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced analysis failed: {e}")
            # ✅ ALERT when enhanced analysis fails
            self._send_analysis_failure_alert(e)
            raise
    
    def _build_historical_data(self, start_date: date, end_date: date) -> Dict:
        """
        ✅ BUILD HISTORICAL DATA từ TrackingEvaluation với đầy đủ context
        """
        evaluations = (
            TrackingEvaluation.objects.filter(
                evaluation_date__range=[start_date, end_date]
            )
            .select_related("method_result__method", "method_result__session")
            .order_by("evaluation_date")  # ✅ Ordered by time
        )
        
        historical_data = {}
        
        for eval_obj in evaluations:
            method_id = eval_obj.method_result.method.id
            
            # ✅ Calculate tracking_day from dates
            prediction_date = eval_obj.method_result.session.prediction_date
            evaluation_date = eval_obj.evaluation_date
            tracking_day = min(max((evaluation_date - prediction_date).days, 1), 3)
            
            if method_id not in historical_data:
                historical_data[method_id] = {
                    'method': eval_obj.method_result.method,
                    'evaluations': [],
                    'day_1_data': [],
                    'day_2_data': [],
                    'day_3_data': []
                }
            
            # ✅ Store full evaluation context
            eval_data = {
                'evaluation_date': evaluation_date,
                'prediction_date': prediction_date,
                'tracking_day': tracking_day,
                'hit_rate': eval_obj.hit_rate,
                'hit_count': eval_obj.hit_count,
                'wilson_score': eval_obj.wilson_score,
                'hit_numbers': eval_obj.hit_numbers
            }
            
            historical_data[method_id]['evaluations'].append(eval_data)
            
            # ✅ Group by tracking day for analysis
            if tracking_day == 1:
                historical_data[method_id]['day_1_data'].append(eval_data)
            elif tracking_day == 2:
                historical_data[method_id]['day_2_data'].append(eval_data)
            elif tracking_day == 3:
                historical_data[method_id]['day_3_data'].append(eval_data)
        
        logger.info(f"✅ Built historical data for {len(historical_data)} methods")
        return historical_data
    
    def _enhanced_method_selection(self, historical_data: Dict, analysis_date: date, 
                                  target_limit: int) -> Dict:
        """
        ✅ ENHANCED METHOD SELECTION với comprehensive criteria
        """
        method_candidates = {}
        
        for method_id, method_data in historical_data.items():
            try:
                method = method_data['method']
                evaluations = method_data['evaluations']
                
                # ✅ 1. DATA QUALITY ASSESSMENT
                data_quality_score = self._calculate_data_quality_score(method_data)
                
                if data_quality_score < 0.6:  # Minimum threshold
                    continue
                
                # ✅ 2. RECENT PERFORMANCE RELEVANCE
                recent_relevance_score = self._calculate_recent_relevance_score(method_data)
                
                # ✅ 3. PATTERN CONSISTENCY ANALYSIS
                pattern_consistency = self._analyze_pattern_consistency(method_data)
                
                # ✅ 4. WILSON SCORE INTEGRATION
                wilson_score_avg = self._calculate_wilson_score_average(method_data)
                
                # ✅ 5. COMPOSITE SCORING
                composite_score = self._calculate_composite_score(
                    data_quality_score, recent_relevance_score, 
                    pattern_consistency, wilson_score_avg, method_data
                )
                
                # ✅ 6. VALIDATION
                validation_result = self._validate_method_for_analysis(method_data, analysis_date)
                
                if not validation_result['is_valid']:
                    continue
                
                method_candidates[method_id] = {
                    'method': method,
                    'composite_score': composite_score,
                    'data_quality_score': data_quality_score,
                    'recent_relevance_score': recent_relevance_score,
                    'pattern_consistency': pattern_consistency,
                    'wilson_score_avg': wilson_score_avg,
                    'validation_details': validation_result,
                    'method_data': method_data
                }
                
            except Exception as e:
                logger.error(f"❌ Error processing method {method_id}: {e}")
                continue
        
        # ✅ Sort by composite score
        sorted_candidates = dict(sorted(
            method_candidates.items(),
            key=lambda x: x[1]['composite_score'],
            reverse=True
        )[:target_limit])
        
        logger.info(f"✅ Selected {len(sorted_candidates)} qualified methods from {len(historical_data)}")
        return sorted_candidates
    
    def _calculate_data_quality_score(self, method_data: Dict) -> float:
        """
        ✅ DATA QUALITY SCORE based on your requirements
        """
        day_1_data = method_data['day_1_data']
        all_evaluations = method_data['evaluations']
        
        if len(day_1_data) < self.config.MIN_DATA_POINTS:
            return 0.0
        
        # 1. Volume Score (0-0.4)
        volume_score = min(0.4, len(day_1_data) / 50.0)
        
        # 2. Diversity Score (0-0.3) - Avoid single-class data
        hit_rates = [eval_data['hit_rate'] for eval_data in day_1_data]
        unique_hit_rates = len(set([round(hr, 1) for hr in hit_rates]))
        diversity_score = min(0.3, unique_hit_rates / 10.0)
        
        # 3. Completeness Score (0-0.2) - Coverage across tracking days
        day_2_count = len(method_data['day_2_data'])
        day_3_count = len(method_data['day_3_data'])
        expected_coverage = len(day_1_data)
        completeness = (day_2_count + day_3_count) / (expected_coverage * 2)
        completeness_score = min(0.2, completeness * 0.2)
        
        # 4. Recency Score (0-0.1) - Recent data availability
        if len(all_evaluations) >= 10:
            recent_evals = sorted(all_evaluations, key=lambda x: x['evaluation_date'])[-10:]
            recent_diversity = len(set([round(e['hit_rate'], 1) for e in recent_evals])) / 10.0
            recency_score = recent_diversity * 0.1
        else:
            recency_score = 0.05
        
        total_score = volume_score + diversity_score + completeness_score + recency_score
        return min(1.0, total_score)
    
    def _calculate_recent_relevance_score(self, method_data: Dict) -> float:
        """
        ✅ RECENT RELEVANCE SCORE
        """
        day_1_data = method_data['day_1_data']
        
        if len(day_1_data) < 10:
            return 0.0
        
        # Sort by evaluation date
        sorted_data = sorted(day_1_data, key=lambda x: x['evaluation_date'])
        
        # Recent 30% of data
        recent_size = max(5, len(sorted_data) // 3)
        recent_data = sorted_data[-recent_size:]
        older_data = sorted_data[:-recent_size] if len(sorted_data) > recent_size else sorted_data
        
        recent_hit_rate = sum(e['hit_rate'] for e in recent_data) / len(recent_data)
        older_hit_rate = sum(e['hit_rate'] for e in older_data) / len(older_data) if older_data else recent_hit_rate
        
        # Base relevance
        base_relevance = min(recent_hit_rate / 100.0, 1.0)  # Normalize to 0-1
        
        # Trend factor
        if older_hit_rate > 0:
            trend_factor = (recent_hit_rate - older_hit_rate) / max(0.01, older_hit_rate)
            trend_bonus = max(-0.2, min(0.2, trend_factor * 0.1))
        else:
            trend_bonus = 0
        
        # Consistency bonus
        recent_hit_rates = [e['hit_rate'] for e in recent_data]
        if len(recent_hit_rates) > 1:
            recent_variance = np.var(recent_hit_rates)
            consistency_bonus = max(0, 0.1 - recent_variance / 1000.0)  # Scale variance
        else:
            consistency_bonus = 0
        
        relevance_score = base_relevance + trend_bonus + consistency_bonus
        return max(0.0, min(1.0, relevance_score))
    
    def _analyze_pattern_consistency(self, method_data: Dict) -> float:
        """
        ✅ PATTERN CONSISTENCY ANALYSIS
        """
        day_1_data = method_data['day_1_data']
        day_2_data = method_data['day_2_data']
        day_3_data = method_data['day_3_data']
        
        if len(day_1_data) < 10:
            return 0.0
        
        # 1. Cross-day consistency
        day_hit_rates = []
        for day_data in [day_1_data, day_2_data, day_3_data]:
            if day_data:
                avg_hit_rate = sum(e['hit_rate'] for e in day_data) / len(day_data)
                day_hit_rates.append(avg_hit_rate)
        
        if len(day_hit_rates) >= 2:
            day_variance = np.var(day_hit_rates)
            inter_day_consistency = max(0, 1.0 - day_variance / 10000.0)  # Scale variance
        else:
            inter_day_consistency = 0.5
        
        # 2. Intra-day stability
        hit_rates = [e['hit_rate'] for e in day_1_data]
        if len(hit_rates) >= 5:
            # Sliding window analysis
            window_size = min(5, len(hit_rates) // 2)
            pattern_scores = []
            
            for i in range(len(hit_rates) - window_size + 1):
                window = hit_rates[i:i + window_size]
                window_avg = sum(window) / len(window)
                pattern_scores.append(window_avg)
            
            if len(pattern_scores) > 1:
                pattern_variance = np.var(pattern_scores)
                intra_day_consistency = max(0, 1.0 - pattern_variance / 10000.0)
            else:
                intra_day_consistency = 0.5
        else:
            intra_day_consistency = 0.5
        
        # Combined consistency
        consistency_score = (inter_day_consistency * 0.6 + intra_day_consistency * 0.4)
        return max(0.0, min(1.0, consistency_score))
    
    def _calculate_wilson_score_average(self, method_data: Dict) -> float:
        """
        ✅ WILSON SCORE INTEGRATION
        """
        all_evaluations = method_data['evaluations']
        
        if not all_evaluations:
            return 0.0
        
        wilson_scores = [e['wilson_score'] for e in all_evaluations if e['wilson_score'] is not None]
        
        if not wilson_scores:
            return 0.0
        
        return sum(wilson_scores) / len(wilson_scores)
    
    def _calculate_composite_score(self, data_quality: float, recent_relevance: float,
                                  pattern_consistency: float, wilson_avg: float,
                                  method_data: Dict) -> float:
        """
        ✅ COMPOSITE SCORING with your weights
        """
        # Risk penalty calculation
        risk_penalty = self._calculate_risk_penalty(method_data)
        
        # Wilson score normalization (0-1)
        wilson_normalized = max(0, min(1, wilson_avg)) if wilson_avg > 0 else 0.5
        
        composite_score = (
            data_quality * self.config.DATA_QUALITY_WEIGHT +
            recent_relevance * self.config.RECENT_RELEVANCE_WEIGHT +
            pattern_consistency * self.config.PATTERN_CONSISTENCY_WEIGHT +
            (1.0 - risk_penalty) * self.config.RISK_ASSESSMENT_WEIGHT +
            wilson_normalized * self.config.WILSON_SCORE_WEIGHT
        ) * 100
        
        return max(0.0, min(100.0, composite_score))
    
    def _calculate_risk_penalty(self, method_data: Dict) -> float:
        """
        ✅ RISK PENALTY based on your thresholds
        """
        all_evaluations = method_data['evaluations']
        
        if len(all_evaluations) < 15:
            return 0.8  # High penalty for insufficient data
        
        hit_rates = [e['hit_rate'] for e in all_evaluations]
        
        # 1. Volatility penalty
        hit_rate_variance = np.var(hit_rates)
        volatility_penalty = min(0.4, hit_rate_variance / 10000.0)
        
        # 2. Suspicious performance penalty
        avg_hit_rate = sum(hit_rates) / len(hit_rates)
        if avg_hit_rate < self.config.SUSPICIOUS_LOW_HIT_RATE:  # <20% suspicious
            extreme_penalty = 0.3
        elif avg_hit_rate > 90:  # >90% too good to be true
            extreme_penalty = 0.2
        else:
            extreme_penalty = 0.0
        
        # 3. Inconsistency penalty across tracking days
        day_averages = []
        for day_data in [method_data['day_1_data'], method_data['day_2_data'], method_data['day_3_data']]:
            if day_data:
                day_avg = sum(e['hit_rate'] for e in day_data) / len(day_data)
                day_averages.append(day_avg)
        
        if len(day_averages) > 1:
            day_inconsistency = np.std(day_averages)
            inconsistency_penalty = min(0.3, day_inconsistency / 100.0)
        else:
            inconsistency_penalty = 0.1
        
        total_penalty = volatility_penalty + extreme_penalty + inconsistency_penalty
        return min(1.0, total_penalty)
    
    def _validate_method_for_analysis(self, method_data: Dict, analysis_date: date) -> Dict:
        """
        ✅ FINAL VALIDATION
        """
        day_1_data = method_data['day_1_data']
        all_evaluations = method_data['evaluations']
        
        validation_result = {
            'is_valid': True,
            'reasons': [],
            'warnings': []
        }
        
        # 1. Minimum data requirement
        if len(day_1_data) < self.config.MIN_DATA_POINTS:
            validation_result['is_valid'] = False
            validation_result['reasons'].append(f"Insufficient data: {len(day_1_data)} < {self.config.MIN_DATA_POINTS}")
            return validation_result
        
        # 2. Data diversity requirement
        hit_rates = [e['hit_rate'] for e in all_evaluations]
        unique_values = len(set([round(hr, 1) for hr in hit_rates]))
        if unique_values < 2:
            validation_result['is_valid'] = False
            validation_result['reasons'].append("Single-class data detected")
            return validation_result
        
        # 3. Recent performance check
        recent_data = sorted(day_1_data, key=lambda x: x['evaluation_date'])[-10:]
        recent_hit_rate = sum(e['hit_rate'] for e in recent_data) / len(recent_data)
        
        if recent_hit_rate == 0:
            validation_result['warnings'].append("No recent hits detected")
        elif recent_hit_rate > 95:
            validation_result['warnings'].append("Suspiciously high recent hit rate")
        
        return validation_result
    
    def _detailed_method_analysis(self, qualified_methods: Dict, analysis_date: date) -> Dict:
        """
        ✅ DETAILED ANALYSIS for qualified methods
        """
        analysis_results = {}
        
        for method_id, candidate_data in qualified_methods.items():
            try:
                method = candidate_data['method']
                method_data = candidate_data['method_data']
                
                # Enhanced risk level
                risk_level = self._determine_enhanced_risk_level(
                    candidate_data['composite_score'],
                    candidate_data
                )
                
                # Best day analysis
                best_day_analysis = self._analyze_best_tracking_day(method_data)
                
                analysis_results[method_id] = {
                    'method': method,
                    'composite_score': round(candidate_data['composite_score'], 2),
                    'risk_level': risk_level,
                    'data_points': len(method_data['evaluations']),
                    'best_day': best_day_analysis['best_day'],
                    'best_day_probability': best_day_analysis['best_day_probability'],
                    # ✅ Minimal output as requested
                    'enhanced_details': {
                        'data_quality': round(candidate_data['data_quality_score'], 3),
                        'recent_relevance': round(candidate_data['recent_relevance_score'], 3),
                        'pattern_consistency': round(candidate_data['pattern_consistency'], 3),
                        'wilson_score_avg': round(candidate_data['wilson_score_avg'], 3)
                    } if logger.level <= logging.DEBUG else None
                }
                
            except Exception as e:
                logger.error(f"❌ Error in detailed analysis for method {method_id}: {e}")
                continue
        
        return analysis_results
    
    def _determine_enhanced_risk_level(self, composite_score: float, candidate_data: Dict) -> str:
        """
        ✅ ENHANCED RISK LEVEL determination
        """
        data_quality = candidate_data['data_quality_score']
        recent_relevance = candidate_data['recent_relevance_score']
        
        if (composite_score >= 75 and 
            data_quality >= 0.8 and 
            recent_relevance >= 0.6):
            return "low"
        elif (composite_score >= 60 and 
              data_quality >= 0.7 and 
              recent_relevance >= 0.5):
            return "medium"
        elif composite_score >= 45:
            return "high"
        else:
            return "very_high"
    
    def _analyze_best_tracking_day(self, method_data: Dict) -> Dict:
        """
        ✅ ANALYZE BEST TRACKING DAY
        """
        day_performances = {}
        
        for day_num, day_data in enumerate([method_data['day_1_data'], 
                                           method_data['day_2_data'], 
                                           method_data['day_3_data']], 1):
            if day_data:
                hit_rates = [e['hit_rate'] for e in day_data]
                avg_hit_rate = sum(hit_rates) / len(hit_rates)
                hit_probability = len([hr for hr in hit_rates if hr > 0]) / len(hit_rates) * 100
                
                day_performances[day_num] = {
                    'avg_hit_rate': avg_hit_rate,
                    'hit_probability': hit_probability,
                    'sample_size': len(hit_rates)
                }
        
        if not day_performances:
            return {'best_day': 1, 'best_day_probability': 0}
        
        # Find best day based on hit probability weighted by sample size
        best_day = 1
        best_score = 0
        
        for day, perf in day_performances.items():
            if perf['sample_size'] >= 5:  # Minimum sample size
                score = perf['hit_probability'] * min(1.0, perf['sample_size'] / 20.0)
                if score > best_score:
                    best_score = score
                    best_day = day
        
        return {
            'best_day': best_day,
            'best_day_probability': day_performances.get(best_day, {}).get('hit_probability', 0)
        }
    
    def _send_analysis_failure_alert(self, error: Exception):
        """
        ✅ ALERT WHEN ENHANCED ANALYSIS FAILS
        """
        logger.error(f"🚨 ENHANCED ANALYSIS FAILURE ALERT: {str(error)}")
        # You can implement email/Slack notifications here if needed


# ✅ INTEGRATION WITH EXISTING VIEWS
def get_enhanced_method_analysis(start_date: date, end_date: date, 
                                target_limit: int = 15) -> Dict:
    """
    ✅ MAIN FUNCTION to integrate with existing views
    Song song với existing analysis
    """
    analyzer = EnhancedMethodAnalyzer()
    
    try:
        enhanced_results = analyzer.analyze_methods_enhanced(
            start_date, end_date, target_limit
        )
        
        return {
            'success': True,
            'enhanced_analysis': enhanced_results['enhanced_analysis'],
            'metadata': enhanced_results['metadata']
        }
        
    except Exception as e:
        logger.error(f"❌ Enhanced analysis completely failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'enhanced_analysis': {},
            'metadata': {}
        }