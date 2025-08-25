from datetime import datetime, timedelta, date
from django.views.generic import TemplateView, DetailView, ListView
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.views import View
from results.models import KetQuaXoSo

from .bac_nho_analyzer import BacNhoAnalyzer
from .bac_nho_analyzer_v1 import BacNhoAnalyzer_v1
import logging

from .models import SoiCauBacNho, ThongKeHieuQua, QuyLuatBacNho, MethodWeight

from django.db.models import Count, Q, F

from .models import  LichSuSoiCau, CauHinhPhanTich


import json
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)

class SoiCauBacNhoView(TemplateView):
    """
    View hiển thị kết quả soi cầu bạc nhớ
    """
    template_name = 'soicaubacnho/soi_cau_bac_nho.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy ngày từ tham số hoặc mặc định là ngày mai
        target_date_str = self.request.GET.get('target_date')
        try:
            if target_date_str:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            else:
                target_date = timezone.now().date() + timedelta(days=1)
        except ValueError:
            messages.error(self.request, "Định dạng ngày không hợp lệ. Sử dụng định dạng YYYY-MM-DD.")
            target_date = timezone.now().date() + timedelta(days=1)
        
        # Khởi tạo analyzer
        analyzer = BacNhoAnalyzer(target_date=target_date)
        
        # Kiểm tra xem có dự đoán đã lưu cho ngày này chưa
        saved_predictions = SoiCauBacNho.objects.filter(
            ngay_du_doan=target_date,
            phuong_phap='ket_hop'
        ).first()
        
        if saved_predictions:
            # Sử dụng dự đoán đã lưu
            predictions = {
                'target_date': target_date,
                'source_date': target_date - timedelta(days=1),
                'predicted_numbers': saved_predictions.get_ket_qua_du_doan(),
                'confidence': saved_predictions.ty_le_tin_cay,
                'created_at': saved_predictions.created_at
            }
            
            # Lấy thêm thông tin từ các phương pháp khác
            other_methods = SoiCauBacNho.objects.filter(
                ngay_du_doan=target_date
            ).exclude(phuong_phap='ket_hop')
            
            method_predictions = {}
            for method in other_methods:
                method_predictions[method.phuong_phap] = {
                    'name': dict(SoiCauBacNho.PREDICTION_METHODS).get(method.phuong_phap, method.phuong_phap),
                    'predicted_numbers': method.get_ket_qua_du_doan(),
                    'confidence': method.ty_le_tin_cay
                }
            
            # Thêm vào predictions
            predictions['method_predictions'] = method_predictions
            
            context['from_cache'] = True
        else:
            # Phân tích và dự đoán mới
            results = analyzer.analyze_and_predict()
            
            if 'error' in results:
                messages.error(self.request, results['error'])
                context['error'] = results['error']
                return context
            
            # Format kết quả để hiển thị
            predictions = {
                'target_date': results['target_date'],
                'source_date': results['source_date'],
                'predicted_numbers': results['predictions']['ket_hop']['predicted_numbers'],
                'confidence': results['predictions']['ket_hop']['confidence'],
                'created_at': timezone.now()
            }
            
            # Thêm thông tin từ các phương pháp khác
            method_predictions = {}
            for method, pred in results['predictions'].items():
                if method != 'ket_hop':
                    method_predictions[method] = {
                        'name': dict(SoiCauBacNho.PREDICTION_METHODS).get(method, method),
                        'predicted_numbers': pred['predicted_numbers'],
                        'confidence': pred['confidence']
                    }
            
            # Thêm vào predictions
            predictions['method_predictions'] = method_predictions
            
            context['from_cache'] = False
        
        # Lấy kết quả thực tế nếu đã có
        actual_result = KetQuaXoSo.objects.filter(ngay=target_date).first()
        if actual_result:
            actual_numbers = []
            if hasattr(actual_result, 'get_all_2digit_numbers'):
                actual_numbers = actual_result.get_all_2digit_numbers()
            
            context['actual_result'] = {
                'date': target_date,
                'numbers': actual_numbers,
                'matched': any(num in actual_numbers for num in predictions['predicted_numbers'])
            }
        
        # Lấy thống kê hiệu quả
        performance_stats = self._get_performance_statistics()
        
        # Lấy danh sách quy luật bạc nhớ
        top_rules = QuyLuatBacNho.objects.filter(
            co_hieu_luc=True
        ).order_by('-he_so_tin_cay')[:10]
        
        # Thêm vào context
        context.update({
            'predictions': predictions,
            'target_date': target_date,
            'today': timezone.now().date(),
            'performance_stats': performance_stats,
            'top_rules': top_rules
        })
        
        return context
    
    def _get_performance_statistics(self):
        """
        Lấy thống kê hiệu quả của các phương pháp
        
        Returns:
            Dict thống kê hiệu quả
        """
        # Lấy thống kê hiệu quả gần nhất
        latest_stats = ThongKeHieuQua.objects.order_by('-ngay_ket_thuc').first()
        if not latest_stats:
            return {}
        
        # Lấy thống kê cho từng phương pháp
        method_stats = ThongKeHieuQua.objects.filter(
            ngay_ket_thuc=latest_stats.ngay_ket_thuc
        ).order_by('-ty_le_trung')
        
        stats = {
            'date_range': f"{latest_stats.ngay_bat_dau.strftime('%d/%m/%Y')} - {latest_stats.ngay_ket_thuc.strftime('%d/%m/%Y')}",
            'methods': []
        }
        
        for method in method_stats:
            stats['methods'].append({
                'name': dict(SoiCauBacNho.PREDICTION_METHODS).get(method.phuong_phap, method.phuong_phap),
                'key': method.phuong_phap,
                'hit_rate': method.ty_le_trung,
                'hits': method.so_lan_trung,
                'total': method.tong_so_du_doan,
                'trend': method.xu_huong
            })
        
        # Tính tổng hợp
        if stats['methods']:
            stats['overall'] = {
                'hit_rate': sum(m['hit_rate'] for m in stats['methods']) / len(stats['methods']),
                'hits': sum(m['hits'] for m in stats['methods']),
                'total': sum(m['total'] for m in stats['methods'])
            }
        
        return stats

