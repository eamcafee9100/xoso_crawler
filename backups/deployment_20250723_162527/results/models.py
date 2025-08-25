import json

# Hoặc cấu hình logging
import logging
from collections import defaultdict
from datetime import date, datetime, timedelta

import numpy as np
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Cấu hình logging để ghi lại thông tin debug
from django.db.models import CharField, Count, F, Func, JSONField, Value
from django.db.models.functions import Concat, Substr
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .calculation_methods import CALCULATION_METHODS

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
    encoding="utf-8",
)


class KetQuaXoSoManager(models.Manager):
    def get_fatigued_numbers(self, days=30, threshold=2.0, limit=10):
        """
        Lấy danh sách các số xuất hiện quá nhiều (số mệt) dựa trên độ lệch chuẩn

        Args:
            days: Số ngày phân tích (mặc định 30 ngày)
            threshold: Ngưỡng độ lệch chuẩn (mặc định 2.0)
            limit: Giới hạn số lượng kết quả (mặc định 10)

        Returns:
            List[dict]: Danh sách các số mệt với thông tin:
                - number: Số xổ số
                - count: Số lần xuất hiện
                - deviation: Độ lệch so với trung bình
                - z_score: Điểm Z thống kê
        """
        from_date = timezone.now().date() - timedelta(days=days)

        # Lấy tất cả số 2D và tần suất xuất hiện
        number_counts = self._get_2d_number_counts(from_date)

        if not number_counts:
            return []

        # Tính toán thống kê
        counts = np.array([x["count"] for x in number_counts])
        mean = np.mean(counts)
        std = np.std(counts)

        # Lọc các số vượt ngưỡng
        fatigued_numbers = []
        for item in number_counts:
            z_score = (item["count"] - mean) / std if std > 0 else 0
            if z_score > threshold:
                fatigued_numbers.append(
                    {
                        "number": item["number"],
                        "count": item["count"],
                        "deviation": f"{(item['count']/mean*100 - 100):.1f}%",
                        "z_score": round(z_score, 2),
                    }
                )

        # Sắp xếp và giới hạn kết quả
        return sorted(fatigued_numbers, key=lambda x: x["z_score"], reverse=True)[
            :limit
        ]

    def _get_2d_number_counts(self, from_date):
        """
        Helper method để lấy tần suất các số 2D từ database

        Sử dụng Python processing thay vì Django ORM annotations phức tạp
        """
        from collections import defaultdict

        queryset = self.get_queryset().filter(ngay__gte=from_date)
        number_counts = defaultdict(int)

        # Xử lý từng record bằng Python thay vì database aggregation
        for record in queryset.iterator():
            try:
                # Lấy tất cả số 2D từ record này
                all_2d_numbers = record.get_all_2digit_numbers()

                # Đếm tần suất
                for number in all_2d_numbers:
                    number_counts[number] += 1

            except Exception as e:
                # Bỏ qua record lỗi
                continue

        # Chuyển đổi về format mong muốn
        result = [
            {"number": number, "count": count}
            for number, count in number_counts.items()
        ]

        # Sắp xếp theo count giảm dần
        return sorted(result, key=lambda x: x["count"], reverse=True)

    def get_frequency_analysis(self, days=30):
        """
        Phân tích tần suất xuất hiện của các số 2D
        """
        from_date = timezone.now().date() - timedelta(days=days)
        queryset = self.get_queryset().filter(ngay__gte=from_date)

        # Sử dụng method từ model
        frequency_counts = self.model.get_frequency_counts(queryset=queryset)

        # Format kết quả
        total_draws = queryset.count()
        result = []

        for number, count in frequency_counts.items():
            percentage = (count / total_draws * 100) if total_draws > 0 else 0
            result.append(
                {"number": number, "count": count, "percentage": round(percentage, 2)}
            )

        return sorted(result, key=lambda x: x["count"], reverse=True)


class KetQuaXoSo(models.Model):
    THU_CHOICES = [
        ("Thứ 2", "Thứ 2"),
        ("Thứ 3", "Thứ 3"),
        ("Thứ 4", "Thứ 4"),
        ("Thứ 5", "Thứ 5"),
        ("Thứ 6", "Thứ 6"),
        ("Thứ 7", "Thứ 7"),
        ("Chủ nhật", "Chủ nhật"),
    ]

    objects = KetQuaXoSoManager()

    thu = models.CharField(max_length=10, choices=THU_CHOICES, verbose_name="Thứ")
    ngay = models.DateField(unique=True, verbose_name="Ngày xổ số")
    giai_db = models.CharField(max_length=20, verbose_name="Giải đặc biệt")
    giai_1 = models.CharField(max_length=20, verbose_name="Giải nhất")
    giai_2 = models.CharField(max_length=100, verbose_name="Giải nhì")
    giai_3 = models.TextField(verbose_name="Giải ba")
    giai_4 = models.CharField(max_length=100, verbose_name="Giải tư")
    giai_5 = models.TextField(verbose_name="Giải năm")
    giai_6 = models.CharField(max_length=100, verbose_name="Giải sáu")
    giai_7 = models.CharField(max_length=100, verbose_name="Giải bảy")

    # Properties để tách các giải thành từng số riêng biệt
    @property
    def giai_2_1(self):
        numbers = self._split_prize(self.giai_2, expected_count=2)
        return numbers[0] if numbers else None

    @property
    def giai_2_2(self):
        numbers = self._split_prize(self.giai_2, expected_count=2)
        return numbers[1] if len(numbers) > 1 else None

    @property
    def giai_3_1(self):
        numbers = self._split_prize(self.giai_3, expected_count=6)
        return numbers[0] if numbers else None

    @property
    def giai_3_2(self):
        numbers = self._split_prize(self.giai_3, expected_count=6)
        return numbers[1] if len(numbers) > 1 else None

    @property
    def giai_3_3(self):
        numbers = self._split_prize(self.giai_3, expected_count=6)
        return numbers[2] if len(numbers) > 2 else None

    @property
    def giai_3_4(self):
        numbers = self._split_prize(self.giai_3, expected_count=6)
        return numbers[3] if len(numbers) > 3 else None

    @property
    def giai_3_5(self):
        numbers = self._split_prize(self.giai_3, expected_count=6)
        return numbers[4] if len(numbers) > 4 else None

    @property
    def giai_3_6(self):
        numbers = self._split_prize(self.giai_3, expected_count=6)
        return numbers[5] if len(numbers) > 5 else None

    @property
    def giai_4_1(self):
        numbers = self._split_prize(self.giai_4, expected_count=4)
        return numbers[0] if numbers else None

    @property
    def giai_4_2(self):
        numbers = self._split_prize(self.giai_4, expected_count=4)
        return numbers[1] if len(numbers) > 1 else None

    @property
    def giai_4_3(self):
        numbers = self._split_prize(self.giai_4, expected_count=4)
        return numbers[2] if len(numbers) > 2 else None

    @property
    def giai_4_4(self):
        numbers = self._split_prize(self.giai_4, expected_count=4)
        return numbers[3] if len(numbers) > 3 else None

    @property
    def giai_5_1(self):
        numbers = self._split_prize(self.giai_5, expected_count=6)
        return numbers[0] if numbers else None

    @property
    def giai_5_2(self):
        numbers = self._split_prize(self.giai_5, expected_count=6)
        return numbers[1] if len(numbers) > 1 else None

    @property
    def giai_5_3(self):
        numbers = self._split_prize(self.giai_5, expected_count=6)
        return numbers[2] if len(numbers) > 2 else None

    @property
    def giai_5_4(self):
        numbers = self._split_prize(self.giai_5, expected_count=6)
        return numbers[3] if len(numbers) > 3 else None

    @property
    def giai_5_5(self):
        numbers = self._split_prize(self.giai_5, expected_count=6)
        return numbers[4] if len(numbers) > 4 else None

    @property
    def giai_5_6(self):
        numbers = self._split_prize(self.giai_5, expected_count=6)
        return numbers[5] if len(numbers) > 5 else None

    @property
    def giai_6_1(self):
        numbers = self._split_prize(self.giai_6, expected_count=3)
        return numbers[0] if numbers else None

    @property
    def giai_6_2(self):
        numbers = self._split_prize(self.giai_6, expected_count=3)
        return numbers[1] if len(numbers) > 1 else None

    @property
    def giai_6_3(self):
        numbers = self._split_prize(self.giai_6, expected_count=3)
        return numbers[2] if len(numbers) > 2 else None

    @property
    def giai_7_1(self):
        numbers = self._split_prize(self.giai_7, expected_count=4)
        return numbers[0] if numbers else None

    @property
    def giai_7_2(self):
        numbers = self._split_prize(self.giai_7, expected_count=4)
        return numbers[1] if len(numbers) > 1 else None

    @property
    def giai_7_3(self):
        numbers = self._split_prize(self.giai_7, expected_count=4)
        return numbers[2] if len(numbers) > 2 else None

    @property
    def giai_7_4(self):
        numbers = self._split_prize(self.giai_7, expected_count=4)
        return numbers[3] if len(numbers) > 3 else None

    def _split_prize(self, field_value, expected_count=None):
        """
        Hàm hỗ trợ để tách các số từ một trường giải.
        Args:
            field_value: Giá trị của trường (chuỗi hoặc danh sách).
            expected_count: Số lượng số tối đa mong muốn (None nếu không giới hạn).
        Returns:
            List các số đã được chuẩn hóa.
        """
        numbers = []
        if not field_value:
            return numbers

        if isinstance(field_value, (int, float)):
            field_value = str(int(field_value))

        if isinstance(field_value, str):
            field_value = field_value.strip()
            if not field_value:
                return numbers

            separators = [",", " ", ";", "-", "\t", "|"]
            for sep in separators:
                if sep in field_value:
                    parts = field_value.split(sep)
                    break
            else:
                parts = [field_value]

            for part in parts:
                part = part.strip()
                if part and part.isdigit():
                    numbers.append(part)

        elif isinstance(field_value, (list, tuple)):
            for item in field_value:
                if item and str(item).isdigit():
                    numbers.append(str(item))

        # Giới hạn số lượng số nếu có expected_count
        if expected_count is not None:
            numbers = numbers[:expected_count]

        return numbers

    def get_all_2digit_numbers(self):
        """
        Lấy tất cả các số 2 chữ số từ tất cả các giải
        Trả về danh sách các chuỗi 2 chữ số đã được chuẩn hóa
        """
        numbers = []

        # Xử lý các giải
        prize_fields = [
            self.giai_db,
            self.giai_1,
            self.giai_2,
            self.giai_3,
            self.giai_4,
            self.giai_5,
            self.giai_6,
            self.giai_7,
        ]

        for giai in prize_fields:
            if giai:  # Check if field is not empty/None
                # Split by commas or spaces, handle multiple separators
                for num in giai.replace(",", " ").split():
                    if num.isdigit() and len(num) >= 2:
                        numbers.append(num[-2:].zfill(2))

        return set(numbers)  # Trả về tập hợp để loại bỏ trùng lặp

    def get_all_three_digit_numbers(self):
        """
        Lấy tất cả các số 3 chữ số từ tất cả các giải
        """
        numbers = []

        # Danh sách các trường giải cần xử lý
        prize_fields = [
            "giai_db",
            "giai_1",
            "giai_2",
            "giai_3",
            "giai_4",
            "giai_5",
            "giai_6",
            "giai_7",
        ]

        for field in prize_fields:
            value = getattr(self, field, None)

            if not value:
                continue

            # Xử lý từng số trong trường này
            for num_str in self._split_prize(value):
                if num_str.isdigit():
                    # Chuẩn hóa thành 3 chữ số
                    num = str(num_str).zfill(5)[-3:]  # Lấy 3 số cuối
                    if len(num) == 3:
                        numbers.append(num)

        # Loại bỏ trùng lặp nhưng giữ thứ tự
        seen = set()
        unique_numbers = [num for num in numbers if not (num in seen or seen.add(num))]

        return unique_numbers

    @classmethod
    def get_frequency_counts(cls, queryset=None, days=30, digit_type="2d"):
        """
        Tính tần suất xuất hiện của các số từ tất cả các giải
        """
        from collections import defaultdict

        if queryset is None:
            from_date = timezone.now().date() - timedelta(days=days)
            queryset = cls.objects.filter(ngay__gte=from_date)

        counts = defaultdict(int)

        for record in queryset.iterator():
            try:
                if digit_type == "2d":
                    numbers = record.get_all_2digit_numbers()
                else:
                    numbers = record.get_all_three_digit_numbers()

                for num in numbers:
                    counts[num] += 1

            except Exception:
                continue

        return dict(counts)

    def get_head_tail_stats(self, days=30):
        """Thống kê đầu đuôi"""
        from collections import defaultdict

        from_date = timezone.now().date() - timedelta(days=days)
        results = KetQuaXoSo.objects.filter(ngay__gte=from_date)

        head_counts = defaultdict(int)
        tail_counts = defaultdict(int)

        for result in results:
            for num in result.get_all_2digit_numbers():
                head = num[0]  # Đầu số
                tail = num[-1]  # Đuôi số
                head_counts[head] += 1
                tail_counts[tail] += 1

        return {
            "heads": sorted(head_counts.items(), key=lambda x: x[1], reverse=True),
            "tails": sorted(tail_counts.items(), key=lambda x: x[1], reverse=True),
        }

    def get_sum_stats(self, days=30):
        """Thống kê theo tổng"""
        from collections import defaultdict

        from_date = timezone.now().date() - timedelta(days=days)
        results = KetQuaXoSo.objects.filter(ngay__gte=from_date)

        sum_counts = defaultdict(int)

        for result in results:
            for num in result.get_all_2digit_numbers():
                digit_sum = sum(int(d) for d in num)
                sum_counts[digit_sum] += 1

        return sorted(sum_counts.items(), key=lambda x: x[1], reverse=True)

    def get_touch_stats(self, days=30):
        """Thống kê chạm (số lần xuất hiện của mỗi chữ số)"""
        from collections import defaultdict

        from_date = timezone.now().date() - timedelta(days=days)
        results = KetQuaXoSo.objects.filter(ngay__gte=from_date)

        digit_counts = defaultdict(int)

        for result in results:
            for num in result.get_all_2digit_numbers():
                for d in num:
                    digit_counts[int(d)] += 1

        return sorted(digit_counts.items(), key=lambda x: x[1], reverse=True)

    def get_number_appearance_history(self, number, digit_type="2d"):
        """Lịch sử xuất hiện của một số cụ thể"""
        history = []
        results = KetQuaXoSo.objects.filter(ngay__lte=self.ngay).order_by("-ngay")

        for result in results:
            numbers = (
                result.get_all_2digit_numbers()
                if digit_type == "2d"
                else result.get_all_three_digit_numbers()
            )
            if number in numbers:
                history.append(result.ngay)

        return history

    def get_number_cycles(self, number, digit_type="2d"):
        """Phân tích chu kỳ xuất hiện của một số cụ thể"""
        results = KetQuaXoSo.objects.filter(ngay__lte=self.ngay).order_by("-ngay")
        appearances = []
        last_appearance = None

        for result in results:
            numbers = (
                result.get_all_2digit_numbers()
                if digit_type == "2d"
                else result.get_all_three_digit_numbers()
            )
            if number in numbers:
                if last_appearance:
                    cycle = (last_appearance - result.ngay).days
                    appearances.append({"date": result.ngay, "cycle": cycle})
                last_appearance = result.ngay

        # Tính toán thống kê chu kỳ
        cycles = [appearance["cycle"] for appearance in appearances]
        avg_cycle = sum(cycles) / len(cycles) if cycles else 0
        min_cycle = min(cycles) if cycles else 0
        max_cycle = max(cycles) if cycles else 0

        return {
            "number": number,
            "total_appearances": len(appearances),
            "last_appearance": (
                (self.ngay - last_appearance).days if last_appearance else None
            ),
            "avg_cycle": avg_cycle,
            "min_cycle": min_cycle,
            "max_cycle": max_cycle,
            "appearances": appearances[:10],  # 10 lần xuất hiện gần nhất
        }

    class Meta:
        verbose_name = "Kết quả xổ số miền Bắc"
        verbose_name_plural = "Các kết quả xổ số miền Bắc"
        ordering = ["-ngay"]

    def __str__(self):
        return f"{self.thu} - {self.ngay.strftime('%d/%m/%Y')}"

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import json

