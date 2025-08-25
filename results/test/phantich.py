def get_last_two_digits(number):
    """
    Hàm này trả về 2 số cuối của một số xổ số, đảm bảo chuỗi luôn có độ dài 2.
    Ví dụ: 94526 => '26'
    """
    s = str(number).zfill(2)
    return s[-2:]


def exact_match(today_results, tomorrow_results):
    """
    Thuật toán so sánh khớp hoàn toàn
    today_results và tomorrow_results là từ điển với khóa là tên giải và giá trị là danh sách các số xổ số.
    Trả về danh sách các kết quả khớp hoàn toàn theo dạng:
    (tên giải, số hôm nay, số kế tiếp)
    """
    matches = []
    for prize, numbers_today in today_results.items():
        for num_today in numbers_today:
            last_two_today = get_last_two_digits(num_today)
            # Kiểm tra trên tất cả các giải của ngày kế tiếp
            for prize_next, numbers_next in tomorrow_results.items():
                for num_next in numbers_next:
                    last_two_next = get_last_two_digits(num_next)
                    if last_two_today == last_two_next:
                        matches.append((prize, num_today, num_next))
    return matches


def hamming_distance(str1, str2):
    """Tính khoảng cách Hamming giữa 2 chuỗi có độ dài bằng nhau"""
    return sum(ch1 != ch2 for ch1, ch2 in zip(str1, str2))


def match_by_hamming(today_results, tomorrow_results, tolerance=1):
    """
    Thuật toán so sánh qua khoảng cách Hamming giữa 2 số cuối.
    Nếu khoảng cách <= tolerance => coi là có tương đồng.
    """
    matches = []
    for prize, numbers_today in today_results.items():
        for num_today in numbers_today:
            last_two_today = get_last_two_digits(num_today)
            for prize_next, numbers_next in tomorrow_results.items():
                for num_next in numbers_next:
                    last_two_next = get_last_two_digits(num_next)
                    distance = hamming_distance(last_two_today, last_two_next)
                    if distance <= tolerance:
                        matches.append((prize, num_today, num_next, distance))
    return matches


def match_by_numeric_difference(today_results, tomorrow_results, threshold=5):
    """
    So sánh giá trị số của 2 số cuối.
    Nếu hiệu số tuyệt đối <= threshold thì coi là tương đồng.
    """
    matches = []
    for prize, numbers_today in today_results.items():
        for num_today in numbers_today:
            last_two_today_int = int(get_last_two_digits(num_today))
            for prize_next, numbers_next in tomorrow_results.items():
                for num_next in numbers_next:
                    last_two_next_int = int(get_last_two_digits(num_next))
                    if abs(last_two_today_int - last_two_next_int) <= threshold:
                        matches.append((prize, num_today, num_next, abs(last_two_today_int - last_two_next_int)))
    return matches


if __name__ == "__main__":
    # Ví dụ dữ liệu: thay đổi theo cấu trúc dữ liệu thực tế
    # Cấu trúc: mỗi ngày là 1 dict với tên giải là khóa, giá trị là danh sách các số xổ số.
    today_results = {
        "Giải ĐB": [18703],
        "Giải nhất": [94526],
        "Giải nhì": [69259, 74878],
        "Giải ba": [5401, 90209, 58895, 71725, 85361, 56442],
        "Giải tư": [3115, 2717, 6551, 9220],
        "Giải năm": [1739, 9045, 1314, 6507, 925, 7029],
        "Giải sáu": [181, 60, 543],
        "Giải bảy": [38, 33, 25, 74],
    }
    tomorrow_results = {
        # Ví dụ dữ liệu cho ngày kế tiếp (ví dụ như ngày sau)
        "Giải ĐB": [94736],
        "Giải nhất": [47686],
        "Giải nhì": [18591, 18600],
        "Giải ba": [58455, 95764, 89581, 14306, 5719, 22468],
        "Giải tư": [4407, 3870, 1494, 1970],
        "Giải năm": [2282, 5159, 9925, 7162, 2117, 6165],
        "Giải sáu": [526, 301, 826],
        "Giải bảy": [78, 21, 50, 65],
        # Nếu có nhiều bảng khác trong ngày kế tiếp có thể tích hợp thêm
    }

    print("Kết quả khớp hoàn toàn:")
    for match in exact_match(today_results, tomorrow_results):
        print(match)

    print("\nKết quả theo Hamming distance (tolerance = 1):")
    for match in match_by_hamming(today_results, tomorrow_results, tolerance=1):
        print(match)

    print("\nKết quả theo hiệu số (threshold = 5):")
    for match in match_by_numeric_difference(today_results, tomorrow_results, threshold=5):
        print(match)