def get_last_two_digits(number):
    """
    Lấy 2 số cuối của một số dưới dạng chuỗi có độ dài tối thiểu 2.
    Ví dụ: 94526 -> '26', 89 -> '89', 08 -> '08'
    """
    s = str(number).zfill(2)
    return s[-2:]


def extract_pattern(prize_list, pos_pair):
    """
    Hàm này cho phép trích xuất 2 chữ số theo quy tắc xác định từ một danh sách các số.
    param:
       prize_list: danh sách số của một giải, ví dụ: [89, 8, 95, 67]. 
                   Lưu ý: nếu số có số 0 đứng đầu, đảm bảo chuyển về chuỗi có định dạng 2 chữ số (ví dụ "08").
       pos_pair: tuple gồm 2 chỉ số (i, j) đại diện cho vị trí trong số ở danh sách, 
                 trong đó:
                    i: vị trí của chữ số từ số thứ nhất
                    j: vị trí của chữ số từ số thứ hai
                 Ví dụ: (0, 0) nghĩa là lấy chữ số đầu tiên từ số ở vị trí thứ 2 và chữ số đầu tiên từ số ở vị trí thứ 3 của danh sách.
    Trả về:
       Một chuỗi gồm 2 chữ số được ghép lại.
    """
    # Ví dụ: prize_list[1] = "08" và prize_list[2] = "95"
    # Nếu pos_pair = (0, 0): lấy "0" từ "08" và "9" từ "95", ghép lại thành "09"
    try:
        str1 = str(prize_list[1]).zfill(2)
        str2 = str(prize_list[2]).zfill(2)
        digit1 = str1[pos_pair[0]]
        digit2 = str2[pos_pair[1]]
        return digit1 + digit2
    except IndexError:
        return None


def exact_match_algorithm(today_results, future_results, prize_group):
    """
    Thuật toán so sánh trực tiếp các 2 chữ số đã trích xuất từ một quy tắc
    của ngày hôm nay với 2 chữ số cuối của các số trong cùng một giải của ngày kế tiếp.
    param:
         today_results: danh sách kết quả của một giải ở ngày hôm nay (ví dụ Giải tư của ngày hôm nay)
         future_results: danh sách kết quả của một giải ở ngày kế tiếp (ví dụ Giải tư của ngày sau)
         prize_group: tên giải, dùng cho việc in ra thông tin (ví dụ: "Giải tư")
    Trả về:
         Danh sách các tuple (số_today, số_future) khi mà 2 chữ số trích xuất từ today_results trùng với 2 chữ số cuối của số trong future_results.
    """
    matches = []
    # Giả sử chúng ta trích xuất 2 chữ số theo một quy tắc đã định (ví dụ như hàm extract_pattern với (0,0))
    extracted = extract_pattern(today_results, (0, 0))
    if not extracted:
        return matches
    for num in future_results:
        last_two = get_last_two_digits(num)
        if extracted == last_two:
            matches.append( (extracted, num) )
    print(f"Trong {prize_group}, với số trích xuất là {extracted}, ta tìm thấy các kết quả trùng trong ngày kế tiếp: {matches}")
    return matches


def hamming_distance(str1, str2):
    """Tính khoảng cách Hamming giữa 2 chuỗi có độ dài bằng nhau."""
    if len(str1) != len(str2):
        return None
    return sum(ch1 != ch2 for ch1, ch2 in zip(str1, str2))


def numeric_difference_analysis(seq_today, seq_future):
    """
    Phân tích số học giữa chuỗi các số đã trích xuất trong ngày hôm nay và các số (2 chữ số cuối)
    trong ngày kế tiếp.
    seq_today: danh sách các chuỗi 2 chữ số từ ngày hôm nay (có thể trích xuất theo nhiều quy tắc khác nhau)
    seq_future: danh sách các chuỗi 2 chữ số từ ngày kế tiếp
    Trả về: danh sách các tuple (số_today, số_future, hiệu số tuyệt đối)
    """
    matches = []
    for number_today in seq_today:
        for number_future in seq_future:
            diff = abs(int(number_today) - int(number_future))
            matches.append((number_today, number_future, diff))
    return matches


if __name__ == "__main__":
    # Dữ liệu ngày 23/06/2025 (Thứ hai)
    # Giả sử chúng ta có dữ liệu cho Giải bảy dưới dạng danh sách các số.
    results_thu2_g7 = [89, "08", 95, 67]
    # Dữ liệu ngày 24/06/2025 (Thứ ba)
    # Giả sử chúng ta có dữ liệu cho Giải tư của ngày sau dưới dạng danh sách các số.
    results_thu3_g4 = [8027, 7802, "0289", 8409]  # Ví dụ: số 8409 có 2 chữ số cuối là "09"
    
    # 1. Sử dụng quy tắc trích xuất như ví dụ:
    # Lấy chữ số đầu của số thứ 2 (index=1) và chữ số đầu của số thứ 3 (index=2) của Giải bảy tại Thứ hai
    extracted_2digit = extract_pattern(results_thu2_g7, (0, 0))
    print(f"Số trích xuất từ Giải bảy (Thứ hai) theo quy tắc (0,0): {extracted_2digit}")
    
    # 2. So sánh kết quả trích xuất với 2 chữ số cuối của các số trong Giải tư ngày kế tiếp
    future_two_digits = [get_last_two_digits(num) for num in results_thu3_g4]
    print(f"2 chữ số cuối của các số trong Giải tư (Thứ ba): {future_two_digits}")
    
    # 3. Kiểm tra xem có kết quả nào trùng khớp không theo thuật toán so sánh trực tiếp
    match_results = exact_match_algorithm(results_thu2_g7, results_thu3_g4, "Giải tương ứng")
    
    # 4. Giả sử bạn thu thập dãy số trích xuất qua nhiều ngày và áp dụng phân tích số học
    # Ví dụ, với danh sách trích xuất từ ngày hôm nay:
    extracted_list_today = [extract_pattern(results_thu2_g7, (0, 0))]
    # Và tập hợp 2 chữ số cuối từ ngày kế tiếp từ Giải tư:
    extracted_list_future = future_two_digits
    numeric_matches = numeric_difference_analysis(extracted_list_today, extracted_list_future)
    print("Kết quả phân tích sự chênh lệch số học:")
    for res in numeric_matches:
        print(f"Trích xuất: {res[0]}, Kết quả tương ứng: {res[1]}, Hiệu số: {res[2]}")
    
    # 5. Thêm phân tích khoảng cách Hamming (nếu muốn cho phép sai lệch 1 chữ số ví dụ)
    for num_future in future_two_digits:
        dist = hamming_distance(extracted_2digit, num_future)
        print(f"Khoảng cách Hamming giữa {extracted_2digit} và {num_future}: {dist}")