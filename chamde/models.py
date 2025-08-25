from django.db import models
from results.models import KetQuaXoSo

# Create your models here.
class ChamAnalysis(models.Model):
    """Phân tích chạm cho mỗi ngày xổ số"""
    ngay = models.DateField(unique=True)
    ket_qua = models.ForeignKey(KetQuaXoSo, on_delete=models.CASCADE, related_name='cham_analyses')
    
    # Giá trị chạm của giải đặc biệt
    db_cham_dau = models.CharField(max_length=1, help_text="Chữ số đầu của giải đặc biệt")
    db_cham_duoi = models.CharField(max_length=1, help_text="Chữ số cuối của giải đặc biệt")
    
    # Giải đặc biệt đầy đủ và các chữ số
    db_full = models.CharField(max_length=6, help_text="Giải đặc biệt đầy đủ")
    db_last2 = models.CharField(max_length=2, help_text="2 số cuối giải đặc biệt")
    db_digit1 = models.CharField(max_length=1, help_text="Chữ số thứ nhất")
    db_digit2 = models.CharField(max_length=1, help_text="Chữ số thứ hai")
    db_digit3 = models.CharField(max_length=1, help_text="Chữ số thứ ba")
    db_digit4 = models.CharField(max_length=1, help_text="Chữ số thứ tư")
    db_digit5 = models.CharField(max_length=1, help_text="Chữ số thứ năm")
    db_digit6 = models.CharField(max_length=1, help_text="Chữ số thứ sáu (nếu có)")
    
    # Tổng của giải đặc biệt
    db_total = models.IntegerField(help_text="Tổng các chữ số của giải đặc biệt")
    db_last2_total = models.IntegerField(help_text="Tổng 2 chữ số cuối")
    
    # Giải nhất và chữ số giữa (cho phương pháp cầu chạm 1)
    giai_nhat_full = models.CharField(max_length=5, help_text="Giải nhất đầy đủ")
    giai_nhat_mid_digit = models.CharField(max_length=1, help_text="Chữ số giữa của giải nhất")
    
    # Thông tin ngày
    day_of_week = models.IntegerField(help_text="Thứ trong tuần (0-6)")
    is_sunday = models.BooleanField(help_text="Có phải là Chủ Nhật không")
    is_monday = models.BooleanField(default=False, help_text="Có phải là Thứ Hai không")
    is_tuesday = models.BooleanField(default=False, help_text="Có phải là Thứ Ba không")
    is_wednesday = models.BooleanField(default=False, help_text="Có phải là Thứ Tư không")
    is_thursday = models.BooleanField(default=False, help_text="Có phải là Thứ Năm không")
    is_friday = models.BooleanField(default=False, help_text="Có phải là Thứ Sáu không")
    is_saturday = models.BooleanField(default=False, help_text="Có phải là Thứ Bảy không")
    
    week_number = models.IntegerField(help_text="Tuần thứ mấy trong năm")
    month = models.IntegerField(help_text="Tháng")
    
    # Thêm các trường chạm đầu theo từng số
    cham_dau_0 = models.BooleanField(default=False, help_text="Chạm đầu số 0")
    cham_dau_1 = models.BooleanField(default=False, help_text="Chạm đầu số 1")
    cham_dau_2 = models.BooleanField(default=False, help_text="Chạm đầu số 2")
    cham_dau_3 = models.BooleanField(default=False, help_text="Chạm đầu số 3")
    cham_dau_4 = models.BooleanField(default=False, help_text="Chạm đầu số 4")
    cham_dau_5 = models.BooleanField(default=False, help_text="Chạm đầu số 5")
    cham_dau_6 = models.BooleanField(default=False, help_text="Chạm đầu số 6")
    cham_dau_7 = models.BooleanField(default=False, help_text="Chạm đầu số 7")
    cham_dau_8 = models.BooleanField(default=False, help_text="Chạm đầu số 8")
    cham_dau_9 = models.BooleanField(default=False, help_text="Chạm đầu số 9")
    
    # Thêm các trường chạm đuôi theo từng số
    cham_duoi_0 = models.BooleanField(default=False, help_text="Chạm đuôi số 0")
    cham_duoi_1 = models.BooleanField(default=False, help_text="Chạm đuôi số 1")
    cham_duoi_2 = models.BooleanField(default=False, help_text="Chạm đuôi số 2")
    cham_duoi_3 = models.BooleanField(default=False, help_text="Chạm đuôi số 3")
    cham_duoi_4 = models.BooleanField(default=False, help_text="Chạm đuôi số 4")
    cham_duoi_5 = models.BooleanField(default=False, help_text="Chạm đuôi số 5")
    cham_duoi_6 = models.BooleanField(default=False, help_text="Chạm đuôi số 6")
    cham_duoi_7 = models.BooleanField(default=False, help_text="Chạm đuôi số 7")
    cham_duoi_8 = models.BooleanField(default=False, help_text="Chạm đuôi số 8")
    cham_duoi_9 = models.BooleanField(default=False, help_text="Chạm đuôi số 9")
    
    # Trường phân tích thêm cho các phương pháp cầu
    cau_cham1_value = models.CharField(max_length=1, null=True, blank=True,
                                       help_text="Giá trị cho cầu chạm kiểu 1 (lấy từ giải nhất CN)")
    cau_cham2_value = models.CharField(max_length=2, null=True, blank=True,
                                       help_text="Giá trị cho cầu chạm kiểu 2 (tổng đề CN + đuôi đề thứ 6)")
    
    class Meta:
        indexes = [
            models.Index(fields=['ngay']),
            models.Index(fields=['day_of_week']),
            models.Index(fields=['db_cham_dau']),
            models.Index(fields=['db_cham_duoi']),
            models.Index(fields=['db_last2']),
        ]
    
    def __str__(self):
        return f"Phân tích chạm ngày {self.ngay}"
    
    def save(self, *args, **kwargs):
        """Override save để tự động set các trường is_day"""
        weekday = self.ngay.weekday()  # 0=Monday, 6=Sunday
        
        # Reset tất cả về False
        self.is_monday = False
        self.is_tuesday = False
        self.is_wednesday = False
        self.is_thursday = False
        self.is_friday = False
        self.is_saturday = False
        self.is_sunday = False
        
        # Set đúng ngày
        if weekday == 0:
            self.is_monday = True
        elif weekday == 1:
            self.is_tuesday = True
        elif weekday == 2:
            self.is_wednesday = True
        elif weekday == 3:
            self.is_thursday = True
        elif weekday == 4:
            self.is_friday = True
        elif weekday == 5:
            self.is_saturday = True
        elif weekday == 6:
            self.is_sunday = True
        
        # Set các trường chạm đầu/đuôi
        if self.db_cham_dau:
            for i in range(10):
                setattr(self, f'cham_dau_{i}', str(i) == self.db_cham_dau)
        
        if self.db_cham_duoi:
            for i in range(10):
                setattr(self, f'cham_duoi_{i}', str(i) == self.db_cham_duoi)
        
        super().save(*args, **kwargs)

