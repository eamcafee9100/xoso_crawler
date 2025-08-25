from typing import Dict, Any, List
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.urls import reverse
import json
import logging

from .models import (
    PredictionCycle, DailyTrackingSession, MethodPredictionResult,
    TrackingEvaluation, CycleMethodParticipation, PredictionStrategy,
    PredictionMethod
)
from .core.services.TrackingService import tracking_service
from results.models import KetQuaXoSo

logger = logging.getLogger(__name__)


@login_required
def cycle_create(request):
    """
    Tạo chu kỳ mới
    """
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            cycle_name = request.POST.get('cycle_name')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            tracking_days = int(request.POST.get('tracking_days', 3))
            selected_methods = request.POST.getlist('methods')
            
            # Validate
            if not all([cycle_name, start_date, end_date]):
                messages.error(request, "Vui lòng điền đầy đủ thông tin bắt buộc")
                return render(request, 'predictions_tracker/cycles/create.html', {
                    'available_methods': PredictionMethod.objects.filter(is_active=True),
                    'page_title': 'Tạo chu kỳ mới'
                })
            
            # Tạo cycle
            cycle = PredictionCycle.objects.create(
                cycle_name=cycle_name,
                start_date=start_date,
                end_date=end_date,
                tracking_days=tracking_days,
                status='planning'
            )
            
            # Thêm methods vào cycle
            for method_id in selected_methods:
                method = PredictionMethod.objects.get(id=method_id)
                CycleMethodParticipation.objects.create(
                    cycle=cycle,
                    method=method,
                    is_ensemble_enabled=request.POST.get(f'ensemble_{method_id}') == 'on',
                    custom_weight=float(request.POST.get(f'weight_{method_id}', 1.0))
                )
            
            messages.success(request, f"Đã tạo chu kỳ '{cycle_name}' thành công!")
            return redirect('predictions_tracker:cycle_detail', cycle_id=cycle.id)
            
        except Exception as e:
            logger.error(f"Error creating cycle: {e}")
            messages.error(request, f"Lỗi tạo chu kỳ: {str(e)}")
    
    # GET request
    available_methods = PredictionMethod.objects.filter(is_active=True)
    
    context = {
        'available_methods': available_methods,
        'page_title': 'Tạo chu kỳ mới'
    }
    
    return render(request, 'predictions_tracker/cycles/create.html', context)

