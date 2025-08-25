import logging
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
from django.db.models import Q
from scipy import stats

from predictions_tracker.core.services.IntelligenceIntegration import (
    DataServiceEnhancer,
)
from predictions_tracker.models import (
    DailyTrackingSession,
    MethodPredictionResult,
    PredictionMethod,
    TrackingEvaluation,
)

logger = logging.getLogger(__name__)
from typing import Optional, Tuple

from sklearn.dummy import DummyClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import PolynomialFeatures, StandardScaler


class DataService:
    """
    ✅ UNIFIED DATA SERVICE CHO ML VÀ PATTERN ANALYSIS
    """

    def __init__(self):
        """✅ KHỞI TẠO DataService với ML capabilities"""
        self.advanced_models = {}
        self.model_performance = {}
        self.feature_transformers = {}  # ✅ THÊM: Lưu feature transformers
        try:
            self.scaler = StandardScaler()
        except ImportError:
            self.scaler = None
            logger.warning("⚠️ StandardScaler not available")
        logger.info("DataService initialized with ML capabilities")

    @staticmethod
    def get_training_data_for_ml(
        months_back: int = 12,
        min_samples_per_method: int = 20,
        method_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """
        ✅ LẤY DỮ LIỆU CHO ML TRAINING - SỬA LỖI QUERY
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=months_back * 30)

            logger.info(f"📅 ML Training data query: {start_date} to {end_date}")

            # ✅ SỬA: Query trực tiếp từ TrackingEvaluation
            query = (
                TrackingEvaluation.objects.filter(
                    evaluation_date__range=[start_date, end_date]
                )
                .select_related("method_result__method", "method_result__session")
                .order_by("evaluation_date")
            )

            if method_ids:
                query = query.filter(method_result__method_id__in=method_ids)

            evaluations = list(query)  # ✅ Convert to list để debug
            eval_count = len(evaluations)

            logger.info(f"📊 Query result: {eval_count} evaluations found")

            if eval_count == 0:
                # ✅ DEBUG: Kiểm tra có evaluation nào trong DB không
                total_evals = TrackingEvaluation.objects.count()
                logger.warning(
                    f"❌ No evaluations in date range. Total evaluations in DB: {total_evals}"
                )

                if total_evals > 0:
                    # Lấy evaluation gần nhất để debug
                    latest_eval = TrackingEvaluation.objects.order_by(
                        "-evaluation_date"
                    ).first()
                    logger.info(
                        f"Latest evaluation date: {latest_eval.evaluation_date}"
                    )

                return []

            # ✅ DEBUG: Log một số evaluations đầu tiên
            logger.info(f"📋 Sample evaluations:")
            for i, eval in enumerate(evaluations[:3]):
                logger.info(
                    f"  Eval {i+1}: Method {eval.method_result.method.id}, "
                    f"Date {eval.evaluation_date}, Hit Count {eval.hit_count}"
                )

            # Process evaluations
            training_samples = []
            method_sample_counts = defaultdict(int)
            processed_count = 0

            for evaluation in evaluations:
                try:
                    method = evaluation.method_result.method
                    session = evaluation.method_result.session

                    # ✅ Tính tracking_day chính xác
                    prediction_date = session.prediction_date
                    evaluation_date = evaluation.evaluation_date
                    tracking_day = (evaluation_date - prediction_date).days

                    # ✅ VALIDATE tracking_day
                    if not (1 <= tracking_day <= 3):
                        logger.debug(
                            f"Skipping eval: invalid tracking_day {tracking_day}"
                        )
                        continue

                    # ✅ Kiểm tra có predicted numbers không
                    predicted_numbers = evaluation.method_result.base_prediction_numbers
                    if not predicted_numbers:
                        logger.debug(f"Skipping eval: no predicted numbers")
                        continue

                    # ✅ Extract features đơn giản
                    features = DataService._extract_ml_features_simple(
                        evaluation, method, session, tracking_day
                    )

                    if not features:
                        logger.debug(f"Skipping eval: no features extracted")
                        continue

                    # Target: hit or miss (1 or 0)
                    target = 1 if evaluation.hit_count > 0 else 0

                    sample = {
                        "method_id": method.id,
                        "prediction_date": prediction_date,
                        "evaluation_date": evaluation_date,
                        "tracking_day": tracking_day,
                        "features": features,
                        "target": target,
                        "hit_count": evaluation.hit_count,
                        "hit_rate": evaluation.hit_rate,
                    }

                    training_samples.append(sample)
                    method_sample_counts[method.id] += 1
                    processed_count += 1

                except Exception as e:
                    logger.warning(
                        f"⚠️ Error processing evaluation {evaluation.id}: {e}"
                    )
                    continue

            logger.info(f"📈 Processed {processed_count}/{eval_count} evaluations")
            logger.info(f"📊 Method sample counts: {dict(method_sample_counts)}")

            # ✅ Filter by min_samples_per_method
            valid_samples = []
            valid_methods = 0

            for sample in training_samples:
                if method_sample_counts[sample["method_id"]] >= min_samples_per_method:
                    valid_samples.append(sample)
                    # Count unique valid methods
                    if sample["method_id"] not in [
                        s["method_id"] for s in valid_samples[:-1]
                    ]:
                        valid_methods += 1

            logger.info(
                f"✅ Final ML training dataset: {len(valid_samples)} samples from {valid_methods} methods"
            )
            logger.info(
                f"📋 Valid methods: {set(s['method_id'] for s in valid_samples)}"
            )

            return valid_samples

        except Exception as e:
            logger.error(f"❌ Error getting ML training data: {e}")
            return []

    @staticmethod
    def _extract_ml_features_simple(
        evaluation: "TrackingEvaluation",
        method: "PredictionMethod",
        session: "DailyTrackingSession",
        tracking_day: int,
    ) -> Dict[str, float]:
        """
        ✅ TRÍCH XUẤT FEATURES ĐƠN GIẢN CHO ML TRAINING
        """
        try:
            features = {}

            # Basic features
            features["hit_count"] = float(evaluation.hit_count)
            features["hit_rate"] = float(evaluation.hit_rate)
            features["total_predicted"] = float(
                len(evaluation.method_result.base_prediction_numbers or [])
            )
            features["tracking_day"] = float(tracking_day)

            # Method features
            features["method_id_hash"] = float(hash(str(method.id)) % 1000)
            features["method_priority"] = float(method.priority)

            # Session features
            features["session_confidence"] = float(
                evaluation.method_result.overall_confidence
            )

            # Date features
            pred_date = session.prediction_date
            features["day_of_week"] = float(pred_date.weekday())
            features["day_of_month"] = float(pred_date.day)
            features["month"] = float(pred_date.month)
            features["is_weekend"] = float(pred_date.weekday() >= 5)

            # ✅ VALIDATE ALL FEATURES ARE NUMBERS
            validated_features = {}
            for key, value in features.items():
                try:
                    validated_features[key] = float(value)
                except (ValueError, TypeError):
                    validated_features[key] = 0.0
                    logger.debug(f"Invalid feature value for {key}: {value}")

            return validated_features

        except Exception as e:
            logger.error(f"❌ Error extracting simple ML features: {e}")
            return {}

    @staticmethod
    def get_pattern_data_for_analysis(
        method_ids: Optional[List[str]],  # ✅ CHANGE: Accept List[str] instead of List[int]
        target_date: str,
        months_back: int = 6,
        min_data_points: int = 5,
    ) -> Dict[str, Dict[str, List[int]]]:
        """
        ✅ CẬP NHẬT: LẤY DỮ LIỆU CHO PATTERN ANALYSIS - SỬA LỖI METHOD_ID VALIDATION
        
        Args:
            method_ids (Optional[List[str]]): List method IDs as strings
            target_date (str): Target date "YYYY-MM-DD"
            months_back (int): Number of months to look back
            min_data_points (int): Minimum data points required per method

        Returns:
            Dict[str, Dict[str, List[int]]]: Pattern data
        """
        try:
            # ✅ Parse target date với fallback
            try:
                end_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except:
                end_date = date.today()

            start_date = end_date - timedelta(days=months_back * 30)

            logger.info(f"📅 Pattern analysis data query: {start_date} to {end_date}")

            # ✅ CLEAN AND VALIDATE METHOD IDS
            valid_method_ids = []
            if method_ids:
                for method_id in method_ids:
                    if method_id is None:
                        continue
                        
                    method_id_str = str(method_id).strip()
                    
                    # Skip invalid values
                    if not method_id_str or method_id_str in ['-', '', 'null', 'undefined']:
                        continue
                        
                    # Try to convert to int for database query
                    try:
                        method_id_int = int(method_id_str)
                        valid_method_ids.append(method_id_int)
                    except ValueError:
                        logger.warning(f"⚠️ Skipping non-numeric method_id: {method_id_str}")
                        continue

            # ✅ QUERY FROM DATABASE
            query = (
                DailyTrackingSession.objects.filter(
                    prediction_date__range=[start_date, end_date]
                )
                .select_related("cycle")
                .prefetch_related(
                    "method_results__method", "method_results__evaluations"
                )
                .order_by("prediction_date")
            )

            # ✅ FILTER BY VALID METHOD IDS
            if valid_method_ids:
                query = query.filter(method_results__method_id__in=valid_method_ids)

            sessions = query.distinct()
            session_count = sessions.count()

            logger.info(f"📊 Found {session_count} sessions for pattern analysis")

            if session_count == 0:
                logger.warning("❌ No sessions found in pattern analysis query")
                return {"hit_day_1": {}, "hit_day_2": {}, "hit_day_3": {}}

            # ✅ PROCESS SESSIONS - REST OF THE METHOD REMAINS THE SAME
            historical_patterns = {
                "hit_day_1": defaultdict(list),
                "hit_day_2": defaultdict(list),
                "hit_day_3": defaultdict(list),
            }

            actual_results_cache = {}
            processed_sessions = 0
            processed_methods = 0

            for session in sessions:
                try:
                    prediction_date = session.prediction_date

                    # ✅ CACHE actual results cho 3 ngày kế tiếp
                    actual_results = {}
                    for day in range(1, 4):
                        tracking_date = prediction_date + timedelta(days=day)
                        cache_key = tracking_date.strftime("%Y-%m-%d")

                        if cache_key not in actual_results_cache:
                            try:
                                from results.models import KetQuaXoSo
                                result = KetQuaXoSo.objects.get(ngay=tracking_date)
                                actual_results_cache[cache_key] = set(
                                    result.get_all_2digit_numbers()
                                )
                            except:
                                actual_results_cache[cache_key] = set()

                        actual_results[day] = actual_results_cache[cache_key]

                    # ✅ XỬ LÝ từng method result
                    for method_result in session.method_results.all():
                        try:
                            method_id = method_result.method.id
                            
                            # ✅ SKIP if method not in valid list
                            if valid_method_ids and method_id not in valid_method_ids:
                                continue
                            
                            predicted_numbers = set(
                                method_result.base_prediction_numbers or []
                            )

                            if not predicted_numbers:
                                continue

                            day_hits = [0, 0, 0]

                            # ✅ Tính hit pattern cho 3 ngày
                            for day in range(1, 4):
                                if actual_results[day]:
                                    hit_count = len(
                                        predicted_numbers.intersection(
                                            actual_results[day]
                                        )
                                    )
                                    if hit_count > 0:
                                        day_hits[day - 1] = 1

                            # ✅ THÊM VÀO PATTERN theo đúng thứ tự
                            method_id_str = str(method_id)
                            historical_patterns["hit_day_1"][method_id_str].append(
                                day_hits[0]
                            )
                            historical_patterns["hit_day_2"][method_id_str].append(
                                day_hits[1]
                            )
                            historical_patterns["hit_day_3"][method_id_str].append(
                                day_hits[2]
                            )

                            processed_methods += 1

                        except Exception as method_error:
                            logger.warning(
                                f"⚠️ Error processing method result {method_result.id}: {method_error}"
                            )
                            continue

                    processed_sessions += 1

                except Exception as session_error:
                    logger.warning(
                        f"⚠️ Error processing session {session.id}: {session_error}"
                    )
                    continue

            logger.info(
                f"📈 Processed {processed_sessions}/{session_count} sessions, {processed_methods} method results"
            )

            # ✅ Convert to regular dict and filter by min_data_points
            result = {}
            for day_key in ["hit_day_1", "hit_day_2", "hit_day_3"]:
                result[day_key] = {}
                for method_id, data in historical_patterns[day_key].items():
                    if len(data) >= min_data_points:
                        result[day_key][method_id] = data

            valid_methods = len(result["hit_day_1"])
            logger.info(
                f"✅ Pattern analysis data: {valid_methods} methods with ≥{min_data_points} data points"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Error getting pattern analysis data: {e}")
            return {"hit_day_1": {}, "hit_day_2": {}, "hit_day_3": {}}
        
    @staticmethod
    def get_comprehensive_historical_data(
        target_date: str, method_ids: Optional[List[int]] = None, months_back: int = 6
    ) -> Dict[str, Dict[str, List[int]]]:
        """
        ✅ WRAPPER METHOD để tương thích với _get_comprehensive_historical_data
        Sử dụng cùng logic với get_pattern_data_for_analysis

        Args:
            target_date (str): Target date "YYYY-MM-DD"
            method_ids (Optional[List[int]]): List method IDs to filter
            months_back (int): Number of months to look back

        Returns:
            Dict[str, Dict[str, List[int]]]: Same format as get_pattern_data_for_analysis
        """
        return self.get_pattern_data_for_analysis(
            target_date=target_date,
            method_ids=method_ids,
            months_back=months_back,
            min_data_points=1,  # No minimum filter for historical data
        )

    @staticmethod
    def validate_pattern_data_quality(
        patterns_data: Dict[str, Dict[str, List[int]]],
        min_methods: int = 5,
        min_data_points: int = 10,
    ) -> Dict[str, Any]:
        """
        ✅ THÊM: Validate chất lượng pattern data

        Args:
            patterns_data: Pattern data from get_pattern_data_for_analysis
            min_methods: Minimum methods required
            min_data_points: Minimum data points per method

        Returns:
            Dict[str, Any]: Quality assessment result
        """
        try:
            total_methods = len(patterns_data.get("hit_day_1", {}))
            valid_methods = 0
            total_data_points = 0
            diversity_scores = []

            for method_id in patterns_data.get("hit_day_1", {}).keys():
                day1_data = patterns_data["hit_day_1"][method_id]
                day2_data = patterns_data.get("hit_day_2", {}).get(method_id, [])
                day3_data = patterns_data.get("hit_day_3", {}).get(method_id, [])

                # Check sufficient data
                if len(day1_data) >= min_data_points:
                    all_data = day1_data + day2_data + day3_data
                    unique_values = set(all_data)

                    # Check diversity (có cả hit và miss)
                    if len(unique_values) >= 2:
                        valid_methods += 1
                        total_data_points += len(day1_data)

                        # Calculate diversity score
                        hit_rate = sum(all_data) / len(all_data)
                        diversity = (
                            min(hit_rate, 1 - hit_rate) * 2
                        )  # Max = 1 when hit_rate = 0.5
                        diversity_scores.append(diversity)

            avg_data_points = (
                total_data_points / valid_methods if valid_methods > 0 else 0
            )
            avg_diversity = np.mean(diversity_scores) if diversity_scores else 0

            is_sufficient = (
                total_methods >= min_methods
                and valid_methods >= min_methods
                and avg_diversity >= 0.1  # At least some diversity
            )

            return {
                "is_sufficient": is_sufficient,
                "total_methods": total_methods,
                "valid_methods": valid_methods,
                "avg_data_points": avg_data_points,
                "avg_diversity": avg_diversity,
                "quality_score": (valid_methods / max(min_methods, 1)) * avg_diversity,
                "recommendation": (
                    "sufficient"
                    if is_sufficient
                    else (
                        "insufficient_methods"
                        if valid_methods < min_methods
                        else "insufficient_diversity"
                    )
                ),
            }

        except Exception as e:
            logger.error(f"❌ Error validating pattern data quality: {e}")
            return {
                "is_sufficient": False,
                "error": str(e),
                "total_methods": 0,
                "valid_methods": 0,
            }

    def _extract_cyclical_features(
        self, day1: List[int], day2: List[int], day3: List[int]
    ) -> Dict[str, float]:
        """
        ✅ TRÍCH XUẤT ĐẶC TRƯNG CHU KỲ

        Returns:
            Dict[str, float] - Cyclical features với keys rõ ràng
        """
        features = {}

        for day_idx, data in enumerate([day1, day2, day3], 1):
            if len(data) < 7:
                continue

            # Phân tích chu kỳ theo tuần (7 ngày)
            weekly_pattern = np.array([data[i::7] for i in range(7)])
            features[f"day{day_idx}_weekly_variance"] = float(
                np.var([np.mean(week) for week in weekly_pattern])
            )

            # Chu kỳ theo tháng (30 ngày)
            if len(data) >= 30:
                monthly_chunks = [
                    data[i : i + 30] for i in range(0, len(data) - 29, 30)
                ]
                features[f"day{day_idx}_monthly_consistency"] = float(
                    1.0 - np.std([np.mean(chunk) for chunk in monthly_chunks])
                )

            # Auto-correlation với lag khác nhau
            for lag in [1, 3, 7, 14]:
                if len(data) > lag:
                    correlation = np.corrcoef(data[:-lag], data[lag:])[0, 1]
                    features[f"day{day_idx}_autocorr_lag{lag}"] = float(
                        correlation if not np.isnan(correlation) else 0.0
                    )

        return features

    def train_advanced_prediction_model(
        self,
        hit_patterns: Dict[str, Dict[str, List[int]]],
        prediction_horizon: int = 1,
        use_enhanced_features: bool = True,  # ✅ THÊM THAM SỐ MỚI
    ) -> Dict[str, Any]:
        """
        ✅ TRAIN advanced prediction model với Enhanced Features
        """
        try:
            logger.info("🤖 Training ADVANCED prediction model with Enhanced Features")

            if not hit_patterns:
                return {"training_completed": False, "error": "No training data"}

            # ✅ IMPORT enhanced feature service
            from .EnhancedFeatureService import enhanced_feature_service

            # ✅ PREPARE training data với enhanced features
            training_data = []
            labels = []

            method_ids = list(hit_patterns.get("hit_day_1", {}).keys())

            for method_id in method_ids:
                try:
                    # ✅ EXTRACT enhanced features
                    if use_enhanced_features:
                        features = enhanced_feature_service.extract_comprehensive_features(
                            method_id=int(method_id),
                            target_date=date.today(),  # Will be updated per prediction
                            historical_patterns=hit_patterns,
                            prediction_horizon=prediction_horizon,
                        )
                    else:
                        # ✅ FALLBACK to basic features
                        features = self._extract_basic_features(hit_patterns, method_id)

                    # ✅ PREPARE training samples cho từng ngày
                    for day_key in ["day_1", "day_2", "day_3"]:
                        if day_key in features:
                            day_features = features[day_key]

                            # ✅ CONVERT features to array
                            feature_vector = [
                                day_features.get(fname, 0.0)
                                for fname in sorted(day_features.keys())
                            ]

                            # ✅ GET target labels
                            day_num = int(day_key.split("_")[1])
                            target_data = hit_patterns.get(
                                f"hit_day_{day_num}", {}
                            ).get(method_id, [])

                            if target_data:
                                # ✅ CREATE training samples
                                for i in range(len(target_data) - prediction_horizon):
                                    training_data.append(feature_vector)
                                    labels.append(target_data[i + prediction_horizon])

                except Exception as method_error:
                    logger.warning(
                        f"⚠️ Error processing method {method_id}: {method_error}"
                    )
                    continue

            if not training_data:
                return {"training_completed": False, "error": "No valid training data"}

            # ✅ TRAIN models cho từng ngày
            self.advanced_models = {}

            for day_num in [1, 2, 3]:
                try:
                    # ✅ FILTER data for this day
                    day_indices = [
                        i
                        for i, (_, day_key) in enumerate(
                            [
                                (method_id, day_key)
                                for method_id in method_ids
                                for day_key in ["day_1", "day_2", "day_3"]
                            ]
                        )
                        if day_key == f"day_{day_num}"
                    ]

                    if not day_indices:
                        continue

                    day_training_data = [training_data[i] for i in day_indices]
                    day_labels = [labels[i] for i in day_indices]

                    # ✅ TRAIN model for this day
                    model = self._train_day_model(
                        day_training_data, day_labels, day_num
                    )
                    self.advanced_models[f"day_{day_num}"] = model

                except Exception as day_error:
                    logger.error(f"❌ Error training day {day_num} model: {day_error}")
                    continue

            # ✅ STORE feature names
            if training_data:
                sample_features = (
                    enhanced_feature_service.extract_comprehensive_features(
                        method_id=int(method_ids[0]),
                        target_date=date.today(),
                        historical_patterns=hit_patterns,
                    )
                )

                if sample_features and "day_1" in sample_features:
                    self.feature_names = sorted(sample_features["day_1"].keys())

            logger.info(
                f"✅ Advanced training completed with {len(self.advanced_models)} models"
            )

            return {
                "training_completed": True,
                "models_trained": len(self.advanced_models),
                "feature_count": (
                    len(self.feature_names) if hasattr(self, "feature_names") else 0
                ),
                "training_samples": len(training_data),
                "enhanced_features": use_enhanced_features,
            }

        except Exception as e:
            logger.error(f"❌ Error in advanced model training: {e}")
            return {"training_completed": False, "error": str(e)}

    def _train_day_model(
        self, training_data: List[List[float]], labels: List[int], day_num: int
    ):
        """
        ✅ TRAIN model cho một ngày cụ thể
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler

            # ✅ SPLIT data
            X_train, X_test, y_train, y_test = train_test_split(
                training_data, labels, test_size=0.2, random_state=42, stratify=labels
            )

            # ✅ SCALE features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # ✅ TRAIN model
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight="balanced",  # ✅ HANDLE class imbalance
            )

            model.fit(X_train_scaled, y_train)

            # ✅ EVALUATE model
            train_score = model.score(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)

            logger.info(
                f"📊 Day {day_num} model - Train: {train_score:.3f}, Test: {test_score:.3f}"
            )

            return {
                "model": model,
                "scaler": scaler,
                "train_score": train_score,
                "test_score": test_score,
                "feature_importance": model.feature_importances_.tolist(),
            }

        except Exception as e:
            logger.error(f"❌ Error training day {day_num} model: {e}")
            return None

    def _create_training_fallback(self) -> Dict[str, Any]:
        """
        ✅ TẠO FALLBACK RESPONSE KHI TRAINING THẤT BẠI

        Returns:
            Dict[str, Any] - Fallback training result với schema nhất quán
        """
        return {
            "training_completed": False,
            "models_trained": [],
            "performance": {},
            "training_samples": 0,
            "error": "insufficient_training_data",
            "fallback_reason": "training_data_preparation_failed",
            "recommendations": [
                "Cần ít nhất 50 samples per day để train model",
                "Kiểm tra data quality và completeness",
                "Thử giảm min_data_points hoặc tăng months_back",
            ],
        }

    def _prepare_day_specific_data(
        self, training_data: List[Dict], target_day: int, prediction_horizon: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        ✅ CHUẨN BỊ DỮ LIỆU CHO NGÀY CỤ THỂ

        Args:
            training_data: List[Dict] - Training samples từ _prepare_advanced_training_data
            target_day: int - Ngày target (1, 2, hoặc 3)
            prediction_horizon: int - Prediction horizon

        Returns:
            Tuple[np.ndarray, np.ndarray] - (X, y) cho training
        """
        try:
            X_list = []
            y_list = []

            logger.info(
                f"📊 Preparing data for day {target_day} from {len(training_data)} samples"
            )

            for sample in training_data:
                try:
                    # Lấy features
                    features = sample.get("features", {})
                    if not features:
                        continue

                    # Lấy target cho ngày cụ thể
                    targets = sample.get("targets", {})
                    target_key = f"day_{target_day}"

                    if target_key not in targets:
                        continue

                    target_value = targets[target_key]

                    # Convert features dict thành array
                    feature_vector = self._convert_features_to_vector(features)

                    if feature_vector is not None and len(feature_vector) > 0:
                        X_list.append(feature_vector)
                        y_list.append(int(target_value))  # Ensure binary classification

                except Exception as e:
                    logger.warning(f"⚠️ Error processing sample: {e}")
                    continue

            if len(X_list) == 0:
                logger.error(f"❌ No valid samples for day {target_day}")
                return np.array([]), np.array([])

            X = np.array(X_list)
            y = np.array(y_list)

            logger.info(
                f"✅ Prepared data for day {target_day}: X shape {X.shape}, y distribution: {np.bincount(y)}"
            )

            return X, y

        except Exception as e:
            logger.error(f"❌ Error preparing day-specific data: {e}")
            return np.array([]), np.array([])

    def _advanced_feature_engineering(
        self, X: np.ndarray, target_day: int = None, is_training: bool = True
    ) -> np.ndarray:
        """
        ✅ FEATURE ENGINEERING NÂNG CAO - SỬA LỖI FEATURE COUNT MISMATCH

        Args:
            X: np.ndarray - Raw feature matrix
            target_day: int - Target day for model-specific transformers
            is_training: bool - True nếu đang training, False nếu đang predict

        Returns:
            np.ndarray - Engineered feature matrix với số features nhất quán
        """
        try:
            if len(X) == 0:
                return X

            logger.debug(
                f"🔧 Feature engineering - Input shape: {X.shape}, Training: {is_training}"
            )

            # 1. Standardization
            scaler_key = f"scaler_{target_day}" if target_day else "scaler_default"

            if is_training:
                # ✅ TRAINING: Fit và lưu scaler
                if not hasattr(self, "feature_transformers"):
                    self.feature_transformers = {}

                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                self.feature_transformers[scaler_key] = scaler
                logger.debug(f"✅ Fitted and saved scaler for {scaler_key}")
            else:
                # ✅ PREDICTION: Sử dụng scaler đã fit
                if (
                    hasattr(self, "feature_transformers")
                    and scaler_key in self.feature_transformers
                ):
                    scaler = self.feature_transformers[scaler_key]
                    X_scaled = scaler.transform(X)
                    logger.debug(f"✅ Used existing scaler for {scaler_key}")
                else:
                    logger.warning(
                        f"⚠️ No fitted scaler found for {scaler_key}, using identity transform"
                    )
                    X_scaled = X

            # 2. Polynomial features (degree 2 cho important features)
            poly_key = f"poly_{target_day}" if target_day else "poly_default"

            try:
                from sklearn.preprocessing import PolynomialFeatures

                if is_training:
                    # ✅ TRAINING: Fit polynomial features
                    important_indices = list(
                        range(min(10, X_scaled.shape[1]))
                    )  # First 10 features

                    if len(important_indices) > 0:
                        poly = PolynomialFeatures(
                            degree=2, include_bias=False, interaction_only=True
                        )
                        X_important = X_scaled[:, important_indices]
                        X_poly = poly.fit_transform(X_important)

                        # Combine original scaled features với polynomial features
                        X_engineered = np.hstack([X_scaled, X_poly])

                        # ✅ LƯU polynomial transformer
                        self.feature_transformers[poly_key] = {
                            "transformer": poly,
                            "important_indices": important_indices,
                        }
                        logger.debug(
                            f"✅ Fitted and saved polynomial features for {poly_key}"
                        )
                    else:
                        X_engineered = X_scaled
                        self.feature_transformers[poly_key] = None
                else:
                    # ✅ PREDICTION: Sử dụng polynomial transformer đã fit
                    if (
                        hasattr(self, "feature_transformers")
                        and poly_key in self.feature_transformers
                        and self.feature_transformers[poly_key] is not None
                    ):

                        poly_info = self.feature_transformers[poly_key]
                        poly = poly_info["transformer"]
                        important_indices = poly_info["important_indices"]

                        X_important = X_scaled[:, important_indices]
                        X_poly = poly.transform(X_important)
                        X_engineered = np.hstack([X_scaled, X_poly])

                        logger.debug(
                            f"✅ Used existing polynomial features for {poly_key}"
                        )
                    else:
                        logger.warning(
                            f"⚠️ No fitted polynomial transformer found for {poly_key}"
                        )
                        X_engineered = X_scaled

            except ImportError:
                logger.warning(
                    "⚠️ PolynomialFeatures not available, using scaled features only"
                )
                X_engineered = X_scaled

            # 3. Feature selection (remove low variance features)
            selector_key = (
                f"selector_{target_day}" if target_day else "selector_default"
            )

            try:
                from sklearn.feature_selection import VarianceThreshold

                if is_training:
                    # ✅ TRAINING: Fit feature selector
                    selector = VarianceThreshold(threshold=0.01)
                    X_selected = selector.fit_transform(X_engineered)

                    # ✅ LƯU feature selector
                    self.feature_transformers[selector_key] = selector
                    logger.debug(
                        f"✅ Fitted and saved feature selector for {selector_key}"
                    )
                else:
                    # ✅ PREDICTION: Sử dụng selector đã fit
                    if (
                        hasattr(self, "feature_transformers")
                        and selector_key in self.feature_transformers
                    ):

                        selector = self.feature_transformers[selector_key]
                        X_selected = selector.transform(X_engineered)
                        logger.debug(
                            f"✅ Used existing feature selector for {selector_key}"
                        )
                    else:
                        logger.warning(f"⚠️ No fitted selector found for {selector_key}")
                        X_selected = X_engineered

            except ImportError:
                logger.warning(
                    "⚠️ VarianceThreshold not available, using engineered features as-is"
                )
                X_selected = X_engineered

            logger.debug(
                f"✅ Feature engineering completed: {X.shape} -> {X_selected.shape}"
            )
            return X_selected

        except Exception as e:
            logger.error(f"❌ Error in feature engineering: {e}")
            # Return scaled features as fallback
            try:
                if is_training:
                    return self.scaler.fit_transform(X) if self.scaler else X
                else:
                    return self.scaler.transform(X) if self.scaler else X
            except:
                return X

    def _train_single_model(self, X: np.ndarray, y: np.ndarray, target_day: int):
        """
        ✅ TRAIN SINGLE MODEL - SỬA LỖI FEATURE ENGINEERING

        Args:
            X: np.ndarray - Feature matrix (RAW features, chưa qua engineering)
            y: np.ndarray - Target vector
            target_day: int - Target day number

        Returns:
            Trained model hoặc None nếu thất bại
        """
        try:
            logger.info(f"🔬 Training single model for day {target_day}")

            # ✅ SỬA: Apply feature engineering với target_day specific và is_training=True
            X_processed = self._advanced_feature_engineering(
                X, target_day=target_day, is_training=True
            )

            # Kiểm tra class balance
            unique_classes, class_counts = np.unique(y, return_counts=True)
            logger.info(
                f"📊 Class distribution for day {target_day}: {dict(zip(unique_classes, class_counts))}"
            )
            logger.info(
                f"📏 Final training features shape for day {target_day}: {X_processed.shape}"
            )

            # Chọn thuật toán dựa trên data size và class balance
            if len(X_processed) < 100:
                # Small dataset: use simple model
                from sklearn.linear_model import LogisticRegression

                model = LogisticRegression(
                    random_state=42,
                    max_iter=1000,
                    class_weight="balanced",  # Handle class imbalance
                )
            elif len(unique_classes) < 2:
                # Only one class: create dummy classifier
                from sklearn.dummy import DummyClassifier

                model = DummyClassifier(strategy="most_frequent")
                logger.warning(
                    f"⚠️ Only one class found for day {target_day}, using dummy classifier"
                )
            else:
                # Larger dataset: use Random Forest
                from sklearn.ensemble import RandomForestClassifier

                model = RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    class_weight="balanced",
                    max_depth=10,  # Prevent overfitting
                    min_samples_split=5,
                    min_samples_leaf=2,
                )

            # ✅ Train model với processed features
            model.fit(X_processed, y)

            logger.info(
                f"✅ Single model trained successfully for day {target_day} with {X_processed.shape[1]} features"
            )
            return model

        except Exception as e:
            logger.error(f"❌ Error training single model for day {target_day}: {e}")

            # Fallback: dummy classifier
            try:
                from sklearn.dummy import DummyClassifier

                dummy = DummyClassifier(strategy="most_frequent")
                dummy.fit(X, y)  # Use raw features for dummy
                logger.info(f"🔄 Using dummy classifier fallback for day {target_day}")
                return dummy
            except:
                return None

    def _validate_model_performance(
        self, model, X: np.ndarray, y: np.ndarray, target_day: int
    ) -> Dict[str, Any]:
        """
        ✅ VALIDATE MODEL PERFORMANCE - SỬA LỖI FEATURE ENGINEERING

        Args:
            model: Trained model
            X: np.ndarray - Feature matrix (RAW features, chưa qua engineering)
            y: np.ndarray - Target vector
            target_day: int - Target day number

        Returns:
            Dict[str, float] - Performance metrics với schema nhất quán
        """
        try:
            if model is None or len(X) == 0:
                return {
                    "accuracy": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1_score": 0.0,
                    "roc_auc": 0.5,
                    "cross_val_score_mean": 0.0,
                    "cross_val_score_std": 0.0,
                    "sample_size": 0,
                    "validation_method": "insufficient_data",
                }

            logger.info(f"🎯 Validating model performance for day {target_day}")

            # ✅ SỬA: Apply cùng feature engineering như training với is_training=False
            X_processed = self._advanced_feature_engineering(
                X, target_day=target_day, is_training=False
            )

            # Basic metrics
            sample_size = len(X_processed)
            unique_classes = np.unique(y)

            # Cross-validation if enough data
            if sample_size >= 20 and len(unique_classes) >= 2:
                try:
                    cv_scores = cross_val_score(
                        model,
                        X_processed,
                        y,
                        cv=min(5, sample_size // 4),
                        scoring="accuracy",
                    )
                    cv_mean = float(np.mean(cv_scores))
                    cv_std = float(np.std(cv_scores))
                    validation_method = "cross_validation"
                except Exception as cv_error:
                    logger.warning(f"⚠️ Cross-validation failed: {cv_error}")
                    cv_mean = 0.0
                    cv_std = 0.0
                    validation_method = "cv_failed"
            else:
                cv_mean = 0.0
                cv_std = 0.0
                validation_method = "insufficient_data_for_cv"

            # Train set performance (for reference)
            try:
                y_pred = model.predict(X_processed)
                y_pred_proba = (
                    model.predict_proba(X_processed)[:, 1]
                    if hasattr(model, "predict_proba") and len(unique_classes) >= 2
                    else None
                )

                # Calculate metrics
                from sklearn.metrics import (
                    accuracy_score,
                    f1_score,
                    precision_score,
                    recall_score,
                    roc_auc_score,
                )

                accuracy = float(accuracy_score(y, y_pred))

                # Handle binary classification metrics
                if len(unique_classes) >= 2:
                    precision = float(
                        precision_score(y, y_pred, average="binary", zero_division=0)
                    )
                    recall = float(
                        recall_score(y, y_pred, average="binary", zero_division=0)
                    )
                    f1 = float(f1_score(y, y_pred, average="binary", zero_division=0))

                    # ROC AUC
                    if y_pred_proba is not None:
                        try:
                            roc_auc = float(roc_auc_score(y, y_pred_proba))
                        except:
                            roc_auc = 0.5
                    else:
                        roc_auc = 0.5
                else:
                    precision = recall = f1 = 0.0
                    roc_auc = 0.5

            except Exception as metrics_error:
                logger.warning(f"⚠️ Error calculating metrics: {metrics_error}")
                accuracy = precision = recall = f1 = 0.0
                roc_auc = 0.5

            performance = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "roc_auc": roc_auc,
                "cross_val_score_mean": cv_mean,
                "cross_val_score_std": cv_std,
                "sample_size": sample_size,
                "validation_method": validation_method,
                "unique_classes": len(unique_classes),
                "class_distribution": dict(zip(*np.unique(y, return_counts=True))),
                "final_features_count": X_processed.shape[
                    1
                ],  # ✅ THÊM: Log final feature count
            }

            logger.info(
                f"✅ Model validation completed for day {target_day}: "
                f"accuracy={accuracy:.3f}, cv_score={cv_mean:.3f}±{cv_std:.3f}, "
                f"features={X_processed.shape[1]}"
            )

            return performance

        except Exception as e:
            logger.error(
                f"❌ Error validating model performance for day {target_day}: {e}"
            )
            return {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "roc_auc": 0.5,
                "cross_val_score_mean": 0.0,
                "cross_val_score_std": 0.0,
                "sample_size": 0,
                "validation_method": "error",
                "error": str(e),
            }

    def _prepare_advanced_training_data(
        self, hit_patterns: Dict[str, Dict[str, List[int]]], prediction_horizon: int
    ) -> List[Dict]:
        """
        ✅ CHUẨN BỊ DỮ LIỆU TRAINING - SỬA LỖI GỌI HÀM

        Returns:
            List[Dict] - Training samples với schema nhất quán:
            [
                {
                    "method_id": str,
                    "features": Dict[str, float],
                    "targets": {
                        "day_1": int,
                        "day_2": int,
                        "day_3": int
                    },
                    "context_window": int
                }
            ]
        """
        training_samples = []

        # ✅ VALIDATE INPUT FORMAT theo quy tắc
        if not hit_patterns or not isinstance(hit_patterns, dict):
            logger.error(f"❌ Invalid hit_patterns format: {type(hit_patterns)}")
            return []

        # ✅ ENSURE hit_day_1 exists and is dict
        if "hit_day_1" not in hit_patterns or not isinstance(
            hit_patterns["hit_day_1"], dict
        ):
            logger.error(
                f"❌ hit_day_1 not found or invalid: {hit_patterns.get('hit_day_1', 'Missing')}"
            )
            return []

        logger.info(
            f"📊 Processing {len(hit_patterns['hit_day_1'])} methods for training data"
        )

        for method_id in hit_patterns["hit_day_1"].keys():
            try:
                # ✅ SỬA: Đảm bảo lấy data từ dict đúng cách
                day1_data = hit_patterns["hit_day_1"].get(method_id, [])
                day2_data = hit_patterns.get("hit_day_2", {}).get(method_id, [])
                day3_data = hit_patterns.get("hit_day_3", {}).get(method_id, [])

                # ✅ VALIDATE data types theo quy tắc
                if not all(
                    isinstance(data, list) for data in [day1_data, day2_data, day3_data]
                ):
                    logger.warning(f"⚠️ Invalid data types for method {method_id}")
                    continue

                if len(day1_data) < 15:  # Need at least 15 points for sliding window
                    logger.debug(
                        f"⚠️ Insufficient data for method {method_id}: {len(day1_data)} points"
                    )
                    continue

                # Sliding window approach
                window_size = 14  # 2 tuần context

                for i in range(window_size, len(day1_data) - prediction_horizon):
                    try:
                        # Context window (14 ngày trước đó)
                        context_d1 = day1_data[i - window_size : i]
                        context_d2 = (
                            day2_data[i - window_size : i]
                            if i < len(day2_data)
                            else [0] * window_size
                        )
                        context_d3 = (
                            day3_data[i - window_size : i]
                            if i < len(day3_data)
                            else [0] * window_size
                        )

                        # Target (ngày cần dự đoán)
                        target_idx = i + prediction_horizon - 1
                        if target_idx < len(day1_data):
                            target_d1 = day1_data[target_idx]
                        else:
                            continue

                        if target_idx < len(day2_data):
                            target_d2 = day2_data[target_idx]
                        else:
                            target_d2 = 0

                        if target_idx < len(day3_data):
                            target_d3 = day3_data[target_idx]
                        else:
                            target_d3 = 0

                        # ✅ SỬA: Gọi instance method với self
                        features = self.extract_advanced_features(
                            hit_patterns={
                                "hit_day_1": context_d1,
                                "hit_day_2": context_d2,
                                "hit_day_3": context_d3,
                            },
                            method_id=method_id,
                        )

                        if features:
                            training_samples.append(
                                {
                                    "method_id": method_id,
                                    "features": features,
                                    "targets": {
                                        "day_1": target_d1,
                                        "day_2": target_d2,
                                        "day_3": target_d3,
                                    },
                                    "context_window": i,
                                }
                            )

                    except Exception as window_error:
                        logger.warning(
                            f"⚠️ Error processing window {i} for method {method_id}: {window_error}"
                        )
                        continue

            except Exception as method_error:
                logger.error(f"❌ Error processing method {method_id}: {method_error}")
                continue

        logger.info(f"✅ Generated {len(training_samples)} training samples")
        return training_samples

    def extract_advanced_features(
        self, hit_patterns: Dict[str, List[int]], method_id: str
    ) -> Dict[str, float]:
        """
        ✅ TRÍCH XUẤT ĐẶC TRƯNG NÂNG CAO - INSTANCE METHOD

        Args:
            hit_patterns: Dict[str, List[int]] - Format:
                {
                    "hit_day_1": [0,1,0,1,...],
                    "hit_day_2": [0,0,1,0,...],
                    "hit_day_3": [1,0,0,1,...]
                }
            method_id: str - Method ID

        Returns:
            Dict[str, float] - Advanced features với keys rõ ràng
        """
        features = {}

        try:
            # ✅ SỬA: Lấy dữ liệu trực tiếp từ hit_patterns
            day1_data = hit_patterns.get("hit_day_1", [])
            day2_data = hit_patterns.get("hit_day_2", [])
            day3_data = hit_patterns.get("hit_day_3", [])

            # ✅ VALIDATE data theo quy tắc
            if not day1_data or not isinstance(day1_data, list):
                logger.warning(f"⚠️ Invalid or empty day1_data for method {method_id}")
                return {}

            logger.debug(
                f"🔧 Extracting features for method {method_id}: day1={len(day1_data)}, day2={len(day2_data)}, day3={len(day3_data)}"
            )

            # 1. ĐẶC TRƯNG CHU KỲ (Cyclical Features)
            try:
                cyclical_features = self._extract_cyclical_features(
                    day1_data, day2_data, day3_data
                )
                features.update(cyclical_features)
            except Exception as e:
                logger.warning(f"⚠️ Error extracting cyclical features: {e}")

            # 2. ĐẶC TRƯNG THỐNG KÊ (Statistical Features)
            try:
                statistical_features = self._extract_statistical_features(
                    day1_data, day2_data, day3_data
                )
                features.update(statistical_features)
            except Exception as e:
                logger.warning(f"⚠️ Error extracting statistical features: {e}")

            # 3. ĐẶC TRƯNG CHUỖI (Sequential Features)
            try:
                sequential_features = self._extract_sequential_features(
                    day1_data, day2_data, day3_data
                )
                features.update(sequential_features)
            except Exception as e:
                logger.warning(f"⚠️ Error extracting sequential features: {e}")

            # 4. ĐẶC TRƯNG TƯƠNG QUAN (Cross-correlation Features)
            try:
                correlation_features = self._extract_correlation_features(
                    day1_data, day2_data, day3_data
                )
                features.update(correlation_features)
            except Exception as e:
                logger.warning(f"⚠️ Error extracting correlation features: {e}")

            # 5. ĐẶC TRƯNG TỦY CHỈNH (Domain-specific Features)
            try:
                domain_features = self._extract_domain_features(
                    day1_data, day2_data, day3_data
                )
                features.update(domain_features)
            except Exception as e:
                logger.warning(f"⚠️ Error extracting domain features: {e}")

            # ✅ VALIDATE ALL FEATURES ARE JSON SERIALIZABLE - tuân thủ quy tắc giao tiếp
            validated_features = {}
            for key, value in features.items():
                try:
                    # ✅ ENSURE JSON SERIALIZABLE với kiểu dữ liệu rõ ràng
                    if isinstance(value, (bool, np.bool_)):
                        validated_features[key] = bool(value)
                    elif isinstance(value, (int, np.integer)):
                        validated_features[key] = int(value)
                    elif isinstance(value, (float, np.floating)):
                        if np.isnan(value) or np.isinf(value):
                            validated_features[key] = 0.0
                        else:
                            validated_features[key] = float(value)
                    elif isinstance(value, np.ndarray):
                        validated_features[key] = float(
                            np.mean(value)
                        )  # Convert array to scalar
                    else:
                        # ✅ TRY TO CONVERT TO FLOAT
                        validated_features[key] = float(value)
                except (ValueError, TypeError, OverflowError):
                    logger.warning(
                        f"⚠️ Invalid feature value for {key}: {value} (type: {type(value)})"
                    )
                    validated_features[key] = 0.0

            logger.debug(
                f"✅ Extracted {len(validated_features)} features for method {method_id}"
            )
            return validated_features

        except Exception as e:
            logger.error(
                f"❌ Error extracting advanced features for method {method_id}: {e}"
            )
            return {}

    def _train_ensemble_model(self, X: np.ndarray, y: np.ndarray, target_day: int):
        """
        ✅ TRAIN ENSEMBLE MODEL - SỬA LỖI FEATURE ENGINEERING

        Args:
            X: np.ndarray - RAW feature matrix
            y: np.ndarray - Target vector
            target_day: int - Target day number

        Returns:
            Trained ensemble model
        """
        try:
            logger.info(f"🔬 Training ensemble model for day {target_day}")

            # ✅ SỬA: Apply feature engineering với target_day specific và is_training=True
            X_processed = self._advanced_feature_engineering(
                X, target_day=target_day, is_training=True
            )

            from sklearn.ensemble import (
                ExtraTreesClassifier,
                GradientBoostingClassifier,
                RandomForestClassifier,
                VotingClassifier,
            )
            from sklearn.linear_model import LogisticRegression
            from sklearn.svm import SVC

            # Base models
            models = [
                (
                    "rf",
                    RandomForestClassifier(
                        n_estimators=100, random_state=42, class_weight="balanced"
                    ),
                ),
                ("gb", GradientBoostingClassifier(n_estimators=100, random_state=42)),
                (
                    "et",
                    ExtraTreesClassifier(
                        n_estimators=100, random_state=42, class_weight="balanced"
                    ),
                ),
                (
                    "svm",
                    SVC(probability=True, random_state=42, class_weight="balanced"),
                ),
                (
                    "lr",
                    LogisticRegression(
                        random_state=42, class_weight="balanced", max_iter=1000
                    ),
                ),
            ]

            # Ensemble
            ensemble = VotingClassifier(estimators=models, voting="soft")
            ensemble.fit(X_processed, y)

            logger.info(
                f"✅ Ensemble model trained successfully for day {target_day} with {X_processed.shape[1]} features"
            )
            return ensemble

        except Exception as e:
            logger.error(f"❌ Error training ensemble model for day {target_day}: {e}")
            # Fallback to single model
            return self._train_single_model(X, y, target_day)

    def _convert_features_to_vector(
        self, features: Dict[str, float]
    ) -> Optional[np.ndarray]:
        """
        ✅ CHUYỂN ĐỔI FEATURES DICT THÀNH VECTOR - SỬA LỖI FEATURE COUNT

        Args:
            features: Dict[str, float] - Features dictionary

        Returns:
            Optional[np.ndarray] - Feature vector hoặc None nếu lỗi
        """
        try:
            # ✅ SỬA: Đảm bảo feature order nhất quán với _prepare_feature_vector
            expected_features = [
                # Statistical features (15 features)
                "day1_mean",
                "day1_std",
                "day1_variance",
                "day1_skewness",
                "day1_kurtosis",
                "day2_mean",
                "day2_std",
                "day2_variance",
                "day2_skewness",
                "day2_kurtosis",
                "day3_mean",
                "day3_std",
                "day3_variance",
                "day3_skewness",
                "day3_kurtosis",
                # Sequential features (18 features)
                "day1_current_streak",
                "day1_max_streak",
                "day1_avg_streak",
                "day2_current_streak",
                "day2_max_streak",
                "day2_avg_streak",
                "day3_current_streak",
                "day3_max_streak",
                "day3_avg_streak",
                "day1_avg_gap",
                "day1_gap_variance",
                "day1_last_gap",
                "day1_transition_rate",
                "day2_avg_gap",
                "day2_gap_variance",
                "day2_last_gap",
                "day2_transition_rate",
                "day3_avg_gap",
                "day3_gap_variance",
                "day3_last_gap",
                "day3_transition_rate",
                # Correlation features (7 features)
                "day12_correlation",
                "day13_correlation",
                "day23_correlation",
                "pattern_entropy",
                "day12_lag1_corr",
                "day12_lag2_corr",
                "day12_lag3_corr",
                # Cyclical features (27 features)
                "day1_weekly_variance",
                "day1_monthly_consistency",
                "day1_autocorr_lag1",
                "day1_autocorr_lag3",
                "day1_autocorr_lag7",
                "day1_autocorr_lag14",
                "day2_weekly_variance",
                "day2_monthly_consistency",
                "day2_autocorr_lag1",
                "day2_autocorr_lag3",
                "day2_autocorr_lag7",
                "day2_autocorr_lag14",
                "day3_weekly_variance",
                "day3_monthly_consistency",
                "day3_autocorr_lag1",
                "day3_autocorr_lag3",
                "day3_autocorr_lag7",
                "day3_autocorr_lag14",
                "day1_rolling_stability",
                "day1_outlier_ratio",
                "day1_range",
                "day1_coefficient_variation",
                "day2_rolling_stability",
                "day2_outlier_ratio",
                "day2_range",
                "day2_coefficient_variation",
                "day3_rolling_stability",
                "day3_outlier_ratio",
                "day3_range",
                "day3_coefficient_variation",
                "cross_day_mean_variance",
                "cross_day_mean_stability",
                "cross_day_independence_pvalue",
                # Domain features (18 features)
                "day1_momentum",
                "day1_consistency_score",
                "day1_hot_cold_ratio",
                "day1_fatigue_factor",
                "day1_recovery_potential",
                "day1_pressure_factor",
                "day2_momentum",
                "day2_consistency_score",
                "day2_hot_cold_ratio",
                "day2_fatigue_factor",
                "day2_recovery_potential",
                "day2_pressure_factor",
                "day3_momentum",
                "day3_consistency_score",
                "day3_hot_cold_ratio",
                "day3_fatigue_factor",
                "day3_recovery_potential",
                "day3_pressure_factor",
                "preferred_day",
                "day_preference_strength",
                "day12_synergy",
                "day13_synergy",
                "day23_synergy",
                "overall_synergy",
            ]

            # ✅ DEBUG: Log feature counts
            logger.debug(f"Expected features count: {len(expected_features)}")
            logger.debug(f"Provided features count: {len(features)}")

            # Create feature vector
            feature_vector = []
            missing_features = []

            for feature_name in expected_features:
                value = features.get(feature_name, 0.0)

                # Handle NaN/Inf values
                if isinstance(value, (int, float)):
                    if np.isnan(value) or np.isinf(value):
                        value = 0.0
                else:
                    value = 0.0

                if feature_name not in features:
                    missing_features.append(feature_name)

                feature_vector.append(float(value))

            # ✅ LOG missing features để debug
            if missing_features:
                logger.debug(
                    f"Missing {len(missing_features)} features: {missing_features[:10]}..."
                )

            logger.debug(f"Final feature vector length: {len(feature_vector)}")
            return np.array(feature_vector)

        except Exception as e:
            logger.error(f"❌ Error converting features to vector: {e}")
            return None

    def _prepare_feature_vector(self, features: Dict[str, float]) -> np.ndarray:
        """
        ✅ CHUẨN BỊ FEATURE VECTOR CHO ML MODEL - SYNC VỚI _convert_features_to_vector

        Args:
            features: Dict[str, float] - Features extracted from data

        Returns:
            np.ndarray - Feature vector ready for model prediction
        """
        try:
            # ✅ SỬA: Sử dụng cùng expected_features như _convert_features_to_vector
            expected_features = [
                # Statistical features (15 features)
                "day1_mean",
                "day1_std",
                "day1_variance",
                "day1_skewness",
                "day1_kurtosis",
                "day2_mean",
                "day2_std",
                "day2_variance",
                "day2_skewness",
                "day2_kurtosis",
                "day3_mean",
                "day3_std",
                "day3_variance",
                "day3_skewness",
                "day3_kurtosis",
                # Sequential features (18 features)
                "day1_current_streak",
                "day1_max_streak",
                "day1_avg_streak",
                "day2_current_streak",
                "day2_max_streak",
                "day2_avg_streak",
                "day3_current_streak",
                "day3_max_streak",
                "day3_avg_streak",
                "day1_avg_gap",
                "day1_gap_variance",
                "day1_last_gap",
                "day1_transition_rate",
                "day2_avg_gap",
                "day2_gap_variance",
                "day2_last_gap",
                "day2_transition_rate",
                "day3_avg_gap",
                "day3_gap_variance",
                "day3_last_gap",
                "day3_transition_rate",
                # Correlation features (7 features)
                "day12_correlation",
                "day13_correlation",
                "day23_correlation",
                "pattern_entropy",
                "day12_lag1_corr",
                "day12_lag2_corr",
                "day12_lag3_corr",
                # Cyclical features (27 features)
                "day1_weekly_variance",
                "day1_monthly_consistency",
                "day1_autocorr_lag1",
                "day1_autocorr_lag3",
                "day1_autocorr_lag7",
                "day1_autocorr_lag14",
                "day2_weekly_variance",
                "day2_monthly_consistency",
                "day2_autocorr_lag1",
                "day2_autocorr_lag3",
                "day2_autocorr_lag7",
                "day2_autocorr_lag14",
                "day3_weekly_variance",
                "day3_monthly_consistency",
                "day3_autocorr_lag1",
                "day3_autocorr_lag3",
                "day3_autocorr_lag7",
                "day3_autocorr_lag14",
                "day1_rolling_stability",
                "day1_outlier_ratio",
                "day1_range",
                "day1_coefficient_variation",
                "day2_rolling_stability",
                "day2_outlier_ratio",
                "day2_range",
                "day2_coefficient_variation",
                "day3_rolling_stability",
                "day3_outlier_ratio",
                "day3_range",
                "day3_coefficient_variation",
                "cross_day_mean_variance",
                "cross_day_mean_stability",
                "cross_day_independence_pvalue",
                # Domain features (18 features)
                "day1_momentum",
                "day1_consistency_score",
                "day1_hot_cold_ratio",
                "day1_fatigue_factor",
                "day1_recovery_potential",
                "day1_pressure_factor",
                "day2_momentum",
                "day2_consistency_score",
                "day2_hot_cold_ratio",
                "day2_fatigue_factor",
                "day2_recovery_potential",
                "day2_pressure_factor",
                "day3_momentum",
                "day3_consistency_score",
                "day3_hot_cold_ratio",
                "day3_fatigue_factor",
                "day3_recovery_potential",
                "day3_pressure_factor",
                "preferred_day",
                "day_preference_strength",
                "day12_synergy",
                "day13_synergy",
                "day23_synergy",
                "overall_synergy",
            ]

            # Create feature vector
            feature_vector = []
            for feature_name in expected_features:
                value = features.get(feature_name, 0.0)
                # ✅ Ensure numeric and handle NaN/Inf
                if isinstance(value, (int, float)):
                    if np.isnan(value) or np.isinf(value):
                        value = 0.0
                else:
                    value = 0.0
                feature_vector.append(float(value))

            logger.debug(
                f"Prepared feature vector length: {len(feature_vector)} (expected: {len(expected_features)})"
            )
            return np.array(feature_vector)

        except Exception as e:
            logger.error(f"❌ Error preparing feature vector: {e}")
            # Return zero vector as fallback với đúng số features
            return np.zeros(85)  # 15+18+7+27+18 = 85 features

    def _extract_statistical_features(
        self, day1: List[int], day2: List[int], day3: List[int]
    ) -> Dict[str, float]:
        """
        ✅ TRÍCH XUẤT ĐẶC TRƯNG THỐNG KÊ - BỔ SUNG ĐẦY ĐỦ FEATURES

        Returns:
            Dict[str, float] - Statistical features với keys rõ ràng
        """
        features = {}

        try:
            for day_idx, data in enumerate([day1, day2, day3], 1):
                if len(data) < 3:
                    # Set default values for insufficient data
                    features[f"day{day_idx}_mean"] = 0.0
                    features[f"day{day_idx}_std"] = 0.0
                    features[f"day{day_idx}_variance"] = 0.0
                    features[f"day{day_idx}_skewness"] = 0.0
                    features[f"day{day_idx}_kurtosis"] = 0.0
                    features[f"day{day_idx}_percentile_75"] = 0.0
                    features[f"day{day_idx}_percentile_25"] = 0.0
                    features[f"day{day_idx}_iqr"] = 0.0
                    features[f"day{day_idx}_range"] = 0.0
                    features[f"day{day_idx}_coefficient_variation"] = 0.0
                    features[f"day{day_idx}_rolling_stability"] = 0.0
                    features[f"day{day_idx}_outlier_ratio"] = 0.0
                    continue

                # Basic statistics
                features[f"day{day_idx}_mean"] = float(np.mean(data))
                features[f"day{day_idx}_std"] = float(np.std(data))
                features[f"day{day_idx}_variance"] = float(np.var(data))

                # Distribution shape
                if len(data) >= 5:
                    try:
                        from scipy import stats

                        features[f"day{day_idx}_skewness"] = float(stats.skew(data))
                        features[f"day{day_idx}_kurtosis"] = float(stats.kurtosis(data))
                    except ImportError:
                        features[f"day{day_idx}_skewness"] = 0.0
                        features[f"day{day_idx}_kurtosis"] = 0.0
                else:
                    features[f"day{day_idx}_skewness"] = 0.0
                    features[f"day{day_idx}_kurtosis"] = 0.0

                # Percentiles
                features[f"day{day_idx}_percentile_75"] = float(np.percentile(data, 75))
                features[f"day{day_idx}_percentile_25"] = float(np.percentile(data, 25))
                features[f"day{day_idx}_iqr"] = (
                    features[f"day{day_idx}_percentile_75"]
                    - features[f"day{day_idx}_percentile_25"]
                )

                # Range and spread
                features[f"day{day_idx}_range"] = float(np.max(data) - np.min(data))
                features[f"day{day_idx}_coefficient_variation"] = (
                    features[f"day{day_idx}_std"] / features[f"day{day_idx}_mean"]
                    if features[f"day{day_idx}_mean"] > 0
                    else 0.0
                )

                # Stability metrics
                if len(data) >= 10:
                    # Rolling average stability
                    window_size = min(5, len(data) // 2)
                    rolling_means = [
                        np.mean(data[i : i + window_size])
                        for i in range(len(data) - window_size + 1)
                    ]
                    features[f"day{day_idx}_rolling_stability"] = float(
                        1.0 - np.std(rolling_means)
                    )
                else:
                    features[f"day{day_idx}_rolling_stability"] = 0.0

                # Outlier detection (using IQR method)
                if features[f"day{day_idx}_iqr"] > 0:
                    q1 = features[f"day{day_idx}_percentile_25"]
                    q3 = features[f"day{day_idx}_percentile_75"]
                    lower_bound = q1 - 1.5 * features[f"day{day_idx}_iqr"]
                    upper_bound = q3 + 1.5 * features[f"day{day_idx}_iqr"]
                    outliers = [x for x in data if x < lower_bound or x > upper_bound]
                    features[f"day{day_idx}_outlier_ratio"] = float(
                        len(outliers) / len(data)
                    )
                else:
                    features[f"day{day_idx}_outlier_ratio"] = 0.0

            # Cross-day statistical comparisons
            if len(day1) >= 3 and len(day2) >= 3 and len(day3) >= 3:
                all_means = [features[f"day{i}_mean"] for i in range(1, 4)]
                features["cross_day_mean_variance"] = float(np.var(all_means))
                features["cross_day_mean_stability"] = float(
                    1.0 - (np.std(all_means) / (np.mean(all_means) + 1e-6))
                )

                # Statistical significance tests
                try:
                    from scipy.stats import chi2_contingency

                    min_len = min(len(day1), len(day2), len(day3))
                    contingency_table = np.array(
                        [
                            day1[:min_len],
                            day2[:min_len],
                            day3[:min_len],
                        ]
                    )
                    chi2, p_value, _, _ = chi2_contingency(
                        contingency_table + 1
                    )  # +1 to avoid zero
                    features["cross_day_independence_pvalue"] = float(p_value)
                except:
                    features["cross_day_independence_pvalue"] = 0.5  # Neutral
            else:
                features["cross_day_mean_variance"] = 0.0
                features["cross_day_mean_stability"] = 0.0
                features["cross_day_independence_pvalue"] = 0.5

            return features

        except Exception as e:
            logger.error(f"❌ Error extracting statistical features: {e}")
            return {}

    def _extract_sequential_features(
        self, day1: List[int], day2: List[int], day3: List[int]
    ) -> Dict[str, float]:
        """
        ✅ TRÍCH XUẤT ĐẶC TRƯNG CHUỖI - BỔ SUNG ĐẦY ĐỦ FEATURES

        Returns:
            Dict[str, float] - Sequential features với keys rõ ràng
        """
        features = {}

        try:
            for day_idx, data in enumerate([day1, day2, day3], 1):
                if len(data) < 5:
                    # Set default values for insufficient data
                    features[f"day{day_idx}_current_streak"] = 0.0
                    features[f"day{day_idx}_max_streak"] = 0.0
                    features[f"day{day_idx}_avg_streak"] = 0.0
                    features[f"day{day_idx}_avg_gap"] = 0.0
                    features[f"day{day_idx}_gap_variance"] = 0.0
                    features[f"day{day_idx}_last_gap"] = 0.0
                    features[f"day{day_idx}_transition_rate"] = 0.0
                    continue

                # Streak analysis (chuỗi liên tiếp)
                current_streak = self._calculate_current_streak(data)
                max_streak = self._calculate_max_streak(data)
                avg_streak = self._calculate_avg_streak_length(data)

                features[f"day{day_idx}_current_streak"] = float(current_streak)
                features[f"day{day_idx}_max_streak"] = float(max_streak)
                features[f"day{day_idx}_avg_streak"] = float(avg_streak)

                # Gap analysis (khoảng cách giữa các hit)
                hit_indices = [i for i, val in enumerate(data) if val == 1]
                if len(hit_indices) >= 2:
                    gaps = [
                        hit_indices[i + 1] - hit_indices[i]
                        for i in range(len(hit_indices) - 1)
                    ]
                    features[f"day{day_idx}_avg_gap"] = float(np.mean(gaps))
                    features[f"day{day_idx}_gap_variance"] = float(np.var(gaps))
                    features[f"day{day_idx}_last_gap"] = float(
                        len(data) - hit_indices[-1] if hit_indices else len(data)
                    )
                else:
                    features[f"day{day_idx}_avg_gap"] = 0.0
                    features[f"day{day_idx}_gap_variance"] = 0.0
                    features[f"day{day_idx}_last_gap"] = float(len(data))

                # Pattern transitions (chuyển đổi 0->1, 1->0)
                transitions = sum(
                    1 for i in range(1, len(data)) if data[i] != data[i - 1]
                )
                features[f"day{day_idx}_transition_rate"] = float(
                    transitions / len(data)
                )

            return features

        except Exception as e:
            logger.error(f"❌ Error extracting sequential features: {e}")
            return {}

    def _extract_domain_features(
        self, day1: List[int], day2: List[int], day3: List[int]
    ) -> Dict[str, float]:
        """
        ✅ TRÍCH XUẤT ĐẶC TRƯNG TỦY CHỈNH CHO DOMAIN XỔ SỐ - BỔ SUNG ĐẦY ĐỦ

        Returns:
            Dict[str, float] - Domain-specific features với keys rõ ràng
        """
        features = {}

        try:
            for day_idx, data in enumerate([day1, day2, day3], 1):
                if len(data) < 3:
                    # Set default values for insufficient data
                    features[f"day{day_idx}_hot_cold_ratio"] = 1.0
                    features[f"day{day_idx}_momentum"] = 0.0
                    features[f"day{day_idx}_fatigue_factor"] = 0.0
                    features[f"day{day_idx}_recovery_potential"] = 1.0
                    features[f"day{day_idx}_consistency_score"] = 0.0
                    features[f"day{day_idx}_pressure_factor"] = 0.5
                    continue

                # Hot vs Cold periods analysis
                recent_window = min(7, len(data) // 3)
                if recent_window >= 3:
                    recent_hits = sum(data[-recent_window:])
                    older_hits = (
                        sum(data[:-recent_window]) if len(data) > recent_window else 0
                    )
                    older_period_length = len(data) - recent_window
                    recent_rate = recent_hits / recent_window
                    older_rate = (
                        older_hits / older_period_length
                        if older_period_length > 0
                        else 0
                    )

                    features[f"day{day_idx}_hot_cold_ratio"] = float(
                        recent_rate / (older_rate + 1e-6)
                    )
                else:
                    features[f"day{day_idx}_hot_cold_ratio"] = 1.0

                # Momentum analysis (trend strength)
                if len(data) >= 6:
                    # Split into 3 equal parts
                    third = len(data) // 3
                    early_rate = sum(data[:third]) / third
                    middle_rate = sum(data[third : 2 * third]) / third
                    late_rate = sum(data[2 * third :]) / (len(data) - 2 * third)

                    # Calculate momentum (acceleration)
                    momentum = (late_rate - early_rate) + 0.5 * (
                        middle_rate - early_rate
                    )
                    features[f"day{day_idx}_momentum"] = float(momentum)
                else:
                    features[f"day{day_idx}_momentum"] = 0.0

                # Fatigue factor (performance degradation after hits)
                hit_indices = [i for i, val in enumerate(data) if val == 1]
                if len(hit_indices) >= 2:
                    # Check performance in windows after hits
                    post_hit_performance = []
                    for hit_idx in hit_indices[:-1]:  # Exclude last hit
                        # Check next 3 positions after hit
                        next_window = data[hit_idx + 1 : hit_idx + 4]
                        if next_window:
                            post_hit_performance.append(
                                sum(next_window) / len(next_window)
                            )

                    if post_hit_performance:
                        overall_rate = sum(data) / len(data)
                        avg_post_hit_rate = np.mean(post_hit_performance)
                        features[f"day{day_idx}_fatigue_factor"] = float(
                            1.0 - (avg_post_hit_rate / (overall_rate + 1e-6))
                        )
                    else:
                        features[f"day{day_idx}_fatigue_factor"] = 0.0
                else:
                    features[f"day{day_idx}_fatigue_factor"] = 0.0

                # Recovery potential (ability to bounce back after misses)
                miss_indices = [i for i, val in enumerate(data) if val == 0]
                if len(miss_indices) >= 2:
                    # Check performance in windows after misses
                    post_miss_performance = []
                    for miss_idx in miss_indices[:-1]:  # Exclude last miss
                        # Check next 3 positions after miss
                        next_window = data[miss_idx + 1 : miss_idx + 4]
                        if next_window:
                            post_miss_performance.append(
                                sum(next_window) / len(next_window)
                            )

                    if post_miss_performance:
                        overall_rate = sum(data) / len(data)
                        avg_post_miss_rate = np.mean(post_miss_performance)
                        features[f"day{day_idx}_recovery_potential"] = float(
                            avg_post_miss_rate / (overall_rate + 1e-6)
                        )
                    else:
                        features[f"day{day_idx}_recovery_potential"] = 1.0
                else:
                    features[f"day{day_idx}_recovery_potential"] = 1.0

                # Consistency score (reliability measure)
                if len(data) >= 5:
                    # Calculate consistency based on deviation from expected pattern
                    hit_rate = sum(data) / len(data)
                    expected_hits = hit_rate * len(data)
                    actual_hits = sum(data)

                    # Temporal consistency (are hits evenly distributed?)
                    if actual_hits > 0:
                        expected_gap = len(data) / actual_hits
                        hit_indices = [i for i, val in enumerate(data) if val == 1]
                        if len(hit_indices) >= 2:
                            actual_gaps = [
                                hit_indices[i + 1] - hit_indices[i]
                                for i in range(len(hit_indices) - 1)
                            ]
                            gap_variance = np.var(actual_gaps)
                            features[f"day{day_idx}_consistency_score"] = float(
                                1.0 / (1.0 + gap_variance)
                            )
                        else:
                            features[f"day{day_idx}_consistency_score"] = 0.5
                    else:
                        features[f"day{day_idx}_consistency_score"] = 0.0
                else:
                    features[f"day{day_idx}_consistency_score"] = 0.0

                # Pressure factor (performance under "due" conditions)
                if len(data) >= 10:
                    # Find long miss streaks (pressure situations)
                    current_miss_streak = 0
                    max_miss_streak = 0
                    pressure_recovery = []

                    for i, val in enumerate(data):
                        if val == 0:
                            current_miss_streak += 1
                            max_miss_streak = max(max_miss_streak, current_miss_streak)
                        else:
                            # Hit after long miss streak?
                            if current_miss_streak >= 5:  # Pressure situation
                                pressure_recovery.append(1)  # Recovered
                            current_miss_streak = 0

                    if pressure_recovery:
                        features[f"day{day_idx}_pressure_factor"] = float(
                            np.mean(pressure_recovery)
                        )
                    else:
                        features[f"day{day_idx}_pressure_factor"] = 0.5
                else:
                    features[f"day{day_idx}_pressure_factor"] = 0.5

            # Cross-day domain features
            if len(day1) >= 3 and len(day2) >= 3 and len(day3) >= 3:
                # Day preference analysis
                day_rates = [
                    sum(day1) / len(day1),
                    sum(day2) / len(day2),
                    sum(day3) / len(day3),
                ]

                best_day = np.argmax(day_rates) + 1
                features["preferred_day"] = float(best_day)
                features["day_preference_strength"] = float(
                    np.max(day_rates) - np.mean(day_rates)
                )

                # Cross-day synergy (do hits in one day predict hits in another?)
                min_len = min(len(day1), len(day2), len(day3))
                d1_short = day1[:min_len]
                d2_short = day2[:min_len]
                d3_short = day3[:min_len]

                # Day 1 -> Day 2 synergy
                day12_synergy = 0.0
                day13_synergy = 0.0
                day23_synergy = 0.0

                if min_len >= 5:
                    # Calculate conditional probabilities
                    d1_hit_indices = [i for i, val in enumerate(d1_short) if val == 1]
                    d2_hit_indices = [i for i, val in enumerate(d2_short) if val == 1]
                    d3_hit_indices = [i for i, val in enumerate(d3_short) if val == 1]

                    if d1_hit_indices and d2_hit_indices:
                        # Count concurrent hits
                        concurrent_12 = len(set(d1_hit_indices) & set(d2_hit_indices))
                        day12_synergy = concurrent_12 / min(
                            len(d1_hit_indices), len(d2_hit_indices)
                        )

                    if d1_hit_indices and d3_hit_indices:
                        concurrent_13 = len(set(d1_hit_indices) & set(d3_hit_indices))
                        day13_synergy = concurrent_13 / min(
                            len(d1_hit_indices), len(d3_hit_indices)
                        )

                    if d2_hit_indices and d3_hit_indices:
                        concurrent_23 = len(set(d2_hit_indices) & set(d3_hit_indices))
                        day23_synergy = concurrent_23 / min(
                            len(d2_hit_indices), len(d3_hit_indices)
                        )

                features["day12_synergy"] = float(day12_synergy)
                features["day13_synergy"] = float(day13_synergy)
                features["day23_synergy"] = float(day23_synergy)
                features["overall_synergy"] = float(
                    np.mean([day12_synergy, day13_synergy, day23_synergy])
                )
            else:
                # Default values for insufficient data
                features["preferred_day"] = 1.0
                features["day_preference_strength"] = 0.0
                features["day12_synergy"] = 0.0
                features["day13_synergy"] = 0.0
                features["day23_synergy"] = 0.0
                features["overall_synergy"] = 0.0

            return features

        except Exception as e:
            logger.error(f"❌ Error extracting domain features: {e}")
            return {}

    def predict_next_days(
        self,
        hit_patterns: Dict[str, Dict[str, List[int]]],
        method_ids: List[str],
        prediction_horizon: int = 1,
        use_enhanced_features: bool = True,  # ✅ THÊM THAM SỐ MỚI
    ) -> Dict[str, Dict[str, Any]]:
        """
        ✅ PREDICT next days với Enhanced Features
        """
        try:
            logger.info(
                f"🔮 Predicting next days for {len(method_ids)} methods with Enhanced Features"
            )

            if not hasattr(self, "advanced_models") or not self.advanced_models:
                logger.warning("⚠️ No trained models available")
                return {}

            # ✅ IMPORT enhanced feature service
            from .EnhancedFeatureService import enhanced_feature_service

            predictions = {}

            for method_id in method_ids:
                try:
                    # ✅ EXTRACT enhanced features
                    if use_enhanced_features:
                        features = (
                            enhanced_feature_service.extract_comprehensive_features(
                                method_id=int(method_id),
                                target_date=date.today(),
                                historical_patterns=hit_patterns,
                                prediction_horizon=prediction_horizon,
                            )
                        )
                    else:
                        features = self.extract_advanced_features(
                            hit_patterns, method_id
                        )

                    # ✅ PREDICT cho từng ngày
                    day_predictions = {}

                    for day_num in [1, 2, 3]:
                        day_key = f"day_{day_num}"
                        model_key = f"day_{day_num}"

                        if model_key in self.advanced_models and day_key in features:
                            model_info = self.advanced_models[model_key]

                            if model_info and "model" in model_info:
                                # ✅ PREPARE features
                                day_features = features[day_key]
                                feature_vector = [
                                    day_features.get(fname, 0.0)
                                    for fname in sorted(day_features.keys())
                                ]

                                # ✅ SCALE features
                                feature_vector_scaled = model_info["scaler"].transform(
                                    [feature_vector]
                                )

                                # ✅ PREDICT
                                probability = model_info["model"].predict_proba(
                                    feature_vector_scaled
                                )[0]
                                hit_probability = (
                                    probability[1]
                                    if len(probability) > 1
                                    else probability[0]
                                )

                                # ✅ CALCULATE confidence
                                confidence = self._calculate_enhanced_confidence(
                                    hit_probability, day_features, model_info
                                )

                                day_predictions[day_key] = {
                                    "probability": float(hit_probability),
                                    "confidence": float(confidence),
                                    "quality_score": float(confidence * 100),
                                    "prediction_source": "enhanced_ml",
                                }
                            else:
                                day_predictions[day_key] = {
                                    "probability": 0.1,
                                    "confidence": 0.1,
                                    "quality_score": 10.0,
                                    "prediction_source": "fallback",
                                }
                        else:
                            day_predictions[day_key] = {
                                "probability": 0.1,
                                "confidence": 0.1,
                                "quality_score": 10.0,
                                "prediction_source": "missing_model",
                            }

                    # ✅ FIND best day
                    best_day = max(
                        day_predictions.keys(),
                        key=lambda k: day_predictions[k]["probability"],
                    )
                    best_day_num = int(best_day.split("_")[1])

                    # ✅ CALCULATE overall confidence
                    overall_confidence = np.mean(
                        [pred["confidence"] for pred in day_predictions.values()]
                    )

                    predictions[method_id] = {
                        "method_name": f"Method {method_id}",
                        "day_1": day_predictions.get("day_1", {}),
                        "day_2": day_predictions.get("day_2", {}),
                        "day_3": day_predictions.get("day_3", {}),
                        "recommended_day": best_day_num,
                        "overall_confidence": float(overall_confidence),
                        "prediction_quality": self._assess_prediction_quality(
                            overall_confidence
                        ),
                    }

                except Exception as method_error:
                    logger.error(
                        f"❌ Error predicting for method {method_id}: {method_error}"
                    )
                    continue

            logger.info(f"✅ Predictions completed for {len(predictions)} methods")
            return predictions

        except Exception as e:
            logger.error(f"❌ Error in predict_next_days: {e}")
            return {}

    def _calculate_enhanced_confidence(
        self,
        hit_probability: float,
        day_features: Dict[str, float],
        model_info: Dict[str, Any],
    ) -> float:
        """
        ✅ CALCULATE enhanced confidence score
        """
        try:
            # ✅ BASE confidence từ model
            base_confidence = model_info.get("test_score", 0.5)

            # ✅ ADJUST based on features
            stability_factor = day_features.get("pattern_stability", 0.5)
            trend_strength = day_features.get("trend_strength", 0.0)
            data_quality = day_features.get("prediction_confidence", 0.5)

            # ✅ WEIGHTED confidence
            enhanced_confidence = (
                base_confidence * 0.4
                + stability_factor * 0.3
                + trend_strength * 0.2
                + data_quality * 0.1
            )

            # ✅ ADJUST based on probability certainty
            probability_certainty = abs(hit_probability - 0.5) * 2  # 0 to 1
            enhanced_confidence *= 0.7 + probability_certainty * 0.3

            return min(1.0, max(0.0, enhanced_confidence))

        except Exception as e:
            logger.warning(f"⚠️ Error calculating enhanced confidence: {e}")
            return 0.5

    def _assess_prediction_quality(self, confidence: float) -> str:
        """
        ✅ ASSESS prediction quality
        """
        if confidence >= 0.8:
            return "excellent"
        elif confidence >= 0.6:
            return "good"
        elif confidence >= 0.4:
            return "average"
        else:
            return "poor"

    def _extract_correlation_features(
        self, day1: List[int], day2: List[int], day3: List[int]
    ) -> Dict[str, float]:
        """Trích xuất đặc trưng tương quan giữa các ngày"""
        features = {}

        min_len = min(len(day1), len(day2), len(day3))
        if min_len < 10:
            return features

        # Cắt về cùng độ dài
        d1, d2, d3 = day1[:min_len], day2[:min_len], day3[:min_len]

        # Tương quan giữa các cặp ngày
        features["day12_correlation"] = (
            np.corrcoef(d1, d2)[0, 1]
            if not np.isnan(np.corrcoef(d1, d2)[0, 1])
            else 0.0
        )
        features["day13_correlation"] = (
            np.corrcoef(d1, d3)[0, 1]
            if not np.isnan(np.corrcoef(d1, d3)[0, 1])
            else 0.0
        )
        features["day23_correlation"] = (
            np.corrcoef(d2, d3)[0, 1]
            if not np.isnan(np.corrcoef(d2, d3)[0, 1])
            else 0.0
        )

        # Lag correlation (tương quan với độ trễ)
        for lag in [1, 2, 3]:
            if min_len > lag:
                features[f"day12_lag{lag}_corr"] = (
                    np.corrcoef(d1[:-lag], d2[lag:])[0, 1]
                    if not np.isnan(np.corrcoef(d1[:-lag], d2[lag:])[0, 1])
                    else 0.0
                )

        # Phân tích theo chuỗi (sequential patterns)
        combined = list(zip(d1, d2, d3))
        pattern_counts = {}
        for pattern in combined:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        # Entropy của patterns
        total = len(combined)
        entropy = -sum(
            (count / total) * np.log2(count / total)
            for count in pattern_counts.values()
        )
        features["pattern_entropy"] = entropy

        return features

    # ✅ THÊM CÁC HÀM HỖ TRỢ CHO SEQUENTIAL FEATURES

    def _calculate_current_streak(self, data: List[int]) -> int:
        """Tính streak hiện tại (dương: hit streak, âm: miss streak)"""
        if not data:
            return 0

        current_value = data[-1]
        streak = 1

        for i in range(len(data) - 2, -1, -1):
            if data[i] == current_value:
                streak += 1
            else:
                break

        return streak if current_value == 1 else -streak

    def _calculate_max_streak(self, data: List[int]) -> int:
        """Tính max streak (hit hoặc miss)"""
        if not data:
            return 0

        max_streak = 1
        current_streak = 1

        for i in range(1, len(data)):
            if data[i] == data[i - 1]:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1

        return max_streak

    def _calculate_avg_streak_length(self, data: List[int]) -> float:
        """Tính độ dài streak trung bình"""
        if not data:
            return 0.0

        streaks = []
        current_streak = 1

        for i in range(1, len(data)):
            if data[i] == data[i - 1]:
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1

        streaks.append(current_streak)  # Add last streak

        return np.mean(streaks) if streaks else 0.0


# ✅ SINGLETON INSTANCE
data_service = DataService()

data_service = DataService()
DataServiceEnhancer.add_intelligence_methods(data_service)
original_predict = data_service.predict_next_days
data_service.predict_next_days = DataServiceEnhancer.enhance_predict_next_days(
    data_service, original_predict
)
