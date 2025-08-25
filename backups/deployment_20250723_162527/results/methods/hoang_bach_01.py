from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class HoangBach01Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 01 Đề 2 số
    Dự đoán từ bóng của tổng giải 1.1.2 + 3.6.4 + 4.4.2 và bóng của tổng giải 2.1.3 + 4.1.1 + 4.3.4
    """
    def get_code(self) -> str:
        return "hoang_bach_01"
    
    def get_name(self) -> str:
        return "Hoang Bach 01 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ bóng của tổng giải 1.1.2 + 3.6.4 + 4.4.2 và bóng của tổng giải 2.1.3 + 4.1.1 + 4.3.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_1 = data.get('giai_1', '')  # Giải 1, 5 chữ số
        giai_3_6 = data.get('giai_3_6', '')  # Giải 3.6, 5 chữ số
        giai_4_4 = data.get('giai_4_4', '')  # Giải 4.4, 4 chữ số
        giai_2_1 = data.get('giai_2_1', '')  # Giải 2.1, 5 chữ số
        giai_4_1 = data.get('giai_4_1', '')  # Giải 4.1, 4 chữ số
        giai_4_3 = data.get('giai_4_3', '')  # Giải 4.3, 4 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_1) == 5 and len(giai_3_6) == 5 and len(giai_4_4) == 4 and 
                len(giai_2_1) == 5 and len(giai_4_1) == 4 and len(giai_4_3) == 4):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_1={giai_1}, giai_3_6={giai_3_6}, giai_4_4={giai_4_4}, "
                          f"giai_2_1={giai_2_1}, giai_4_1={giai_4_1}, giai_4_3={giai_4_3}")
            return {'two_digits_special': []}
        
        try:
            # Tính số thứ nhất: bóng của tổng giải 1.1.2 + 3.6.4 + 4.4.2
            sum_first = (int(giai_1[1]) + int(giai_3_6[3]) + int(giai_4_4[1])) % 10
            first_nums = [str(sum_first), str(get_ball_number(int(sum_first)))]
            # Tính số thứ hai: bóng của tổng giải 2.1.3 + 4.1.1 + 4.3.4
            sum_second = (int(giai_2_1[2]) + int(giai_4_1[0]) + int(giai_4_3[3])) % 10
            second_nums = [str(sum_second), str(get_ball_number(sum_second))]
            
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = set()
            for first in first_nums:
                for second in second_nums:
                    # Thêm cặp số thẳng
                    two_digits.add(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.add(f"{second}{first}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 01 đề 2 số: {str(e)}")
            return {'two_digits_special': []}
        
class HoangBach02Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 02 Đề 2 số
    Dự đoán từ bóng của tổng giải 3.1.2 + 3.3.5 + 3.5.4 và bóng của tổng giải 3.4.1 + 4.3.4 + 7.4.2
    """
    def get_code(self) -> str:
        return "hoang_bach_02"
    
    def get_name(self) -> str:
        return "Hoang Bach 02 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ bóng của tổng giải 3.1.2 + 3.3.5 + 3.5.4 và bóng của tổng giải 3.4.1 + 4.3.4 + 7.4.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_db = data.get('giai_db', '')    # Giải đặc biệt, 5 chữ số
        giai_1 = data.get('giai_1', '')      # Giải 1, 5 chữ số
        giai_3_1 = data.get('giai_3_1', '')  # Giải 3.1, 5 chữ số
        giai_3_3 = data.get('giai_3_3', '')  # Giải 3.3, 5 chữ số
        giai_3_5 = data.get('giai_3_5', '')  # Giải 3.5, 5 chữ số
        giai_3_4 = data.get('giai_3_4', '')  # Giải 3.4, 5 chữ số
        giai_4_3 = data.get('giai_4_3', '')  # Giải 4.3, 4 chữ số
        giai_7_4 = data.get('giai_7_4', '')  # Giải 7.4, 2 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_db) == 5 and len(giai_1) == 5 and 
                len(giai_3_1) == 5 and len(giai_3_3) == 5 and len(giai_3_5) == 5 and len(giai_3_4) == 5 and 
                len(giai_4_3) == 4 and len(giai_7_4) == 2):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_db={giai_db}, giai_1={giai_1}, giai_3_1={giai_3_1}, giai_3_3={giai_3_3}, "
                          f"giai_3_5={giai_3_5}, giai_3_4={giai_3_4}, giai_4_3={giai_4_3}, giai_7_4={giai_7_4}")
            return {'two_digits_special': []}
        
        try:
            # Tính số thứ nhất: bóng của tổng giải 3.1.2 + 3.3.5 + 3.5.4
            sum_first = (int(giai_3_1[1]) + int(giai_3_3[4]) + int(giai_3_5[3])) % 10
            first_nums = [str(sum_first), str(get_ball_number(sum_first))]
            
            # Tính số thứ hai: bóng của tổng giải 3.4.1 + 4.3.4 + 7.4.2
            sum_second = (int(giai_3_4[0]) + int(giai_4_3[3]) + int(giai_7_4[1])) % 10
            second_nums = [str(sum_second), str(get_ball_number(sum_second))]
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            for first in first_nums:
                for second in second_nums:
                    two_digits.add(f"{first}{second}")
                    two_digits.add(f"{second}{first}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 02 đề 2 số: {str(e)}")
            return {'two_digits_special': []}
        
