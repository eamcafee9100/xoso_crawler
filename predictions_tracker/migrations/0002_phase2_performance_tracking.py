# Generated migration for Phase 2 Performance Tracking models

import django.db.models.deletion
import django.utils.timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "predictions_tracker",
            "0001_initial",
        ),  # Adjust based on your latest migration
    ]

    operations = [
        # MethodPerformanceHistory table
        migrations.CreateModel(
            name="MethodPerformanceHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tracking_date",
                    models.DateField(db_index=True, verbose_name="Ngày theo dõi"),
                ),
                (
                    "predictions_made",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Số dự đoán đã thực hiện"
                    ),
                ),
                (
                    "hits_count",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Số dự đoán trúng"
                    ),
                ),
                (
                    "accuracy_rate",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=5,
                        null=True,
                        validators=[MinValueValidator(0), MaxValueValidator(100)],
                        verbose_name="Tỷ lệ chính xác (%)",
                    ),
                ),
                (
                    "weighted_score",
                    models.DecimalField(
                        blank=True,
                        decimal_places=4,
                        max_digits=8,
                        null=True,
                        verbose_name="Điểm số có trọng số",
                    ),
                ),
                (
                    "market_conditions",
                    models.JSONField(
                        default=dict,
                        help_text="Lưu trữ thông tin về điều kiện thị trường khi dự đoán",
                        verbose_name="Điều kiện thị trường",
                    ),
                ),
                (
                    "performance_metadata",
                    models.JSONField(
                        default=dict,
                        help_text="Thông tin bổ sung về hiệu suất phương pháp",
                        verbose_name="Metadata hiệu suất",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Thời gian tạo"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Thời gian cập nhật"
                    ),
                ),
                (
                    "method",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="performance_history",
                        to="predictions_tracker.predictionmethod",
                        verbose_name="Phương pháp dự đoán",
                    ),
                ),
            ],
            options={
                "verbose_name": "Lịch sử hiệu suất phương pháp",
                "verbose_name_plural": "Lịch sử hiệu suất phương pháp",
            },
        ),
        # DynamicMethodWeights table
        migrations.CreateModel(
            name="DynamicMethodWeights",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "weight_value",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="Trọng số từ 0.0 đến 1.0",
                        max_digits=6,
                        validators=[MinValueValidator(0), MaxValueValidator(1)],
                        verbose_name="Giá trị trọng số",
                    ),
                ),
                (
                    "confidence_score",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Mức độ tin cậy của trọng số",
                        max_digits=5,
                        validators=[MinValueValidator(0), MaxValueValidator(100)],
                        verbose_name="Điểm tin cậy (%)",
                    ),
                ),
                (
                    "adjustment_reason",
                    models.TextField(
                        help_text="Giải thích tại sao trọng số được điều chỉnh",
                        verbose_name="Lý do điều chỉnh",
                    ),
                ),
                (
                    "effective_from",
                    models.DateField(
                        default=django.utils.timezone.now, verbose_name="Có hiệu lực từ"
                    ),
                ),
                (
                    "effective_to",
                    models.DateField(
                        blank=True, null=True, verbose_name="Có hiệu lực đến"
                    ),
                ),
                (
                    "created_by",
                    models.CharField(
                        default="system", max_length=50, verbose_name="Tạo bởi"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Thời gian tạo"
                    ),
                ),
                (
                    "method",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dynamic_weights",
                        to="predictions_tracker.predictionmethod",
                        verbose_name="Phương pháp dự đoán",
                    ),
                ),
            ],
            options={
                "verbose_name": "Trọng số động phương pháp",
                "verbose_name_plural": "Trọng số động phương pháp",
            },
        ),
        # MethodCorrelationMatrix table
        migrations.CreateModel(
            name="MethodCorrelationMatrix",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "correlation_coefficient",
                    models.DecimalField(
                        decimal_places=6,
                        help_text="Từ -1 (tương quan nghịch) đến 1 (tương quan thuận)",
                        max_digits=8,
                        validators=[MinValueValidator(-1), MaxValueValidator(1)],
                        verbose_name="Hệ số tương quan",
                    ),
                ),
                (
                    "statistical_significance",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="P-value của kiểm định tương quan",
                        max_digits=6,
                        validators=[MinValueValidator(0), MaxValueValidator(1)],
                        verbose_name="Mức ý nghĩa thống kê",
                    ),
                ),
                (
                    "sample_size",
                    models.PositiveIntegerField(
                        help_text="Số lượng quan sát được sử dụng trong tính toán",
                        verbose_name="Kích thước mẫu",
                    ),
                ),
                (
                    "calculation_date",
                    models.DateField(db_index=True, verbose_name="Ngày tính toán"),
                ),
                (
                    "time_period_days",
                    models.PositiveIntegerField(
                        help_text="Số ngày được sử dụng để tính tương quan",
                        verbose_name="Khoảng thời gian (ngày)",
                    ),
                ),
                (
                    "analysis_metadata",
                    models.JSONField(
                        default=dict,
                        help_text="Thông tin bổ sung về phân tích tương quan",
                        verbose_name="Metadata phân tích",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Thời gian tạo"
                    ),
                ),
                (
                    "method_a",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="correlations_as_a",
                        to="predictions_tracker.predictionmethod",
                        verbose_name="Phương pháp A",
                    ),
                ),
                (
                    "method_b",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="correlations_as_b",
                        to="predictions_tracker.predictionmethod",
                        verbose_name="Phương pháp B",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ma trận tương quan phương pháp",
                "verbose_name_plural": "Ma trận tương quan phương pháp",
            },
        ),
        # PerformanceAlerts table
        migrations.CreateModel(
            name="PerformanceAlerts",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "alert_type",
                    models.CharField(
                        choices=[
                            ("accuracy_drop", "Accuracy Drop"),
                            ("weight_change", "Weight Change"),
                            ("correlation_shift", "Correlation Shift"),
                            ("performance_spike", "Performance Spike"),
                            ("method_failure", "Method Failure"),
                            ("system_anomaly", "System Anomaly"),
                        ],
                        db_index=True,
                        max_length=50,
                        verbose_name="Loại cảnh báo",
                    ),
                ),
                (
                    "severity_level",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("medium", "Medium"),
                            ("high", "High"),
                            ("critical", "Critical"),
                        ],
                        db_index=True,
                        max_length=20,
                        verbose_name="Mức độ nghiêm trọng",
                    ),
                ),
                ("message", models.TextField(verbose_name="Thông điệp cảnh báo")),
                (
                    "alert_data",
                    models.JSONField(
                        default=dict,
                        help_text="Chi tiết bổ sung về cảnh báo",
                        verbose_name="Dữ liệu cảnh báo",
                    ),
                ),
                (
                    "triggered_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Thời gian kích hoạt"
                    ),
                ),
                (
                    "acknowledged_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Thời gian xác nhận"
                    ),
                ),
                (
                    "acknowledged_by",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        verbose_name="Xác nhận bởi",
                    ),
                ),
                (
                    "resolved_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Thời gian giải quyết"
                    ),
                ),
                (
                    "resolved_by",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        verbose_name="Giải quyết bởi",
                    ),
                ),
                (
                    "method",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="alerts",
                        to="predictions_tracker.predictionmethod",
                        verbose_name="Phương pháp liên quan",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cảnh báo hiệu suất",
                "verbose_name_plural": "Cảnh báo hiệu suất",
            },
        ),
        # Add constraints and indexes
        migrations.AddConstraint(
            model_name="methodperformancehistory",
            constraint=models.UniqueConstraint(
                fields=("method", "tracking_date"), name="unique_method_tracking_date"
            ),
        ),
        migrations.AddConstraint(
            model_name="methodcorrelationmatrix",
            constraint=models.UniqueConstraint(
                fields=("method_a", "method_b", "calculation_date"),
                name="unique_method_correlation_date",
            ),
        ),
        # Add database indexes for performance
        migrations.AddIndex(
            model_name="methodperformancehistory",
            index=models.Index(
                fields=["tracking_date", "accuracy_rate"], name="perf_hist_date_acc_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="methodperformancehistory",
            index=models.Index(
                fields=["method", "tracking_date"], name="perf_hist_method_date_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="dynamicmethodweights",
            index=models.Index(
                fields=["method", "effective_from", "effective_to"],
                name="dyn_weights_method_period_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="dynamicmethodweights",
            index=models.Index(
                fields=["effective_from", "effective_to"], name="dyn_weights_period_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="methodcorrelationmatrix",
            index=models.Index(
                fields=["calculation_date", "correlation_coefficient"],
                name="corr_matrix_date_coeff_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="methodcorrelationmatrix",
            index=models.Index(
                fields=["method_a", "method_b"], name="corr_matrix_methods_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="performancealerts",
            index=models.Index(
                fields=["alert_type", "severity_level"], name="alerts_type_severity_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="performancealerts",
            index=models.Index(
                fields=["triggered_at", "severity_level"],
                name="alerts_time_severity_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="performancealerts",
            index=models.Index(
                fields=["method", "alert_type"], name="alerts_method_type_idx"
            ),
        ),
    ]
