# Hướng Dẫn Sử Dụng Hệ Thống Dự Đoán Cải Tiến

## Tổng Quan

Hệ thống dự đoán cải tiến giải quyết tất cả các điểm yếu được xác định trong phân tích hệ thống, bao gồm:

### ✅ Các Cải Tiến Chính

1. **🔬 Khung Kiểm Tra Khoa Học**
   - Backtesting Framework: Kiểm tra hiệu suất trên dữ liệu lịch sử
   - Statistical Significance Testing: Kiểm tra tính có ý nghĩa thống kê
   - Control Group Analysis: So sánh với nhóm đối chứng ngẫu nhiên

2. **📊 Định Lượng Độ Không Chắc Chắn**
   - Confidence Intervals: Khoảng tin cậy cho dự đoán
   - Individual Number Confidence: Độ tin cậy cho từng số
   - Risk Assessment: Đánh giá rủi ro và khuyến nghị

3. **🤖 Tối Ưu Hóa Thích Ứng**
   - Dynamic Weight Adjustment: Điều chỉnh trọng số dựa trên hiệu suất
   - Performance-based Learning: Học từ kết quả thực tế
   - Method Performance Tracking: Theo dõi hiệu suất từng phương pháp

4. **📈 Giám Sát Hiệu Suất Thời Gian Thực**
   - Real-time Performance Monitoring: Giám sát hiệu suất liên tục
   - Alert System: Hệ thống cảnh báo tự động
   - Performance Dashboard: Bảng điều khiển hiệu suất

## Cài Đặt và Khởi Tạo

### 1. Import Hệ Thống

```python
from ml_validation.enhanced_system import EnhancedPredictionSystem
from ml_validation.backtesting import BacktestingFramework
from ml_validation.statistical_tests import StatisticalValidator
from ml_validation.confidence_intervals import ConfidenceCalculator
from ml_validation.adaptive_weights import AdaptiveWeightOptimizer
from ml_validation.performance_monitor import PerformanceMonitor
```

### 2. Khởi Tạo Hệ Thống

```python
# Khởi tạo hệ thống với monitoring
system = EnhancedPredictionSystem(enable_monitoring=True)

# Khởi tạo với dữ liệu lịch sử
system.initialize_system(historical_days=100)
```

## Sử Dụng Hệ Thống

### 1. Tạo Dự Đoán Cải Tiến

```python
from datetime import datetime, timedelta

# Ngày dự đoán
target_date = datetime.now() + timedelta(days=1)

# Tạo dự đoán với validation đầy đủ
prediction_result = system.make_enhanced_prediction(
    target_date=target_date,
    include_validation=True,
    confidence_level=0.95
)

# Kết quả dự đoán
print(f"Số dự đoán: {prediction_result.predicted_numbers}")
print(f"Độ tin cậy tổng thể: {prediction_result.confidence_metrics.overall_confidence:.1f}%")
print(f"Số lần trúng dự kiến: {prediction_result.expected_hits[0]:.1f} - {prediction_result.expected_hits[1]:.1f}")
print(f"Mức độ không chắc chắn: {prediction_result.uncertainty_level}")
print(f"Khuyến nghị: {prediction_result.recommendation}")
```

### 2. Cập Nhật Với Kết Quả Thực Tế

```python
# Khi có kết quả thực tế
actual_numbers = [12, 23, 34, 45, 56, 67, 78, 89, 90, 11, 22, 33, 44, 55, 66, 77, 88, 99, 00, 13, 24, 35, 46, 57, 68, 79, 80]

# Cập nhật hệ thống
system.update_with_actual_result(
    prediction_result=prediction_result,
    actual_numbers=actual_numbers,
    prediction_date=target_date
)
```

### 3. Chạy Validation Toàn Diện

```python
# Chạy validation cho 30 ngày gần nhất
validation_results = system.run_comprehensive_validation(days_back=30)

# Kết quả validation
print("Kết quả Validation:")
print(f"Sức khỏe hệ thống: {validation_results['system_health']['score']}/100")

if 'backtesting' in validation_results:
    bt = validation_results['backtesting']['overview']
    print(f"Backtesting - Độ chính xác TB: {bt['average_accuracy']}")
    print(f"Tỉ lệ trúng: {bt['hit_rate']}")

if 'statistical_significance' in validation_results:
    stats = validation_results['statistical_significance']
    print(f"Có ý nghĩa thống kê: {stats['significance_test']['is_significant']}")
    print(f"Cải thiện so với ngẫu nhiên: {stats['control_comparison']['improvement']:.3f}")
```

## Tính Năng Chi Tiết

### 1. Confidence Intervals (Khoảng Tin Cậy)

```python
# Độ tin cậy từng số
individual_confidences = prediction_result.confidence_metrics.individual_confidences
top_confident = sorted(individual_confidences.items(), key=lambda x: x[1], reverse=True)[:5]

print("Top 5 số có độ tin cậy cao nhất:")
for number, confidence in top_confident:
    print(f"  Số {number:02d}: {confidence:.1f}%")

# Metrics tin cậy
metrics = prediction_result.confidence_metrics.confidence_metrics
print(f"Khoảng tin cậy 95%: [{metrics.confidence_interval[0]:.1f}, {metrics.confidence_interval[1]:.1f}]")
print(f"Điểm tin cậy: {metrics.reliability_score:.1f}%")
```