class ModelTrainingHistory(models.Model):
    """
    Lịch sử training models với đầy đủ metadata
    """
    MODEL_TYPES = [
        ('enhanced_cycle', 'Enhanced Cycle Predictor'),
        ('advanced_lottery', 'Advanced Lottery Predictor'),
        ('ensemble', 'Ensemble Model'),
        ('random_forest', 'Random Forest'),
        ('neural_network', 'Neural Network'),
    ]
    
    TRAINING_STATUS = [
        ('pending', 'Pending'),
        ('training', 'Training'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('deprecated', 'Deprecated'),
    ]
    
    # Basic info
    model_id = models.CharField(max_length=100, unique=True, db_index=True)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    version = models.CharField(max_length=20)
    
    # Training metadata
    training_date = models.DateTimeField(default=timezone.now)
    training_duration = models.FloatField(null=True, blank=True, help_text="Training time in seconds")
    data_size = models.IntegerField(help_text="Number of training records")
    feature_count = models.IntegerField(default=0)
    
    # Training parameters
    training_params = models.JSONField(default=dict, help_text="Training hyperparameters")
    feature_list = models.JSONField(default=list, help_text="List of features used")
    
    # Performance metrics
    training_accuracy = models.FloatField(null=True, blank=True)
    validation_accuracy = models.FloatField(null=True, blank=True)
    cross_val_score = models.FloatField(null=True, blank=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=TRAINING_STATUS, default='pending')
    error_message = models.TextField(blank=True)
    model_file_path = models.CharField(max_length=255, blank=True)
    
    # Performance tracking
    total_predictions = models.IntegerField(default=0)
    successful_predictions = models.IntegerField(default=0)
    current_accuracy = models.FloatField(default=0.0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'model_training_history'
        ordering = ['-training_date']
        indexes = [
            models.Index(fields=['model_type', 'training_date']),
            models.Index(fields=['status', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.model_type} v{self.version} - {self.training_date.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def success_rate(self):
        """Calculate success rate"""
        if self.total_predictions == 0:
            return 0.0
        return (self.successful_predictions / self.total_predictions) * 100
    
    def update_performance(self, is_successful: bool):
        """Update performance metrics"""
        self.total_predictions += 1
        if is_successful:
            self.successful_predictions += 1
        self.current_accuracy = self.success_rate
        self.save(update_fields=['total_predictions', 'successful_predictions', 'current_accuracy'])
    
    def get_training_summary(self):
        """Get training summary as dict"""
        return {
            'model_id': self.model_id,
            'type': self.model_type,
            'version': self.version,
            'training_date': self.training_date.isoformat(),
            'duration': self.training_duration,
            'data_size': self.data_size,
            'accuracy': self.training_accuracy,
            'validation_accuracy': self.validation_accuracy,
            'success_rate': self.success_rate,
            'status': self.status
        }

class PredictionPerformanceMetrics(models.Model):
    """
    Chi tiết metrics hiệu suất dự đoán theo từng ngày
    """
    # Foreign keys
    model_training = models.ForeignKey(ModelTrainingHistory, on_delete=models.CASCADE, 
                                     related_name='performance_metrics')
    
    # Date and prediction info
    prediction_date = models.DateField(db_index=True)
    analysis_date = models.DateField()
    prediction_count = models.IntegerField(default=0)
    
    # Performance metrics
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    
    # Hit analysis
    total_hits = models.IntegerField(default=0)
    total_misses = models.IntegerField(default=0)
    hit_rate = models.FloatField(default=0.0)
    
    # Confidence analysis
    avg_confidence = models.FloatField(default=0.0)
    top_prediction_confidence = models.FloatField(default=0.0)
    confidence_distribution = models.JSONField(default=dict)
    
    # Detailed results
    predicted_numbers = models.JSONField(default=list)
    actual_numbers = models.JSONField(default=list)
    hit_numbers = models.JSONField(default=list)
    miss_numbers = models.JSONField(default=list)
    
    # Processing metadata
    processing_time = models.FloatField(default=0.0)
    data_quality_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prediction_performance_metrics'
        unique_together = ['model_training', 'prediction_date']
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['prediction_date', 'accuracy']),
            models.Index(fields=['model_training', 'prediction_date']),
        ]
    
    def __str__(self):
        return f"{self.model_training.model_type} - {self.prediction_date} (Acc: {self.accuracy:.2%})"
    
    def calculate_all_metrics(self, predictions: dict, actual_numbers: list):
        """Calculate all performance metrics"""
        predicted_nums = list(predictions.keys())
        actual_nums = actual_numbers
        
        # Basic counts
        hit_nums = list(set(predicted_nums) & set(actual_nums))
        miss_nums = list(set(predicted_nums) - set(actual_nums))
        
        self.predicted_numbers = predicted_nums
        self.actual_numbers = actual_nums
        self.hit_numbers = hit_nums
        self.miss_numbers = miss_nums
        
        self.total_hits = len(hit_nums)
        self.total_misses = len(miss_nums)
        self.prediction_count = len(predicted_nums)
        
        # Calculate metrics
        if self.prediction_count > 0:
            self.precision = self.total_hits / self.prediction_count
            self.hit_rate = self.precision
        
        if len(actual_nums) > 0:
            self.recall = self.total_hits / len(actual_nums)
            self.accuracy = self.total_hits / len(actual_nums)
        
        if self.precision + self.recall > 0:
            self.f1_score = 2 * (self.precision * self.recall) / (self.precision + self.recall)
        
        # Confidence analysis
        confidences = list(predictions.values())
        if confidences:
            self.avg_confidence = sum(confidences) / len(confidences)
            self.top_prediction_confidence = max(confidences)
            
            # Confidence distribution
            self.confidence_distribution = {
                'high': len([c for c in confidences if c >= 0.8]),
                'medium': len([c for c in confidences if 0.6 <= c < 0.8]),
                'low': len([c for c in confidences if 0.4 <= c < 0.6]),
                'very_low': len([c for c in confidences if c < 0.4])
            }

class PredictionRecord(models.Model):
    """
    Lưu trữ từng lần dự đoán chi tiết
    """
    PREDICTION_TYPES = [
        ('ml', 'Machine Learning'),
        ('traditional', 'Traditional Methods'),
        ('ensemble', 'Ensemble'),
        ('manual', 'Manual Prediction'),
    ]
    
    # Foreign keys and basic info
    model_training = models.ForeignKey(ModelTrainingHistory, on_delete=models.CASCADE,
                                     related_name='prediction_records')
    performance_metric = models.ForeignKey(PredictionPerformanceMetrics, on_delete=models.CASCADE,
                                         related_name='prediction_records')
    
    # Prediction details
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    prediction_date = models.DateField(db_index=True)
    analysis_date = models.DateField()
    
    # Prediction data
    predicted_number = models.CharField(max_length=2)
    confidence_score = models.FloatField()
    rank_position = models.IntegerField()
    
    # Result tracking
    is_hit = models.BooleanField(default=False)
    actual_result_available = models.BooleanField(default=False)
    
    # Metadata
    feature_importance = models.JSONField(default=dict)
    prediction_reasoning = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prediction_records'
        unique_together = ['performance_metric', 'predicted_number']
        ordering = ['-prediction_date', 'rank_position']
        indexes = [
            models.Index(fields=['prediction_date', 'is_hit']),
            models.Index(fields=['predicted_number', 'prediction_date']),
        ]
    
    def __str__(self):
        hit_status = "✓" if self.is_hit else "✗"
        return f"{hit_status} {self.predicted_number} ({self.confidence_score:.2%}) - {self.prediction_date}"

# Cải thiện model CycleAccuracy hiện có
class CycleAccuracy(models.Model):
    """
    Enhanced accuracy tracking with more detailed metrics
    """
    date = models.DateField(unique=True, db_index=True)
    
    # Enhanced metrics
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)
    accuracy = models.FloatField(default=0.0)
    
    # Prediction counts
    total_predictions = models.IntegerField(default=0)
    correct_predictions = models.IntegerField(default=0)
    
    # Enhanced tracking
    features_used = models.JSONField(default=list)
    model_version = models.CharField(max_length=20, default='1.0')
    data_quality_score = models.FloatField(default=0.0)
    processing_time = models.FloatField(default=0.0)
    
    # Additional analysis
    number_distribution = models.JSONField(default=dict)
    confidence_stats = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cycle_accuracy'
        ordering = ['-date']
    
    def __str__(self):
        return f"Accuracy {self.date}: {self.accuracy:.2%} (F1: {self.f1_score:.2%})"
    
class Prediction(models.Model):
    date = models.DateField()
    method = models.CharField(max_length=100)
    predicted_numbers = models.JSONField()
    shap_values = models.JSONField(null=True)
    actual_result = models.ForeignKey(KetQuaXoSo, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class CalculationMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    formula = models.JSONField(default=dict)  # Lưu logic tính dạng structured data
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class ExtractedResult(models.Model):
    image = models.ImageField(upload_to="lottery_images/")
    extracted_json = models.JSONField()  # Lưu kết quả OCR
    analysis_results = models.JSONField()  # Kết quả phân tích
    processing_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["processing_date"]),
        ]


class AppliedCalculation(models.Model):
    image = models.ForeignKey("ExtractedResult", on_delete=models.CASCADE)
    method = models.ForeignKey(CalculationMethod, on_delete=models.CASCADE)
    input_params = models.JSONField()  # Tham số đầu vào cụ thể
    output_numbers = models.JSONField()  # Kết quả áp dụng
    execution_time = models.FloatField()  # Thời gian xử lý (ms)


class HistoricalAnalysis(models.Model):
    target_date = models.DateField()
    compared_dates = models.JSONField()  # Danh sách ngày đã so sánh
    pattern_matches = models.JSONField()  # Các mẫu số trùng khớp
    prediction_score = models.FloatField()


class MethodPerformance(models.Model):
    method_name = models.CharField(max_length=50, unique=True)
    total_predictions = models.IntegerField(default=0)
    successful_predictions = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def success_rate(self):
        if self.total_predictions == 0:
            return 0
        return (
            (self.successful_predictions / self.total_predictions * 100)
            if self.total_predictions > 0
            else 0
        )



from .calculation.calc_config import CALCULATION_CONFIGS


class LoKhung2Ngay(models.Model):

    analysis_date = models.DateField(verbose_name="Ngày phân tích")
    next_day_1 = models.DateField(verbose_name="Ngày kế tiếp 1")
    next_day_2 = models.DateField(verbose_name="Ngày kế tiếp 2")

    # Giải gốc
    giai35 = models.CharField(max_length=10, verbose_name="Giải 3.5")
    giai56 = models.CharField(max_length=10, verbose_name="Giải 5.6")

    # Số tính toán
    so_thu_nhat = models.IntegerField(verbose_name="Số thứ nhất")
    so_thu_hai = models.IntegerField(verbose_name="Số thứ hai")

    # Kết quả dự đoán
    cap_lo = models.CharField(
        max_length=10, verbose_name="Cặp lô dự đoán"
    )  # VD: "47-74"

    # Kết quả thực tế
    ket_qua_ngay_1 = models.JSONField(verbose_name="KQ ngày sau 1", default=list)
    ket_qua_ngay_2 = models.JSONField(verbose_name="KQ ngày sau 2", default=list)
    so_trung = models.JSONField(verbose_name="Số trúng", default=list)
    trung = models.BooleanField(default=False, verbose_name="Có trúng")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lô khung 2 ngày"
        verbose_name_plural = "Các lô khung 2 ngày"
        ordering = ["-analysis_date"]
        indexes = [
            models.Index(fields=["analysis_date"]),
            models.Index(fields=["next_day_1"]),
            models.Index(fields=["next_day_2"]),
        ]

    def __str__(self):
        return f"Lô khung {self.cap_lo} ngày {self.analysis_date.strftime('%d/%m/%Y')}"

    @classmethod
    def calculate_number(cls, number_str, method):
        """
        Tính số theo phương pháp:
        - sum_first_last: số đầu + số cuối
        - sum_first_two: tổng 2 số đầu
        - last_two_digits: lấy 2 số cuối
        """
        if not number_str or not number_str.isdigit():
            return None
        if method == "lokhung_2_ngay":
            if method == "giai35":
                if len(number_str) >= 2:
                    return (int(number_str[0]) + int(number_str[-1])) % 10
            elif method == "giai56":
                if len(number_str) >= 2:
                    return (int(number_str[0]) + int(number_str[1])) % 10
            return None
        elif method == "sum_first_two":
            if len(number_str) >= 2:
                return (int(number_str[0]) + int(number_str[1])) % 10
        elif method == "last_two_digits":
            if len(number_str) >= 2:
                return int(number_str[-2:])
        return None

    @classmethod
    def generate_cap_lo(cls, numbers):
        """Tạo cặp lô từ danh sách số"""
        if len(numbers) < 2:
            return []
        so1, so2 = numbers[0], numbers[1]
        if so1 == so2:
            return [f"{so1}{so2}"]
        return [f"{so1}{so2}", f"{so2}{so1}"]

    @classmethod
    def create_for_date(cls, date, configs=CALCULATION_CONFIGS):
        """Tạo bản ghi phân tích cho một ngày với các cấu hình phép tính"""
        try:
            from .models import KetQuaXoSo  # Import ở đây để tránh circular import

            prize = KetQuaXoSo.objects.filter(ngay=date).first()
            if not prize:
                logger.warning(f"No prize data found for date {date}")
                return None

            # Tính toán next_day_1 và next_day_2
            next_day_1 = date + timedelta(days=1)
            next_day_2 = date + timedelta(days=2)

            # Lấy kết quả của 2 ngày tiếp theo
            next_prize_1 = KetQuaXoSo.objects.filter(ngay=next_day_1).first()
            next_prize_2 = KetQuaXoSo.objects.filter(ngay=next_day_2).first()

            # Tạo cấu hình phép tính
            calculation_config = {}
            numbers = []
            for config in configs:
                source = config["source"]
                method = config["method"]
                number_str = getattr(prize, source, None)
                if number_str:
                    calculated_number = cls.calculate_number(number_str, method)
                    if calculated_number is not None:
                        calculation_config[config["name"]] = {
                            "source": source,
                            "value": number_str,
                            "method": method,
                            "result": calculated_number,
                        }
                        numbers.append(calculated_number)

            # Tạo cặp lô dự đoán
            predicted_pairs = cls.generate_cap_lo(numbers)
            print("predicted_pairs :" + predicted_pairs)

            # Lấy kết quả thực tế
            def extract_prize_numbers(prize_obj):
                if not prize_obj:
                    return []
                numbers = []
                prize_fields = [
                    "giai_db",
                    "giai_1",
                    "giai_2",
                    "giai_3",
                    "giai_4",
                    "giai_5",
                    "giai_6",
                    "giai_7",
                ]
                for field in prize_fields:
                    if hasattr(prize_obj, field) and getattr(prize_obj, field):
                        value = getattr(prize_obj, field)
                        numbers.extend([num[-2:] for num in value.split()])
                return list(set(numbers))

            ket_qua_1 = extract_prize_numbers(next_prize_1)
            ket_qua_2 = extract_prize_numbers(next_prize_2)

            # Kiểm tra số trúng
            so_trung = []
            for pair in predicted_pairs:
                if any(pair in result for result in ket_qua_1):
                    so_trung.append(
                        {"so": pair, "ngay": next_day_1.strftime("%Y-%m-%d")}
                    )
                if any(pair in result for result in ket_qua_2):
                    so_trung.append(
                        {"so": pair, "ngay": next_day_2.strftime("%Y-%m-%d")}
                    )

            # Tạo hoặc cập nhật bản ghi
            lo_khung, created = cls.objects.update_or_create(
                analysis_date=date,
                defaults={
                    "next_day_1": next_day_1,
                    "next_day_2": next_day_2,
                    "calculation_config": calculation_config,
                    "predicted_pairs": predicted_pairs,
                    "ket_qua_ngay_1": ket_qua_1,
                    "ket_qua_ngay_2": ket_qua_2,
                    "so_trung": so_trung,
                    "trung": len(so_trung) > 0,
                },
            )

            logger.info(f"Created/Updated analysis for {date}: {predicted_pairs}")
            return lo_khung

        except Exception as e:
            logger.error(f"Error creating analysis for date {date}: {str(e)}")
            return None

    @classmethod
    def update_latest_lokhung_data(cls, configs=CALCULATION_CONFIGS):
        """Tự động cập nhật dữ liệu lô khung cho các ngày chưa có"""
        try:
            from .models import KetQuaXoSo

            analyzed_dates = set(
                cls.objects.all().values_list("analysis_date", flat=True)
            )
            xoso_dates = (
                KetQuaXoSo.objects.all()
                .order_by("-ngay")
                .values_list("ngay", flat=True)
            )

            count = 0
            for date_obj in xoso_dates:
                if date_obj in analyzed_dates:
                    continue
                if cls.create_for_date(date_obj, configs):
                    count += 1
                    analyzed_dates.add(date_obj)

            return count
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật dữ liệu lô khung: {str(e)}", exc_info=True)
            return 0


class CachTinhDanDe(models.Model):
    TEN_CHOICES = [
        ("36", "Phương pháp 36"),
        ("tu_thu_de", "Tứ thủ đề"),
        ("3_cang", "3 càng"),
        ("giai_db", "Dựa trên giải đặc biệt"),
        ("_105_de_4_so", "Dựa trên giải 3.1, 4.1 và 6.3,3.6"),
        (
            "pascal",
            "Soi cầu Pascal: Dùng tam giác Pascal từ giải đặc biệt và giải nhất",
        ),
    ]
    TEN_CHOICES_DICT = dict(TEN_CHOICES)  # Add this for easy lookup
    ten = models.CharField(max_length=50, choices=TEN_CHOICES)

    @classmethod
    def validate_calculation_methods(cls):
        valid_methods = {key for key, _ in cls.TEN_CHOICES}
        for method in CALCULATION_METHODS:
            if method not in valid_methods:
                raise ValueError(f"Phương pháp {method} không có trong TEN_CHOICES")

    dan_de = models.ForeignKey(
        "DanDeDacBiet", on_delete=models.CASCADE, related_name="cach_tinh"
    )
    ten = models.CharField(
        max_length=50, choices=TEN_CHOICES, verbose_name="Tên cách tính"
    )
    mo_ta = models.TextField(verbose_name="Mô tả cách tính", blank=True)
    bo_so = models.JSONField(verbose_name="Bộ số", default=list)
    so_trung = models.JSONField(verbose_name="Số trúng", default=list)
    so_luong_trung = models.IntegerField(default=0, verbose_name="Số lượng trúng")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cách tính dàn đề"
        verbose_name_plural = "Các cách tính dàn đề"

    def __str__(self):
        date_str = (
            self.dan_de.analysis_date.strftime("%d/%m/%Y")
            if self.dan_de and self.dan_de.analysis_date
            else "N/A"
        )
        return f"{self.get_ten_display()} - {date_str}"


class PredictionMethod(models.Model):
    """
    Model lưu trữ thông tin về các phương pháp dự đoán
    """

    code = models.CharField(max_length=50, verbose_name="Mã phương pháp")
    name = models.CharField(max_length=200, verbose_name="Tên phương pháp")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phương pháp dự đoán"
        verbose_name_plural = "Các phương pháp dự đoán"

    def __str__(self):
        return self.name


class DanDeDacBiet(models.Model):
    """
    Model chính lưu trữ dữ liệu phân tích từ kết quả xổ số cho một ngày cụ thể
    """

    analysis_date = models.DateField(verbose_name="Ngày phân tích")
    next_day_date = models.DateField(verbose_name="Ngày kế tiếp")
    special_prize_next_day = models.CharField(
        max_length=5, verbose_name="Giải ĐB ngày sau", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dàn đề đặc biệt"
        verbose_name_plural = "Các dàn đề đặc biệt"
        ordering = ["-analysis_date"]
        indexes = [
            models.Index(fields=["analysis_date"]),
            models.Index(fields=["next_day_date"]),
        ]

    def __str__(self):
        return f"Dàn đề ngày {self.analysis_date.strftime('%d/%m/%Y') if self.analysis_date else 'N/A'}"

    @classmethod
    def create_for_date(cls, analysis_date):
        """Tạo bản ghi cho một ngày cụ thể và tính toán kết quả từ tất cả các phương pháp"""
        try:
            from results.methods import get_all_methods
            from results.models import PredictionResult

            # Lấy dữ liệu kết quả xổ số cho ngày phân tích
            result = KetQuaXoSo.objects.get(ngay=analysis_date)
            next_day_date = analysis_date + timedelta(days=1)
            next_day_result = KetQuaXoSo.objects.filter(ngay=next_day_date).first()

            # Xóa kết quả dự đoán cũ (nếu có)
            existing_dan_de = cls.objects.filter(analysis_date=analysis_date).first()

            # Tạo bản ghi DanDeDacBiet
            dan_de, created = cls.objects.update_or_create(
                analysis_date=analysis_date,
                defaults={
                    "next_day_date": next_day_date,
                    "special_prize_next_day": (
                        next_day_result.giai_db if next_day_result else ""
                    ),
                },
            )

            # Chuẩn bị dữ liệu đầu vào cho các phương pháp
            input_data = {
                "giai_db": result.giai_db or "",
                "giai_1": result.giai_1 or "",
                "giai_2_1": result.giai_2_1 or "",
                "giai_2_2": result.giai_2_2 or "",
                "giai_3_1": result.giai_3_1 or "",
                "giai_3_2": result.giai_3_2 or "",
                "giai_3_3": result.giai_3_3 or "",
                "giai_3_4": result.giai_3_4 or "",
                "giai_3_5": result.giai_3_5 or "",
                "giai_3_6": result.giai_3_6 or "",
                "giai_4_1": result.giai_4_1 or "",
                "giai_4_2": result.giai_4_2 or "",
                "giai_4_3": result.giai_4_3 or "",
                "giai_4_4": result.giai_4_4 or "",
                "giai_5_1": result.giai_5_1 or "",
                "giai_5_2": result.giai_5_2 or "",
                "giai_5_3": result.giai_5_3 or "",
                "giai_5_4": result.giai_5_4 or "",
                "giai_5_5": result.giai_5_5 or "",
                "giai_5_6": result.giai_5_6 or "",
                "giai_6_1": result.giai_6_1 or "",
                "giai_6_2": result.giai_6_2 or "",
                "giai_6_3": result.giai_6_3 or "",
                "giai_7_1": result.giai_7_1 or "",
                "giai_7_2": result.giai_7_2 or "",
                "giai_7_3": result.giai_7_3 or "",
                "giai_7_4": result.giai_7_4 or "",
            }

            # Chạy tất cả các phương pháp dự đoán và lưu kết quả
            methods = get_all_methods()
            for method in methods:
                method.create_prediction(dan_de, input_data, next_day_result)

            return dan_de

        except KetQuaXoSo.DoesNotExist:
            logger.error(f"Không tìm thấy kết quả xổ số cho ngày {analysis_date}")
            return None
        except Exception as e:
            logger.error(
                f"Lỗi khi tạo dàn đề cho ngày {analysis_date}: {str(e)}", exc_info=True
            )
            return None

    @classmethod
    def create_for_date_allprize(cls, analysis_date):
        """Tạo bản ghi cho một ngày cụ thể và tính toán kết quả từ tất cả các phương pháp"""
        try:
            from results.methods_de_all_prize import get_all_methods
            from results.models import PredictionResult

            # Lấy dữ liệu kết quả xổ số cho ngày phân tích
            result = KetQuaXoSo.objects.get(ngay=analysis_date)
            next_day_date = analysis_date + timedelta(days=1)
            next_day_result = KetQuaXoSo.objects.filter(ngay=next_day_date).first()

            # Xóa kết quả dự đoán cũ (nếu có)
            existing_dan_de = cls.objects.filter(analysis_date=analysis_date).first()

            # Tạo bản ghi DanDeDacBiet
            dan_de, created = cls.objects.update_or_create(
                analysis_date=analysis_date,
                defaults={
                    "next_day_date": next_day_date,
                    "special_prize_next_day": (
                        next_day_result.giai_db if next_day_result else ""
                    ),
                },
            )

            # Chuẩn bị dữ liệu đầu vào cho các phương pháp
            input_data = {
                "giai_db": result.giai_db or "",
                "giai_1": result.giai_1 or "",
                "giai_2_1": result.giai_2_1 or "",
                "giai_2_2": result.giai_2_2 or "",
                "giai_3_1": result.giai_3_1 or "",
                "giai_3_2": result.giai_3_2 or "",
                "giai_3_3": result.giai_3_3 or "",
                "giai_3_4": result.giai_3_4 or "",
                "giai_3_5": result.giai_3_5 or "",
                "giai_3_6": result.giai_3_6 or "",
                "giai_4_1": result.giai_4_1 or "",
                "giai_4_2": result.giai_4_2 or "",
                "giai_4_3": result.giai_4_3 or "",
                "giai_4_4": result.giai_4_4 or "",
                "giai_5_1": result.giai_5_1 or "",
                "giai_5_2": result.giai_5_2 or "",
                "giai_5_3": result.giai_5_3 or "",
                "giai_5_4": result.giai_5_4 or "",
                "giai_5_5": result.giai_5_5 or "",
                "giai_5_6": result.giai_5_6 or "",
                "giai_6_1": result.giai_6_1 or "",
                "giai_6_2": result.giai_6_2 or "",
                "giai_6_3": result.giai_6_3 or "",
                "giai_7_1": result.giai_7_1 or "",
                "giai_7_2": result.giai_7_2 or "",
                "giai_7_3": result.giai_7_3 or "",
                "giai_7_4": result.giai_7_4 or "",
            }

            # Chạy tất cả các phương pháp dự đoán và lưu kết quả
            methods = get_all_methods()
            for method in methods:
                method.create_prediction(dan_de, input_data, next_day_result)

            return dan_de

        except KetQuaXoSo.DoesNotExist:
            logger.error(f"Không tìm thấy kết quả xổ số cho ngày {analysis_date}")
            return None
        except Exception as e:
            logger.error(
                f"Lỗi khi tạo dàn đề cho ngày {analysis_date}: {str(e)}", exc_info=True
            )
            return None


class EnhancedPrediction(models.Model):
    date = models.DateField()
    numbers = models.TextField(blank=True, null=True)
    method = models.ForeignKey(PredictionMethod, on_delete=models.CASCADE, null=True)
    confidence_scores = models.JSONField(default=dict)  # {'09': 0.85, '23': 0.72}
    created_at = models.DateTimeField(auto_now_add=True)
    accuracy = models.FloatField(
        null=True, blank=True
    )  # Độ chính xác của dự đoán, có thể tính sau khi có kết quả thực tế

    class Meta:
        indexes = [
            models.Index(fields=["date", "method"]),
        ]


class PredictionResult(models.Model):
    """
    Model lưu trữ kết quả dự đoán từ một phương pháp cụ thể
    """

    dan_de = models.ForeignKey(
        DanDeDacBiet, on_delete=models.CASCADE, related_name="predictions"
    )
    method = models.ForeignKey(
        PredictionMethod, on_delete=models.CASCADE, related_name="results"
    )
    predicted_numbers = models.JSONField(verbose_name="Các số dự đoán", default=list)
    winning_numbers = models.JSONField(verbose_name="Các số trúng", default=list)
    hit_count = models.IntegerField(default=0, verbose_name="Số lượng trúng")
    is_special_prize = models.BooleanField(default=False, verbose_name="Là đặc biệt")
    digit_count = models.IntegerField(default=2, verbose_name="Số chữ số")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kết quả dự đoán"
        verbose_name_plural = "Các kết quả dự đoán"
        indexes = [
            models.Index(fields=["dan_de", "method"]),
            models.Index(fields=["hit_count"]),
        ]

    def __str__(self):
        return f"{self.method.name} - {self.dan_de.analysis_date.strftime('%d/%m/%Y')}"


class DanDeDacBietAllPrize(models.Model):
    """
    Model chính lưu trữ dữ liệu phân tích từ kết quả xổ số cho một ngày cụ thể
    """

    analysis_date = models.DateField(verbose_name="Ngày phân tích")
    next_day_date = models.DateField(verbose_name="Ngày kế tiếp")
    special_prize_next_day = models.CharField(
        max_length=5, verbose_name="Giải ĐB ngày sau", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dàn đề đặc biệt All Prize"
        verbose_name_plural = "Các dàn đề đặc biệt All Prize"
        ordering = ["-analysis_date"]
        indexes = [
            models.Index(fields=["analysis_date"]),
            models.Index(fields=["next_day_date"]),
        ]

    def __str__(self):
        return f"Dàn đề ngày {self.analysis_date.strftime('%d/%m/%Y') if self.analysis_date else 'N/A'}"

    @classmethod
    def create_for_date_allprize(cls, analysis_date):
        """Tạo bản ghi cho một ngày cụ thể và tính toán kết quả từ tất cả các phương pháp"""
        try:
            from results.methods_de_all_prize import get_all_methods
            from results.models import PredictionDeAllPrizeResult

            # Lấy dữ liệu kết quả xổ số cho ngày phân tích
            result = KetQuaXoSo.objects.get(ngay=analysis_date)
            next_day_date = analysis_date + timedelta(days=1)
            next_day_result = KetQuaXoSo.objects.filter(ngay=next_day_date).first()

            # Xóa kết quả dự đoán cũ (nếu có)
            existing_dan_de = cls.objects.filter(analysis_date=analysis_date).first()

            # Tạo bản ghi DanDeDacBiet
            dan_de, created = cls.objects.update_or_create(
                analysis_date=analysis_date,
                defaults={
                    "next_day_date": next_day_date,
                    "special_prize_next_day": (
                        next_day_result.giai_db if next_day_result else ""
                    ),
                },
            )

            # Chuẩn bị dữ liệu đầu vào cho các phương pháp
            input_data = {
                "giai_db": result.giai_db or "",
                "giai_1": result.giai_1 or "",
                "giai_2_1": result.giai_2_1 or "",
                "giai_2_2": result.giai_2_2 or "",
                "giai_3_1": result.giai_3_1 or "",
                "giai_3_2": result.giai_3_2 or "",
                "giai_3_3": result.giai_3_3 or "",
                "giai_3_4": result.giai_3_4 or "",
                "giai_3_5": result.giai_3_5 or "",
                "giai_3_6": result.giai_3_6 or "",
                "giai_4_1": result.giai_4_1 or "",
                "giai_4_2": result.giai_4_2 or "",
                "giai_4_3": result.giai_4_3 or "",
                "giai_4_4": result.giai_4_4 or "",
                "giai_5_1": result.giai_5_1 or "",
                "giai_5_2": result.giai_5_2 or "",
                "giai_5_3": result.giai_5_3 or "",
                "giai_5_4": result.giai_5_4 or "",
                "giai_5_5": result.giai_5_5 or "",
                "giai_5_6": result.giai_5_6 or "",
                "giai_6_1": result.giai_6_1 or "",
                "giai_6_2": result.giai_6_2 or "",
                "giai_6_3": result.giai_6_3 or "",
                "giai_7_1": result.giai_7_1 or "",
                "giai_7_2": result.giai_7_2 or "",
                "giai_7_3": result.giai_7_3 or "",
                "giai_7_4": result.giai_7_4 or "",
            }

            # Chạy tất cả các phương pháp dự đoán và lưu kết quả
            methods = get_all_methods()
            for method in methods:
                method.create_prediction(dan_de, input_data, next_day_result)

            return dan_de

        except KetQuaXoSo.DoesNotExist:
            logger.error(f"Không tìm thấy kết quả xổ số cho ngày {analysis_date}")
            return None
        except Exception as e:
            logger.error(
                f"Lỗi khi tạo dàn đề cho ngày {analysis_date}: {str(e)}", exc_info=True
            )
            return None


class PredictionMethodAllPrize(models.Model):
    """
    Model lưu trữ thông tin về các phương pháp dự đoán
    """

    code = models.CharField(max_length=50, verbose_name="Mã phương pháp")
    name = models.CharField(max_length=200, verbose_name="Tên phương pháp")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phương pháp dự đoán"
        verbose_name_plural = "Các phương pháp dự đoán"

    def __str__(self):
        return self.name


class PredictionDeAllPrizeResult(models.Model):
    """
    Model lưu trữ kết quả dự đoán từ một phương pháp cụ thể
    """

    dan_de = models.ForeignKey(
        DanDeDacBietAllPrize,
        on_delete=models.CASCADE,
        related_name="predictionsallprize",
    )
    method = models.ForeignKey(
        PredictionMethodAllPrize,
        on_delete=models.CASCADE,
        related_name="resultsallprize",
    )
    predicted_numbers = models.JSONField(verbose_name="Các số dự đoán", default=list)
    winning_numbers = models.JSONField(verbose_name="Các số trúng", default=list)
    hit_count = models.IntegerField(default=0, verbose_name="Số lượng trúng")
    is_special_prize = models.BooleanField(default=False, verbose_name="Là đặc biệt")
    digit_count = models.IntegerField(default=2, verbose_name="Số chữ số")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kết quả dự đoán"
        verbose_name_plural = "Các kết quả dự đoán"
        indexes = [
            models.Index(fields=["dan_de", "method"]),
            models.Index(fields=["hit_count"]),
        ]

    def __str__(self):
        return f"{self.method.name} - {self.dan_de.analysis_date.strftime('%d/%m/%Y')}"


class PredictionFeedback(models.Model):
    """
    Model lưu trữ phản hồi từ người dùng về kết quả dự đoán
    """

    prediction = models.ForeignKey(
        PredictionResult, on_delete=models.CASCADE, related_name="feedback"
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(1, "1 sao"), (2, "2 sao"), (3, "3 sao"), (4, "4 sao"), (5, "5 sao")],
        verbose_name="Đánh giá",
        default=5,
    )
    comment = models.TextField(blank=True, verbose_name="Bình luận")
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="prediction_feedback",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Phản hồi dự đoán"
        verbose_name_plural = "Các phản hồi dự đoán"

    def __str__(self):
        return f"Đánh giá {self.rating}⭐ cho {self.prediction}"


class PredictionStatistic(models.Model):
    date = models.DateField()
    method = models.CharField(max_length=100)
    total_predicted = models.IntegerField(default=0)
    total_hit = models.IntegerField(default=0)
    accuracy = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)
    # Thêm các trường mới
    predictions = models.TextField(blank=True, null=True)  # Lưu dưới dạng JSON
    actual_numbers = models.TextField(blank=True, null=True)  # Lưu dưới dạng JSON
    hit_rate = models.FloatField(default=0.0)

    class Meta:
        unique_together = ["date", "method"]
        indexes = [
            models.Index(fields=["date", "method"]),
        ]

    def __str__(self):
        return f"{self.date} - {self.method}: {self.accuracy:.2f}%"


class BachThuLoMethod(models.Model):
    """
    Model lưu trữ thông tin về các phương pháp tính bạch thủ lô
    """

    DIGIT_CHOICES = [
        (2, "2 số"),
        (3, "3 số"),
        (4, "4 số"),
    ]

    CALCULATION_TYPE_CHOICES = [
        ("addition", "Cộng"),
        ("subtraction", "Trừ"),
        ("multiplication", "Nhân"),
        ("division", "Chia"),
        ("modulo", "Chia lấy dư"),
        ("combination", "Kết hợp"),
        ("pattern", "Theo mẫu"),
        ("statistical", "Thống kê"),
        ("custom", "Tùy chỉnh"),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Mã phương pháp",
        help_text="Mã định danh duy nhất cho phương pháp",
    )
    name = models.CharField(max_length=200, verbose_name="Tên phương pháp")
    description = models.TextField(blank=True, verbose_name="Mô tả chi tiết")
    calculation_type = models.CharField(
        max_length=20,
        choices=CALCULATION_TYPE_CHOICES,
        default="combination",
        verbose_name="Loại phép tính",
    )
    target_digits = models.IntegerField(
        choices=DIGIT_CHOICES, default=2, verbose_name="Số chữ số đích"
    )
    formula = models.TextField(
        blank=True,
        verbose_name="Công thức tính",
        help_text="Mô tả công thức hoặc thuật toán tính toán",
    )
    input_fields = models.JSONField(
        default=list,
        verbose_name="Các trường dữ liệu đầu vào",
        help_text="Danh sách các trường cần thiết từ kết quả xổ số",
    )
    priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Độ ưu tiên",
        help_text="Từ 1 (thấp) đến 10 (cao)",
    )
    success_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Tỷ lệ thành công (%)",
        help_text="Tỷ lệ trúng thống kê",
    )
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phương pháp bạch thủ lô"
        verbose_name_plural = "Các phương pháp bạch thủ lô"
        ordering = ["-priority", "name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["calculation_type"]),
            models.Index(fields=["is_active", "priority"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_success_rate_display(self):
        """Hiển thị tỷ lệ thành công dạng phần trăm"""
        return f"{self.success_rate}%"


class BachThuLoAnalysis(models.Model):
    """
    Model chính lưu trữ dữ liệu phân tích bạch thủ lô cho một ngày cụ thể
    """

    method = models.ForeignKey(
        BachThuLoMethod, on_delete=models.CASCADE, related_name="analyses"
    )

    analysis_date = models.DateField(verbose_name="Ngày phân tích", db_index=True)
    next_day_date = models.DateField(verbose_name="Ngày dự đoán")
    special_prize_next_day = models.CharField(
        max_length=10,
        verbose_name="Giải ĐB ngày sau",
        blank=True,
        help_text="Kết quả thực tế để kiểm tra độ chính xác",
    )
    total_methods_used = models.IntegerField(
        default=0, verbose_name="Tổng số phương pháp sử dụng"
    )
    total_predictions = models.IntegerField(default=0, verbose_name="Tổng số dự đoán")
    total_hits = models.IntegerField(default=0, verbose_name="Tổng số trúng")
    hit_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Tỷ lệ trúng (%)"
    )
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phân tích bạch thủ lô"
        verbose_name_plural = "Các phân tích bạch thủ lô"
        ordering = ["-analysis_date"]
        unique_together = ["analysis_date"]
        indexes = [
            models.Index(fields=["analysis_date"]),
            models.Index(fields=["next_day_date"]),
            models.Index(fields=["hit_rate"]),
        ]

    def __str__(self):
        return f"Bạch thủ lô ngày {self.analysis_date.strftime('%d/%m/%Y') if self.analysis_date else 'N/A'}"

    def calculate_hit_rate(self):
        """Tính toán tỷ lệ trúng"""
        if self.total_predictions > 0:
            self.hit_rate = (self.total_hits / self.total_predictions) * 100
        else:
            self.hit_rate = 0
        return self.hit_rate

    @classmethod
    def create_for_date(cls, analysis_date):
        """Tạo bản ghi phân tích cho một ngày cụ thể"""
        try:
            from results.models import (
                KetQuaXoSo,  # Import tại đây để tránh circular import
            )

            # Lấy dữ liệu kết quả xổ số cho ngày phân tích
            result = KetQuaXoSo.objects.get(ngay=analysis_date)
            next_day_date = analysis_date + timedelta(days=1)
            next_day_result = KetQuaXoSo.objects.filter(ngay=next_day_date).first()

            # Tạo hoặc cập nhật bản ghi phân tích
            analysis, created = cls.objects.update_or_create(
                analysis_date=analysis_date,
                defaults={
                    "next_day_date": next_day_date,
                    "special_prize_next_day": (
                        next_day_result.giai_db if next_day_result else ""
                    ),
                },
            )

            # Xóa các kết quả cũ nếu có
            if not created:
                BachThuLoResult.objects.filter(analysis=analysis).delete()

            # Chuẩn bị dữ liệu đầu vào
            input_data = cls._prepare_input_data(result)

            # Chạy tất cả các phương pháp đang hoạt động
            active_methods = BachThuLoMethod.objects.filter(is_active=True)
            total_methods = 0
            total_predictions = 0
            total_hits = 0

            for method in active_methods:
                result_obj = method.create_prediction(
                    analysis, input_data, next_day_result
                )
                if result_obj:
                    total_methods += 1
                    total_predictions += len(result_obj.predicted_numbers)
                    total_hits += result_obj.hit_count

            # Cập nhật thống kê
            analysis.total_methods_used = total_methods
            analysis.total_predictions = total_predictions
            analysis.total_hits = total_hits
            analysis.calculate_hit_rate()
            analysis.save()

            return analysis

        except Exception as e:
            logger.error(
                f"Lỗi khi tạo phân tích bạch thủ lô cho ngày {analysis_date}: {str(e)}",
                exc_info=True,
            )
            return None

    @staticmethod
    def _prepare_input_data(result):
        """Chuẩn bị dữ liệu đầu vào từ kết quả xổ số"""
        return {
            "giai_db": result.giai_db or "",
            "giai_1": result.giai_1 or "",
            "giai_2_1": result.giai_2_1 or "",
            "giai_2_2": result.giai_2_2 or "",
            "giai_3_1": result.giai_3_1 or "",
            "giai_3_2": result.giai_3_2 or "",
            "giai_3_3": result.giai_3_3 or "",
            "giai_3_4": result.giai_3_4 or "",
            "giai_3_5": result.giai_3_5 or "",
            "giai_3_6": result.giai_3_6 or "",
            "giai_4_1": result.giai_4_1 or "",
            "giai_4_2": result.giai_4_2 or "",
            "giai_4_3": result.giai_4_3 or "",
            "giai_4_4": result.giai_4_4 or "",
            "giai_5_1": result.giai_5_1 or "",
            "giai_5_2": result.giai_5_2 or "",
            "giai_5_3": result.giai_5_3 or "",
            "giai_5_4": result.giai_5_4 or "",
            "giai_5_5": result.giai_5_5 or "",
            "giai_5_6": result.giai_5_6 or "",
            "giai_6_1": result.giai_6_1 or "",
            "giai_6_2": result.giai_6_2 or "",
            "giai_6_3": result.giai_6_3 or "",
            "giai_7_1": result.giai_7_1 or "",
            "giai_7_2": result.giai_7_2 or "",
            "giai_7_3": result.giai_7_3 or "",
            "giai_7_4": result.giai_7_4 or "",
        }


class BachThuLoResult(models.Model):
    """
    Model lưu trữ kết quả dự đoán bạch thủ lô từ một phương pháp cụ thể
    """

    analysis = models.ForeignKey(
        BachThuLoAnalysis, on_delete=models.CASCADE, related_name="bach_thu_results"
    )
    method = models.ForeignKey(
        BachThuLoMethod, on_delete=models.CASCADE, related_name="bach_thu_results"
    )
    predicted_numbers = models.JSONField(
        verbose_name="Các số bạch thủ dự đoán",
        default=list,
        help_text="Danh sách các số 2 chữ số được dự đoán",
    )
    calculation_details = models.JSONField(
        verbose_name="Chi tiết tính toán",
        default=dict,
        help_text="Lưu trữ các bước tính toán chi tiết",
    )
    winning_numbers = models.JSONField(
        verbose_name="Các số trúng",
        default=list,
        help_text="Các số dự đoán có trong kết quả",
    )
    hit_count = models.IntegerField(default=0, verbose_name="Số lượng trúng")
    is_special_prize_hit = models.BooleanField(
        default=False, verbose_name="Trúng giải đặc biệt"
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Điểm tin cậy (%)",
    )
    execution_time = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=0.0000,
        verbose_name="Thời gian thực thi (giây)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kết quả bạch thủ lô"
        verbose_name_plural = "Các kết quả bạch thủ lô"
        unique_together = ["analysis", "method"]
        indexes = [
            models.Index(fields=["analysis", "method"]),
            models.Index(fields=["hit_count"]),
            models.Index(fields=["is_special_prize_hit"]),
            models.Index(fields=["confidence_score"]),
        ]

    def __str__(self):
        return f"{self.method.name} - {self.analysis.analysis_date.strftime('%d/%m/%Y')} - {self.hit_count} trúng"

    def calculate_hit_rate(self):
        """Tính tỷ lệ trúng của kết quả này"""
        if len(self.predicted_numbers) > 0:
            return (self.hit_count / len(self.predicted_numbers)) * 100
        return 0

    def get_prediction_summary(self):
        """Lấy tóm tắt dự đoán"""
        return {
            "method": self.method.name,
            "total_predictions": len(self.predicted_numbers),
            "hits": self.hit_count,
            "hit_rate": self.calculate_hit_rate(),
            "special_prize_hit": self.is_special_prize_hit,
            "confidence": float(self.confidence_score),
        }


class BachThuLoStatistics(models.Model):
    """
    Model lưu trữ thống kê tổng hợp cho các phương pháp bạch thủ lô
    """

    PERIOD_CHOICES = [
        ("daily", "Hàng ngày"),
        ("weekly", "Hàng tuần"),
        ("monthly", "Hàng tháng"),
        ("quarterly", "Hàng quý"),
        ("yearly", "Hàng năm"),
    ]

    method = models.ForeignKey(
        BachThuLoMethod, on_delete=models.CASCADE, related_name="statistics"
    )
    period_type = models.CharField(
        max_length=20, choices=PERIOD_CHOICES, verbose_name="Loại chu kỳ"
    )
    period_start = models.DateField(verbose_name="Bắt đầu chu kỳ")
    period_end = models.DateField(verbose_name="Kết thúc chu kỳ")
    total_analyses = models.IntegerField(default=0, verbose_name="Tổng số phân tích")
    total_predictions = models.IntegerField(default=0, verbose_name="Tổng số dự đoán")
    total_hits = models.IntegerField(default=0, verbose_name="Tổng số trúng")
    hit_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, verbose_name="Tỷ lệ trúng (%)"
    )
    special_prize_hits = models.IntegerField(
        default=0, verbose_name="Số lần trúng giải đặc biệt"
    )
    average_confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Điểm tin cậy trung bình",
    )
    best_day = models.DateField(null=True, blank=True, verbose_name="Ngày tốt nhất")
    worst_day = models.DateField(null=True, blank=True, verbose_name="Ngày tệ nhất")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Thống kê bạch thủ lô"
        verbose_name_plural = "Các thống kê bạch thủ lô"
        unique_together = ["method", "period_type", "period_start", "period_end"]
        ordering = ["-period_end", "-hit_rate"]
        indexes = [
            models.Index(fields=["method", "period_type"]),
            models.Index(fields=["period_start", "period_end"]),
            models.Index(fields=["hit_rate"]),
        ]

    def __str__(self):
        return f"{self.method.name} - {self.period_type} ({self.period_start} - {self.period_end})"

    def calculate_statistics(self):
        """Tính toán lại các thống kê"""
        results = BachThuLoResult.objects.filter(
            method=self.method,
            analysis__analysis_date__range=[self.period_start, self.period_end],
        )

        self.total_analyses = results.count()
        self.total_predictions = sum(len(r.predicted_numbers) for r in results)
        self.total_hits = sum(r.hit_count for r in results)
        self.special_prize_hits = results.filter(is_special_prize_hit=True).count()

        if self.total_predictions > 0:
            self.hit_rate = (self.total_hits / self.total_predictions) * 100
        else:
            self.hit_rate = 0

        if results.exists():
            self.average_confidence = sum(r.confidence_score for r in results) / len(
                results
            )
            # Tìm ngày tốt nhất và tệ nhất
            best_result = max(results, key=lambda x: x.calculate_hit_rate())
            worst_result = min(results, key=lambda x: x.calculate_hit_rate())
            self.best_day = best_result.analysis.analysis_date
            self.worst_day = worst_result.analysis.analysis_date
        else:
            self.average_confidence = 0

        self.save()


