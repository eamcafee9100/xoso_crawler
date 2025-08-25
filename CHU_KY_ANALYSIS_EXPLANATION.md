# 🔍 PHÂN TÍCH CHI TIẾT CƠ CHẾ DỰ ĐOÁN XSMB

## 🎯 **TỔNG QUAN HỆ THỐNG**

Hệ thống dự đoán XSMB sử dụng **3 thành phần chính**:
1. **Phân tích chu kỳ** (1, 3, 7, 14, 30 ngày)
2. **Machine Learning** (chỉ khi có ≥100 ngày data)
3. **Hot Pairs Analysis** (cặp số nóng)

---

## 📊 **1. PHÂN TÍCH CHU KỲ - NGUỒN GỐC & CƠ CHẾ**

### **🔍 A. Nguồn dữ liệu từ đâu?**
```python
# Trong predict_view (views.py dòng 470-473)
history_query = KetQuaXoSo.objects.filter(ngay__lt=selected_date).order_by("-ngay")[:30]
history = list(history_query)  # Lấy 30 ngày gần nhất

# Truyền vào HybridPredictor
result = predictor.predict(selected_date, history)
```

**Nguồn**: Database `KetQuaXoSo` - lấy **30 ngày gần nhất** trước ngày dự đoán

### **🔧 B. Cơ chế phân tích chu kỳ**
```python
# Trong hybrid_predictor.py - hàm analyze_cycles()
def analyze_cycles(self, history):
    cycle_days = {
        "1_ngay": 1,    # Chỉ ngày hôm trước
        "3_ngay": 3,    # 3 ngày gần nhất
        "7_ngay": 7,    # 1 tuần gần nhất
        "14_ngay": 14,  # 2 tuần gần nhất
        "30_ngay": 30,  # 1 tháng gần nhất
    }
    
    for name, days in cycle_days.items():
        cycle_history = history[:days]  # Lấy 'days' ngày gần nhất
        freq = defaultdict(int)
        
        # Đếm tần suất xuất hiện của từng số
        for day in cycle_history:
            numbers = day.get_all_2digit_numbers()  # Lấy tất cả số 2 digit từ giải
            for num in numbers:
                freq[num] += 1
        
        # Lấy top 10 số xuất hiện nhiều nhất
        top_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
```

### **📈 C. Ví dụ cụ thể:**
- **Chu kỳ 1 ngày**: Chỉ xem ngày hôm trước có những số nào
- **Chu kỳ 3 ngày**: Đếm số nào xuất hiện nhiều trong 3 ngày gần nhất
- **Chu kỳ 7 ngày**: Thống kê 7 ngày, số nào "hot" nhất
- **Chu kỳ 14 ngày**: Pattern 2 tuần
- **Chu kỳ 30 ngày**: Trend dài hạn 1 tháng

---

## 🎯 **2. CƠ CHẾ CHỌN 15 SỐ TOP DỰ ĐOÁN**

### **🔢 A. Hệ thống tính điểm (Scoring System)**
```python
# Trong predict() - hybrid_predictor.py
scores = defaultdict(float)

# BƯỚC 1: Điểm từ phân tích chu kỳ (70-85% trọng số)
for cycle_name, data in cycle_analysis.items():
    weight = self.cycle_weights.get(cycle_name, 0)
    
    # Điểm từ tần suất xuất hiện
    for num, cnt in data["top_frequency"]:
        scores[num] += cnt * weight
    
    # Bonus điểm cho chu kỳ ngắn (pattern liên tiếp)
    for num, cnt in data["one_day_cycle"]:
        scores[num] += cnt * weight * 1.5

# BƯỚC 2: Điểm từ ML (15% trọng số, chỉ khi ≥100 ngày)
if len(history) >= 100:
    ml_preds = self.predict_with_ml(history)
    for num, conf in ml_preds:
        scores[num] += conf * 0.15

# BƯỚC 3: Bonus điểm cho Hot Pairs (10% tăng cường)
for num in hot_numbers:
    if num in scores:
        scores[num] *= 1.1
```

### **⚖️ B. Trọng số chu kỳ (Cycle Weights)**
```python
self.cycle_weights = {
    "1_ngay": 0.35,   # 35% - Quan trọng nhất (pattern ngắn hạn)
    "3_ngay": 0.25,   # 25% - Trend 3 ngày
    "7_ngay": 0.20,   # 20% - Pattern tuần
    "14_ngay": 0.15,  # 15% - Trend 2 tuần
    "30_ngay": 0.05,  # 5%  - Background trend
}
```

**Logic**: Chu kỳ ngắn có trọng số cao hơn vì có tính dự đoán tốt hơn

