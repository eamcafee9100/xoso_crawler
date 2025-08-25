import json
import logging
from datetime import date, timedelta

import hashlib
from venv import logger
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count, JSONField
from django.utils import timezone

from results.models import NumberFrequencyStats, KetQuaXoSo
import logging
logger = logging.getLogger(__name__)

class PredictionMethod(models.Model):
    """
    Model riêng cho predictions_tracker - không sử dụng PredictionMethodBtl
    """

    # Thông tin cơ bản
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã phương pháp")
    name = models.CharField(max_length=200, verbose_name="Tên phương pháp")
    description = models.TextField(blank=True, verbose_name="Mô tả")

    # Phân loại
    CATEGORY_CHOICES = [
        ("cycle", "Phân tích chu kỳ"),
        ("frequency", "Phân tích tần suất"),
        ("gap", "Phân tích khoảng cách"),
        ("markov", "Chuỗi Markov"),
        ("pattern", "Khai thác mẫu"),
        ("ensemble", "Kết hợp nhiều chiến lược"),
        ("statistical", "Phân tích thống kê"),
        ("neural", "Mạng nơ-ron"),
        ("other", "Khác"),
    ]
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="other",
        verbose_name="Loại phương pháp",
        db_index=True,
    )

    # Cấu hình
    parameters = models.JSONField(
        default=dict,
        verbose_name="Tham số cấu hình",
        help_text="Lưu các tham số cấu hình của phương pháp",
    )

    # Trạng thái
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Độ ưu tiên",
        help_text="1 = cao nhất, 10 = thấp nhất",
    )

    # Thống kê hiệu suất
    total_predictions = models.IntegerField(default=0, verbose_name="Tổng dự đoán")
    total_hits = models.IntegerField(default=0, verbose_name="Tổng trúng")
    success_rate = models.FloatField(default=0.0, verbose_name="Tỷ lệ thành công (%)")
    avg_hit_count = models.FloatField(default=0.0, verbose_name="Trung bình số trúng")

    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Lần sử dụng cuối"
    )

    class Meta:
        verbose_name = "Phương pháp dự đoán"
        verbose_name_plural = "Phương pháp dự đoán"
        ordering = ["priority", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["success_rate"]),
            models.Index(fields=["-last_used_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.success_rate:.1f}%)"

    def update_statistics(self):
        """Cập nhật thống kê từ tracking results"""
        from django.db.models import Avg, Count, Sum

        # Import MethodPredictionResult để tránh lỗi forward reference
        from .models import MethodPredictionResult, TrackingEvaluation

        # Tính từ MethodPredictionResult
        stats = MethodPredictionResult.objects.filter(method=self).aggregate(
            total_predictions=Count("id"),
        )

        # Tính từ evaluations
        evaluations = TrackingEvaluation.objects.filter(method_result__method=self)

        if evaluations.exists():
            eval_stats = evaluations.aggregate(
                total_hits=Sum("hit_count"),
                avg_hit_count=Avg("hit_count"),
                avg_hit_rate=Avg("hit_rate"),
            )

            self.total_predictions = stats["total_predictions"] or 0
            self.total_hits = eval_stats["total_hits"] or 0
            self.avg_hit_count = eval_stats["avg_hit_count"] or 0
            self.success_rate = eval_stats["avg_hit_rate"] or 0
        else:
            self.total_predictions = 0
            self.total_hits = 0
            self.avg_hit_count = 0
            self.success_rate = 0

        self.last_used_at = timezone.now()
        self.save(
            update_fields=[
                "total_predictions",
                "total_hits",
                "success_rate",
                "avg_hit_count",
                "last_used_at",
            ]
        )


class PredictionStrategy(models.Model):
    """
    Chiến lược dự đoán - mở rộng PredictionMethod
    """

    # Liên kết với method riêng
    method = models.OneToOneField(
        PredictionMethod,
        on_delete=models.CASCADE,
        related_name="strategy_extension",
        verbose_name="Phương pháp",
    )

    # Thông tin ensemble
    STRATEGY_TYPES = [
        ("cycle", "Phân tích chu kỳ"),
        ("frequency", "Phân tích tần suất"),
        ("gap", "Phân tích khoảng cách"),
        ("markov", "Chuỗi Markov"),
        ("pattern", "Khai thác mẫu"),
        ("ensemble", "Kết hợp nhiều chiến lược"),
    ]
    strategy_type = models.CharField(max_length=20, choices=STRATEGY_TYPES)

    # Cấu hình ensemble
    ensemble_weight = models.FloatField(
        default=1.0, verbose_name="Trọng số trong ensemble"
    )
    ensemble_config = models.JSONField(default=dict, verbose_name="Cấu hình ensemble")

    # Liên kết với ensemble analysis
    uses_cycle_analysis = models.BooleanField(
        default=False, verbose_name="Sử dụng phân tích chu kỳ"
    )
    uses_frequency_analysis = models.BooleanField(
        default=False, verbose_name="Sử dụng phân tích tần suất"
    )
    uses_gap_analysis = models.BooleanField(
        default=False, verbose_name="Sử dụng phân tích khoảng cách"
    )
    uses_markov_analysis = models.BooleanField(
        default=False, verbose_name="Sử dụng Markov chain"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chiến lược dự đoán"
        verbose_name_plural = "Chiến lược dự đoán"
        ordering = ["-ensemble_weight"]

    def __str__(self):
        return f"{self.method.name} - {dict(self.STRATEGY_TYPES).get(self.strategy_type, self.strategy_type)}"

    @property
    def name(self):
        return self.method.name

    @property
    def is_active(self):
        return self.method.is_active


class PredictionCycle(models.Model):
    """
    Chu kỳ theo dõi hiệu suất
    """

    cycle_name = models.CharField(max_length=100, verbose_name="Tên chu kỳ")
    start_date = models.DateField(verbose_name="Ngày bắt đầu", db_index=True)
    end_date = models.DateField(verbose_name="Ngày kết thúc", db_index=True)
    tracking_days = models.IntegerField(default=3, verbose_name="Số ngày theo dõi")

    # Liên kết với methods riêng
    included_methods = models.ManyToManyField(
        PredictionMethod,
        through="CycleMethodParticipation",
        related_name="tracking_cycles",
        verbose_name="Phương pháp tham gia",
    )

    # Trạng thái
    STATUS_CHOICES = [
        ("planning", "Đang lên kế hoạch"),
        ("active", "Đang hoạt động"),
        ("completed", "Đã hoàn thành"),
        ("paused", "Tạm dừng"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planning")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chu kỳ theo dõi"
        verbose_name_plural = "Chu kỳ theo dõi"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.cycle_name} ({self.start_date} - {self.end_date})"


class CycleMethodParticipation(models.Model):
    """
    Bảng trung gian: Method nào tham gia cycle nào với cấu hình gì
    """

    cycle = models.ForeignKey(PredictionCycle, on_delete=models.CASCADE)
    method = models.ForeignKey(PredictionMethod, on_delete=models.CASCADE)

    # Cấu hình riêng cho method trong cycle này
    is_ensemble_enabled = models.BooleanField(
        default=False, verbose_name="Bật ensemble"
    )
    custom_weight = models.FloatField(default=1.0, verbose_name="Trọng số riêng")
    custom_config = models.JSONField(default=dict, verbose_name="Cấu hình riêng")

    # Trạng thái
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    joined_date = models.DateField(auto_now_add=True, verbose_name="Ngày tham gia")

    class Meta:
        unique_together = ["cycle", "method"]
        verbose_name = "Tham gia chu kỳ"
        verbose_name_plural = "Tham gia chu kỳ"

    def __str__(self):
        return f"{self.method.name} trong {self.cycle.cycle_name}"


class DailyTrackingSession(models.Model):
    """
    Phiên theo dõi hàng ngày
    """

    cycle = models.ForeignKey(
        PredictionCycle, on_delete=models.CASCADE, related_name="daily_sessions"
    )
    prediction_date = models.DateField(verbose_name="Ngày dự đoán", db_index=True)
    session_id = models.CharField(max_length=50, verbose_name="ID phiên", unique=True)

    # Liên kết với kết quả thực tế từ KetQuaXoSo
    actual_result = models.ForeignKey(
        KetQuaXoSo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Kết quả thực tế",
    )

    # Ensemble data từ combine_strategies()
    ensemble_recommendations = models.JSONField(
        default=list,
        verbose_name="Khuyến nghị ensemble",
        help_text="Kết quả từ combine_strategies(analysis_date, history_data)",
    )

    # Chi tiết từng strategy
    cycle_analysis_data = models.JSONField(
        default=dict,
        verbose_name="Dữ liệu phân tích chu kỳ",
        help_text="Từ AnalysisStrategiesService.analyze_cycles()",
    )
    gap_analysis_data = models.JSONField(
        default=dict,
        verbose_name="Dữ liệu phân tích khoảng cách",
        help_text="Từ AnalysisStrategiesService.analyze_gaps()",
    )
    pattern_mining_data = models.JSONField(
        default=dict,
        verbose_name="Dữ liệu khai thác mẫu",
        help_text="Từ AnalysisStrategiesService.mine_patterns()",
    )

    # Thống kê tracking
    tracking_start_date = models.DateField(verbose_name="Bắt đầu tracking")
    tracking_end_date = models.DateField(verbose_name="Kết thúc tracking")
    current_tracking_day = models.IntegerField(
        default=0, verbose_name="Ngày tracking hiện tại"
    )

    # Trạng thái
    STATUS_CHOICES = [
        ("pending", "Chờ kết quả"),
        ("tracking", "Đang theo dõi"),
        ("completed", "Hoàn thành"),
        ("expired", "Hết hạn"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phiên theo dõi hàng ngày"
        verbose_name_plural = "Phiên theo dõi hàng ngày"
        ordering = ["-prediction_date"]
        unique_together = ["cycle", "prediction_date"]

    def __str__(self):
        return f"Phiên {self.prediction_date} - {self.cycle.cycle_name}"

    def get_actual_numbers(self):
        """Tái sử dụng method từ KetQuaXoSo"""
        if self.actual_result:
            return list(self.actual_result.get_all_2digit_numbers())
        return []

    def get_recommended_numbers(self, top_n=15):
        """Lấy top N từ ensemble"""
        if not self.ensemble_recommendations:
            return []
        return [item["number"] for item in self.ensemble_recommendations[:top_n]]


class MethodPredictionResult(models.Model):
    """
    Kết quả dự đoán chi tiết từng method
    """

    session = models.ForeignKey(
        DailyTrackingSession, on_delete=models.CASCADE, related_name="method_results"
    )
    method = models.ForeignKey(
        PredictionMethod, on_delete=models.CASCADE, related_name="tracking_results"
    )

    # Dự đoán từ method cơ bản
    base_prediction_numbers = models.JSONField(
        verbose_name="Số dự đoán cơ bản", help_text="Từ method gốc"
    )

    # Dự đoán từ ensemble (nếu có)
    ensemble_enhanced_numbers = models.JSONField(
        default=list, verbose_name="Số dự đoán được ensemble tăng cường"
    )

    # Confidence scores từ các analysis
    cycle_confidence = models.FloatField(default=0.0, verbose_name="Độ tin cậy chu kỳ")
    frequency_confidence = models.FloatField(
        default=0.0, verbose_name="Độ tin cậy tần suất"
    )
    gap_confidence = models.FloatField(
        default=0.0, verbose_name="Độ tin cậy khoảng cách"
    )
    overall_confidence = models.FloatField(
        default=0.0, verbose_name="Độ tin cậy tổng thể"
    )

    # Chi tiết analysis cho method này
    method_analysis_details = models.JSONField(
        default=dict, verbose_name="Chi tiết phân tích method"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kết quả dự đoán method"
        verbose_name_plural = "Kết quả dự đoán method"
        unique_together = ["session", "method"]

    def __str__(self):
        return f"{self.method.name} - {self.session.prediction_date}"


class TrackingEvaluation(models.Model):
    """
    Đánh giá theo dõi
    """

    session = models.ForeignKey(
        DailyTrackingSession, on_delete=models.CASCADE, related_name="evaluations"
    )
    method_result = models.ForeignKey(
        MethodPredictionResult,
        on_delete=models.CASCADE,
        related_name="evaluations",
        null=True,
        blank=True,
    )

    # Ngày đánh giá
    evaluation_date = models.DateField(verbose_name="Ngày đánh giá", db_index=True)
    days_after_prediction = models.IntegerField(verbose_name="Số ngày sau dự đoán")

    # Kết quả (sử dụng KetQuaXoSo.get_all_2digit_numbers())
    actual_numbers = models.JSONField(verbose_name="Số thực tế")
    predicted_numbers = models.JSONField(verbose_name="Số dự đoán")
    hit_numbers = models.JSONField(verbose_name="Số trúng")

    # Thống kê
    hit_count = models.IntegerField(default=0, verbose_name="Số lượng trúng")
    total_predicted = models.IntegerField(default=0, verbose_name="Tổng dự đoán")
    hit_rate = models.FloatField(default=0.0, verbose_name="Tỷ lệ trúng (%)")
    wilson_score = models.FloatField(default=0.0, verbose_name="Wilson score")

    # Phân tích chi tiết bằng utils hiện có
    gap_analysis_result = models.JSONField(
        default=dict,
        verbose_name="Kết quả phân tích gap",
        help_text="Từ gap_analysis()",
    )
    frequency_analysis_result = models.JSONField(
        default=dict,
        verbose_name="Kết quả phân tích tần suất",
        help_text="Từ frequency_analysis()",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Đánh giá theo dõi"
        verbose_name_plural = "Đánh giá theo dõi"
        unique_together = ["session", "evaluation_date", "method_result"]

    def __str__(self):
        method_name = (
            self.method_result.method.name if self.method_result else "Ensemble"
        )
        return f"{method_name} - {self.evaluation_date}"


class CyclicalNumberPredictor(models.Model):
    """Dự đoán số dựa trên chu kỳ tần suất"""

    analysis_date = models.DateField(verbose_name="Ngày phân tích")
    target_date = models.DateField(verbose_name="Ngày dự đoán")

    # Prediction results
    predicted_numbers = models.JSONField(
        default=list, help_text="List of predicted numbers with scores"
    )
    prediction_confidence = models.FloatField(
        default=0.0, verbose_name="Độ tin cậy dự đoán"
    )
    cycle_strength = models.FloatField(default=0.0, verbose_name="Độ mạnh chu kỳ")

    # Analysis metadata
    cycle_patterns = models.JSONField(default=dict, help_text="Cycle patterns detected")
    frequency_analysis = models.JSONField(
        default=dict, help_text="Frequency analysis results"
    )
    phase_compatibility = models.JSONField(
        default=dict, help_text="Phase compatibility scores"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["analysis_date", "target_date"]
        verbose_name = "Cyclical Number Predictor"
        verbose_name_plural = "Cyclical Number Predictors"
        indexes = [
            models.Index(fields=["analysis_date"]),
            models.Index(fields=["target_date"]),
            models.Index(fields=["prediction_confidence"]),
        ]

    def __str__(self):
        return f"Predict {self.target_date} from {self.analysis_date} (Conf: {self.prediction_confidence:.2f})"

    @classmethod
    def predict_numbers_by_frequency_cycles(
        cls, analysis_date: date
    ) -> "CyclicalNumberPredictor":
        """
        Dự đoán số dựa trên chu kỳ tần suất

        Returns:
            CyclicalNumberPredictor: Object chứa predictions và metadata
        """
        from datetime import timedelta

        target_date = analysis_date + timedelta(days=1)

        # Get or create predictor
        predictor, created = cls.objects.get_or_create(
            analysis_date=analysis_date,
            target_date=target_date,
            defaults={
                "predicted_numbers": [],
                "prediction_confidence": 0.0,
                "cycle_strength": 0.0,
                "cycle_patterns": {},
                "frequency_analysis": {},
                "phase_compatibility": {},
            },
        )

        if created or predictor._needs_update():
            predictor._perform_cyclical_prediction()
            predictor.save()

        return predictor

    def _needs_update(self) -> bool:
        """Check if prediction needs update"""
        from datetime import timedelta

        return (timezone.now() - self.created_at) > timedelta(hours=1)

    def _perform_cyclical_prediction(self) -> None:
        """
        Core prediction logic dựa trên frequency cycles

        Returns: None (updates instance attributes)
        """
        from collections import Counter, defaultdict
        from datetime import timedelta

        try:
            # 1. Analyze frequency patterns
            frequency_analysis = self._analyze_frequency_patterns()

            # 2. Detect cycle patterns
            cycle_patterns = self._detect_cycle_patterns()

            # 3. Calculate phase compatibility
            phase_compatibility = self._calculate_phase_compatibility()

            # 4. Generate predictions
            predicted_numbers = self._generate_number_predictions(
                frequency_analysis, cycle_patterns, phase_compatibility
            )

            # 5. Calculate confidence metrics
            prediction_confidence = self._calculate_prediction_confidence(
                frequency_analysis, cycle_patterns
            )
            cycle_strength = self._calculate_cycle_strength()

            # Update instance
            self.predicted_numbers = predicted_numbers
            self.prediction_confidence = prediction_confidence
            self.cycle_strength = cycle_strength
            self.frequency_analysis = frequency_analysis
            self.cycle_patterns = cycle_patterns
            self.phase_compatibility = phase_compatibility

        except Exception as e:
            logger.error(f"Cyclical prediction error: {str(e)}")
            self._set_fallback_prediction()

    def _analyze_frequency_patterns(self) -> dict:
        """
        Phân tích patterns tần suất xuất hiện

        Returns:
            dict: {
                "similar_contexts": list,
                "frequency_scores": dict,
                "pattern_strength": float
            }
        """
        from datetime import timedelta

        # Get similar contexts (same day_of_month, month, weekday)
        similar_contexts = (
            NumberFrequencyStats.objects.filter(
                day_of_month=self.target_date.day,
                month=self.target_date.month,
                day_of_week=self.target_date.weekday(),
                date__lt=self.analysis_date,  # Only historical data
            )
            .select_related()
            .order_by("-date")[:100]
        )  # Last 100 similar contexts

        if not similar_contexts:
            return {
                "similar_contexts": [],
                "frequency_scores": {},
                "pattern_strength": 0.0,
            }

        # Calculate frequency scores
        frequency_scores = defaultdict(float)
        total_contexts = len(similar_contexts)

        for i, stat in enumerate(similar_contexts):
            # Recent contexts get higher weight
            weight = 1.0 / (i + 1) if i < 20 else 0.1
            frequency_scores[stat.number] += weight

        # Normalize scores
        max_score = max(frequency_scores.values()) if frequency_scores else 1
        normalized_scores = {
            num: score / max_score for num, score in frequency_scores.items()
        }

        pattern_strength = min(1.0, total_contexts / 50.0)  # Strong if 50+ contexts

        return {
            "similar_contexts": [
                {
                    "date": stat.date.isoformat(),
                    "number": stat.number,
                    "appeared_in_special": stat.appeared_in_special,
                }
                for stat in similar_contexts[:20]
            ],
            "frequency_scores": normalized_scores,
            "pattern_strength": pattern_strength,
        }

    def _detect_cycle_patterns(self) -> dict:
        """
        Phát hiện patterns chu kỳ

        Returns:
            dict: {
                "weekly_patterns": dict,
                "monthly_patterns": dict,
                "cycle_consistency": float
            }
        """
        from datetime import timedelta

        # Weekly pattern analysis
        weekly_patterns = self._analyze_weekly_patterns()

        # Monthly pattern analysis
        monthly_patterns = self._analyze_monthly_patterns()

        # Calculate cycle consistency
        cycle_consistency = self._calculate_cycle_consistency(
            weekly_patterns, monthly_patterns
        )

        return {
            "weekly_patterns": weekly_patterns,
            "monthly_patterns": monthly_patterns,
            "cycle_consistency": cycle_consistency,
        }

    def _analyze_weekly_patterns(self) -> dict:
        """Analyze weekly occurrence patterns"""
        from collections import defaultdict

        # Get data for same weekday in recent months
        same_weekday_stats = (
            NumberFrequencyStats.objects.filter(
                day_of_week=self.target_date.weekday(),
                date__gte=self.analysis_date - timedelta(days=90),
                date__lt=self.analysis_date,
            )
            .values("number")
            .annotate(count=Count("number"), last_seen=models.Max("date"))
            .order_by("-count")
        )

        weekly_scores = {}
        for stat in same_weekday_stats:
            weekly_scores[stat["number"]] = stat["count"]

        return {
            "weekday": self.target_date.weekday(),
            "pattern_scores": weekly_scores,
            "total_occurrences": sum(weekly_scores.values()),
        }

    def _analyze_monthly_patterns(self) -> dict:
        """Analyze monthly occurrence patterns"""
        # Get data for same day_of_month in recent years
        same_day_stats = (
            NumberFrequencyStats.objects.filter(
                day_of_month=self.target_date.day,
                date__gte=self.analysis_date - timedelta(days=365),
                date__lt=self.analysis_date,
            )
            .values("number")
            .annotate(count=Count("number"))
            .order_by("-count")
        )

        monthly_scores = {}
        for stat in same_day_stats:
            monthly_scores[stat["number"]] = stat["count"]

        return {
            "day_of_month": self.target_date.day,
            "pattern_scores": monthly_scores,
            "total_occurrences": sum(monthly_scores.values()),
        }

    def _calculate_cycle_consistency(
        self, weekly_patterns: dict, monthly_patterns: dict
    ) -> float:
        """Calculate how consistent the cycles are"""
        weekly_total = weekly_patterns.get("total_occurrences", 0)
        monthly_total = monthly_patterns.get("total_occurrences", 0)

        if weekly_total == 0 and monthly_total == 0:
            return 0.0

        # Simple consistency metric
        consistency = min(1.0, (weekly_total + monthly_total) / 100.0)
        return consistency

    def _calculate_phase_compatibility(self) -> dict:
        """
        Calculate compatibility with current cyclical phase

        Returns:
            dict: {
                "current_phase": str,
                "phase_scores": dict,
                "compatibility_strength": float
            }
        """
        # Get current cyclical context
        try:
            context = CyclicalContextEngine.objects.get(
                analysis_date=self.analysis_date
            )
            current_phase = context.day_of_month_phase
            cycle_strength = context.cycle_strength
        except CyclicalContextEngine.DoesNotExist:
            current_phase = "mid"  # Default fallback
            cycle_strength = 0.5

        # Calculate phase-specific scores
        phase_scores = self._get_phase_specific_scores(current_phase)

        return {
            "current_phase": current_phase,
            "phase_scores": phase_scores,
            "compatibility_strength": cycle_strength,
        }

    def _get_phase_specific_scores(self, phase: str) -> dict:
        """Get scores for numbers in specific phase"""
        from datetime import timedelta

        # Define phase date ranges
        if phase == "early":
            day_range = range(1, 11)
        elif phase == "mid":
            day_range = range(11, 21)
        else:  # late
            day_range = range(21, 32)

        # Get historical data for this phase
        phase_stats = (
            NumberFrequencyStats.objects.filter(
                day_of_month__in=day_range,
                date__gte=self.analysis_date - timedelta(days=180),
                date__lt=self.analysis_date,
            )
            .values("number")
            .annotate(count=Count("number"))
            .order_by("-count")
        )

        phase_scores = {}
        for stat in phase_stats:
            phase_scores[stat["number"]] = stat["count"]

        return phase_scores

    def _generate_number_predictions(
        self, frequency_analysis: dict, cycle_patterns: dict, phase_compatibility: dict
    ) -> list:
        """
        Generate final number predictions với scoring

        Returns:
            list: [{"number": str, "score": float, "reasons": list}, ...]
        """
        from collections import defaultdict

        final_scores = defaultdict(float)
        number_reasons = defaultdict(list)

        # 1. Frequency scores (weight: 0.4)
        freq_scores = frequency_analysis.get("frequency_scores", {})
        for number, score in freq_scores.items():
            final_scores[number] += score * 0.4
            if score > 0.5:
                number_reasons[number].append(f"High frequency: {score:.2f}")

        # 2. Weekly pattern scores (weight: 0.3)
        weekly_scores = cycle_patterns.get("weekly_patterns", {}).get(
            "pattern_scores", {}
        )
        max_weekly = max(weekly_scores.values()) if weekly_scores else 1
        for number, count in weekly_scores.items():
            score = count / max_weekly
            final_scores[number] += score * 0.3
            if score > 0.3:
                number_reasons[number].append(f"Weekly pattern: {score:.2f}")

        # 3. Monthly pattern scores (weight: 0.2)
        monthly_scores = cycle_patterns.get("monthly_patterns", {}).get(
            "pattern_scores", {}
        )
        max_monthly = max(monthly_scores.values()) if monthly_scores else 1
        for number, count in monthly_scores.items():
            score = count / max_monthly
            final_scores[number] += score * 0.2
            if score > 0.2:
                number_reasons[number].append(f"Monthly pattern: {score:.2f}")

        # 4. Phase compatibility scores (weight: 0.1)
        phase_scores = phase_compatibility.get("phase_scores", {})
        max_phase = max(phase_scores.values()) if phase_scores else 1
        for number, count in phase_scores.items():
            score = count / max_phase
            final_scores[number] += score * 0.1
            if score > 0.1:
                number_reasons[number].append(f"Phase compatible: {score:.2f}")

        # Sort and format predictions
        sorted_predictions = sorted(
            final_scores.items(), key=lambda x: x[1], reverse=True
        )

        predictions = []
        for number, score in sorted_predictions[:30]:  # Top 30
            predictions.append(
                {
                    "number": str(number).zfill(2),
                    "score": round(score, 3),
                    "reasons": number_reasons[number],
                }
            )

        return predictions

    def _calculate_prediction_confidence(
        self, frequency_analysis: dict, cycle_patterns: dict
    ) -> float:
        """
        Calculate overall prediction confidence

        Returns:
            float: Confidence score 0-1
        """
        # Base confidence from pattern strength
        pattern_strength = frequency_analysis.get("pattern_strength", 0)

        # Cycle consistency bonus
        cycle_consistency = cycle_patterns.get("cycle_consistency", 0)

        # Data volume bonus
        similar_contexts = len(frequency_analysis.get("similar_contexts", []))
        data_bonus = min(0.3, similar_contexts / 50.0)  # Max 0.3 bonus

        confidence = pattern_strength * 0.5 + cycle_consistency * 0.3 + data_bonus
        return min(1.0, confidence)

    def _calculate_cycle_strength(self) -> float:
        """Calculate overall cycle strength"""
        try:
            context = CyclicalContextEngine.objects.get(
                analysis_date=self.analysis_date
            )
            return context.cycle_strength
        except CyclicalContextEngine.DoesNotExist:
            return 0.5  # Default fallback

    def _set_fallback_prediction(self) -> None:
        """Set fallback prediction when main logic fails"""
        self.predicted_numbers = []
        self.prediction_confidence = 0.0
        self.cycle_strength = 0.0
        self.frequency_analysis = {"error": "Fallback prediction"}
        self.cycle_patterns = {"error": "Fallback prediction"}
        self.phase_compatibility = {"error": "Fallback prediction"}


class MethodCyclicalPerformance(models.Model):
    """Theo dõi hiệu suất theo chu kỳ của các phương pháp dự đoán"""

    method_name = models.CharField(max_length=100)
    year = models.IntegerField()
    month = models.IntegerField()

    # Hiệu suất theo giai đoạn trong tháng
    early_month_performance = JSONField(
        default=dict, help_text="Hiệu suất 10 ngày đầu tháng"
    )
    mid_month_performance = JSONField(
        default=dict, help_text="Hiệu suất 10 ngày giữa tháng"
    )
    late_month_performance = JSONField(
        default=dict, help_text="Hiệu suất 10 ngày cuối tháng"
    )

    # Thống kê tổng quát
    total_hit_days = models.IntegerField(
        default=0, help_text="Tổng số ngày trúng trong tháng"
    )
    total_days = models.IntegerField(
        default=0, help_text="Tổng số ngày có dự đoán trong tháng"
    )
    hit_rate = models.FloatField(
        default=0, help_text="Tỷ lệ trúng (total_hit_days/total_days)"
    )

    # Trạng thái chu kỳ
    fatigue_threshold_reached = models.BooleanField(
        default=False,
        help_text="Đánh dấu phương pháp đã đạt ngưỡng mệt mỏi (19-21 ngày)",
    )
    fatigue_reached_on = models.DateField(
        null=True, blank=True, help_text="Ngày phương pháp đạt ngưỡng mệt mỏi"
    )

    class Meta:
        unique_together = ("method_name", "year", "month")
        indexes = [
            models.Index(fields=["method_name"]),
            models.Index(fields=["year", "month"]),
            models.Index(fields=["fatigue_threshold_reached"]),
        ]

    def __str__(self):
        return f"{self.method_name}: {self.month}/{self.year} - {self.total_hit_days}/{self.total_days} days"

    def update_performance_data(self, session_date, hit_count, total_predictions):
        """Cập nhật dữ liệu performance cho method"""
        from datetime import timedelta

        # Determine phase
        day = session_date.day
        if day <= 10:
            phase = "early"
        elif day <= 20:
            phase = "mid"
        else:
            phase = "late"

        # Update appropriate phase data
        phase_field = f"{phase}_month_performance"
        current_data = getattr(self, phase_field)

        if not isinstance(current_data, dict):
            current_data = {}

        # Update hit rate
        current_hits = current_data.get("total_hits", 0) + hit_count
        current_total = current_data.get("total_predictions", 0) + total_predictions

        current_data.update(
            {
                "total_hits": current_hits,
                "total_predictions": current_total,
                "hit_rate": current_hits / current_total if current_total > 0 else 0,
                "last_updated": session_date.isoformat(),
            }
        )

        setattr(self, phase_field, current_data)

        # Update overall stats
        self.total_days += 1
        if hit_count > 0:
            self.total_hit_days += 1

        self.hit_rate = (
            self.total_hit_days / self.total_days if self.total_days > 0 else 0
        )


class CyclicalContextEngine(models.Model):
    """Engine phân tích bối cảnh chu kỳ"""

    analysis_date = models.DateField(unique=True, verbose_name="Ngày phân tích")

    # Cyclical context data
    day_of_month_phase = models.CharField(
        max_length=10,
        choices=[("early", "Đầu tháng"), ("mid", "Giữa tháng"), ("late", "Cuối tháng")],
        verbose_name="Giai đoạn trong tháng",
    )
    week_phase = models.CharField(
        max_length=10,
        choices=[("start", "Đầu tuần"), ("mid", "Giữa tuần"), ("end", "Cuối tuần")],
        verbose_name="Giai đoạn trong tuần",
    )
    month_trend = models.CharField(
        max_length=15,
        choices=[("ascending", "Tăng"), ("peak", "Đỉnh"), ("descending", "Giảm")],
        verbose_name="Xu hướng tháng",
    )

    # Active cycles and patterns
    active_cycles = models.JSONField(default=list, verbose_name="Chu kỳ đang hoạt động")
    fatigue_methods = models.JSONField(default=list, verbose_name="Methods đã mệt mỏi")
    cycle_strength = models.FloatField(default=0.0, verbose_name="Độ mạnh chu kỳ")

    # Analysis metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cyclical Context Engine"
        verbose_name_plural = "Cyclical Context Engines"
        ordering = ["-analysis_date"]
        indexes = [
            models.Index(fields=["analysis_date"]),
            models.Index(fields=["day_of_month_phase"]),
            models.Index(fields=["week_phase"]),
        ]

    def __str__(self):
        return (
            f"Context {self.analysis_date}: {self.day_of_month_phase}/{self.week_phase}"
        )

    @classmethod
    def analyze_current_context(cls, analysis_date):
        """Phân tích bối cảnh chu kỳ hiện tại"""
        context, created = cls.objects.get_or_create(
            analysis_date=analysis_date,
            defaults={
                "day_of_month_phase": cls._get_month_phase(analysis_date),
                "week_phase": cls._get_week_phase(analysis_date),
                "month_trend": cls._get_month_trend(analysis_date),
                "active_cycles": cls._identify_active_cycles(analysis_date),
                "fatigue_methods": cls._detect_fatigued_methods(analysis_date),
                "cycle_strength": cls._calculate_cycle_strength(analysis_date),
            },
        )

        if not created:
            # Update existing context
            context.day_of_month_phase = cls._get_month_phase(analysis_date)
            context.week_phase = cls._get_week_phase(analysis_date)
            context.month_trend = cls._get_month_trend(analysis_date)
            context.active_cycles = cls._identify_active_cycles(analysis_date)
            context.fatigue_methods = cls._detect_fatigued_methods(analysis_date)
            context.cycle_strength = cls._calculate_cycle_strength(analysis_date)
            context.save()

        return context

    @staticmethod
    def _get_month_phase(date):
        day = date.day
        if day <= 10:
            return "early"
        elif day <= 20:
            return "mid"
        else:
            return "late"

    @staticmethod
    def _get_week_phase(date):
        weekday = date.weekday()  # 0=Monday, 6=Sunday
        if weekday <= 1:  # Mon, Tue
            return "start"
        elif weekday <= 4:  # Wed, Thu, Fri
            return "mid"
        else:  # Sat, Sun
            return "end"

    @staticmethod
    def _get_month_trend(analysis_date):
        """Phân tích xu hướng tháng dựa trên historical performance"""
        from datetime import timedelta

        # Lấy data 30 ngày gần đây
        end_date = analysis_date - timedelta(days=1)
        start_date = end_date - timedelta(days=30)

        try:
            # Phân tích trend từ NumberFrequencyStats
            recent_stats = (
                NumberFrequencyStats.objects.filter(date__range=[start_date, end_date])
                .values("date")
                .annotate(daily_count=models.Count("number"))
                .order_by("date")
            )

            if len(recent_stats) < 10:
                return "stable"

            # Simple trend analysis
            daily_counts = [stat["daily_count"] for stat in recent_stats]
            first_half = daily_counts[: len(daily_counts) // 2]
            second_half = daily_counts[len(daily_counts) // 2 :]

            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)

            if second_avg > first_avg * 1.1:
                return "ascending"
            elif second_avg < first_avg * 0.9:
                return "descending"
            else:
                return "peak"

        except Exception:
            return "stable"

    @staticmethod
    def _identify_active_cycles(analysis_date):
        """Xác định các chu kỳ đang hoạt động"""
        active_cycles = []

        # Weekly cycle check
        if analysis_date.weekday() in [0, 1, 2]:  # Mon, Tue, Wed
            active_cycles.append({"type": "weekly", "phase": "active", "strength": 0.8})

        # Monthly cycle check
        day = analysis_date.day
        if 5 <= day <= 25:  # Mid-month activity
            active_cycles.append(
                {"type": "monthly", "phase": "active", "strength": 0.7}
            )

        return active_cycles

    @staticmethod
    def _detect_fatigued_methods(analysis_date):
        """Phát hiện methods đã đạt ngưỡng mệt mỏi"""
        from datetime import timedelta

        fatigued_methods = []

        # Kiểm tra MethodCyclicalPerformance
        current_month = analysis_date.month
        current_year = analysis_date.year

        fatigued_performances = MethodCyclicalPerformance.objects.filter(
            year=current_year, month=current_month, fatigue_threshold_reached=True
        )

        for performance in fatigued_performances:
            if performance.fatigue_reached_on:
                days_fatigued = (analysis_date - performance.fatigue_reached_on).days
                if days_fatigued <= 21:  # Still in fatigue period
                    fatigued_methods.append(
                        {
                            "method_name": performance.method_name,
                            "days_fatigued": days_fatigued,
                            "fatigue_since": performance.fatigue_reached_on.isoformat(),
                        }
                    )

        return fatigued_methods

    @staticmethod
    def _calculate_cycle_strength(analysis_date):
        """Tính độ mạnh chu kỳ tổng thể"""
        from datetime import timedelta

        # Base strength từ vị trí trong tháng và tuần
        day = analysis_date.day
        weekday = analysis_date.weekday()

        # Monthly strength (cao nhất ở giữa tháng)
        if 8 <= day <= 22:
            month_strength = 0.8
        elif 5 <= day <= 25:
            month_strength = 0.6
        else:
            month_strength = 0.4

        # Weekly strength (cao nhất ở giữa tuần)
        if weekday in [1, 2, 3]:  # Tue, Wed, Thu
            week_strength = 0.8
        elif weekday in [0, 4]:  # Mon, Fri
            week_strength = 0.6
        else:  # Sat, Sun
            week_strength = 0.3

        # Combined strength
        cycle_strength = month_strength * 0.6 + week_strength * 0.4

        return round(cycle_strength, 3)


class MethodCycleSyncMatrix(models.Model):
    """Ma trận đồng bộ method-cycle"""

    method = models.ForeignKey(
        "predictions_tracker.PredictionMethod",
        on_delete=models.CASCADE,
        related_name="cycle_sync_records",
    )
    analysis_date = models.DateField(verbose_name="Ngày phân tích")

    # Cyclical fitness metrics
    cyclical_fitness = models.FloatField(default=0.0, verbose_name="Độ phù hợp chu kỳ")
    phase_alignment = models.FloatField(default=0.0, verbose_name="Độ đồng bộ phase")
    fatigue_risk = models.FloatField(default=0.0, verbose_name="Rủi ro mệt mỏi")

    # Performance by phases
    early_month_sync = models.FloatField(default=0.0, verbose_name="Sync đầu tháng")
    mid_month_sync = models.FloatField(default=0.0, verbose_name="Sync giữa tháng")
    late_month_sync = models.FloatField(default=0.0, verbose_name="Sync cuối tháng")

    # Trend analysis
    trend_direction = models.CharField(
        max_length=15,
        choices=[
            ("improving", "Cải thiện"),
            ("stable", "Ổn định"),
            ("declining", "Giảm"),
        ],
        default="stable",
    )
    trend_strength = models.FloatField(default=0.0, verbose_name="Độ mạnh xu hướng")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["method", "analysis_date"]
        verbose_name = "Method Cycle Sync Matrix"
        verbose_name_plural = "Method Cycle Sync Matrices"
        indexes = [
            models.Index(fields=["analysis_date"]),
            models.Index(fields=["cyclical_fitness"]),
            models.Index(fields=["fatigue_risk"]),
        ]

    def __str__(self):
        return f"{self.method.name} - {self.analysis_date} (Fitness: {self.cyclical_fitness:.2f})"

    @classmethod
    def build_sync_matrix(cls, analysis_date):
        """Xây dựng ma trận đồng bộ cho ngày phân tích"""
        from predictions_tracker.models import PredictionMethod

        # Get active methods
        active_methods = PredictionMethod.objects.filter(is_active=True)

        # Get cyclical context
        context = CyclicalContextEngine.analyze_current_context(analysis_date)

        sync_records = []

        for method in active_methods:
            sync_data = cls._calculate_method_sync(method, analysis_date, context)

            sync_record, created = cls.objects.update_or_create(
                method=method, analysis_date=analysis_date, defaults=sync_data
            )

            sync_records.append(sync_record)

        return sync_records

    @classmethod
    def _calculate_method_sync(cls, method, analysis_date, context):
        """Tính toán sync data cho method"""
        current_phase = context.day_of_month_phase

        # Get cyclical performance data
        try:
            performance = MethodCyclicalPerformance.objects.get(
                method_name=method.name,
                year=analysis_date.year,
                month=analysis_date.month,
            )

            # Calculate phase-specific fitness
            if current_phase == "early":
                phase_performance = performance.early_month_performance
            elif current_phase == "mid":
                phase_performance = performance.mid_month_performance
            else:
                phase_performance = performance.late_month_performance

            cyclical_fitness = phase_performance.get("hit_rate", 0) * 100

            # Calculate phase alignment
            early_rate = performance.early_month_performance.get("hit_rate", 0)
            mid_rate = performance.mid_month_performance.get("hit_rate", 0)
            late_rate = performance.late_month_performance.get("hit_rate", 0)

            rates = [early_rate, mid_rate, late_rate]
            max_rate = max(rates)
            current_rate = phase_performance.get("hit_rate", 0)

            phase_alignment = current_rate / max_rate if max_rate > 0 else 0

            # Calculate fatigue risk
            fatigue_risk = 1.0 if performance.fatigue_threshold_reached else 0.0
            if performance.total_days >= 15:  # Approaching fatigue
                fatigue_risk = min(1.0, performance.total_days / 21.0)

        except MethodCyclicalPerformance.DoesNotExist:
            # Fallback: Use method's general statistics if no cyclical data
            if method.success_rate > 0:
                # Estimate cyclical fitness from general success rate
                cyclical_fitness = method.success_rate
                
                # Estimate phase alignment based on current phase
                if current_phase == "mid":
                    phase_alignment = 0.8  # Mid-month usually better
                elif current_phase == "early":
                    phase_alignment = 0.6
                else:
                    phase_alignment = 0.5
                
                # Lower fatigue risk for methods without history
                fatigue_risk = 0.3
                
                # Estimate phase rates
                early_rate = method.success_rate * 0.8 / 100
                mid_rate = method.success_rate * 1.0 / 100
                late_rate = method.success_rate * 0.7 / 100
            else:
                # Complete fallback with minimal values
                cyclical_fitness = 25.0  # Give a chance to new methods
                phase_alignment = 0.5
                fatigue_risk = 0.2
                early_rate = 0.25
                mid_rate = 0.25
                late_rate = 0.25

        return {
            "cyclical_fitness": round(cyclical_fitness, 3),
            "phase_alignment": round(phase_alignment, 3),
            "fatigue_risk": round(fatigue_risk, 3),
            "early_month_sync": round(early_rate * 100, 3),
            "mid_month_sync": round(mid_rate * 100, 3),
            "late_month_sync": round(late_rate * 100, 3),
            "trend_direction": cls._determine_trend_direction(method, analysis_date),
            "trend_strength": cls._calculate_trend_strength(method, analysis_date),
        }

    @staticmethod
    def _determine_trend_direction(method, analysis_date):
        """Xác định hướng xu hướng của method"""
        from datetime import timedelta

        # Compare recent performance with previous period
        current_month = analysis_date.month
        current_year = analysis_date.year

        try:
            current_perf = MethodCyclicalPerformance.objects.get(
                method_name=method.name, year=current_year, month=current_month
            )

            # Get previous month
            prev_date = analysis_date - timedelta(days=30)
            prev_perf = MethodCyclicalPerformance.objects.get(
                method_name=method.name, year=prev_date.year, month=prev_date.month
            )

            current_rate = current_perf.hit_rate
            prev_rate = prev_perf.hit_rate

            if current_rate > prev_rate * 1.1:
                return "improving"
            elif current_rate < prev_rate * 0.9:
                return "declining"
            else:
                return "stable"

        except MethodCyclicalPerformance.DoesNotExist:
            return "stable"

    @staticmethod
    def _calculate_trend_strength(method, analysis_date):
        """Tính độ mạnh xu hướng"""
        from datetime import timedelta

        try:
            # Get recent performance data (last 3 months)
            performances = []
            for i in range(3):
                check_date = analysis_date - timedelta(days=30 * i)
                try:
                    perf = MethodCyclicalPerformance.objects.get(
                        method_name=method.name,
                        year=check_date.year,
                        month=check_date.month,
                    )
                    performances.append(perf.hit_rate)
                except MethodCyclicalPerformance.DoesNotExist:
                    continue

            if len(performances) < 2:
                return 0.0

            # Calculate trend strength using linear regression
            import numpy as np

            x = list(range(len(performances)))
            y = performances

            if len(x) > 1:
                slope = np.polyfit(x, y, 1)[0]
                return abs(slope) * 10  # Scale for interpretability

        except Exception:
            pass

        return 0.0


class ABTestVariant(models.Model):
    """A/B Test Variant cho parameter optimization"""

    test_name = models.CharField(max_length=100, verbose_name="Tên test")
    variant_name = models.CharField(max_length=50, verbose_name="Tên variant")

    # Test configuration
    target_method = models.ForeignKey(
        PredictionMethod,
        on_delete=models.CASCADE,
        related_name="ab_test_variants",
        verbose_name="Method được test",
    )

    # Parameter configuration
    test_parameters = models.JSONField(
        default=dict,
        verbose_name="Tham số test",
        help_text="Parameters được test trong variant này",
    )
    baseline_parameters = models.JSONField(
        default=dict,
        verbose_name="Tham số baseline",
        help_text="Parameters gốc để so sánh",
    )

    # Test period
    start_date = models.DateField(verbose_name="Ngày bắt đầu test")
    end_date = models.DateField(verbose_name="Ngày kết thúc test")

    # Traffic allocation
    traffic_percentage = models.FloatField(
        default=50.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Phần trăm traffic",
        help_text="Phần trăm requests được route đến variant này",
    )

    # Consistent hashing key
    hash_key = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Hash key",
        help_text="Key cho consistent hashing",
    )

    # Status
    STATUS_CHOICES = [
        ("draft", "Nháp"),
        ("active", "Đang chạy"),
        ("paused", "Tạm dừng"),
        ("completed", "Hoàn thành"),
        ("cancelled", "Đã hủy"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="Trạng thái",
    )

    # Metadata
    created_by = models.CharField(max_length=100, verbose_name="Người tạo")
    hypothesis = models.TextField(
        blank=True,
        verbose_name="Giả thuyết",
        help_text="Giả thuyết về kết quả mong đợi",
    )
    success_criteria = models.JSONField(
        default=dict,
        verbose_name="Tiêu chí thành công",
        help_text="Định nghĩa khi nào test được coi là thành công",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "A/B Test Variant"
        verbose_name_plural = "A/B Test Variants"
        unique_together = ["test_name", "variant_name"]
        indexes = [
            models.Index(fields=["test_name", "status"]),
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["hash_key"]),
            models.Index(fields=["target_method", "status"]),
        ]

    def __str__(self):
        return f"{self.test_name} - {self.variant_name} ({self.status})"

    def save(self, *args, **kwargs):
        """Auto-generate hash key if not provided"""
        if not self.hash_key:
            self.hash_key = self._generate_hash_key()
        super().save(*args, **kwargs)

    def _generate_hash_key(self) -> str:
        """Generate unique hash key for consistent hashing"""
        base_string = f"{self.test_name}_{self.variant_name}_{self.target_method.code}"
        return hashlib.sha256(base_string.encode()).hexdigest()

    def is_active_on_date(self, check_date: date) -> bool:
        """Check if variant is active on specific date"""
        return (
            self.status == "active" and self.start_date <= check_date <= self.end_date
        )

    def should_serve_traffic(self, request_id: str) -> bool:
        """
        Determine if this variant should serve traffic for request

        Args:
            request_id: Unique identifier for request (e.g., date + method)

        Returns:
            bool: True if should serve this variant
        """
        try:
            # Consistent hashing based on request_id
            hash_input = f"{request_id}_{self.hash_key}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
            percentage = (hash_value % 100) + 1  # 1-100

            return percentage <= self.traffic_percentage

        except Exception:
            return False

    def get_current_performance(self) -> dict:
        """
        Get current performance metrics

        Returns:
            dict: {
                "total_tests": int,
                "avg_accuracy": float,
                "success_rate": float,
                "last_test_date": str
            }
        """
        try:
            results = self.test_results.all()

            if not results.exists():
                return {
                    "total_tests": 0,
                    "avg_accuracy": 0.0,
                    "success_rate": 0.0,
                    "last_test_date": None,
                }

            stats = results.aggregate(
                total_tests=Count("id"),
                avg_accuracy=Avg("accuracy_rate"),
                success_count=Count("id", filter=models.Q(is_successful=True)),
            )

            success_rate = (
                (stats["success_count"] / stats["total_tests"]) * 100
                if stats["total_tests"] > 0
                else 0
            )
            last_result = results.order_by("-test_date").first()

            return {
                "total_tests": stats["total_tests"],
                "avg_accuracy": round(stats["avg_accuracy"] or 0, 4),
                "success_rate": round(success_rate, 2),
                "last_test_date": (
                    last_result.test_date.isoformat() if last_result else None
                ),
            }

        except Exception as e:
            logger.error(f"Error getting performance for variant {self.id}: {str(e)}")
            return {
                "total_tests": 0,
                "avg_accuracy": 0.0,
                "success_rate": 0.0,
                "last_test_date": None,
                "error": str(e),
            }


class ABTestResult(models.Model):
    """Kết quả A/B Test"""

    variant = models.ForeignKey(
        ABTestVariant,
        on_delete=models.CASCADE,
        related_name="test_results",
        verbose_name="Variant",
    )

    # Test execution details
    test_date = models.DateField(verbose_name="Ngày test", db_index=True)
    session_id = models.CharField(
        max_length=100,
        verbose_name="Session ID",
        help_text="Unique ID cho test session",
    )

    # Prediction data
    predicted_numbers = models.JSONField(
        verbose_name="Số dự đoán", help_text="Numbers được predict bởi variant"
    )
    actual_numbers = models.JSONField(
        verbose_name="Số thực tế", help_text="Actual numbers from KetQuaXoSo"
    )
    hit_numbers = models.JSONField(
        default=list, verbose_name="Số trúng", help_text="Numbers trúng (intersection)"
    )

    # Performance metrics
    hit_count = models.IntegerField(default=0, verbose_name="Số lượng trúng")
    total_predicted = models.IntegerField(default=0, verbose_name="Tổng số dự đoán")
    accuracy_rate = models.FloatField(default=0.0, verbose_name="Tỷ lệ trúng")

    # Statistical significance metrics
    confidence_interval_lower = models.FloatField(
        null=True, blank=True, verbose_name="CI lower bound"
    )
    confidence_interval_upper = models.FloatField(
        null=True, blank=True, verbose_name="CI upper bound"
    )
    p_value = models.FloatField(null=True, blank=True, verbose_name="P-value")

    # Success criteria evaluation
    is_successful = models.BooleanField(
        default=False, verbose_name="Đạt tiêu chí thành công"
    )
    success_details = models.JSONField(
        default=dict,
        verbose_name="Chi tiết thành công",
        help_text="Details về việc đánh giá success criteria",
    )

    # Performance comparison with baseline
    baseline_accuracy = models.FloatField(
        null=True, blank=True, verbose_name="Baseline accuracy"
    )
    performance_improvement = models.FloatField(
        null=True, blank=True, verbose_name="Cải thiện performance (%)"
    )

    # Metadata
    execution_time_ms = models.IntegerField(
        default=0, verbose_name="Thời gian thực thi (ms)"
    )
    error_message = models.TextField(blank=True, verbose_name="Thông báo lỗi")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "A/B Test Result"
        verbose_name_plural = "A/B Test Results"
        unique_together = ["variant", "test_date", "session_id"]
        indexes = [
            models.Index(fields=["test_date"]),
            models.Index(fields=["variant", "test_date"]),
            models.Index(fields=["accuracy_rate"]),
            models.Index(fields=["is_successful"]),
        ]

    def __str__(self):
        return f"{self.variant.test_name} - {self.test_date} (Acc: {self.accuracy_rate:.2%})"

    def save(self, *args, **kwargs):
        """Auto-calculate metrics on save"""
        if self.predicted_numbers and self.actual_numbers:
            self._calculate_performance_metrics()
            self._evaluate_success_criteria()
        super().save(*args, **kwargs)

    def _calculate_performance_metrics(self) -> None:
        """Calculate hit count, accuracy rate, and hit numbers"""
        try:
            predicted_set = set(self.predicted_numbers)
            actual_set = set(self.actual_numbers)

            # Calculate hits
            hit_numbers = list(predicted_set.intersection(actual_set))
            self.hit_numbers = hit_numbers
            self.hit_count = len(hit_numbers)
            self.total_predicted = len(predicted_set)

            # Calculate accuracy rate
            self.accuracy_rate = (
                self.hit_count / self.total_predicted
                if self.total_predicted > 0
                else 0.0
            )

            # Calculate confidence interval (Wilson score interval for binomial proportion)
            self._calculate_confidence_interval()

        except Exception as e:
            logger.error(f"Error calculating metrics for result {self.id}: {str(e)}")
            self.error_message = f"Metrics calculation error: {str(e)}"

    def _calculate_confidence_interval(self, confidence_level: float = 0.95) -> None:
        """Calculate Wilson score confidence interval"""
        try:
            import math

            n = self.total_predicted
            p = self.accuracy_rate

            if n == 0:
                self.confidence_interval_lower = 0.0
                self.confidence_interval_upper = 0.0
                return

            # Z-score for confidence level (95% = 1.96)
            z = 1.96 if confidence_level == 0.95 else 2.576  # 99%

            # Wilson score interval
            denominator = 1 + (z**2 / n)
            centre_adjusted_probability = (p + (z**2 / (2 * n))) / denominator
            adjustment = (z / denominator) * math.sqrt(
                (p * (1 - p) + z**2 / (4 * n)) / n
            )

            self.confidence_interval_lower = max(
                0.0, centre_adjusted_probability - adjustment
            )
            self.confidence_interval_upper = min(
                1.0, centre_adjusted_probability + adjustment
            )

        except Exception as e:
            logger.warning(f"CI calculation error: {str(e)}")
            self.confidence_interval_lower = 0.0
            self.confidence_interval_upper = 1.0

    def _evaluate_success_criteria(self) -> None:
        """Evaluate if result meets success criteria"""
        try:
            success_criteria = self.variant.success_criteria

            if not success_criteria:
                self.is_successful = False
                self.success_details = {"error": "No success criteria defined"}
                return

            evaluation_results = {}
            overall_success = True

            # Check minimum accuracy threshold
            min_accuracy = success_criteria.get("min_accuracy", 0.0)
            if min_accuracy > 0:
                meets_min_accuracy = self.accuracy_rate >= min_accuracy
                evaluation_results["min_accuracy"] = {
                    "required": min_accuracy,
                    "actual": self.accuracy_rate,
                    "meets_criteria": meets_min_accuracy,
                }
                overall_success = overall_success and meets_min_accuracy

            # Check improvement over baseline
            min_improvement = success_criteria.get("min_improvement_percent", 0.0)
            if min_improvement > 0 and self.baseline_accuracy is not None:
                improvement = (
                    (self.accuracy_rate - self.baseline_accuracy)
                    / self.baseline_accuracy
                ) * 100
                self.performance_improvement = improvement

                meets_improvement = improvement >= min_improvement
                evaluation_results["improvement"] = {
                    "required": min_improvement,
                    "actual": improvement,
                    "meets_criteria": meets_improvement,
                }
                overall_success = overall_success and meets_improvement

            # Check statistical significance
            max_p_value = success_criteria.get("max_p_value", 1.0)
            if self.p_value is not None:
                is_significant = self.p_value <= max_p_value
                evaluation_results["statistical_significance"] = {
                    "required_p_value": max_p_value,
                    "actual_p_value": self.p_value,
                    "is_significant": is_significant,
                }
                overall_success = overall_success and is_significant

            self.is_successful = overall_success
            self.success_details = {
                "overall_success": overall_success,
                "criteria_evaluation": evaluation_results,
                "evaluated_at": timezone.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Success criteria evaluation error: {str(e)}")
            self.is_successful = False
            self.success_details = {"error": str(e)}

    def compare_with_baseline(self, baseline_result: "ABTestResult") -> dict:
        """
        Compare this result with baseline result

        Args:
            baseline_result: ABTestResult object to compare against

        Returns:
            dict: Comparison metrics
        """
        try:
            if not baseline_result:
                return {"error": "No baseline result provided"}

            # Basic metrics comparison
            accuracy_diff = self.accuracy_rate - baseline_result.accuracy_rate
            accuracy_diff_percent = (
                (accuracy_diff / baseline_result.accuracy_rate) * 100
                if baseline_result.accuracy_rate > 0
                else 0
            )

            # Statistical test (simplified)
            try:
                from scipy import stats

                # Two-proportion z-test
                count1 = self.hit_count
                nobs1 = self.total_predicted
                count2 = baseline_result.hit_count
                nobs2 = baseline_result.total_predicted

                if nobs1 > 0 and nobs2 > 0:
                    stat, p_value = stats.proportions_ztest(
                        [count1, count2], [nobs1, nobs2]
                    )
                    self.p_value = p_value
                else:
                    stat, p_value = 0, 1.0

            except ImportError:
                stat, p_value = 0, 1.0
                logger.warning("scipy not available for statistical tests")

            return {
                "baseline_accuracy": baseline_result.accuracy_rate,
                "variant_accuracy": self.accuracy_rate,
                "accuracy_difference": accuracy_diff,
                "accuracy_improvement_percent": accuracy_diff_percent,
                "statistical_significance": {
                    "z_statistic": stat,
                    "p_value": p_value,
                    "is_significant": p_value < 0.05 if p_value is not None else False,
                },
                "comparison_date": timezone.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Baseline comparison error: {str(e)}")
            return {"error": str(e)}

class ABTestStatus(models.TextChoices):
    """Status của A/B test"""
    DRAFT = 'draft', 'Draft'
    ACTIVE = 'active', 'Active'
    PAUSED = 'paused', 'Paused'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'

class WeeklyPredictionMethod(models.Model):
    """
    Method dự đoán theo thứ trong tuần - TÁCH RIÊNG
    """
    # Inherit từ PredictionMethod nhưng có logic riêng
    base_method = models.OneToOneField(
        PredictionMethod,
        on_delete=models.CASCADE,
        related_name="weekly_variant",
        verbose_name="Method gốc"
    )
    
    # Thứ trong tuần (0=Monday, 6=Sunday)
    target_weekday = models.IntegerField(
        choices=[
            (0, "Thứ 2"),
            (1, "Thứ 3"), 
            (2, "Thứ 4"),
            (3, "Thứ 5"),
            (4, "Thứ 6"),
            (5, "Thứ 7"),
            (6, "Chủ nhật"),
        ],
        verbose_name="Thứ mục tiêu"
    )
    
    # Số tuần theo dõi
    tracking_weeks = models.IntegerField(default=4, verbose_name="Số tuần theo dõi")
    
    # Thống kê riêng cho weekly
    total_weekly_predictions = models.IntegerField(default=0)
    total_weekly_hits = models.IntegerField(default=0)  
    weekly_success_rate = models.FloatField(default=0.0)
    last_prediction_week = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Weekly Prediction Method"
        verbose_name_plural = "Weekly Prediction Methods"
        unique_together = ["base_method", "target_weekday"]
        indexes = [
            models.Index(fields=["target_weekday", "is_active"]),
            models.Index(fields=["weekly_success_rate"]),
        ]

    def __str__(self):
        weekday_name = dict(self._meta.get_field('target_weekday').choices)[self.target_weekday]
        return f"{self.base_method.name} - {weekday_name}"


class WeeklyTrackingSession(models.Model):
    """
    Session theo dõi weekly - TÁCH RIÊNG khỏi DailyTrackingSession
    """
    weekly_method = models.ForeignKey(
        WeeklyPredictionMethod,
        on_delete=models.CASCADE,
        related_name="tracking_sessions"
    )
    
    # Ngày dự đoán (thứ X)
    prediction_date = models.DateField(verbose_name="Ngày dự đoán", db_index=True)
    
    # Ngày tracking (thứ X tuần sau)
    tracking_date = models.DateField(verbose_name="Ngày tracking", db_index=True)
    
    # Dự đoán
    predicted_numbers = models.JSONField(verbose_name="Số dự đoán")
    total_predicted = models.IntegerField(default=0)
    
    # Kết quả
    actual_numbers = models.JSONField(default=list, verbose_name="Số thực tế")
    hit_numbers = models.JSONField(default=list, verbose_name="Số trúng")
    hit_count = models.IntegerField(default=0)
    hit_rate = models.FloatField(default=0.0)
    
    # Status
    STATUS_CHOICES = [
        ("pending", "Chờ kết quả"),
        ("completed", "Hoàn thành"),
        ("failed", "Thất bại"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Weekly Tracking Session"
        verbose_name_plural = "Weekly Tracking Sessions"
        unique_together = ["weekly_method", "prediction_date"]
        indexes = [
            models.Index(fields=["prediction_date"]),
            models.Index(fields=["tracking_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.weekly_method} - {self.prediction_date}"
    
    def calculate_results(self):
        """Tính toán kết quả trúng"""
        if not self.actual_numbers or not self.predicted_numbers:
            return
        
        predicted_set = set(self.predicted_numbers)
        actual_set = set(self.actual_numbers)
        hit_set = predicted_set.intersection(actual_set)
        
        self.hit_numbers = list(hit_set)
        self.hit_count = len(hit_set)
        self.total_predicted = len(predicted_set)
        self.hit_rate = (self.hit_count / self.total_predicted * 100) if self.total_predicted else 0
        self.status = "completed"
        self.save()


class WeeklyPerformanceStats(models.Model):
    """
    Thống kê hiệu suất weekly theo tháng
    """
    weekly_method = models.ForeignKey(
        WeeklyPredictionMethod,
        on_delete=models.CASCADE,
        related_name="monthly_stats"
    )
    
    year = models.IntegerField()
    month = models.IntegerField()
    
    # Thống kê tháng
    total_sessions = models.IntegerField(default=0)
    completed_sessions = models.IntegerField(default=0)
    total_predictions = models.IntegerField(default=0)
    total_hits = models.IntegerField(default=0)
    avg_hit_rate = models.FloatField(default=0.0)
    
    # Best/worst weeks
    best_week_date = models.DateField(null=True, blank=True)
    best_week_hit_rate = models.FloatField(default=0.0)
    worst_week_date = models.DateField(null=True, blank=True)
    worst_week_hit_rate = models.FloatField(default=0.0)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Weekly Performance Stats"
        verbose_name_plural = "Weekly Performance Stats"
        unique_together = ["weekly_method", "year", "month"]

    def update_stats(self):
        """Cập nhật thống kê từ sessions"""
        sessions = self.weekly_method.tracking_sessions.filter(
            prediction_date__year=self.year,
            prediction_date__month=self.month
        )
        
        completed = sessions.filter(status="completed")
        
        self.total_sessions = sessions.count()
        self.completed_sessions = completed.count()
        self.total_predictions = sum(s.total_predicted for s in completed)
        self.total_hits = sum(s.hit_count for s in completed)
        self.avg_hit_rate = (self.total_hits / self.total_predictions * 100) if self.total_predictions else 0
        
        # Best/worst weeks
        if completed.exists():
            best = completed.order_by("-hit_rate").first()
            worst = completed.order_by("hit_rate").first()
            
            self.best_week_date = best.prediction_date
            self.best_week_hit_rate = best.hit_rate
            self.worst_week_date = worst.prediction_date
            self.worst_week_hit_rate = worst.hit_rate
        
        self.save()