class DanBtl(models.Model):
    """
    Model chính lưu trữ dữ liệu phân tích từ kết quả xổ số cho một ngày cụ thể
    """

    analysis_date = models.DateField(verbose_name="Ngày phân tích")
    next_day_date = models.DateField(verbose_name="Ngày kế tiếp")
    prize_next_day = models.CharField(
        max_length=500, verbose_name="Giải trúng ngày sau", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dàn bạch thủ lô"
        verbose_name_plural = "Các dàn bạch thủ lô"
        ordering = ["-analysis_date"]
        indexes = [
            models.Index(fields=["analysis_date"]),
            models.Index(fields=["next_day_date"]),
        ]

    def __str__(self):
        return f"Dàn đề ngày {self.analysis_date.strftime('%d/%m/%Y') if self.analysis_date else 'N/A'}"

    @classmethod
    def create_for_date(cls, analysis_date):
        """Tạo bản ghi cho một ngày cụ thể và tính toán kết quả từ tất cả các phương pháp"""
        try:
            from results.methods_btl import get_all_methods
            from results.models import PredictionResultBtl

            # Lấy dữ liệu kết quả xổ số cho ngày phân tích
            result = KetQuaXoSo.objects.get(ngay=analysis_date)
            next_day_date = analysis_date + timedelta(days=1)
            next_day_result = KetQuaXoSo.objects.filter(ngay=next_day_date).first()

            # Lấy giải đặc biệt của ngày tiếp theo (hoặc chuỗi rỗng nếu không có)
            prize_next_day = ""
            if next_day_result and hasattr(next_day_result, "giai_db"):
                # Nếu giải đặc biệt dài hơn 5 ký tự, chỉ lấy 5 ký tự cuối
                if next_day_result.giai_db:
                    prize_next_day = (
                        next_day_result.giai_db if next_day_result else "",
                    )

            # Tạo bản ghi DanBtl
            dan_btl, created = cls.objects.update_or_create(
                analysis_date=analysis_date,
                defaults={
                    "next_day_date": next_day_date,
                    "prize_next_day": prize_next_day,  # Đã sửa - chỉ lưu giải đặc biệt
                },
            )

            # Chuẩn bị dữ liệu đầu vào cho các phương pháp
            input_data = {
                "giai_db": result.giai_db or "",
                "giai_1": result.giai_1 or "",
                "giai_2_1": result.giai_2_1 or "",
                "giai_2_2": result.giai_2_2 or "",
                "giai_3_1": result.giai_3_1 or "",
                "giai_3_2": result.giai_3_2 or "",
                "giai_3_3": result.giai_3_3 or "",
                "giai_3_4": result.giai_3_4 or "",
                "giai_3_5": result.giai_3_5 or "",
                "giai_3_6": result.giai_3_6 or "",
                "giai_4_1": result.giai_4_1 or "",
                "giai_4_2": result.giai_4_2 or "",
                "giai_4_3": result.giai_4_3 or "",
                "giai_4_4": result.giai_4_4 or "",
                "giai_5_1": result.giai_5_1 or "",
                "giai_5_2": result.giai_5_2 or "",
                "giai_5_3": result.giai_5_3 or "",
                "giai_5_4": result.giai_5_4 or "",
                "giai_5_5": result.giai_5_5 or "",
                "giai_5_6": result.giai_5_6 or "",
                "giai_6_1": result.giai_6_1 or "",
                "giai_6_2": result.giai_6_2 or "",
                "giai_6_3": result.giai_6_3 or "",
                "giai_7_1": result.giai_7_1 or "",
                "giai_7_2": result.giai_7_2 or "",
                "giai_7_3": result.giai_7_3 or "",
                "giai_7_4": result.giai_7_4 or "",
            }

            # Chạy tất cả các phương pháp dự đoán và lưu kết quả
            methods = get_all_methods()
            for method in methods:
                # Truyền đối tượng KetQuaXoSo cho ngày tiếp theo, không phải chuỗi
                method.create_prediction(dan_btl, input_data, next_day_result)

            return dan_btl
        except KetQuaXoSo.DoesNotExist:
            logger.error(f"Không tìm thấy kết quả xổ số cho ngày {analysis_date}")
            return None
        except Exception as e:
            logger.error(
                f"Lỗi khi tạo dàn đề cho ngày {analysis_date}: {str(e)}", exc_info=True
            )
            return None


class PredictionMethodBtl(models.Model):
    """
    Model lưu trữ thông tin về các phương pháp dự đoán
    """

    code = models.CharField(max_length=50, verbose_name="Mã phương pháp")
    name = models.CharField(max_length=200, verbose_name="Tên phương pháp")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phương pháp dự đoán Btl"
        verbose_name_plural = "Các phương pháp dự đoán Btl"

    def __str__(self):
        return self.name


class PredictionResultBtl(models.Model):
    """
    Model lưu trữ kết quả dự đoán từ một phương pháp cụ thể
    """

    dan_btl = models.ForeignKey(
        DanBtl, on_delete=models.CASCADE, related_name="predictions_btl"
    )
    method = models.ForeignKey(
        PredictionMethodBtl, on_delete=models.CASCADE, related_name="results_btl"
    )
    predicted_numbers = models.JSONField(verbose_name="Các số dự đoán", default=list)
    winning_numbers = models.JSONField(verbose_name="Các số trúng", default=list)
    hit_count = models.IntegerField(default=0, verbose_name="Số lượng trúng")
    is_special_prize = models.BooleanField(default=False, verbose_name="Là đặc biệt")
    digit_count = models.IntegerField(default=2, verbose_name="Số chữ số")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kết quả dự đoán Bạch thủ lô"
        verbose_name_plural = "Các kết quả dự đoán Bạch thủ lô"
        indexes = [
            models.Index(fields=["dan_btl", "method"]),
            models.Index(fields=["hit_count"]),
        ]

    def __str__(self):
        return f"{self.method.name} - {self.dan_btl.analysis_date.strftime('%d/%m/%Y')}"


class OptimalMethodEnsemble(models.Model):
    """
    Lưu trữ tập hợp phương pháp tối ưu đã được tính toán trước
    """

    analysis_date = models.DateField(verbose_name="Ngày phân tích", unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Lưu trữ tập hợp phương pháp tối ưu dưới dạng JSON
    optimal_methods_json = models.TextField(
        verbose_name="Tập hợp phương pháp tối ưu (JSON)"
    )

    # Lưu trữ thông tin hiệu suất và xếp hạng
    ranked_methods_json = models.TextField(
        verbose_name="Phương pháp đã xếp hạng (JSON)", null=True, blank=True
    )

    # Thông tin bổ sung
    calculation_time = models.FloatField(
        verbose_name="Thời gian tính toán (giây)", null=True, blank=True
    )
    method_count = models.IntegerField(verbose_name="Số lượng phương pháp", default=0)

    class Meta:
        verbose_name = "Tập hợp phương pháp tối ưu"
        verbose_name_plural = "Các tập hợp phương pháp tối ưu"
        ordering = ["-analysis_date"]
        indexes = [
            models.Index(fields=["analysis_date"]),
        ]

    def __str__(self):
        return f"Phương pháp tối ưu cho ngày {self.analysis_date.strftime('%d/%m/%Y')}"

    def get_optimal_methods(self):
        """Trả về danh sách phương pháp tối ưu từ JSON"""
        try:
            return json.loads(self.optimal_methods_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_ranked_methods(self):
        """Trả về danh sách phương pháp đã xếp hạng từ JSON"""
        try:
            return (
                json.loads(self.ranked_methods_json) if self.ranked_methods_json else []
            )
        except (json.JSONDecodeError, TypeError):
            return []

    def set_optimal_methods(self, methods):
        """Lưu danh sách phương pháp tối ưu dưới dạng JSON"""
        # Đảm bảo tất cả các giá trị đều có thể được chuyển đổi thành JSON
        clean_methods = []
        for method in methods:
            clean_method = {}
            for key, value in method.items():
                if (
                    isinstance(value, (int, float, str, bool, list, dict))
                    or value is None
                ):
                    # Đảm bảo các số float được lưu đúng cách
                    if isinstance(value, float):
                        clean_method[key] = float(value)
                    else:
                        clean_method[key] = value
                else:
                    # Chuyển đổi các kiểu dữ liệu không được hỗ trợ thành chuỗi
                    clean_method[key] = str(value)
            clean_methods.append(clean_method)

        self.optimal_methods_json = json.dumps(clean_methods)
        self.method_count = len(methods)

    def set_ranked_methods(self, methods):
        """Lưu danh sách phương pháp đã xếp hạng dưới dạng JSON"""
        # Tương tự như trên, đảm bảo tất cả các giá trị đều có thể được chuyển đổi thành JSON
        clean_methods = []
        for method in methods:
            clean_method = {}
            for key, value in method.items():
                if (
                    isinstance(value, (int, float, str, bool, list, dict))
                    or value is None
                ):
                    if isinstance(value, float):
                        clean_method[key] = float(value)
                    else:
                        clean_method[key] = value
                else:
                    clean_method[key] = str(value)
            clean_methods.append(clean_method)

        self.ranked_methods_json = json.dumps(clean_methods)


# class phân tích và dự đoán btl
class BtlAnalytics(models.Model):
    """
    Bảng phân tích dữ liệu Bạch Thủ Lô để hỗ trợ báo cáo
    """

    # Khóa thời gian
    date = models.DateField(verbose_name="Ngày phân tích", db_index=True)
    year = models.IntegerField(verbose_name="Năm", db_index=True)
    month = models.IntegerField(verbose_name="Tháng", db_index=True)
    day = models.IntegerField(verbose_name="Ngày", db_index=True)
    day_of_week = models.IntegerField(
        verbose_name="Thứ trong tuần", db_index=True
    )  # 0 = Thứ 2, 6 = Chủ nhật
    week_of_year = models.IntegerField(verbose_name="Tuần trong năm", db_index=True)

    # Liên kết đến dữ liệu gốc
    dan_btl = models.ForeignKey(
        DanBtl,
        on_delete=models.CASCADE,
        related_name="analytics",
        verbose_name="Dàn Bạch Thủ Lô",
    )

    # Dữ liệu tổng quan
    total_methods = models.IntegerField(verbose_name="Tổng số phương pháp", default=0)
    total_predictions = models.IntegerField(verbose_name="Tổng số dự đoán", default=0)
    total_hits = models.IntegerField(verbose_name="Tổng số trúng", default=0)
    overall_hit_rate = models.FloatField(
        verbose_name="Tỷ lệ trúng tổng thể (%)", default=0
    )

    # Thông tin kết quả xổ số
    prize_next_day = models.CharField(
        max_length=10, verbose_name="Giải đặc biệt ngày kế tiếp", blank=True
    )
    winning_numbers = models.JSONField(
        verbose_name="Các số trúng ngày kế tiếp", default=list
    )

    # Thông tin thống kê phương pháp
    methods_with_hits = models.IntegerField(
        verbose_name="Số phương pháp có trúng", default=0
    )
    methods_hit_rate = models.FloatField(
        verbose_name="Tỷ lệ phương pháp trúng (%)", default=0
    )

    # Thông tin số dự đoán phổ biến
    most_predicted_numbers = models.JSONField(
        verbose_name="Top 10 số được dự đoán nhiều nhất", default=list
    )
    most_consensus_numbers = models.JSONField(
        verbose_name="Top 10 số có nhiều phương pháp dự đoán nhất", default=list
    )

    # Thông tin phương pháp tốt nhất
    best_methods = models.JSONField(
        verbose_name="Top 5 phương pháp tốt nhất", default=list
    )

    # Thông tin về chu kỳ và xu hướng
    trending_numbers = models.JSONField(
        verbose_name="Các số đang có xu hướng", default=list
    )

    # Dữ liệu hiệu suất theo nhóm phương pháp
    method_group_performance = models.JSONField(
        verbose_name="Hiệu suất theo nhóm phương pháp", default=dict
    )

    # Thông tin về lịch sử trúng/trật
    sequential_hits = models.IntegerField(
        verbose_name="Số ngày trúng liên tiếp tính đến ngày này", default=0
    )
    sequential_misses = models.IntegerField(
        verbose_name="Số ngày trật liên tiếp tính đến ngày này", default=0
    )

    # Thời điểm tạo và cập nhật
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phân tích Bạch Thủ Lô"
        verbose_name_plural = "Phân tích Bạch Thủ Lô"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["year", "month"]),
            models.Index(fields=["year", "week_of_year"]),
            models.Index(fields=["day_of_week"]),
            models.Index(fields=["overall_hit_rate"]),
        ]
        unique_together = ["date", "dan_btl"]

    def __str__(self):
        return f"Phân tích BTL ngày {self.date.strftime('%d/%m/%Y')}"

    @property
    def has_hits(self):
        """Kiểm tra xem ngày này có trúng không"""
        return self.total_hits > 0


class BtlMethodAnalytics(models.Model):
    """
    Bảng phân tích dữ liệu chi tiết cho từng phương pháp
    """

    # Liên kết đến phân tích chính và phương pháp
    btl_analytics = models.ForeignKey(
        BtlAnalytics,
        on_delete=models.CASCADE,
        related_name="method_analytics",
        verbose_name="Phân tích Bạch Thủ Lô",
    )
    method = models.ForeignKey(
        PredictionMethodBtl,
        on_delete=models.CASCADE,
        related_name="analytics",
        verbose_name="Phương pháp",
    )

    # Ngày phân tích (thêm cho tiện truy vấn)
    date = models.DateField(verbose_name="Ngày phân tích", db_index=True)

    # Thông tin dự đoán và kết quả
    prediction_count = models.IntegerField(verbose_name="Số lượng dự đoán", default=0)
    hit_count = models.IntegerField(verbose_name="Số lượng trúng", default=0)
    hit_rate = models.FloatField(verbose_name="Tỷ lệ trúng (%)", default=0)

    # Chỉ số tin cậy và đánh giá
    confidence_score = models.FloatField(
        verbose_name="Điểm tin cậy (Wilson score)", default=0
    )
    profit_estimate = models.IntegerField(verbose_name="Ước tính lợi nhuận", default=0)
    roi_estimate = models.FloatField(verbose_name="ROI ước tính (%)", default=0)

    # Thông tin về dự đoán
    predicted_numbers = models.JSONField(
        verbose_name="Các số được dự đoán", default=list
    )
    hit_numbers = models.JSONField(verbose_name="Các số trúng", default=list)

    # Dữ liệu xu hướng
    rolling_hit_rate_7d = models.FloatField(
        verbose_name="Tỷ lệ trúng trung bình 7 ngày (%)", default=0
    )
    rolling_hit_rate_30d = models.FloatField(
        verbose_name="Tỷ lệ trúng trung bình 30 ngày (%)", default=0
    )
    trend_direction = models.CharField(
        max_length=10,
        choices=[("up", "Tăng"), ("down", "Giảm"), ("stable", "Ổn định")],
        default="stable",
        verbose_name="Xu hướng hiệu suất",
    )

    # Thời điểm tạo và cập nhật
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Phân tích Phương pháp BTL"
        verbose_name_plural = "Phân tích Phương pháp BTL"
        ordering = ["-date", "hit_rate"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["method"]),
            models.Index(fields=["hit_rate"]),
            models.Index(fields=["confidence_score"]),
        ]
        unique_together = ["btl_analytics", "method"]

    def __str__(self):
        return f"{self.method.name} - {self.date.strftime('%d/%m/%Y')}"


