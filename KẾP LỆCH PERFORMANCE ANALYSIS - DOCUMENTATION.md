# 🎯 Kép Lệch Performance Analysis System - Documentation

## 📋 Tổng quan

Hệ thống phân tích hiệu suất và khả năng sinh lời của phương pháp Kép Lệch trong dự đoán xổ số miền Bắc. System này cung cấp phân tích toàn diện dựa trên dữ liệu lịch sử 2 năm, bao gồm:

- ✅ Tỷ lệ thành công dự đoán
- 💰 Phân tích ROI và lợi nhuận
- ⚠️ Đánh giá rủi ro chi tiết  
- 💡 Khuyến nghị chiến lược
- 📊 Thống kê theo tuần/tháng/mùa
- 🎯 So sánh hiệu suất với thực tế

## 🏗️ Kiến trúc hệ thống

### Core Components

1. **KepLechPerformanceAnalyzer** (`kep_lech_performance_analyzer.py`)
   - Engine chính thực hiện phân tích
   - Xử lý dữ liệu và tính toán hiệu suất
   - Generate predictions và validation

2. **Views** (`kep_lech_views.py`)
   - KepLechPerformanceView: Web interface
   - KepLechPerformanceAPIView: RESTful API
   - KepLechQuickReportView: Báo cáo nhanh
   - KepLechBacktestView: Backtest tùy chỉnh

3. **Templates**
   - `kep_lech_dashboard.html`: Dashboard chính
   - `kep_lech_performance_analysis.html`: Báo cáo chi tiết

4. **Management Commands**
   - `kep_lech_analysis.py`: Command line interface

## 🎯 Bộ số Kép Lệch

### Kép Dương (40 số)
```
05, 50, 16, 61, 27, 72, 38, 83, 49, 94,
06, 60, 07, 70, 08, 80, 09, 90, 15, 51,
26, 62, 37, 73, 48, 84, 59, 95, 13, 31,
24, 42, 35, 53, 46, 64, 57, 75, 68, 86
```

### Kép Âm (10 số)
```
07, 70, 14, 41, 29, 92, 36, 63, 58, 85
```

### Sát Kép (24 số)
```
04, 40, 06, 60, 15, 51, 95, 59, 17, 71,
14, 41, 28, 82, 26, 62, 37, 73, 36, 63,
39, 93, 48, 84
```

## 🔍 Phương pháp phân tích

### 1. Weekly Pattern Analysis
- Phân tích patterns Kép Lệch theo tuần
- Thống kê tần suất xuất hiện từng loại
- Xác định trends và cycles

### 2. Prediction Generation
Dựa trên logic từ `keplech.py`:
- **Rule 1**: Kép xuất hiện ít → Khuyến nghị đánh
- **Rule 2**: Kép xuất hiện nhiều → Cảnh báo tránh
- **Rule 3**: Không có kép → Tập trung kép Âm
- **Rule 4**: Dựa vào số đầu giải ĐB thứ 2
- **Rule 5**: Patterns theo ngày trong tuần

### 3. Performance Validation
- So sánh dự đoán với kết quả tuần tiếp theo
- Tính tỷ lệ thành công (success rate)
- Phân loại: Success / Partial / Failed

### 4. Financial Analysis
- Tính toán ROI dựa trên investment simulation
- Phân tích risk/reward ratio
- Calculate metrics: Sharpe ratio, Max drawdown, Win rate

### 5. Risk Assessment
- Đánh giá volatility và stability
- Scenario analysis (Best/Realistic/Worst case)
- Capital requirements và risk management

## 🌐 API Endpoints

### GET `/pre-lokhung/api/kep-lech-data-status/`
Kiểm tra tình trạng dữ liệu có sẵn

**Response:**
```json
{
  "success": true,
  "data_status": {
    "total_results": 1500,
    "date_range": {
      "start": "2023-01-01",
      "end": "2025-07-30",
      "total_days": 945
    },
    "possible_weeks": 135,
    "recommended_analysis_periods": [...]
  }
}
```

### GET `/pre-lokhung/api/kep-lech-quick-report/`
Báo cáo nhanh 30 ngày gần nhất

### GET `/pre-lokhung/api/kep-lech-performance/?days=730`
Phân tích đầy đủ với parameters:
- `days`: Số ngày phân tích (30-1095)
- `refresh`: Force refresh cache (true/false)
- `format`: Output format (full/summary/raw)

### POST `/pre-lokhung/api/kep-lech-backtest/`
Backtest với tham số tùy chỉnh

**Request Body:**
```json
{
  "start_days": 365,
  "investment_amount": 500000,
  "strategy_config": {
    "confidence_threshold": 0.8,
    "max_weekly_investment_ratio": 0.05
  }
}
```

### GET `/pre-lokhung/api/kep-lech-clear-cache/`
Xóa cache để refresh dữ liệu

## 🖥️ Web Interface

