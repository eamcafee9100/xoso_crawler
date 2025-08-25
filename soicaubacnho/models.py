# models.py (phiên bản hợp nhất)
from django.db import models
from django.utils import timezone
import json
from django.contrib.auth.models import User

class SoiCauBacNho(models.Model):
    """Lưu trữ kết quả phân tích và dự đoán theo phương pháp Bạc Nhớ"""
    PREDICTION_METHODS = [
        ('theo_ngay', 'Soi cầu theo ngày'),
        ('theo_tong_db', 'Soi cầu theo tổng giải đặc biệt'),
        ('theo_thu', 'Soi cầu theo thứ'),
        ('theo_cap_kem', 'Soi cầu theo cặp số đi kèm'),
        ('theo_lo', 'Soi cầu theo lô'),
        ('theo_dau_cam', 'Soi cầu theo đầu câm'),
        ('theo_duoi_cam', 'Soi cầu theo đuôi câm'),
        ('discovered_rules', 'Quy luật đã phát hiện'),
        ('cyclical', 'Chu kỳ'),
        ('machine_learning', 'Học máy'),
        # Thêm các phương pháp mới
        ('theo_dau_duoi_cam', 'Soi cầu theo đầu đuôi câm'),
        ('theo_kep', 'Soi cầu theo kép'),
        ('ml_advanced', 'Học máy nâng cao'),
        ('ensemble', 'Ensemble'),
        ('market_trend', 'Xu hướng thị trường'),
        ('ket_hop', 'Soi cầu kết hợp')
    ]
    
    # Thêm trường phiên bản để xác định sử dụng phiên bản nào
    VERSION_CHOICES = [
        ('v0', 'Phiên bản gốc'),
        ('v1', 'Phiên bản 1'),
    ]
    phien_ban = models.CharField(max_length=10, choices=VERSION_CHOICES, default='v0', verbose_name="Phiên bản")
    
    # Thông tin dự đoán
    ngay_du_doan = models.DateField(help_text="Ngày dự đoán (target)")
    ngay_phan_tich = models.DateField(default=timezone.now, help_text="Ngày thực hiện phân tích")
    phuong_phap = models.CharField(max_length=20, choices=PREDICTION_METHODS, help_text="Phương pháp soi cầu")
    
    # Thông tin về dữ liệu đầu vào
    ket_qua_ngay_truoc = models.CharField(max_length=255, help_text="Kết quả ngày trước đó")
    thu_trong_tuan = models.IntegerField(help_text="Thứ trong tuần (0: Thứ Hai - 6: Chủ Nhật)")
    
    # Kết quả dự đoán
    ket_qua_du_doan = models.CharField(max_length=255, help_text="Kết quả dự đoán (dạng JSON)")
    ty_le_tin_cay = models.FloatField(default=0, help_text="Tỷ lệ tin cậy của dự đoán (0-100%)")
    
    # Kết quả thực tế (cập nhật sau khi có KQXS)
    ket_qua_thuc_te = models.CharField(max_length=255, null=True, blank=True, help_text="Kết quả thực tế")
    ket_qua_trung = models.BooleanField(null=True, blank=True, help_text="Kết quả dự đoán có trúng không")
    
    # Thông tin bổ sung
    ghi_chu = models.TextField(blank=True, null=True, help_text="Ghi chú bổ sung")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_ket_qua_du_doan(self, ket_qua_list):
        self.ket_qua_du_doan = json.dumps(ket_qua_list)
    
    def get_ket_qua_du_doan(self):
        return json.loads(self.ket_qua_du_doan) if self.ket_qua_du_doan else []

    def set_ket_qua_thuc_te(self, ket_qua_list):
        # Nếu ket_qua_list là set, chuyển thành list
        if isinstance(ket_qua_list, set):
            ket_qua_list = list(ket_qua_list)
        # Nếu là list chứa set, chuyển từng phần tử
        elif isinstance(ket_qua_list, list):
            ket_qua_list = [list(item) if isinstance(item, set) else item for item in ket_qua_list]
        self.ket_qua_thuc_te = json.dumps(ket_qua_list)
    
    def get_ket_qua_thuc_te(self):
        """Trả về danh sách các số trong kết quả thực tế"""
        if not self.ket_qua_thuc_te:
            return []
        
        # Thử phân tích JSON
        try:
            return json.loads(self.ket_qua_thuc_te)
        except json.JSONDecodeError:
            # Nếu không phải JSON, giả định là danh sách các số phân tách bởi dấu phẩy
            return [num.strip() for num in self.ket_qua_thuc_te.split(',') if num.strip()] 
        
    def get_version_name(self):
        return dict(self.VERSION_CHOICES).get(self.phien_ban, "Không xác định")
    
    def get_weekday_display(self):
        weekday_names = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']
        return weekday_names[self.thu_trong_tuan] if 0 <= self.thu_trong_tuan < 7 else f"Ngày {self.thu_trong_tuan}"
    
    class Meta:
        verbose_name = "Soi cầu bạc nhớ"
        verbose_name_plural = "Soi cầu bạc nhớ"
        indexes = [
            models.Index(fields=['ngay_du_doan']),
            models.Index(fields=['phuong_phap']),
            models.Index(fields=['thu_trong_tuan']),
            models.Index(fields=['phien_ban']),
        ]