class BtlTimeAggregation(models.Model):
    """
    Bảng tổng hợp dữ liệu Bạch Thủ Lô theo thời gian (tháng, tuần, quý)
    """

    # Thông tin thời gian
    aggregation_type = models.CharField(
        max_length=10,
        choices=[
            ("daily", "Ngày"),
            ("weekly", "Tuần"),
            ("monthly", "Tháng"),
            ("quarterly", "Quý"),
            ("yearly", "Năm"),
        ],
        db_index=True,
        verbose_name="Loại tổng hợp",
    )
    year = models.IntegerField(verbose_name="Năm", db_index=True)
    period = models.IntegerField(verbose_name="Kỳ (tuần/tháng/quý)", db_index=True)
    start_date = models.DateField(verbose_name="Ngày bắt đầu")
    end_date = models.DateField(verbose_name="Ngày kết thúc")

    # Dữ liệu tổng hợp
    total_days = models.IntegerField(verbose_name="Tổng số ngày", default=0)
    days_with_hits = models.IntegerField(verbose_name="Số ngày có trúng", default=0)
    days_hit_rate = models.FloatField(verbose_name="Tỷ lệ ngày trúng (%)", default=0)

    total_predictions = models.IntegerField(verbose_name="Tổng số dự đoán", default=0)
    total_hits = models.IntegerField(verbose_name="Tổng số trúng", default=0)
    overall_hit_rate = models.FloatField(
        verbose_name="Tỷ lệ trúng tổng thể (%)", default=0
    )

    # Thông tin phương pháp
    best_method = models.ForeignKey(
        PredictionMethodBtl,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="best_timeagg",
        verbose_name="Phương pháp tốt nhất",
    )

    best_methods = models.JSONField(
        verbose_name="Top 5 phương pháp tốt nhất", default=list
    )
    method_performance = models.JSONField(
        verbose_name="Hiệu suất tất cả phương pháp", default=dict
    )

    # Phân tích số
    hot_numbers = models.JSONField(verbose_name="Các số nóng", default=list)
    cold_numbers = models.JSONField(verbose_name="Các số lạnh", default=list)

    # Thời điểm tạo và cập nhật
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tổng hợp BTL theo thời gian"
        verbose_name_plural = "Tổng hợp BTL theo thời gian"
        ordering = ["-year", "-period"]
        indexes = [
            models.Index(fields=["aggregation_type"]),
            models.Index(fields=["year", "period"]),
            models.Index(fields=["start_date"]),
            models.Index(fields=["end_date"]),
        ]
        unique_together = ["aggregation_type", "year", "period"]

    def __str__(self):
        if self.aggregation_type == "monthly":
            return f"Tổng hợp tháng {self.period}/{self.year}"
        elif self.aggregation_type == "weekly":
            return f"Tổng hợp tuần {self.period}/{self.year}"
        elif self.aggregation_type == "quarterly":
            return f"Tổng hợp quý {self.period}/{self.year}"
        elif self.aggregation_type == "yearly":
            return f"Tổng hợp năm {self.year}"
        else:
            return f"Tổng hợp ngày {self.start_date.strftime('%d/%m/%Y')}"


