from datetime import datetime, timedelta,date
from django.shortcuts import render
from results.models import KetQuaXoSo

def soi_cau_hai_nhay(request):
    # Xử lý form
    region = request.GET.get('region', 'mb')  # Mặc định miền Bắc
    selected_date = request.GET.get('date')
    days = int(request.GET.get('days', '30'))  # Mặc định 30 ngày
    
    try:
        selected_date = datetime.strptime(selected_date, '%d-%m-%Y').date() if selected_date else date.today()
    except:
        selected_date = date.today()
    
    # Tính ngày bắt đầu
    start_date = selected_date - timedelta(days=days)
    
    # Lấy dữ liệu
    latest_results = KetQuaXoSo.objects.filter(
        ngay__gte=start_date,
        ngay__lte=selected_date
    ).order_by('-ngay')
    
    # Đếm số lần xuất hiện
    number_stats = {}
    for result in latest_results:
        numbers = result.get_all_2digit_numbers()
        for num in numbers:
            number_stats[num] = number_stats.get(num, 0) + 1
    
    # Phân loại số
    two_hit = [num for num, cnt in number_stats.items() if cnt == 2]
    three_hit = [num for num, cnt in number_stats.items() if cnt == 3]
    four_hit = [num for num, cnt in number_stats.items() if cnt >= 4]
    
    context = {
        'region': region,
        'selected_date': selected_date.strftime('%d-%m-%Y'),
        'days': days,
        'two_hit_numbers': sorted(two_hit),
        'three_hit_numbers': sorted(three_hit),
        'four_hit_numbers': sorted(four_hit),
        'analysis_period': f'{days} ngày',
        'total_days': latest_results.count(),
    }
    return render(request, 'results/soi_cau_hai_nhay.html', context)