class LichSuSoiCau(models.Model):
    """Lưu trữ lịch sử soi cầu để theo dõi hiệu quả theo thời gian"""
    soi_cau = models.ForeignKey(SoiCauBacNho, on_delete=models.CASCADE, related_name='lich_su')
    thoi_gian = models.DateTimeField(default=timezone.now)
    doi_tuong_id = models.IntegerField(verbose_name="ID đối tượng", null=True, blank=True)
    loai_soi_cau = models.CharField(max_length=50)
    ket_qua = models.TextField(verbose_name="Kết quả JSON")
    phien_ban = models.CharField(max_length=10, choices=SoiCauBacNho.VERSION_CHOICES, default='v1')
    trang_thai = models.CharField(max_length=20, choices=[
        ('chua_kiem_tra', 'Chưa kiểm tra'),
        ('trung', 'Trúng'),
        ('truot', 'Trượt'),
    ], default='chua_kiem_tra')
    
    def __str__(self):
        return f"Lịch sử soi cầu {self.id} - {self.loai_soi_cau} - {self.thoi_gian}"
    
    class Meta:
        verbose_name = "Lịch sử soi cầu"
        verbose_name_plural = "Lịch sử soi cầu"
        indexes = [
            models.Index(fields=['thoi_gian']),
            models.Index(fields=['phien_ban']),
            models.Index(fields=['trang_thai']),
        ]


