import itertools
from decimal import Decimal, ROUND_HALF_UP

def calculate_profit(method_data, bet_amount=10000):
    """
    Tính toán lợi nhuận khi đánh lô, xiên 2, xiên 3, xiên 4 với mức cược cố định
    
    Args:
        method_data: Dữ liệu của phương pháp dự đoán
        bet_amount: Số tiền đặt cược cho mỗi số/xiên (mặc định: 10,000 VND)
        
    Returns:
        Dict chứa thông tin lợi nhuận cho các loại cược
    """
    predicted_numbers = method_data.get('predicted_numbers', [])
    hit_numbers = method_data.get('hit_numbers', [])
    
    if not predicted_numbers:
        return None
    
    # Tỷ lệ trả thưởng
    lo_rate = 3.5*2.7  # Lô trả 80 lần tiền cược
    xien2_rate = 17  # Xiên 2 trả 17 lần
    xien3_rate = 65  # Xiên 3 trả 65 lần
    xien4_rate = 250  # Xiên 4 trả 250 lần
    
    # Tính toán lô đơn
    lo_cost = len(predicted_numbers) * bet_amount *2.7
    lo_win = len(hit_numbers) * bet_amount * lo_rate
    lo_profit = lo_win - lo_cost
    
    # Tính xiên 2
    xien2_combinations = list(itertools.combinations(predicted_numbers, 2))
    xien2_cost = len(xien2_combinations) * bet_amount
    xien2_win_combinations = 0
    
    for combo in xien2_combinations:
        if all(num in hit_numbers for num in combo):
            xien2_win_combinations += 1
    
    xien2_win = xien2_win_combinations * bet_amount * xien2_rate
    xien2_profit = xien2_win - xien2_cost
    
    # Tính xiên 3
    xien3_combinations = list(itertools.combinations(predicted_numbers, 3))
    xien3_cost = len(xien3_combinations) * bet_amount
    xien3_win_combinations = 0
    
    for combo in xien3_combinations:
        if all(num in hit_numbers for num in combo):
            xien3_win_combinations += 1
    
    xien3_win = xien3_win_combinations * bet_amount * xien3_rate
    xien3_profit = xien3_win - xien3_cost
    
    # Tính xiên 4
    xien4_combinations = list(itertools.combinations(predicted_numbers, 4))
    xien4_cost = len(xien4_combinations) * bet_amount
    xien4_win_combinations = 0
    
    for combo in xien4_combinations:
        if all(num in hit_numbers for num in combo):
            xien4_win_combinations += 1
    
    xien4_win = xien4_win_combinations * bet_amount * xien4_rate
    xien4_profit = xien4_win - xien4_cost
    
    # Tính tổng lợi nhuận
    total_cost = lo_cost + xien2_cost + xien3_cost + xien4_cost
    total_win = lo_win + xien2_win + xien3_win + xien4_win
    total_profit = total_win - total_cost
    
    # Tính ROI (Return on Investment) - tỷ suất lợi nhuận trên vốn đầu tư
    roi = (total_profit / total_cost * 100) if total_cost > 0 else 0
    
    # Format số tiền hiển thị
    def format_money(amount):
        rounded = Decimal(amount).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
        formatted = '{:,}'.format(int(rounded))
        return formatted.replace(',', '.')
    
    return {
        'lo': {
            'numbers': len(predicted_numbers),
            'hit_numbers': len(hit_numbers),
            'cost': format_money(lo_cost),
            'win': format_money(lo_win),
            'profit': format_money(lo_profit),
            'roi': round(lo_profit / lo_cost * 100, 2) if lo_cost > 0 else 0,
            'profit_status': 'positive' if lo_profit > 0 else 'negative' if lo_profit < 0 else 'neutral'
        },
        'xien2': {
            'combinations': len(xien2_combinations),
            'hit_combinations': xien2_win_combinations,
            'cost': format_money(xien2_cost),
            'win': format_money(xien2_win),
            'profit': format_money(xien2_profit),
            'roi': round(xien2_profit / xien2_cost * 100, 2) if xien2_cost > 0 else 0,
            'profit_status': 'positive' if xien2_profit > 0 else 'negative' if xien2_profit < 0 else 'neutral'
        },
        'xien3': {
            'combinations': len(xien3_combinations),
            'hit_combinations': xien3_win_combinations,
            'cost': format_money(xien3_cost),
            'win': format_money(xien3_win),
            'profit': format_money(xien3_profit),
            'roi': round(xien3_profit / xien3_cost * 100, 2) if xien3_cost > 0 else 0,
            'profit_status': 'positive' if xien3_profit > 0 else 'negative' if xien3_profit < 0 else 'neutral'
        },
        'xien4': {
            'combinations': len(xien4_combinations),
            'hit_combinations': xien4_win_combinations,
            'cost': format_money(xien4_cost),
            'win': format_money(xien4_win),
            'profit': format_money(xien4_profit),
            'roi': round(xien4_profit / xien4_cost * 100, 2) if xien4_cost > 0 else 0,
            'profit_status': 'positive' if xien4_profit > 0 else 'negative' if xien4_profit < 0 else 'neutral'
        },
        'total': {
            'cost': format_money(total_cost),
            'win': format_money(total_win),
            'profit': format_money(total_profit),
            'roi': round(roi, 2),
            'profit_status': 'positive' if total_profit > 0 else 'negative' if total_profit < 0 else 'neutral'
        }
    }