class NumberFrequencyStats(models.Model):
    """Lưu trữ tần suất xuất hiện của các số theo ngày"""

    number = models.CharField(max_length=2, help_text="Số 2 chữ số (00-99)")
    date = models.DateField(help_text="Ngày xuất hiện")

    # Vị trí xuất hiện (để phân tích theo giải)
    appeared_in_special = models.BooleanField(
        default=False, help_text="Xuất hiện trong giải đặc biệt"
    )
    appeared_in_first = models.BooleanField(
        default=False, help_text="Xuất hiện trong giải nhất"
    )
    appeared_in_other = models.BooleanField(
        default=False, help_text="Xuất hiện trong các giải khác"
    )

    # Thông tin bổ sung
    day_of_week = models.IntegerField(help_text="Thứ trong tuần (0-6)")
    day_of_month = models.IntegerField(help_text="Ngày trong tháng (1-31)")
    week_of_month = models.IntegerField(help_text="Tuần trong tháng (1-5)")
    month = models.IntegerField(help_text="Tháng (1-12)")
    year = models.IntegerField(help_text="Năm")

    class Meta:
        unique_together = ("number", "date")
        indexes = [
            models.Index(fields=["number"]),
            models.Index(fields=["date"]),
            models.Index(fields=["day_of_month"]),
            models.Index(fields=["month"]),
            models.Index(fields=["year"]),
            models.Index(fields=["day_of_week"]),
        ]

    def __str__(self):
        return f"Number {self.number} on {self.date}"


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