from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class HoangBach03Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 03 Đề 2 số
    Dự đoán từ tổng giải 2.1.5 + 3.2.1 + 3.5.2 và tổng giải 4.1.4 + 5.3.2 + 5.5.2,
    tổng giải 2.2.3 + 2.2.4 + 2.2.5 và tổng giải 3.6.2 + 3.6.3 + 3.6.4
    """
    def get_code(self) -> str:
        return "hoang_bach_03"
    
    def get_name(self) -> str:
        return "Hoang Bach 03 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ tổng giải 2.1.5 + 3.2.1 + 3.5.2 và tổng giải 4.1.4 + 5.3.2 + 5.5.2, " \
               "tổng giải 2.2.3 + 2.2.4 + 2.2.5 và tổng giải 3.6.2 + 3.6.3 + 3.6.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_db = data.get('giai_db', '')    # Giải đặc biệt, 5 chữ số
        giai_1 = data.get('giai_1', '')      # Giải 1, 5 chữ số
        giai_2_1 = data.get('giai_2_1', '')  # Giải 2.1, 5 chữ số
        giai_2_2 = data.get('giai_2_2', '')  # Giải 2.2, 5 chữ số
        giai_3_2 = data.get('giai_3_2', '')  # Giải 3.2, 5 chữ số
        giai_3_5 = data.get('giai_3_5', '')  # Giải 3.5, 5 chữ số
        giai_3_6 = data.get('giai_3_6', '')  # Giải 3.6, 5 chữ số
        giai_4_1 = data.get('giai_4_1', '')  # Giải 4.1, 4 chữ số
        giai_5_3 = data.get('giai_5_3', '')  # Giải 5.3, 4 chữ số
        giai_5_5 = data.get('giai_5_5', '')  # Giải 5.5, 4 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_db) == 5 and len(giai_1) == 5 and 
                len(giai_2_1) == 5 and len(giai_2_2) == 5 and 
                len(giai_3_2) == 5 and len(giai_3_5) == 5 and len(giai_3_6) == 5 and 
                len(giai_4_1) == 4 and len(giai_5_3) == 4 and len(giai_5_5) == 4):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_db={giai_db}, giai_1={giai_1}, giai_2_1={giai_2_1}, giai_2_2={giai_2_2}, "
                          f"giai_3_2={giai_3_2}, giai_3_5={giai_3_5}, giai_3_6={giai_3_6}, "
                          f"giai_4_1={giai_4_1}, giai_5_3={giai_5_3}, giai_5_5={giai_5_5}")
            return {'two_digits_special': []}
        
        try:
            # Tính số thứ nhất: tổng giải 2.1.5 + 3.2.1 + 3.5.2
            sum_first = (int(giai_2_1[4]) + int(giai_3_2[0]) + int(giai_3_5[1])) % 10
            first_nums = [str(sum_first), str(get_ball_number(sum_first))]
            
            # Tính số thứ hai: tổng giải 4.1.4 + 5.3.2 + 5.5.2
            sum_second = (int(giai_4_1[3]) + int(giai_5_3[1]) + int(giai_5_5[1])) % 10
            second_nums = [str(sum_second), str(get_ball_number(sum_second))]
            
            # Tính số thứ ba: tổng giải 2.2.3 + 2.2.4 + 2.2.5
            sum_third = (int(giai_2_2[2]) + int(giai_2_2[3]) + int(giai_2_2[4])) % 10
            third_nums = [str(sum_third), str(get_ball_number(sum_third))]
            
            # Tính số thứ tư: tổng giải 3.6.2 + 3.6.3 + 3.6.4
            sum_fourth = (int(giai_3_6[1]) + int(giai_3_6[2]) + int(giai_3_6[3])) % 10
            fourth_nums = [str(sum_fourth), str(get_ball_number(sum_fourth))]
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số từ số thứ 1 và số thứ 2
            for first in first_nums:
                for second in second_nums:
                    two_digits.add(f"{first}{second}")
                    two_digits.add(f"{second}{first}")
            # Cặp số từ số thứ 3 và số thứ 4
            for third in third_nums:
                for fourth in fourth_nums:
                    two_digits.add(f"{third}{fourth}")
                    two_digits.add(f"{fourth}{third}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 03 đề 2 số: {str(e)}")
            return {'two_digits_special': []}
        
from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class HoangBach04Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 03 Đề 2 số
    Dự đoán từ tổng giải 2.1.5 + 3.2.1 + 3.5.2 và tổng giải 4.1.4 + 5.3.2 + 5.5.2,
    tổng giải 2.2.3 + 2.2.4 + 2.2.5 và tổng giải 3.6.2 + 3.6.3 + 3.6.4
    """
    def get_code(self) -> str:
        return "hoang_bach_04"
    
    def get_name(self) -> str:
        return "Hoang Bach 04 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ tổng giải 2.1.5 + 3.2.1 + 3.5.2 và tổng giải 4.1.4 + 5.3.2 + 5.5.2, " \
               "tổng giải 2.2.3 + 2.2.4 + 2.2.5 và tổng giải 3.6.2 + 3.6.3 + 3.6.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_db = data.get('giai_db', '')    # Giải đặc biệt, 5 chữ số
        giai_1 = data.get('giai_1', '')      # Giải 1, 5 chữ số
        giai_2_1 = data.get('giai_2_1', '')  # Giải 2.1, 5 chữ số
        giai_2_2 = data.get('giai_2_2', '')  # Giải 2.2, 5 chữ số
        giai_3_2 = data.get('giai_3_2', '')  # Giải 3.2, 5 chữ số
        giai_3_5 = data.get('giai_3_5', '')  # Giải 3.5, 5 chữ số
        giai_3_6 = data.get('giai_3_6', '')  # Giải 3.6, 5 chữ số
        giai_4_1 = data.get('giai_4_1', '')  # Giải 4.1, 4 chữ số
        giai_5_3 = data.get('giai_5_3', '')  # Giải 5.3, 4 chữ số
        giai_5_5 = data.get('giai_5_5', '')  # Giải 5.5, 4 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_db) == 5 and len(giai_1) == 5 and 
                len(giai_2_1) == 5 and len(giai_2_2) == 5 and 
                len(giai_3_2) == 5 and len(giai_3_5) == 5 and len(giai_3_6) == 5 and 
                len(giai_4_1) == 4 and len(giai_5_3) == 4 and len(giai_5_5) == 4):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_db={giai_db}, giai_1={giai_1}, giai_2_1={giai_2_1}, giai_2_2={giai_2_2}, "
                          f"giai_3_2={giai_3_2}, giai_3_5={giai_3_5}, giai_3_6={giai_3_6}, "
                          f"giai_4_1={giai_4_1}, giai_5_3={giai_5_3}, giai_5_5={giai_5_5}")
            return {'two_digits_special': []}
        
        try:
            # Tính số thứ nhất: tổng giải 2.1.5 + 3.2.1 + 3.5.2
            sum_first = (int(giai_2_1[4]) + int(giai_3_2[0]) + int(giai_3_5[1])) % 10
            first_nums = [str(sum_first), str(get_ball_number(sum_first))]
            
            # Tính số thứ hai: tổng giải 4.1.4 + 5.3.2 + 5.5.2
            sum_second = (int(giai_4_1[3]) + int(giai_5_3[1]) + int(giai_5_5[1])) % 10
            second_nums = [str(sum_second), str(get_ball_number(sum_second))]
            
            # Tính số thứ ba: tổng giải 2.2.3 + 2.2.4 + 2.2.5
            sum_third = (int(giai_2_2[2]) + int(giai_2_2[3]) + int(giai_2_2[4])) % 10
            third_nums = [str(sum_third), str(get_ball_number(sum_third))]
            
            # Tính số thứ tư: tổng giải 3.6.2 + 3.6.3 + 3.6.4
            sum_fourth = (int(giai_3_6[1]) + int(giai_3_6[2]) + int(giai_3_6[3])) % 10
            fourth_nums = [str(sum_fourth), str(get_ball_number(sum_fourth))]
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số từ số thứ 1 và số thứ 2
            for first in first_nums:
                for second in second_nums:
                    two_digits.add(f"{first}{second}")
                    two_digits.add(f"{second}{first}")
            # Cặp số từ số thứ 3 và số thứ 4
            for third in third_nums:
                for fourth in fourth_nums:
                    two_digits.add(f"{third}{fourth}")
                    two_digits.add(f"{fourth}{third}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 03 đề 2 số: {str(e)}")
            return {'two_digits_special': []}
        
