from django import forms
from .models import CalculationMethod
from django.core.validators import MinLengthValidator
from .bach_thu_methods import get_all_bach_thu_methods
import logging
logger = logging.getLogger(__name__)
from django.utils import timezone
class ImportKetQuaForm(forms.Form):
    data_input = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 15,
            'placeholder': '''Dán dữ liệu vào đây theo định dạng:
Thứ hai\t\tNgày: 28/04/2025
Giải ĐB\t\t75140
Giải nhất\t\t16674
Giải nhì\t\t26182 - 65386
...'''
        }),
        label='Nhập dữ liệu xổ số'
    )

class CalculationMethodForm(forms.ModelForm):
    class Meta:
        model = CalculationMethod
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Tên phương pháp',
            'description': 'Mô tả',
            'is_active': 'Kích hoạt'
        }



class BachThuPredictionForm(forms.Form):
    REGION_CHOICES = [
        ('mb', 'Miền Bắc'),
        ('mn', 'Miền Nam'),
        ('mt', 'Miền Trung'),
    ]
    
    prediction_date = forms.DateField(
        label='Ngày dự đoán',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',  # HTML5 date picker
            'max': timezone.now().strftime('%Y-%m-%d')  # Giới hạn ngày tối đa là hôm nay
        }),
        initial=timezone.now().date(),
        help_text="Chọn ngày bạn muốn dự đoán kết quả xổ số."
    )
    
    # Số ngày dữ liệu lịch sử muốn sử dụng để dự đoán
    history_days = forms.IntegerField(
        label='Số ngày dữ liệu lịch sử',
        min_value=1,
        max_value=30,
        initial=7,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
        }),
        help_text="Số ngày dữ liệu quá khứ để phân tích (1-30 ngày)."
    )
    
    region_code = forms.ChoiceField(
        label='Khu vực',
        choices=REGION_CHOICES,
        initial='mb',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tạo danh sách các phương pháp có sẵn với xử lý lỗi
        try:
            from bach_thu_methods import get_all_bach_thu_methods
            methods = get_all_bach_thu_methods()
            method_choices = [(method.get_code(), method.get_name()) for method in methods]
        except Exception as e:
            logger.error(f"Error loading bach thu methods: {e}")
            method_choices = []  # Danh sách trống nếu có lỗi
        
        self.fields['method_codes'] = forms.MultipleChoiceField(
            label='Chọn phương pháp',
            choices=method_choices,
            widget=forms.CheckboxSelectMultiple,
            required=False,
            help_text="Không chọn sẽ sử dụng tất cả các phương pháp."
        )

# forms.py

from django import forms
from .models import NumberFrequencyStats

class NumberFrequencyStatsForm(forms.ModelForm):
    """Form để tạo/cập nhật dữ liệu tần suất số"""
    
    class Meta:
        model = NumberFrequencyStats
        fields = ['number', 'date', 'appeared_in_special', 'appeared_in_first', 'appeared_in_other']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def clean_number(self):
        number = self.cleaned_data.get('number')
        if number:
            # Đảm bảo số có 2 chữ số
            try:
                number = number.zfill(2)[-2:]
            except:
                number = str(int(number)).zfill(2)[-2:]
        return number


class BulkImportForm(forms.Form):
    """Form để nhập dữ liệu hàng loạt"""
    
    IMPORT_CHOICES = [
        ('csv', 'Nhập từ file CSV'),
        ('ketquaxoso', 'Nhập từ dữ liệu KetQuaXoSo'),
    ]
    
    import_type = forms.ChoiceField(
        choices=IMPORT_CHOICES,
        widget=forms.RadioSelect,
        initial='ketquaxoso',
        label="Loại nhập dữ liệu"
    )
    
    csv_file = forms.FileField(
        required=False,
        label="File CSV",
        help_text="Tải lên file CSV với các cột: number, date, appeared_in_special, appeared_in_first, appeared_in_other"
    )
    
    import_from_ketquaxoso = forms.BooleanField(
        required=False,
        initial=True,
        label="Nhập từ KetQuaXoSo",
        help_text="Lấy dữ liệu từ model KetQuaXoSo"
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Ngày bắt đầu"
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Ngày kết thúc"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        import_type = cleaned_data.get('import_type')
        
        if import_type == 'csv' and not cleaned_data.get('csv_file'):
            self.add_error('csv_file', "Vui lòng chọn file CSV để tải lên.")
            
        if import_type == 'ketquaxoso':
            cleaned_data['import_from_ketquaxoso'] = True
            
        return cleaned_data