class SoiCauBacNhoHistoryView(ListView):
    """
    View hiển thị lịch sử dự đoán bạc nhớ
    """
    model = SoiCauBacNho
    template_name = 'soicaubacnho/soi_cau_bac_nho_history.html'
    context_object_name = 'predictions'
    paginate_by = 100
    
    def get_queryset(self):
        # Chỉ lấy dự đoán kết hợp
        queryset = SoiCauBacNho.objects.filter(
            phuong_phap='ket_hop'
        ).order_by('-ngay_du_doan')
        
        # Lọc theo ngày nếu có
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(ngay_du_doan__gte=start_date)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(ngay_du_doan__lte=end_date)
            except ValueError:
                pass
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Mặc định là khoảng thời gian 30 ngày gần nhất
        default_end_date = date.today()
        default_start_date = default_end_date - timedelta(days=30)
        
        # Thêm các tham số tìm kiếm vào context
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        

        context['historical_start_date'] = self.request.GET.get('historical_start_date', default_start_date.strftime('%Y-%m-%d'))
        context['historical_end_date'] = self.request.GET.get('historical_end_date', default_end_date.strftime('%Y-%m-%d'))
        
         # Thông tin thêm
        context['earliest_xoso_date'] = KetQuaXoSo.objects.order_by('ngay').values_list('ngay', flat=True).first()
        context['latest_xoso_date'] = KetQuaXoSo.objects.order_by('-ngay').values_list('ngay', flat=True).first()
        
        # Đếm số lượng dự đoán trong khoảng thời gian đã chọn
        if context['start_date'] and context['end_date']:
            try:
                start = datetime.strptime(context['start_date'], '%Y-%m-%d').date()
                end = datetime.strptime(context['end_date'], '%Y-%m-%d').date()
                
                context['date_range_days'] = (end - start).days + 1
                context['date_range_predictions'] = SoiCauBacNho.objects.filter(
                    phuong_phap='ket_hop',
                    ngay_du_doan__range=(start, end)
                ).count()
                
                # Các ngày có kết quả xổ số nhưng chưa có dự đoán
                xoso_dates = set(KetQuaXoSo.objects.filter(
                    ngay__range=(start, end)
                ).values_list('ngay', flat=True))
                
                prediction_dates = set(SoiCauBacNho.objects.filter(
                    phuong_phap='ket_hop',
                    ngay_du_doan__range=(start, end)
                ).values_list('ngay_du_doan', flat=True))
                
                context['missing_prediction_days'] = len(xoso_dates - prediction_dates)
                
            except ValueError:
                pass
        # Lấy danh sách ngày để truy vấn kết quả xổ số một lần
        prediction_dates = [pred.ngay_du_doan for pred in context['predictions']]
        
        
        xoso_results = {}
        for result in KetQuaXoSo.objects.filter(ngay__in=prediction_dates):
            xoso_results[result.ngay] = {
                'full_result': result,
                'all_numbers': result.get_all_2digit_numbers(),
                'giai_db': result.giai_db,
                'thu': result.thu,
                'details': {
                'giai_1': result.giai_1,
                'giai_2': [result.giai_2_1, result.giai_2_2],
                'giai_3': [result.giai_3_1, result.giai_3_2, result.giai_3_3, 
                          result.giai_3_4, result.giai_3_5, result.giai_3_6],
                'giai_4': [result.giai_4_1, result.giai_4_2, result.giai_4_3, result.giai_4_4],
                'giai_5': [result.giai_5_1, result.giai_5_2, result.giai_5_3, 
                          result.giai_5_4, result.giai_5_5, result.giai_5_6],
                'giai_6': [result.giai_6_1, result.giai_6_2, result.giai_6_3],
                'giai_7': [result.giai_7_1, result.giai_7_2, result.giai_7_3, result.giai_7_4]
            }
            }
        
        # Thêm thông tin bổ sung cho mỗi dự đoán
        for prediction in context['predictions']:
            # Chuyển string JSON thành danh sách
            prediction.numbers_list = prediction.get_ket_qua_du_doan()
            
            # Lấy kết quả thực tế từ SoiCauBacNho
            actual_numbers = prediction.get_ket_qua_thuc_te()
            
            # Lấy thông tin chi tiết từ KetQuaXoSo
            prediction.xoso_detail = xoso_results.get(prediction.ngay_du_doan, None)
            
            # Nếu không có kết quả thực tế trong SoiCauBacNho nhưng có trong KetQuaXoSo
            if not actual_numbers and prediction.xoso_detail:
                actual_numbers = prediction.xoso_detail['all_numbers']
                # Cập nhật ket_qua_thuc_te trong SoiCauBacNho nếu chưa có
                if not prediction.ket_qua_thuc_te and actual_numbers:
                    prediction.set_ket_qua_thuc_te(actual_numbers)
                    prediction.ket_qua_trung = any(num in actual_numbers for num in prediction.numbers_list)
                    prediction.save()
            
            # Tính số lượng trúng
            if actual_numbers:
                hits = [num for num in prediction.numbers_list if num in actual_numbers]
                prediction.hit_count = len(hits)
                prediction.hit_numbers = hits
                
                # Phân loại trúng theo giải (nếu có thông tin chi tiết)
                if prediction.xoso_detail:
                    prediction.hit_details = {}
                    # Tạo dict ánh xạ số đến giải
                    prize_mapping = {}
                    for prize, numbers in prediction.xoso_detail['details'].items():
                        for num in numbers:
                            if num:
                                num_2digit = num.zfill(2)[-2:]
                                prize_mapping[num_2digit] = prize
                    
                    # Đánh dấu giải của các số trúng
                    for hit_num in hits:
                        prediction.hit_details[hit_num] = prize_mapping.get(hit_num, 'unknown')
            else:
                prediction.hit_count = 0
                prediction.hit_numbers = []
        
        # Thêm thông tin thống kê
        total_predictions = len(context['predictions'])
        correct_predictions = sum(1 for p in context['predictions'] if p.ket_qua_trung)
        
        context['stats'] = {
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions,
            'hit_rate': (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
        }
        
        # Thêm tham số tìm kiếm
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        
        return context


class RunHistoricalPredictionsView(View):
    """
    View xử lý việc chạy lại dự đoán cho các ngày trong quá khứ
    """
    def post(self, request, *args, **kwargs):
        # Lấy thông tin từ form
        start_date = request.POST.get('historical_start_date')
        end_date = request.POST.get('historical_end_date')
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Kiểm tra khoảng thời gian hợp lệ
            if start_date > end_date:
                messages.error(request, "Ngày bắt đầu không thể sau ngày kết thúc")
                return redirect(reverse('soi_cau_bac_nho_history'))
            
            # Giới hạn khoảng thời gian để tránh quá tải hệ thống
            max_days = 365  # Giới hạn 1 năm
            if (end_date - start_date).days > max_days:
                messages.error(request, f"Khoảng thời gian tối đa là {max_days} ngày")
                return redirect(reverse('soi_cau_bac_nho_history'))
            
            # Lấy danh sách các ngày có kết quả xổ số
            xoso_dates = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).values_list('ngay', flat=True).order_by('ngay')
            
            if not xoso_dates:
                messages.error(request, "Không có kết quả xổ số nào trong khoảng thời gian đã chọn")
                return redirect(reverse('soi_cau_bac_nho_history'))
            
            # Chạy dự đoán cho từng ngày
            success_count = 0
            for date in xoso_dates:
                target_date = date + timedelta(days=1)
                
                # Kiểm tra xem ngày tiếp theo cũng có kết quả xổ số không
                next_day_has_result = KetQuaXoSo.objects.filter(ngay=target_date).exists()
                if not next_day_has_result:
                    continue
                
                # Khởi tạo analyzer và chạy dự đoán
                analyzer = BacNhoAnalyzer(target_date=target_date)
                try:
                    results = analyzer.analyze_and_predict()
                    success_count += 1
                except Exception as e:
                    # Log lỗi và tiếp tục với ngày tiếp theo
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Lỗi khi dự đoán cho ngày {target_date}: {e}")
                    continue
            
            # Cập nhật kết quả thực tế
            update_result = analyzer.update_prediction_results()
            
            if success_count > 0:
                messages.success(
                    request, 
                    f"Đã chạy dự đoán thành công cho {success_count} ngày và cập nhật kết quả thực tế"
                )
            else:
                messages.warning(request, "Không thể chạy dự đoán cho bất kỳ ngày nào")
                
            # Chuyển hướng về trang lịch sử với filter mới tạo
            return redirect(reverse('soi_cau_bac_nho_history') + f'?start_date={start_date}&end_date={end_date}')
            
        except ValueError as e:
            messages.error(request, f"Định dạng ngày không hợp lệ: {e}")
            return redirect(reverse('soi_cau_bac_nho_history'))
        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra: {e}")
            return redirect(reverse('soi_cau_bac_nho_history'))
        

