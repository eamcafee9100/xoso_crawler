from django.db import models
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta, date
import json
import numpy as np
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
from results.models import KetQuaXoSo
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import logging

logger = logging.getLogger(__name__)
class PhuongPhapTinhToan(models.Model):
    """Model lưu trữ các phương pháp tính toán do người dùng định nghĩa"""
    
    LOAI_PHUONG_PHAP_CHOICES = [
        ('gan', 'Dự đoán số gần'),
        ('xa', 'Dự đoán số xa'),
        ('chu_ky', 'Phân tích chu kỳ'),
        ('thong_ke', 'Thống kê tần suất'),
        ('dau_duoi', 'Phân tích đầu đuôi'),
        ('tong', 'Phân tích tổng'),
        ('lo_kep', 'Lô kép'),
        ('bach_thu', 'Bạch thủ'),
        ('dan_de', 'Đàn de'),
        ('cau_mb', 'Cầu miền Bắc'),
        ('custom', 'Tùy chỉnh'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Hoạt động'),
        ('inactive', 'Tạm dừng'),
        ('testing', 'Đang thử nghiệm'),
        ('archived', 'Lưu trữ'),
    ]
    
    ten_phuong_phap = models.CharField(max_length=200, verbose_name="Tên phương pháp")
    loai_phuong_phap = models.CharField(
        max_length=20, 
        choices=LOAI_PHUONG_PHAP_CHOICES,
        verbose_name="Loại phương pháp"
    )
    mo_ta = models.TextField(blank=True, verbose_name="Mô tả")
    
    # Cấu hình tham số
    tham_so_config = models.JSONField(
        default=dict,
        help_text="Cấu hình tham số dưới dạng JSON",
        verbose_name="Cấu hình tham số"
    )
    
    # Công thức tính toán
    cong_thuc = models.TextField(
        help_text="Công thức hoặc thuật toán tính toán",
        verbose_name="Công thức"
    )
    
    # Trọng số và độ tin cậy
    trong_so = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        verbose_name="Trọng số"
    )
    
    do_tin_cay = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Độ tin cậy"
    )
    
    # Trạng thái và metadata
    trang_thai = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='testing',
        verbose_name="Trạng thái"
    )
    
    nguoi_tao = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Người tạo"
    )
    
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    # Thống kê sử dụng
    so_lan_su_dung = models.PositiveIntegerField(default=0, verbose_name="Số lần sử dụng")
    so_lan_dung = models.PositiveIntegerField(default=0, verbose_name="Số lần đúng")
    
    class Meta:
        verbose_name = "Phương pháp tính toán"
        verbose_name_plural = "Các phương pháp tính toán"
        ordering = ['-ngay_cap_nhat']
    
    def __str__(self):
        return f"{self.ten_phuong_phap} ({self.get_loai_phuong_phap_display()})"
    
    @property
    def ty_le_thanh_cong(self):
        """Tỷ lệ thành công của phương pháp"""
        if self.so_lan_su_dung == 0:
            return 0
        return round((self.so_lan_dung / self.so_lan_su_dung) * 100, 2)
    
    def cap_nhat_ket_qua(self, ket_qua_dung: bool):
        """Cập nhật kết quả sử dụng phương pháp"""
        self.so_lan_su_dung += 1
        if ket_qua_dung:
            self.so_lan_dung += 1
        self.save(update_fields=['so_lan_su_dung', 'so_lan_dung'])


class DuDoanManager(models.Manager):
    def get_predictions_for_date_range(self, start_date, end_date):
        """Lấy dự đoán trong khoảng thời gian"""
        return self.filter(ngay_du_doan__range=[start_date, end_date])
    
    def get_best_predictions(self, ngay_du_doan, limit=10):
        """Lấy dự đoán tốt nhất cho một ngày"""
        return self.filter(ngay_du_doan=ngay_du_doan).order_by('-diem_tin_cay')[:limit]
    
    def get_predictions_by_method(self, phuong_phap_id):
        """Lấy dự đoán theo phương pháp"""
        return self.filter(phuong_phap_id=phuong_phap_id).order_by('-ngay_tao')


class DuDoan(models.Model):
    """Model lưu trữ các dự đoán số"""
    
    LOAI_SO_CHOICES = [
        ('2d', 'Số 2D'),
        ('3d', 'Số 3D'),
        ('bach_thu', 'Bạch thủ'),
        ('song_thu', 'Song thủ'),
        ('dan_de', 'Đàn de'),
        ('xiuchu', 'Xiên chu'),
    ]
    
    TRANG_THAI_CHOICES = [
        ('cho_ket_qua', 'Chờ kết quả'),
        ('trung', 'Trúng'),
        ('truot', 'Trượt'),
        ('huy', 'Hủy'),
    ]
    
    objects = DuDoanManager()
    
    phuong_phap = models.ForeignKey(
        PhuongPhapTinhToan,
        on_delete=models.CASCADE,
        verbose_name="Phương pháp"
    )
    
    # Thông tin dự đoán
    ngay_phan_tich = models.DateField(
        verbose_name="Ngày phân tích",
        help_text="Ngày dữ liệu được sử dụng để phân tích"
    )
    
    ngay_du_doan = models.DateField(
        verbose_name="Ngày dự đoán",
        help_text="Ngày dự kiến số sẽ về"
    )
    
    so_du_doan = models.CharField(
        max_length=10,
        verbose_name="Số dự đoán"
    )
    
    loai_so = models.CharField(
        max_length=20,
        choices=LOAI_SO_CHOICES,
        default='2d',
        verbose_name="Loại số"
    )
    
    # Điểm tin cậy và xác suất
    diem_tin_cay = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Điểm tin cậy (%)"
    )
    
    xac_suat = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Xác suất"
    )
    
    # Thông tin bổ sung
    ghi_chu = models.TextField(blank=True, verbose_name="Ghi chú")
    
    chi_tiet_phan_tich = models.JSONField(
        default=dict,
        verbose_name="Chi tiết phân tích",
        help_text="Lưu trữ chi tiết quá trình phân tích"
    )
    
    # Trạng thái và kết quả
    trang_thai = models.CharField(
        max_length=20,
        choices=TRANG_THAI_CHOICES,
        default='cho_ket_qua',
        verbose_name="Trạng thái"
    )
    
    ket_qua_thuc_te = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Kết quả thực tế"
    )
    
    # Metadata
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    nguoi_tao = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Người tạo"
    )
    
    class Meta:
        verbose_name = "Dự đoán"
        verbose_name_plural = "Các dự đoán"
        ordering = ['-ngay_du_doan', '-diem_tin_cay']
        unique_together = ['phuong_phap', 'ngay_du_doan', 'so_du_doan']
    
    def __str__(self):
        return f"{self.so_du_doan} - {self.ngay_du_doan} ({self.diem_tin_cay}%)"
    
    def kiem_tra_ket_qua(self):
        """Kiểm tra kết quả dự đoán với kết quả thực tế"""
        try:
            
            ket_qua = KetQuaXoSo.objects.get(ngay=self.ngay_du_doan)
            
            if self.loai_so == '2d':
                so_trung = ket_qua.get_all_2digit_numbers()
            else:
                so_trung = ket_qua.get_all_three_digit_numbers()
            
            if self.so_du_doan in so_trung:
                self.trang_thai = 'trung'
                self.ket_qua_thuc_te = self.so_du_doan
                self.phuong_phap.cap_nhat_ket_qua(True)
            else:
                self.trang_thai = 'truot'
                self.phuong_phap.cap_nhat_ket_qua(False)
            
            self.save(update_fields=['trang_thai', 'ket_qua_thuc_te'])
            return self.trang_thai == 'trung'
            
        except Exception as e:
            return False


