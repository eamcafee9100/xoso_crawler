import json
from datetime import date, timedelta

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import BaoCaoHieuQua, DuDoan, LoKhung, PhanTichSoLieu, PhuongPhapTinhToan


class PhuongPhapTinhToanForm(forms.ModelForm):
    """Form cho phương pháp tính toán"""

    class Meta:
        model = PhuongPhapTinhToan
        fields = [
            "ten_phuong_phap",
            "loai_phuong_phap",
            "mo_ta",
            "tham_so_config",
            "cong_thuc",
            "trong_so",
            "do_tin_cay",
            "trang_thai",
        ]
        widgets = {
            "ten_phuong_phap": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nhập tên phương pháp"}
            ),
            "loai_phuong_phap": forms.Select(attrs={"class": "form-control"}),
            "mo_ta": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Mô tả phương pháp...",
                }
            ),
            "tham_so_config": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": '{"param1": "value1", "param2": "value2"}',
                }
            ),
            "cong_thuc": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Nhập công thức hoặc thuật toán...",
                }
            ),
            "trong_so": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.1",
                    "min": "0.1",
                    "max": "10.0",
                }
            ),
            "do_tin_cay": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.0",
                    "max": "1.0",
                }
            ),
            "trang_thai": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_tham_so_config(self):
        """Validate JSON format"""
        tham_so_config = self.cleaned_data["tham_so_config"]
        if tham_so_config:
            try:
                json.loads(tham_so_config)
            except ValueError:
                raise ValidationError("Tham số cấu hình phải là JSON hợp lệ")
        return tham_so_config


class DuDoanForm(forms.ModelForm):
    """Form cho dự đoán"""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["phuong_phap"].queryset = PhuongPhapTinhToan.objects.filter(
                nguoi_tao=self.user, trang_thai="active"
            )

    class Meta:
        model = DuDoan
        fields = [
            "phuong_phap",
            "ngay_phan_tich",
            "ngay_du_doan",
            "so_du_doan",
            "loai_so",
            "diem_tin_cay",
            "xac_suat",
            "ghi_chu",
            "chi_tiet_phan_tich",
        ]
        widgets = {
            "phuong_phap": forms.Select(attrs={"class": "form-control"}),
            "ngay_phan_tich": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "ngay_du_doan": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "so_du_doan": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "VD: 12, 123"}
            ),
            "loai_so": forms.Select(attrs={"class": "form-control"}),
            "diem_tin_cay": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "min": "0", "max": "100"}
            ),
            "xac_suat": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "1"}
            ),
            "ghi_chu": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "chi_tiet_phan_tich": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": '{"key": "value"}',
                }
            ),
        }

    def clean_ngay_du_doan(self):
        """Validate ngày dự đoán"""
        ngay_du_doan = self.cleaned_data["ngay_du_doan"]
        if ngay_du_doan < date.today():
            raise ValidationError("Ngày dự đoán không thể là ngày trong quá khứ")
        return ngay_du_doan

    def clean_so_du_doan(self):
        """Validate số dự đoán"""
        so_du_doan = self.cleaned_data["so_du_doan"]
        loai_so = self.cleaned_data.get("loai_so")

        if loai_so in ["2d"]:
            if not (so_du_doan.isdigit() and len(so_du_doan) == 2):
                raise ValidationError("Số 2D phải có đúng 2 chữ số")
        elif loai_so in ["3d"]:
            if not (so_du_doan.isdigit() and len(so_du_doan) == 3):
                raise ValidationError("Số 3D phải có đúng 3 chữ số")

        return so_du_doan

    def clean_chi_tiet_phan_tich(self):
        """Validate JSON format"""
        chi_tiet = self.cleaned_data["chi_tiet_phan_tich"]
        if chi_tiet:
            try:
                json.loads(chi_tiet)
            except ValueError:
                raise ValidationError("Chi tiết phân tích phải là JSON hợp lệ")
        return chi_tiet


class LoKhungForm(forms.ModelForm):
    """Form cho lô khung"""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["phuong_phap_chinh"].queryset = (
                PhuongPhapTinhToan.objects.filter(nguoi_tao=self.user)
            )
            self.fields["phuong_phap_phu"].queryset = PhuongPhapTinhToan.objects.filter(
                nguoi_tao=self.user
            )

    class Meta:
        model = LoKhung
        fields = [
            "ten_lo_khung",
            "ngay_bat_dau",
            "ngay_ket_thuc",
            "danh_sach_so",
            "phuong_phap_chinh",
            "phuong_phap_phu",
            "diem_tin_cay_tong",
            "ngay_co_kha_nang_cao_nhat",
        ]
        widgets = {
            "ten_lo_khung": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nhập tên lô khung"}
            ),
            "ngay_bat_dau": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "ngay_ket_thuc": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "danh_sach_so": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": '["12", "34", "56"]',
                }
            ),
            "phuong_phap_chinh": forms.Select(attrs={"class": "form-control"}),
            "phuong_phap_phu": forms.SelectMultiple(attrs={"class": "form-control"}),
            "diem_tin_cay_tong": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1", "min": "0", "max": "100"}
            ),
            "ngay_co_kha_nang_cao_nhat": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def clean_danh_sach_so(self):
        danh_sach_so = self.cleaned_data.get("danh_sach_so")
        # Nếu là string thì mới json.loads, nếu đã là list thì giữ nguyên
        if isinstance(danh_sach_so, str):
            try:
                so_list = json.loads(danh_sach_so)
            except Exception:
                raise forms.ValidationError(
                    "Danh sách số không hợp lệ (không phải JSON hợp lệ)."
                )
        elif isinstance(danh_sach_so, list):
            so_list = danh_sach_so
        else:
            raise forms.ValidationError("Kiểu dữ liệu danh_sach_so không hợp lệ.")
        # ... các kiểm tra khác ...
        return so_list

    def clean_ngay_ket_thuc(self):
        """Validate khoảng thời gian"""
        ngay_bat_dau = self.cleaned_data.get("ngay_bat_dau")
        ngay_ket_thuc = self.cleaned_data["ngay_ket_thuc"]

        if ngay_bat_dau and ngay_ket_thuc:
            if ngay_ket_thuc <= ngay_bat_dau:
                raise ValidationError("Ngày kết thúc phải sau ngày bắt đầu")

            # Kiểm tra không quá 7 ngày
            if (ngay_ket_thuc - ngay_bat_dau).days > 7:
                raise ValidationError("Lô khung không được quá 7 ngày")

        return ngay_ket_thuc

   

