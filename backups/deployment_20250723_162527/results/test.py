from crawlers import crawl_xsmb_ketquame    
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta

def crawl_xsmb_view(request):
    results = []
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        try:
            # Chuyển đổi từ YYYY-MM-DD (HTML date input) sang DD-MM-YYYY (dùng cho crawler)
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            start_date_str = start_date_obj.strftime('%d-%m-%Y')
            end_date_str = end_date_obj.strftime('%d-%m-%Y')
            
            if start_date_obj > end_date_obj:
                messages.error(request, "Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc")
            elif (end_date_obj - start_date_obj).days > 90:  # Giới hạn 3 tháng
                messages.warning(request, "Chỉ có thể tải tối đa 90 ngày một lần")
            else:
                results = crawl_xsmb_ketquame(start_date_str, end_date_str)
                
                # Thống kê kết quả
                success_count = sum(1 for r in results if r['success'])
                messages.success(request, f"Đã tải thành công {success_count}/{len(results)} ngày")
                
        except ValueError:
            messages.error(request, "Định dạng ngày không hợp lệ")
    print(f"Results: {results}")
    return render(request, 'results/crawl_form.html', {
        'results': results,
        'default_start': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'default_end': datetime.now().strftime('%Y-%m-%d')
    })