class LoKhungManager(models.Manager):
    def get_active_frames(self):
        """Lấy các lô khung đang hoạt động"""
        return self.filter(trang_thai='active')
    
    def get_frames_for_date(self, target_date):
        """Lấy lô khung cho ngày cụ thể"""
        return self.filter(
            ngay_bat_dau__lte=target_date,
            ngay_ket_thuc__gte=target_date
        )


class LoKhung(models.Model):
    """Model quản lý lô khung 3 ngày"""
    
    TRANG_THAI_CHOICES = [
        ('active', 'Đang hoạt động'),
        ('completed', 'Hoàn thành'),
        ('expired', 'Hết hạn'),
        ('cancelled', 'Hủy bỏ'),
    ]
    
    objects = LoKhungManager()
    
    ten_lo_khung = models.CharField(max_length=200, verbose_name="Tên lô khung")
    
    # Thời gian hiệu lực
    ngay_bat_dau = models.DateField(verbose_name="Ngày bắt đầu")
    ngay_ket_thuc = models.DateField(verbose_name="Ngày kết thúc")
    
    # Danh sách số dự đoán
    danh_sach_so = models.JSONField(
        default=list,
        verbose_name="Danh sách số",
        help_text="Danh sách các số trong lô khung"
    )
    
    # Phương pháp sử dụng
    phuong_phap_chinh = models.ForeignKey(
        PhuongPhapTinhToan,
        on_delete=models.CASCADE,
        verbose_name="Phương pháp chính"
    )
    
    phuong_phap_phu = models.ManyToManyField(
        PhuongPhapTinhToan,
        related_name='lo_khung_phu',
        blank=True,
        verbose_name="Phương pháp phụ"
    )
    
    # Độ tin cậy và điểm số
    diem_tin_cay_tong = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Điểm tin cậy tổng"
    )
    
    ngay_co_kha_nang_cao_nhat = models.DateField(
        verbose_name="Ngày có khả năng cao nhất"
    )
    
    # Trạng thái và kết quả
    trang_thai = models.CharField(
        max_length=20,
        choices=TRANG_THAI_CHOICES,
        default='active',
        verbose_name="Trạng thái"
    )
    
    ket_qua_theo_ngay = models.JSONField(
        default=dict,
        verbose_name="Kết quả theo ngày",
        help_text="Lưu kết quả trúng/trượt theo từng ngày"
    )
    
    # Metadata
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    nguoi_tao = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Người tạo"
    )
    
    class Meta:
        verbose_name = "Lô khung"
        verbose_name_plural = "Các lô khung"
        ordering = ['-ngay_tao']
    
    def __str__(self):
        return f"{self.ten_lo_khung} ({self.ngay_bat_dau} - {self.ngay_ket_thuc})"
    
    @property
    def so_ngay_con_lai(self):
        """Số ngày còn lại của lô khung"""
        today = timezone.now().date()
        if today > self.ngay_ket_thuc:
            return 0
        return (self.ngay_ket_thuc - today).days + 1
    
    def cap_nhat_ket_qua_ngay(self, ngay, so_trung):
        """Cập nhật kết quả cho một ngày cụ thể"""
        ngay_str = ngay.strftime('%Y-%m-%d')
        
        if not self.ket_qua_theo_ngay:
            self.ket_qua_theo_ngay = {}
        
        so_trung_trong_khung = [so for so in so_trung if so in self.danh_sach_so]
        
        self.ket_qua_theo_ngay[ngay_str] = {
            'so_trung': so_trung_trong_khung,
            'tong_so_trung': len(so_trung_trong_khung),
            'ty_le_trung': len(so_trung_trong_khung) / len(self.danh_sach_so) * 100
        }
        
        # Cập nhật trạng thái nếu có số trúng
        if so_trung_trong_khung:
            self.trang_thai = 'completed'
        
        self.save(update_fields=['ket_qua_theo_ngay', 'trang_thai'])


