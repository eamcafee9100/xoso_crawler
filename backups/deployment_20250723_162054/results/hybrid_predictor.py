# results/hybrid_predictor.py
from collections import defaultdict
from itertools import combinations
from django.db.models import Q
from .models import KetQuaXoSo, CycleAccuracy

from django.db.models import Avg
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import date, timedelta


class HybridPredictor:
    def __init__(self):
        self.cycle_weights = self.load_dynamic_weights()
        self.ml_model = None
        self.scaler = None
        self.hot_pairs = []
        self.model_path = os.path.join(os.path.dirname(__file__), 'ml_models/xs_model.pkl')
        self.scaler_path = os.path.join(os.path.dirname(__file__), 'ml_models/scaler.pkl')
        self.model_name = "HybridPredictor_v1"
        self.load_weights()

    def load_weights(self):
        """Tải trọng số từ database"""
        self.cycle_weights = {
            '1_ngay': 0.55,
            '3_ngay': 0.65,
            '7_ngay': 0.40,
            '14_ngay': 0.45,
            '30_ngay': 0.35
        }
        
        try:
            # Lấy độ chính xác trung bình
            avg_accuracy = CycleAccuracy.objects.aggregate(avg=Avg('accuracy'))['avg'] or 50
            
            # Điều chỉnh trọng số dựa trên độ chính xác tương đối
            for cycle in CycleAccuracy.objects.all():
                relative_accuracy = cycle.accuracy / avg_accuracy
                self.cycle_weights[cycle.cycle_type] *= relative_accuracy
            
            # Chuẩn hóa lại tổng trọng số = 1
            total = sum(self.cycle_weights.values())
            self.cycle_weights = {k: v/total for k, v in self.cycle_weights.items()}
            
        except Exception as e:
            print(f"Không tải được trọng số từ DB, sử dụng mặc định: {str(e)}")
               
    def load_dynamic_weights(self):
        """Tải trọng số từ database hoặc dùng mặc định"""
        try:
            weights = {}
            total_accuracy = 0
            for cycle in CycleAccuracy.objects.all():
                weights[cycle.cycle_type] = cycle.accuracy
                total_accuracy += cycle.accuracy
            
            # Chuẩn hóa trọng số nếu có dữ liệu
            if total_accuracy > 0:
                return {k: v/total_accuracy for k, v in weights.items()}
        except:
            pass
        
        # Trọng số mặc định nếu chưa có dữ liệu
        return {'1_ngay': 0.35, '3_ngay': 0.25, '7_ngay': 0.2, '14_ngay': 0.15, '30_ngay': 0.05}
    
    def analyze_cycles(self, history):
        """Phân tích đa chu kỳ cải tiến"""
        analysis = {}
        cycle_days = {'1_ngay': 1, '3_ngay': 3, '7_ngay': 7, '14_ngay': 14, '30_ngay': 30}
        
        for name, days in cycle_days.items():
            cycle_history = history[:days]
            freq = defaultdict(int)
            one_day = defaultdict(int)
            
            for i, day in enumerate(cycle_history):
                numbers = day.get_all_2digit_numbers()
                for num in numbers:
                    freq[num] += 1
                    
                    # Phát hiện chu kỳ 1 ngày (xuất hiện liên tiếp)
                    if i > 0 and num in cycle_history[i-1].get_all_2digit_numbers():
                        one_day[num] += 1
            
            # Lấy top số
            top_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
            top_one_day = sorted(one_day.items(), key=lambda x: x[1], reverse=True)[:5]
            
            analysis[name] = {
                'top_frequency': top_freq,
                'one_day_cycle': top_one_day,
                'total_days': days
            }
        
        return analysis
    
    def train_ml_model(self, history):
        """Huấn luyện model ML nếu chưa có"""
        try:
            # Kiểm tra nếu model đã được train và lưu
            if os.path.exists(self.model_path):
                self.ml_model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                return
            
            # Chuẩn bị dữ liệu training
            X, y = self.prepare_ml_data(history)
            
            # Feature scaling
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Huấn luyện model
            self.ml_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.ml_model.fit(X_scaled, y)
            
            # Lưu model để sử dụng sau
            joblib.dump(self.ml_model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
        except Exception as e:
            print(f"Lỗi khi train ML model: {str(e)}")
            self.ml_model = None
    
    def prepare_ml_data(self, history):
        """Chuẩn bị dữ liệu cho ML model"""
        # Triển khai theo nhu cầu cụ thể của bạn
        # Đây chỉ là ví dụ cơ bản
        X = []
        y = []
        
        for i in range(30, len(history)):
            # Lấy features từ 30 ngày trước
            features = self.extract_features(history[i-30:i])
            X.append(features)
            
            # Lấy target là các số xuất hiện ngày hiện tại
            target = history[i].get_all_2digit_numbers()
            y.append(target)
        
        return np.array(X), np.array(y)
    
    def extract_features(self, history_window):
        """Trích xuất đặc trưng từ cửa sổ lịch sử"""
        # Triển khai theo nhu cầu cụ thể
        # Ví dụ: tần suất xuất hiện của các số
        freq = defaultdict(int)
        for day in history_window:
            for num in day.get_all_2digit_numbers():
                freq[num] += 1
        
        # Chuyển thành vector đặc trưng
        features = []
        for num in range(100):  # Tất cả các số từ 00-99
            features.append(freq.get(f"{num:02d}", 0))
        
        return features
    
    def predict_with_ml(self, history):
        """Dự đoán bằng model ML"""
        if self.ml_model is None:
            self.train_ml_model(history)
            if self.ml_model is None:
                return []
        
        try:
            # Chuẩn bị dữ liệu dự đoán
            features = self.extract_features(history[:30])
            X = self.scaler.transform([features])
            
            # Dự đoán xác suất
            probas = self.ml_model.predict_proba(X)[0]
            
            # Lấy top các số có xác suất cao
            top_indices = np.argsort(probas)[::-1][:10]
            return [(f"{i:02d}", probas[i]*100) for i in top_indices]
        
        except Exception as e:
            print(f"Lỗi khi dự đoán bằng ML: {str(e)}")
            return []
    
    def analyze_hot_pairs(self, history):
        """Phân tích cặp số nóng"""
        pair_counts = defaultdict(int)
        for day in history[:7]:  # 7 ngày gần nhất
            numbers = day.get_all_2digit_numbers()
            for pair in combinations(sorted(numbers), 2):
                pair_counts[pair] += 1
        
        self.hot_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return self.hot_pairs
    
    def predict(self, target_date, history, top_n=15):
        """Phiên bản kết hợp tối ưu"""
        if not history:
            return {
                'predicted_numbers': [],
                'cycle_analysis': {},
                'hot_pairs': [],
                'weights': self.cycle_weights
            }
        
        # Phân tích đa chu kỳ
        cycle_analysis = self.analyze_cycles(history)
        
        # Phân tích cặp nóng
        self.analyze_hot_pairs(history)
        
        # Tính điểm tổng hợp
        scores = defaultdict(float)
        
        # 1. Điểm từ phân tích chu kỳ
        for cycle_name, data in cycle_analysis.items():
            weight = self.cycle_weights.get(cycle_name, 0)
            
            # Điểm từ tần suất xuất hiện
            for num, cnt in data['top_frequency']:
                scores[num] += cnt * weight
            
            # Bonus điểm cho chu kỳ ngắn
            for num, cnt in data['one_day_cycle']:
                scores[num] += cnt * weight * 1.5
        
        # 2. Điểm từ ML (nếu có)
        try:
            ml_preds = self.predict_with_ml(history)
            for num, conf in ml_preds:
                scores[num] += conf * 0.25  # Trọng số nhỏ hơn phân tích chu kỳ
        except Exception as e:
            print(f"ML prediction failed: {str(e)}")
        
        # 3. Tăng cường điểm cho số trong cặp nóng
        hot_numbers = set()
        for pair, _ in self.hot_pairs:
            hot_numbers.update(pair)
        
        for num in hot_numbers:
            if num in scores:
                scores[num] *= 1.2  # Tăng 20% điểm
        
        # Chuẩn hóa và trả kết quả
        max_score = max(scores.values()) if scores else 1
        scored_numbers = [(num, (score/max_score)*100) for num, score in scores.items()]
        top_numbers = sorted(scored_numbers, key=lambda x: x[1], reverse=True)[:top_n]
        
        return {
            'predicted_numbers': top_numbers,
            'cycle_analysis': cycle_analysis,
            'hot_pairs': self.hot_pairs,
            'weights': self.cycle_weights
        }