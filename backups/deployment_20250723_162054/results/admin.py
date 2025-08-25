from django.contrib import admin
from django.db.models import Avg, Count, Sum
from .models import DanDeDacBiet, PredictionMethod, PredictionResult, DanBtl, PredictionMethodBtl, PredictionResultBtl, KetQuaXoSo

class PredictionResultInline(admin.TabularInline):
    model = PredictionResult
    readonly_fields = ('method', 'predicted_numbers', 'winning_numbers', 'hit_count', 'is_special_prize', 'digit_count')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

class PredictionResultBtlInline(admin.TabularInline):
    model = PredictionResultBtl
    readonly_fields = ('method', 'predicted_numbers', 'winning_numbers', 'hit_count', 'is_special_prize', 'digit_count')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(DanDeDacBiet)
class DanDeDacBietAdmin(admin.ModelAdmin):
    list_display = ('analysis_date', 'next_day_date', 'special_prize_next_day', 'get_hit_count', 'created_at')
    list_filter = ('analysis_date',)
    search_fields = ('analysis_date',)
    inlines = [PredictionResultInline]

    def get_hit_count(self, obj):
        return obj.predictions.aggregate(Sum('hit_count'))['hit_count__sum'] or 0
    get_hit_count.short_description = "Tổng số trúng"

@admin.register(DanBtl)
class DanBtlAdmin(admin.ModelAdmin):
    list_display = ('analysis_date', 'next_day_date', 'prize_next_day', 'get_hit_count', 'created_at')
    list_filter = ('analysis_date',)
    search_fields = ('analysis_date',)
    inlines = [PredictionResultBtlInline]

    def get_hit_count(self, obj):
        return obj.predictions_btl.aggregate(Sum('hit_count'))['hit_count__sum'] or 0
    get_hit_count.short_description = "Tổng số trúng"

@admin.register(PredictionMethod)
class PredictionMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'get_success_rate')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')

    def get_success_rate(self, obj):
        stats = obj.results.aggregate(
            hit_count=Sum('hit_count'),
            total=Count('id')
        )
        if stats['total'] > 0:
            rate = (stats['hit_count'] or 0) / stats['total']
            return f"{rate:.2%}"
        return "0%"
    get_success_rate.short_description = "Tỷ lệ trúng"

@admin.register(PredictionMethodBtl)
class PredictionMethodBtlAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'get_success_rate')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')

    def get_success_rate(self, obj):
        stats = obj.results_btl.aggregate(
            hit_count=Sum('hit_count'),
            total=Count('id')
        )
        if stats['total'] > 0:
            rate = (stats['hit_count'] or 0) / stats['total']
            return f"{rate:.2%}"
        return "0%"
    get_success_rate.short_description = "Tỷ lệ trúng"

@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ('dan_de', 'method', 'hit_count', 'is_special_prize', 'digit_count')
    list_filter = ('method', 'is_special_prize', 'digit_count')
    search_fields = ('dan_de__analysis_date',)

@admin.register(PredictionResultBtl)
class PredictionResultBtlAdmin(admin.ModelAdmin):
    list_display = ('dan_btl', 'method', 'hit_count', 'is_special_prize', 'digit_count')
    list_filter = ('method', 'is_special_prize', 'digit_count')
    search_fields = ['dan_btl__analysis_date']

@admin.register(KetQuaXoSo)
class KetQuaXoSoAdmin(admin.ModelAdmin):
    list_display = ['ngay', 'thu', 'giai_db', 'giai_1', 'giai_2_1', 'giai_2_2', 'giai_3_1', 'giai_3_2', 'giai_3_3', 'giai_3_4', 'giai_3_5', 'giai_3_6', 'giai_4_1', 'giai_4_2', 'giai_4_3', 'giai_4_4', 'giai_5_1', 'giai_5_2', 'giai_5_3', 'giai_5_4', 'giai_5_5', 'giai_5_6', 'giai_6_1', 'giai_6_2', 'giai_6_3', 'giai_7_1', 'giai_7_2', 'giai_7_3', 'giai_7_4']
    search_fields = ['ngay', 'giai_db', 'giai_1', 'giai_2_1', 'giai_2_2', 'giai_3_1', 'giai_3_2', 'giai_3_3', 'giai_3_4', 'giai_3_5', 'giai_3_6', 'giai_4_1', 'giai_4_2', 'giai_4_3', 'giai_4_4', 'giai_5_1', 'giai_5_2', 'giai_5_3', 'giai_5_4', 'giai_5_5', 'giai_5_6', 'giai_6_1', 'giai_6_2', 'giai_6_3', 'giai_7_1', 'giai_7_2', 'giai_7_3', 'giai_7_4']
    list_filter = ['thu']
    date_hierarchy = 'ngay'

from django.contrib import admin
from .models import StateAnalysis, PredictionModel, StatePrediction

@admin.register(StateAnalysis)
class StateAnalysisAdmin(admin.ModelAdmin):
    list_display = ['ngay', 'state', 'giai_7_2', 'giai_7_3', 'created_at']
    list_filter = ['state', 'ngay', 'created_at']
    search_fields = ['state', 'ngay']
    readonly_fields = ['created_at']
    date_hierarchy = 'ngay'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('source_record')

@admin.register(PredictionModel)
class PredictionModelAdmin(admin.ModelAdmin):
    list_display = ['model_type', 'accuracy', 'training_data_size', 'is_active', 'created_at']
    list_filter = ['model_type', 'is_active', 'created_at']
    search_fields = ['model_type']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['activate_models', 'deactivate_models']
    
    def activate_models(self, request, queryset):
        for model in queryset:
            # Deactivate other models of same type
            PredictionModel.objects.filter(
                model_type=model.model_type, 
                is_active=True
            ).update(is_active=False)
            model.is_active = True
            model.save()
        self.message_user(request, f'{queryset.count()} models activated')
    activate_models.short_description = 'Activate selected models'
    
    def deactivate_models(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} models deactivated')
    deactivate_models.short_description = 'Deactivate selected models'

@admin.register(StatePrediction)
class StatePredictionAdmin(admin.ModelAdmin):
    list_display = ['prediction_date', 'current_state', 'predicted_state', 
                   'actual_state', 'is_correct', 'confidence', 'model']
    list_filter = ['model__model_type', 'is_correct', 'prediction_date', 'created_at']
    search_fields = ['current_state', 'predicted_state', 'actual_state']
    readonly_fields = ['created_at']
    date_hierarchy = 'prediction_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('model')