class BaoCaoHieuQua(models.Model):
    """Model báo cáo hiệu quả của các phương pháp"""
    
    LOAI_BAO_CAO_CHOICES = [
        ('daily', 'Báo cáo hàng ngày'),
        ('weekly', 'Báo cáo hàng tuần'),
        ('monthly', 'Báo cáo hàng tháng'),
        ('custom', 'Báo cáo tùy chỉnh'),
    ]
    
    phuong_phap = models.ForeignKey(
        PhuongPhapTinhToan,
        on_delete=models.CASCADE,
        verbose_name="Phương pháp"
    )
    
    loai_bao_cao = models.CharField(
        max_length=20,
        choices=LOAI_BAO_CAO_CHOICES,
        verbose_name="Loại báo cáo"
    )
    
    # Khoảng thời gian báo cáo
    tu_ngay = models.DateField(verbose_name="Từ ngày")
    den_ngay = models.DateField(verbose_name="Đến ngày")
    
    # Thống kê cơ bản
    tong_so_du_doan = models.PositiveIntegerField(verbose_name="Tổng số dự đoán")
    so_du_doan_dung = models.PositiveIntegerField(verbose_name="Số dự đoán đúng")
    ty_le_thanh_cong = models.FloatField(verbose_name="Tỷ lệ thành công (%)")
    
    # Thống kê nâng cao
    diem_hieu_qua = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Điểm hiệu quả"
    )
    
    chi_so_on_dinh = models.FloatField(
        verbose_name="Chỉ số ổn định",
        help_text="Đánh giá độ ổn định của phương pháp"
    )
    
    ngay_dinh_cao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ngày đỉnh cao",
        help_text="Ngày có hiệu suất cao nhất"
    )
    
    muc_do_met_moi = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name="Mức độ mệt mỏi (%)"
    )
    
    # Chi tiết thống kê
    thong_ke_chi_tiet = models.JSONField(
        default=dict,
        verbose_name="Thống kê chi tiết"
    )
    
    # Gợi ý và khuyến nghị
    goi_y_cai_thien = models.TextField(
        blank=True,
        verbose_name="Gợi ý cải thiện"
    )
    
    muc_do_khuyen_cao = models.CharField(
        max_length=20,
        choices=[
            ('high', 'Khuyến cáo cao'),
            ('medium', 'Khuyến cáo trung bình'),
            ('low', 'Khuyến cáo thấp'),
            ('not_recommended', 'Không khuyến cáo'),
        ],
        default='medium',
        verbose_name="Mức độ khuyến cáo"
    )
    
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    
    class Meta:
        verbose_name = "Báo cáo hiệu quả"
        verbose_name_plural = "Các báo cáo hiệu quả"
        ordering = ['-ngay_tao']
        unique_together = ['phuong_phap', 'tu_ngay', 'den_ngay', 'loai_bao_cao']
    
    def __str__(self):
        return f"Báo cáo {self.phuong_phap.ten_phuong_phap} ({self.tu_ngay} - {self.den_ngay})"
    
    @classmethod
    def tao_bao_cao(cls, phuong_phap, tu_ngay, den_ngay, loai_bao_cao='custom'):
        """Tạo báo cáo hiệu quả cho một phương pháp"""
        
        # Lấy tất cả dự đoán trong khoảng thời gian
        du_doan_list = DuDoan.objects.filter(
            phuong_phap=phuong_phap,
            ngay_du_doan__range=[tu_ngay, den_ngay]
        )
        
        tong_so_du_doan = du_doan_list.count()
        so_du_doan_dung = du_doan_list.filter(trang_thai='trung').count()
        
        ty_le_thanh_cong = (so_du_doan_dung / tong_so_du_doan * 100) if tong_so_du_doan > 0 else 0
        
        # Tính toán các chỉ số nâng cao
        diem_hieu_qua = cls._tinh_diem_hieu_qua(du_doan_list)
        chi_so_on_dinh = cls._tinh_chi_so_on_dinh(du_doan_list)
        muc_do_met_moi = cls._tinh_muc_do_met_moi(du_doan_list)
        
        # Tìm ngày đỉnh cao
        ngay_dinh_cao = cls._tim_ngay_dinh_cao(du_doan_list)
        
        # Tạo thống kê chi tiết
        thong_ke_chi_tiet = cls._tao_thong_ke_chi_tiet(du_doan_list)
        
        # Tạo gợi ý cải thiện
        goi_y_cai_thien = cls._tao_goi_y_cai_thien(
            ty_le_thanh_cong, chi_so_on_dinh, muc_do_met_moi
        )
        
        # Xác định mức độ khuyến cáo
        muc_do_khuyen_cao = cls._xac_dinh_muc_do_khuyen_cao(
            ty_le_thanh_cong, chi_so_on_dinh, muc_do_met_moi
        )
        
        bao_cao = cls.objects.create(
            phuong_phap=phuong_phap,
            loai_bao_cao=loai_bao_cao,
            tu_ngay=tu_ngay,
            den_ngay=den_ngay,
            tong_so_du_doan=tong_so_du_doan,
            so_du_doan_dung=so_du_doan_dung,
            ty_le_thanh_cong=ty_le_thanh_cong,
            diem_hieu_qua=diem_hieu_qua,
            chi_so_on_dinh=chi_so_on_dinh,
            ngay_dinh_cao=ngay_dinh_cao,
            muc_do_met_moi=muc_do_met_moi,
            thong_ke_chi_tiet=thong_ke_chi_tiet,
            goi_y_cai_thien=goi_y_cai_thien,
            muc_do_khuyen_cao=muc_do_khuyen_cao
        )
        
        return bao_cao
    
    @staticmethod
    def _tinh_diem_hieu_qua(du_doan_list):
        """Tính điểm hiệu quả tổng hợp"""
        if not du_doan_list.exists():
            return 0
        
        # Tính dựa trên tỷ lệ thành công và độ tin cậy trung bình
        ty_le_thanh_cong = du_doan_list.filter(trang_thai='trung').count() / du_doan_list.count()
        diem_tin_cay_tb = du_doan_list.aggregate(
            avg_confidence=models.Avg('diem_tin_cay')
        )['avg_confidence'] or 0
        
        return round((ty_le_thanh_cong * 70 + diem_tin_cay_tb * 0.3), 2)
    
    @staticmethod
    def _tinh_chi_so_on_dinh(du_doan_list):
        """Tính chỉ số ổn định"""
        if du_doan_list.count() < 5:
            return 0
        
        # Phân tích biến động theo thời gian
        ngay_thanh_cong = defaultdict(int)
        ngay_tong = defaultdict(int)
        
        for du_doan in du_doan_list:
            ngay_str = du_doan.ngay_du_doan.strftime('%Y-%m-%d')
            ngay_tong[ngay_str] += 1
            if du_doan.trang_thai == 'trung':
                ngay_thanh_cong[ngay_str] += 1
        
        # Tính độ lệch chuẩn của tỷ lệ thành công theo ngày
        ty_le_theo_ngay = []
        for ngay, tong in ngay_tong.items():
            ty_le = ngay_thanh_cong[ngay] / tong if tong > 0 else 0
            ty_le_theo_ngay.append(ty_le)
        
        if len(ty_le_theo_ngay) < 2:
            return 50  # Giá trị mặc định
        
        std_dev = np.std(ty_le_theo_ngay)
        chi_so_on_dinh = max(0, 100 - (std_dev * 100))
        
        return round(chi_so_on_dinh, 2)
    
    @staticmethod
    def _tinh_muc_do_met_moi(du_doan_list):
        """Tính mức độ mệt mỏi của phương pháp"""
        if du_doan_list.count() < 10:
            return 0

        # Phân tích xu hướng giảm hiệu quả theo thời gian
        du_doan_sorted = list(du_doan_list.order_by('ngay_du_doan'))

        total_count = len(du_doan_sorted)
        nua_dau = du_doan_sorted[:total_count//2]
        nua_cuoi = du_doan_sorted[total_count//2:]

        def ty_le_trung(ds):
            if not ds:
                return 0
            trung = sum(1 for d in ds if d.trang_thai == 'trung')
            return trung / len(ds)

        ty_le_dau = ty_le_trung(nua_dau)
        ty_le_cuoi = ty_le_trung(nua_cuoi)

        # Mức độ mệt mỏi = mức độ giảm hiệu quả
        if ty_le_dau == 0:
            return 0

        giam_hieu_qua = max(0, (ty_le_dau - ty_le_cuoi) / ty_le_dau)
        return round(giam_hieu_qua * 100, 2)
    
    @staticmethod
    def _tim_ngay_dinh_cao(du_doan_list):
        """Tìm ngày có hiệu suất cao nhất"""
        ngay_thanh_cong = defaultdict(int)
        ngay_tong = defaultdict(int)
        
        for du_doan in du_doan_list:
            ngay = du_doan.ngay_du_doan
            ngay_tong[ngay] += 1
            if du_doan.trang_thai == 'trung':
                ngay_thanh_cong[ngay] += 1
        
        ngay_dinh_cao = None
        ty_le_cao_nhat = 0
        
        for ngay, tong in ngay_tong.items():
            if tong >= 3:  # Chỉ xét những ngày có ít nhất 3 dự đoán
                ty_le = ngay_thanh_cong[ngay] / tong
                if ty_le > ty_le_cao_nhat:
                    ty_le_cao_nhat = ty_le
                    ngay_dinh_cao = ngay
        
        return ngay_dinh_cao
    
    @staticmethod
    def _tao_thong_ke_chi_tiet(du_doan_list):
        """Tạo thống kê chi tiết"""
        thong_ke = {
            'phan_bo_theo_loai_so': {},
            'phan_bo_theo_diem_tin_cay': {},
            'xu_huong_theo_thoi_gian': {},
            'top_so_thanh_cong': {},
            'phan_tich_chu_ky': {}
        }
        
        # Phân bố theo loại số
        for du_doan in du_doan_list:
            loai = du_doan.loai_so
            if loai not in thong_ke['phan_bo_theo_loai_so']:
                thong_ke['phan_bo_theo_loai_so'][loai] = {'tong': 0, 'trung': 0}
            
            thong_ke['phan_bo_theo_loai_so'][loai]['tong'] += 1
            if du_doan.trang_thai == 'trung':
                thong_ke['phan_bo_theo_loai_so'][loai]['trung'] += 1
        
        # Phân bố theo điểm tin cậy
        for du_doan in du_doan_list:
            khoang = f"{int(du_doan.diem_tin_cay//10)*10}-{int(du_doan.diem_tin_cay//10)*10+9}"
            if khoang not in thong_ke['phan_bo_theo_diem_tin_cay']:
                thong_ke['phan_bo_theo_diem_tin_cay'][khoang] = {'tong': 0, 'trung': 0}
            
            thong_ke['phan_bo_theo_diem_tin_cay'][khoang]['tong'] += 1
            if du_doan.trang_thai == 'trung':
                thong_ke['phan_bo_theo_diem_tin_cay'][khoang]['trung'] += 1
        
        # Top số thành công
        so_thanh_cong = Counter()
        for du_doan in du_doan_list.filter(trang_thai='trung'):
            so_thanh_cong[du_doan.so_du_doan] += 1
        
        thong_ke['top_so_thanh_cong'] = dict(so_thanh_cong.most_common(10))
        
        return thong_ke
    
    @staticmethod
    def _tao_goi_y_cai_thien(ty_le_thanh_cong, chi_so_on_dinh, muc_do_met_moi):
        """Tạo gợi ý cải thiện"""
        goi_y = []
        
        if ty_le_thanh_cong < 30:
            goi_y.append("Tỷ lệ thành công thấp. Cần xem xét lại các tham số hoặc công thức tính toán.")
        
        if chi_so_on_dinh < 50:
            goi_y.append("Phương pháp thiếu ổn định. Nên điều chỉnh để giảm biến động.")
        
        if muc_do_met_moi > 60:
            goi_y.append("Phương pháp đang có dấu hiệu mệt mỏi. Cần nghỉ ngơi hoặc điều chỉnh.")
        
        if not goi_y:
            goi_y.append("Phương pháp đang hoạt động tốt. Tiếp tục theo dõi và duy trì.")
        
        return " ".join(goi_y)
    
    @staticmethod
    def _xac_dinh_muc_do_khuyen_cao(ty_le_thanh_cong, chi_so_on_dinh, muc_do_met_moi):
        """Xác định mức độ khuyến cáo"""
        diem_tong = 0
        
        # Điểm từ tỷ lệ thành công
        if ty_le_thanh_cong >= 60:
            diem_tong += 3
        elif ty_le_thanh_cong >= 40:
            diem_tong += 2
        elif ty_le_thanh_cong >= 20:
            diem_tong += 1
        
        # Điểm từ chỉ số ổn định
        if chi_so_on_dinh >= 70:
            diem_tong += 2
        elif chi_so_on_dinh >= 50:
            diem_tong += 1
        
        # Trừ điểm từ mức độ mệt mỏi
        if muc_do_met_moi >= 70:
            diem_tong -= 2
        elif muc_do_met_moi >= 40:
            diem_tong -= 1
        
        # Xác định mức độ khuyến cáo
        if diem_tong >= 4:
            return 'high'
        elif diem_tong >= 2:
            return 'medium'
        elif diem_tong >= 0:
            return 'low'
        else:
            return 'not_recommended'


class PhanTichSoLieu(models.Model):
    """Model phân tích số liệu cho từng ngày"""
    
    ngay_phan_tich = models.DateField(unique=True, verbose_name="Ngày phân tích")
    ket_qua_xo_so = models.ForeignKey(
        'results.KetQuaXoSo',  # Reference to existing model
        on_delete=models.CASCADE,
        verbose_name="Kết quả xổ số"
    )
    
    # Phân tích số liệu cơ bản
    so_2d_xuat_hien = models.JSONField(
        default=list,
        verbose_name="Số 2D xuất hiện"
    )
    
    so_3d_xuat_hien = models.JSONField(
        default=list,
        verbose_name="Số 3D xuất hiện"
    )
    
    # Thống kê đầu đuôi
    thong_ke_dau = models.JSONField(
        default=dict,
        verbose_name="Thống kê đầu số"
    )
    
    thong_ke_duoi = models.JSONField(
        default=dict,
        verbose_name="Thống kê đuôi số"
    )
    
    # Thống kê tổng và chạm
    thong_ke_tong = models.JSONField(
        default=dict,
        verbose_name="Thống kê tổng"
    )
    
    thong_ke_cham = models.JSONField(
        default=dict,
        verbose_name="Thống kê chạm"
    )
    
    # Phân tích chu kỳ
    phan_tich_chu_ky = models.JSONField(
        default=dict,
        verbose_name="Phân tích chu kỳ"
    )
    
    # Dự đoán cho 3 ngày tiếp theo
    du_doan_3_ngay = models.JSONField(
        default=dict,
        verbose_name="Dự đoán 3 ngày tiếp theo"
    )
    
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    ngay_cap_nhat = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    
    class Meta:
        verbose_name = "Phân tích số liệu"
        verbose_name_plural = "Các phân tích số liệu"
        ordering = ['-ngay_phan_tich']
    
    def __str__(self):
        return f"Phân tích {self.ngay_phan_tich}"
    
    @classmethod
    def tao_phan_tich_tu_dong(cls, ngay_phan_tich):
        """Tạo phân tích tự động cho một ngày"""
        try:
              # Import existing model
            ket_qua = KetQuaXoSo.objects.get(ngay=ngay_phan_tich)
            
            # Tạo hoặc cập nhật phân tích
            phan_tich, created = cls.objects.get_or_create(
                ngay_phan_tich=ngay_phan_tich,
                defaults={'ket_qua_xo_so': ket_qua}
            )
            
            # Thực hiện các phân tích
            phan_tich._phan_tich_so_lieu_co_ban()
            phan_tich._phan_tich_dau_duoi()
            phan_tich._phan_tich_tong_cham()
            phan_tich._phan_tich_chu_ky()
            phan_tich._tao_du_doan_3_ngay()
            
            phan_tich.save()
            return phan_tich
            
        except Exception as e:
            return None
    
    def _phan_tich_so_lieu_co_ban(self):
        """Phân tích số liệu cơ bản"""
        self.so_2d_xuat_hien = self.ket_qua_xo_so.get_all_2digit_numbers()
        self.so_3d_xuat_hien = self.ket_qua_xo_so.get_all_three_digit_numbers()
    
    def _phan_tich_dau_duoi(self):
        """Phân tích đầu đuôi"""
        dau_counts = defaultdict(int)
        duoi_counts = defaultdict(int)
        
        for so in self.so_2d_xuat_hien:
            dau_counts[so[0]] += 1
            duoi_counts[so[-1]] += 1
        
        self.thong_ke_dau = dict(dau_counts)
        self.thong_ke_duoi = dict(duoi_counts)
    
    def _phan_tich_tong_cham(self):
        """Phân tích tổng và chạm"""
        tong_counts = defaultdict(int)
        cham_counts = defaultdict(int)
        
        for so in self.so_2d_xuat_hien:
            # Tổng
            tong = sum(int(d) for d in so)
            tong_counts[tong] += 1
            
            # Chạm
            for digit in so:
                cham_counts[int(digit)] += 1
        
        self.thong_ke_tong = dict(tong_counts)
        self.thong_ke_cham = dict(cham_counts)
    
    def _phan_tich_chu_ky(self):
        """Phân tích chu kỳ các số"""
        
        chu_ky_data = {}
        
        # Phân tích chu kỳ cho từng số 2D
        for so in self.so_2d_xuat_hien:
            # Tìm lịch sử xuất hiện của số này
            lich_su = []
            ket_qua_truoc = KetQuaXoSo.objects.filter(
                ngay__lt=self.ngay_phan_tich
            ).order_by('-ngay')[:100]  # Lấy 100 ngày gần nhất
            
            for kq in ket_qua_truoc:
                if so in kq.get_all_2digit_numbers():
                    lich_su.append(kq.ngay)
            
            if len(lich_su) >= 2:
                # Tính chu kỳ trung bình
                chu_ky_list = []
                for i in range(len(lich_su) - 1):
                    chu_ky = (lich_su[i] - lich_su[i + 1]).days
                    chu_ky_list.append(chu_ky)
                
                chu_ky_data[so] = {
                    'chu_ky_tb': sum(chu_ky_list) / len(chu_ky_list),
                    'lan_cuoi': (self.ngay_phan_tich - lich_su[0]).days if lich_su else 0,
                    'so_lan_xuat_hien': len(lich_su)
                }
        
        self.phan_tich_chu_ky = chu_ky_data
    
    def _tao_du_doan_3_ngay(self):
        """Tạo dự đoán cho 3 ngày tiếp theo"""
        du_doan = {}
        
        # Dự đoán dựa trên chu kỳ
        for so, thong_tin in self.phan_tich_chu_ky.items():
            chu_ky_tb = thong_tin['chu_ky_tb']
            lan_cuoi = thong_tin['lan_cuoi']
            
            # Tính xác suất xuất hiện trong 3 ngày tới
            for ngay_thu in range(1, 4):
                ngay_du_doan = self.ngay_phan_tich + timedelta(days=ngay_thu)
                ngay_str = ngay_du_doan.strftime('%Y-%m-%d')
                
                if ngay_str not in du_doan:
                    du_doan[ngay_str] = {}
                
                # Tính xác suất dựa trên chu kỳ
                khoang_cach = lan_cuoi + ngay_thu
                xac_suat = max(0, min(1, 1 - abs(khoang_cach - chu_ky_tb) / chu_ky_tb))
                
                du_doan[ngay_str][so] = {
                    'xac_suat': round(xac_suat, 3),
                    'chu_ky_tb': chu_ky_tb,
                    'khoang_cach_hien_tai': khoang_cach
                }
        
        # Xác định ngày có khả năng cao nhất cho mỗi số
        for so in self.phan_tich_chu_ky.keys():
            xac_suat_cao_nhat = 0
            ngay_cao_nhat = None
            
            for ngay_str, so_dict in du_doan.items():
                if so in so_dict and so_dict[so]['xac_suat'] > xac_suat_cao_nhat:
                    xac_suat_cao_nhat = so_dict[so]['xac_suat']
                    ngay_cao_nhat = ngay_str
            
            if ngay_cao_nhat:
                du_doan[ngay_cao_nhat][so]['la_ngay_cao_nhat'] = True
        
        self.du_doan_3_ngay = du_doan


class CanhBaoHieuQua(models.Model):


    """Model cảnh báo về hiệu quả phương pháp"""
    
    LOAI_CANH_BAO_CHOICES = [
        ('hieu_qua_thap', 'Hiệu quả thấp'),
        ('khong_on_dinh', 'Không ổn định'),
        ('met_moi', 'Mệt mỏi'),
        ('ngung_hoat_dong', 'Ngừng hoạt động'),
        ('thanh_cong_cao', 'Thành công cao'),
    ]
    
    MUC_DO_CHOICES = [
        ('info', 'Thông tin'),
        ('warning', 'Cảnh báo'),
        ('critical', 'Nghiêm trọng'),
        ('success', 'Thành công'),
    ]
    
    phuong_phap = models.ForeignKey(
        PhuongPhapTinhToan,
        on_delete=models.CASCADE,
        verbose_name="Phương pháp"
    )
    
    loai_canh_bao = models.CharField(
        max_length=20,
        choices=LOAI_CANH_BAO_CHOICES,
        verbose_name="Loại cảnh báo"
    )
    
    muc_do = models.CharField(
        max_length=10,
        choices=MUC_DO_CHOICES,
        verbose_name="Mức độ"
    )
    
    tieu_de = models.CharField(max_length=200, verbose_name="Tiêu đề")
    noi_dung = models.TextField(verbose_name="Nội dung")
    
    gia_tri_hien_tai = models.FloatField(verbose_name="Giá trị hiện tại")
    nguong_canh_bao = models.FloatField(verbose_name="Ngưỡng cảnh báo")
    
    da_xu_ly = models.BooleanField(default=False, verbose_name="Đã xử lý")
    ghi_chu_xu_ly = models.TextField(blank=True, verbose_name="Ghi chú xử lý")
    
    ngay_canh_bao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày cảnh báo")
    ngay_xu_ly = models.DateTimeField(blank=True, null=True, verbose_name="Ngày xử lý")
    
    class Meta:
        verbose_name = "Cảnh báo hiệu quả"
        verbose_name_plural = "Các cảnh báo hiệu quả"
        ordering = ['-ngay_canh_bao']
    
    def __str__(self):
        return f"{self.tieu_de} - {self.phuong_phap.ten_phuong_phap}"
    
    def danh_dau_da_xu_ly(self, ghi_chu=""):
        """Đánh dấu cảnh báo đã được xử lý"""
        self.da_xu_ly = True
        self.ghi_chu_xu_ly = ghi_chu
        self.ngay_xu_ly = timezone.now()
        self.save(update_fields=['da_xu_ly', 'ghi_chu_xu_ly', 'ngay_xu_ly'])
    
    @classmethod
    def kiem_tra_va_tao_canh_bao(cls, phuong_phap):
        """Kiểm tra và tạo cảnh báo cho phương pháp"""
        canh_bao_list = []
        
        # Kiểm tra tỷ lệ thành công
        if phuong_phap.ty_le_thanh_cong < 20:
            canh_bao = cls.objects.create(
                phuong_phap=phuong_phap,
                loai_canh_bao='hieu_qua_thap',
                muc_do='warning',
                tieu_de=f"Hiệu quả thấp: {phuong_phap.ten_phuong_phap}",
                noi_dung=f"Tỷ lệ thành công chỉ đạt {phuong_phap.ty_le_thanh_cong}%, thấp hơn ngưỡng 20%.",
                gia_tri_hien_tai=phuong_phap.ty_le_thanh_cong,
                nguong_canh_bao=20.0
            )
            canh_bao_list.append(canh_bao)
        
        # Kiểm tra số lần sử dụng gần đây
        du_doan_gan_day = DuDoan.objects.filter(
            phuong_phap=phuong_phap,
            ngay_tao__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        if du_doan_gan_day == 0:
            canh_bao = cls.objects.create(
                phuong_phap=phuong_phap,
                loai_canh_bao='ngung_hoat_dong',
                muc_do='info',
                tieu_de=f"Không hoạt động: {phuong_phap.ten_phuong_phap}",
                noi_dung="Phương pháp không được sử dụng trong 7 ngày qua.",
                gia_tri_hien_tai=du_doan_gan_day,
                nguong_canh_bao=1.0
            )
            canh_bao_list.append(canh_bao)
        
        return canh_bao_list
    
class PredictionMethodBtlManager(models.Manager):
    """Custom manager cho PredictionMethodBtl với các truy vấn tối ưu"""
    
    def get_top_performers(self, limit=10, period_days=30):
        """Lấy các phương pháp hiệu suất cao nhất"""
        from django.utils import timezone
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        return self.filter(
            is_active=True,
            results_btl__dan_btl__analysis_date__range=[start_date, end_date]
        ).annotate(
            recent_success_rate=models.Avg('results_btl__hit_rate'),
            recent_predictions=models.Count('results_btl')
        ).filter(
            recent_predictions__gte=5  # Ít nhất 5 dự đoán gần đây
        ).order_by('-recent_success_rate')[:limit]
    
    def get_performance_summary(self, method_id, period_days=30):
        """Lấy tóm tắt hiệu suất cho một phương pháp"""
        from django.utils import timezone
        from django.db.models import Avg, Count, Max, Min
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        return self.filter(id=method_id).annotate(
            period_predictions=Count(
                'results_btl',
                filter=models.Q(results_btl__dan_btl__analysis_date__range=[start_date, end_date])
            ),
            period_avg_hits=Avg(
                'results_btl__hit_count',
                filter=models.Q(results_btl__dan_btl__analysis_date__range=[start_date, end_date])
            ),
            period_max_hits=Max(
                'results_btl__hit_count',
                filter=models.Q(results_btl__dan_btl__analysis_date__range=[start_date, end_date])
            ),
            period_success_rate=Avg(
                'results_btl__hit_rate',
                filter=models.Q(results_btl__dan_btl__analysis_date__range=[start_date, end_date])
            )
        ).first()


class DanBtlManager(models.Manager):
    """Custom manager cho DanBtl với các truy vấn tối ưu"""
    
    def get_date_range_with_stats(self, start_date, end_date):
        """Lấy dữ liệu trong khoảng thời gian với thống kê"""
        return self.filter(
            analysis_date__range=[start_date, end_date]
        ).select_related().prefetch_related(
            'predictions_btl__method'
        ).order_by('-analysis_date')
    
    def get_best_performing_days(self, limit=10):
        """Lấy các ngày có hiệu suất tốt nhất"""
        return self.filter(
            has_actual_result=True
        ).order_by('-best_method_hit_count', '-avg_hit_rate')[:limit]




class PredictionMethodBtl(models.Model):
    """
    Model lưu trữ thông tin về các phương pháp dự đoán - Được tối ưu hóa
    """
    objects = PredictionMethodBtlManager()
    code = models.CharField(
        max_length=50, 
        unique=True,  # Đảm bảo mã phương pháp duy nhất
        verbose_name="Mã phương pháp",
        db_index=True  # Tăng tốc truy vấn
    )
    name = models.CharField(max_length=200, verbose_name="Tên phương pháp")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    category = models.CharField(
        max_length=50,
        choices=[
            ('traditional', 'Phương pháp truyền thống'),
            ('statistical', 'Phương pháp thống kê'),
            ('ml', 'Machine Learning'),
            ('hybrid', 'Kết hợp')
        ],
        default='traditional',
        verbose_name="Loại phương pháp",
        db_index=True
    )
    
    # Thêm các thông số cấu hình
    parameters = models.JSONField(
        default=dict,
        verbose_name="Tham số cấu hình",
        help_text="Lưu các tham số cấu hình của phương pháp"
    )
    
    # Trạng thái và hiệu suất
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    priority = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Độ ưu tiên",
        help_text="1 = cao nhất, 10 = thấp nhất"
    )
    
    # Thống kê tổng hợp - Denormalization để tăng tốc báo cáo
    total_predictions = models.IntegerField(default=0, verbose_name="Tổng số dự đoán")
    total_hits = models.IntegerField(default=0, verbose_name="Tổng số trúng")
    success_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Tỷ lệ thành công (%)"
    )
    avg_hit_count = models.FloatField(default=0.0, verbose_name="Số trúng trung bình")
    
    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name="Lần sử dụng cuối")

    class Meta:
        verbose_name = "Phương pháp dự đoán"
        verbose_name_plural = "Các phương pháp dự đoán"
        ordering = ['priority', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['success_rate']),
            models.Index(fields=['-last_used_at']),
        ]
        
    def __str__(self):
        return f"{self.name} ({self.success_rate:.1f}%)"
    
    def update_statistics(self):
        """Cập nhật thống kê tổng hợp từ kết quả dự đoán"""
        from django.db.models import Count, Sum, Avg
        
        stats = self.results_btl.aggregate(
            total_predictions=Count('id'),
            total_hits=Sum('hit_count'),
            avg_hit_count=Avg('hit_count')
        )
        
        self.total_predictions = stats['total_predictions'] or 0
        self.total_hits = stats['total_hits'] or 0
        self.avg_hit_count = stats['avg_hit_count'] or 0
        
        if self.total_predictions > 0:
            # Tính tỷ lệ thành công (có ít nhất 1 số trúng)
            successful_predictions = self.results_btl.filter(hit_count__gt=0).count()
            self.success_rate = (successful_predictions / self.total_predictions) * 100
        else:
            self.success_rate = 0
            
        self.last_used_at = timezone.now()
        self.save(update_fields=['total_predictions', 'total_hits', 'success_rate', 
                                'avg_hit_count', 'last_used_at'])


