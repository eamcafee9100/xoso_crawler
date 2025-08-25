from typing import List
from .base import BasePredictionMethod  
from .main_method import MainDanDeMethod, MainDande3DigitMethod
from .ttd_method import TuThuDeMethod
# from .pascal_method import PascalMethod
from .hoang_bach_01 import HoangBach01Method, HoangBach02Method, HoangBach03Method, HoangBach04Method, HoangBach05Method, HoangBach06Method

from .de_24_method import De24TwoDigitMethod, De24ThreeDigitMethod
from .de_25_method import De25TwoDigitMethod, De25ThreeDigitMethod
from .de_26_method import De26TwoDigitMethod, De26ThreeDigitMethod
from .de_52_method import De52TwoDigitMethod, De52ThreeDigitMethod
from .de_58_method import De58TwoDigitMethod, De58ThreeDigitMethod
from .de_59_method import De59TwoDigitMethod, De59ThreeDigitMethod
from .de_63_method import De63TwoDigitMethod, De63ThreeDigitMethod
from .de_77_method import De77TwoDigitMethod, De77ThreeDigitMethod
from .de_78_method import De78TwoDigitMethod, De78ThreeDigitMethod
from .de_79_method import De79TwoDigitMethod, De79ThreeDigitMethod
from .de_80_method import De80TwoDigitMethod, De80ThreeDigitMethod
from .de_81_method import De81TwoDigitMethod, De81ThreeDigitMethod
from .de_88_method import De88TwoDigitMethod, De88ThreeDigitMethod
from .de_92_method import De92TwoDigitMethod, De92ThreeDigitMethod
from .de_93_method import De93TwoDigitMethod, De93ThreeDigitMethod
from .de_101_method import De101TwoDigitMethod, De101ThreeDigitMethod
from .de_105_method import De105TwoDigitMethod, De105ThreeDigitMethod
from .de_106_method import De106TwoDigitMethod, De106ThreeDigitMethod
from .de_107_method import De107TwoDigitMethod, De107ThreeDigitMethod  
from .de_108_method import De108TwoDigitMethod, De108ThreeDigitMethod
from .de_109_method import De109TwoDigitMethod, De109ThreeDigitMethod
from .de_110_method import De110TwoDigitMethod, De110ThreeDigitMethod
from .de_112_method import De112TwoDigitMethod, De112ThreeDigitMethod
from .de_113_method import De113TwoDigitMethod, De113ThreeDigitMethod
from .de_115_method import De115TwoDigitMethod, De115ThreeDigitMethod
from .de_116_method import De116TwoDigitMethod, De116ThreeDigitMethod
from .de_117_method import De117TwoDigitMethod, De117ThreeDigitMethod
from .de_118_method import De118TwoDigitMethod, De118ThreeDigitMethod
from .de_119_method import De119TwoDigitMethod, De119ThreeDigitMethod
from .de_120_method import De120TwoDigitMethod, De120ThreeDigitMethod
from .de_121_method import De121TwoDigitMethod, De121ThreeDigitMethod
from .de_122_method import De122TwoDigitMethod, De122ThreeDigitMethod
from .de_123_method import De123TwoDigitMethod, De123ThreeDigitMethod
from .de_124_method import De124TwoDigitMethod, De124ThreeDigitMethod
from .de_125_method import De125TwoDigitMethod, De125ThreeDigitMethod
from .de_126_method import De126TwoDigitMethod, De126ThreeDigitMethod
from .de_127_method import De127TwoDigitMethod, De127ThreeDigitMethod
from .de_128_method import De128TwoDigitMethod, De128ThreeDigitMethod
from .de_129_method import De129TwoDigitMethod, De129ThreeDigitMethod
from .de_130_method import De130TwoDigitMethod, De130ThreeDigitMethod
from .de_131_method import De131TwoDigitMethod, De131ThreeDigitMethod
from .de_132_method import De132TwoDigitMethod, De132ThreeDigitMethod
from .de_133_method import De133TwoDigitMethod, De133ThreeDigitMethod
from .de_134_method import De134TwoDigitMethod, De134ThreeDigitMethod
from .de_135_method import De135TwoDigitMethod, De135ThreeDigitMethod
from .de_136_method import De136TwoDigitMethod, De136ThreeDigitMethod

 

