# results/hybrid_predictor.py
import os
from collections import defaultdict
from datetime import date, timedelta
from itertools import combinations

import joblib
import numpy as np
from django.db.models import Avg, Q
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from .models import CycleAccuracy, KetQuaXoSo


class HybridPredictor:
    def __init__(self):
        self.cycle_weights = self.load_dynamic_weights()
        self.ml_model = None
        self.scaler = None
        self.hot_pairs = []
        self.model_path = os.path.join(
            os.path.dirname(__file__), "ml_models/xs_model.pkl"
        )
        self.scaler_path = os.path.join(
            os.path.dirname(__file__), "ml_models/scaler.pkl"
        )
        self.model_name = "HybridPredictor_v1"
        self.load_weights()

    def load_weights(self):
        """Tải trọng số từ database"""
        self.cycle_weights = {
            "1_ngay": 0.55,
            "3_ngay": 0.65,
            "7_ngay": 0.40,
            "14_ngay": 0.45,
            "30_ngay": 0.35,
        }

        try:
            # Lấy độ chính xác trung bình
            avg_accuracy = (
                CycleAccuracy.objects.aggregate(avg=Avg("accuracy"))["avg"] or 50
            )

            # Điều chỉnh trọng số dựa trên độ chính xác tương đối
            for cycle in CycleAccuracy.objects.all():
                relative_accuracy = cycle.accuracy / avg_accuracy
                self.cycle_weights[cycle.cycle_type] *= relative_accuracy

            # Chuẩn hóa lại tổng trọng số = 1
            total = sum(self.cycle_weights.values())
            self.cycle_weights = {k: v / total for k, v in self.cycle_weights.items()}

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
                return {k: v / total_accuracy for k, v in weights.items()}
        except:
            pass

        # Trọng số mặc định nếu chưa có dữ liệu
        return {
            "1_ngay": 0.35,
            "3_ngay": 0.25,
            "7_ngay": 0.2,
            "14_ngay": 0.15,
            "30_ngay": 0.05,
        }

    def analyze_cycles(self, history):
        """Phân tích đa chu kỳ cải tiến"""
        analysis = {}
        cycle_days = {
            "1_ngay": 1,
            "3_ngay": 3,
            "7_ngay": 7,
            "14_ngay": 14,
            "30_ngay": 30,
        }

        for name, days in cycle_days.items():
            cycle_history = history[:days]
            freq = defaultdict(int)
            one_day = defaultdict(int)

            for i, day in enumerate(cycle_history):
                numbers = day.get_all_2digit_numbers()
                for num in numbers:
                    freq[num] += 1

                    # Phát hiện chu kỳ 1 ngày (xuất hiện liên tiếp)
                    if i > 0 and num in cycle_history[i - 1].get_all_2digit_numbers():
                        one_day[num] += 1

            # Lấy top số
            top_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
            top_one_day = sorted(one_day.items(), key=lambda x: x[1], reverse=True)[:5]

            analysis[name] = {
                "top_frequency": top_freq,
                "one_day_cycle": top_one_day,
                "total_days": days,
            }

        return analysis

    def train_ml_model(self, history):
        """Huấn luyện model ML chỉ khi có đủ dữ liệu thực tế"""
        try:
            # Kiểm tra nếu model đã được train và lưu
            if os.path.exists(self.model_path):
                self.ml_model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                print("✅ Đã load ML model từ file")
                return

            # 🎯 REALISTIC: Cần tối thiểu 100 ngày để ML có ý nghĩa
            if len(history) < 100:
                print(
                    f"📊 Chỉ có {len(history)} ngày dữ liệu. ML model cần tối thiểu 100 ngày để có hiệu quả."
                )
                print("🔄 Sử dụng statistical analysis thay thế.")
                self.ml_model = None
                return

            # Chuẩn bị dữ liệu training với window size nhỏ hơn
            X, y = self.prepare_ml_data(history)

            if len(X) == 0 or len(y) == 0:
                print("⚠️  Không có dữ liệu training hợp lệ sau khi prepare.")
                self.ml_model = None
                return

            # Đảm bảo X là 2D array
            X = np.array(X)
            if X.ndim == 1:
                X = X.reshape(-1, 1)
            elif X.ndim > 2:
                X = X.reshape(len(X), -1)

            # Feature scaling
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)

            # Xử lý y - chuyển từ list of lists thành binary matrix
            all_numbers = [f"{i:02d}" for i in range(100)]  # 00-99
            y_binary = []

            for target_numbers in y:
                binary_vector = [
                    1 if num in target_numbers else 0 for num in all_numbers
                ]
                y_binary.append(binary_vector)

            y_binary = np.array(y_binary)

            # 🎯 OPTIMIZED: Sử dụng model nhẹ hơn cho lottery prediction
            from sklearn.linear_model import LogisticRegression
            from sklearn.multioutput import MultiOutputClassifier

            # LogisticRegression nhanh hơn RandomForest cho case này
            base_model = LogisticRegression(
                random_state=42, max_iter=1000, solver="lbfgs", n_jobs=-1
            )
            self.ml_model = MultiOutputClassifier(base_model)
            self.ml_model.fit(X_scaled, y_binary)

            # Lưu model để sử dụng sau
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.ml_model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)

            print(
                f"✅ ML model đã được train thành công với {len(X)} samples, {X.shape[1]} features"
            )
            print(f"📈 Sử dụng LogisticRegression (nhanh và phù hợp với lottery data)")

        except Exception as e:
            print(f"❌ Lỗi khi train ML model: {str(e)}")
            print("🔄 Fallback sang statistical analysis.")
            self.ml_model = None

    def prepare_ml_data(self, history):
        """Chuẩn bị dữ liệu cho ML model với window size tối ưu"""
        X = []
        y = []

        # 🎯 REALISTIC: Sử dụng window size nhỏ hơn để có nhiều samples hơn
        window_size = min(14, len(history) // 4)  # Tối đa 14 ngày, hoặc 1/4 total data
        min_samples_needed = max(window_size + 10, 25)  # Cần ít nhất 25 samples

        if len(history) < min_samples_needed:
            print(
                f"prepare_ml_data: Cần tối thiểu {min_samples_needed} ngày dữ liệu để tạo training set."
            )
            return np.array([]), []

        try:
            for i in range(window_size, len(history)):
                # Lấy features từ window_size ngày trước
                features = self.extract_features(history[i - window_size : i])

                if features and len(features) > 0:
                    X.append(features)

                    # Lấy target là các số xuất hiện ngày hiện tại
                    target = history[i].get_all_2digit_numbers()
                    y.append(target if target else [])

            if len(X) == 0:
                print("prepare_ml_data: Không có features hợp lệ.")
                return np.array([]), []

            X = np.array(X)
            print(
                f"📊 prepare_ml_data: Tạo được {len(X)} samples với window_size={window_size} ngày"
            )
            print(f"🔢 Features shape: {X.shape}")

            return X, y

        except Exception as e:
            print(f"❌ Lỗi trong prepare_ml_data: {str(e)}")
            return np.array([]), []

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
        """Dự đoán bằng model ML - chỉ khi có đủ dữ liệu"""
        # 🎯 REALISTIC: Chỉ sử dụng ML khi thực sự có ý nghĩa
        if len(history) < 100:
            print(
                f"📊 Có {len(history)} ngày - sử dụng statistical analysis thay vì ML"
            )
            return []

        if self.ml_model is None:
            self.train_ml_model(history)
            if self.ml_model is None:
                print("🔄 ML model không khả dụng, fallback sang statistical analysis.")
                return []

        try:
            if self.scaler is None:
                print("⚠️  Scaler không khả dụng, không thể thực hiện ML prediction.")
                return []

            # Sử dụng window size tương tự như khi training
            window_size = min(14, len(history) // 4)
            features = self.extract_features(history[:window_size])

            if not features or len(features) == 0:
                print("⚠️  Không thể extract features cho ML prediction.")
                return []

            X = self.scaler.transform([features])

            # Xử lý prediction cho MultiOutputClassifier
            predictions = self.ml_model.predict_proba(X)

            # Tính trung bình xác suất cho mỗi số
            scores = {}
            all_numbers = [f"{i:02d}" for i in range(100)]

            for i, num in enumerate(all_numbers):
                if i < len(predictions):
                    # Lấy xác suất của class 1 (xuất hiện)
                    prob = predictions[i][0][1] if len(predictions[i][0]) > 1 else 0
                    scores[num] = prob * 100

            # Lấy top 10 số có xác suất cao nhất
            top_predictions = sorted(scores.items(), key=lambda x: x[1], reverse=True)[
                :10
            ]
            print(f"🤖 ML prediction: Top số từ model (window_size={window_size})")
            return top_predictions

        except Exception as e:
            print(f"❌ Lỗi khi dự đoán bằng ML: {str(e)}")
            print("🔄 Fallback sang statistical analysis.")
            return []

    def analyze_hot_pairs(self, history):
        """Phân tích cặp số nóng"""
        pair_counts = defaultdict(int)
        for day in history[:7]:  # 7 ngày gần nhất
            numbers = day.get_all_2digit_numbers()
            for pair in combinations(sorted(numbers), 2):
                pair_counts[pair] += 1

        self.hot_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        return self.hot_pairs

    def predict(self, target_date, history, top_n=15):
        """Phiên bản kết hợp tối ưu"""
        if not history:
            return {
                "predicted_numbers": [],
                "cycle_analysis": {},
                "hot_pairs": [],
                "weights": self.cycle_weights,
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
            for num, cnt in data["top_frequency"]:
                scores[num] += cnt * weight

            # Bonus điểm cho chu kỳ ngắn
            for num, cnt in data["one_day_cycle"]:
                scores[num] += cnt * weight * 1.5

        # 2. Điểm từ ML (chỉ khi có đủ dữ liệu thực tế)
        ml_contribution = 0
        if len(history) >= 100:  # Chỉ sử dụng ML khi có đủ data
            try:
                ml_preds = self.predict_with_ml(history)
                for num, conf in ml_preds:
                    scores[num] += conf * 0.15  # Giảm trọng số ML xuống 15%
                    ml_contribution += 1
                print(f"🤖 ML đóng góp {len(ml_preds)} predictions với trọng số 15%")
            except Exception as e:
                print(f"⚠️  ML prediction failed: {str(e)}")
        else:
            print(
                f"📊 Sử dụng pure statistical analysis ({len(history)} ngày < 100 ngày)"
            )

        # 3. Tăng cường điểm cho số trong cặp nóng
        hot_numbers = set()
        for pair, _ in self.hot_pairs:
            hot_numbers.update(pair)

        hot_bonus_count = 0
        for num in hot_numbers:
            if num in scores:
                scores[num] *= 1.1  # Giảm bonus từ 20% xuống 10% để cân bằng
                hot_bonus_count += 1

        # Chuẩn hóa và trả kết quả
        max_score = max(scores.values()) if scores else 1
        scored_numbers = [
            (num, (score / max_score) * 100) for num, score in scores.items()
        ]
        top_numbers = sorted(scored_numbers, key=lambda x: x[1], reverse=True)[:top_n]

        print(
            f"🎯 Final prediction: {len(top_numbers)} số (Statistical: ✅, ML: {'✅' if ml_contribution > 0 else '❌'}, Hot pairs: {hot_bonus_count})"
        )

        return {
            "predicted_numbers": top_numbers,
            "cycle_analysis": cycle_analysis,
            "hot_pairs": self.hot_pairs,
            "weights": self.cycle_weights,
            "ml_used": ml_contribution > 0,
            "data_days": len(history),
        }