class DanBtl(models.Model):
    """
    Model chính được tối ưu hóa cho khả năng mở rộng và báo cáo
    """
    objects = DanBtlManager()
    analysis_date = models.DateField(
        verbose_name="Ngày phân tích",
        db_index=True  # Quan trọng cho truy vấn theo ngày
    )
    next_day_date = models.DateField(verbose_name="Ngày kế tiếp")
    
    # Thông tin kết quả ngày tiếp theo
    prize_next_day = models.CharField(max_length=500, verbose_name="Giải trúng ngày sau", blank=True)
    has_actual_result = models.BooleanField(default=False, verbose_name="Đã có kết quả thực tế")
    
    # Thống kê tổng hợp cho ngày này - Denormalization
    total_methods_used = models.IntegerField(default=0, verbose_name="Số phương pháp sử dụng")
    total_predictions_made = models.IntegerField(default=0, verbose_name="Tổng số dự đoán")
    total_hits_achieved = models.IntegerField(default=0, verbose_name="Tổng số trúng")
    best_method_hit_count = models.IntegerField(default=0, verbose_name="Số trúng cao nhất")
    avg_hit_rate = models.FloatField(default=0.0, verbose_name="Tỷ lệ trúng trung bình")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian xử lý")

    class Meta:
        verbose_name = "Dàn bạch thủ lô"
        verbose_name_plural = "Các dàn bạch thủ lô"
        ordering = ['-analysis_date']
        indexes = [
            models.Index(fields=['analysis_date']),
            models.Index(fields=['next_day_date']),
            models.Index(fields=['has_actual_result']),
            models.Index(fields=['-best_method_hit_count']),
            models.Index(fields=['analysis_date', 'has_actual_result']),  # Composite index
        ]
        unique_together = [['analysis_date']]  # Đảm bảo mỗi ngày chỉ có 1 bản ghi

    def __str__(self):
        return f"Dàn đề ngày {self.analysis_date.strftime('%d/%m/%Y')}"
    
    def update_statistics(self):
        """Cập nhật thống kê tổng hợp từ các kết quả dự đoán"""
        from django.db.models import Count, Sum, Max, Avg
        
        stats = self.predictions_btl.aggregate(
            total_methods=Count('method', distinct=True),
            total_predictions=Count('id'),
            total_hits=Sum('hit_count'),
            best_hit_count=Max('hit_count'),
            avg_hit_count=Avg('hit_count')
        )
        
        self.total_methods_used = stats['total_methods'] or 0
        self.total_predictions_made = stats['total_predictions'] or 0
        self.total_hits_achieved = stats['total_hits'] or 0
        self.best_method_hit_count = stats['best_hit_count'] or 0
        self.avg_hit_rate = stats['avg_hit_count'] or 0
        
        self.save(update_fields=[
            'total_methods_used', 'total_predictions_made', 'total_hits_achieved',
            'best_method_hit_count', 'avg_hit_rate'
        ])
    
    @classmethod
    def create_for_date(cls, analysis_date):
        """Tạo bản ghi cho một ngày cụ thể - Được tối ưu hóa"""
        try:
            from results.methods_btl import get_all_methods
            from results.models import KetQuaXoSo
            
            # Lấy dữ liệu kết quả xổ số cho ngày phân tích
            result = KetQuaXoSo.objects.get(ngay=analysis_date)
            next_day_date = analysis_date + timedelta(days=1)
            next_day_result = KetQuaXoSo.objects.filter(ngay=next_day_date).first()
            
            # Lấy giải đặc biệt của ngày tiếp theo
            prize_next_day = ''
            has_actual_result = False
            if next_day_result and hasattr(next_day_result, 'giai_db'):
                if next_day_result.giai_db:
                    prize_next_day = next_day_result.giai_db
                    has_actual_result = True
            
            # Tạo bản ghi DanBtl với thống kê ban đầu
            dan_btl, created = cls.objects.update_or_create(
                analysis_date=analysis_date,
                defaults={
                    'next_day_date': next_day_date,
                    'prize_next_day': prize_next_day,
                    'has_actual_result': has_actual_result,
                    'processed_at': timezone.now(),
                }
            )
            
            # Chuẩn bị dữ liệu đầu vào
            input_data = {
                'giai_db': result.giai_db or '',
                'giai_1': result.giai_1 or '',
                'giai_2_1': result.giai_2_1 or '',
                'giai_2_2': result.giai_2_2 or '',
                # ... các giải khác
            }
            
            # Chạy các phương pháp dự đoán
            methods = get_all_methods()
            for method in methods:
                method.create_prediction(dan_btl, input_data, next_day_result)
            
            # Cập nhật thống kê sau khi tạo xong các dự đoán
            dan_btl.update_statistics()
            
            return dan_btl
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo dàn đề cho ngày {analysis_date}: {str(e)}", exc_info=True)
            return None