def get_all_methods() -> List[BasePredictionMethod]:
    """
    Trả về danh sách tất cả các phương pháp dự đoán đã đăng ký
    """
    methods = [
        HoangBach01Method(), HoangBach02Method(), HoangBach03Method(),
        HoangBach04Method(), HoangBach05Method(), HoangBach06Method(),
        MainDanDeMethod(), MainDande3DigitMethod(), TuThuDeMethod(),
        De24TwoDigitMethod(), De24ThreeDigitMethod(),
        De25TwoDigitMethod(), De25ThreeDigitMethod(),
        De26TwoDigitMethod(), De26ThreeDigitMethod(),
        De52TwoDigitMethod(), De52ThreeDigitMethod(),
        De58TwoDigitMethod(), De58ThreeDigitMethod(), 
        De59TwoDigitMethod(), De59ThreeDigitMethod(), 
        De63TwoDigitMethod(), De63ThreeDigitMethod(),
        De77TwoDigitMethod(), De77ThreeDigitMethod(),
        De78TwoDigitMethod(), De78ThreeDigitMethod(),
        De79TwoDigitMethod(), De79ThreeDigitMethod(),
        De80TwoDigitMethod(), De80ThreeDigitMethod(),
        De81TwoDigitMethod(), De81ThreeDigitMethod(),
        De88TwoDigitMethod(), De88ThreeDigitMethod(),
        De92TwoDigitMethod(), De92ThreeDigitMethod(),
        De93TwoDigitMethod(), De93ThreeDigitMethod(),
        De101TwoDigitMethod(), De101ThreeDigitMethod(),
        De105TwoDigitMethod(), De105ThreeDigitMethod(),
        De106TwoDigitMethod(), De106ThreeDigitMethod(),
        De107TwoDigitMethod(), De107ThreeDigitMethod(),
        De108TwoDigitMethod(), De108ThreeDigitMethod(),
        De109TwoDigitMethod(), De109ThreeDigitMethod(),
        De110TwoDigitMethod(), De110ThreeDigitMethod(), 
        De112TwoDigitMethod(), De112ThreeDigitMethod(),
        De113TwoDigitMethod(), De113ThreeDigitMethod(),
        De115TwoDigitMethod(), De115ThreeDigitMethod(),
        De116TwoDigitMethod(), De116ThreeDigitMethod(),
        De117TwoDigitMethod(), De117ThreeDigitMethod(),
        De118TwoDigitMethod(), De118ThreeDigitMethod(),  # Bỏ comment khi đã tạo
        De119TwoDigitMethod(), De119ThreeDigitMethod(),
        De120TwoDigitMethod(), De120ThreeDigitMethod(),
        De121TwoDigitMethod(), De121ThreeDigitMethod(),
        De122TwoDigitMethod(), De122ThreeDigitMethod(),  # Bỏ comment khi đã tạo
        De123TwoDigitMethod(), De123ThreeDigitMethod(),
        De124TwoDigitMethod(), De124ThreeDigitMethod(),
        De125TwoDigitMethod(), De125ThreeDigitMethod(),
        De126TwoDigitMethod(), De126ThreeDigitMethod(),
        De127TwoDigitMethod(), De127ThreeDigitMethod(),
        De128TwoDigitMethod(), De128ThreeDigitMethod(),  # Bỏ comment khi đã tạo
        De129TwoDigitMethod(), De129ThreeDigitMethod(),
        De130TwoDigitMethod(), De130ThreeDigitMethod(),
        De131TwoDigitMethod(), De131ThreeDigitMethod(),
        De132TwoDigitMethod(), De132ThreeDigitMethod(),
        De133TwoDigitMethod(), De133ThreeDigitMethod(),  # Bỏ comment khi đã tạo
        De134TwoDigitMethod(), De134ThreeDigitMethod(),
        De135TwoDigitMethod(), De135ThreeDigitMethod(),
        De136TwoDigitMethod(), De136ThreeDigitMethod(),
        # Thêm các phương pháp khác vào đây nếu có nhi
        # Bỏ comment khi các phương pháp đã được tạo
        # MainDanDeMethod(),
        # TuThuDeMetho
        # PascalMethod(),
        # SpecialPrizeMethod(),
        # De105Method()
    ]
    return methods