class ChamPattern(models.Model):
    """Mô hình cơ sở cho các mẫu chạm"""
    ngay = models.DateField()
    cham_value = models.CharField(max_length=1, help_text="Giá trị chạm (0-9)")
    has_hit = models.BooleanField(default=False, help_text="Có trúng trong giải đặc biệt không")
    
    class Meta:
        abstract = True
class ChamDau(ChamPattern):
    """Theo dõi chạm đầu theo ngày"""
    numbers = models.JSONField(help_text="Danh sách các số thuộc chạm đầu này")
    appeared_numbers = models.JSONField(help_text="Các số thuộc chạm này xuất hiện trong KQXS")
    
    class Meta:
        unique_together = ('ngay', 'cham_value')
        indexes = [
            models.Index(fields=['ngay']),
            models.Index(fields=['cham_value']),
            models.Index(fields=['has_hit']),
        ]
        
    def __str__(self):
        return f"Chạm đầu {self.cham_value} ngày {self.ngay}"
    
class ChamDuoi(ChamPattern):
    """Theo dõi chạm đuôi theo ngày"""
    numbers = models.JSONField(help_text="Danh sách các số thuộc chạm đuôi này")
    appeared_numbers = models.JSONField(help_text="Các số thuộc chạm này xuất hiện trong KQXS")
    
    class Meta:
        unique_together = ('ngay', 'cham_value')
        indexes = [
            models.Index(fields=['ngay']),
            models.Index(fields=['cham_value']),
            models.Index(fields=['has_hit']),
        ]
        
    def __str__(self):
        return f"Chạm đuôi {self.cham_value} ngày {self.ngay}"
    