class PredictionResultBtl(models.Model):
    """
    Model lưu trữ kết quả dự đoán - Được tối ưu hóa cho báo cáo
    """
    dan_btl = models.ForeignKey(
        DanBtl, 
        on_delete=models.CASCADE, 
        related_name='predictions_btl',
        db_index=True
    )
    method = models.ForeignKey(
        PredictionMethodBtl, 
        on_delete=models.CASCADE, 
        related_name='results_btl',
        db_index=True
    )
    
    # Dữ liệu dự đoán
    predicted_numbers = models.JSONField(verbose_name="Các số dự đoán", default=list)
    winning_numbers = models.JSONField(verbose_name="Các số trúng", default=list)
    
    # Thống kê kết quả
    hit_count = models.IntegerField(default=0, verbose_name="Số lượng trúng", db_index=True)
    prediction_count = models.IntegerField(default=0, verbose_name="Số lượng dự đoán")
    hit_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Tỷ lệ trúng (%)"
    )
    
    # Chi tiết về loại dự đoán
    is_special_prize = models.BooleanField(default=False, verbose_name="Là đặc biệt")
    digit_count = models.IntegerField(default=2, verbose_name="Số chữ số")
    
    # Thông tin bổ sung
    confidence_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Điểm tin cậy"
    )
    execution_time_ms = models.IntegerField(default=0, verbose_name="Thời gian thực thi (ms)")
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Kết quả dự đoán Bạch thủ lô"
        verbose_name_plural = "Các kết quả dự đoán Bạch thủ lô"
        ordering = ['-hit_count', '-confidence_score']
        indexes = [
            models.Index(fields=['dan_btl', 'method']),
            models.Index(fields=['hit_count']),
            models.Index(fields=['method', 'hit_count']),
            models.Index(fields=['-hit_rate']),
        ]
        unique_together = [['dan_btl', 'method']]  # Mỗi phương pháp chỉ có 1 kết quả cho 1 ngày
        
    def __str__(self):
        return f"{self.method.name} - {self.dan_btl.analysis_date.strftime('%d/%m/%Y')} ({self.hit_count} trúng)"
    
    def save(self, *args, **kwargs):
        """Override save để tự động tính toán các thống kê"""
        # Tính toán tỷ lệ trúng
        if self.prediction_count > 0:
            self.hit_rate = (self.hit_count / self.prediction_count) * 100
        else:
            self.hit_rate = 0
            
        # Tính số lượng dự đoán nếu chưa có
        if not self.prediction_count and self.predicted_numbers:
            self.prediction_count = len(self.predicted_numbers)
            
        super().save(*args, **kwargs)
        
        # Cập nhật thống kê cho method và dan_btl nếu có methods
        if hasattr(self.method, 'update_statistics'):
            self.method.update_statistics()
        if hasattr(self.dan_btl, 'update_statistics'):
            self.dan_btl.update_statistics()
            

