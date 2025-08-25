from typing import Dict, List, Any, Optional, Union

def get_ball_number(number: Union[int, str]) -> int:
    """Chuyển số thành bóng theo quy tắc lô đề."""
    ball_map = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}
    num = int(number) if isinstance(number, str) else number
    return ball_map.get(num, num)

def process_prize(prize: str) -> str:
    """Xử lý giải: lấy 4 số cuối và chuyển số trùng thành bóng."""
    if not prize or len(prize) < 1:
        return ''
    last4 = prize[-4:] if len(prize) >= 4 else prize.zfill(4)[-4:]
    processed = [last4[0]]  # Giữ nguyên số đầu tiên
    for i in range(1, 4):
        current_char = last4[i]
        if current_char in last4[:i]:
            processed.append(str(get_ball_number(int(current_char))))
        else:
            processed.append(current_char)
    return ''.join(processed)

def parse_prizes(data: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Phân tích chuỗi giải thưởng thành các số riêng biệt
    
    Args:
        data: Dictionary chứa chuỗi các giải
        
    Returns:
        Dictionary chứa các số đã phân tích
    """
    result = {}
    for key, value in data.items():
        if not value:
            result[key] = []
            continue
            
        numbers = value.strip().split()
        result[key] = numbers
        
    return result