class AdvancedAnalysisResult(models.Model):
    """Lưu trữ kết quả phân tích nâng cao"""

    # Thông tin cơ bản
    analysis_date = models.DateField(unique=True, help_text="Ngày thực hiện phân tích")
    target_date = models.DateField(help_text="Ngày cần dự đoán")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Kết quả phân tích
    frequency_cycle_analysis = JSONField(
        null=True, blank=True, help_text="Kết quả phân tích chu kỳ tần suất"
    )
    number_relationship_analysis = JSONField(
        null=True, blank=True, help_text="Kết quả phân tích mối quan hệ giữa các số"
    )
    pattern_analysis = JSONField(
        null=True, blank=True, help_text="Kết quả phân tích mẫu"
    )
    related_set_analysis = JSONField(
        null=True, blank=True, help_text="Kết quả phân tích bộ số liên quan"
    )
    spectral_analysis = JSONField(
        null=True, blank=True, help_text="Kết quả phân tích phổ"
    )
    graph_analysis = JSONField(
        null=True, blank=True, help_text="Kết quả phân tích đồ thị"
    )

    # Model predictions
    shap_prediction = JSONField(null=True, blank=True, help_text="Kết quả dự đoán SHAP")
    lstm_prediction = JSONField(null=True, blank=True, help_text="Kết quả dự đoán LSTM")
    rl_prediction = JSONField(
        null=True, blank=True, help_text="Kết quả dự đoán Reinforcement Learning"
    )

    # Final combined predictions
    combined_predictions = JSONField(
        null=True, blank=True, help_text="Kết quả dự đoán kết hợp cuối cùng"
    )
    prediction_weights = JSONField(
        null=True, blank=True, help_text="Trọng số của từng phương pháp"
    )

    # Performance metrics
    actual_results = JSONField(
        null=True,
        blank=True,
        help_text="Kết quả thực tế (được cập nhật sau khi có kết quả)",
    )
    performance_metrics = JSONField(
        null=True, blank=True, help_text="Các chỉ số hiệu suất của dự đoán"
    )

    class Meta:
        ordering = ["-analysis_date"]
        indexes = [
            models.Index(fields=["analysis_date"]),
            models.Index(fields=["target_date"]),
        ]

    def __str__(self):
        return f"Analysis for {self.analysis_date}"