class CauChamPrediction(models.Model):
    """Dự đoán dựa trên các phương pháp cầu chạm"""
    ngay_du_doan = models.DateField(help_text="Ngày dự đoán")
    ngay_tao = models.DateTimeField(auto_now_add=True, help_text="Ngày tạo dự đoán")
    
    # Phương pháp cầu chạm
    PHUONG_PHAP_CHOICES = [
        ('cau_cham1', 'Cầu chạm kiểu 1 (Giải nhất CN)'),
        ('cau_cham2', 'Cầu chạm kiểu 2 (Tổng đề CN + đuôi đề thứ 6)'),
        ('cau_cham_custom', 'Cầu chạm tùy chỉnh'),
    ]
    phuong_phap = models.CharField(max_length=20, choices=PHUONG_PHAP_CHOICES)
    
    # Giá trị chạm và dự đoán
    cham_value = models.CharField(max_length=2, help_text="Giá trị chạm được chọn")
    du_doan_numbers = models.JSONField(help_text="Các số được dự đoán")
    
    # Kết quả
    ket_qua_thuc_te = models.CharField(max_length=2, null=True, blank=True, help_text="Kết quả thực tế")
    ket_qua_trung = models.BooleanField(null=True, blank=True, help_text="Có trúng không")
    
    # Thông tin bổ sung
    do_tin_cay = models.FloatField(default=0, help_text="Độ tin cậy của dự đoán (0-100)")
    thong_tin_bo_sung = models.JSONField(null=True, blank=True, help_text="Thông tin bổ sung")
    
    class Meta:
        indexes = [
            models.Index(fields=['ngay_du_doan']),
            models.Index(fields=['phuong_phap']),
            models.Index(fields=['cham_value']),
        ]
        
    def __str__(self):
        return f"Dự đoán cầu chạm {self.cham_value} cho ngày {self.ngay_du_doan}"
    
class QuaTramPattern(models.Model):
    """Theo dõi mẫu quả trám trong kết quả xổ số"""
    ngay = models.DateField(help_text="Ngày phát hiện mẫu")
    giai_thuong = models.CharField(max_length=10, help_text="Giải thưởng xuất hiện mẫu")
    
    # Các chữ số trong mẫu quả trám
    digit_top = models.CharField(max_length=1, help_text="Chữ số trên cùng")
    digit_mid_left = models.CharField(max_length=1, help_text="Chữ số giữa bên trái")
    digit_mid_right = models.CharField(max_length=1, help_text="Chữ số giữa bên phải")
    digit_bottom = models.CharField(max_length=1, help_text="Chữ số dưới cùng")
    
    # Số được dự đoán cho ngày tiếp theo
    predicted_number = models.CharField(max_length=2, help_text="Số được dự đoán")
    
    # Kết quả theo dõi
    hit_date = models.DateField(null=True, blank=True, help_text="Ngày số dự đoán về")
    days_to_hit = models.IntegerField(null=True, blank=True, help_text="Số ngày để trúng")
    has_hit = models.BooleanField(default=False, help_text="Đã trúng chưa")
    
    class Meta:
        indexes = [
            models.Index(fields=['ngay']),
            models.Index(fields=['predicted_number']),
            models.Index(fields=['has_hit']),
        ]
        
    def __str__(self):
        return f"Mẫu quả trám ngày {self.ngay}: {self.digit_top}-{self.digit_mid_left}{self.digit_mid_right}-{self.digit_bottom}"
    
