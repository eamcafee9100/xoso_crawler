from itertools import combinations

class LotteryBet:
    def __init__(self, xien_cost):
        """
        Khởi tạo với giá tiền đánh xiên do người dùng nhập.
        xien_cost: Giá tiền đánh cho xiên 2, xiên 3, xiên 4 (bằng nhau).
        """
        self.bet_rules = {
            'lo': {'cost': 27000, 'win': 99400},  # Lô thường
            'xien2': {'cost': xien_cost, 'win': xien_cost * 17},  # Xiên 2
            'xien3': {'cost': xien_cost, 'win': xien_cost * 65},  # Xiên 3
            'xien4': {'cost': xien_cost, 'win': xien_cost * 250}  # Xiên 4
        }

    def calculate_bet_cost(self, bet_type, quantity):
        """
        Tính tổng tiền cược dựa trên loại cược và số lượng.
        bet_type: 'lo', 'xien2', 'xien3', 'xien4'
        quantity: Số lượng cược (số, cặp,...)
        """
        if bet_type not in self.bet_rules:
            return "Loại cược không hợp lệ!"
        return self.bet_rules[bet_type]['cost'] * quantity

    def calculate_win_amount(self, bet_type, winning_quantity):
        """
        Tính tiền trúng dựa trên loại cược và số lượng trúng.
        bet_type: 'lo', 'xien2', 'xien3', 'xien4'
        winning_quantity: Số lượng cược trúng
        """
        if bet_type not in self.bet_rules:
            return "Loại cược không hợp lệ!"
        return self.bet_rules[bet_type]['win'] * winning_quantity

    def calculate_xien_quay(self, total_numbers, winning_numbers):
        """
        Tính tiền trúng cho xiên quay dựa trên tổng số đánh và số trúng.
        Trả về tổng tiền trúng và chi tiết định dạng.
        """
        
        win_amount = 0
        matched_count = winning_numbers
        details = [f"Tiền trúng xiên quay ({winning_numbers} số trúng):"]
        
        if matched_count > total_numbers:
            return 0, ["Số trúng không thể lớn hơn tổng số đánh!"]
        
        if matched_count < 2:
            return 0, ["Không trúng xiên quay vì ít hơn 2 số trúng!"]
        
        # Tính xiên 2
        xien2_combinations = len(list(combinations(range(matched_count), 2)))
        xien2_win = self.calculate_win_amount('xien2', xien2_combinations)
        if xien2_combinations > 0:
            details.append(f"    Xiên 2: C({matched_count},2) = {xien2_combinations} cặp × {self.bet_rules['xien2']['cost']:,} × 17 = {xien2_win:,} VND.")
            win_amount += xien2_win
        
        # Tính xiên 3
        xien3_combinations = len(list(combinations(range(matched_count), 3)))
        xien3_win = self.calculate_win_amount('xien3', xien3_combinations)
        if xien3_combinations > 0:
            details.append(f"    Xiên 3: C({matched_count},3) = {xien3_combinations} cặp × {self.bet_rules['xien3']['cost']:,} × 65 = {xien3_win:,} VND.")
            win_amount += xien3_win
        
        # Tính xiên 4
        xien4_combinations = len(list(combinations(range(matched_count), 4)))
        xien4_win = self.calculate_win_amount('xien4', xien4_combinations)
        if xien4_combinations > 0:
            details.append(f"    Xiên 4: C({matched_count},4) = {xien4_combinations} cặp × {self.bet_rules['xien4']['cost']:,} × 250 = {xien4_win:,} VND.")
            win_amount += xien4_win
        
        # Tính tổng
        if win_amount > 0:
            total_str = " + ".join([f"{x:,}" for x in [xien2_win, xien3_win, xien4_win] if x > 0])
            details.append(f"    Tổng xiên quay: {total_str} = {win_amount:,} VND.")
        else:
            details.append(f"    Tổng xiên quay: 0 VND.")
        
        return win_amount, details

    def user_input(self):
        """
        Hàm nhập liệu từ người dùng và hiển thị kết quả với định dạng chi tiết.
        """
        try:
            # Nhập tổng số đánh và số trúng
            total_numbers = int(input("Nhập tổng số lượng số đã đánh: "))
            winning_numbers = int(input("Nhập số lượng số trúng: "))
            
            # Tính tiền cược lô thường
            lo_cost = self.calculate_bet_cost('lo', total_numbers)
            print(f"Tiền cược lô thường: {total_numbers} số × 27,000 = {lo_cost:,} VND.")
            
            # Tính tiền cược xiên
            xien2_count = len(list(combinations(range(total_numbers), 2)))
            xien3_count = len(list(combinations(range(total_numbers), 3)))
            xien4_count = len(list(combinations(range(total_numbers), 4)))
            xien2_cost = self.calculate_bet_cost('xien2', xien2_count)
            xien3_cost = self.calculate_bet_cost('xien3', xien3_count)
            xien4_cost = self.calculate_bet_cost('xien4', xien4_count)
            print("Tiền cược xiên:")
            print(f"    Xiên 2: C({total_numbers},2) = {xien2_count} cặp × {self.bet_rules['xien2']['cost']:,} = {xien2_cost:,} VND.")
            print(f"    Xiên 3: C({total_numbers},3) = {xien3_count} cặp × {self.bet_rules['xien3']['cost']:,} = {xien3_cost:,} VND.")
            print(f"    Xiên 4: C({total_numbers},4) = {xien4_count} cặp × {self.bet_rules['xien4']['cost']:,} = {xien4_cost:,} VND.")
            
            # Tính tổng tiền cược
            total_bet_cost = lo_cost + xien2_cost + xien3_cost + xien4_cost
            print(f"Tổng tiền cược: {lo_cost:,} + {xien2_cost:,} + {xien3_cost:,} + {xien4_cost:,} = {total_bet_cost:,} VND.")
            
            # Tính tiền trúng lô thường
            lo_win = self.calculate_win_amount('lo', winning_numbers)
            print(f"Tiền trúng lô thường: {winning_numbers} số × 99,400 = {lo_win:,} VND.")
            
            # Tính tiền trúng xiên quay
            xien_quay_win, xien_quay_details = self.calculate_xien_quay(total_numbers, winning_numbers)
            for detail in xien_quay_details:
                print(detail)
            
        except ValueError:
            print("Vui lòng nhập số nguyên hợp lệ!")

# Ví dụ sử dụng
if __name__ == "__main__":
    try:
        xien_cost = int(input("Nhập giá tiền đánh xiên (xiên 2, xiên 3, xiên 4): "))
        lottery = LotteryBet(xien_cost)
        lottery.user_input()
    except ValueError:
        print("Vui lòng nhập giá tiền xiên là số nguyên hợp lệ!")