from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class HoangBach05Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 05 Đề 2 số
    Dự đoán từ tổng giải 2.2.5 + 3.1.3 + 7.1.2 và tổng giải 2.1.1 + 3.2.2 + 5.2.2
    """
    def get_code(self) -> str:
        return "hoang_bach_05"
    
    def get_name(self) -> str:
        return "Hoang Bach 05 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ tổng giải 2.2.5 + 3.1.3 + 7.1.2 và tổng giải 2.1.1 + 3.2.2 + 5.2.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_db = data.get('giai_db', '')    # Giải đặc biệt, 5 chữ số
        giai_1 = data.get('giai_1', '')      # Giải 1, 5 chữ số
        giai_2_1 = data.get('giai_2_1', '')  # Giải 2.1, 5 chữ số
        giai_2_2 = data.get('giai_2_2', '')  # Giải 2.2, 5 chữ số
        giai_3_1 = data.get('giai_3_1', '')  # Giải 3.1, 5 chữ số
        giai_3_2 = data.get('giai_3_2', '')  # Giải 3.2, 5 chữ số
        giai_5_2 = data.get('giai_5_2', '')  # Giải 5.2, 4 chữ số
        giai_7_1 = data.get('giai_7_1', '')  # Giải 7.1, 2 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_db) == 5 and len(giai_1) == 5 and 
                len(giai_2_1) == 5 and len(giai_2_2) == 5 and 
                len(giai_3_1) == 5 and len(giai_3_2) == 5 and 
                len(giai_5_2) == 4 and len(giai_7_1) == 2):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_db={giai_db}, giai_1={giai_1}, giai_2_1={giai_2_1}, giai_2_2={giai_2_2}, "
                          f"giai_3_1={giai_3_1}, giai_3_2={giai_3_2}, giai_5_2={giai_5_2}, giai_7_1={giai_7_1}")
            return {'two_digits_special': []}
        
        try:
            # Tính số thứ nhất: tổng giải 2.2.5 + 3.1.3 + 7.1.2
            sum_first = (int(giai_2_2[4]) + int(giai_3_1[2]) + int(giai_7_1[1])) % 10
            first_nums = [str(sum_first), str(get_ball_number(sum_first))]
            
            # Tính số thứ hai: tổng giải 2.1.1 + 3.2.2 + 5.2.2
            sum_second = (int(giai_2_1[0]) + int(giai_3_2[1]) + int(giai_5_2[1])) % 10
            second_nums = [str(sum_second), str(get_ball_number(sum_second))]
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            for first in first_nums:
                for second in second_nums:
                    two_digits.add(f"{first}{second}")
                    two_digits.add(f"{second}{first}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 05 đề 2 số: {str(e)}")
            return {'two_digits_special': []}
        
from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class HoangBach06Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 06 Đề 2 số với Chạm và Tổng
    Dự đoán từ chạm 1 (tổng giải 3.2.1 + 3.6.3 + 7.1.1) và tổng 1 (tổng giải 3.1.1 + 3.1.2 + 3.1.3),
    chạm 2 (tổng giải 1.1.2 + 2.1.4 + 5.6.3) và tổng 2 (tổng giải 4.1.2 + 4.1.3 + 4.1.4)
    """
    def get_code(self) -> str:
        return "hoang_bach_06"
    
    def get_name(self) -> str:
        return "Hoang Bach 06 Đề 2 số với Chạm và Tổng"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ chạm 1 (tổng giải 3.2.1 + 3.6.3 + 7.1.1) và tổng 1 (tổng giải 3.1.1 + 3.1.2 + 3.1.3), " \
               "chạm 2 (tổng giải 1.1.2 + 2.1.4 + 5.6.3) và tổng 2 (tổng giải 4.1.2 + 4.1.3 + 4.1.4)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_db = data.get('giai_db', '')    # Giải đặc biệt, 5 chữ số
        giai_1 = data.get('giai_1', '')      # Giải 1, 5 chữ số
        giai_2_1 = data.get('giai_2_1', '')  # Giải 2.1, 5 chữ số
        giai_3_1 = data.get('giai_3_1', '')  # Giải 3.1, 5 chữ số
        giai_3_2 = data.get('giai_3_2', '')  # Giải 3.2, 5 chữ số
        giai_3_6 = data.get('giai_3_6', '')  # Giải 3.6, 5 chữ số
        giai_4_1 = data.get('giai_4_1', '')  # Giải 4.1, 4 chữ số
        giai_5_6 = data.get('giai_5_6', '')  # Giải 5.6, 4 chữ số
        giai_7_1 = data.get('giai_7_1', '')  # Giải 7.1, 2 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_db) == 5 and len(giai_1) == 5 and len(giai_2_1) == 5 and 
                len(giai_3_1) == 5 and len(giai_3_2) == 5 and len(giai_3_6) == 5 and 
                len(giai_4_1) == 4 and len(giai_5_6) == 4 and len(giai_7_1) == 2):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_db={giai_db}, giai_1={giai_1}, giai_2_1={giai_2_1}, "
                          f"giai_3_1={giai_3_1}, giai_3_2={giai_3_2}, giai_3_6={giai_3_6}, "
                          f"giai_4_1={giai_4_1}, giai_5_6={giai_5_6}, giai_7_1={giai_7_1}")
            return {'two_digits_special': []}
        
        try:
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
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu")
                return {'two_digits_special': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 06 đề 2 số với chạm và tổng: {str(e)}")
            return {'two_digits_special': []}
        
from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class HoangBach01Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 01 Đề 2 số
    Dự đoán từ bóng của tổng giải 1.1.2 + 3.6.4 + 4.4.2 và bóng của tổng giải 2.1.3 + 4.1.1 + 4.3.4
    """
    def get_code(self) -> str:
        return "hoang_bach_01"
    
    def get_name(self) -> str:
        return "Hoang Bach 01 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ bóng của tổng giải 1.1.2 + 3.6.4 + 4.4.2 và bóng của tổng giải 2.1.3 + 4.1.1 + 4.3.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_1 = data.get('giai_1', '')  # Giải 1, 5 chữ số
        giai_3_6 = data.get('giai_3_6', '')  # Giải 3.6, 5 chữ số
        giai_4_4 = data.get('giai_4_4', '')  # Giải 4.4, 4 chữ số
        giai_2_1 = data.get('giai_2_1', '')  # Giải 2.1, 5 chữ số
        giai_4_1 = data.get('giai_4_1', '')  # Giải 4.1, 4 chữ số
        giai_4_3 = data.get('giai_4_3', '')  # Giải 4.3, 4 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_1) == 5 and len(giai_3_6) == 5 and len(giai_4_4) == 4 and 
                len(giai_2_1) == 5 and len(giai_4_1) == 4 and len(giai_4_3) == 4):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_1={giai_1}, giai_3_6={giai_3_6}, giai_4_4={giai_4_4}, "
                          f"giai_2_1={giai_2_1}, giai_4_1={giai_4_1}, giai_4_3={giai_4_3}")
            return {'two_digits_special': []}
        
        try:
            # Tính số thứ nhất: bóng của tổng giải 1.1.2 + 3.6.4 + 4.4.2
            sum_first = (int(giai_1[1]) + int(giai_3_6[3]) + int(giai_4_4[1])) % 10
            first_nums = [str(sum_first), str(get_ball_number(int(sum_first)))]
            # Tính số thứ hai: bóng của tổng giải 2.1.3 + 4.1.1 + 4.3.4
            sum_second = (int(giai_2_1[2]) + int(giai_4_1[0]) + int(giai_4_3[3])) % 10
            second_nums = [str(sum_second), str(get_ball_number(sum_second))]
            
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = set()
            for first in first_nums:
                for second in second_nums:
                    # Thêm cặp số thẳng
                    two_digits.add(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.add(f"{second}{first}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 01 đề 2 số: {str(e)}")
            return {'two_digits_special': []}
        
class HoangBach02Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 02 Đề 2 số
    Dự đoán từ bóng của tổng giải 3.1.2 + 3.3.5 + 3.5.4 và bóng của tổng giải 3.4.1 + 4.3.4 + 7.4.2
    """
    def get_code(self) -> str:
        return "hoang_bach_02"
    
    def get_name(self) -> str:
        return "Hoang Bach 02 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ bóng của tổng giải 3.1.2 + 3.3.5 + 3.5.4 và bóng của tổng giải 3.4.1 + 4.3.4 + 7.4.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_db = data.get('giai_db', '')    # Giải đặc biệt, 5 chữ số
        giai_1 = data.get('giai_1', '')      # Giải 1, 5 chữ số
        giai_3_1 = data.get('giai_3_1', '')  # Giải 3.1, 5 chữ số
        giai_3_3 = data.get('giai_3_3', '')  # Giải 3.3, 5 chữ số
        giai_3_5 = data.get('giai_3_5', '')  # Giải 3.5, 5 chữ số
        giai_3_4 = data.get('giai_3_4', '')  # Giải 3.4, 5 chữ số
        giai_4_3 = data.get('giai_4_3', '')  # Giải 4.3, 4 chữ số
        giai_7_4 = data.get('giai_7_4', '')  # Giải 7.4, 2 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_db) == 5 and len(giai_1) == 5 and 
                len(giai_3_1) == 5 and len(giai_3_3) == 5 and len(giai_3_5) == 5 and len(giai_3_4) == 5 and 
                len(giai_4_3) == 4 and len(giai_7_4) == 2):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_db={giai_db}, giai_1={giai_1}, giai_3_1={giai_3_1}, giai_3_3={giai_3_3}, "
                          f"giai_3_5={giai_3_5}, giai_3_4={giai_3_4}, giai_4_3={giai_4_3}, giai_7_4={giai_7_4}")
            return {'two_digits_special': []}
        
        try:
            # Tính số thứ nhất: bóng của tổng giải 3.1.2 + 3.3.5 + 3.5.4
            sum_first = (int(giai_3_1[1]) + int(giai_3_3[4]) + int(giai_3_5[3])) % 10
            first_nums = [str(sum_first), str(get_ball_number(sum_first))]
            
            # Tính số thứ hai: bóng của tổng giải 3.4.1 + 4.3.4 + 7.4.2
            sum_second = (int(giai_3_4[0]) + int(giai_4_3[3]) + int(giai_7_4[1])) % 10
            second_nums = [str(sum_second), str(get_ball_number(sum_second))]
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            for first in first_nums:
                for second in second_nums:
                    two_digits.add(f"{first}{second}")
                    two_digits.add(f"{second}{first}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 02 đề 2 số: {str(e)}")
            return {'two_digits_special': []}
        