class ThongKeHieuQua(models.Model):
    """Thống kê hiệu quả của các phương pháp soi cầu"""
    phuong_phap = models.CharField(max_length=20, choices=SoiCauBacNho.PREDICTION_METHODS)
    ngay_bat_dau = models.DateField(help_text="Ngày bắt đầu thống kê")
    ngay_ket_thuc = models.DateField(help_text="Ngày kết thúc thống kê")
    phien_ban = models.CharField(max_length=10, choices=SoiCauBacNho.VERSION_CHOICES, default='v1')
    tong_so_du_doan = models.IntegerField(default=0, help_text="Tổng số dự đoán")
    so_lan_trung = models.IntegerField(default=0, help_text="Số lần trúng")
    ty_le_trung = models.FloatField(default=0, help_text="Tỷ lệ trúng (%)")
    
    # Thông tin chi tiết
    du_doan_theo_ngay = models.TextField(blank=True, help_text="Chi tiết dự đoán theo ngày (JSON)")
    
    # Xu hướng hiệu quả
    xu_huong = models.CharField(max_length=20, default='stable',
                              choices=[('up', 'Tăng'), ('down', 'Giảm'), ('stable', 'Ổn định')])
    do_manh_xu_huong = models.FloatField(default=0, help_text="Độ mạnh của xu hướng (0-1)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_du_doan_theo_ngay(self, data):
        self.du_doan_theo_ngay = json.dumps(data)
    
    def get_du_doan_theo_ngay(self):
        return json.loads(self.du_doan_theo_ngay) if self.du_doan_theo_ngay else {}
    
    class Meta:
        verbose_name = "Thống kê hiệu quả"
        verbose_name_plural = "Thống kê hiệu quả"
        indexes = [
            models.Index(fields=['phuong_phap']),
            models.Index(fields=['ngay_bat_dau', 'ngay_ket_thuc']),
            models.Index(fields=['phien_ban']),
        ]


class QuyLuatBacNho(models.Model):
    """Lưu trữ các quy luật bạc nhớ đã được phát hiện và hiệu quả của chúng"""
    loai_quy_luat = models.CharField(max_length=50, help_text="Loại quy luật (theo ngày, theo thứ, ...)")
    mo_ta = models.TextField(help_text="Mô tả quy luật")
    phien_ban = models.CharField(max_length=10, choices=SoiCauBacNho.VERSION_CHOICES, default='v1')
    
    # Định dạng quy luật
    dieu_kien = models.TextField(help_text="Điều kiện áp dụng quy luật (JSON)")
    ket_qua = models.TextField(help_text="Kết quả dự đoán khi thỏa điều kiện (JSON)")
    
    # Đánh giá hiệu quả
    so_lan_ap_dung = models.IntegerField(default=0, help_text="Số lần áp dụng quy luật")
    so_lan_trung = models.IntegerField(default=0, help_text="Số lần trúng khi áp dụng")
    ty_le_trung = models.FloatField(default=0, help_text="Tỷ lệ trúng (%)")
    
    # Thông tin thêm
    ngay_phat_hien = models.DateField(default=timezone.now, help_text="Ngày phát hiện quy luật")
    co_hieu_luc = models.BooleanField(default=True, help_text="Quy luật còn hiệu lực không")
    he_so_tin_cay = models.FloatField(default=50, help_text="Hệ số tin cậy (0-100%)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_dieu_kien(self, data):
        self.dieu_kien = json.dumps(data)
    
    def get_dieu_kien(self):
        return json.loads(self.dieu_kien) if self.dieu_kien else {}
    
    def set_ket_qua(self, data):
        self.ket_qua = json.dumps(data)
    
    def get_ket_qua(self):
        return json.loads(self.ket_qua) if self.ket_qua else []
    
    class Meta:
        verbose_name = "Quy luật bạc nhớ"
        verbose_name_plural = "Các quy luật bạc nhớ"
        indexes = [
            models.Index(fields=['loai_quy_luat']),
            models.Index(fields=['co_hieu_luc']),
            models.Index(fields=['he_so_tin_cay']),
            models.Index(fields=['phien_ban']),
        ]


class MethodWeight(models.Model):
    """
    Model lưu trữ trọng số của các phương pháp dự đoán
    """
    effective_date = models.DateField(verbose_name="Ngày có hiệu lực")
    method_name = models.CharField(max_length=50, verbose_name="Tên phương pháp")
    method_version = models.CharField(max_length=10, default="1.0", verbose_name="Phiên bản phương pháp")
    phien_ban = models.CharField(max_length=10, choices=SoiCauBacNho.VERSION_CHOICES, default='v1')
    weight = models.FloatField(verbose_name="Trọng số")
    calculation_basis = models.CharField(
        max_length=20,
        choices=[
            ('optimized', 'Tối ưu hóa tự động'),
            ('manual', 'Thiết lập thủ công'),
            ('historical', 'Dựa trên dữ liệu lịch sử')
        ],
        default='optimized',
        verbose_name="Cơ sở tính toán"
    )
    days_analyzed = models.IntegerField(default=30, verbose_name="Số ngày phân tích")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời điểm tạo")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    
    class Meta:
        verbose_name = "Trọng số phương pháp"
        verbose_name_plural = "Trọng số các phương pháp"
        ordering = ['-effective_date', 'method_name']
        # Thêm unique constraint để đảm bảo không có hai bản ghi trùng lặp
        unique_together = [['effective_date', 'method_name', 'method_version', 'phien_ban']]
    
    def __str__(self):
        return f"{self.method_name} ({self.effective_date.strftime('%d/%m/%Y')}): {self.weight}"
    
    @classmethod
    def get_latest_weights(cls, phien_ban='v1'):
        """
        Lấy trọng số mới nhất cho các phương pháp
        Returns:
            Dict mapping method_name to weight
        """
        today = timezone.now().date()
        # Lấy trọng số mới nhất có hiệu lực từ hôm nay trở về trước
        latest_weights = {}
        # Lấy ngày hiệu lực mới nhất
        latest_date = cls.objects.filter(
            effective_date__lte=today,
            phien_ban=phien_ban
        ).values('effective_date').order_by('-effective_date').first()
        
        if latest_date:
            # Lấy tất cả trọng số có hiệu lực vào ngày đó
            weights = cls.objects.filter(
                effective_date=latest_date['effective_date'],
                phien_ban=phien_ban
            )
            for weight in weights:
                latest_weights[weight.method_name] = weight.weight
        
        return latest_weights
    
    @classmethod
    def get_weight_history(cls, method_name, days=90, phien_ban='v1'):
        """
        Lấy lịch sử trọng số của một phương pháp
        Args:
            method_name: Tên phương pháp
            days: Số ngày lịch sử cần lấy
            phien_ban: Phiên bản analyzer
        Returns:
            List các dict chứa thông tin trọng số theo thời gian
        """
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=days)
        
        weights = cls.objects.filter(
            method_name=method_name,
            effective_date__range=(start_date, end_date),
            phien_ban=phien_ban
        ).order_by('effective_date')
        
        return [
            {
                'date': weight.effective_date,
                'weight': weight.weight,
                'basis': weight.calculation_basis,
                'days_analyzed': weight.days_analyzed
            }
            for weight in weights
        ]


class CauHinhPhanTich(models.Model):
    """Cấu hình cho các phân tích bạc nhớ"""
    ten_cau_hinh = models.CharField(max_length=100)
    phien_ban_mac_dinh = models.CharField(max_length=10, choices=SoiCauBacNho.VERSION_CHOICES, default='v1')
    phuong_phap_mac_dinh = models.JSONField(default=list, help_text="Danh sách các phương pháp mặc định")
    trong_so_mac_dinh = models.JSONField(default=dict, help_text="Trọng số cho các phương pháp")
    tham_so_khac = models.JSONField(default=dict, help_text="Các tham số khác")
    nguoi_tao = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True)
    mo_ta = models.TextField(blank=True)
    trang_thai = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.ten_cau_hinh} ({self.phien_ban_mac_dinh})"
    
    class Meta:
        verbose_name = "Cấu hình phân tích"
        verbose_name_plural = "Cấu hình phân tích"
        ordering = ['-thoi_gian_cap_nhat']