class NumberStatistics(models.Model):
    """Thống kê chi tiết về từng số theo thời gian"""
    number = models.CharField(max_length=2, help_text="Số 2 chữ số (00-99)")
    
    # Thống kê chạm
    cham_dau = models.CharField(max_length=1, help_text="Chạm đầu")
    cham_duoi = models.CharField(max_length=1, help_text="Chạm đuôi")
    
    # Thống kê xuất hiện
    total_appearances = models.IntegerField(default=0, help_text="Tổng số lần xuất hiện")
    db_appearances = models.IntegerField(default=0, help_text="Số lần xuất hiện trong giải đặc biệt")
    last_appearance_date = models.DateField(null=True, blank=True, help_text="Ngày xuất hiện gần nhất")
    
    # Thống kê theo chu kỳ
    avg_days_between_hits = models.FloatField(null=True, blank=True, help_text="Số ngày trung bình giữa các lần về")
    std_days_between_hits = models.FloatField(null=True, blank=True, help_text="Độ lệch chuẩn của số ngày giữa các lần về")
    
    # Thống kê theo ngày trong tuần
    monday_hits = models.IntegerField(default=0)
    tuesday_hits = models.IntegerField(default=0)
    wednesday_hits = models.IntegerField(default=0)
    thursday_hits = models.IntegerField(default=0)
    friday_hits = models.IntegerField(default=0)
    saturday_hits = models.IntegerField(default=0)
    sunday_hits = models.IntegerField(default=0)
    
    # Các loại đặc biệt
    is_double = models.BooleanField(default=False, help_text="Có phải số kép không")
    is_mirror = models.BooleanField(default=False, help_text="Có phải số gương không")
    is_consecutive = models.BooleanField(default=False, help_text="Có phải số liên tiếp không")
    
    # Thông tin cập nhật
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['cham_dau']),
            models.Index(fields=['cham_duoi']),
            models.Index(fields=['last_appearance_date']),
        ]
        
    def __str__(self):
        return f"Thống kê số {self.number}"
    
class NumberFrequencyTimeSeriesStats(models.Model):
    """Thống kê chuỗi thời gian của các số theo khoảng thời gian"""
    number = models.CharField(max_length=2, help_text="Số 2 chữ số (00-99)")
    
    # Khoảng thời gian
    PERIOD_CHOICES = [
        ('daily', 'Hàng ngày'),
        ('weekly', 'Hàng tuần'),
        ('monthly', 'Hàng tháng'),
        ('yearly', 'Hàng năm'),
    ]
    period_type = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    period_start = models.DateField(help_text="Ngày bắt đầu khoảng thời gian")
    period_end = models.DateField(help_text="Ngày kết thúc khoảng thời gian")
    
    # Thống kê
    appearance_count = models.IntegerField(default=0, help_text="Số lần xuất hiện")
    db_appearance_count = models.IntegerField(default=0, help_text="Số lần xuất hiện trong giải đặc biệt")
    appearance_days = models.JSONField(null=True, blank=True, help_text="Ngày xuất hiện")
    
    # Chạm
    cham_dau = models.CharField(max_length=1, help_text="Chạm đầu")
    cham_duoi = models.CharField(max_length=1, help_text="Chạm đuôi")
    
    # Phân tích xu hướng
    trend = models.FloatField(null=True, blank=True, help_text="Xu hướng tăng/giảm")
    
    class Meta:
        unique_together = ('number', 'period_type', 'period_start')
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['period_type']),
            models.Index(fields=['period_start']),
            models.Index(fields=['cham_dau']),
            models.Index(fields=['cham_duoi']),
        ]
        
    def __str__(self):
        return f"Thống kê số {self.number} từ {self.period_start} đến {self.period_end}"
    