class MethodPerformanceHistory(models.Model):
    """Lưu trữ lịch sử hiệu suất của từng phương pháp"""

    method_name = models.CharField(max_length=100)
    date = models.DateField()

    # Số lượng dự đoán và kết quả
    prediction_count = models.IntegerField(default=0)
    hit_count = models.IntegerField(default=0)

    # Chỉ số hiệu suất
    hit_rate = models.FloatField(default=0)
    confidence_score = models.FloatField(
        default=0
    )  # Wilson score hoặc chỉ số tin cậy khác

    # Trọng số được gán
    assigned_weight = models.FloatField(default=0)

    # Liên kết với kết quả phân tích
    analysis = models.ForeignKey(
        AdvancedAnalysisResult,
        on_delete=models.CASCADE,
        related_name="method_performances",
    )

    class Meta:
        unique_together = ("method_name", "date")
        ordering = ["-date", "method_name"]

    def __str__(self):
        return f"{self.method_name} on {self.date}: {self.hit_rate:.2f}%"


class OptimizedWeights(models.Model):
    """Lưu trữ trọng số tối ưu cho các phương pháp dự đoán"""

    calculation_date = models.DateField(auto_now_add=True)
    weights = JSONField(default=dict)
    meta_info = JSONField(default=dict)

    class Meta:
        ordering = ["-calculation_date"]

    def __str__(self):
        return f"Weights calculated on {self.calculation_date}"


import json

from django.db import models




class MethodWeight(models.Model):
    """Lưu trữ lịch sử trọng số các phương pháp dự đoán"""

    effective_date = models.DateField(help_text="Ngày áp dụng trọng số")
    method_name = models.CharField(max_length=50, help_text="Tên phương pháp")
    method_version = models.CharField(
        max_length=20, default="1.0", help_text="Phiên bản phương pháp"
    )
    weight = models.FloatField(default=0.5, help_text="Trọng số (0-1)")
    calculation_basis = models.CharField(
        max_length=50,
        choices=[
            ("historical", "Dựa trên hiệu suất lịch sử"),
            ("optimized", "Tối ưu hóa bằng thuật toán"),
            ("manual", "Thiết lập thủ công"),
        ],
        default="historical",
        help_text="Cơ sở tính toán trọng số",
    )
    days_analyzed = models.IntegerField(default=30, help_text="Số ngày đã phân tích")

    # Thông tin bổ sung để theo dõi hiệu suất
    hit_rate = models.FloatField(default=0.0, help_text="Tỷ lệ trúng")
    day_hit_rate = models.FloatField(default=0.0, help_text="Tỷ lệ ngày trúng")
    tired_rate = models.FloatField(default=0.0, help_text="Tỷ lệ mệt mỏi")
    trend_direction = models.CharField(
        max_length=20, default="stable", help_text="Hướng xu hướng"
    )
    trend_strength = models.FloatField(default=0.0, help_text="Độ mạnh xu hướng")

    class Meta:
        indexes = [
            models.Index(fields=["effective_date"]),
            models.Index(fields=["method_name"]),
        ]

    def __str__(self):
        return f"{self.method_name} ({self.effective_date}): {self.weight:.2f}"


class MethodWeightsHistory(models.Model):
    """Model to store method weights history"""

    date_created = models.DateTimeField(auto_now_add=True)
    effective_date = (
        models.DateField()
    )  # Date from which these weights become effective
    method_name = models.CharField(max_length=50)
    method_version = models.CharField(max_length=20, default="1.0")
    weight = models.FloatField(default=0.5)
    calculation_basis = models.CharField(
        max_length=50,
        choices=[
            ("historical", "Based on historical performance"),
            ("optimized", "Optimized through algorithm"),
            ("manual", "Manually set"),
        ],
        default="historical",
    )
    days_analyzed = models.IntegerField(
        default=30
    )  # How many days were analyzed to calculate this weight

    class Meta:
        indexes = [
            models.Index(fields=["effective_date"]),
            models.Index(fields=["method_name"]),
        ]


