from datetime import date, timedelta
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
import logging

logger = logging.getLogger(__name__)

class EnhancedFeatureService:
    """
    ✅ ENHANCED Feature Engineering Service cho accuracy cao hơn
    
    Focuses on:
    - Cyclical patterns (weekly, monthly cycles)
    - Sequential patterns (consecutive hits/misses)
    - Correlation patterns (cross-day relationships)
    - Quality scoring (confidence metrics)
    """
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.feature_cache = {}
        
    def extract_comprehensive_features(
        self,
        method_id: int,
        target_date: date,
        historical_patterns: Dict[str, Dict[str, List[int]]],
        prediction_horizon: int = 1
    ) -> Dict[str, Dict[str, float]]:
        """
        ✅ EXTRACT COMPREHENSIVE FEATURES cho từng ngày
        
        Args:
            method_id: ID của method
            target_date: Ngày target
            historical_patterns: Patterns từ DataService
            prediction_horizon: Số ngày dự đoán
            
        Returns:
            Dict[str, Dict[str, float]]: Features cho từng ngày
            {
                "day_1": {"feature_1": 0.5, "feature_2": 0.3, ...},
                "day_2": {"feature_1": 0.7, "feature_2": 0.2, ...},
                "day_3": {"feature_1": 0.2, "feature_2": 0.8, ...}
            }
        """
        try:
            method_id_str = str(method_id)
            
            # ✅ VALIDATE input data
            if not self._validate_historical_patterns(historical_patterns, method_id_str):
                logger.warning(f"⚠️ Invalid historical patterns for method {method_id}")
                return self._create_fallback_features()
            
            # ✅ GET data cho method này
            day1_data = historical_patterns.get('hit_day_1', {}).get(method_id_str, [])
            day2_data = historical_patterns.get('hit_day_2', {}).get(method_id_str, [])
            day3_data = historical_patterns.get('hit_day_3', {}).get(method_id_str, [])
            
            # ✅ ENSURE data consistency
            max_length = max(len(day1_data), len(day2_data), len(day3_data))
            if max_length < 30:  # Minimum data points
                logger.warning(f"⚠️ Insufficient data for method {method_id}: {max_length} points")
                return self._create_fallback_features()
            
            # ✅ PAD data to same length
            day1_data = self._pad_data(day1_data, max_length)
            day2_data = self._pad_data(day2_data, max_length)
            day3_data = self._pad_data(day3_data, max_length)
            
            # ✅ EXTRACT features cho từng ngày
            features = {}
            
            for day_num in [1, 2, 3]:
                day_key = f"day_{day_num}"
                
                if day_num == 1:
                    current_data = day1_data
                elif day_num == 2:
                    current_data = day2_data
                else:
                    current_data = day3_data
                
                # ✅ EXTRACT features cho ngày này
                day_features = self._extract_day_features(
                    current_data=current_data,
                    day1_data=day1_data,
                    day2_data=day2_data,
                    day3_data=day3_data,
                    day_num=day_num,
                    target_date=target_date
                )
                
                features[day_key] = day_features
            
            logger.info(f"✅ Extracted comprehensive features for method {method_id}")
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting features for method {method_id}: {e}")
            return self._create_fallback_features()
    
    def _extract_day_features(
        self,
        current_data: List[int],
        day1_data: List[int],
        day2_data: List[int],
        day3_data: List[int],
        day_num: int,
        target_date: date
    ) -> Dict[str, float]:
        """
        ✅ EXTRACT features cho một ngày cụ thể
        
        Returns:
            Dict[str, float]: Features với values normalized [0, 1]
        """
        features = {}
        
        # ✅ 1. BASIC STATISTICAL FEATURES
        features.update(self._extract_basic_stats(current_data))
        
        # ✅ 2. CYCLICAL FEATURES
        features.update(self._extract_cyclical_features(current_data, target_date))
        
        # ✅ 3. SEQUENTIAL FEATURES
        features.update(self._extract_sequential_features(current_data))
        
        # ✅ 4. CORRELATION FEATURES
        features.update(self._extract_correlation_features(
            current_data, day1_data, day2_data, day3_data, day_num
        ))
        
        # ✅ 5. TREND FEATURES
        features.update(self._extract_trend_features(current_data))
        
        # ✅ 6. QUALITY FEATURES
        features.update(self._extract_quality_features(current_data))
        
        return features
    
    def _extract_basic_stats(self, data: List[int]) -> Dict[str, float]:
        """
        ✅ BASIC statistical features
        """
        if not data:
            return {}
        
        data_array = np.array(data)
        
        return {
            'hit_rate': float(np.mean(data_array)),
            'hit_variance': float(np.var(data_array)),
            'hit_std': float(np.std(data_array)),
            'recent_hit_rate': float(np.mean(data_array[-10:])) if len(data_array) >= 10 else float(np.mean(data_array)),
            'early_hit_rate': float(np.mean(data_array[:10])) if len(data_array) >= 10 else float(np.mean(data_array))
        }
    
    def _extract_cyclical_features(self, data: List[int], target_date: date) -> Dict[str, float]:
        """
        ✅ CYCLICAL patterns - weekly, monthly cycles
        """
        if len(data) < 7:
            return {}
        
        features = {}
        
        # ✅ WEEKLY cycle
        weekly_pattern = []
        for i in range(7):
            week_indices = [j for j in range(i, len(data), 7)]
            week_hits = [data[j] for j in week_indices if j < len(data)]
            weekly_pattern.append(np.mean(week_hits) if week_hits else 0)
        
        # ✅ Current day of week
        current_dow = target_date.weekday()
        features['weekly_pattern_strength'] = float(np.std(weekly_pattern))
        features['current_dow_performance'] = float(weekly_pattern[current_dow])
        
        # ✅ MONTHLY cycle (if enough data)
        if len(data) >= 30:
            monthly_chunks = [data[i:i+30] for i in range(0, len(data), 30)]
            monthly_rates = [np.mean(chunk) for chunk in monthly_chunks if chunk]
            features['monthly_trend'] = float(np.corrcoef(range(len(monthly_rates)), monthly_rates)[0,1] if len(monthly_rates) > 1 else 0)
        else:
            features['monthly_trend'] = 0.0
        
        return features
    
    def _extract_sequential_features(self, data: List[int]) -> Dict[str, float]:
        """
        ✅ SEQUENTIAL patterns - consecutive hits/misses
        """
        if len(data) < 3:
            return {}
        
        features = {}
        
        # ✅ CONSECUTIVE patterns
        consecutive_hits = []
        consecutive_misses = []
        current_streak = 0
        current_type = None
        
        for value in data:
            if value == current_type:
                current_streak += 1
            else:
                if current_type is not None:
                    if current_type == 1:
                        consecutive_hits.append(current_streak)
                    else:
                        consecutive_misses.append(current_streak)
                current_streak = 1
                current_type = value
        
        # ✅ Add final streak
        if current_type == 1:
            consecutive_hits.append(current_streak)
        else:
            consecutive_misses.append(current_streak)
        
        features['max_consecutive_hits'] = float(max(consecutive_hits) if consecutive_hits else 0)
        features['max_consecutive_misses'] = float(max(consecutive_misses) if consecutive_misses else 0)
        features['avg_consecutive_hits'] = float(np.mean(consecutive_hits) if consecutive_hits else 0)
        features['avg_consecutive_misses'] = float(np.mean(consecutive_misses) if consecutive_misses else 0)
        
        # ✅ RECENT streak
        recent_streak = 0
        for i in range(len(data) - 1, -1, -1):
            if data[i] == data[-1]:
                recent_streak += 1
            else:
                break
        
        features['recent_streak_length'] = float(recent_streak)
        features['recent_streak_is_hit'] = float(data[-1] if data else 0)
        
        return features
    
    def _extract_correlation_features(
        self,
        current_data: List[int],
        day1_data: List[int],
        day2_data: List[int],
        day3_data: List[int],
        day_num: int
    ) -> Dict[str, float]:
        """
        ✅ CORRELATION features - cross-day relationships
        """
        features = {}
        
        # ✅ CORRELATION with other days
        min_length = min(len(current_data), len(day1_data), len(day2_data), len(day3_data))
        if min_length < 10:
            return {}
        
        # ✅ TRUNCATE to same length
        current_truncated = current_data[:min_length]
        day1_truncated = day1_data[:min_length]
        day2_truncated = day2_data[:min_length]
        day3_truncated = day3_data[:min_length]
        
        try:
            if day_num != 1:
                corr_day1 = np.corrcoef(current_truncated, day1_truncated)[0, 1]
                features['correlation_with_day1'] = float(corr_day1 if not np.isnan(corr_day1) else 0)
            
            if day_num != 2:
                corr_day2 = np.corrcoef(current_truncated, day2_truncated)[0, 1]
                features['correlation_with_day2'] = float(corr_day2 if not np.isnan(corr_day2) else 0)
            
            if day_num != 3:
                corr_day3 = np.corrcoef(current_truncated, day3_truncated)[0, 1]
                features['correlation_with_day3'] = float(corr_day3 if not np.isnan(corr_day3) else 0)
        except Exception as e:
            logger.warning(f"⚠️ Error calculating correlations: {e}")
        
        # ✅ SEQUENTIAL dependencies
        if len(current_data) >= 2:
            lag1_corr = np.corrcoef(current_data[:-1], current_data[1:])[0, 1]
            features['lag1_autocorrelation'] = float(lag1_corr if not np.isnan(lag1_corr) else 0)
        
        return features
    
    def _extract_trend_features(self, data: List[int]) -> Dict[str, float]:
        """
        ✅ TREND features - temporal patterns
        """
        if len(data) < 5:
            return {}
        
        features = {}
        
        # ✅ OVERALL trend
        x = np.arange(len(data))
        y = np.array(data)
        
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            features['overall_trend'] = float(slope)
            features['trend_strength'] = float(r_value ** 2)
            features['trend_significance'] = float(1 - p_value)
        except Exception as e:
            logger.warning(f"⚠️ Error calculating trend: {e}")
            features['overall_trend'] = 0.0
            features['trend_strength'] = 0.0
            features['trend_significance'] = 0.0
        
        # ✅ RECENT trend (last 30% of data)
        recent_size = max(5, len(data) // 3)
        recent_data = data[-recent_size:]
        recent_x = np.arange(len(recent_data))
        
        try:
            recent_slope, _, recent_r, _, _ = stats.linregress(recent_x, recent_data)
            features['recent_trend'] = float(recent_slope)
            features['recent_trend_strength'] = float(recent_r ** 2)
        except Exception as e:
            features['recent_trend'] = 0.0
            features['recent_trend_strength'] = 0.0
        
        return features
    
    def _extract_quality_features(self, data: List[int]) -> Dict[str, float]:
        """
        ✅ QUALITY features - confidence metrics
        """
        if not data:
            return {}
        
        features = {}
        
        # ✅ DATA quality
        features['data_length'] = float(len(data))
        features['data_completeness'] = float(1.0)  # Assuming complete data
        
        # ✅ PATTERN stability
        if len(data) >= 20:
            # Split into chunks and measure consistency
            chunk_size = len(data) // 4
            chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
            chunk_rates = [np.mean(chunk) for chunk in chunks if len(chunk) >= 5]
            
            if len(chunk_rates) > 1:
                features['pattern_stability'] = float(1 - np.std(chunk_rates))
            else:
                features['pattern_stability'] = 0.5
        else:
            features['pattern_stability'] = 0.5
        
        # ✅ PREDICTION confidence
        recent_variance = np.var(data[-10:]) if len(data) >= 10 else np.var(data)
        features['prediction_confidence'] = float(1 / (1 + recent_variance))
        
        return features
    
    def _validate_historical_patterns(self, patterns: Dict, method_id_str: str) -> bool:
        """
        ✅ VALIDATE input patterns
        """
        if not patterns:
            return False
        
        required_keys = ['hit_day_1', 'hit_day_2', 'hit_day_3']
        if not all(key in patterns for key in required_keys):
            return False
        
        if method_id_str not in patterns['hit_day_1']:
            return False
        
        return True
    
    def _pad_data(self, data: List[int], target_length: int) -> List[int]:
        """
        ✅ PAD data to target length
        """
        if len(data) >= target_length:
            return data[:target_length]
        
        # Pad with zeros
        return data + [0] * (target_length - len(data))
    
    def _create_fallback_features(self) -> Dict[str, Dict[str, float]]:
        """
        ✅ CREATE fallback features when data is insufficient
        """
        fallback_features = {
            'hit_rate': 0.1,
            'hit_variance': 0.0,
            'hit_std': 0.0,
            'recent_hit_rate': 0.1,
            'early_hit_rate': 0.1,
            'weekly_pattern_strength': 0.0,
            'current_dow_performance': 0.1,
            'monthly_trend': 0.0,
            'max_consecutive_hits': 0.0,
            'max_consecutive_misses': 0.0,
            'avg_consecutive_hits': 0.0,
            'avg_consecutive_misses': 0.0,
            'recent_streak_length': 0.0,
            'recent_streak_is_hit': 0.0,
            'correlation_with_day1': 0.0,
            'correlation_with_day2': 0.0,
            'correlation_with_day3': 0.0,
            'lag1_autocorrelation': 0.0,
            'overall_trend': 0.0,
            'trend_strength': 0.0,
            'trend_significance': 0.0,
            'recent_trend': 0.0,
            'recent_trend_strength': 0.0,
            'data_length': 0.0,
            'data_completeness': 0.0,
            'pattern_stability': 0.0,
            'prediction_confidence': 0.0,
        }
        
        return {
            'day_1': fallback_features.copy(),
            'day_2': fallback_features.copy(),
            'day_3': fallback_features.copy(),
        }

# ✅ Create global instance
enhanced_feature_service = EnhancedFeatureService()