class ChamPatternAnalysis(models.Model):
    """Phân tích mẫu chạm theo khoảng thời gian"""
    # Khoảng thời gian
    period_start = models.DateField(help_text="Ngày bắt đầu khoảng thời gian")
    period_end = models.DateField(help_text="Ngày kết thúc khoảng thời gian")
    
    PATTERN_TYPE_CHOICES = [
        ('cham_dau', 'Chạm đầu'),
        ('cham_duoi', 'Chạm đuôi'),
        ('cau_cham1', 'Cầu chạm kiểu 1'),
        ('cau_cham2', 'Cầu chạm kiểu 2'),
    ]
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPE_CHOICES)
    pattern_value = models.CharField(max_length=2, help_text="Giá trị mẫu")
    
    # Thống kê
    total_occurrences = models.IntegerField(default=0, help_text="Tổng số lần xuất hiện")
    hit_count = models.IntegerField(default=0, help_text="Số lần trúng")
    hit_rate = models.FloatField(default=0, help_text="Tỷ lệ trúng (%)")
    
    # Thống kê theo thứ
    monday_hits = models.IntegerField(default=0)
    tuesday_hits = models.IntegerField(default=0)
    wednesday_hits = models.IntegerField(default=0)
    thursday_hits = models.IntegerField(default=0)
    friday_hits = models.IntegerField(default=0)
    saturday_hits = models.IntegerField(default=0)
    sunday_hits = models.IntegerField(default=0)
    
    # Dữ liệu chi tiết
    detailed_data = models.JSONField(help_text="Dữ liệu chi tiết theo ngày")
    
    class Meta:
        unique_together = ('pattern_type', 'pattern_value', 'period_start', 'period_end')
        indexes = [
            models.Index(fields=['pattern_type']),
            models.Index(fields=['pattern_value']),
            models.Index(fields=['period_start']),
            models.Index(fields=['hit_rate']),
        ]
        
    def __str__(self):
        return f"Phân tích {self.pattern_type} {self.pattern_value} từ {self.period_start} đến {self.period_end}"
    

class WeeklyDigitPatternStats(models.Model):
    """Thống kê mẫu chữ số theo tuần"""
    year = models.IntegerField(help_text="Năm")
    week_number = models.IntegerField(help_text="Tuần trong năm")
    
    # Ngày bắt đầu và kết thúc tuần
    week_start = models.DateField(help_text="Ngày bắt đầu tuần")
    week_end = models.DateField(help_text="Ngày kết thúc tuần")
    
    # Chữ số đầu xuất hiện nhiều nhất trong tuần
    most_common_first_digit = models.CharField(max_length=1, help_text="Chữ số đầu phổ biến nhất")
    first_digit_frequency = models.IntegerField(help_text="Tần suất xuất hiện")
    
    # Chữ số cuối xuất hiện nhiều nhất trong tuần
    most_common_last_digit = models.CharField(max_length=1, help_text="Chữ số cuối phổ biến nhất")
    last_digit_frequency = models.IntegerField(help_text="Tần suất xuất hiện")
    
    # Chạm đầu nhiều nhất
    most_hit_cham_dau = models.CharField(max_length=1, help_text="Chạm đầu về nhiều nhất")
    cham_dau_hit_count = models.IntegerField(help_text="Số lần về")
    
    # Chạm đuôi nhiều nhất
    most_hit_cham_duoi = models.CharField(max_length=1, help_text="Chạm đuôi về nhiều nhất")
    cham_duoi_hit_count = models.IntegerField(help_text="Số lần về")
    
    # Số xuất hiện nhiều nhất
    most_common_number = models.CharField(max_length=2, help_text="Số xuất hiện nhiều nhất")
    most_common_number_count = models.IntegerField(help_text="Số lần xuất hiện")
    
    # Dữ liệu chi tiết
    first_digit_data = models.JSONField(help_text="Dữ liệu chi tiết chữ số đầu")
    last_digit_data = models.JSONField(help_text="Dữ liệu chi tiết chữ số cuối")
    cham_dau_data = models.JSONField(help_text="Dữ liệu chi tiết chạm đầu")
    cham_duoi_data = models.JSONField(help_text="Dữ liệu chi tiết chạm đuôi")
    
    class Meta:
        unique_together = ('year', 'week_number')
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['week_number']),
            models.Index(fields=['week_start']),
        ]
        
    def __str__(self):
        return f"Thống kê mẫu chữ số tuần {self.week_number} năm {self.year}"
    