### 2. Adaptive Weight Optimization

```python
# Xem trọng số hiện tại
current_weights = system.weight_optimizer.get_current_weights()
print("Trọng số hiện tại:")
for method, weight in current_weights.items():
    print(f"  {method}: {weight:.3f} ({weight*100:.1f}%)")

# Xem hiệu suất các phương pháp
performance_summary = system.weight_optimizer.get_performance_summary()
print(f"Số lần điều chỉnh trọng số: {performance_summary['adaptation_count']}")
print(f"Xu hướng hiệu suất: {performance_summary['performance_trend']}")
```

### 3. Performance Monitoring

```python
# Lấy dữ liệu dashboard
if system.performance_monitor:
    dashboard_data = system.performance_monitor.get_dashboard_data()
    
    # Trạng thái hiện tại
    current = dashboard_data['current_status']
    print(f"Độ chính xác hiện tại: {current['accuracy']:.3f}")
    print(f"Thời gian phản hồi: {current['response_time']:.2f}s")
    print(f"Sử dụng bộ nhớ: {current['memory_usage']:.1f}MB")
    
    # Cảnh báo gần đây
    recent_alerts = system.performance_monitor.get_recent_alerts(hours=24)
    if recent_alerts:
        print(f"Có {len(recent_alerts)} cảnh báo trong 24h qua")
        for alert in recent_alerts[-3:]:
            print(f"  [{alert.level.value.upper()}] {alert.message}")
```

### 4. Backtesting Framework

```python
from datetime import datetime, timedelta

# Chạy backtesting cho khoảng thời gian cụ thể
start_date = datetime.now() - timedelta(days=60)
end_date = datetime.now() - timedelta(days=1)

if system.backtesting_framework:
    backtest_summary = system.backtesting_framework.run_historical_backtest(
        start_date=start_date,
        end_date=end_date,
        prediction_methods=['hybrid', 'statistical', 'frequency', 'cycle']
    )
    
    print("Kết quả Backtesting:")
    print(f"Tổng số test: {backtest_summary.total_tests}")
    print(f"Độ chính xác TB: {backtest_summary.avg_accuracy:.3f}")
    print(f"Tỉ lệ trúng: {backtest_summary.hit_rate:.3f}")
    print(f"Tương quan độ tin cậy: {backtest_summary.confidence_correlation:.3f}")
    
    # Hiệu suất từng phương pháp
    print("Hiệu suất từng phương pháp:")
    for method, performance in backtest_summary.method_performance.items():
        print(f"  {method}: {performance:.3f}")
```

## Tích Hợp Django

### 1. Views Integration

```python
# Trong views.py
from enhanced_integration import enhanced_predict_view, EnhancedPredictionAPIView

# Thay thế view cũ
def predict_view(request):
    return enhanced_predict_view(request)
```

### 2. URL Configuration

```python
# Trong urls.py
from enhanced_integration import EnhancedPredictionAPIView, ValidationReportView, performance_dashboard_view

urlpatterns = [
    path('predict/', enhanced_predict_view, name='enhanced_predict'),
    path('api/enhanced-prediction/', EnhancedPredictionAPIView.as_view(), name='enhanced_prediction_api'),
    path('validation-report/', ValidationReportView.as_view(), name='validation_report'),
    path('performance-dashboard/', performance_dashboard_view, name='performance_dashboard'),
]
```

### 3. Template Context

```python
# Trong settings.py
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'enhanced_integration.enhanced_system_context',
            ],
        },
    },
]
```

## Template Usage

### 1. Enhanced Prediction Display

```html
<!-- Trong template -->
{% load enhanced_tags %}

<div class="prediction-result">
    <h3>Dự Đoán Cải Tiến</h3>
    
    <!-- Números dự đoán -->
    <div class="predicted-numbers">
        {% for number in enhanced_prediction.predicted_numbers %}
        <span class="badge bg-primary">{{ number|stringformat:"02d" }}</span>
        {% endfor %}
    </div>
    
    <!-- Độ tin cậy -->
    <div class="confidence-info">
        <h4>Thông Tin Độ Tin Cậy</h4>
        <p>Độ tin cậy tổng thể: 
            <span class="badge bg-{{ enhanced_prediction.uncertainty_level|confidence_class }}">
                {{ enhanced_prediction.overall_confidence|floatformat:1 }}%
                {{ enhanced_prediction.uncertainty_level|confidence_icon }}
            </span>
        </p>
        <p>Số trúng dự kiến: {{ enhanced_prediction.expected_hits.0|floatformat:1 }} - {{ enhanced_prediction.expected_hits.1|floatformat:1 }}</p>
    </div>
    
    <!-- Khuyến nghị -->
    <div class="recommendation">
        <h4>Khuyến Nghị</h4>
        <p>{{ enhanced_prediction.recommendation }}</p>
    </div>
    
    <!-- Trọng số phương pháp -->
    <div class="method-weights">
        <h4>Trọng Số Phương Pháp</h4>
        {% for method, weight in weight_optimization.items %}
        <div class="weight-bar">
            <span>{{ method }}: {{ weight|floatformat:3 }}</span>
            <div class="progress">
                <div class="progress-bar" style="width: {{ weight|floatformat:1 }}%"></div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
```