class DailyPredictionAnalysis(models.Model):
    """
    Model lưu trữ phân tích dự đoán hàng ngày
    """

    analysis_date = models.DateField(unique=True, verbose_name="Ngày phân tích")
    target_date = models.DateField(verbose_name="Ngày dự đoán")

    # Dữ liệu dự đoán
    predictions_data = models.JSONField(verbose_name="Dữ liệu dự đoán", default=dict)
    has_actual_results = models.BooleanField(
        default=False, help_text="Whether actual results are available for comparison"
    )
    # Kết quả thực tế
    actual_numbers = models.JSONField(
        verbose_name="Số thực tế", null=True, blank=True, default=list
    )

    # Thống kê hiệu suất
    total_predictions = models.IntegerField(default=0, verbose_name="Tổng số dự đoán")
    correct_predictions = models.IntegerField(default=0, verbose_name="Số dự đoán đúng")
    accuracy_rate = models.FloatField(default=0.0, verbose_name="Tỷ lệ chính xác (%)")

    # Thống kê theo phương pháp
    method_performance = models.JSONField(
        verbose_name="Hiệu suất theo phương pháp", default=dict
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processing_time = models.FloatField(
        default=0.0, verbose_name="Thời gian xử lý (giây)"
    )

    class Meta:
        db_table = "daily_prediction_analysis"
        indexes = [
            models.Index(fields=["analysis_date"]),
            models.Index(fields=["target_date"]),
            models.Index(fields=["accuracy_rate"]),
        ]
        verbose_name = "Phân tích dự đoán hàng ngày"
        verbose_name_plural = "Phân tích dự đoán hàng ngày"

    def __str__(self):
        return f"Phân tích {self.analysis_date} -> {self.target_date}"

    def calculate_accuracy(self):
        """Tính toán độ chính xác khi có kết quả thực tế"""
        if not self.actual_numbers:
            return

        total_correct = 0
        total_predictions = 0
        method_stats = {}

        for method_name, predictions in self.predictions_data.items():
            if isinstance(predictions, dict) and "numbers" in predictions:
                predicted_numbers = predictions["numbers"]
            elif isinstance(predictions, list):
                predicted_numbers = predictions
            else:
                continue

            # Tính số trúng cho phương pháp này
            correct = len(set(predicted_numbers) & set(self.actual_numbers))
            total = len(predicted_numbers)

            method_stats[method_name] = {
                "total": total,
                "correct": correct,
                "accuracy": (correct / total * 100) if total > 0 else 0,
            }

            total_correct += correct
            total_predictions += total

        # Cập nhật thống kê tổng thể
        self.correct_predictions = total_correct
        self.total_predictions = total_predictions
        self.accuracy_rate = (
            (total_correct / total_predictions * 100) if total_predictions > 0 else 0
        )
        self.method_performance = method_stats

        self.save()

    @classmethod
    def get_monthly_stats(cls, year, month):
        """Lấy thống kê tháng"""
        records = cls.objects.filter(
            analysis_date__year=year, analysis_date__month=month
        ).exclude(actual_numbers__isnull=True)

        if not records:
            return None

        total_accuracy = sum(r.accuracy_rate for r in records)
        avg_accuracy = total_accuracy / len(records)

        # Thống kê theo phương pháp
        method_stats = {}
        for record in records:
            for method, stats in record.method_performance.items():
                if method not in method_stats:
                    method_stats[method] = {"total": 0, "correct": 0, "count": 0}

                method_stats[method]["total"] += stats.get("total", 0)
                method_stats[method]["correct"] += stats.get("correct", 0)
                method_stats[method]["count"] += 1

        # Tính accuracy cho từng phương pháp
        for method in method_stats:
            total = method_stats[method]["total"]
            correct = method_stats[method]["correct"]
            method_stats[method]["accuracy"] = (
                (correct / total * 100) if total > 0 else 0
            )

        return {
            "total_days": len(records),
            "avg_accuracy": avg_accuracy,
            "best_day": max(records, key=lambda x: x.accuracy_rate),
            "worst_day": min(records, key=lambda x: x.accuracy_rate),
            "method_performance": method_stats,
        }


class AccuracyTrend(models.Model):
    """
    Model theo dõi xu hướng độ chính xác theo thời gian
    """

    date = models.DateField(unique=True, verbose_name="Ngày")

    # Độ chính xác rolling
    accuracy_7day = models.FloatField(default=0.0, verbose_name="Độ chính xác 7 ngày")
    accuracy_15day = models.FloatField(default=0.0, verbose_name="Độ chính xác 15 ngày")
    accuracy_30day = models.FloatField(default=0.0, verbose_name="Độ chính xác 30 ngày")

    # Xu hướng
    trend_direction = models.CharField(
        max_length=20,
        choices=[
            ("improving", "Cải thiện"),
            ("declining", "Giảm"),
            ("stable", "Ổn định"),
        ],
        default="stable",
        verbose_name="Hướng xu hướng",
    )

    # Top phương pháp
    best_methods = models.JSONField(verbose_name="Phương pháp tốt nhất", default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accuracy_trend"
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["accuracy_30day"]),
        ]

    @classmethod
    def update_trend(cls, target_date):
        """Cập nhật xu hướng cho một ngày"""
        try:
            # Lấy dữ liệu 30 ngày gần nhất
            end_date = target_date
            start_date = end_date - timedelta(days=30)

            analyses = (
                DailyPredictionAnalysis.objects.filter(
                    analysis_date__range=(start_date, end_date)
                )
                .exclude(actual_numbers__isnull=True)
                .order_by("analysis_date")
            )

            if len(analyses) < 7:
                return None

            # Tính accuracy rolling
            accuracy_7day = cls._calculate_rolling_accuracy(analyses, 7)
            accuracy_15day = cls._calculate_rolling_accuracy(analyses, 15)
            accuracy_30day = cls._calculate_rolling_accuracy(analyses, 30)

            # Xác định xu hướng
            trend = cls._determine_trend(analyses[-7:])

            # Tìm phương pháp tốt nhất
            best_methods = cls._find_best_methods(analyses[-15:])

            # Cập nhật hoặc tạo mới
            trend_record, created = cls.objects.update_or_create(
                date=target_date,
                defaults={
                    "accuracy_7day": accuracy_7day,
                    "accuracy_15day": accuracy_15day,
                    "accuracy_30day": accuracy_30day,
                    "trend_direction": trend,
                    "best_methods": best_methods,
                },
            )

            return trend_record

        except Exception as e:
            logger.error(f"Error updating accuracy trend: {e}")
            return None

    @staticmethod
    def _calculate_rolling_accuracy(analyses, days):
        """Tính accuracy rolling"""
        recent_analyses = list(analyses)[-days:]
        if not recent_analyses:
            return 0.0

        total_accuracy = sum(a.accuracy_rate for a in recent_analyses)
        return total_accuracy / len(recent_analyses)

    @staticmethod
    def _determine_trend(recent_analyses):
        """Xác định xu hướng"""
        if len(recent_analyses) < 3:
            return "stable"

        # So sánh nửa đầu vs nửa cuối
        mid = len(recent_analyses) // 2
        first_half_avg = sum(a.accuracy_rate for a in recent_analyses[:mid]) / mid
        second_half_avg = sum(a.accuracy_rate for a in recent_analyses[mid:]) / (
            len(recent_analyses) - mid
        )

        diff = second_half_avg - first_half_avg

        if diff > 5:  # Cải thiện > 5%
            return "improving"
        elif diff < -5:  # Giảm > 5%
            return "declining"
        else:
            return "stable"

    @staticmethod
    def _find_best_methods(analyses):
        """Tìm phương pháp tốt nhất"""
        method_totals = {}

        for analysis in analyses:
            for method, stats in analysis.method_performance.items():
                if method not in method_totals:
                    method_totals[method] = {"total": 0, "correct": 0}

                method_totals[method]["total"] += stats.get("total", 0)
                method_totals[method]["correct"] += stats.get("correct", 0)

        # Tính accuracy và sắp xếp
        method_accuracy = []
        for method, totals in method_totals.items():
            if totals["total"] > 0:
                accuracy = (totals["correct"] / totals["total"]) * 100
                method_accuracy.append(
                    {
                        "method": method,
                        "accuracy": accuracy,
                        "total_predictions": totals["total"],
                    }
                )

        # Sắp xếp theo accuracy
        method_accuracy.sort(key=lambda x: x["accuracy"], reverse=True)

        return method_accuracy[:5]  # Top 5


class PredictionCache(models.Model):
    """
    Cache cho prediction results
    """

    date = models.DateField()
    analysis_type = models.CharField(max_length=50, default="combined")
    data = models.TextField()  # JSON data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    class Meta:
        unique_together = ["date", "analysis_type"]
        indexes = [
            models.Index(fields=["date", "analysis_type"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"Cache {self.analysis_type} - {self.date}"

    def is_expired(self):
        return timezone.now() > self.expires_at


import os
import pickle
from datetime import timedelta

from django.db import models
from django.utils import timezone

from results.models import KetQuaXoSo


class StateAnalysisManager(models.Manager):
    def create_from_ketqua(self, ket_qua):
        """Tạo state analysis từ kết quả xổ số"""
        try:
            # Trích xuất state từ giải 7-2 và 7-3
            num_7_2 = ket_qua.giai_7_2
            num_7_3 = ket_qua.giai_7_3

            if num_7_2 is None or num_7_3 is None:
                return None

            str_7_2 = str(num_7_2).zfill(2)
            str_7_3 = str(num_7_3).zfill(2)
            state = str_7_2[0] + str_7_3[0]

            return self.create(
                ngay=ket_qua.ngay,
                state=state,
                giai_7_2=num_7_2,
                giai_7_3=num_7_3,
                source_record=ket_qua,
            )
        except Exception as e:
            return None


class StateAnalysis(models.Model):
    """Model lưu trữ phân tích state từ kết quả xổ số"""

    ngay = models.DateField("Ngày", db_index=True)
    state = models.CharField("State", max_length=10, db_index=True)
    giai_7_2 = models.IntegerField("Giải 7-2", null=True, blank=True)
    giai_7_3 = models.IntegerField("Giải 7-3", null=True, blank=True)
    source_record = models.ForeignKey(
        KetQuaXoSo, on_delete=models.CASCADE, related_name="state_analyses"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = StateAnalysisManager()

    class Meta:
        db_table = "results_state_analysis"
        unique_together = ["ngay", "state"]
        ordering = ["ngay"]
        verbose_name = "State Analysis"
        verbose_name_plural = "State Analyses"

    def __str__(self):
        return f"{self.ngay} - State: {self.state}"


class PredictionModelManager(models.Manager):
    def get_active_model(self, model_type):
        """Lấy model đang hoạt động theo loại"""
        return (
            self.filter(model_type=model_type, is_active=True)
            .order_by("-created_at")
            .first()
        )

    def create_model_record(self, model_type, file_path, metadata=None):
        """Tạo bản ghi model mới"""
        # Deactivate old models of same type
        self.filter(model_type=model_type, is_active=True).update(is_active=False)

        return self.create(
            model_type=model_type,
            file_path=file_path,
            metadata=metadata or {},
            is_active=True,
        )


class PredictionModel(models.Model):
    """Model lưu trữ thông tin các models đã huấn luyện"""

    MODEL_TYPES = [
        ("hmm", "Hidden Markov Model"),
        ("lstm", "LSTM Neural Network"),
        ("markov", "Simple Markov Chain"),
    ]

    model_type = models.CharField("Loại Model", max_length=20, choices=MODEL_TYPES)
    file_path = models.CharField("Đường dẫn file", max_length=500)
    metadata = models.JSONField("Metadata", default=dict, blank=True)
    accuracy = models.FloatField("Độ chính xác", null=True, blank=True)
    training_data_size = models.IntegerField(
        "Kích thước dữ liệu huấn luyện", null=True, blank=True
    )
    is_active = models.BooleanField("Đang hoạt động", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PredictionModelManager()

    class Meta:
        db_table = "results_prediction_model"
        ordering = ["-created_at"]
        verbose_name = "Prediction Model"
        verbose_name_plural = "Prediction Models"

    def __str__(self):
        return (
            f"{self.get_model_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"
        )

    def load_model(self):
        """Load model từ file"""
        if os.path.exists(self.file_path):
            with open(self.file_path, "rb") as f:
                return pickle.load(f)
        return None


class StatePredictionManager(models.Manager):
    def create_prediction(
        self,
        model_instance,
        current_state,
        predicted_state,
        confidence=None,
        metadata=None,
    ):
        """Tạo prediction mới"""
        return self.create(
            model=model_instance,
            current_state=current_state,
            predicted_state=predicted_state,
            confidence=confidence,
            metadata=metadata or {},
            prediction_date=timezone.now().date(),
        )

    def get_recent_predictions(self, days=7):
        """Lấy predictions gần đây"""
        from_date = timezone.now().date() - timedelta(days=days)
        return self.filter(prediction_date__gte=from_date).order_by("-created_at")


class StatePrediction(models.Model):
    """Model lưu trữ các dự đoán state"""

    model = models.ForeignKey(
        PredictionModel, on_delete=models.CASCADE, related_name="predictions"
    )
    current_state = models.CharField("State hiện tại", max_length=10)
    predicted_state = models.CharField("State dự đoán", max_length=10)
    confidence = models.FloatField("Độ tin cậy", null=True, blank=True)
    metadata = models.JSONField("Metadata", default=dict, blank=True)
    prediction_date = models.DateField("Ngày dự đoán", db_index=True)
    actual_state = models.CharField(
        "State thực tế", max_length=10, null=True, blank=True
    )
    is_correct = models.BooleanField("Dự đoán đúng", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = StatePredictionManager()

    class Meta:
        db_table = "results_state_prediction"
        ordering = ["-created_at"]
        verbose_name = "State Prediction"
        verbose_name_plural = "State Predictions"

    def __str__(self):
        return (
            f"{self.current_state} -> {self.predicted_state} ({self.prediction_date})"
        )

    def check_accuracy(self):
        """Kiểm tra độ chính xác của dự đoán"""
        if self.actual_state:
            self.is_correct = self.predicted_state == self.actual_state
            self.save()
            return self.is_correct
        return None
