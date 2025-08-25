from django.contrib import admin

# Register your models here.
from .models import ChamAnalysis

@admin.register(ChamAnalysis)
class ChamAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'ngay', 'db_full', 'db_last2', 'db_cham_dau', 'db_cham_duoi',
        'db_total', 'db_last2_total', 'giai_nhat_full', 'giai_nhat_mid_digit',
        'day_of_week', 'is_sunday', 'is_monday', 'is_tuesday', 'is_wednesday',
        'is_thursday', 'is_friday', 'is_saturday', 'week_number', 'month',
        'cau_cham1_value', 'cau_cham2_value'
    ]
    list_filter = ['is_sunday', 'is_monday', 'is_tuesday', 'is_wednesday', 'is_thursday', 'is_friday', 'is_saturday', 'month']
    search_fields = ['ngay', 'db_full', 'db_last2', 'giai_nhat_full']
    date_hierarchy = 'ngay'