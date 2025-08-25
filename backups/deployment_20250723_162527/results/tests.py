


from typing import Dict, List, Any, Optional, Union
def get_ball_number(number: Union[int, str]) -> int:
    """Chuyển số thành bóng theo quy tắc lô đề."""
    ball_map = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}
    num = int(number) if isinstance(number, str) else number
    return ball_map.get(num, num)
giai_1 = "22776"
giai_2_1 = "95300"
giai_3_1 = "98097"
giai_3_2 = "48961"
giai_3_6 = "69964"
giai_4_1 = "4813"
giai_5_6 = "9399"
giai_7_1 = "29"


# Tính số thứ nhất (chạm 1): tổng giải 3.2.1 + 3.6.3 + 7.1.1
sum_first = (int(giai_3_2[0]) + int(giai_3_6[2]) + int(giai_7_1[0])) % 10
touch_1 = sum_first
touch_1_ball = get_ball_number(touch_1)

# Tính số thứ hai (chạm 1): tổng giải 3.1.1 + 3.1.2 + 3.1.3
sum_second = (int(giai_3_1[0]) + int(giai_3_1[1]) + int(giai_3_1[2])) % 10
touch_2 = sum_second
touch_2_ball = get_ball_number(touch_2)

# Tính số thứ ba (tổng 1): tổng giải 1.1.2 + 2.1.4 + 5.6.3
sum_third = (int(giai_1[1]) + int(giai_2_1[3]) + int(giai_5_6[2])) % 10
total_1 = sum_third

# Tính số thứ tư (tổng 2): tổng giải 4.1.2 + 4.1.3 + 4.1.4
sum_fourth = (int(giai_4_1[1]) + int(giai_4_1[2]) + int(giai_4_1[3])) % 10
total_2 = sum_fourth

# Tạo các cặp số 2 chữ số
two_digits = set()

# Từ chạm 1 và tổng 1
second_digit_1 = (total_1 - touch_1) % 10
if 0 <= second_digit_1 <= 9:
    two_digits.add(f"{touch_1}{second_digit_1}")
    two_digits.add(f"{second_digit_1}{touch_1}")

# Từ bóng của chạm 1 và tổng 1
second_digit_1_ball = (total_1 - touch_1_ball) % 10
if 0 <= second_digit_1_ball <= 9:
    two_digits.add(f"{touch_1_ball}{second_digit_1_ball}")
    two_digits.add(f"{second_digit_1_ball}{touch_1_ball}")

# Từ chạm 2 và tổng 2
second_digit_2 = (total_2 - touch_2) % 10
if 0 <= second_digit_2 <= 9:
    two_digits.add(f"{touch_2}{second_digit_2}")
    two_digits.add(f"{second_digit_2}{touch_2}")

# Từ bóng của chạm 2 và tổng 2
second_digit_2_ball = (total_2 - touch_2_ball) % 10
if 0 <= second_digit_2_ball <= 9:
    two_digits.add(f"{touch_2_ball}{second_digit_2_ball}")
    two_digits.add(f"{second_digit_2_ball}{touch_2_ball}")

print(two_digits)

from datetime import date, timedelta

d = date(2025, 6, 30)
print(d + timedelta(days=1))  # Kết quả: 2025-07-01