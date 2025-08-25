CALCULATION_CONFIGS = [
    {
        'name': 'Lô Khung 2 ngày',
        'source': 'giai_3_5, giai_5_6',  # Lấy từ thuộc tính giai_3_5 của KetQuaXoSo
        'method': 'lokhung_2_ngay',  # Phương pháp: tổng số đầu + số cuối
    },
    {
        'name': 'Giải 5.6 (Tổng 2 số đầu)',
        'source': 'giai_5_6',  # Lấy từ thuộc tính giai_5_6 của KetQuaXoSo
        'method': 'sum_first_two',  # Phương pháp: tổng 2 số đầu
    },
    {
        'name': 'Giải đặc biệt (Tổng 2 số cuối)',
        'source': 'giai_db_1',  # Lấy từ thuộc tính giai_db_1 của KetQuaXoSo
        'method': 'last_two_digits',  # Phương pháp: lấy 2 số cuối
    },
    # Thêm các phép tính khác ở đây
]