### Dashboard
**URL:** `/pre-lokhung/kep-lech-dashboard/`
- Giao diện tổng quan với quick actions
- Form tùy chỉnh thời gian phân tích
- Links đến các tính năng chính

### Performance Analysis
**URL:** `/pre-lokhung/kep-lech-performance/`
- Báo cáo chi tiết với visualization
- Tabs: Overview, Weekly Details, Profit Analysis, Risk, Recommendations
- Responsive design, mobile-friendly

## 🎮 Command Line Usage

### Basic Analysis
```bash
python manage.py kep_lech_analysis --days 365
```

### Advanced Options  
```bash
python manage.py kep_lech_analysis \
    --days 730 \
    --output-file analysis_result.json \
    --format summary \
    --verbose \
    --clear-cache
```

**Parameters:**
- `--days`: Số ngày phân tích (default: 730)
- `--output-file`: Save kết quả ra file JSON
- `--format`: full/summary/simple (default: full)
- `--clear-cache`: Xóa cache trước khi chạy
- `--verbose`: Hiển thị chi tiết

## 📊 Output Format

### Summary Statistics
```json
{
  "total_weeks_analyzed": 104,
  "prediction_accuracy": {
    "success_rate": 45.2,
    "successful_weeks": 47,
    "failed_weeks": 57
  },
  "financial_performance": {
    "total_roi": 12.5,
    "winning_weeks": 52,
    "losing_weeks": 45,
    "average_weekly_return": 2.1
  },
  "risk_assessment": {
    "risk_level": "medium",
    "volatility": 25.8,
    "max_drawdown": -85000,
    "sharpe_ratio": 0.48
  }
}
```

### Strategy Recommendations
```json
{
  "overall_verdict": "proceed_with_caution",
  "investment_strategy": [
    "Mức đầu tư khuyến nghị: 2-3% tổng vốn",
    "Tỷ lệ thành công trung bình: 45.2%"
  ],
  "risk_management": [
    "Đặt stop-loss ở mức -15% vốn đầu tư",
    "Chốt lời khi đạt +25% lợi nhuận"
  ]
}
```

## ⚙️ Configuration

### Analysis Config
```python
ANALYSIS_CONFIG = {
    'analysis_period_years': 2,
    'min_bet_amount': 1000,  # VND
    'payout_ratio': 70,      # 70 lần
    'commission_rate': 0.02, # 2%
    'risk_management': {
        'max_weekly_investment_ratio': 0.03,
        'stop_loss_ratio': 0.15,
        'take_profit_ratio': 0.25,
    }
}
```

### Cache Settings
- Cache timeout: 1 hour (3600 seconds)
- Cache keys: `kep_lech_analysis_{days}`
- Automatic cache invalidation

## 🚀 Deployment Notes

### Production Setup
1. Ensure proper Django cache backend (Redis recommended)
2. Set up proper logging configuration
3. Configure static files serving
4. Set appropriate timeouts for long-running analysis

### Performance Optimization
- Use database indexing on `ngay` field
- Implement pagination for large datasets
- Consider background task processing for heavy analysis

### Monitoring
- Track analysis execution time
- Monitor cache hit/miss ratios
- Log prediction accuracy over time

## 🔧 Troubleshooting

### Common Issues

**1. No data available**
```
Error: Không có dữ liệu trong khoảng thời gian phân tích
Solution: Kiểm tra KetQuaXoSo model có dữ liệu
```

**2. Analysis timeout**
```
Error: Analysis takes too long
Solution: Reduce analysis period hoặc optimize queries
```

**3. Memory issues**
```
Error: Out of memory during large analysis
Solution: Use iterator() cho large datasets
```

### Debug Mode
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Future Enhancements

### Planned Features
- [ ] Real-time analysis với WebSocket
- [ ] Machine Learning integration
- [ ] Advanced visualization với Chart.js
- [ ] Export to PDF/Excel
- [ ] Mobile app API
- [ ] Telegram/Discord bot integration

### Performance Improvements
- [ ] Background task processing với Celery
- [ ] Database optimization
- [ ] Caching layer improvements
- [ ] API rate limiting

## ⚠️ Important Notes

### Disclaimer
- Hệ thống chỉ mang tính chất tham khảo
- Không đảm bảo kết quả đầu tư trong tương lai
- Luôn đầu tư có trách nhiệm

### Data Requirements
- Cần ít nhất 30 ngày dữ liệu để phân tích
- Khuyến nghị 6+ tháng cho kết quả tin cậy
- Dữ liệu phải complete và accurate

### Risk Warning
- Kép Lệch chỉ chiếm ~12-15% tổng kết quả
- Không nên phụ thuộc hoàn toàn vào một phương pháp
- Luôn áp dụng money management nghiêm ngặt

---

**Last Updated:** July 30, 2025  
**Version:** 2.0.0  
**Author:** AI Assistant  
**Contact:** Via GitHub Issues