class SoiCauBacNhoAPIView:
    """
    API View cho các thao tác liên quan đến Bạc Nhớ
    """
    
    @staticmethod
    def get_predictions(request):
        """
        API endpoint để lấy dự đoán cho một ngày cụ thể
        """
        try:
            # Lấy ngày từ tham số
            target_date_str = request.GET.get('target_date')
            try:
                if target_date_str:
                    target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                else:
                    target_date = timezone.now().date() + timedelta(days=1)
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Định dạng ngày không hợp lệ. Sử dụng định dạng YYYY-MM-DD.'
                }, status=400)
            
            # Khởi tạo analyzer
            analyzer = BacNhoAnalyzer(target_date=target_date)
            
            # Kiểm tra xem có dự đoán đã lưu cho ngày này chưa
            saved_predictions = SoiCauBacNho.objects.filter(
                ngay_du_doan=target_date,
                phuong_phap='ket_hop'
            ).first()
            
            if saved_predictions:
                # Sử dụng dự đoán đã lưu
                predictions = {
                    'target_date': target_date.strftime('%Y-%m-%d'),
                    'source_date': (target_date - timedelta(days=1)).strftime('%Y-%m-%d'),
                    'predicted_numbers': saved_predictions.get_ket_qua_du_doan(),
                    'confidence': saved_predictions.ty_le_tin_cay,
                    'created_at': saved_predictions.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'from_cache': True
                }
            else:
                # Phân tích và dự đoán mới
                results = analyzer.analyze_and_predict()
                
                if 'error' in results:
                    return JsonResponse({
                        'status': 'error',
                        'message': results['error']
                    }, status=400)
                
                # Format kết quả
                predictions = {
                    'target_date': results['target_date'].strftime('%Y-%m-%d'),
                    'source_date': results['source_date'].strftime('%Y-%m-%d'),
                    'predicted_numbers': results['predictions']['ket_hop']['predicted_numbers'],
                    'confidence': results['predictions']['ket_hop']['confidence'],
                    'created_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'from_cache': False
                }
            
            # Lấy kết quả thực tế nếu đã có
            actual_result = KetQuaXoSo.objects.filter(ngay=target_date).first()
            if actual_result:
                actual_numbers = []
                if hasattr(actual_result, 'get_all_2digit_numbers'):
                    actual_numbers = actual_result.get_all_2digit_numbers()
                
                predictions['actual_result'] = {
                    'date': target_date.strftime('%Y-%m-%d'),
                    'numbers': actual_numbers,
                    'matched': any(num in actual_numbers for num in predictions['predicted_numbers'])
                }
            
            return JsonResponse({
                'status': 'success',
                'data': predictions
            })
        except Exception as e:
            logger.error(f"Lỗi khi lấy dự đoán: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Lỗi: {str(e)}'
            }, status=500)
    
    @staticmethod
    def update_results(request):
        """
        API endpoint để cập nhật kết quả thực tế cho các dự đoán
        """
        try:
            # Khởi tạo analyzer
            analyzer = BacNhoAnalyzer()
            
            # Cập nhật kết quả
            result = analyzer.update_prediction_results()
            
            return JsonResponse({
                'status': 'success',
                'data': result
            })
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật kết quả: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Lỗi: {str(e)}'
            }, status=500)
    
    @staticmethod
    def discover_patterns(request):
        """
        API endpoint để phát hiện quy luật mới
        """
        try:
            # Khởi tạo analyzer
            analyzer = BacNhoAnalyzer()
            
            # Phát hiện quy luật mới
            result = analyzer.discover_new_patterns()
            
            return JsonResponse({
                'status': 'success',
                'data': result
            })
        except Exception as e:
            logger.error(f"Lỗi khi phát hiện quy luật mới: {e}")
            return JsonResponse({
                'status': 'error',
                'message': f'Lỗi: {str(e)}'
            }, status=500)
        
