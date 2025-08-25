# Enhanced Prediction System - Quick Start Guide

## 🚀 Bắt đầu nhanh

Enhanced Prediction System đã được cài đặt thành công! Đây là hướng dẫn nhanh để bắt đầu sử dụng.

## ✅ Kiểm tra trạng thái hệ thống

```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Kiểm tra trạng thái hệ thống
python manage.py enhanced_system --action=status
```

## 🔧 Khởi tạo hệ thống

```bash
# Khởi tạo hệ thống với dữ liệu thực
python manage.py enhanced_system --action=initialize

# Hoặc force initialize nếu có vấn đề
python manage.py enhanced_system --action=initialize --force
```

## 📊 Kiểm tra sức khỏe hệ thống

```bash
# Validate toàn bộ hệ thống
python manage.py enhanced_system --action=validate

# Validate với output chi tiết
python manage.py enhanced_system --action=validate --verbose
```

## 🎯 Sử dụng API

### 1. Khởi động Django server
```bash
python manage.py runserver
```

### 2. Truy cập web interface
- **Main Interface**: http://localhost:8000/enhanced/enhanced-prediction/
- **Monitoring Dashboard**: http://localhost:8000/enhanced/monitoring-dashboard/
- **System Health**: http://localhost:8000/enhanced/system-health/

### 3. API Endpoints

#### Tạo prediction mới
```bash
curl -X POST http://localhost:8000/enhanced/api/enhanced-prediction/ \
  -H "Content-Type: application/json" \
  -d '{"target_date": "2025-08-02"}'
```

#### Lấy prediction cho ngày cụ thể
```bash
curl "http://localhost:8000/enhanced/api/enhanced-prediction/?date=2025-08-02"
```

#### Kiểm tra system health
```bash
curl http://localhost:8000/enhanced/system-health/
```

## 📈 Monitoring & Management

### Xem dashboard monitoring
```bash
# Mở browser và truy cập:
http://localhost:8000/enhanced/monitoring-dashboard/
```

### Backup hệ thống
```bash
python manage.py enhanced_system --action=backup
```

### Reset hệ thống (nếu cần)
```bash
python manage.py enhanced_system --action=reset --force
```

## 🔍 Troubleshooting

### Lỗi thường gặp:

1. **Unknown command: 'enhanced_system'**
   - Đảm bảo đã activate virtual environment
   - Kiểm tra Django settings có include app 'results'

2. **Module not found errors**
   - Chạy: `python manage.py enhanced_system --action=setup --force`

3. **Insufficient data errors**
   - Cần ít nhất 100 records trong database
   - Hoặc dùng `--force` để bypass

4. **Weight validation errors**
   - Hệ thống sẽ tự động điều chỉnh, không cần thao tác

### Kiểm tra logs
```bash
# Xem logs chi tiết
python manage.py enhanced_system --action=validate --verbose
```

## 🎊 Tính năng chính

- ✅ **Real-time Prediction**: Dự đoán dựa trên dữ liệu thực
- 📊 **Statistical Validation**: Backtesting và confidence scoring
- 🔄 **Adaptive Learning**: Weights tự động optimize
- 📈 **Performance Monitoring**: Real-time dashboard
- 🛡️ **Production Ready**: Error handling và monitoring
- 🎯 **High Accuracy**: Các thuật toán tối ưu hóa

## 📚 Tài liệu đầy đủ

Xem thêm chi tiết trong:
- `ENHANCED_SYSTEM_PRODUCTION_GUIDE.md` - Hướng dẫn production deployment
- Web dashboard - Monitoring real-time
- API documentation - Trong production guide

## 🎉 Thành công!

Hệ thống đã sẵn sàng sử dụng! Truy cập web interface để bắt đầu tạo predictions.

**Happy Predicting! 🎲**