from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class HoangBach03Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 03 Đề 2 số
    Dự đoán từ tổng giải 2.1.5 + 3.2.1 + 3.5.2 và tổng giải 4.1.4 + 5.3.2 + 5.5.2,
    tổng giải 2.2.3 + 2.2.4 + 2.2.5 và tổng giải 3.6.2 + 3.6.3 + 3.6.4
    """
    def get_code(self) -> str:
        return "hoang_bach_03"
    
    def get_name(self) -> str:
        return "Hoang Bach 03 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ tổng giải 2.1.5 + 3.2.1 + 3.5.2 và tổng giải 4.1.4 + 5.3.2 + 5.5.2, " \
               "tổng giải 2.2.3 + 2.2.4 + 2.2.5 và tổng giải 3.6.2 + 3.6.3 + 3.6.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_db = data.get('giai_db', '')    # Giải đặc biệt, 5 chữ số
        giai_1 = data.get('giai_1', '')      # Giải 1, 5 chữ số
        giai_2_1 = data.get('giai_2_1', '')  # Giải 2.1, 5 chữ số
        giai_2_2 = data.get('giai_2_2', '')  # Giải 2.2, 5 chữ số
        giai_3_2 = data.get('giai_3_2', '')  # Giải 3.2, 5 chữ số
        giai_3_5 = data.get('giai_3_5', '')  # Giải 3.5, 5 chữ số
        giai_3_6 = data.get('giai_3_6', '')  # Giải 3.6, 5 chữ số
        giai_4_1 = data.get('giai_4_1', '')  # Giải 4.1, 4 chữ số
        giai_5_3 = data.get('giai_5_3', '')  # Giải 5.3, 4 chữ số
        giai_5_5 = data.get('giai_5_5', '')  # Giải 5.5, 4 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_db) == 5 and len(giai_1) == 5 and 
                len(giai_2_1) == 5 and len(giai_2_2) == 5 and 
                len(giai_3_2) == 5 and len(giai_3_5) == 5 and len(giai_3_6) == 5 and 
                len(giai_4_1) == 4 and len(giai_5_3) == 4 and len(giai_5_5) == 4):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_db={giai_db}, giai_1={giai_1}, giai_2_1={giai_2_1}, giai_2_2={giai_2_2}, "
                          f"giai_3_2={giai_3_2}, giai_3_5={giai_3_5}, giai_3_6={giai_3_6}, "
                          f"giai_4_1={giai_4_1}, giai_5_3={giai_5_3}, giai_5_5={giai_5_5}")
            return {'two_digits_special': []}
        
        try:
            # Tính số thứ nhất: tổng giải 2.1.5 + 3.2.1 + 3.5.2
            sum_first = (int(giai_2_1[4]) + int(giai_3_2[0]) + int(giai_3_5[1])) % 10
            first_nums = [str(sum_first), str(get_ball_number(sum_first))]
            
            # Tính số thứ hai: tổng giải 4.1.4 + 5.3.2 + 5.5.2
            sum_second = (int(giai_4_1[3]) + int(giai_5_3[1]) + int(giai_5_5[1])) % 10
            second_nums = [str(sum_second), str(get_ball_number(sum_second))]
            
            # Tính số thứ ba: tổng giải 2.2.3 + 2.2.4 + 2.2.5
            sum_third = (int(giai_2_2[2]) + int(giai_2_2[3]) + int(giai_2_2[4])) % 10
            third_nums = [str(sum_third), str(get_ball_number(sum_third))]
            
            # Tính số thứ tư: tổng giải 3.6.2 + 3.6.3 + 3.6.4
            sum_fourth = (int(giai_3_6[1]) + int(giai_3_6[2]) + int(giai_3_6[3])) % 10
            fourth_nums = [str(sum_fourth), str(get_ball_number(sum_fourth))]
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số từ số thứ 1 và số thứ 2
            for first in first_nums:
                for second in second_nums:
                    two_digits.add(f"{first}{second}")
                    two_digits.add(f"{second}{first}")
            # Cặp số từ số thứ 3 và số thứ 4
            for third in third_nums:
                for fourth in fourth_nums:
                    two_digits.add(f"{third}{fourth}")
                    two_digits.add(f"{fourth}{third}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 03 đề 2 số: {str(e)}")
            return {'two_digits_special': []}
        
from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class HoangBach04Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 03 Đề 2 số
    Dự đoán từ tổng giải 2.1.5 + 3.2.1 + 3.5.2 và tổng giải 4.1.4 + 5.3.2 + 5.5.2,
    tổng giải 2.2.3 + 2.2.4 + 2.2.5 và tổng giải 3.6.2 + 3.6.3 + 3.6.4
    """
    def get_code(self) -> str:
        return "hoang_bach_04"
    
    def get_name(self) -> str:
        return "Hoang Bach 04 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ tổng giải 2.1.5 + 3.2.1 + 3.5.2 và tổng giải 4.1.4 + 5.3.2 + 5.5.2, " \
               "tổng giải 2.2.3 + 2.2.4 + 2.2.5 và tổng giải 3.6.2 + 3.6.3 + 3.6.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_db = data.get('giai_db', '')    # Giải đặc biệt, 5 chữ số
        giai_1 = data.get('giai_1', '')      # Giải 1, 5 chữ số
        giai_2_1 = data.get('giai_2_1', '')  # Giải 2.1, 5 chữ số
        giai_2_2 = data.get('giai_2_2', '')  # Giải 2.2, 5 chữ số
        giai_3_2 = data.get('giai_3_2', '')  # Giải 3.2, 5 chữ số
        giai_3_5 = data.get('giai_3_5', '')  # Giải 3.5, 5 chữ số
        giai_3_6 = data.get('giai_3_6', '')  # Giải 3.6, 5 chữ số
        giai_4_1 = data.get('giai_4_1', '')  # Giải 4.1, 4 chữ số
        giai_5_3 = data.get('giai_5_3', '')  # Giải 5.3, 4 chữ số
        giai_5_5 = data.get('giai_5_5', '')  # Giải 5.5, 4 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_db) == 5 and len(giai_1) == 5 and 
                len(giai_2_1) == 5 and len(giai_2_2) == 5 and 
                len(giai_3_2) == 5 and len(giai_3_5) == 5 and len(giai_3_6) == 5 and 
                len(giai_4_1) == 4 and len(giai_5_3) == 4 and len(giai_5_5) == 4):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_db={giai_db}, giai_1={giai_1}, giai_2_1={giai_2_1}, giai_2_2={giai_2_2}, "
                          f"giai_3_2={giai_3_2}, giai_3_5={giai_3_5}, giai_3_6={giai_3_6}, "
                          f"giai_4_1={giai_4_1}, giai_5_3={giai_5_3}, giai_5_5={giai_5_5}")
            return {'two_digits_special': []}
        
        try:
            # Tính số thứ nhất: tổng giải 2.1.5 + 3.2.1 + 3.5.2
            sum_first = (int(giai_2_1[4]) + int(giai_3_2[0]) + int(giai_3_5[1])) % 10
            first_nums = [str(sum_first), str(get_ball_number(sum_first))]
            
            # Tính số thứ hai: tổng giải 4.1.4 + 5.3.2 + 5.5.2
            sum_second = (int(giai_4_1[3]) + int(giai_5_3[1]) + int(giai_5_5[1])) % 10
            second_nums = [str(sum_second), str(get_ball_number(sum_second))]
            
            # Tính số thứ ba: tổng giải 2.2.3 + 2.2.4 + 2.2.5
            sum_third = (int(giai_2_2[2]) + int(giai_2_2[3]) + int(giai_2_2[4])) % 10
            third_nums = [str(sum_third), str(get_ball_number(sum_third))]
            
            # Tính số thứ tư: tổng giải 3.6.2 + 3.6.3 + 3.6.4
            sum_fourth = (int(giai_3_6[1]) + int(giai_3_6[2]) + int(giai_3_6[3])) % 10
            fourth_nums = [str(sum_fourth), str(get_ball_number(sum_fourth))]
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số từ số thứ 1 và số thứ 2
            for first in first_nums:
                for second in second_nums:
                    two_digits.add(f"{first}{second}")
                    two_digits.add(f"{second}{first}")
            # Cặp số từ số thứ 3 và số thứ 4
            for third in third_nums:
                for fourth in fourth_nums:
                    two_digits.add(f"{third}{fourth}")
                    two_digits.add(f"{fourth}{third}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 03 đề 2 số: {str(e)}")
            return {'two_digits_special': []}
        