class ChiTietPhanTich(models.Model):
    """Lưu trữ chi tiết về quá trình phân tích"""
    soi_cau = models.ForeignKey(SoiCauBacNho, on_delete=models.CASCADE, related_name='chi_tiet')
    buoc_phan_tich = models.CharField(max_length=100, help_text="Tên bước phân tích")
    thoi_gian_bat_dau = models.DateTimeField()
    thoi_gian_ket_thuc = models.DateTimeField()
    trang_thai = models.CharField(max_length=20, choices=[
        ('success', 'Thành công'),
        ('failed', 'Thất bại'),
        ('partial', 'Một phần'),
    ])
    ket_qua = models.TextField(help_text="Kết quả chi tiết dạng JSON")
    loi = models.TextField(blank=True, null=True, help_text="Thông tin lỗi nếu có")
    
    def set_ket_qua(self, data):
        self.ket_qua = json.dumps(data)
    
    def get_ket_qua(self):
        return json.loads(self.ket_qua) if self.ket_qua else {}
    
    def __str__(self):
        return f"Chi tiết {self.buoc_phan_tich} - {self.soi_cau.ngay_du_doan}"
    
    class Meta:
        verbose_name = "Chi tiết phân tích"
        verbose_name_plural = "Chi tiết phân tích"
        ordering = ['soi_cau', 'thoi_gian_bat_dau']