### **🏆 C. Quá trình chọn 15 số cuối cùng**
```python
# Chuẩn hóa điểm số (0-100%)
max_score = max(scores.values()) if scores else 1
scored_numbers = [
    (num, (score / max_score) * 100) for num, score in scores.items()
]

# Sắp xếp theo điểm cao → thấp và lấy top 15
top_numbers = sorted(scored_numbers, key=lambda x: x[1], reverse=True)[:top_n]
```

---

## 📊 **3. CƠ CHẾ HIỂN THỊ TRONG TEMPLATE**

### **🎨 A. Dữ liệu truyền vào template**
```python
# Trong predict_view (views.py)
context.update({
    "predictions": {
        "numbers": result.get("predicted_numbers", []),  # Top 15 số với điểm
        "accuracy": round(accuracy, 2),
        "hot_pairs": result.get("hot_pairs", []),
    },
    "cycle_analysis": result.get("cycle_analysis", {}),  # Chi tiết từng chu kỳ
})
```

### **🎭 B. Hiển thị trong predict.html**
```html
<!-- Top 15 số dự đoán -->
{% for num, score in predictions.numbers %}
<tr>
    <td>{{ forloop.counter }}</td>
    <td>{{ num }}</td>
    <td>{{ score|floatformat:1 }}%</td>  <!-- Điểm tin cậy -->
    <td>{% if num in actual_result.get_all_2digit_numbers %}✓{% endif %}</td>
</tr>
{% endfor %}

<!-- Chi tiết từng chu kỳ -->
{% for cycle_name, cycle_data in cycle_analysis.items %}
<h4>Chu kỳ {{ cycle_name|cut:"_ngay"|title }} ngày</h4>
{% for number, freq in cycle_data.top_frequency %}
<span class="number-badge">{{ number }}</span>
{% endfor %}
{% endfor %}
```

---

## 🔬 **4. VÍ DỤ TÍNH TOÁN CỤ THỂ**

### **📝 Giả sử có data:**
- **Chu kỳ 1 ngày**: Số 12 xuất hiện 3 lần
- **Chu kỳ 3 ngày**: Số 12 xuất hiện 5 lần
- **Hot pairs**: Số 12 nằm trong cặp nóng

### **💻 Tính điểm cho số 12:**
```python
score_12 = 0

# Từ chu kỳ 1 ngày
score_12 += 3 * 0.35 = 1.05

# Từ chu kỳ 3 ngày
score_12 += 5 * 0.25 = 1.25

# Bonus hot pairs
score_12 *= 1.1 = (1.05 + 1.25) * 1.1 = 2.53

# Chuẩn hóa thành %
final_score = (2.53 / max_score) * 100
```

---

## 📈 **5. FLOW TỔNG QUAN**

```
1. Lấy 30 ngày data từ KetQuaXoSo
                ↓
2. Phân tích 5 chu kỳ (1,3,7,14,30 ngày)
   - Đếm tần suất từng số
   - Tìm pattern liên tiếp
                ↓
3. Phân tích Hot Pairs (7 ngày gần nhất)
                ↓
4. ML Analysis (chỉ nếu ≥100 ngày)
                ↓
5. Tính điểm tổng hợp với trọng số
   - Chu kỳ ngắn: trọng số cao
   - ML: 15% nếu có
   - Hot pairs: bonus 10%
                ↓
6. Chuẩn hóa điểm 0-100%
                ↓
7. Sắp xếp và lấy top 15 số
                ↓
8. Hiển thị trong template với độ tin cậy
```

---

## ⚙️ **6. CÁC THÔNG SỐ QUAN TRỌNG**

| **Thông số** | **Giá trị** | **Ý nghĩa** |
|--------------|-------------|-------------|
| **History range** | 30 ngày | Lấy dữ liệu gần nhất |
| **Top predictions** | 15 số | Số lượng dự đoán cuối cùng |
| **Cycle weights** | 35%,25%,20%,15%,5% | Trọng số chu kỳ |
| **ML threshold** | 100 ngày | Tối thiểu để dùng ML |
| **Hot pairs range** | 7 ngày | Phạm vi phân tích cặp nóng |
| **Hot pairs bonus** | +10% | Tăng cường điểm |

---

## 🎯 **KẾT LUẬN**

**Hệ thống hoạt động dựa trên:**
1. **Statistical Analysis** (chính) - Phân tích tần suất xuất hiện theo các chu kỳ
2. **Pattern Recognition** - Tìm số xuất hiện liên tiếp
3. **ML Enhancement** - Chỉ khi có đủ dữ liệu
4. **Hot Pairs Bonus** - Tăng cường cho số trong cặp nóng

**15 số cuối cùng** được chọn dựa trên **điểm tổng hợp** từ tất cả các yếu tố trên, với chu kỳ ngắn hạn được ưu tiên cao nhất.
