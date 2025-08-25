import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import logging
from django.db.models import Q, Count, Avg
from django.utils import timezone

from results.models import KetQuaXoSo
from predictions_tracker.models import (
    PredictionMethod, 
    DailyTrackingSession, 
    MethodPredictionResult,
    TrackingEvaluation
)

logger = logging.getLogger(__name__)

class FeatureEngineeringService:
    """
    Enhanced Feature Engineering Service tận dụng tối đa dữ liệu từ KetQuaXoSo và tracking data
    """
    
    def __init__(self):
        # Cache để tối ưu performance
        self._kqxs_cache = {}
        self._frequency_cache = {}
        self._cycle_cache = {}
        logger.info("✅ FeatureEngineeringService initialized")
    
    def extract_comprehensive_features(
        self, 
        method: PredictionMethod,
        target_date: date,
        predicted_numbers: List[str],
        historical_data: List[Dict],
        context: Dict[str, Any] = None
    ) -> Dict[str, float]:
        """
        ✅ TRÍCH XUẤT FEATURES TOÀN DIỆN CHO ML
        
        Args:
            method: PredictionMethod object
            target_date: Ngày cần dự đoán
            predicted_numbers: Các số được dự đoán
            historical_data: Dữ liệu lịch sử tracking
            context: Additional context data
            
        Returns:
            Dict[str, float]: Comprehensive features dictionary
        """
        try:
            logger.info(f"🔬 Extracting comprehensive features for method {method.id} on {target_date}")
            
            features = {}
            
            # 1. ✅ FEATURES TỪ KetQuaXoSo (Mỏ vàng dữ liệu thống kê)
            kqxs_features = self._extract_kqxs_features(
                predicted_numbers, target_date, days_back=30
            )
            features.update(kqxs_features)
            
            # 2. ✅ TEMPORAL FEATURES (Đặc trưng thời gian)
            temporal_features = self._extract_temporal_features(target_date)
            features.update(temporal_features)
            
            # 3. ✅ METHOD-SPECIFIC FEATURES (Đặc trưng riêng của phương pháp)
            method_features = self._extract_method_specific_features(
                method, historical_data, target_date
            )
            features.update(method_features)
            
            # 4. ✅ HISTORICAL PATTERNS FEATURES
            pattern_features = self._extract_historical_pattern_features(
                historical_data, target_date
            )
            features.update(pattern_features)
            
            # 5. ✅ MARKET CONDITIONS FEATURES (Điều kiện thị trường)
            market_features = self._extract_market_condition_features(target_date)
            features.update(market_features)
            
            # 6. ✅ INTERACTION FEATURES (Tương tác giữa các features)
            interaction_features = self._create_interaction_features(features)
            features.update(interaction_features)
            
            logger.info(f"✅ Extracted {len(features)} features for method {method.id}")
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting features for method {method.id}: {e}")
            return self._get_fallback_features(target_date)
    
    def _extract_kqxs_features(
        self, 
        predicted_numbers: List[str], 
        target_date: date, 
        days_back: int = 30
    ) -> Dict[str, float]:
        """
        ✅ TRÍCH XUẤT FEATURES TỪ KetQuaXoSo - MỎ VÀNG DỮ LIỆU
        """
        features = {}
        
        try:
            # Lấy dữ liệu KQXS 30 ngày gần nhất
            start_date = target_date - timedelta(days=days_back)
            recent_results = KetQuaXoSo.objects.filter(
                ngay__range=[start_date, target_date - timedelta(days=1)]
            ).order_by('-ngay')
            
            if not recent_results.exists():
                return self._get_default_kqxs_features()
            
            # 1. ✅ TẦN SUẤT CỦA CÁC SỐ ĐƯỢC DỰ ĐOÁN
            frequency_features = self._calculate_number_frequencies(
                predicted_numbers, recent_results
            )
            features.update(frequency_features)
            
            # 2. ✅ TRẠNG THÁI GAN/KHÔNG GAN
            gan_features = self._calculate_gan_status(predicted_numbers, recent_results)
            features.update(gan_features)
            
            # 3. ✅ ĐẶC TRƯNG ĐẦU/ĐUÔI/TỔNG/CHẠM NGÀY HÔM TRƯỚC
            previous_day_features = self._extract_previous_day_features(
                target_date, predicted_numbers
            )
            features.update(previous_day_features)
            
            # 4. ✅ CHU KỲ CỦA CÁC SỐ DỰ ĐOÁN
            cycle_features = self._calculate_number_cycles(
                predicted_numbers, recent_results, target_date
            )
            features.update(cycle_features)
            
            # 5. ✅ THỐNG KÊ NÂNG CAO TỪ KetQuaXoSo
            advanced_stats = self._extract_advanced_kqxs_stats(recent_results)
            features.update(advanced_stats)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting KQXS features: {e}")
            return self._get_default_kqxs_features()
    
    def _calculate_number_frequencies(
        self, 
        predicted_numbers: List[str], 
        recent_results
    ) -> Dict[str, float]:
        """Tính tần suất xuất hiện của các số dự đoán"""
        features = {}
        
        if not predicted_numbers:
            return {
                'freq_avg': 0.0,
                'freq_max': 0.0,
                'freq_min': 0.0,
                'freq_std': 0.0
            }
        
        # Tính tần suất cho từng số
        frequencies = []
        total_days = recent_results.count()
        
        for number in predicted_numbers:
            count = 0
            for result in recent_results:
                if number in result.get_all_2digit_numbers():
                    count += 1
            
            frequency = count / total_days if total_days > 0 else 0
            frequencies.append(frequency)
        
        if frequencies:
            features.update({
                'freq_avg': float(np.mean(frequencies)),
                'freq_max': float(np.max(frequencies)),
                'freq_min': float(np.min(frequencies)),
                'freq_std': float(np.std(frequencies)),
                'freq_sum': float(np.sum(frequencies)),
                'high_freq_count': sum(1 for f in frequencies if f > 0.1),
                'low_freq_count': sum(1 for f in frequencies if f < 0.05)
            })
        
        return features
    
    def _calculate_gan_status(
        self, 
        predicted_numbers: List[str], 
        recent_results
    ) -> Dict[str, float]:
        """Tính trạng thái gan/không gan của các số"""
        features = {}
        
        if not predicted_numbers:
            return {'gan_ratio': 0.0, 'gan_avg_days': 0.0}
        
        gan_count = 0
        total_gap_days = 0
        
        for number in predicted_numbers:
            # Tìm lần xuất hiện gần nhất
            days_since_last = 0
            found = False
            
            for i, result in enumerate(recent_results):
                if number in result.get_all_2digit_numbers():
                    days_since_last = i
                    found = True
                    break
            
            if not found:
                days_since_last = len(recent_results)  # Số này chưa về trong period
            
            # Số được coi là "gan" nếu không về trong 15 ngày gần nhất
            if days_since_last >= 15:
                gan_count += 1
            
            total_gap_days += days_since_last
        
        features.update({
            'gan_ratio': gan_count / len(predicted_numbers),
            'gan_avg_days': total_gap_days / len(predicted_numbers),
            'gan_count': gan_count,
            'non_gan_count': len(predicted_numbers) - gan_count
        })
        
        return features
    
    def _extract_previous_day_features(
        self, 
        target_date: date, 
        predicted_numbers: List[str]
    ) -> Dict[str, float]:
        """Trích xuất features từ ngày hôm trước"""
        features = {}
        
        try:
            previous_date = target_date - timedelta(days=1)
            previous_result = KetQuaXoSo.objects.filter(ngay=previous_date).first()
            
            if not previous_result:
                return self._get_default_previous_day_features()
            
            # Lấy các số về ngày hôm trước
            previous_numbers = list(previous_result.get_all_2digit_numbers())
            
            if not predicted_numbers or not previous_numbers:
                return self._get_default_previous_day_features()
            
            # Phân tích đầu/đuôi/tổng/chạm
            head_matches = 0
            tail_matches = 0
            sum_matches = 0
            touch_matches = 0
            
            for pred_num in predicted_numbers:
                if len(pred_num) >= 2:
                    pred_head = pred_num[0]
                    pred_tail = pred_num[-1]
                    pred_sum = sum(int(d) for d in pred_num) % 10
                    
                    # Kiểm tra với các số về ngày hôm trước
                    for prev_num in previous_numbers:
                        if len(prev_num) >= 2:
                            # Đầu số
                            if pred_head == prev_num[0]:
                                head_matches += 1
                            
                            # Đuôi số
                            if pred_tail == prev_num[-1]:
                                tail_matches += 1
                            
                            # Tổng
                            prev_sum = sum(int(d) for d in prev_num) % 10
                            if pred_sum == prev_sum:
                                sum_matches += 1
                            
                            # Chạm (có chung chữ số)
                            if set(pred_num) & set(prev_num):
                                touch_matches += 1
            
            # Normalize bằng số lượng predicted numbers
            total_predicted = len(predicted_numbers)
            features.update({
                'prev_head_match_ratio': head_matches / total_predicted,
                'prev_tail_match_ratio': tail_matches / total_predicted,
                'prev_sum_match_ratio': sum_matches / total_predicted,
                'prev_touch_match_ratio': touch_matches / total_predicted,
                'prev_total_matches': head_matches + tail_matches + sum_matches + touch_matches
            })
            
            # Thống kê ngày hôm trước
            prev_stats = previous_result.get_head_tail_stats(days=1)
            features.update({
                'prev_day_number_count': len(previous_numbers),
                'prev_day_diversity': len(set(previous_numbers)) / len(previous_numbers) if previous_numbers else 0
            })
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting previous day features: {e}")
            return self._get_default_previous_day_features()
    
    def _calculate_number_cycles(
        self, 
        predicted_numbers: List[str], 
        recent_results, 
        target_date: date
    ) -> Dict[str, float]:
        """Tính chu kỳ xuất hiện của các số dự đoán"""
        features = {}
        
        if not predicted_numbers:
            return self._get_default_cycle_features()
        
        cycle_lengths = []
        days_since_last = []
        
        for number in predicted_numbers:
            # Phân tích chu kỳ cho từng số
            appearances = []
            
            for i, result in enumerate(recent_results):
                if number in result.get_all_2digit_numbers():
                    appearances.append(i)
            
            if len(appearances) >= 2:
                # Tính chu kỳ trung bình
                gaps = [appearances[i] - appearances[i+1] for i in range(len(appearances)-1)]
                avg_cycle = np.mean(gaps) if gaps else 0
                cycle_lengths.append(avg_cycle)
                
                # Ngày kể từ lần cuối
                days_since_last.append(appearances[0])
            else:
                # Số chưa về hoặc chỉ về 1 lần
                cycle_lengths.append(0)
                days_since_last.append(len(recent_results))
        
        if cycle_lengths:
            features.update({
                'cycle_avg': float(np.mean(cycle_lengths)),
                'cycle_max': float(np.max(cycle_lengths)),
                'cycle_min': float(np.min(cycle_lengths)),
                'cycle_std': float(np.std(cycle_lengths)),
                'days_since_avg': float(np.mean(days_since_last)),
                'overdue_count': sum(1 for d in days_since_last if d > 20),
                'recent_count': sum(1 for d in days_since_last if d <= 5)
            })
        
        return features
    
    def _extract_temporal_features(self, target_date: date) -> Dict[str, float]:
        """✅ TRÍCH XUẤT CÁC ĐẶC TRƯNG THỜI GIAN"""
        features = {}
        
        # Ngày trong tuần (0=Monday, 6=Sunday)
        features['day_of_week'] = float(target_date.weekday())
        features['is_weekend'] = float(target_date.weekday() >= 5)
        features['is_monday'] = float(target_date.weekday() == 0)
        features['is_friday'] = float(target_date.weekday() == 4)
        
        # Ngày trong tháng
        features['day_of_month'] = float(target_date.day)
        features['is_month_start'] = float(target_date.day <= 5)
        features['is_month_end'] = float(target_date.day >= 25)
        
        # Tuần trong tháng
        features['week_of_month'] = float((target_date.day - 1) // 7 + 1)
        
        # Tháng trong năm
        features['month'] = float(target_date.month)
        features['quarter'] = float((target_date.month - 1) // 3 + 1)
        
        # Kiểm tra ngày lễ, Tết (simplified)
        features['is_special_period'] = float(self._is_special_period(target_date))
        
        # Chu kỳ lunar (approximation)
        features['lunar_phase'] = float(self._approximate_lunar_phase(target_date))
        
        return features
    
    def _extract_method_specific_features(
        self, 
        method: PredictionMethod, 
        historical_data: List[Dict], 
        target_date: date
    ) -> Dict[str, float]:
        """✅ TRÍCH XUẤT ĐẶC TRƯNG RIÊNG CỦA PHƯƠNG PHÁP"""
        features = {}
        
        if not historical_data:
            return self._get_default_method_features()
        
        # 1. Performance theo ngày trong tuần
        weekday_performance = self._analyze_weekday_performance(historical_data, target_date)
        features.update(weekday_performance)
        
        # 2. Chuỗi thắng/thua hiện tại
        streak_features = self._calculate_current_streak(historical_data)
        features.update(streak_features)
        
        # 3. Độ ổn định (variance của hit rate)
        stability_features = self._calculate_stability_metrics(historical_data)
        features.update(stability_features)
        
        # 4. Trend gần đây
        trend_features = self._analyze_recent_trend(historical_data)
        features.update(trend_features)
        
        # 5. Performance theo tracking day (1, 2, 3)
        tracking_day_features = self._analyze_tracking_day_performance(historical_data)
        features.update(tracking_day_features)
        
        return features
    
    def _analyze_weekday_performance(
        self, 
        historical_data: List[Dict], 
        target_date: date
    ) -> Dict[str, float]:
        """Phân tích performance theo ngày trong tuần"""
        features = {}
        
        weekday_hits = defaultdict(list)
        target_weekday = target_date.weekday()
        
        for data in historical_data:
            eval_date = data.get('evaluation_date')
            if eval_date:
                weekday = eval_date.weekday()
                weekday_hits[weekday].append(data.get('hit_rate', 0))
        
        # Performance trên ngày target
        if target_weekday in weekday_hits:
            target_day_rates = weekday_hits[target_weekday]
            features['target_weekday_avg'] = float(np.mean(target_day_rates))
            features['target_weekday_std'] = float(np.std(target_day_rates))
            features['target_weekday_count'] = len(target_day_rates)
        else:
            features['target_weekday_avg'] = 0.0
            features['target_weekday_std'] = 0.0
            features['target_weekday_count'] = 0
        
        # So sánh với các ngày khác
        all_other_rates = []
        for day, rates in weekday_hits.items():
            if day != target_weekday:
                all_other_rates.extend(rates)
        
        if all_other_rates:
            features['other_weekdays_avg'] = float(np.mean(all_other_rates))
            features['weekday_advantage'] = features['target_weekday_avg'] - features['other_weekdays_avg']
        else:
            features['other_weekdays_avg'] = 0.0
            features['weekday_advantage'] = 0.0
        
        return features
    
    def _calculate_current_streak(self, historical_data: List[Dict]) -> Dict[str, float]:
        """Tính chuỗi thắng/thua hiện tại"""
        features = {}
        
        if not historical_data:
            return {'current_streak': 0.0, 'streak_length': 0.0, 'is_hot_streak': 0.0}
        
        # Sort by date descending (newest first)
        sorted_data = sorted(
            historical_data, 
            key=lambda x: x.get('evaluation_date', date.min), 
            reverse=True
        )
        
        if not sorted_data:
            return {'current_streak': 0.0, 'streak_length': 0.0, 'is_hot_streak': 0.0}
        
        # Xác định streak hiện tại
        current_streak = 0
        streak_type = 0  # 1 for win, -1 for loss, 0 for neutral
        
        first_result = sorted_data[0].get('hit_rate', 0)
        is_winning = first_result > 15  # Threshold for "win"
        streak_type = 1 if is_winning else -1
        
        for data in sorted_data:
            hit_rate = data.get('hit_rate', 0)
            is_hit = hit_rate > 15
            
            if (is_winning and is_hit) or (not is_winning and not is_hit):
                current_streak += 1
            else:
                break
        
        features['current_streak'] = float(current_streak * streak_type)
        features['streak_length'] = float(abs(current_streak))
        features['is_hot_streak'] = float(current_streak >= 3 and streak_type == 1)
        features['is_cold_streak'] = float(current_streak >= 3 and streak_type == -1)
        
        return features
    
    def _calculate_stability_metrics(self, historical_data: List[Dict]) -> Dict[str, float]:
        """Tính độ ổn định của phương pháp"""
        features = {}
        
        if not historical_data:
            return {'stability_score': 0.0, 'hit_rate_variance': 0.0, 'consistency_score': 0.0}
        
        hit_rates = [data.get('hit_rate', 0) for data in historical_data]
        
        if hit_rates:
            mean_rate = np.mean(hit_rates)
            variance = np.var(hit_rates)
            std_dev = np.std(hit_rates)
            
            # Stability score (lower variance = higher stability)
            stability_score = 1.0 / (1.0 + variance / 100.0)
            
            # Consistency score
            consistency_score = 1.0 - (std_dev / (mean_rate + 1e-6))
            
            features.update({
                'stability_score': float(stability_score),
                'hit_rate_variance': float(variance),
                'hit_rate_std': float(std_dev),
                'consistency_score': float(max(0, consistency_score)),
                'coefficient_variation': float(std_dev / (mean_rate + 1e-6))
            })
        
        return features
    
    def _analyze_recent_trend(self, historical_data: List[Dict]) -> Dict[str, float]:
        """Phân tích xu hướng gần đây"""
        features = {}
        
        if len(historical_data) < 5:
            return {'recent_trend': 0.0, 'trend_strength': 0.0, 'momentum': 0.0}
        
        # Sort by date
        sorted_data = sorted(
            historical_data, 
            key=lambda x: x.get('evaluation_date', date.min)
        )
        
        hit_rates = [data.get('hit_rate', 0) for data in sorted_data]
        
        # Calculate trend using linear regression
        x = np.arange(len(hit_rates))
        coeffs = np.polyfit(x, hit_rates, 1)
        trend_slope = coeffs[0]
        
        # Recent vs older performance
        recent_period = len(hit_rates) // 3  # Last 1/3 of data
        if recent_period > 0:
            recent_avg = np.mean(hit_rates[-recent_period:])
            older_avg = np.mean(hit_rates[:-recent_period])
            momentum = recent_avg - older_avg
        else:
            momentum = 0
        
        features.update({
            'recent_trend': float(trend_slope),
            'trend_strength': float(abs(trend_slope)),
            'momentum': float(momentum),
            'is_improving': float(trend_slope > 1),
            'is_declining': float(trend_slope < -1)
        })
        
        return features
    
    def _analyze_tracking_day_performance(self, historical_data: List[Dict]) -> Dict[str, float]:
        """Phân tích performance theo tracking day"""
        features = {}
        
        day_performance = {1: [], 2: [], 3: []}
        
        for data in historical_data:
            tracking_day = data.get('tracking_day')
            hit_rate = data.get('hit_rate', 0)
            
            if tracking_day in day_performance:
                day_performance[tracking_day].append(hit_rate)
        
        for day in [1, 2, 3]:
            if day_performance[day]:
                features[f'day{day}_avg_rate'] = float(np.mean(day_performance[day]))
                features[f'day{day}_count'] = len(day_performance[day])
                features[f'day{day}_best'] = float(np.max(day_performance[day]))
            else:
                features[f'day{day}_avg_rate'] = 0.0
                features[f'day{day}_count'] = 0
                features[f'day{day}_best'] = 0.0
        
        # Find best tracking day
        day_avgs = [features[f'day{day}_avg_rate'] for day in [1, 2, 3]]
        best_day = day_avgs.index(max(day_avgs)) + 1 if any(day_avgs) else 1
        features['best_tracking_day'] = float(best_day)
        
        return features
    
    def _extract_advanced_kqxs_stats(self, recent_results) -> Dict[str, float]:
        """Trích xuất thống kê nâng cao từ KetQuaXoSo"""
        features = {}
        
        try:
            if not recent_results.exists():
                return {}
            
            # Tính diversity của numbers
            all_numbers = []
            for result in recent_results:
                all_numbers.extend(result.get_all_2digit_numbers())
            
            if all_numbers:
                unique_numbers = set(all_numbers)
                features['number_diversity'] = len(unique_numbers) / len(all_numbers)
                features['total_numbers_seen'] = len(unique_numbers)
                
                # Top frequent numbers
                counter = Counter(all_numbers)
                top_3_freq = sum(count for _, count in counter.most_common(3))
                features['top3_concentration'] = top_3_freq / len(all_numbers)
            
            # Analyze patterns using KetQuaXoSo methods
            if recent_results.exists():
                latest_result = recent_results.first()
                
                # Head/tail stats
                head_tail_stats = latest_result.get_head_tail_stats(days=30)
                if head_tail_stats:
                    heads = dict(head_tail_stats.get('heads', []))
                    tails = dict(head_tail_stats.get('tails', []))
                    
                    features['head_diversity'] = len(heads)
                    features['tail_diversity'] = len(tails)
                    features['most_common_head_freq'] = max(heads.values()) if heads else 0
                    features['most_common_tail_freq'] = max(tails.values()) if tails else 0
                
                # Sum stats
                sum_stats = latest_result.get_sum_stats(days=30)
                if sum_stats:
                    features['sum_pattern_strength'] = sum_stats[0][1] / len(recent_results) if sum_stats else 0
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting advanced KQXS stats: {e}")
            return {}
    
    def _extract_historical_pattern_features(
        self, 
        historical_data: List[Dict], 
        target_date: date
    ) -> Dict[str, float]:
        """Trích xuất features từ patterns lịch sử"""
        features = {}
        
        if not historical_data:
            return {}
        
        # Cyclical patterns
        monthly_performance = defaultdict(list)
        quarterly_performance = defaultdict(list)
        
        for data in historical_data:
            eval_date = data.get('evaluation_date')
            hit_rate = data.get('hit_rate', 0)
            
            if eval_date:
                month = eval_date.month
                quarter = (eval_date.month - 1) // 3 + 1
                
                monthly_performance[month].append(hit_rate)
                quarterly_performance[quarter].append(hit_rate)
        
        # Target date patterns
        target_month = target_date.month
        target_quarter = (target_date.month - 1) // 3 + 1
        
        if monthly_performance[target_month]:
            features['target_month_avg'] = float(np.mean(monthly_performance[target_month]))
            features['target_month_count'] = len(monthly_performance[target_month])
        else:
            features['target_month_avg'] = 0.0
            features['target_month_count'] = 0
        
        if quarterly_performance[target_quarter]:
            features['target_quarter_avg'] = float(np.mean(quarterly_performance[target_quarter]))
            features['target_quarter_count'] = len(quarterly_performance[target_quarter])
        else:
            features['target_quarter_avg'] = 0.0
            features['target_quarter_count'] = 0
        
        return features
    
    def _extract_market_condition_features(self, target_date: date) -> Dict[str, float]:
        """Trích xuất features về điều kiện thị trường"""
        features = {}
        
        try:
            # Số lượng methods active gần target date
            active_methods_count = PredictionMethod.objects.filter(
                is_active=True,
                last_used_at__gte=target_date - timedelta(days=7)
            ).count()
            
            features['market_activity'] = float(active_methods_count)
            
            # Tổng số sessions trong tuần trước
            weekly_sessions = DailyTrackingSession.objects.filter(
                prediction_date__range=[
                    target_date - timedelta(days=7),
                    target_date - timedelta(days=1)
                ]
            ).count()
            
            features['market_volume'] = float(weekly_sessions)
            
            # Competition level (số methods cùng dự đoán cho ngày này)
            same_date_predictions = DailyTrackingSession.objects.filter(
                prediction_date=target_date
            ).count()
            
            features['competition_level'] = float(same_date_predictions)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting market condition features: {e}")
            return {'market_activity': 0.0, 'market_volume': 0.0, 'competition_level': 0.0}
    
    def _create_interaction_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """Tạo interaction features giữa các features"""
        interaction_features = {}
        
        try:
            # Frequency × Gan status interaction
            if 'freq_avg' in features and 'gan_ratio' in features:
                interaction_features['freq_gan_interaction'] = features['freq_avg'] * (1 - features['gan_ratio'])
            
            # Weekday × Recent trend interaction
            if 'target_weekday_avg' in features and 'recent_trend' in features:
                interaction_features['weekday_trend_interaction'] = features['target_weekday_avg'] * features['recent_trend']
            
            # Stability × Performance interaction
            if 'stability_score' in features and 'target_weekday_avg' in features:
                interaction_features['stability_performance'] = features['stability_score'] * features['target_weekday_avg']
            
            # Cycle × Market interaction
            if 'cycle_avg' in features and 'market_activity' in features:
                interaction_features['cycle_market_interaction'] = features['cycle_avg'] * features['market_activity']
            
            # Temporal interactions
            if 'day_of_week' in features and 'week_of_month' in features:
                interaction_features['temporal_interaction'] = features['day_of_week'] * features['week_of_month']
            
            return interaction_features
            
        except Exception as e:
            logger.error(f"❌ Error creating interaction features: {e}")
            return {}
    
    # ✅ HELPER METHODS & DEFAULTS
    
    def _is_special_period(self, target_date: date) -> bool:
        """Kiểm tra có phải thời gian đặc biệt (Tết, lễ)"""
        # Simplified logic - có thể mở rộng
        month = target_date.month
        day = target_date.day
        
        # Tết Nguyên Đán (approximation)
        if month in [1, 2] and day <= 15:
            return True
        
        # Các ngày lễ lớn
        special_dates = [
            (4, 30), (5, 1), (9, 2), (12, 25)  # 30/4, 1/5, 2/9, 25/12
        ]
        
        return (month, day) in special_dates
    
    def _approximate_lunar_phase(self, target_date: date) -> float:
        """Tính gần đúng pha mặt trăng (0-1)"""
        # Simple approximation using known lunar cycle
        reference_date = date(2000, 1, 6)  # Known new moon
        days_diff = (target_date - reference_date).days
        lunar_cycle = 29.53  # Average lunar cycle in days
        
        phase = (days_diff % lunar_cycle) / lunar_cycle
        return phase
    
    def _get_fallback_features(self, target_date: date) -> Dict[str, float]:
        """Features mặc định khi có lỗi"""
        return {
            'day_of_week': float(target_date.weekday()),
            'is_weekend': float(target_date.weekday() >= 5),
            'day_of_month': float(target_date.day),
            'month': float(target_date.month),
            'freq_avg': 0.0,
            'gan_ratio': 0.5,
            'stability_score': 0.5,
            'recent_trend': 0.0,
            'current_streak': 0.0
        }
    
    def _get_default_kqxs_features(self) -> Dict[str, float]:
        """Default KQXS features"""
        return {
            'freq_avg': 0.0, 'freq_max': 0.0, 'freq_min': 0.0, 'freq_std': 0.0,
            'gan_ratio': 0.5, 'gan_avg_days': 15.0,
            'prev_head_match_ratio': 0.0, 'prev_tail_match_ratio': 0.0,
            'cycle_avg': 10.0, 'days_since_avg': 10.0
        }
    
    def _get_default_previous_day_features(self) -> Dict[str, float]:
        """Default previous day features"""
        return {
            'prev_head_match_ratio': 0.0,
            'prev_tail_match_ratio': 0.0,
            'prev_sum_match_ratio': 0.0,
            'prev_touch_match_ratio': 0.0,
            'prev_total_matches': 0.0,
            'prev_day_number_count': 20.0,
            'prev_day_diversity': 1.0
        }
    
    def _get_default_cycle_features(self) -> Dict[str, float]:
        """Default cycle features"""
        return {
            'cycle_avg': 10.0, 'cycle_max': 20.0, 'cycle_min': 5.0, 'cycle_std': 5.0,
            'days_since_avg': 10.0, 'overdue_count': 0.0, 'recent_count': 0.0
        }
    
    def _get_default_method_features(self) -> Dict[str, float]:
        """Default method features"""
        return {
            'target_weekday_avg': 15.0, 'weekday_advantage': 0.0,
            'current_streak': 0.0, 'stability_score': 0.5,
            'recent_trend': 0.0, 'best_tracking_day': 1.0
        }

# Singleton instance
feature_engineering_service = FeatureEngineeringService()