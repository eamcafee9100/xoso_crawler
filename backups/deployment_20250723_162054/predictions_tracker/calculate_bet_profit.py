import itertools

def calculate_combinations(n, k):
    """Tính số tổ hợp C(n, k)"""
    return len(list(itertools.combinations(range(n), k)))

def get_valid_numbers(prompt, min_nums, max_nums=None):
    """Nhập danh sách số hợp lệ từ người dùng"""
    while True:
        try:
            numbers = input(prompt).strip().split()
            numbers = [int(num) for num in numbers]
            if len(numbers) < min_nums or (max_nums and len(numbers) > max_nums):
                print(f"Vui lòng nhập từ {min_nums} đến {max_nums if max_nums else 'nhiều'} số.")
                continue
            if len(set(numbers)) != len(numbers):
                print("Các số phải khác nhau. Vui lòng nhập lại.")
                continue
            return set(numbers)
        except ValueError:
            print("Vui lòng chỉ nhập số nguyên. Thử lại.")

def calculate_profit(total_numbers, winning_numbers, bet_amount=10000):
    """Tính lợi nhuận cho xiên 2, xiên 3, xiên 4"""
    # Tỷ lệ ăn
    odds = {2: 17, 3: 65, 4: 250}
    results = {}

    for k in [2, 3, 4]:
        # Tính tổng số xiên
        total_bets = calculate_combinations(len(total_numbers), k)
        # Tính số xiên trúng
        winning_bets = calculate_combinations(len(winning_numbers), k) if len(winning_numbers) >= k else 0
        # Tính chi phí
        cost = total_bets * bet_amount
        # Tính tiền thắng
        win_amount = winning_bets * bet_amount * odds[k]
        # Tính lợi nhuận
        profit = win_amount - cost

        results[k] = {
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'cost': cost,
            'win_amount': win_amount,
            'profit': profit
        }

    # Tính tổng hợp
    total_cost = sum(results[k]['cost'] for k in results)
    total_win = sum(results[k]['win_amount'] for k in results)
    total_profit = total_win - total_cost

    return results, total_cost, total_win, total_profit

def format_vnd(amount):
    """Định dạng số tiền thành VNĐ"""
    return f"{amount:,} VNĐ"

def main():
    print("Chương trình tính lợi nhuận xiên 2, xiên 3, xiên 4")
    print("Tỷ lệ ăn: xiên 2 (x17), xiên 3 (x65), xiên 4 (x250)")
    print("Mỗi xiên: 10,000 VNĐ")

    # Nhập các số
    total_numbers = get_valid_numbers("Nhập các số (cách nhau bằng dấu cách, ít nhất 4 số): ", min_nums=4)
    print(f"Các số đã chọn: {sorted(total_numbers)}")

    # Nhập các số trúng
    winning_numbers = get_valid_numbers(
        f"Nhập các số trúng (tối đa {len(total_numbers)} số): ",
        min_nums=0, max_nums=len(total_numbers)
    )
    print(f"Các số trúng: {sorted(winning_numbers)}")

    # Tính toán
    results, total_cost, total_win, total_profit = calculate_profit(total_numbers, total_numbers & winning_numbers)

    # In kết quả
    print("\nKết quả:")
    for k in [2, 3, 4]:
        print(f"\nXiên {k}:")
        print(f"- Số xiên: {results[k]['total_bets']}")
        print(f"- Số xiên trúng: {results[k]['winning_bets']}")
        print(f"- Tổng chi phí: {format_vnd(results[k]['cost'])}")
        print(f"- Tiền thắng mỗi xiên: {format_vnd(results[k]['win_amount'] // results[k]['winning_bets'] if results[k]['winning_bets'] else 0)}")
        print(f"- Tổng tiền thắng: {format_vnd(results[k]['win_amount'])}")
        print(f"- Lợi nhuận: {format_vnd(results[k]['profit'])} {'(lỗ)' if results[k]['profit'] < 0 else ''}")

    print("\nTổng hợp:")
    print(f"- Tổng chi phí: {format_vnd(total_cost)}")
    print(f"- Tổng tiền thắng: {format_vnd(total_win)}")
    print(f"- Lợi nhuận tổng: {format_vnd(total_profit)} {'(lỗ)' if total_profit < 0 else ''}")

if __name__ == "__main__":
    main()