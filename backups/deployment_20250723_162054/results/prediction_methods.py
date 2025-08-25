from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class PredictionMethod(ABC):
    """Lớp cơ sở cho tất cả phương pháp dự đoán"""
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    @abstractmethod
    def calculate(self, data: dict) -> list:
        pass
    
    @staticmethod
    def get_ball_number(number):
        ball_map = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}
        return ball_map.get(int(number), number)

# Triển khai cụ thể từng phương pháp
class MainNumberSetMethod(PredictionMethod):
    def __init__(self):
        super().__init__("Dàn đề chính", "Tạo bộ số từ giải 3 và giải 2")
    
    def calculate(self, data):
        # Logic từ generate_number_set
        pass

class PascalMethod(PredictionMethod):
    def __init__(self):
        super().__init__("Soi cầu Pascal", "Dự đoán từ giải đặc biệt và giải nhất")
    
    def calculate(self, data):
        # Logic từ calculate_pascal_method
        pass

class De105Method(PredictionMethod):
    def __init__(self):
        super().__init__("105 Đề 4 số", "Dự đoán từ giải 3.1, 4.1, 6.3, 3.6")
    
    def calculate(self, data):
        # Logic từ _105_de_4_so
        pass