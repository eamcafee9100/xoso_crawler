import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import shap
from collections import defaultdict
from .models import KetQuaXoSo
from django.utils import timezone   


class BaiToanBachThuLo:
    def __init__(self, target_date):
        self.target_date = target_date
        self.historical_data = self._load_data()
        self.methods = {
            'tong_dac_biet': self._method_tong_dac_biet,
            'lap_lai_gan_nhat': self._method_lap_lai_gan_nhat,
            'tan_so_xuat_hien': self._method_tan_so_xuat_hien,
            'bong_so': self._method_bong_so
        }
    
    def _load_data(self):
        # Load dữ liệu lịch sử 180 ngày
        return KetQuaXoSo.objects.filter(
            ngay__lt=self.target_date
        ).order_by('-ngay')[:180]
    
    def predict(self):
        results = []
        for method_name, method_func in self.methods.items():
            numbers, confidence = method_func()
            results.append({
                'method': method_name,
                'numbers': numbers,
                'confidence': confidence
            })
        
        # Kết hợp kết quả bằng voting
        final_predictions = self._combine_predictions(results)
        return {'methods': results, 'final': final_predictions}
    
    def analyze_with_shap(self):
        # Chuẩn bị dữ liệu cho SHAP
        X, y = self._prepare_shap_data()
        
        # Train model
        model = RandomForestClassifier()
        X_train, X_test, y_train, y_test = train_test_split(X, y)
        model.fit(X_train, y_train)
        
        # SHAP analysis
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        return explainer, shap_values
    
    def evaluate_methods(self):
        # Đánh giá hiệu quả các phương pháp trên lịch sử
        evaluation = {}
        for method_name in self.methods.keys():
            success_rate = self._calculate_success_rate(method_name)
            evaluation[method_name] = success_rate
        return evaluation
    
    # Các phương pháp dự đoán
    def _method_tong_dac_biet(self):
        # Logic tính tổng đặc biệt
        pass
    
    def _method_lap_lai_gan_nhat(self):
        # Logic tìm số lặp lại gần nhất
        pass
    
    # ... (các phương pháp khác)
    
    def _prepare_shap_data(self):
        # Chuẩn bị dữ liệu dạng bảng cho SHAP
        pass
    
    def _calculate_success_rate(self, method_name):
        # Tính tỷ lệ thành công của phương pháp trong quá khứ
        pass