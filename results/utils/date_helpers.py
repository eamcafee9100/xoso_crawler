from datetime import datetime, timedelta

def get_next_lottery_day(current_date):
    """Tính ngày xổ số tiếp theo (trừ thứ 2 và CN)"""
    if isinstance(current_date, str):
        current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
    
    next_day = current_date + timedelta(days=1)
    while next_day.weekday() in [0, 6]:  # Thứ 2 hoặc CN
        next_day += timedelta(days=1)
    return next_day