import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from .models import KetQuaXoSo
import time
import re
from datetime import datetime

def crawl_xoso_thantai(target_date=None):
    """
    Crawl kết quả xổ số từ xosothantai.mobi với xác nhận ngày từ thẻ <h2>
    :param target_date: Ngày cần crawl (datetime.date object). Nếu None sẽ lấy ngày hiện tại
    :return: Tuple (success: bool, message: str)
    """
    base_url = "https://xosothantai.mobi/xsmb-sxmb-xstd-xshn-kqxsmb-ket-qua-xo-so-mien-bac.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Xác định ngày cần crawl
        if target_date is None:
            target_date = datetime.now().date()
        
        # Thêm tham số ngày vào URL
        url = f"{base_url}?ngay={target_date.day}&thang={target_date.month}&nam={target_date.year}"
        
        # Gửi request và parse HTML
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Xác nhận ngày từ thẻ <h2>
        date_header = soup.find('h2')
        if not date_header:
            return False, "Không tìm thấy thẻ tiêu đề chứa ngày"
        
        # Trích xuất ngày từ nội dung thẻ h2 (ví dụ: "Kết quả xổ số miền Bắc 14-04-2025")
        date_text = date_header.get_text().strip()
        date_match = re.search(r'(\d{2})-(\d{2})-(\d{4})', date_text)
        
        if not date_match:
            return False, f"Không tìm thấy ngày trong tiêu đề: {date_text}"
        
        day, month, year = map(int, date_match.groups())
        page_date = date(year, month, day)
        
        # Xác nhận ngày trên trang web khớp với ngày cần crawl
        if page_date != target_date:
            return False, f"Ngày không khớp. Mong đợi: {target_date}, Trang web: {page_date}"
        
        # 2. Tiếp tục xử lý các giải như trước...
        result_table = soup.find('table', {'class': 'kqmb extendable'})
        if not result_table:
            return False, "Không tìm thấy bảng kết quả"
        
        ket_qua = {
            'ngay': target_date,
            'giai_db': '',
            'giai_1': '',
            'giai_2': '',
            'giai_3': '',
            'giai_4': '',
            'giai_5': '',
            'giai_6': '',
            'giai_7': ''
        }

        # 3. Xử lý từng giải theo cấu trúc HTML cụ thể
        # Giải Đặc Biệt (class="v-gdb")
        giai_db = soup.find('span', {'class': 'v-gdb'})
        if giai_db:
            ket_qua['giai_db'] = giai_db.text.strip()

        # Giải 1 (class="v-g1")
        giai_1 = soup.find('span', {'class': 'v-g1'})
        if giai_1:
            ket_qua['giai_1'] = giai_1.text.strip()

        # Giải 2 (class bắt đầu bằng "v-g2-")
        giai_2 = [span.text.strip() for span in soup.find_all('span', class_=lambda x: x and x.startswith('v-g2-'))]
        if giai_2:
            ket_qua['giai_2'] = ",".join(giai_2[:2])  # Chỉ lấy 2 số đầu

        # Giải 3 (class bắt đầu bằng "v-g3-")
        giai_3 = [span.text.strip() for span in soup.find_all('span', class_=lambda x: x and x.startswith('v-g3-'))]
        if giai_3:
            # Chia thành 2 hàng, mỗi hàng 3 số
            ket_qua['giai_3'] = "|".join([
                ",".join(giai_3[:3]),
                ",".join(giai_3[3:6])
            ])

        # Giải 4 (class bắt đầu bằng "v-g4-")
        giai_4 = [span.text.strip() for span in soup.find_all('span', class_=lambda x: x and x.startswith('v-g4-'))]
        if giai_4:
            ket_qua['giai_4'] = ",".join(giai_4[:4])  # Lấy 4 số

        # Giải 5 (class bắt đầu bằng "v-g5-")
        giai_5 = [span.text.strip() for span in soup.find_all('span', class_=lambda x: x and x.startswith('v-g5-'))]
        if giai_5:
            # Chia thành 2 hàng, mỗi hàng 3 số
            ket_qua['giai_5'] = "|".join([
                ",".join(giai_5[:3]),
                ",".join(giai_5[3:6])
            ])

        # Giải 6 (class bắt đầu bằng "v-g6-")
        giai_6 = [span.text.strip() for span in soup.find_all('span', class_=lambda x: x and x.startswith('v-g6-'))]
        if giai_6:
            ket_qua['giai_6'] = ",".join(giai_6[:3])  # Lấy 3 số

        # Giải 7 (class bắt đầu bằng "v-g7-")
        giai_7 = [span.text.strip() for span in soup.find_all('span', class_=lambda x: x and x.startswith('v-g7-'))]
        if giai_7:
            ket_qua['giai_7'] = ",".join(giai_7[:4])  # Lấy 4 số

        # 4. Lưu vào database
        KetQuaXoSo.objects.update_or_create(
            ngay=ket_qua['ngay'],
            defaults=ket_qua
        )
        return True

    except Exception as e:
        print(f"[ERROR] Lỗi khi crawl dữ liệu ngày {target_date}: {str(e)}")
        return False
    
def crawl_thang_4():
    """Crawl tất cả các ngày trong tháng 4/2023"""
    start_date = date(2025, 4, 1)  # Thay năm nếu cần
    end_date = date(2025, 4, 27)   # Thay năm nếu cần
    results = []
    current_date = start_date
    while current_date <= end_date:
        success, message = crawl_xoso_thantai(current_date)
        results.append({
            'date': current_date.strftime('%d/%m/%Y'),
            'success': success,
            'message': message
        })
        current_date += timedelta(days=1)
        time.sleep(1)  # Thêm delay để tránh bị block
    
    return results