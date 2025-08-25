# Tính năng xem 30 ngày gần đây - Monthly Report

## 📋 Tổng quan
Tính năng này bổ sung thêm tùy chọn xem báo cáo dự đoán cho **30 ngày gần đây** bên cạnh chế độ xem theo tháng hiện tại.

## 🎯 Mục tiêu
- Cho phép người dùng xem performance của các phương pháp dự đoán trong 30 ngày trước đó
- Không bị giới hạn bởi ranh giới tháng (tháng trước/tháng này)
- Giúp phân tích xu hướng gần đây một cách linh hoạt hơn

## 🛠️ Thay đổi thực hiện

### 1. View (predictions_tracker/views.py)
```python
class MonthlyPredictionReportView(TemplateView):
    def get_context_data(self, **kwargs):
        # ✅ THÊM SUPPORT CHO VIEW MODE
        view_mode = self.request.GET.get("view_mode", "monthly")
        
        if view_mode == "last30days":
            # 30 ngày gần đây
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=29)
        else:
            # Theo tháng (mặc định)
            year = int(self.request.GET.get("year", timezone.now().year))
            month = int(self.request.GET.get("month", timezone.now().month))
            # ... logic tháng
```

### 2. Template (monthly_report.html)
- **View Mode Switcher**: Toggle buttons để chuyển đổi chế độ
- **Dynamic Title**: Tiêu đề thay đổi theo chế độ hiện tại
- **Conditional Navigation**: Navigation tháng chỉ hiện khi ở chế độ monthly
- **Info Alerts**: Hiển thị thông tin về khoảng thời gian hiện tại

### 3. Helper Functions
- `_get_method_stats_by_date_range()`: Tính thống kê theo date range
- `_get_navigation_data()`: Cập nhật để hỗ trợ view_mode

## 🔗 URL Patterns

| Chế độ | URL | Mô tả |
|--------|-----|-------|
| Theo tháng | `/monthly-report/?view_mode=monthly&year=2025&month=8` | Xem tháng 8/2025 |
| 30 ngày gần đây | `/monthly-report/?view_mode=last30days` | Xem 30 ngày trước từ hôm nay |
| Mặc định | `/monthly-report/` | Xem tháng hiện tại |

## 🎨 UI Components

### View Mode Switcher
```html
<div class="btn-group me-3" role="group">
    <a href="?view_mode=monthly" 
       class="btn btn-primary">
        <i class="fas fa-calendar-alt"></i> Theo tháng
    </a>
    <a href="?view_mode=last30days" 
       class="btn btn-outline-primary">
        <i class="fas fa-clock"></i> 30 ngày gần đây
    </a>
</div>
```

### Dynamic Info Alert
```html
{% if view_mode == 'last30days' %}
<div class="alert alert-info mb-4">
    <strong>Chế độ xem: 30 ngày gần đây</strong><br>
    <small>Hiển thị dữ liệu từ {{ start_date|date:"d/m/Y" }} đến {{ end_date|date:"d/m/Y" }}</small>
</div>
{% endif %}
```

## 📊 Logic tính toán

### Chế độ Monthly
```python
start_date = date(year, month, 1)
last_day = calendar.monthrange(year, month)[1] 
end_date = date(year, month, last_day)
```

### Chế độ Last 30 Days
```python
end_date = timezone.now().date()
start_date = end_date - timedelta(days=29)  # 30 ngày total
```

## ✅ Backward Compatibility
- URLs cũ vẫn hoạt động bình thường
- Mặc định sử dụng chế độ monthly
- Tất cả logic và template tags hiện tại được giữ nguyên

## 🧪 Testing
Đã test:
- ✅ Date logic calculation
- ✅ URL parameter handling  
- ✅ Template syntax
- ✅ View mode detection
- ✅ Navigation conditional display

## 🚀 Deployment Notes
1. Chỉ cần update 2 files: `views.py` và `monthly_report.html`
2. Không cần migration database
3. Không phá vỡ tính năng hiện tại
4. Responsive design được giữ nguyên

## 💡 Future Enhancements
- Thêm tùy chọn custom date range
- Export data cho khoảng thời gian tùy chọn
- So sánh hiệu suất giữa các khoảng thời gian
