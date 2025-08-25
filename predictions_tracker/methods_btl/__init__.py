# method/__init__.py
import pkgutil
import importlib
import inspect

from .base import BasePredictionMethod

# Danh sách lưu trữ các instance của các phương pháp
_all_methods = []

# Tên package hiện tại (phải trùng tên thư mục chứa __init__.py)
package_name = __name__

# Duyệt các module trong package (bỏ base và utils)
for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    if module_name.startswith("btl_") and module_name.endswith("_method"):
        full_module_name = f"{package_name}.{module_name}"
        try:
            # Import module
            module = importlib.import_module(full_module_name)

            # Tìm class kế thừa BasePredictionMethod
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, BasePredictionMethod) and cls is not BasePredictionMethod:
                    _all_methods.append(cls())  # Khởi tạo và thêm vào danh sách

        except Exception as e:
            print(f"❌ Lỗi khi import {full_module_name}: {e}")

def get_all_methods():
    """
    Trả về danh sách tất cả các phương pháp dự đoán đã được nạp
    """
    return _all_methods