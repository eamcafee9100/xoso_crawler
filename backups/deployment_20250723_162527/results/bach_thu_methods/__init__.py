# bach_thu_methods/__init__.py
from typing import List
from .base import BaseBachThuMethod
from .gap_method import GapMethod
from .dau_duoi_method import DauDuoiMethod
from .gan_method import GanMethod

def get_all_bach_thu_methods() -> List[BaseBachThuMethod]:
    """
    Trả về danh sách tất cả các phương pháp dự đoán bạch thủ lô đã đăng ký
    """
    methods = [
        GapMethod(),
        DauDuoiMethod(), 
        GanMethod(),
    ]
    return methods

def get_method_by_code(code: str) -> BaseBachThuMethod:
    """
    Lấy phương pháp theo mã code
    
    Args:
        code: Mã định danh của phương pháp
        
    Returns:
        Instance của phương pháp tương ứng
        
    Raises:
        ValueError: Nếu không tìm thấy phương pháp
    """
    methods = get_all_bach_thu_methods()
    for method in methods:
        if method.get_code() == code:
            return method
    
    raise ValueError(f"Method with code '{code}' not found")

def get_active_methods() -> List[BaseBachThuMethod]:
    """
    Trả về danh sách các phương pháp đang hoạt động
    """
    methods = get_all_bach_thu_methods()
    active_methods = []
    
    for method in methods:
        if hasattr(method, 'bach_thu_method') and method.bach_thu_method.is_active:
            active_methods.append(method)
    
    return active_methods