class BaoCaoHieuQuaForm(forms.ModelForm):
    """Form cho báo cáo hiệu quả"""

    class Meta:
        model = BaoCaoHieuQua
        fields = ["phuong_phap", "loai_bao_cao", "tu_ngay", "den_ngay"]
        widgets = {
            "phuong_phap": forms.Select(attrs={"class": "form-control"}),
            "loai_bao_cao": forms.Select(attrs={"class": "form-control"}),
            "tu_ngay": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "den_ngay": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def clean_den_ngay(self):
        """Validate khoảng thời gian"""
        tu_ngay = self.cleaned_data.get("tu_ngay")
        den_ngay = self.cleaned_data["den_ngay"]

        if tu_ngay and den_ngay:
            if den_ngay <= tu_ngay:
                raise ValidationError("Đến ngày phải sau từ ngày")

            # Không quá 1 năm
            if (den_ngay - tu_ngay).days > 365:
                raise ValidationError("Khoảng thời gian báo cáo không được quá 1 năm")

        return den_ngay


class PhanTichSoLieuForm(forms.ModelForm):
    """Form cho phân tích số liệu"""

    class Meta:
        model = PhanTichSoLieu
        fields = ["ngay_phan_tich"]
        widgets = {
            "ngay_phan_tich": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }


class DateRangeForm(forms.Form):
    """Form chọn khoảng thời gian"""

    tu_ngay = forms.DateField(
        label="Từ ngày",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    den_ngay = forms.DateField(
        label="Đến ngày",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )

    def clean_den_ngay(self):
        tu_ngay = self.cleaned_data.get("tu_ngay")
        den_ngay = self.cleaned_data["den_ngay"]

        if tu_ngay and den_ngay and den_ngay <= tu_ngay:
            raise ValidationError("Đến ngày phải sau từ ngày")

        return den_ngay


class SearchForm(forms.Form):
    """Form tìm kiếm chung"""

    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nhập từ khóa tìm kiếm..."}
        ),
    )

    sort = forms.ChoiceField(
        choices=[
            ("-ngay_tao", "Mới nhất"),
            ("ngay_tao", "Cũ nhất"),
            ("-diem_tin_cay", "Tin cậy cao nhất"),
            ("diem_tin_cay", "Tin cậy thấp nhất"),
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )


from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import PredictionMethodBtl


class DateRangeForm(forms.Form):
    """Form chọn khoảng thời gian cho báo cáo"""

    start_date = forms.DateField(
        label="Từ ngày",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    end_date = forms.DateField(
        label="Đến ngày",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thiết lập giá trị mặc định
        today = timezone.now().date()
        self.fields["end_date"].initial = today
        self.fields["start_date"].initial = today - timedelta(days=30)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("Ngày bắt đầu phải trước ngày kết thúc")

            if (end_date - start_date).days > 365:
                raise forms.ValidationError(
                    "Khoảng thời gian không được vượt quá 365 ngày"
                )

        return cleaned_data


class MethodComparisonForm(forms.Form):
    """Form chọn phương pháp để so sánh"""

    methods = forms.ModelMultipleChoiceField(
        queryset=PredictionMethodBtl.objects.filter(is_active=True),
        label="Chọn phương pháp",
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=True,
    )

    def clean_methods(self):
        methods = self.cleaned_data["methods"]
        if len(methods) < 2:
            raise forms.ValidationError(
                "Vui lòng chọn ít nhất 2 phương pháp để so sánh"
            )
        if len(methods) > 10:
            raise forms.ValidationError("Không thể so sánh quá 10 phương pháp cùng lúc")
        return methods


class ReportFilterForm(forms.Form):
    """Form filter cho báo cáo"""

    PERIOD_CHOICES = [
        (7, "7 ngày gần nhất"),
        (30, "30 ngày gần nhất"),
        (90, "90 ngày gần nhất"),
        (365, "1 năm gần nhất"),
        (0, "Tùy chọn"),
    ]

    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        label="Khoảng thời gian",
        widget=forms.Select(attrs={"class": "form-control"}),
        initial=30,
    )

    category = forms.ChoiceField(
        label="Loại phương pháp",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )

    min_predictions = forms.IntegerField(
        label="Số dự đoán tối thiểu",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1, "value": 5}),
        initial=5,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thiết lập choices cho category
        categories = [("", "Tất cả")] + list(
            PredictionMethodBtl._meta.get_field("category").choices
        )
        self.fields["category"].choices = categories