# Thêm vào views.py

class OptimizeWeightsView(TemplateView):
    """
    View hiển thị và thực hiện tối ưu hóa trọng số
    """
    template_name = 'soicaubacnho/optimize_weights.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Khởi tạo analyzer
        analyzer = BacNhoAnalyzer()
        
        # Lấy trọng số hiện tại
        current_weights = analyzer._get_historical_method_weights()
        
        # Lấy thông tin về chu kỳ mệt mỏi
        method_cycles = analyzer.analyze_method_fatigue_cycles()
        
        # Lấy thống kê hiệu quả
        performance_stats = ThongKeHieuQua.objects.order_by('-ngay_ket_thuc').first()
        if performance_stats:
            performance_date_range = f"{performance_stats.ngay_bat_dau.strftime('%d/%m/%Y')} - {performance_stats.ngay_ket_thuc.strftime('%d/%m/%Y')}"
        else:
            performance_date_range = "Không có dữ liệu"
        
        # Thử tối ưu hóa trọng số
        optimized_weights = None
        optimization_error = None
        try:
            optimized_weights = analyzer.optimize_method_weights()
        except Exception as e:
            optimization_error = str(e)
            logger.error(f"Lỗi khi tối ưu hóa trọng số: {e}")
        
        context.update({
            'current_weights': current_weights,
            'method_cycles': method_cycles,
            'performance_date_range': performance_date_range,
            'optimized_weights': optimized_weights,
            'optimization_error': optimization_error
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Xử lý yêu cầu tối ưu hóa và lưu trọng số mới"""
        # Khởi tạo analyzer
        analyzer = BacNhoAnalyzer()
        
        action = request.POST.get('action')
        
        if action == 'optimize':
            try:
                # Tối ưu hóa trọng số
                optimized_weights = analyzer.optimize_method_weights()
                
                # Lưu trọng số mới vào DB
                effective_date = timezone.now().date() + timedelta(days=1)
                
                for method, weight in optimized_weights.items():
                    MethodWeight.objects.create(
                        effective_date=effective_date,
                        method_name=method,
                        method_version="1.0",
                        weight=weight,
                        calculation_basis='optimized',
                        days_analyzed=30
                    )
                
                messages.success(request, f"Đã tối ưu hóa và lưu trọng số mới, có hiệu lực từ ngày {effective_date.strftime('%d/%m/%Y')}")
            except Exception as e:
                messages.error(request, f"Lỗi khi tối ưu hóa trọng số: {str(e)}")
        
        elif action == 'manual_save':
            try:
                # Lấy trọng số từ form
                manual_weights = {}
                for method, _ in SoiCauBacNho.PREDICTION_METHODS:
                    if method != 'ket_hop':
                        weight_str = request.POST.get(f'weight_{method}', '0.5')
                        try:
                            weight = float(weight_str)
                            manual_weights[method] = weight
                        except ValueError:
                            manual_weights[method] = 0.5
                
                # Lưu trọng số mới vào DB
                effective_date = timezone.now().date() + timedelta(days=1)
                
                for method, weight in manual_weights.items():
                    MethodWeight.objects.create(
                        effective_date=effective_date,
                        method_name=method,
                        method_version="1.0",
                        weight=weight,
                        calculation_basis='manual',
                        days_analyzed=0
                    )
                
                messages.success(request, f"Đã lưu trọng số thủ công, có hiệu lực từ ngày {effective_date.strftime('%d/%m/%Y')}")
            except Exception as e:
                messages.error(request, f"Lỗi khi lưu trọng số thủ công: {str(e)}")
        
        # Quay lại view hiện tại
        return redirect('optimize_weights')
    

def dashboard(request):
    """Trang tổng quan"""
    # Lấy phiên bản mặc định từ cấu hình
    default_version = CauHinhPhanTich.objects.filter(trang_thai=True).first()
    if default_version:
        selected_version = default_version.phien_ban_mac_dinh
    else:
        selected_version = 'v1'  # Mặc định là v1 nếu không có cấu hình
    
    # Lấy phiên bản từ query parameter hoặc session
    version = request.GET.get('version')
    if version:
        request.session['selected_version'] = version
    else:
        version = request.session.get('selected_version', get_default_version())
    
    # Lấy dữ liệu cho dashboard
    today = timezone.now().date()
    
    # Dự đoán mới nhất
    latest_predictions = SoiCauBacNho.objects.filter(
        phien_ban=version,
        phuong_phap='ket_hop'
    ).order_by('-ngay_du_doan')[:10]
    
    # Thống kê hiệu quả gần đây
    recent_stats = get_recent_performance_stats(version)
    
    context = {
        'latest_predictions': latest_predictions,
        'recent_stats': recent_stats,
        'selected_version': version,
        'available_versions': SoiCauBacNho.VERSION_CHOICES,
    }
    
    return render(request, 'soicaubacnho/dashboard.html', context)


def predict_view(request):
    """Trang dự đoán mới"""
    # Lấy thông tin phiên bản từ request hoặc mặc định
    version = request.GET.get('version', 'v1')
    valid_versions = [code for code, _ in SoiCauBacNho.VERSION_CHOICES]
    if version not in valid_versions:
        version = 'v1'  # Fallback về phiên bản mặc định
    
    # Lấy ngày từ request hoặc mặc định là ngày mai
    target_date_str = request.GET.get('date')
    if target_date_str:
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = timezone.now().date() + timedelta(days=1)
    else:
        target_date = timezone.now().date() + timedelta(days=1)
    
    # Nếu đã submit form
    if request.method == 'POST':
        version = request.POST.get('version', 'v1')
        # Kiểm tra phiên bản hợp lệ
        if version not in valid_versions:
            version = 'v1'  # Fallback về phiên bản mặc định
        print(f"Selected version: {version}")
        # Khởi tạo phân tích theo phiên bản
        AnalyzerClass = get_analyzer_class(version)
        analyzer = AnalyzerClass(target_date=target_date)
        # Thực hiện phân tích và dự đoán
        results = analyzer.analyze_and_predict()
        
        # Chuyển hướng đến trang kết quả
        combined_id = None
        if 'predictions' in results and 'ket_hop' in results.get('predictions', {}):
            ket_hop = results['predictions']['ket_hop']
            if isinstance(ket_hop, dict) and 'id' in ket_hop:
                combined_id = ket_hop['id']
        
        if combined_id:
            return redirect('prediction_results', pk=combined_id)
        else:
            # Xử lý trường hợp không tìm thấy combined_id
            return redirect('dashboard')
        
    # Lấy danh sách các phương pháp dự đoán
    methods = SoiCauBacNho.PREDICTION_METHODS
    
    context = {
        'target_date': target_date,
        'version': version,
        'available_versions': SoiCauBacNho.VERSION_CHOICES,
        'methods': methods,
    }
    
    return render(request, 'soicaubacnho/predict_form.html', context)


    
def prediction_results(request, pk):
    """Hiển thị kết quả dự đoán"""
    # Lấy dự đoán kết hợp
    combined_prediction = get_object_or_404(SoiCauBacNho, pk=pk, phuong_phap='ket_hop')
    target_date = combined_prediction.ngay_du_doan
    actual_result = None
    actual_result = KetQuaXoSo.objects.filter(ngay=target_date).first().get_all_2digit_numbers() if actual_result else []
    # Lấy tất cả các dự đoán cho cùng ngày và phiên bản
    all_predictions = SoiCauBacNho.objects.filter(
        ngay_du_doan=target_date,
        phien_ban=combined_prediction.phien_ban
    ).exclude(phuong_phap='ket_hop')
    
    # Phân loại dự đoán theo phương pháp
    predictions_by_method = {pred.phuong_phap: pred for pred in all_predictions}
    
    # Lấy thông tin trọng số từ dự đoán kết hợp
    try:
        ghi_chu = json.loads(combined_prediction.ghi_chu)
        method_weights = ghi_chu.get('method_weights', {})
    except:
        method_weights = {}
    
    context = {
        'combined_prediction': combined_prediction,
        'predictions_by_method': predictions_by_method,
        'method_weights': method_weights,
        'version': combined_prediction.phien_ban,
        'actual_numbers': combined_prediction.get_ket_qua_thuc_te(),
    }
    
    return render(request, 'soicaubacnho/prediction_results.html', context)


def compare_versions(request):
    """So sánh kết quả giữa các phiên bản"""
    # Lấy ngày từ request hoặc mặc định là hôm nay
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = timezone.now().date()
    else:
        target_date = timezone.now().date()
    
    # Lấy dự đoán kết hợp từ tất cả các phiên bản cho ngày đã chọn
    combined_predictions = {}
    for version_code, version_name in SoiCauBacNho.VERSION_CHOICES:
        prediction = SoiCauBacNho.objects.filter(
            ngay_du_doan=target_date,
            phien_ban=version_code,
            phuong_phap='ket_hop'
        ).first()
        
        if prediction:
            combined_predictions[version_code] = {
                'prediction': prediction,
                'numbers': prediction.get_ket_qua_du_doan(),
                'confidence': prediction.ty_le_tin_cay,
            }
    
    # Lấy kết quả thực tế nếu có
    actual_result = KetQuaXoSo.objects.filter(ngay=target_date).first()
    actual_numbers = []
    if actual_result:
        try:
            # Giả sử có phương thức để lấy các số 2 chữ số
            if hasattr(actual_result, 'get_all_2digit_numbers'):
                actual_numbers = actual_result.get_all_2digit_numbers()
            else:
                # Nếu không có phương thức đó, cần triển khai logic ở đây
                pass
        except:
            pass
    
    # Đánh giá kết quả nếu có kết quả thực tế
    if actual_numbers:
        for version in combined_predictions:
            pred_numbers = combined_predictions[version]['numbers']
            hits = [num for num in pred_numbers if num in actual_numbers]
            combined_predictions[version]['hits'] = hits
            combined_predictions[version]['hit_count'] = len(hits)
            combined_predictions[version]['accuracy'] = (len(hits) / len(pred_numbers)) * 100 if pred_numbers else 0
    
    context = {
        'target_date': target_date,
        'combined_predictions': combined_predictions,
        'actual_result': actual_result,
        'actual_numbers': actual_numbers,
    }
    
    return render(request, 'soicaubacnho/compare_versions.html', context)


@require_POST
def run_analyzer(request):
    """API endpoint để chạy phân tích"""
    try:
        data = json.loads(request.body)
        version = data.get('version', 'v1')
        # Kiểm tra phiên bản hợp lệ
        valid_versions = [code for code, _ in SoiCauBacNho.VERSION_CHOICES]
        if version not in valid_versions:
            return JsonResponse({
                'success': False,
                'message': f'Phiên bản {version} không hợp lệ'
            })
        print(f"Running analyzer for version: {version}")
        target_date_str = data.get('target_date')
        
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            target_date = timezone.now().date() + timedelta(days=1)
        
        # Lấy class analyzer phù hợp
        AnalyzerClass = get_analyzer_class(version)
        analyzer = AnalyzerClass(target_date=target_date)
        
        # Thực hiện phân tích và dự đoán
        results = analyzer.analyze_and_predict()
        
        # Trả về ID của dự đoán kết hợp
        combined_id = None
        if 'predictions' in results and 'ket_hop' in results['predictions']:
            combined_pred = SoiCauBacNho.objects.filter(
                ngay_du_doan=target_date,
                phien_ban=version,
                phuong_phap='ket_hop'
            ).first()
            if combined_pred:
                combined_id = combined_pred.id
        
        return JsonResponse({
            'success': True,
            'combined_id': combined_id,
            'target_date': target_date_str,
            'version': version,
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}',
            'details': error_details
        })

@require_POST
def get_results(request):
    """API endpoint để lấy kết quả xổ số và cập nhật dự đoán"""
    try:
        data = json.loads(request.body)
        target_date_str = data.get('target_date')
        version = data.get('version', 'v1')
        
        # Log dữ liệu nhận được
        logger.info(f"Nhận request lấy kết quả cho ngày {target_date_str}, phiên bản {version}")
        
        # Kiểm tra phiên bản hợp lệ
        valid_versions = [code for code, _ in SoiCauBacNho.VERSION_CHOICES]
        if version not in valid_versions:
            return JsonResponse({
                'success': False,
                'message': f'Phiên bản {version} không hợp lệ'
            })
        
        # Chuyển đổi ngày
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            logger.error(f"Định dạng ngày không hợp lệ: {target_date_str}")
            return JsonResponse({
                'success': False,
                'message': f'Định dạng ngày không hợp lệ: {target_date_str}'
            })
        
        # Kiểm tra xem đã có kết quả xổ số cho ngày này chưa
        # Lấy kết quả thực tế nếu có
        actual_result = KetQuaXoSo.objects.filter(ngay=target_date).first()
        print(f"Lấy kết quả thực tế cho ngày {target_date_str}: {actual_result}")
        actual_numbers = []
        if actual_result:
            try:
                # Giả sử có phương thức để lấy các số 2 chữ số
                if hasattr(actual_result, 'get_all_2digit_numbers'):
                    actual_numbers = actual_result.get_all_2digit_numbers()
                else:
                    # Nếu không có phương thức đó, cần triển khai logic ở đây
                    pass
            except:
                pass
        
        print(f"Kết quả thực tế cho ngày {target_date_str}: {actual_numbers}")
        # Cập nhật kết quả cho các dự đoán
        updated_predictions = []
        predictions = SoiCauBacNho.objects.filter(
            ngay_du_doan=target_date,
            phien_ban=version,
            ket_qua_thuc_te__isnull=True  # Chỉ cập nhật những dự đoán chưa có kết quả
        )
        
        for pred in predictions:
            pred_numbers = pred.get_ket_qua_du_doan()
            # Kiểm tra xem có trúng không (có ít nhất 1 số trong dự đoán nằm trong kết quả thực tế)
            is_hit = any(num in actual_numbers for num in pred_numbers)

            # Cập nhật dự đoán
            pred.ket_qua_thuc_te = json.dumps(actual_numbers)
            pred.ket_qua_trung = is_hit
            pred.save()
            
            updated_predictions.append(pred.id)
        
        # Tìm dự đoán kết hợp để trả về ID
        combined_pred = SoiCauBacNho.objects.filter(
            ngay_du_doan=target_date,
            phien_ban=version,
            phuong_phap='ket_hop'
        ).first()
        
        combined_id = combined_pred.id if combined_pred else None
        
        return JsonResponse({
            'success': True,
            'actual_numbers': actual_numbers,
            'updated_predictions': len(updated_predictions),
            'combined_id': combined_id,
            'target_date': target_date_str,
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Lỗi khi lấy kết quả: {e}\n{error_details}")
        
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}',
            'details': error_details
        })
    
def version_config(request):
    """Quản lý cấu hình phiên bản"""
    if request.method == 'POST':
        config_id = request.POST.get('config_id')
        
        if config_id:  # Cập nhật cấu hình hiện có
            config = get_object_or_404(CauHinhPhanTich, id=config_id)
        else:  # Tạo cấu hình mới
            config = CauHinhPhanTich()
            config.nguoi_tao = request.user
        
        # Cập nhật thông tin cấu hình
        config.ten_cau_hinh = request.POST.get('ten_cau_hinh')
        config.phien_ban_mac_dinh = request.POST.get('phien_ban_mac_dinh')
        config.mo_ta = request.POST.get('mo_ta', '')
        config.trang_thai = request.POST.get('trang_thai') == 'on'
        
        # Xử lý các phương pháp và trọng số
        phuong_phap = request.POST.getlist('phuong_phap')
        trong_so = {}
        for method in phuong_phap:
            weight_key = f'trong_so_{method}'
            try:
                trong_so[method] = float(request.POST.get(weight_key, 1.0))
            except ValueError:
                trong_so[method] = 1.0
        
        config.phuong_phap_mac_dinh = phuong_phap
        config.trong_so_mac_dinh = trong_so
        
        # Xử lý các tham số khác
        tham_so_khac = {}
        for key, value in request.POST.items():
            if key.startswith('tham_so_'):
                param_name = key.replace('tham_so_', '')
                tham_so_khac[param_name] = value
        
        config.tham_so_khac = tham_so_khac
        config.save()
        
        return redirect('version_config')
    
    # Lấy tất cả cấu hình
    configs = CauHinhPhanTich.objects.all().order_by('-thoi_gian_cap_nhat')
    
    context = {
        'configs': configs,
        'available_versions': SoiCauBacNho.VERSION_CHOICES,
        'prediction_methods': SoiCauBacNho.PREDICTION_METHODS,
    }
    
    return render(request, 'soicaubacnho/version_config.html', context)

def get_recent_performance_stats(version='v1'):
    """Lấy thống kê hiệu quả gần đây"""
    today = timezone.now().date()
    start_date = today - timedelta(days=30)
    
    # Lấy tất cả dự đoán đã có kết quả
    predictions = SoiCauBacNho.objects.filter(
        phien_ban=version,
        ngay_du_doan__range=(start_date, today),
        ket_qua_thuc_te__isnull=False
    )
    
    # Thống kê theo phương pháp
    method_stats = {}
    for method, method_name in SoiCauBacNho.PREDICTION_METHODS:
        method_preds = predictions.filter(phuong_phap=method)
        total = method_preds.count()
        correct = method_preds.filter(ket_qua_trung=True).count()
        
        if total > 0:
            hit_rate = (correct / total) * 100
        else:
            hit_rate = 0
        
        method_stats[method] = {
            'name': method_name,
            'total': total,
            'correct': correct,
            'hit_rate': hit_rate,
        }
    
    return method_stats

# Thêm vào views.py


@require_POST
def update_prediction_results(request):
    """API endpoint để cập nhật kết quả dự đoán"""
    data = json.loads(request.body)
    version = data.get('version', 'v1')
    
    # Khởi tạo phân tích theo phiên bản
    if version == 'v1':
        analyzer = BacNhoAnalyzer_v1()
    else:
        analyzer = BacNhoAnalyzer()
    
    # Cập nhật kết quả
    result = analyzer.update_prediction_results()
    
    return JsonResponse(result)

# Ví dụ trong views.py

def get_analyzer_class(version):
    """Helper để lấy class analyzer dựa vào phiên bản"""
    if version == 'v0':
        print("Using BacNhoAnalyzer (original version)")
        return BacNhoAnalyzer  # Phiên bản gốc
    elif version == 'v1':
        print("Using BacNhoAnalyzer_v1")
        return BacNhoAnalyzer_v1
    # elif version == 'v2':
    #     return BacNhoAnalyzer_v2
    # Thêm các phiên bản mới ở đây
    else:
        return BacNhoAnalyzer  # Fallback về phiên bản gốc
def get_default_version():
    """
    Lấy phiên bản mặc định dựa trên cấu hình
    Returns:
        Phiên bản mặc định (v0, v1, v2...)
    """
    from .models import CauHinhPhanTich
    
    # Lấy từ cấu hình nếu có
    config = CauHinhPhanTich.objects.filter(trang_thai=True).first()
    if config:
        return config.phien_ban_mac_dinh
    
    # Mặc định trả về v1 nếu không có cấu hình
    return 'v1'

def get_config(request, pk):
    """API endpoint để lấy thông tin cấu hình"""
    try:
        config = get_object_or_404(CauHinhPhanTich, id=pk)
        
        return JsonResponse({
            'success': True,
            'config': {
                'id': config.id,
                'ten_cau_hinh': config.ten_cau_hinh,
                'phien_ban_mac_dinh': config.phien_ban_mac_dinh,
                'phuong_phap_mac_dinh': config.phuong_phap_mac_dinh,
                'trong_so_mac_dinh': config.trong_so_mac_dinh,
                'tham_so_khac': config.tham_so_khac,
                'mo_ta': config.mo_ta,
                'trang_thai': config.trang_thai
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })