import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from concurrent.futures import ThreadPoolExecutor, as_completed
from results.models import KetQuaXoSo
import logging
import lxml
# Cấu hình logging
logger = logging.getLogger(__name__)

def process_prize_table(soup):
    """
    Xử lý bảng kết quả từ HTML và trả về dictionary chứa các giải
    Args:
        soup: BeautifulSoup object chứa nội dung HTML
    Returns:
        dict: Dictionary chứa kết quả các giải
    """
    prizes = {
        'dac_biet': '',          # Giải đặc biệt
        'giai_nhat': '',         # Giải nhất
        'giai_nhi': [],          # Giải nhì
        'giai_ba': [],           # Giải ba
        'giai_tu': [],           # Giải tư
        'giai_nam': [],          # Giải năm
        'giai_sau': [],          # Giải sáu
        'giai_bay': [],          # Giải bảy
        'loai_ve': []            # Các loại vé đặc biệt
    }

    try:
        # Tìm bảng kết quả chính
        result_table = soup.find('table', {'id': 'table-'})
        if not result_table:
            raise ValueError("Không tìm thấy bảng kết quả với id='table-'")

        tbody = result_table.find('tbody')
        if not tbody:
            raise ValueError("Không tìm thấy tbody trong bảng kết quả")

        # Xử lý từng dòng trong bảng
        for row in tbody.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) != 2:
                continue

            first_col = cols[0].get_text(strip=True)
            second_col = cols[1]

            

            # Xử lý các giải thưởng
            if first_col == 'ĐB':
                prizes['dac_biet'] = second_col.find('span', class_='xs').get_text(strip=True)
            elif first_col == 'G.1':
                prizes['giai_nhat'] = second_col.find('span', class_='xs').get_text(strip=True)
            elif first_col == 'G.2':
                prizes['giai_nhi'] = [span.get_text(strip=True) for span in second_col.find_all('span', class_=lambda x: x and 'mb_g2' in x)]
            elif first_col == 'G.3':
                prizes['giai_ba'] = [span.get_text(strip=True) for span in second_col.find_all('span', class_=lambda x: x and 'mb_g3' in x)]
            elif first_col == 'G.4':
                prizes['giai_tu'] = [span.get_text(strip=True) for span in second_col.find_all('span', class_=lambda x: x and 'mb_g4' in x)]
            elif first_col == 'G.5':
                prizes['giai_nam'] = [span.get_text(strip=True) for span in second_col.find_all('span', class_=lambda x: x and 'mb_g5' in x)]
            elif first_col == 'G.6':
                prizes['giai_sau'] = [span.get_text(strip=True) for span in second_col.find_all('span', class_=lambda x: x and 'mb_g6' in x)]
            elif first_col == 'G.7':
                prizes['giai_bay'] = [span.get_text(strip=True) for span in second_col.find_all('span', class_=lambda x: x and 'mb_g7' in x)]

        # Validate dữ liệu
        if not prizes['dac_biet']:
            raise ValueError("Không lấy được giải đặc biệt")

        return prizes

    except Exception as e:
        logger.error(f"Lỗi khi xử lý bảng kết quả: {str(e)}")
        raise

def crawl_single_date(current_date):
    """
    Crawl kết quả xổ số cho một ngày cụ thể
    Args:
        current_date: datetime.date object
    Returns:
        dict: Kết quả crawl cho ngày này
    """
    formatted_date = current_date.strftime('%d-%m-%Y')
    url = f'https://ketqua.me/xsmb-xo-so-mien-bac-ngay-{formatted_date}'
    
    result_data = {
        'date': current_date,
        'success': False,
        'error': None,
        'object': None,
        'prizes': None
    }

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'vi-VN,vi;q=0.9'
        }

        # Thực hiện request với retry
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Kiểm tra nội dung trả về
                if 'Kết quả xổ số miền Bắc' not in response.text:
                    raise ValueError("Nội dung không phải trang kết quả xổ số")
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Kiểm tra thông báo chưa có kết quả
                alert = soup.find('div', class_=lambda x: x and 'alert' in x.lower())
                if alert and "chưa có kết quả" in alert.get_text(strip=True).lower():
                    result_data['error'] = f"Chưa có kết quả ngày {formatted_date}"
                    return result_data
                
                # Xử lý bảng kết quả
                prizes = process_prize_table(soup)
                
                # Chuẩn bị dữ liệu lưu vào database
                xoso_data = {
                    'ngay': make_aware(datetime.combine(current_date, datetime.min.time())),
                    'giai_db': prizes['dac_biet'],
                    'giai_1': prizes['giai_nhat'],
                    'giai_2': ' '.join(prizes['giai_nhi']),
                    'giai_3': ' '.join(prizes['giai_ba']),
                    'giai_4': ' '.join(prizes['giai_tu']),
                    'giai_5': ' '.join(prizes['giai_nam']),
                    'giai_6': ' '.join(prizes['giai_sau']),
                    'giai_7': ' '.join(prizes['giai_bay']),
                    # 'loai_ve': '|'.join(prizes['loai_ve']),
                    'thu': current_date.strftime('%A')[:3].upper()
                }
                
                # Lưu vào database
                obj, created = KetQuaXoSo.objects.update_or_create(
                    ngay=xoso_data['ngay'],
                    defaults=xoso_data
                )
                
                result_data.update({
                    'success': True,
                    'object': obj,
                    'prizes': prizes
                })
                
                return result_data

            except requests.RequestException as e:
                if attempt == 2:  # Lần thử cuối cùng
                    raise
                continue

    except Exception as e:
        logger.error(f"Lỗi khi crawl ngày {formatted_date}: {str(e)}")
        result_data['error'] = str(e)
        return result_data

def crawl_xsmb_ketquame(start_date=None, end_date=None):
    """
    Crawl kết quả xổ số miền Bắc theo khoảng ngày
    Args:
        start_date (datetime/str): Ngày bắt đầu (dd-mm-yyyy)
        end_date (datetime/str): Ngày kết thúc (mặc định = start_date)
    Returns:
        list: Danh sách kết quả các ngày (luôn trả về list)
    """
    try:
        # Xử lý ngày đầu vào
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%d-%m-%Y').date()
        elif not start_date:
            start_date = datetime.now().date()
        
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%d-%m-%Y').date()
        elif not end_date:
            end_date = start_date

        # Validate ngày
        if start_date > end_date:
            raise ValueError("Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc")
        
        if (end_date - start_date).days > 90:
            raise ValueError("Chỉ có thể crawl tối đa 90 ngày một lần")

        results = []
        
        # Xử lý đa luồng
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            current_date = start_date
            
            while current_date <= end_date:
                futures.append(executor.submit(crawl_single_date, current_date))
                current_date += timedelta(days=1)
            
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.error(f"Lỗi khi xử lý kết quả: {str(e)}")
                    results.append({
                        'date': current_date,
                        'success': False,
                        'error': str(e),
                        'object': None,
                        'prizes': None
                    })
        
        # Sắp xếp kết quả theo ngày
        results.sort(key=lambda x: x['date'])
        return results

    except Exception as e:
        logger.error(f"Lỗi hệ thống trong crawl_xsmb_ketquame: {str(e)}")
        # Trả về list chứa thông tin lỗi
        error_date = start_date if start_date else datetime.now().date()
        return [{
            'date': error_date,
            'success': False,
            'error': f"Lỗi hệ thống: {str(e)}",
            'object': None,
            'prizes': None
        }]