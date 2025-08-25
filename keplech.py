import datetime
import numpy as np

# BỘ SỐ KÉP LỆCH ĐẦY ĐỦ
KEP_DUONG = [
    '05', '50', '16', '61', '27', '72', '38', '83', '49', '94',
    '06', '60', '07', '70', '08', '80', '09', '90', '15', '51',
    '26', '62', '37', '73', '48', '84', '59', '95', '13', '31',
    '24', '42', '35', '53', '46', '64', '57', '75', '68', '86'
]

KEP_AM = [
    '07', '70', '14', '41', '29', '92', '36', '63', '58', '85'
]

SAT_KEP = [
    '04', '40', '06', '60', '15', '51', '95', '59', '17', '71',
    '14', '41', '28', '82', '26', '62', '37', '73', '36', '63',
    '39', '93', '48', '84'
]

# QUY ƯỚC BÓNG ÂM DƯƠNG
BONG_DUONG = {0:5, 1:6, 2:7, 3:8, 4:9, 5:0, 6:1, 7:2, 8:3, 9:4}
BONG_AM = {0:7, 1:4, 2:9, 3:6, 4: None, 5:8, 6: None, 7:0, 8:5, 9:2}

def kiem_tra_kep(so):
    """Kiểm tra số có thuộc bộ kép lệch nào"""
    if so in KEP_DUONG: return "Dương"
    if so in KEP_AM: return "Âm"
    if so in SAT_KEP: return "Sát kép"
    return None

def tao_dan_kep(loai):
    """Tạo dàn kép theo loại"""
    if loai == "Dương": return KEP_DUONG
    if loai == "Âm": return KEP_AM
    if loai == "Sát kép": return SAT_KEP
    return []

def phan_tich_tuan(ket_qua):
    """Phân tích kết quả tuần và trả về thống kê"""
    thong_ke = {
        'Dương': {'con': [], 'lan': 0},
        'Âm': {'con': [], 'lan': 0},
        'Sát kép': {'con': [], 'lan': 0},
        'khac': []
    }
    
    for ngay, giai_db in ket_qua.items():
        so_de = giai_db[-2:]  # 2 số cuối giải đặc biệt
        
        kep_type = kiem_tra_kep(so_de)
        if kep_type:
            thong_ke[kep_type]['lan'] += 1
            if so_de not in thong_ke[kep_type]['con']:
                thong_ke[kep_type]['con'].append(so_de)
        else:
            thong_ke['khac'].append(so_de)
    
    return thong_ke

def goi_y_danh(ket_qua, thu):
    """Tạo gợi ý đánh dựa trên phân tích tuần"""
    phan_tich = phan_tich_tuan(ket_qua)
    goi_y = []
    
    # QUY TẮC 1: Dựa vào giải đặc biệt thứ 2
    if 'Thu 2' in ket_qua:
        dau_so = ket_qua['Thu 2'][0]
        goi_y.append(f"Đánh dàn đuôi {dau_so} cả tuần: {[str(i).zfill(2) for i in range(0, 100) if str(i).zfill(2)[1] == dau_so][:10]}...")
    
    # QUY TẮC 2: Kép xuất hiện ít
    for loai in ['Dương', 'Âm', 'Sát kép']:
        if phan_tich[loai]['lan'] < 2:
            goi_y.append(f"Nuôi kép {loai} chưa ra: {[so for so in tao_dan_kep(loai) if so not in phan_tich[loai]['con']][:5]}...")
    
    # QUY TẮC 3: Kép xuất hiện nhiều
    for loai in ['Dương', 'Âm', 'Sát kép']:
        if phan_tich[loai]['lan'] >= 3:
            goi_y.append(f"CẢNH BÁO: Kép {loai} ra {phan_tich[loai]['lan']} lần, không nuôi tiếp")
    
    # QUY TẮC 4: Kép chưa xuất hiện trong tuần
    if all(phan_tich[loai]['lan'] == 0 for loai in ['Dương', 'Âm', 'Sát kép']):
        goi_y.append("Tập trung vào kép Âm: " + ", ".join(KEP_AM[:5]))
    
    # QUY TẮC 5: Dựa vào ngày trong tuần
    if thu == 0:  # Thứ 2
        goi_y.append("Đánh mạnh kép Dương đầu tuần")
    elif thu == 6:  # Chủ nhật
        goi_y.append("Cuối tuần tập trung kép Âm và Sát kép")
    
    return goi_y

def in_ket_qua(ket_qua, thu):
    """In kết quả phân tích và gợi ý"""
    print("\n" + "="*50)
    print(f"PHÂN TÍCH KÉP LỆCH TUẦN {datetime.date.today().isocalendar()[1]}")
    print("="*50)
    
    # In kết quả các ngày
    print("\nKẾT QUẢ TUẦN:")
    for ngay, so in ket_qua.items():
        kep_type = kiem_tra_kep(so[-2:])
        icon = "🔴" if kep_type else "⚪"
        print(f"{ngay}: {so} {icon} {kep_type if kep_type else ''}")
    
    # Phân tích chi tiết
    phan_tich = phan_tich_tuan(ket_qua)
    print("\nTHỐNG KÊ KÉP LỆCH:")
    for loai in ['Dương', 'Âm', 'Sát kép']:
        print(f"- {loai}: {phan_tich[loai]['lan']} lần ({', '.join(phan_tich[loai]['con'])})")
    
    # Gợi ý đánh
    goi_y = goi_y_danh(ket_qua, thu)
    print("\nGỢI Ý ĐÁNH CHO NGÀY TIẾP THEO:")
    for i, y in enumerate(goi_y, 1):
        print(f"{i}. {y}")
    
    # Lưu ý vàng
    print("\n" + "⚠️ LƯU Ý VÀNG:")
    print("- Không nuôi kép quá 7 ngày")
    print("- Dành chỉ 1-3% vốn cho kép lệch")
    print("- Kết hợp với phương pháp khác (bạc nhớ, cầu chạy...)")
    print("- Kép lệch chỉ chiếm 12-15% kết quả - đừng phụ thuộc hoàn toàn")

# DỮ LIỆU MẪU - THAY BẰNG DỮ LIỆU THỰC
ket_qua_tuan = {
    'Thu 2': '90207',  # Kép âm 58
    'Thu 3': '77818',  # Không kép
    'Thu 4': '85644',  # Kép dương 49
    'Thu 5': '44369',  # Kép âm 36
    'Thu 6': '63315',  # Không kép
    'Thu 7': '18512',  # Kép dương 72
    'Chu nhat': '51105'  # Kép âm 85
}

# Chạy chương trình với thứ hiện tại (0=Thứ 2, 6=Chủ nhật)
in_ket_qua(ket_qua_tuan, thu=datetime.datetime.today().weekday())