# Model mới cho báo cáo hiệu suất
class MethodPerformanceReport(models.Model):
    """
    Model lưu trữ báo cáo hiệu suất của các phương pháp theo khoảng thời gian
    """
    PERIOD_CHOICES = [
        ('daily', 'Hàng ngày'),
        ('weekly', 'Hàng tuần'),
        ('monthly', 'Hàng tháng'),
        ('quarterly', 'Hàng quý'),
        ('yearly', 'Hàng năm'),
    ]
    
    method = models.ForeignKey(
        PredictionMethodBtl,
        on_delete=models.CASCADE,
        related_name='performance_reports'
    )
    
    # Khoảng thời gian báo cáo
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    start_date = models.DateField(verbose_name="Ngày bắt đầu")
    end_date = models.DateField(verbose_name="Ngày kết thúc")
    
    # Thống kê hiệu suất
    total_predictions = models.IntegerField(default=0)
    total_hits = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    avg_hit_count = models.FloatField(default=0.0)
    max_hit_count = models.IntegerField(default=0)
    min_hit_count = models.IntegerField(default=0)
    
    # Thống kê nâng cao
    consistency_score = models.FloatField(default=0.0, verbose_name="Điểm ổn định")
    trend_direction = models.CharField(
        max_length=10,
        choices=[('up', 'Tăng'), ('down', 'Giảm'), ('stable', 'Ổn định')],
        default='stable'
    )
    
    # Xếp hạng
    rank_by_success_rate = models.IntegerField(default=0)
    rank_by_avg_hits = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Báo cáo hiệu suất phương pháp"
        verbose_name_plural = "Các báo cáo hiệu suất phương pháp"
        unique_together = [['method', 'period_type', 'start_date', 'end_date']]
        indexes = [
            models.Index(fields=['method', 'period_type']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['-success_rate']),
            models.Index(fields=['-avg_hit_count']),
        ]


# Model mới cho thống kê tổng hợp
class DailyMethodStats(models.Model):
    """
    Model lưu trữ thống kê hàng ngày của từng phương pháp - Tối ưu cho truy vấn nhanh
    """
    method = models.ForeignKey(
        PredictionMethodBtl,
        on_delete=models.CASCADE,
        related_name='daily_stats'
    )
    date = models.DateField(verbose_name="Ngày")
    
    # Thống kê cơ bản
    predictions_made = models.IntegerField(default=0)
    hits_achieved = models.IntegerField(default=0)
    hit_rate = models.FloatField(default=0.0)
    
    # Thống kê chi tiết
    max_hits_in_prediction = models.IntegerField(default=0)
    avg_confidence = models.FloatField(default=0.0)
    execution_time_avg = models.FloatField(default=0.0)
    
    # Xếp hạng trong ngày
    daily_rank = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Thống kê hàng ngày phương pháp"
        verbose_name_plural = "Các thống kê hàng ngày phương pháp"
        unique_together = [['method', 'date']]
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['method', 'date']),
            models.Index(fields=['-hit_rate']),
            models.Index(fields=['date', '-hit_rate']),
        ]