class LoGanStats(models.Model):
    """Thống kê lô gan"""
    number = models.CharField(max_length=2, help_text="Số 2 chữ số (00-99)")
    date = models.DateField(help_text="Ngày thống kê")
    
    # Thông tin gan
    current_absent_days = models.IntegerField(help_text="Số ngày gan tính đến hiện tại")
    last_appearance = models.DateField(null=True, help_text="Lần xuất hiện gần nhất")
    max_absent_days = models.IntegerField(help_text="Số ngày gan tối đa trong lịch sử")
    
    # Thông tin dự đoán
    due_probability = models.FloatField(help_text="Xác suất sắp về (%)")
    expected_return_date = models.DateField(null=True, blank=True, help_text="Ngày dự kiến về")
    
    # Thông tin liên quan đến chạm
    cham_dau = models.CharField(max_length=1, help_text="Chạm đầu")
    cham_duoi = models.CharField(max_length=1, help_text="Chạm đuôi")
    
    class Meta:
        unique_together = ('number', 'date')
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['date']),
            models.Index(fields=['current_absent_days']),
            models.Index(fields=['cham_dau']),
            models.Index(fields=['cham_duoi']),
        ]
        
    def __str__(self):
        return f"Lô gan {self.number} ngày {self.date}: {self.current_absent_days} ngày"
    