from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class HoangBach05Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 05 Đề 2 số
    Dự đoán từ tổng giải 2.2.5 + 3.1.3 + 7.1.2 và tổng giải 2.1.1 + 3.2.2 + 5.2.2
    """
    def get_code(self) -> str:
        return "hoang_bach_05"
    
    def get_name(self) -> str:
        return "Hoang Bach 05 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ tổng giải 2.2.5 + 3.1.3 + 7.1.2 và tổng giải 2.1.1 + 3.2.2 + 5.2.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_db = data.get('giai_db', '')    # Giải đặc biệt, 5 chữ số
        giai_1 = data.get('giai_1', '')      # Giải 1, 5 chữ số
        giai_2_1 = data.get('giai_2_1', '')  # Giải 2.1, 5 chữ số
        giai_2_2 = data.get('giai_2_2', '')  # Giải 2.2, 5 chữ số
        giai_3_1 = data.get('giai_3_1', '')  # Giải 3.1, 5 chữ số
        giai_3_2 = data.get('giai_3_2', '')  # Giải 3.2, 5 chữ số
        giai_5_2 = data.get('giai_5_2', '')  # Giải 5.2, 4 chữ số
        giai_7_1 = data.get('giai_7_1', '')  # Giải 7.1, 2 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_db) == 5 and len(giai_1) == 5 and 
                len(giai_2_1) == 5 and len(giai_2_2) == 5 and 
                len(giai_3_1) == 5 and len(giai_3_2) == 5 and 
                len(giai_5_2) == 4 and len(giai_7_1) == 2):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_db={giai_db}, giai_1={giai_1}, giai_2_1={giai_2_1}, giai_2_2={giai_2_2}, "
                          f"giai_3_1={giai_3_1}, giai_3_2={giai_3_2}, giai_5_2={giai_5_2}, giai_7_1={giai_7_1}")
            return {'two_digits_special': []}
        
        try:
            # Tính số thứ nhất: tổng giải 2.2.5 + 3.1.3 + 7.1.2
            sum_first = (int(giai_2_2[4]) + int(giai_3_1[2]) + int(giai_7_1[1])) % 10
            first_nums = [str(sum_first), str(get_ball_number(sum_first))]
            
            # Tính số thứ hai: tổng giải 2.1.1 + 3.2.2 + 5.2.2
            sum_second = (int(giai_2_1[0]) + int(giai_3_2[1]) + int(giai_5_2[1])) % 10
            second_nums = [str(sum_second), str(get_ball_number(sum_second))]
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            for first in first_nums:
                for second in second_nums:
                    two_digits.add(f"{first}{second}")
                    two_digits.add(f"{second}{first}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 05 đề 2 số: {str(e)}")
            return {'two_digits_special': []}
        
from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class HoangBach06Method(BasePredictionMethod):
    """
    Phương pháp Hoang Bach 06 Đề 2 số với Chạm và Tổng
    Dự đoán từ chạm 1 (tổng giải 3.2.1 + 3.6.3 + 7.1.1) và tổng 1 (tổng giải 3.1.1 + 3.1.2 + 3.1.3),
    chạm 2 (tổng giải 1.1.2 + 2.1.4 + 5.6.3) và tổng 2 (tổng giải 4.1.2 + 4.1.3 + 4.1.4)
    """
    def get_code(self) -> str:
        return "hoang_bach_06"
    
    def get_name(self) -> str:
        return "Hoang Bach 06 Đề 2 số với Chạm và Tổng"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ chạm 1 (tổng giải 3.2.1 + 3.6.3 + 7.1.1) và tổng 1 (tổng giải 3.1.1 + 3.1.2 + 3.1.3), " \
               "chạm 2 (tổng giải 1.1.2 + 2.1.4 + 5.6.3) và tổng 2 (tổng giải 4.1.2 + 4.1.3 + 4.1.4)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải cần thiết
        giai_db = data.get('giai_db', '')    # Giải đặc biệt, 5 chữ số
        giai_1 = data.get('giai_1', '')      # Giải 1, 5 chữ số
        giai_2_1 = data.get('giai_2_1', '')  # Giải 2.1, 5 chữ số
        giai_3_1 = data.get('giai_3_1', '')  # Giải 3.1, 5 chữ số
        giai_3_2 = data.get('giai_3_2', '')  # Giải 3.2, 5 chữ số
        giai_3_6 = data.get('giai_3_6', '')  # Giải 3.6, 5 chữ số
        giai_4_1 = data.get('giai_4_1', '')  # Giải 4.1, 4 chữ số
        giai_5_6 = data.get('giai_5_6', '')  # Giải 5.6, 4 chữ số
        giai_7_1 = data.get('giai_7_1', '')  # Giải 7.1, 2 chữ số
        
        # Kiểm tra độ dài dữ liệu đầu vào
        if not (len(giai_db) == 5 and len(giai_1) == 5 and len(giai_2_1) == 5 and 
                len(giai_3_1) == 5 and len(giai_3_2) == 5 and len(giai_3_6) == 5 and 
                len(giai_4_1) == 4 and len(giai_5_6) == 4 and len(giai_7_1) == 2):
            logger.warning(f"[{self.get_code()}] Dữ liệu đầu vào không hợp lệ: "
                          f"giai_db={giai_db}, giai_1={giai_1}, giai_2_1={giai_2_1}, "
                          f"giai_3_1={giai_3_1}, giai_3_2={giai_3_2}, giai_3_6={giai_3_6}, "
                          f"giai_4_1={giai_4_1}, giai_5_6={giai_5_6}, giai_7_1={giai_7_1}")
            return {'two_digits_special': []}
        
        try:
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
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu")
                return {'two_digits_special': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính Hoang Bach 06 đề 2 số với chạm và tổng: {str(e)}")
            return {'two_digits_special': []}