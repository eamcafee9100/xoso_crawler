import logging
from collections import Counter, defaultdict
from datetime import date, timedelta, datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from predictions_tracker.models import (
    DailyTrackingSession,
    MethodPredictionResult,
    PredictionCycle,
    PredictionMethod,
    TrackingEvaluation,
)
from results.models import KetQuaXoSo

from .DataService import data_service
from .FeatureEngineering import FeatureEngineeringService
from .MLModelService import ml_model_service

logger = logging.getLogger(__name__)
from typing import Optional, Tuple

from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from predictions_tracker.models import PredictionMethod, DailyTrackingSession
from django.db.models import Sum, Avg


class TrackingService:
    """
    Enhanced TrackingService với ML analysis chuyên sâu cho predictions_tracker models
    """

    def __init__(self):
        self.cache_timeout = 3600
        self.scaler = StandardScaler()
        # ✅ REFERENCE TO ML MODEL SERVICE
        self.ml_service = ml_model_service
        logger.info("Enhanced TrackingService initialized")

    def _get_method_historical_data(
        self, method: PredictionMethod, target_date: date, days_back: int = 90
    ) -> List[Dict]:
        """
        ✅ SỬA: Sử dụng DataService để lấy dữ liệu thay vì query trực tiếp
        """
        try:
            logger.info(
                f"🔍 Getting historical data for method {method.id} using DataService"
            )

            # ✅ SỬA: Import DataService nếu chưa có
            try:
                from .DataService import data_service
            except ImportError:
                logger.warning("⚠️ DataService not available, using fallback query")
                return self._get_method_historical_data_fallback(
                    method, target_date, days_back
                )

            # ✅ SỬA: Sử dụng DataService.get_comprehensive_historical_data
            months_back = max(1, days_back // 30)  # Convert days to months

            # Get historical patterns từ DataService
            historical_patterns = data_service.get_comprehensive_historical_data(
                target_date=target_date.isoformat(),
                method_ids=[method.id],
                months_back=months_back,
            )

            # ✅ VALIDATE patterns data
            if not historical_patterns or not historical_patterns.get("hit_day_1"):
                logger.warning(
                    f"⚠️ No patterns data from DataService for method {method.id}"
                )
                return self._get_method_historical_data_fallback(
                    method, target_date, days_back
                )

            method_id_str = str(method.id)

            # ✅ KIỂM TRA method có data không
            if method_id_str not in historical_patterns["hit_day_1"]:
                logger.warning(f"⚠️ Method {method.id} not found in patterns data")
                return self._get_method_historical_data_fallback(
                    method, target_date, days_back
                )

            # ✅ CONVERT patterns data thành format historical_data
            historical_data = self._convert_patterns_to_historical_data(
                patterns=historical_patterns,
                method_id=method.id,
                target_date=target_date,
            )

            logger.info(
                f"📈 Built {len(historical_data)} historical records for method {method.id} from DataService"
            )
            return historical_data

        except Exception as e:
            logger.error(
                f"❌ Error getting historical data for method {method.id}: {e}"
            )
            return self._get_method_historical_data_fallback(
                method, target_date, days_back
            )

    def _convert_patterns_to_historical_data(
        self,
        patterns: Dict[str, Dict[str, List[int]]],
        method_id: int,
        target_date: date,
    ) -> List[Dict]:
        """
        ✅ CHUYỂN ĐỔI patterns data thành format historical_data

        Args:
            patterns: Dict từ DataService với format:
                {
                    "hit_day_1": {method_id: [0,1,0,1,...]},
                    "hit_day_2": {method_id: [0,0,1,0,...]},
                    "hit_day_3": {method_id: [1,0,0,1,...]}
                }
            method_id: ID của method
            target_date: Ngày target để tính dates

        Returns:
            List[Dict]: Historical data với format cũ
        """
        try:
            method_id_str = str(method_id)

            # Lấy data cho method này
            day1_data = patterns.get("hit_day_1", {}).get(method_id_str, [])
            day2_data = patterns.get("hit_day_2", {}).get(method_id_str, [])
            day3_data = patterns.get("hit_day_3", {}).get(method_id_str, [])

            # ✅ VALIDATE data length consistency
            max_length = max(len(day1_data), len(day2_data), len(day3_data))
            if max_length == 0:
                logger.warning(f"⚠️ No data for method {method_id} in patterns")
                return []

            # ✅ PAD shorter arrays với 0
            while len(day1_data) < max_length:
                day1_data.append(0)
            while len(day2_data) < max_length:
                day2_data.append(0)
            while len(day3_data) < max_length:
                day3_data.append(0)

            # ✅ CONVERT patterns thành historical records
            historical_data = []

            # Tạo dates từ target_date trở về trước
            for i in range(max_length):
                prediction_date = target_date - timedelta(days=max_length - i)

                # Tạo record cho mỗi tracking day
                for tracking_day in [1, 2, 3]:
                    evaluation_date = prediction_date + timedelta(days=tracking_day)

                    # Lấy hit data cho tracking day này
                    if tracking_day == 1:
                        hit_value = day1_data[i]
                    elif tracking_day == 2:
                        hit_value = day2_data[i]
                    else:  # tracking_day == 3
                        hit_value = day3_data[i]

                    # Tạo historical record
                    historical_record = {
                        "session_id": f"generated_{prediction_date.isoformat()}",
                        "prediction_date": prediction_date,
                        "evaluation_date": evaluation_date,
                        "tracking_day": tracking_day,
                        "hit_rate": hit_value * 100.0,  # Convert 0/1 to percentage
                        "hit_count": hit_value,
                        "wilson_score": hit_value * 0.8,  # Estimated wilson score
                        "predicted_numbers": [],  # Không có chi tiết numbers
                        "actual_numbers": [],
                        "hit_numbers": [] if hit_value == 0 else ["XX"],  # Placeholder
                        "overall_confidence": 0.5,  # Default confidence
                    }

                    historical_data.append(historical_record)

            logger.info(
                f"✅ Converted {len(historical_data)} pattern records to historical format for method {method_id}"
            )
            return historical_data

        except Exception as e:
            logger.error(
                f"❌ Error converting patterns to historical data for method {method_id}: {e}"
            )
            return []

    def _get_method_historical_data_fallback(
        self, method: PredictionMethod, target_date: date, days_back: int = 90
    ) -> List[Dict]:
        """
        ✅ FALLBACK: Query trực tiếp từ DB như version cũ
        """
        try:
            end_date = target_date
            start_date = end_date - timedelta(days=days_back)

            logger.info(
                f"🔍 FALLBACK: Direct DB query for method {method.id} from {start_date} to {end_date}"
            )

            # Query sessions trực tiếp
            sessions = (
                DailyTrackingSession.objects.filter(
                    prediction_date__range=[start_date, end_date],
                    method_results__method=method,
                )
                .prefetch_related("method_results", "method_results__evaluations")
                .distinct()
            )

            logger.info(
                f"📊 FALLBACK: Found {sessions.count()} sessions for method {method.id}"
            )

            if sessions.count() == 0:
                logger.warning(f"❌ FALLBACK: No sessions found for method {method.id}")
                return []

            # Xây dựng historical data
            historical_data = []
            for session in sessions:
                method_result = session.method_results.filter(method=method).first()
                if not method_result:
                    continue

                # Lấy evaluations cho method này
                evaluations = method_result.evaluations.all()

                for evaluation in evaluations:
                    tracking_day = (
                        evaluation.evaluation_date - session.prediction_date
                    ).days
                    if 1 <= tracking_day <= 3:
                        historical_data.append(
                            {
                                "session_id": session.id,
                                "prediction_date": session.prediction_date,
                                "evaluation_date": evaluation.evaluation_date,
                                "tracking_day": tracking_day,
                                "hit_rate": evaluation.hit_rate,
                                "hit_count": evaluation.hit_count,
                                "wilson_score": evaluation.wilson_score,
                                "predicted_numbers": method_result.base_prediction_numbers,
                                "actual_numbers": evaluation.actual_numbers,
                                "hit_numbers": evaluation.hit_numbers,
                                "overall_confidence": evaluation.method_result.overall_confidence,
                            }
                        )

            logger.info(
                f"📈 FALLBACK: Built {len(historical_data)} historical records for method {method.id}"
            )
            return historical_data

        except Exception as e:
            logger.error(
                f"❌ FALLBACK: Error getting historical data for method {method.id}: {e}"
            )
            return []

    def _analyze_day_patterns(
        self,
        historical_data: List[Dict],
        tracking_day: int,
        method: PredictionMethod,
        target_date: date,
    ) -> Dict[str, Any]:
        """
        Phân tích patterns cho ngày tracking cụ thể
        """
        # Lọc dữ liệu cho tracking_day cụ thể
        day_data = [d for d in historical_data if d["tracking_day"] == tracking_day]

        if len(day_data) < 5:
            return {
                "probability": 0.3,  # Default low probability
                "confidence": 0.2,
                "predicted_numbers": [],
                "hit_rate_trend": "insufficient_data",
                "pattern_strength": 0.0,
                "sample_size": len(day_data),
            }

        # Tính các metrics
        hit_rates = [d["hit_rate"] for d in day_data]
        hit_counts = [d["hit_count"] for d in day_data]
        wilson_scores = [d["wilson_score"] for d in day_data]

        # ML prediction với features
        features = self._extract_day_features(day_data, tracking_day)
        probability = self._predict_day_probability_ml(features, hit_rates)

        # Confidence dựa trên consistency và sample size
        confidence = self._calculate_day_confidence(
            hit_rates, wilson_scores, len(day_data)
        )

        # Trend analysis
        hit_rate_trend = self._analyze_trend(hit_rates)

        # Pattern strength
        pattern_strength = self._calculate_pattern_strength(day_data)

        # Dự đoán số cho ngày này
        predicted_numbers = self._predict_numbers_for_day(
            day_data, target_date, tracking_day
        )

        return {
            "probability": float(probability),
            "confidence": float(confidence),
            "predicted_numbers": predicted_numbers,
            "hit_rate_trend": hit_rate_trend,
            "pattern_strength": float(pattern_strength),
            "sample_size": len(day_data),
            "avg_hit_rate": float(np.mean(hit_rates)),
            "avg_hit_count": float(np.mean(hit_counts)),
            "consistency_score": float(
                1.0 - np.std(hit_rates) / (np.mean(hit_rates) + 1e-6)
            ),
        }

    def _extract_day_features(
        self, day_data: List[Dict], tracking_day: int
    ) -> np.ndarray:
        """
        Trích xuất features cho ML prediction
        """
        if not day_data:
            return np.array([0.0] * 10)

        features = []

        # Basic statistics
        hit_rates = [d["hit_rate"] for d in day_data]
        features.extend(
            [
                np.mean(hit_rates),
                np.std(hit_rates),
                np.max(hit_rates),
                np.min(hit_rates),
            ]
        )

        # Trend features
        if len(hit_rates) >= 3:
            recent_avg = (
                np.mean(hit_rates[-5:])
                if len(hit_rates) >= 5
                else np.mean(hit_rates[-3:])
            )
            older_avg = (
                np.mean(hit_rates[:-5])
                if len(hit_rates) >= 10
                else np.mean(hit_rates[:-3])
            )
            trend_slope = recent_avg - older_avg
        else:
            trend_slope = 0

        features.append(trend_slope)

        # Temporal features
        features.extend(
            [
                tracking_day,  # Which tracking day (1, 2, or 3)
                len(day_data),  # Sample size
            ]
        )

        # Confidence features
        confidences = [d["overall_confidence"] for d in day_data]
        features.extend(
            [
                np.mean(confidences),
                np.std(confidences),
            ]
        )

        # Pattern consistency
        hit_counts = [d["hit_count"] for d in day_data]
        consistency = 1.0 - (np.std(hit_counts) / (np.mean(hit_counts) + 1e-6))
        features.append(consistency)

        return np.array(features)

    def _predict_day_probability_ml(
        self, features: np.ndarray, hit_rates: List[float]
    ) -> float:
        """
        Dự đoán xác suất bằng ML
        """
        try:
            if len(hit_rates) < 5:
                return np.mean(hit_rates) / 100.0 if hit_rates else 0.3

            # Chuẩn bị dữ liệu training đơn giản
            X = features.reshape(1, -1)

            # Tính probability dựa trên weighted average với trend
            base_prob = np.mean(hit_rates) / 100.0

            # Adjust dựa trên trend
            recent_performance = (
                np.mean(hit_rates[-3:]) if len(hit_rates) >= 3 else base_prob * 100
            )
            trend_adjustment = (recent_performance - np.mean(hit_rates)) / 100.0 * 0.3

            probability = max(0.1, min(0.9, base_prob + trend_adjustment))

            return probability

        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return np.mean(hit_rates) / 100.0 if hit_rates else 0.3

    def _calculate_day_confidence(
        self, hit_rates: List[float], wilson_scores: List[float], sample_size: int
    ) -> float:
        """
        Tính confidence dựa trên consistency và sample size
        """
        if not hit_rates:
            return 0.2

        # Base confidence từ wilson scores
        base_confidence = np.mean(wilson_scores) if wilson_scores else 0.3

        # Consistency bonus
        if len(hit_rates) > 1:
            consistency = 1.0 - (np.std(hit_rates) / (np.mean(hit_rates) + 1e-6))
            consistency_bonus = consistency * 0.2
        else:
            consistency_bonus = 0

        # Sample size factor
        size_factor = min(1.0, sample_size / 20.0)  # Full confidence at 20+ samples

        confidence = (base_confidence + consistency_bonus) * size_factor
        return max(0.1, min(0.95, confidence))

    def _analyze_trend(self, values: List[float]) -> str:
        """
        Phân tích trend của hit rates
        """
        if len(values) < 3:
            return "insufficient_data"

        recent = np.mean(values[-3:])
        older = np.mean(values[:-3]) if len(values) > 3 else recent

        diff = recent - older
        if diff > 2:
            return "improving"
        elif diff < -2:
            return "declining"
        else:
            return "stable"

    def _calculate_pattern_strength(self, day_data: List[Dict]) -> float:
        """
        Tính strength của pattern
        """
        if len(day_data) < 3:
            return 0.0

        hit_rates = [d["hit_rate"] for d in day_data]

        # Pattern strength dựa trên consistency và performance
        avg_performance = np.mean(hit_rates) / 100.0
        consistency = 1.0 - (np.std(hit_rates) / (np.mean(hit_rates) + 1e-6))

        return avg_performance * 0.7 + consistency * 0.3

    def _predict_numbers_for_day(
        self, day_data: List[Dict], target_date: date, tracking_day: int
    ) -> List[str]:
        """
        Dự đoán số cụ thể cho ngày tracking
        """
        if not day_data:
            return []

        # Phân tích frequency của numbers đã hit
        number_frequency = Counter()
        for data in day_data:
            for num in data["hit_numbers"]:
                number_frequency[num] += 1

        # Lấy top numbers
        top_numbers = [num for num, freq in number_frequency.most_common(10)]

        # Bổ sung thêm từ predicted_numbers gần đây
        recent_predictions = []
        for data in day_data[-5:]:  # 5 predictions gần nhất
            recent_predictions.extend(data["predicted_numbers"])

        recent_counter = Counter(recent_predictions)
        recent_top = [num for num, freq in recent_counter.most_common(5)]

        # Kết hợp
        result = top_numbers + [num for num in recent_top if num not in top_numbers]

        return result[:8]  # Giới hạn 8 số

    def _find_best_tracking_day(self, day_analysis: Dict[str, Dict]) -> int:
        """
        Tìm ngày tracking tốt nhất
        """
        best_day = 1
        best_score = 0

        for day_key, analysis in day_analysis.items():
            day_num = int(day_key.split("_")[1])

            # Tính composite score
            score = (
                analysis["probability"] * 0.4
                + analysis["confidence"] * 0.3
                + analysis["pattern_strength"] * 0.2
                + min(analysis["sample_size"] / 20.0, 1.0) * 0.1
            )

            if score > best_score:
                best_score = score
                best_day = day_num

        return best_day

    def _calculate_overall_confidence(
        self, day_analysis: Dict[str, Dict], historical_data: List[Dict]
    ) -> float:
        """
        Tính overall confidence cho method
        """
        # Confidence từ best day
        best_day_key = f"day_{self._find_best_tracking_day(day_analysis)}"
        best_day_confidence = day_analysis[best_day_key]["confidence"]

        # Data quality factor
        data_quality = min(
            len(historical_data) / 30.0, 1.0
        )  # Full quality at 30+ points

        # Consistency across days
        day_confidences = [analysis["confidence"] for analysis in day_analysis.values()]
        consistency = 1.0 - (
            np.std(day_confidences) / (np.mean(day_confidences) + 1e-6)
        )

        overall = best_day_confidence * 0.6 + data_quality * 0.2 + consistency * 0.2
        return max(0.1, min(0.95, overall))

    def _analyze_method_patterns(
        self, historical_data: List[Dict], method: PredictionMethod
    ) -> Dict[str, Any]:
        """
        Phân tích patterns chi tiết của method
        """
        if not historical_data:
            return {"error": "no_data"}

        # Cycle analysis
        cycle_performance = defaultdict(list)
        for data in historical_data:
            day_of_week = data["evaluation_date"].weekday()
            cycle_performance[day_of_week].append(data["hit_rate"])

        best_weekday = (
            max(cycle_performance.keys(), key=lambda k: np.mean(cycle_performance[k]))
            if cycle_performance
            else 0
        )

        # Gap analysis - tìm khoảng cách trung bình giữa các hit
        hit_dates = [
            data["evaluation_date"] for data in historical_data if data["hit_count"] > 0
        ]
        if len(hit_dates) >= 2:
            gaps = [
                (hit_dates[i + 1] - hit_dates[i]).days
                for i in range(len(hit_dates) - 1)
            ]
            avg_gap = np.mean(gaps)
            last_hit_days_ago = (
                (historical_data[-1]["evaluation_date"] - hit_dates[-1]).days
                if hit_dates
                else 999
            )
        else:
            avg_gap = 0
            last_hit_days_ago = 999

        # Frequency analysis
        all_numbers = []
        for data in historical_data:
            all_numbers.extend(data["hit_numbers"])

        number_frequency = Counter(all_numbers)
        top_frequent_numbers = [num for num, freq in number_frequency.most_common(10)]

        return {
            "cycle_analysis": {
                "best_weekday": best_weekday,
                "weekday_performance": {
                    k: np.mean(v) for k, v in cycle_performance.items()
                },
            },
            "gap_analysis": {
                "avg_gap_days": float(avg_gap),
                "last_hit_days_ago": last_hit_days_ago,
                "gap_trend": (
                    "overdue" if last_hit_days_ago > avg_gap * 1.5 else "normal"
                ),
            },
            "frequency_analysis": {
                "top_numbers": top_frequent_numbers,
                "number_diversity": len(set(all_numbers)),
                "total_hits": len(all_numbers),
            },
        }

    def _analyze_historical_performance(
        self, historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Phân tích hiệu suất lịch sử
        """
        if not historical_data:
            return {"error": "no_data"}

        hit_rates = [d["hit_rate"] for d in historical_data]
        hit_counts = [d["hit_count"] for d in historical_data]

        # Performance metrics
        performance = {
            "avg_hit_rate": float(np.mean(hit_rates)),
            "max_hit_rate": float(np.max(hit_rates)),
            "min_hit_rate": float(np.min(hit_rates)),
            "std_hit_rate": float(np.std(hit_rates)),
            "avg_hit_count": float(np.mean(hit_counts)),
            "total_evaluations": len(historical_data),
        }

        # Trend analysis
        if len(hit_rates) >= 10:
            recent_avg = np.mean(hit_rates[-5:])
            older_avg = np.mean(hit_rates[:-5])
            trend_direction = (
                "improving"
                if recent_avg > older_avg + 1
                else "declining" if recent_avg < older_avg - 1 else "stable"
            )
        else:
            trend_direction = "insufficient_data"

        # Reliability score
        reliability = 1.0 - (np.std(hit_rates) / (np.mean(hit_rates) + 1e-6))

        performance.update(
            {
                "trend_direction": trend_direction,
                "reliability_score": float(reliability),
                "performance_category": self._categorize_performance(
                    np.mean(hit_rates), reliability
                ),
            }
        )

        return performance

    def _categorize_performance(self, avg_hit_rate: float, reliability: float) -> str:
        """
        Phân loại hiệu suất method
        """
        if avg_hit_rate >= 25 and reliability >= 0.7:
            return "excellent"
        elif avg_hit_rate >= 20 and reliability >= 0.6:
            return "good"
        elif avg_hit_rate >= 15 and reliability >= 0.5:
            return "average"
        elif avg_hit_rate >= 10:
            return "poor"
        else:
            return "very_poor"

    def _create_fallback_analysis(
        self, method: PredictionMethod, target_date: date
    ) -> Dict[str, Any]:
        """
        ✅ TẠO fallback analysis khi không có dữ liệu
        """
        return {
            "method_id": method.id,
            "method_name": method.name,
            "day_predictions": {
                "day_1": {
                    "probability": 0.1,
                    "confidence": 0.0,
                    "predicted_numbers": [],
                },
                "day_2": {
                    "probability": 0.1,
                    "confidence": 0.0,
                    "predicted_numbers": [],
                },
                "day_3": {
                    "probability": 0.1,
                    "confidence": 0.0,
                    "predicted_numbers": [],
                },
            },
            "recommended_day": 1,
            "overall_confidence": 0.0,
            "pattern_analysis": {
                "data_source": "fallback",
                "error": "insufficient_data",
            },
            "historical_performance": {
                "trend_direction": "unknown",
                "performance_category": "no_data",
                "reliability_score": 0.0,
            },
            "data_quality": {
                "total_sessions": 0,
                "avg_hit_rate": 0.0,
                "analysis_date": target_date.isoformat(),
                "data_source": "fallback",
            },
        }

    def analyze_multiple_methods_ml_with_data(
        self,
        method_ids: List[int],
        target_date: date,
        historical_patterns: Dict[str, Dict[str, List[int]]],
        data_quality: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        ✅ Phân tích ML với dữ liệu historical đã được chuẩn bị sẵn

        Args:
            method_ids: List[int] - Method IDs to analyze
            target_date: date - Target date for analysis
            historical_patterns: Dict - Historical data với format:
                {
                    "hit_day_1": {method_id: [0,1,0,1,...]},
                    "hit_day_2": {method_id: [0,0,1,0,...]},
                    "hit_day_3": {method_id: [1,0,0,1,...]}
                }
            data_quality: Dict - Quality metrics của historical data

        Returns:
            Dict[str, Any] - Analysis results for each method
        """
        results = {}

        try:
            logger.info(f"🔬 Analyzing {len(method_ids)} methods with pre-loaded data")

            # ✅ VALIDATE input
            if not historical_patterns or not historical_patterns.get("hit_day_1"):
                logger.error("❌ No historical patterns provided")
                return results

            # ✅ FETCH method objects
            methods = PredictionMethod.objects.filter(id__in=method_ids, is_active=True)

            if not methods.exists():
                logger.warning(f"❌ No active methods found for IDs: {method_ids}")
                return results

            # ✅ ANALYZE each method với pre-loaded data
            for method in methods:
                try:
                    # ✅ SỬA: Convert method.id to string để match keys
                    method_id_str = str(method.id)

                    # Kiểm tra method có dữ liệu không
                    if method_id_str not in historical_patterns["hit_day_1"]:
                        logger.warning(
                            f"⚠️ No data for method {method.id} in historical patterns"
                        )
                        # ✅ TẠO FALLBACK ANALYSIS
                        results[method_id_str] = self._create_fallback_analysis(
                            method, target_date
                        )
                        continue

                    # Lấy dữ liệu cho method này
                    day1_data = historical_patterns["hit_day_1"][method_id_str]
                    day2_data = historical_patterns.get("hit_day_2", {}).get(
                        method_id_str, []
                    )
                    day3_data = historical_patterns.get("hit_day_3", {}).get(
                        method_id_str, []
                    )

                    logger.info(
                        f"🔬 Method {method.id}: day1={len(day1_data)}, day2={len(day2_data)}, day3={len(day3_data)} points"
                    )

                    # ✅ VALIDATE data quality cho method này
                    if len(day1_data) < 5:
                        logger.warning(
                            f"⚠️ Insufficient data for method {method.id}: {len(day1_data)} points"
                        )
                        results[method_id_str] = self._create_fallback_analysis(
                            method, target_date
                        )
                        continue

                    # ✅ PHÂN TÍCH ML với dữ liệu sẵn có
                    analysis = self._analyze_method_ml_patterns_with_data(
                        method=method,
                        target_date=target_date,
                        day1_data=day1_data,
                        day2_data=day2_data,
                        day3_data=day3_data,
                        data_quality=data_quality,
                    )

                    results[method_id_str] = analysis
                    logger.info(f"✅ Successfully analyzed method {method.id}")

                except Exception as e:
                    logger.error(f"❌ Error analyzing method {method.id}: {e}")
                    results[str(method.id)] = self._create_fallback_analysis(
                        method, target_date
                    )
                    continue

            logger.info(
                f"✅ ML analysis with pre-loaded data completed: {len(results)} methods processed"
            )
            return results

        except Exception as e:
            logger.error(
                f"❌ Critical error in analyze_multiple_methods_ml_with_data: {e}"
            )
            return results

    def _analyze_method_ml_patterns_with_data(
        self,
        method: PredictionMethod,
        target_date: date,
        day1_data: List[int],
        day2_data: List[int],
        day3_data: List[int],
        data_quality: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        ✅ Phân tích ML patterns với dữ liệu đã chuẩn bị sẵn
        """
        try:
            logger.info(
                f"🔬 Analyzing method {method.name} with pre-loaded data: "
                f"day1={len(day1_data)}, day2={len(day2_data)}, day3={len(day3_data)}"
            )

            # ✅ TẠO date context
            date_context = {
                "day_of_week": target_date.weekday(),
                "day_of_month": target_date.day,
                "month": target_date.month,
                "is_weekend": target_date.weekday() >= 5,
            }

            # ✅ CALCULATE adaptive weights based on data quality
            time_weights = self._calculate_adaptive_weights_from_quality(data_quality)

            # ✅ APPLY time weights to data
            weighted_day1 = self._apply_time_weights_to_data(day1_data, time_weights)
            weighted_day2 = self._apply_time_weights_to_data(day2_data, time_weights)
            weighted_day3 = self._apply_time_weights_to_data(day3_data, time_weights)

            # ✅ EXTRACT enhanced features
            features = self._extract_enhanced_features_from_data(
                weighted_day1, weighted_day2, weighted_day3, date_context, time_weights
            )

            # ✅ ANALYZE each day
            day_analysis = {}
            for day_idx, (orig_data, weighted_data) in enumerate(
                [
                    (day1_data, weighted_day1),
                    (day2_data, weighted_day2),
                    (day3_data, weighted_day3),
                ],
                1,
            ):
                day_analysis[f"day_{day_idx}"] = self._predict_single_day_enhanced(
                    features=features,
                    day_data=orig_data,
                    weighted_data=weighted_data,
                    day_number=day_idx,
                    date_context=date_context,
                    time_weights=time_weights,
                )

            # ✅ FIND best day
            best_day = self._find_best_tracking_day(day_analysis)

            # ✅ CALCULATE overall confidence
            overall_confidence = self._calculate_overall_confidence_enhanced(
                day_analysis, len(day1_data), data_quality
            )

            # ✅ PATTERN analysis
            pattern_analysis = self._analyze_patterns_from_data(
                day1_data, day2_data, day3_data, method
            )

            # ✅ HISTORICAL performance
            historical_performance = self._analyze_performance_from_data(
                day1_data, day2_data, day3_data
            )

            # ✅ BUILD result với schema nhất quán
            result = {
                "method_id": method.id,
                "method_name": method.name,
                "day_predictions": day_analysis,
                "recommended_day": best_day,
                "overall_confidence": overall_confidence,
                "pattern_analysis": pattern_analysis,
                "historical_performance": historical_performance,
                "data_quality": {
                    "total_sessions": len(day1_data),
                    "avg_hit_rate": np.mean(
                        [
                            sum(day1_data) / len(day1_data) if day1_data else 0,
                            sum(day2_data) / len(day2_data) if day2_data else 0,
                            sum(day3_data) / len(day3_data) if day3_data else 0,
                        ]
                    ),
                    "data_range_days": data_quality.get(
                        "avg_data_points", len(day1_data)
                    ),
                    "analysis_date": target_date.isoformat(),
                    "data_source": "pre_loaded_historical",
                },
            }

            logger.info(
                f"✅ ML analysis completed for {method.name}: "
                f"best_day={best_day}, confidence={overall_confidence:.3f}"
            )

            return result

        except Exception as e:
            logger.error(
                f"❌ Error in _analyze_method_ml_patterns_with_data for method {method.id}: {e}"
            )
            return self._create_fallback_analysis(method, target_date)

    def _calculate_adaptive_weights_from_quality(
        self, data_quality: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Tính adaptive weights từ data quality metrics"""
        avg_data_points = data_quality.get("avg_data_points", 30)
        valid_methods = data_quality.get("valid_methods", 1)

        # Recent boost dựa trên quality
        recent_boost = 1.5 if valid_methods >= 5 else 1.2
        quality_multiplier = min(2.0, max(0.5, valid_methods / 10.0))

        return {
            "recent_boost": recent_boost,
            "quality_multiplier": quality_multiplier,
            "data_points": int(avg_data_points),
        }

    def _apply_time_weights_to_data(
        self, data: List[int], time_weights: Dict[str, Any]
    ) -> List[int]:
        """Apply time weights to historical data"""
        if not data or len(data) < 5:
            return data

        # Simple approach: boost recent data (last 20%)
        boost_count = max(1, len(data) // 5)
        recent_boost = time_weights.get("recent_boost", 1.0)

        weighted_data = data.copy()

        # Duplicate recent data points based on boost
        if recent_boost > 1.0:
            recent_data = data[-boost_count:]
            extra_copies = int((recent_boost - 1.0) * boost_count)
            weighted_data.extend(recent_data * extra_copies)

        return weighted_data

    def _extract_enhanced_features_from_data(
        self,
        day1_data: List[int],
        day2_data: List[int],
        day3_data: List[int],
        date_context: Dict[str, Any],
        time_weights: Dict[str, Any],
    ) -> Dict[str, float]:
        """Extract enhanced features từ dữ liệu hit patterns"""

        features = {}

        # Basic features
        all_data = day1_data + day2_data + day3_data
        features["total_hits"] = sum(all_data)
        features["hit_rate"] = sum(all_data) / len(all_data) if all_data else 0.0
        features["data_length"] = len(day1_data)

        # Date context features
        features.update(date_context)

        # Time weights features
        features["recent_boost"] = time_weights.get("recent_boost", 1.0)
        features["quality_multiplier"] = time_weights.get("quality_multiplier", 1.0)

        # Day-specific features
        for day_idx, day_data in enumerate([day1_data, day2_data, day3_data], 1):
            prefix = f"day{day_idx}_"

            if day_data:
                features[f"{prefix}hit_rate"] = sum(day_data) / len(day_data)
                features[f"{prefix}recent_hit_rate"] = sum(day_data[-5:]) / min(
                    5, len(day_data)
                )
                features[f"{prefix}variance"] = float(np.var(day_data))
                features[f"{prefix}current_streak"] = self._get_current_streak_fixed(
                    day_data
                )
                features[f"{prefix}days_since_hit"] = (
                    self._get_days_since_last_hit_fixed(day_data)
                )
            else:
                features[f"{prefix}hit_rate"] = 0.0
                features[f"{prefix}recent_hit_rate"] = 0.0
                features[f"{prefix}variance"] = 0.0
                features[f"{prefix}current_streak"] = 0
                features[f"{prefix}days_since_hit"] = 999

        return features

    def analyze_method_ml_patterns(
        self, method: PredictionMethod, target_date: date, days_back: int = 90
    ) -> Dict[str, Any]:
        """
        ✅ SỬA: Sử dụng DataService làm nguồn dữ liệu chính
        """
        try:
            logger.info(
                f"🔬 Starting ML analysis for method {method.name} targeting {target_date}"
            )

            # ✅ VALIDATE INPUT
            if not method:
                logger.error("❌ Method is None")
                return self._create_fallback_analysis(method, target_date)

            if not isinstance(target_date, date):
                logger.error(f"❌ Invalid target_date: {target_date}")
                return self._create_fallback_analysis(method, target_date)

            # ✅ 1. TRY DataService FIRST
            try:

                months_back = max(1, days_back // 30)

                # Get comprehensive historical data
                historical_patterns = data_service.get_comprehensive_historical_data(
                    target_date=target_date.isoformat(),
                    method_ids=[method.id],
                    months_back=months_back,
                )

                if historical_patterns and historical_patterns.get("hit_day_1"):
                    method_id_str = str(method.id)

                    if method_id_str in historical_patterns["hit_day_1"]:
                        logger.info(f"✅ Using DataService data for method {method.id}")

                        # ✅ SỬ DỤNG analyze_method_ml_patterns_with_data
                        return self._analyze_method_ml_patterns_with_data(
                            method=method,
                            target_date=target_date,
                            day1_data=historical_patterns["hit_day_1"][method_id_str],
                            day2_data=historical_patterns.get("hit_day_2", {}).get(
                                method_id_str, []
                            ),
                            day3_data=historical_patterns.get("hit_day_3", {}).get(
                                method_id_str, []
                            ),
                            data_quality={
                                "avg_data_points": len(
                                    historical_patterns["hit_day_1"][method_id_str]
                                )
                            },
                        )

                logger.warning(
                    f"⚠️ DataService has no data for method {method.id}, using fallback"
                )

            except ImportError:
                logger.warning("⚠️ DataService not available, using fallback query")
            except Exception as ds_error:
                logger.warning(f"⚠️ DataService error: {ds_error}, using fallback")

            # ✅ 2. FALLBACK: Original method
            try:
                historical_data = self._get_method_historical_data_fallback(
                    method, target_date, days_back
                )

                if not historical_data or len(historical_data) < 10:
                    logger.warning(
                        f"⚠️ Insufficient historical data for method {method.id}: {len(historical_data) if historical_data else 0} records"
                    )
                    return self._create_fallback_analysis(method, target_date)

                logger.info(
                    f"📊 Retrieved {len(historical_data)} historical records for method {method.id}"
                )

            except Exception as e:
                logger.error(
                    f"❌ Error retrieving historical data for method {method.id}: {e}"
                )
                return self._create_fallback_analysis(method, target_date)

            # ✅ 3. CONTINUE với original analysis logic
            # ... rest of original method logic

            # ✅ Phân tích patterns cho từng ngày
            day_analysis = {}
            for tracking_day in [1, 2, 3]:
                try:
                    day_analysis[f"day_{tracking_day}"] = self._analyze_day_patterns(
                        historical_data, tracking_day, method, target_date
                    )
                except Exception as e:
                    logger.error(
                        f"❌ Error analyzing day {tracking_day} for method {method.id}: {e}"
                    )
                    day_analysis[f"day_{tracking_day}"] = {
                        "probability": 0.0,
                        "confidence": 0.0,
                        "predicted_numbers": [],
                        "hit_rate_trend": "error",
                        "pattern_strength": 0.0,
                        "sample_size": 0,
                    }

            # ✅ Continue với rest of logic...
            best_day = self._find_best_tracking_day(day_analysis)
            overall_confidence = self._calculate_overall_confidence(
                day_analysis, historical_data
            )

            # Build final result
            result = {
                "method_id": method.id,
                "method_name": method.name,
                "day_predictions": day_analysis,
                "recommended_day": best_day,
                "overall_confidence": overall_confidence,
                "data_quality": {
                    "total_sessions": len(historical_data),
                    "data_source": "fallback_query",
                    "analysis_date": target_date.isoformat(),
                },
            }

            logger.info(
                f"✅ ML analysis completed for {method.name}: best_day={best_day}, confidence={overall_confidence:.3f}"
            )
            return result

        except Exception as e:
            logger.error(
                f"❌ Critical error in analyze_method_ml_patterns for method {method.id if method else 'None'}: {e}"
            )
            return self._create_fallback_analysis(method, target_date)

    def get_enhanced_ml_predictions(
        self,
        method_ids: List[int],
        target_date: date,
        use_trained_models: bool = True,
        training_months: int = 3,  # ✅ THÊM THAM SỐ MỚI VỚI GIÁ TRỊ MẶC ĐỊNH
    ) -> Dict[str, Any]:
        """
        ✅ SỬ DỤNG TRAINED ML MODELS CHO DỰ ĐOÁN CHÍNH XÁC - SỬA LỖI

        Args:
            method_ids: List[int] - Danh sách ID của các methods cần phân tích
            target_date: date - Ngày dự đoán
            use_trained_models: bool - Có sử dụng pre-trained models không
            training_months: int - Số tháng dữ liệu để train (nếu train mới)

        Returns:
            Dict[str, Any] - Format:
            {
                'success': bool,
                'predictions': Dict[str, Dict],
                'data_source': str,
                'enhanced': bool
            }
        """
        try:
            logger.info(
                f"🤖 Getting enhanced ML predictions for {len(method_ids)} methods"
            )

            # ✅ SỬA: Kiểm tra ML models có sẵn không - SỬA ATTRIBUTE NAME
            has_trained_models = (
                hasattr(self.ml_service, "is_trained")
                and self.ml_service.is_trained
                and hasattr(self.ml_service, "models")
                and self.ml_service.models
                and all(model is not None for model in self.ml_service.models.values())
            )

            if use_trained_models and has_trained_models:
                logger.info("✅ Using trained ML models for predictions")

                predictions = {}

                for method_id in method_ids:
                    try:
                        method = PredictionMethod.objects.get(
                            id=method_id, is_active=True
                        )

                        # Get predicted numbers for this method
                        predicted_numbers = self._get_method_predicted_numbers(
                            method, target_date
                        )

                        # ✅ SỬA: Use ML model service for prediction with training_months
                        ml_prediction = self.ml_service.predict_hit_probability(
                            method=method,
                            target_date=target_date,
                            predicted_numbers=predicted_numbers,
                            training_months=training_months,  # ✅ THÊM THAM SỐ MỚI
                        )

                        predictions[str(method_id)] = ml_prediction

                    except PredictionMethod.DoesNotExist:
                        logger.warning(f"⚠️ Method {method_id} not found or inactive")
                        continue
                    except Exception as e:
                        logger.error(f"❌ Error predicting for method {method_id}: {e}")
                        continue

                return {
                    "success": True,
                    "predictions": predictions,
                    "data_source": "trained_ml_models",
                    "enhanced": True,
                }

            else:
                logger.info(
                    f"⚠️ ML models not available, falling back to pattern-based analysis (training_months={training_months})"
                )

                # ✅ FALLBACK: Tự train và dự đoán thay vì sử dụng pattern analysis
                predictions = {}

                for method_id in method_ids:
                    try:
                        method = PredictionMethod.objects.get(
                            id=method_id, is_active=True
                        )

                        # Train model mới với số tháng được chỉ định
                        days_back = training_months * 30  # Ước lượng số ngày

                        # Phân tích method pattern
                        method_analysis = self.analyze_method_ml_patterns(
                            method=method, target_date=target_date, days_back=days_back
                        )

                        predictions[str(method_id)] = method_analysis

                    except PredictionMethod.DoesNotExist:
                        logger.warning(f"⚠️ Method {method_id} not found or inactive")
                        continue
                    except Exception as e:
                        logger.error(
                            f"❌ Error in fallback analysis for method {method_id}: {e}"
                        )
                        continue

                return {
                    "success": True,
                    "predictions": predictions,
                    "data_source": f"fresh_train_{training_months}_months",
                    "enhanced": True,
                }

        except Exception as e:
            logger.error(f"❌ Error in get_enhanced_ml_predictions: {e}")
            return {
                "success": False,
                "error": str(e),
                "data_source": "error",
                "enhanced": False,
            }

    def _get_method_predicted_numbers(
        self, method: PredictionMethod, target_date: date
    ) -> List[str]:
        """Get predicted numbers for a method (implement based on your logic)"""
        try:
            # ✅ TÌM SESSION GẦN NHẤT VỚI TARGET_DATE
            recent_session = (
                DailyTrackingSession.objects.filter(
                    prediction_date__lte=target_date,  # ✅ Trước hoặc bằng target_date
                    method_results__method=method,
                )
                .order_by("-prediction_date")
                .first()
            )  # ✅ Lấy gần nhất

            if recent_session:
                method_result = recent_session.method_results.filter(
                    method=method
                ).first()
                if method_result and method_result.base_prediction_numbers:
                    logger.info(
                        f"📋 Found {len(method_result.base_prediction_numbers)} predicted numbers for method {method.id}"
                    )
                    return method_result.base_prediction_numbers

            # ✅ FALLBACK: Lấy từ method prediction logic nếu có
            logger.info(
                f"⚠️ No predicted numbers found for method {method.id}, using fallback"
            )
            return []

        except Exception as e:
            logger.error(
                f"❌ Error getting predicted numbers for method {method.id}: {e}"
            )
            return []

    def _get_current_streak_fixed(self, day_data: List[int]) -> int:
        """Tính streak hiện tại (số ngày liên tiếp hit/miss gần nhất)"""
        if not day_data:
            return 0

        current_value = day_data[-1]
        streak = 1

        for i in range(len(day_data) - 2, -1, -1):
            if day_data[i] == current_value:
                streak += 1
            else:
                break

        return streak if current_value == 1 else -streak

    def _get_days_since_last_hit_fixed(self, day_data: List[int]) -> int:
        """Tính số ngày kể từ lần hit cuối cùng"""
        if not day_data:
            return 999

        for i in range(len(day_data) - 1, -1, -1):
            if day_data[i] == 1:
                return len(day_data) - 1 - i

        return 999  # Không tìm thấy hit nào

    def _predict_single_day_enhanced(
        self,
        features: Dict[str, float],
        day_data: List[int],
        weighted_data: List[int],
        day_number: int,
        date_context: Dict[str, Any],
        time_weights: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Enhanced prediction cho một ngày cụ thể"""

        if not day_data:
            return {
                "probability": 0.0,
                "confidence": 0.0,
                "predicted_numbers": [],
                "hit_rate_trend": "no_data",
                "pattern_strength": 0.0,
                "sample_size": 0,
            }

        # Basic metrics
        hit_rate = sum(weighted_data) / len(weighted_data) if weighted_data else 0
        recent_hit_rate = (
            sum(weighted_data[-5:]) / min(5, len(weighted_data)) if weighted_data else 0
        )

        # Enhanced probability calculation
        base_probability = hit_rate

        # Boost dựa trên recent performance
        recent_boost = (recent_hit_rate - hit_rate) * 0.3 if hit_rate > 0 else 0

        # Day-specific adjustment
        day_factor = {1: 1.1, 2: 1.0, 3: 0.9}.get(day_number, 1.0)

        probability = min(0.9, max(0.1, (base_probability + recent_boost) * day_factor))

        # Enhanced confidence calculation
        sample_size_factor = min(1.0, len(day_data) / 20.0)
        consistency = 1.0 - (np.var(weighted_data) if len(weighted_data) > 1 else 0)
        quality_boost = time_weights.get("quality_multiplier", 1.0) - 1.0

        confidence = min(
            0.95,
            max(
                0.1,
                (probability * 0.6 + consistency * 0.3 + quality_boost * 0.1)
                * sample_size_factor,
            ),
        )

        # Trend analysis
        if len(weighted_data) >= 5:
            recent_avg = np.mean(weighted_data[-5:])
            older_avg = (
                np.mean(weighted_data[:-5]) if len(weighted_data) > 5 else recent_avg
            )

            if recent_avg > older_avg + 0.1:
                trend = "improving"
            elif recent_avg < older_avg - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "probability": float(probability),
            "confidence": float(confidence),
            "predicted_numbers": [],  # Có thể implement sau
            "hit_rate_trend": trend,
            "pattern_strength": float(consistency),
            "sample_size": len(day_data),
        }

    def _calculate_overall_confidence_enhanced(
        self,
        day_analysis: Dict[str, Dict],
        data_length: int,
        data_quality: Dict[str, Any],
    ) -> float:
        """Enhanced overall confidence calculation"""

        # Base confidence từ best day
        best_day_key = f"day_{self._find_best_tracking_day(day_analysis)}"
        best_confidence = day_analysis[best_day_key]["confidence"]

        # Data quality factors
        data_factor = min(1.0, data_length / 30.0)
        quality_factor = min(1.0, data_quality.get("valid_methods", 1) / 10.0)

        # Consistency across days
        confidences = [analysis["confidence"] for analysis in day_analysis.values()]
        consistency = 1.0 - (np.std(confidences) / (np.mean(confidences) + 1e-6))

        # Enhanced calculation
        overall = (
            best_confidence * 0.5
            + data_factor * 0.2
            + quality_factor * 0.2
            + consistency * 0.1
        )

        return max(0.1, min(0.95, overall))

    def _analyze_patterns_from_data(
        self,
        day1_data: List[int],
        day2_data: List[int],
        day3_data: List[int],
        method: PredictionMethod,
    ) -> Dict[str, Any]:
        """Phân tích patterns từ hit data"""

        all_data = day1_data + day2_data + day3_data

        if not all_data:
            return {"data_source": "enhanced_fallback", "error": "no_data"}

        # Basic pattern analysis
        total_hits = sum(all_data)
        hit_rate = total_hits / len(all_data)

        # Day performance comparison
        day_rates = []
        for data in [day1_data, day2_data, day3_data]:
            if data:
                day_rates.append(sum(data) / len(data))
            else:
                day_rates.append(0.0)

        best_day = day_rates.index(max(day_rates)) + 1 if day_rates else 1

        return {
            "data_source": "enhanced_patterns",
            "overall_hit_rate": hit_rate,
            "total_data_points": len(all_data),
            "day_performance": {
                "day_1": day_rates[0] if len(day_rates) > 0 else 0,
                "day_2": day_rates[1] if len(day_rates) > 1 else 0,
                "day_3": day_rates[2] if len(day_rates) > 2 else 0,
                "best_day": best_day,
            },
        }

    def _analyze_performance_from_data(
        self, day1_data: List[int], day2_data: List[int], day3_data: List[int]
    ) -> Dict[str, Any]:
        """Phân tích performance từ hit data"""

        all_data = day1_data + day2_data + day3_data

        if not all_data:
            return {"error": "no_data"}

        hit_rate = sum(all_data) / len(all_data)

        # Trend analysis
        if len(all_data) >= 10:
            recent = np.mean(all_data[-5:])
            older = np.mean(all_data[:-5])

            if recent > older + 0.1:
                trend = "improving"
            elif recent < older - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        # Performance categorization
        if hit_rate >= 0.7:
            category = "excellent"
        elif hit_rate >= 0.5:
            category = "good"
        elif hit_rate >= 0.3:
            category = "average"
        elif hit_rate >= 0.1:
            category = "poor"
        else:
            category = "very_poor"

        # Reliability
        reliability = 1.0 - (np.var(all_data) if len(all_data) > 1 else 0)

        return {
            "avg_hit_rate": float(hit_rate * 100),  # Convert to percentage
            "trend_direction": trend,
            "performance_category": category,
            "reliability_score": float(reliability),
            "total_evaluations": len(all_data),
        }

    def _get_current_streak_safe(self, data: List[int]) -> int:
        """Safe version of get current streak"""
        if not data:
            return 0

        current_value = data[-1]
        streak = 0

        for value in reversed(data):
            if value == current_value:
                streak += 1
            else:
                break

        return streak

    def _analyze_from_fallback_patterns(
        self, method: PredictionMethod, target_date: date, patterns_data: Dict
    ) -> Dict[str, Any]:
        """
        ✅ PHÂN TÍCH TỪ FALLBACK PATTERNS - FIXED VERSION
        """
        try:
            method_id = str(method.id)

            # Lấy dữ liệu cho method này
            day1_data = patterns_data.get("hit_day_1", {}).get(method_id, [])
            day2_data = patterns_data.get("hit_day_2", {}).get(method_id, [])
            day3_data = patterns_data.get("hit_day_3", {}).get(method_id, [])

            logger.info(
                f"📊 Fallback analysis for method {method.id}: "
                f"day1={len(day1_data)}, day2={len(day2_data)}, day3={len(day3_data)} points"
            )

            # Phân tích patterns cho từng ngày
            day_analysis = {}
            for day_idx, day_data in enumerate([day1_data, day2_data, day3_data], 1):
                if day_data and len(day_data) >= 5:
                    hit_rate = sum(day_data) / len(day_data)
                    recent_data = day_data[-5:] if len(day_data) >= 5 else day_data
                    recent_hit_rate = sum(recent_data) / len(recent_data)

                    # Confidence dựa trên sample size và consistency
                    confidence = min(0.8, len(day_data) / 20.0)
                    variance = np.var(day_data) if len(day_data) > 1 else 0
                    consistency_bonus = max(0, 0.2 - variance)
                    confidence += consistency_bonus

                    day_analysis[f"day_{day_idx}"] = {
                        "probability": hit_rate,
                        "confidence": confidence,
                        "predicted_numbers": [],
                        "hit_rate_trend": (
                            "improving" if recent_hit_rate > hit_rate else "stable"
                        ),
                        "pattern_strength": 1.0 - variance,
                        "sample_size": len(day_data),
                    }
                else:
                    # ✅ XỬ LÝ TRƯỜNG HỢP KHÔNG ĐỦ DỮ LIỆU
                    day_analysis[f"day_{day_idx}"] = {
                        "probability": 0.0,
                        "confidence": 0.0,
                        "predicted_numbers": [],
                        "hit_rate_trend": "insufficient_data",
                        "pattern_strength": 0.0,
                        "sample_size": len(day_data) if day_data else 0,
                    }

            # Tìm ngày tốt nhất
            if day_analysis:
                best_day = max(
                    day_analysis.keys(), key=lambda k: day_analysis[k]["probability"]
                )
                best_day_num = int(best_day.split("_")[1])
            else:
                best_day_num = 1

            # Tính overall confidence
            confidences = [day_analysis[k]["confidence"] for k in day_analysis.keys()]
            overall_confidence = np.mean(confidences) if confidences else 0.0

            result = {
                "method_id": method.id,
                "method_name": method.name,
                "day_predictions": day_analysis,
                "recommended_day": best_day_num,
                "overall_confidence": overall_confidence,
                "pattern_analysis": {
                    "data_source": "fallback_patterns",
                    "total_data_points": len(day1_data)
                    + len(day2_data)
                    + len(day3_data),
                },
                "historical_performance": {
                    "trend_direction": "stable",
                    "performance_category": "fallback_analysis",
                    "reliability_score": overall_confidence,
                },
                "data_quality": {
                    "total_sessions": len(day1_data),
                    "avg_hit_rate": (
                        np.mean(
                            [
                                sum(data) / len(data)
                                for data in [day1_data, day2_data, day3_data]
                                if data
                            ]
                        )
                        if any([day1_data, day2_data, day3_data])
                        else 0
                    ),
                    "data_range_days": 180,  # 6 months
                    "analysis_date": target_date.isoformat(),
                },
            }

            logger.info(
                f"✅ Fallback analysis completed for method {method.id}: "
                f"best_day={best_day_num}, confidence={overall_confidence:.3f}"
            )

            return result

        except Exception as e:
            logger.error(
                f"❌ Error in _analyze_from_fallback_patterns for method {method.id}: {e}"
            )
            return self._create_fallback_analysis(method, target_date)

    def get_cycle_summary(self, cycle: PredictionCycle) -> Dict[str, Any]:
        """
        Lấy tóm tắt thống kê của chu kỳ
        
        Args:
            cycle: PredictionCycle instance
            
        Returns:
            Dict[str, Any]: {
                "total_sessions": int,
                "completed_sessions": int,
                "completion_rate": float,
                "total_methods": int,
                "active_methods": int,
                "avg_hit_rate": float,
                "best_performing_method": dict,
                "worst_performing_method": dict,
                "timeline": dict,
                "performance_metrics": dict
            }
        """
        try:
            logger.info(f"🔍 Getting cycle summary for cycle {cycle.id}")
            
            # ✅ 1. BASIC CYCLE STATISTICS
            sessions = cycle.daily_sessions.all()
            total_sessions = sessions.count()
            completed_sessions = sessions.filter(status='completed').count()
            completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            # ✅ 2. METHOD STATISTICS
            participations = cycle.cyclemethodparticipation_set.select_related('method').all()
            total_methods = participations.count()
            active_methods = participations.filter(method__is_active=True).count()
            
            # ✅ 3. PERFORMANCE METRICS
            evaluations = TrackingEvaluation.objects.filter(
                session__cycle=cycle
            ).select_related('method_result__method')
            
            if evaluations.exists():
                avg_hit_rate = evaluations.aggregate(
                    avg_rate=Avg('hit_rate')
                )['avg_rate'] or 0
                
                total_evaluations = evaluations.count()
                total_hits = evaluations.aggregate(
                    total_hits=Sum('hit_count')
                )['total_hits'] or 0
                
                # ✅ 4. METHOD PERFORMANCE ANALYSIS
                method_performance = {}
                for evaluation in evaluations:
                    method_id = evaluation.method_result.method.id
                    method_name = evaluation.method_result.method.name
                    
                    if method_id not in method_performance:
                        method_performance[method_id] = {
                            'method_name': method_name,
                            'total_evaluations': 0,
                            'total_hits': 0,
                            'total_hit_rate': 0.0,
                            'avg_hit_rate': 0.0,
                            'wilson_scores': []
                        }
                    
                    method_performance[method_id]['total_evaluations'] += 1
                    method_performance[method_id]['total_hits'] += evaluation.hit_count
                    method_performance[method_id]['total_hit_rate'] += evaluation.hit_rate
                    method_performance[method_id]['wilson_scores'].append(evaluation.wilson_score)
                
                # Calculate averages
                for method_id, perf in method_performance.items():
                    if perf['total_evaluations'] > 0:
                        perf['avg_hit_rate'] = perf['total_hit_rate'] / perf['total_evaluations']
                        perf['avg_wilson_score'] = sum(perf['wilson_scores']) / len(perf['wilson_scores'])
                
                # Find best and worst performing methods
                if method_performance:
                    best_method = max(method_performance.values(), key=lambda x: x['avg_hit_rate'])
                    worst_method = min(method_performance.values(), key=lambda x: x['avg_hit_rate'])
                else:
                    best_method = {'method_name': 'N/A', 'avg_hit_rate': 0.0}
                    worst_method = {'method_name': 'N/A', 'avg_hit_rate': 0.0}
            else:
                avg_hit_rate = 0.0
                total_evaluations = 0
                total_hits = 0
                best_method = {'method_name': 'N/A', 'avg_hit_rate': 0.0}
                worst_method = {'method_name': 'N/A', 'avg_hit_rate': 0.0}
                method_performance = {}  # Ensure method_performance is always defined
            
            # ✅ 5. TIMELINE ANALYSIS
            timeline = {
                'start_date': cycle.start_date.isoformat(),
                'end_date': cycle.end_date.isoformat(),
                'current_date': date.today().isoformat(),
                'days_elapsed': (date.today() - cycle.start_date).days,
                'days_remaining': (cycle.end_date - date.today()).days,
                'progress_percentage': self._calculate_cycle_progress(cycle)
            }
            
            # ✅ 6. PERFORMANCE METRICS
            performance_metrics = {
                'avg_hit_rate': round(avg_hit_rate, 2),
                'total_evaluations': total_evaluations,
                'total_hits': total_hits,
                'hit_success_rate': round((total_hits / total_evaluations) if total_evaluations > 0 else 0, 2),
                'methods_with_data': len(method_performance),
                'tracking_efficiency': round(completion_rate, 2)
            }
            
            cycle_summary = {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'completion_rate': round(completion_rate, 2),
                'total_methods': total_methods,
                'active_methods': active_methods,
                'avg_hit_rate': round(avg_hit_rate, 2),
                'best_performing_method': best_method,
                'worst_performing_method': worst_method,
                'timeline': timeline,
                'performance_metrics': performance_metrics
            }
            
            logger.info(f"✅ Cycle summary generated: {total_sessions} sessions, {total_methods} methods")
            return cycle_summary
            
        except Exception as e:
            logger.error(f"❌ Error getting cycle summary: {e}")
            return {
                'total_sessions': 0,
                'completed_sessions': 0,
                'completion_rate': 0.0,
                'total_methods': 0,
                'active_methods': 0,
                'avg_hit_rate': 0.0,
                'best_performing_method': {'method_name': 'Error', 'avg_hit_rate': 0.0},
                'worst_performing_method': {'method_name': 'Error', 'avg_hit_rate': 0.0},
                'timeline': {
                    'start_date': cycle.start_date.isoformat() if cycle.start_date else '',
                    'end_date': cycle.end_date.isoformat() if cycle.end_date else '',
                    'current_date': date.today().isoformat(),
                    'days_elapsed': 0,
                    'days_remaining': 0,
                    'progress_percentage': 0.0
                },
                'performance_metrics': {
                    'avg_hit_rate': 0.0,
                    'total_evaluations': 0,
                    'total_hits': 0,
                    'hit_success_rate': 0.0,
                    'methods_with_data': 0,
                    'tracking_efficiency': 0.0
                }
            }

    def get_method_comparison(self, cycle: PredictionCycle) -> Dict[str, Any]:
        """
        So sánh hiệu suất các methods trong chu kỳ
        
        Args:
            cycle: PredictionCycle instance
            
        Returns:
            Dict[str, Any]: {
                "methods_comparison": List[Dict],
                "performance_ranking": List[Dict],
                "category_analysis": Dict,
                "trend_analysis": Dict,
                "recommendations": List[Dict]
            }
        """
        try:
            logger.info(f"🔍 Getting method comparison for cycle {cycle.id}")
            
            # ✅ 1. GET ALL METHODS IN CYCLE
            participations = cycle.cyclemethodparticipation_set.select_related('method').all()
            
            if not participations:
                logger.warning(f"⚠️ No methods found in cycle {cycle.id}")
                return {
                    'methods_comparison': [],
                    'performance_ranking': [],
                    'category_analysis': {},
                    'trend_analysis': {},
                    'recommendations': []
                }
            
            # ✅ 2. COLLECT METHOD PERFORMANCE DATA
            methods_comparison = []
            
            for participation in participations:
                method = participation.method
                
                # Get evaluations for this method in this cycle
                evaluations = TrackingEvaluation.objects.filter(
                    session__cycle=cycle,
                    method_result__method=method
                ).order_by('evaluation_date')
                
                if evaluations.exists():
                    # Calculate performance metrics
                    total_evaluations = evaluations.count()
                    total_hits = evaluations.aggregate(Sum('hit_count'))['hit_count__sum'] or 0
                    avg_hit_rate = evaluations.aggregate(Avg('hit_rate'))['hit_rate__avg'] or 0
                    avg_wilson_score = evaluations.aggregate(Avg('wilson_score'))['wilson_score__avg'] or 0
                    
                    # Trend analysis (recent vs older performance)
                    recent_evaluations = evaluations.order_by('-evaluation_date')[:5]
                    recent_avg_hit_rate = recent_evaluations.aggregate(Avg('hit_rate'))['hit_rate__avg'] or 0
                    
                    older_evaluations = evaluations.order_by('-evaluation_date')[5:]
                    older_avg_hit_rate = older_evaluations.aggregate(Avg('hit_rate'))['hit_rate__avg'] or avg_hit_rate
                    
                    # Determine trend
                    if recent_avg_hit_rate > older_avg_hit_rate + 2:
                        trend = 'improving'
                    elif recent_avg_hit_rate < older_avg_hit_rate - 2:
                        trend = 'declining'
                    else:
                        trend = 'stable'
                    
                    # Performance category
                    performance_category = self._categorize_performance(avg_hit_rate, 
                                                                       1.0 - (evaluations.aggregate(Avg('hit_rate'))['hit_rate__avg'] or 0) / 100)
                    
                    # Calculate consistency
                    hit_rates = list(evaluations.values_list('hit_rate', flat=True))
                    consistency = 1.0 - (np.std(hit_rates) / (np.mean(hit_rates) + 1e-6)) if len(hit_rates) > 1 else 0
                    
                else:
                    # No evaluations data
                    total_evaluations = 0
                    total_hits = 0
                    avg_hit_rate = 0.0
                    avg_wilson_score = 0.0
                    recent_avg_hit_rate = 0.0
                    trend = 'no_data'
                    performance_category = 'no_data'
                    consistency = 0.0
                
                method_data = {
                    'method_id': method.id,
                    'method_name': method.name,
                    'method_category': method.get_category_display(),
                    'total_evaluations': total_evaluations,
                    'total_hits': total_hits,
                    'avg_hit_rate': round(avg_hit_rate, 2),
                    'avg_wilson_score': round(avg_wilson_score, 4),
                    'recent_performance': round(recent_avg_hit_rate, 2),
                    'trend': trend,
                    'performance_category': performance_category,
                    'consistency_score': round(consistency, 3),
                    'is_active': method.is_active,
                    'ensemble_enabled': participation.is_ensemble_enabled,
                    'custom_weight': participation.custom_weight
                }
                
                methods_comparison.append(method_data)
            
            # ✅ 3. PERFORMANCE RANKING
            performance_ranking = sorted(
                methods_comparison, 
                key=lambda x: (x['avg_hit_rate'], x['consistency_score']), 
                reverse=True
            )
            
            # ✅ 4. CATEGORY ANALYSIS
            category_analysis = {}
            for method in methods_comparison:
                category = method['method_category']
                if category not in category_analysis:
                    category_analysis[category] = {
                        'count': 0,
                        'avg_hit_rate': 0.0,
                        'best_method': None,
                        'worst_method': None
                    }
                
                category_analysis[category]['count'] += 1
                
                # Calculate average hit rate for category
                category_methods = [m for m in methods_comparison if m['method_category'] == category]
                category_analysis[category]['avg_hit_rate'] = round(
                    sum(m['avg_hit_rate'] for m in category_methods) / len(category_methods), 2
                )
                
                # Find best and worst in category
                category_analysis[category]['best_method'] = max(category_methods, key=lambda x: x['avg_hit_rate'])
                category_analysis[category]['worst_method'] = min(category_methods, key=lambda x: x['avg_hit_rate'])
            
            # ✅ 5. TREND ANALYSIS
            trend_counts = Counter([m['trend'] for m in methods_comparison])
            trend_analysis = {
                'improving_methods': trend_counts.get('improving', 0),
                'declining_methods': trend_counts.get('declining', 0),
                'stable_methods': trend_counts.get('stable', 0),
                'no_data_methods': trend_counts.get('no_data', 0),
                'overall_trend': max(trend_counts.items(), key=lambda x: x[1])[0] if trend_counts else 'no_data'
            }
            
            # ✅ 6. RECOMMENDATIONS
            recommendations = []
            
            # Top performer recommendation
            if performance_ranking:
                top_method = performance_ranking[0]
                if top_method['avg_hit_rate'] > 15:
                    recommendations.append({
                        'type': 'top_performer',
                        'method_name': top_method['method_name'],
                        'recommendation': f"Tăng trọng số cho {top_method['method_name']} (hit rate: {top_method['avg_hit_rate']}%)",
                        'priority': 'high'
                    })
            
            # Underperformer recommendation
            underperformers = [m for m in methods_comparison if m['avg_hit_rate'] < 5 and m['total_evaluations'] > 10]
            if underperformers:
                recommendations.append({
                    'type': 'underperformer',
                    'method_names': [m['method_name'] for m in underperformers],
                    'recommendation': f"Xem xét tạm dừng {len(underperformers)} methods có hiệu suất thấp",
                    'priority': 'medium'
                })
            
            # Improving trend recommendation
            improving_methods = [m for m in methods_comparison if m['trend'] == 'improving']
            if improving_methods:
                recommendations.append({
                    'type': 'improving_trend',
                    'method_names': [m['method_name'] for m in improving_methods],
                    'recommendation': f"Theo dõi chặt chẽ {len(improving_methods)} methods đang cải thiện",
                    'priority': 'low'
                })
            
            result = {
                'methods_comparison': methods_comparison,
                'performance_ranking': performance_ranking,
                'category_analysis': category_analysis,
                'trend_analysis': trend_analysis,
                'recommendations': recommendations
            }
            
            logger.info(f"✅ Method comparison generated: {len(methods_comparison)} methods analyzed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting method comparison: {e}")
            return {
                'methods_comparison': [],
                'performance_ranking': [],
                'category_analysis': {},
                'trend_analysis': {},
                'recommendations': []
            }

    def update_tracking_status(self, session: DailyTrackingSession) -> Dict[str, Any]:
        """
        Cập nhật trạng thái tracking cho session
        
        Args:
            session: DailyTrackingSession instance
            
        Returns:
            Dict[str, Any]: {
                "session_id": str,
                "current_status": str,
                "updated_status": str,
                "tracking_progress": float,
                "completed_evaluations": int,
                "pending_evaluations": int,
                "next_evaluation_date": str,
                "can_advance": bool
            }
        """
        try:
            logger.info(f"🔄 Updating tracking status for session {session.id}")
            
            current_status = session.status
            prediction_date = session.prediction_date
            current_date = date.today()
            
            # ✅ 1. CALCULATE TRACKING PROGRESS
            if hasattr(session, 'cycle') and session.cycle:
                tracking_days = session.cycle.tracking_days
            else:
                tracking_days = 3  # Default
            
            days_since_prediction = (current_date - prediction_date).days
            tracking_progress = min(100.0, (days_since_prediction / tracking_days) * 100)
            
            # ✅ 2. COUNT EVALUATIONS
            total_method_results = session.method_results.count()
            completed_evaluations = session.evaluations.count()
            
            # Calculate expected evaluations (method_results * tracking_days)
            expected_evaluations = total_method_results * tracking_days
            pending_evaluations = max(0, expected_evaluations - completed_evaluations)
            
            # ✅ 3. DETERMINE NEXT EVALUATION DATE
            next_evaluation_date = None
            if days_since_prediction < tracking_days:
                next_evaluation_date = prediction_date + timedelta(days=days_since_prediction + 1)
            
            # ✅ 4. UPDATE STATUS LOGIC
            updated_status = current_status
            can_advance = False
            
            if current_status == 'pending':
                if days_since_prediction >= 0:
                    updated_status = 'in_progress'
                    can_advance = True
            elif current_status == 'in_progress':
                if days_since_prediction >= tracking_days:
                    updated_status = 'completed'
                    can_advance = True
                elif completed_evaluations >= expected_evaluations:
                    updated_status = 'completed'
                    can_advance = True
            
            # ✅ 5. UPDATE SESSION IF NEEDED
            if updated_status != current_status:
                session.status = updated_status
                session.current_tracking_day = min(tracking_days, days_since_prediction)
                session.save()
                
                logger.info(f"✅ Session {session.id} status updated: {current_status} → {updated_status}")
            
            # ✅ 6. BUILD RESPONSE
            tracking_update = {
                'session_id': session.session_id,
                'current_status': current_status,
                'updated_status': updated_status,
                'tracking_progress': round(tracking_progress, 2),
                'completed_evaluations': completed_evaluations,
                'pending_evaluations': pending_evaluations,
                'next_evaluation_date': next_evaluation_date.isoformat() if next_evaluation_date else None,
                'can_advance': can_advance,
                'tracking_days': tracking_days,
                'days_since_prediction': days_since_prediction,
                'prediction_date': prediction_date.isoformat(),
                'total_method_results': total_method_results,
                'expected_evaluations': expected_evaluations
            }
            
            logger.info(f"✅ Tracking status updated: {tracking_progress:.1f}% complete")
            return tracking_update
            
        except Exception as e:
            logger.error(f"❌ Error updating tracking status: {e}")
            return {
                'session_id': session.session_id if hasattr(session, 'session_id') else 'unknown',
                'current_status': 'error',
                'updated_status': 'error',
                'tracking_progress': 0.0,
                'completed_evaluations': 0,
                'pending_evaluations': 0,
                'next_evaluation_date': None,
                'can_advance': False,
                'error': str(e)
            }

    def create_daily_session(self, cycle: PredictionCycle, prediction_date: str) -> DailyTrackingSession:
        """
        Tạo session tracking hàng ngày
        
        Args:
            cycle: PredictionCycle instance
            prediction_date: Ngày dự đoán (string format YYYY-MM-DD)
            
        Returns:
            DailyTrackingSession: Session đã tạo
        """
        try:
            # Convert string date to date object
            if isinstance(prediction_date, str):
                prediction_date_obj = datetime.strptime(prediction_date, '%Y-%m-%d').date()
            else:
                prediction_date_obj = prediction_date
            
            logger.info(f"📅 Creating daily session for cycle {cycle.id} on {prediction_date_obj}")
            
            # ✅ 1. CREATE SESSION
            session = DailyTrackingSession.objects.create(
                cycle=cycle,
                session_id=f"{cycle.cycle_name}_{prediction_date_obj.strftime('%Y%m%d')}",
                prediction_date=prediction_date_obj,
                tracking_start_date=prediction_date_obj,
                tracking_end_date=prediction_date_obj + timedelta(days=cycle.tracking_days),
                status='pending',
                current_tracking_day=0
            )
            
            # ✅ 2. CREATE METHOD RESULTS FOR ALL PARTICIPATING METHODS
            participations = cycle.cyclemethodparticipation_set.select_related('method').all()
            
            for participation in participations:
                method = participation.method
                
                # Generate predictions for this method
                try:
                    # Get method class and generate predictions
                    predicted_numbers = self._generate_method_predictions(method, prediction_date_obj)
                    
                    # Create method result
                    MethodPredictionResult.objects.create(
                        session=session,
                        method=method,
                        base_prediction_numbers=predicted_numbers,
                        overall_confidence=0.5,  # Default confidence
                        prediction_metadata={
                            'generation_date': datetime.now().isoformat(),
                            'method_category': method.category,
                            'ensemble_enabled': participation.is_ensemble_enabled,
                            'custom_weight': participation.custom_weight
                        }
                    )
                    
                    logger.info(f"✅ Created method result for {method.name}")
                    
                except Exception as method_error:
                    logger.error(f"❌ Error creating method result for {method.name}: {method_error}")
                    continue
            
            # ✅ 3. UPDATE SESSION STATUS
            session.status = 'active'
            session.save()
            
            logger.info(f"✅ Daily session created: {session.session_id}")
            return session
            
        except Exception as e:
            logger.error(f"❌ Error creating daily session: {e}")
            raise

    def evaluate_session_performance(self, session: DailyTrackingSession, evaluation_date: date) -> List[TrackingEvaluation]:
        """
        Đánh giá hiệu suất session cho ngày cụ thể
        
        Args:
            session: DailyTrackingSession instance
            evaluation_date: Ngày đánh giá
            
        Returns:
            List[TrackingEvaluation]: List các evaluation đã tạo
        """
        try:
            logger.info(f"📊 Evaluating session {session.id} performance for {evaluation_date}")
            
            # ✅ 1. VALIDATE EVALUATION DATE
            prediction_date = session.prediction_date
            days_after_prediction = (evaluation_date - prediction_date).days
            
            if days_after_prediction < 1 or days_after_prediction > 3:
                logger.warning(f"⚠️ Invalid evaluation date: {evaluation_date} (days after prediction: {days_after_prediction})")
                return []
            
            # ✅ 2. GET ACTUAL RESULTS
            try:
                actual_result = KetQuaXoSo.objects.get(ngay=evaluation_date)
                actual_numbers = set(actual_result.get_all_2digit_numbers())
                logger.info(f"📋 Found {len(actual_numbers)} actual numbers for {evaluation_date}")
            except KetQuaXoSo.DoesNotExist:
                logger.warning(f"⚠️ No actual results found for {evaluation_date}")
                return []
            
            # ✅ 3. EVALUATE EACH METHOD RESULT
            method_results = session.method_results.select_related('method').all()
            evaluations = []
            
            for method_result in method_results:
                try:
                    # Get predicted numbers
                    predicted_numbers = set(method_result.base_prediction_numbers or [])
                    
                    if not predicted_numbers:
                        logger.warning(f"⚠️ No predicted numbers for method {method_result.method.name}")
                        continue
                    
                    # Calculate hits
                    hit_numbers = list(predicted_numbers.intersection(actual_numbers))
                    hit_count = len(hit_numbers)
                    total_predicted = len(predicted_numbers)
                    hit_rate = (hit_count / total_predicted) * 100 if total_predicted > 0 else 0
                    
                    # Calculate Wilson Score (simplified version)
                    wilson_score = self._calculate_wilson_score(hit_count, total_predicted)
                    
                    # Create evaluation
                    evaluation = TrackingEvaluation.objects.create(
                        session=session,
                        method_result=method_result,
                        evaluation_date=evaluation_date,
                        days_after_prediction=days_after_prediction,
                        actual_numbers=list(actual_numbers),
                        predicted_numbers=list(predicted_numbers),
                        hit_numbers=hit_numbers,
                        hit_count=hit_count,
                        total_predicted=total_predicted,
                        hit_rate=hit_rate,
                        wilson_score=wilson_score
                    )
                    
                    evaluations.append(evaluation)
                    
                    logger.info(f"✅ Evaluated {method_result.method.name}: {hit_count}/{total_predicted} hits ({hit_rate:.1f}%)")
                    
                except Exception as method_error:
                    logger.error(f"❌ Error evaluating method {method_result.method.name}: {method_error}")
                    continue
            
            # ✅ 4. UPDATE SESSION STATUS
            if evaluations:
                session.current_tracking_day = days_after_prediction
                session.save()
                
                logger.info(f"✅ Created {len(evaluations)} evaluations for session {session.id}")
            
            return evaluations
            
        except Exception as e:
            logger.error(f"❌ Error evaluating session performance: {e}")
            return []

    def _calculate_cycle_progress(self, cycle: PredictionCycle) -> float:
        """Helper: Tính phần trăm tiến độ của cycle"""
        try:
            start_date = cycle.start_date
            end_date = cycle.end_date
            current_date = date.today()
            
            if current_date < start_date:
                return 0.0
            elif current_date > end_date:
                return 100.0
            else:
                total_days = (end_date - start_date).days
                elapsed_days = (current_date - start_date).days
                return (elapsed_days / total_days) * 100 if total_days > 0 else 0.0
                
        except Exception as e:
            logger.error(f"❌ Error calculating cycle progress: {e}")
            return 0.0

    def _generate_method_predictions(self, method: PredictionMethod, prediction_date: date) -> List[str]:
        """Helper: Generate predictions for a method"""
        try:
            # This is a placeholder - implement based on your method logic
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"❌ Error generating predictions for method {method.name}: {e}")
            return []

    def _calculate_wilson_score(self, hits: int, total: int) -> float:
        """Helper: Calculate Wilson Score for confidence interval"""
        try:
            if total == 0:
                return 0.0
            
            # Simplified Wilson Score calculation
            p = hits / total
            n = total
            z = 1.96  # 95% confidence interval
            
            wilson_score = (p + z*z/(2*n) - z * np.sqrt((p*(1-p) + z*z/(4*n))/n)) / (1 + z*z/n)
            return max(0.0, wilson_score)
            
        except Exception as e:
            logger.error(f"❌ Error calculating Wilson score: {e}")
            return 0.0
   
    
# Singleton instance
tracking_service = TrackingService()