class ChamAnalysisManager(models.Manager):
    def create_from_ketqua(self, ket_qua):
        """Tạo phân tích chạm từ kết quả xổ số"""
        try:
            # Trích xuất thông tin ngày
            ngay = ket_qua.ngay
            day_of_week = ngay.weekday()
            is_sunday = (day_of_week == 6)
            week_number = ngay.isocalendar()[1]
            month = ngay.month
            
            # Trích xuất giải đặc biệt
            db_full = ket_qua.giai_db
            db_last2 = db_full[-2:] if len(db_full) >= 2 else db_full
            
            # Lấy các chữ số
            digits = list(db_full.zfill(6))
            db_digit1 = digits[0]
            db_digit2 = digits[1]
            db_digit3 = digits[2]
            db_digit4 = digits[3]
            db_digit5 = digits[4]
            db_digit6 = digits[5]
            
            # Tính tổng
            db_total = sum(int(d) for d in digits)
            db_last2_total = int(db_last2[0]) + int(db_last2[1]) if len(db_last2) == 2 else int(db_last2[0])
            
            # Chạm đầu và đuôi
            db_cham_dau = db_last2[0] if len(db_last2) >= 1 else ''
            db_cham_duoi = db_last2[1] if len(db_last2) >= 2 else ''
            
            # Giải nhất
            giai_nhat_full = ket_qua.giai_nhat
            if len(giai_nhat_full) >= 3:
                giai_nhat_mid_digit = giai_nhat_full[len(giai_nhat_full)//2]
            else:
                giai_nhat_mid_digit = ''
            
            # Cầu chạm kiểu 1 (chỉ áp dụng cho Chủ Nhật)
            cau_cham1_value = None
            if is_sunday:
                cau_cham1_value = giai_nhat_mid_digit
            
            # Cầu chạm kiểu 2 (cần thông tin từ thứ 6)
            cau_cham2_value = None
            if is_sunday:
                # Lấy kết quả thứ 6 (2 ngày trước Chủ Nhật)
                friday_date = ngay - timedelta(days=2)
                friday_result = KetQuaXoSo.objects.filter(ngay=friday_date).first()
                if friday_result:
                    friday_db_last2 = friday_result.giai_db[-2:] if len(friday_result.giai_db) >= 2 else ''
                    if friday_db_last2 and db_total > 0:
                        # Tạo giá trị cho cầu chạm kiểu 2: tổng đề CN + đuôi đề thứ 6
                        cau_cham2_value = str(db_total % 10) + friday_db_last2[-1]
            
            # Tạo bản ghi ChamAnalysis
            return self.create(
                ngay=ngay,
                ket_qua=ket_qua,
                db_cham_dau=db_cham_dau,
                db_cham_duoi=db_cham_duoi,
                db_full=db_full,
                db_last2=db_last2,
                db_digit1=db_digit1,
                db_digit2=db_digit2,
                db_digit3=db_digit3,
                db_digit4=db_digit4,
                db_digit5=db_digit5,
                db_digit6=db_digit6,
                db_total=db_total,
                db_last2_total=db_last2_total,
                giai_nhat_full=giai_nhat_full,
                giai_nhat_mid_digit=giai_nhat_mid_digit,
                day_of_week=day_of_week,
                is_sunday=is_sunday,
                week_number=week_number,
                month=month,
                cau_cham1_value=cau_cham1_value,
                cau_cham2_value=cau_cham2_value
            )
        except Exception as e:
            print(f"Lỗi khi tạo phân tích chạm từ kết quả xổ số: {e}")
            raise

def generate_cham_dau_numbers(value):
    """Tạo danh sách số thuộc chạm đầu"""
    value = str(value)
    return [f"{value}{i}" for i in range(10) if i != int(value)]

class ChamDauManager(models.Manager):
    def create_for_date(self, ngay, ket_qua):
        """Tạo các bản ghi ChamDau cho một ngày"""
        all_numbers = ket_qua.get_all_2digit_numbers()
        result = []
        
        for value in range(10):
            cham_numbers = generate_cham_dau_numbers(value)
            
            # Tìm các số thuộc chạm này xuất hiện trong kết quả
            appeared = [num for num in cham_numbers if num in all_numbers]
            
            # Kiểm tra xem có trúng giải đặc biệt không
            db_last2 = ket_qua.giai_db[-2:] if len(ket_qua.giai_db) >= 2 else ''
            has_hit = db_last2 and db_last2[0] == str(value)
            
            cham_dau = self.create(
                ngay=ngay,
                cham_value=str(value),
                numbers=cham_numbers,
                appeared_numbers=appeared,
                has_hit=has_hit
            )
            result.append(cham_dau)
            
        return result
    
def generate_cham_duoi_numbers(value):
    """Tạo danh sách số thuộc chạm đuôi"""
    value = str(value)
    return [f"{i}{value}" for i in range(10) if i != int(value)]

class ChamDuoiManager(models.Manager):
    def create_for_date(self, ngay, ket_qua):
        """Tạo các bản ghi ChamDuoi cho một ngày"""
        all_numbers = ket_qua.get_all_2digit_numbers()
        result = []
        
        for value in range(10):
            cham_numbers = generate_cham_duoi_numbers(value)
            
            # Tìm các số thuộc chạm này xuất hiện trong kết quả
            appeared = [num for num in cham_numbers if num in all_numbers]
            
            # Kiểm tra xem có trúng giải đặc biệt không
            db_last2 = ket_qua.giai_db[-2:] if len(ket_qua.giai_db) >= 2 else ''
            has_hit = db_last2 and db_last2[1] == str(value)
            
            cham_duoi = self.create(
                ngay=ngay,
                cham_value=str(value),
                numbers=cham_numbers,
                appeared_numbers=appeared,
                has_hit=has_hit
            )
            result.append(cham_duoi)
            
        return result
    
class QuaTramPatternManager(models.Manager):
    def find_patterns(self, ket_qua):
        """Tìm các mẫu quả trám trong kết quả xổ số"""
        try:
            # Chỉ xét các giải Ba, Tư, Năm
            patterns = []
            
            # Chuyển giải Ba, Tư, Năm thành danh sách các số
            giai_ba = json.loads(ket_qua.giai_ba) if isinstance(ket_qua.giai_ba, str) else ket_qua.giai_ba
            giai_tu = json.loads(ket_qua.giai_tu) if isinstance(ket_qua.giai_tu, str) else ket_qua.giai_tu
            giai_nam = json.loads(ket_qua.giai_nam) if isinstance(ket_qua.giai_nam, str) else ket_qua.giai_nam
            
            # Kết hợp các giải để tìm mẫu quả trám
            all_numbers = []
            for g in giai_ba:
                all_numbers.append(('giai_ba', g))
            for g in giai_tu:
                all_numbers.append(('giai_tu', g))
            for g in giai_nam:
                all_numbers.append(('giai_nam', g))
            
            # Kiểm tra tất cả các tổ hợp có thể
            for i in range(len(all_numbers) - 2):
                for j in range(i + 1, len(all_numbers) - 1):
                    for k in range(j + 1, len(all_numbers)):
                        # Lấy ba số từ ba giải khác nhau
                        if all_numbers[i][0] != all_numbers[j][0] and all_numbers[i][0] != all_numbers[k][0] and all_numbers[j][0] != all_numbers[k][0]:
                            num1, num2, num3 = all_numbers[i][1], all_numbers[j][1], all_numbers[k][1]
                            
                            # Kiểm tra các tổ hợp số để tìm mẫu quả trám
                            for digit_top in range(10):
                                for digit_bottom in range(10):
                                    for digit_mid_left in range(10):
                                        for digit_mid_right in range(10):
                                            # Tạo mẫu quả trám
                                            # A
                                            # BAB
                                            # A
                                            pattern = {
                                                'top': str(digit_top),
                                                'mid_left': str(digit_mid_left),
                                                'mid_right': str(digit_mid_right),
                                                'bottom': str(digit_bottom)
                                            }
                                            
                                            # Kiểm tra xem mẫu có xuất hiện trong ba số này không
                                            if self._check_pattern_in_numbers(pattern, num1, num2, num3):
                                                # Tạo số dự đoán từ mẫu (2 số AB)
                                                predicted_number = pattern['mid_left'] + pattern['mid_right']
                                                
                                                # Lưu mẫu và số dự đoán
                                                pattern_obj = self.create(
                                                    ngay=ket_qua.ngay,
                                                    giai_thuong=f"{all_numbers[i][0]},{all_numbers[j][0]},{all_numbers[k][0]}",
                                                    digit_top=pattern['top'],
                                                    digit_mid_left=pattern['mid_left'],
                                                    digit_mid_right=pattern['mid_right'],
                                                    digit_bottom=pattern['bottom'],
                                                    predicted_number=predicted_number
                                                )
                                                patterns.append(pattern_obj)
            
            return patterns
        except Exception as e:
            print(f"Lỗi khi tìm mẫu quả trám: {e}")
            return []
    
    def _check_pattern_in_numbers(self, pattern, num1, num2, num3):
        """Kiểm tra xem mẫu quả trám có xuất hiện trong ba số hay không"""
        # Chuyển các số thành chuỗi để dễ xử lý
        num1, num2, num3 = str(num1), str(num2), str(num3)
        
        # Kiểm tra tất cả các vị trí có thể trong ba số
        # A
        # BAB
        # A
        
        # Kiểm tra pattern['top'] xuất hiện trong các số
        top_in_num1 = pattern['top'] in num1
        top_in_num2 = pattern['top'] in num2
        top_in_num3 = pattern['top'] in num3
        
        # Kiểm tra pattern['bottom'] xuất hiện trong các số
        bottom_in_num1 = pattern['bottom'] in num1
        bottom_in_num2 = pattern['bottom'] in num2
        bottom_in_num3 = pattern['bottom'] in num3
        
        # Kiểm tra pattern['mid_left'] và pattern['mid_right'] xuất hiện trong các số
        mid_left_in_num1 = pattern['mid_left'] in num1
        mid_left_in_num2 = pattern['mid_left'] in num2
        mid_left_in_num3 = pattern['mid_left'] in num3
        
        mid_right_in_num1 = pattern['mid_right'] in num1
        mid_right_in_num2 = pattern['mid_right'] in num2
        mid_right_in_num3 = pattern['mid_right'] in num3
        
        # Kiểm tra các tổ hợp có thể để tạo thành hình quả trám
        # Kiểm tra nếu top và bottom xuất hiện trong cùng một số
        # và mid_left, mid_right xuất hiện trong hai số còn lại
        
        # Trường hợp 1: top và bottom trong num1
        if (top_in_num1 and bottom_in_num1 and 
            ((mid_left_in_num2 and mid_right_in_num3) or (mid_left_in_num3 and mid_right_in_num2))):
            return True
        
        # Trường hợp 2: top và bottom trong num2
        if (top_in_num2 and bottom_in_num2 and 
            ((mid_left_in_num1 and mid_right_in_num3) or (mid_left_in_num3 and mid_right_in_num1))):
            return True
        
        # Trường hợp 3: top và bottom trong num3
        if (top_in_num3 and bottom_in_num3 and 
            ((mid_left_in_num1 and mid_right_in_num2) or (mid_left_in_num2 and mid_right_in_num1))):
            return True
        
        return False
    
class Prediction(models.Model):
    numbers = models.CharField(max_length=255)  # Store numbers as comma-separated string
    confidence = models.FloatField()
    notes = models.TextField(blank=True)
    target_date = models.DateField()
    method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction for {self.target_date} ({self.method})"