### 2. System Health Display

```html
<!-- Sức khỏe hệ thống -->
<div class="system-health">
    <h4>Sức Khỏe Hệ Thống</h4>
    {% system_health_badge system_health %}
    
    {% if system_health.issues %}
    <div class="alert alert-warning">
        <h5>Vấn Đề Phát Hiện:</h5>
        <ul>
        {% for issue in system_health.issues %}
            <li>{{ issue }}</li>
        {% endfor %}
        </ul>
    </div>
    {% endif %}
</div>
```

## Báo Cáo và Xuất Dữ Liệu

### 1. Xuất Báo Cáo Hệ Thống

```python
# Xuất báo cáo toàn diện
report_file = f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
system.export_system_report(report_file)

print(f"Báo cáo đã được xuất ra: {report_file}")
```

### 2. Xuất Dữ Liệu Monitoring

```python
# Xuất dữ liệu monitoring
if system.performance_monitor:
    monitoring_file = f"monitoring_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    system.performance_monitor.export_monitoring_data(monitoring_file, days=30)
    
    print(f"Dữ liệu monitoring đã được xuất ra: {monitoring_file}")
```

## Best Practices

### 1. Khởi Tạo Hệ Thống

```python
# Khởi tạo với đủ dữ liệu lịch sử
system.initialize_system(historical_days=100)  # Tối thiểu 60 ngày

# Kiểm tra khởi tạo thành công
if system.is_initialized:
    print("✅ Hệ thống đã sẵn sàng")
else:
    print("❌ Hệ thống chưa khởi tạo thành công")
```

### 2. Xử Lý Lỗi

```python
try:
    prediction_result = system.make_enhanced_prediction(target_date)
    
    if prediction_result.performance_score < 40:
        print("⚠️ Cảnh báo: Điểm hiệu suất thấp")
        print(f"Khuyến nghị: {prediction_result.recommendation}")
        
except Exception as e:
    print(f"❌ Lỗi dự đoán: {e}")
    # Sử dụng fallback method
```

### 3. Giám Sát Liên Tục

```python
# Đăng ký callback cho alerts
def handle_alert(alert):
    print(f"🚨 Cảnh báo [{alert.level.value}]: {alert.message}")
    
    if alert.level == AlertLevel.CRITICAL:
        # Thực hiện hành động khẩn cấp
        print("Thực hiện hành động khẩn cấp...")

system.performance_monitor.subscribe_to_alerts(handle_alert)
```

### 4. Cập Nhật Thường Xuyên

```python
# Cập nhật kết quả thực tế ngay khi có
def update_daily_results():
    # Lấy kết quả mới nhất
    latest_result = get_latest_lottery_result()
    
    if latest_result:
        # Tìm prediction tương ứng
        for prediction_data in pending_predictions:
            if prediction_data['date'] == latest_result.date:
                system.update_with_actual_result(
                    prediction_data['result'],
                    latest_result.numbers,
                    latest_result.date
                )
                break

# Chạy hàng ngày
update_daily_results()
```

## Troubleshooting

### 1. Lỗi Khởi Tạo

```python
# Kiểm tra Django models
try:
    from results.models import KetQuaXoSo
    print("✅ Django models có sẵn")
except ImportError:
    print("❌ Django models không tìm thấy - chạy trong test mode")
```

### 2. Lỗi Memory

```python
# Giới hạn memory monitoring
config = MonitoringConfig()
config.memory_threshold = 1000.0  # 1GB
system.performance_monitor.config = config
```

### 3. Lỗi Performance

```python
# Điều chỉnh threshold
config = MonitoringConfig()
config.accuracy_threshold = 0.10  # Giảm ngưỡng accuracy
config.response_time_threshold = 10.0  # Tăng ngưỡng response time
```

## Kết Luận

Hệ thống dự đoán cải tiến giải quyết hoàn toàn các điểm yếu được xác định:

- ✅ **Validation Framework**: Backtesting + Statistical tests
- ✅ **Statistical Rigor**: Significance testing + Control groups  
- ✅ **Bias Mitigation**: Multiple testing correction + Validation sets
- ✅ **Technical Robustness**: Monitoring + Alerts + Adaptive optimization

Hệ thống này cung cấp:
- Dự đoán có độ tin cậy cao với uncertainty quantification
- Validation khoa học nghiêm ngặt
- Tối ưu hóa thích ứng dựa trên hiệu suất thực tế
- Giám sát và cảnh báo thời gian thực
- Báo cáo toàn diện và insights chuyên sâu
