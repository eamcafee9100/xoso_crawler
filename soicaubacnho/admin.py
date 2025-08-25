from django.contrib import admin

# Register your models here.
from .models import SoiCauBacNho, ThongKeHieuQua, QuyLuatBacNho, MethodWeight

@admin.register(MethodWeight)
class MethodWeightAdmin(admin.ModelAdmin):
    list_display = ('method_name', 'effective_date', 'weight', 'calculation_basis', 'created_at')
    list_filter = ('method_name', 'calculation_basis', 'effective_date')
    search_fields = ('method_name', 'notes')
    date_hierarchy = 'effective_date'
    ordering = ('-effective_date', 'method_name')


@admin.register(SoiCauBacNho)
class SoiCauBacNhoAdmin(admin.ModelAdmin):
    list_display = ('ngay_du_doan', 'phien_ban','ngay_phan_tich', 'phuong_phap', 'ket_qua_du_doan', 'thu_trong_tuan', 'ty_le_tin_cay')
    list_filter = ('ngay_phan_tich', 'phuong_phap', 'thu_trong_tuan')
    search_fields = ('ket_qua_du_doan', 'ghi_chu')  
    date_hierarchy = 'ngay_phan_tich'
    ordering = ('-ngay_phan_tich', 'phuong_phap')
    readonly_fields = ('ngay_phan_tich',)
    actions = ['delete_all_records']

    def delete_all_records(self, request, queryset):
        SoiCauBacNho.objects.all().delete()
        self.message_user(request, "Đã xóa toàn bộ dữ liệu trong bảng SoiCauBacNho.")
    delete_all_records.short_description = "Xóa toàn bộ dữ liệu"