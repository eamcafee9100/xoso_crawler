# analytics/predictors.py
import logging
import time
import math
import os
import json
import numpy as np
from collections import Counter, defaultdict
from datetime import timedelta, datetime
from django.utils import timezone

# Cấu hình logging
logger = logging.getLogger(__name__)

class BachThuLoPredictor:
    """Lớp dự đoán bạch thủ lô với các phương pháp khác nhau và cơ chế tự điều chỉnh"""
    
    def __init__(self, target_date, history_days=90, selected_date=None):
        """
        Khởi tạo predictor
        Args:
            target_date: Ngày cần dự đoán
            history_days: Số ngày lịch sử để phân tích
            selected_date: Ngày được chọn (nếu khác với ngày hiện tại)
        """
        self.target_date = target_date
        self.history_days = history_days
        self.selected_date = selected_date or target_date
        self.feature_names = [
            'number', 'days_since_last', 'hot_cold_index',
            'weekday_freq', 'month_freq', 'position_freq',
            'pair_freq', 'sequence_freq'
        ]
        self.model = None
        self.model_version = "1.1.0"  
        
        # Khởi tạo các biến cache
        self._cache = {}
        self._current_analysis = None
        self._method_performance = None
        self._method_weights = None
        self._ml_predictions = None
        
        # Tạo thư mục model nếu chưa có
        self.model_dir = 'models/bach_thu_lo'
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Khởi tạo các analyzer và optimizer
        self.init_analyzers_and_optimizers()
        
        # Cấu hình logging
        self.logger = self.configure_logging()
        
        # Tải dữ liệu lịch sử
        self.historical_data = self.get_historical_data()
        self.logger.info(f"Đã tải {len(self.historical_data)} bản ghi lịch sử")
        
        # Tải mô hình đã lưu nếu có
        if not self.load_model():
            self.logger.info("Không tìm thấy mô hình đã lưu, sẽ tạo mô hình mới")
            self.init_models()
            
        # Log các thông tin quan trọng
        self.logger.info(f"Đã khởi tạo BachThuLoPredictor: target_date={target_date}, history_days={history_days}")
    
    def init_analyzers_and_optimizers(self):
        """
        Khởi tạo các bộ phân tích và tối ưu hóa
        """
        try:
            from .monthly_frequency_analyzer import MonthlyFrequencyAnalyzer
            from .method_fatigue_analyzer import MethodFatigueAnalyzer
            from .weight_optimizer import WeightOptimizer
            from .performance_evaluator import PerformanceEvaluator
            
            self.monthly_analyzer = MonthlyFrequencyAnalyzer()
            self.fatigue_analyzer = MethodFatigueAnalyzer()
            self.weight_optimizer = WeightOptimizer()
            self.performance_evaluator = PerformanceEvaluator()
            
            logger.info("Đã khởi tạo các bộ phân tích và tối ưu hóa")
        except ImportError as e:
            logger.warning(f"Không thể tải đầy đủ các module analyzer: {e}")
            # Tạo các đối tượng giả
            self.monthly_analyzer = None
            self.fatigue_analyzer = None
            self.weight_optimizer = None
            self.performance_evaluator = None
    
    def configure_logging(self):
        """
        Cấu hình logging cho predictor
        """
        import logging
        import os
        from datetime import datetime
        
        # Tạo thư mục log nếu chưa tồn tại
        log_dir = os.path.join("logs", "bach_thu_lo")
        os.makedirs(log_dir, exist_ok=True)
        
        # Tạo tên file log với timestamp
        log_file = os.path.join(log_dir, f"prediction_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Cấu hình logging
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        console_handler = logging.StreamHandler()
        
        # Định dạng log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Cấu hình logger
        logger = logging.getLogger("BachThuLoPredictor")
        logger.setLevel(logging.INFO)
        
        # Xóa handlers cũ nếu có
        if logger.handlers:
            logger.handlers.clear()
            
        # Thêm handlers mới
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def init_models(self):
        """
        Khởi tạo các mô hình ML từ EnhancedMLModelTrainer
        """
        self.logger.info("Khởi tạo các mô hình ML từ EnhancedMLModelTrainer")
        
        try:
            from results.services.MLModelService import MLModelService
            
            self.ml_service = MLModelService()
            
            # Load models nếu chưa có
            if not self.ml_service.models:
                self.logger.info("Không tìm thấy models, bắt đầu training...")
                training_success = self.ml_service.train_models()
                if not training_success:
                    self.logger.error("Không thể train models")
                    self.model = None
                    return
            
            # Sử dụng model tốt nhất
            best_model_name = self._get_best_model_name()
            if best_model_name and best_model_name in self.ml_service.models:
                self.model = self.ml_service.models[best_model_name]
                self.logger.info(f"Đã load model: {best_model_name}")
            else:
                # Fallback to first available model
                available_models = list(self.ml_service.models.keys())
                if available_models:
                    self.model = self.ml_service.models[available_models[0]]
                    self.logger.info(f"Sử dụng model fallback: {available_models[0]}")
                else:
                    raise Exception("Không có model nào available")
                    
        except Exception as e:
            self.logger.error(f"Lỗi khi load ML models: {e}")
            # Fallback to simple model
            self._init_fallback_model()
    
    def _get_best_model_name(self):
        """Lấy tên model tốt nhất dựa trên performance"""
        try:
            # Logic để chọn model tốt nhất
            # Có thể dựa trên accuracy, recent performance, etc.
            model_names = ['random_forest', 'gradient_boosting', 'extra_trees', 'ridge']
            
            # Tạm thời return random_forest làm default
            return 'random_forest'
            
        except Exception as e:
            self.logger.error(f"Lỗi khi chọn best model: {e}")
            return None
    
    def _init_fallback_model(self):
        """Khởi tạo model dự phòng khi không load được ML models"""
        try:
            from xgboost import XGBRegressor
            # XGBoost thường hiệu quả hơn RandomForest cho nhiều bài toán dự đoán
            self.model = XGBRegressor(
                n_estimators=200,
                learning_rate=0.05,
                max_depth=6,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42
            )
            self.logger.info("Đã khởi tạo mô hình XGBoost fallback")
        except ImportError:
            self.logger.warning("Không thể tải XGBoost, sẽ sử dụng RandomForest")
            try:
                from sklearn.ensemble import RandomForestRegressor
                self.model = RandomForestRegressor(n_estimators=100, random_state=42)
                self.logger.info("Đã khởi tạo mô hình RandomForest fallback")
            except ImportError:
                self.logger.error("Không thể khởi tạo bất kỳ mô hình ML nào")
                self.model = None

    def get_historical_data(self):
        """
        Lấy dữ liệu lịch sử xổ số
        Returns:
            List các bản ghi KetQuaXoSo
        """
        try:
            from django.utils import timezone
            from datetime import timedelta
            from results.models import KetQuaXoSo
            
            end_date = self.target_date - timedelta(days=1)
            start_date = end_date - timedelta(days=self.history_days)
            
            data = list(KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by('-ngay'))
            
            self.logger.info(f"Đã lấy {len(data)} bản ghi lịch sử từ {start_date} đến {end_date}")
            return data
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy dữ liệu lịch sử: {e}", exc_info=True)
            return []
    
    def predict_for_date(self, target_date, analysis_date=None):
        """
        Dự đoán cho ngày cụ thể
        Args:
            target_date: Ngày cần dự đoán
            analysis_date: Ngày phân tích (optional)
        Returns:
            List of predictions với format chuẩn
        """
        try:
            # Update target date
            self.target_date = target_date
            self.selected_date = analysis_date or target_date
            
            # Sử dụng method predict thay vì get_comprehensive_predictions
            predictions = self.predict()  # Method này đã tồn tại
            
            # Format để consistent với các service khác
            formatted_predictions = []
            
            if isinstance(predictions, dict):
                # Combine all prediction types
                all_predictions = []
                
                for method_name, method_preds in predictions.items():
                    if isinstance(method_preds, list):
                        for pred in method_preds:
                            if isinstance(pred, dict):
                                all_predictions.append({
                                    'number': pred.get('number', ''),
                                    'confidence': pred.get('confidence', 0.5),
                                    'method': method_name,
                                    'probability': pred.get('confidence', 0.5)
                                })
                            else:
                                # Handle simple number format
                                all_predictions.append({
                                    'number': str(pred).zfill(2),
                                    'confidence': 0.5,
                                    'method': method_name,
                                    'probability': 0.5
                                })
                
                # Sort by confidence và lấy top predictions
                all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
                formatted_predictions = all_predictions[:20]  # Top 20
                
            elif isinstance(predictions, list):
                # Direct list format
                for i, pred in enumerate(predictions[:20]):
                    if isinstance(pred, dict):
                        formatted_predictions.append({
                            'number': pred.get('number', ''),
                            'confidence': pred.get('confidence', 0.5),
                            'method': 'bach_thu_lo',
                            'probability': pred.get('confidence', 0.5)
                        })
                    else:
                        # Handle simple number format
                        formatted_predictions.append({
                            'number': str(pred).zfill(2),
                            'confidence': max(0.1, 1.0 - (i * 0.05)),  # Decreasing confidence
                            'method': 'bach_thu_lo',
                            'probability': max(0.1, 1.0 - (i * 0.05))
                        })
            
            logger.info(f"Generated {len(formatted_predictions)} predictions for {target_date}")
            return formatted_predictions
            
        except Exception as e:
            logger.error(f"Error in predict_for_date: {e}")
            return []
        
    def split_train_test_data(self):
        """
        Phân chia dữ liệu thành tập huấn luyện và kiểm thử
        Returns:
            Tuple (train_data, test_data)
        """
        if not self.historical_data:
            return [], []
        
        # Sử dụng 80% dữ liệu lịch sử cho huấn luyện, 20% cho kiểm thử
        split_point = int(len(self.historical_data) * 0.8)
        train_data = self.historical_data[split_point:]  # Dữ liệu cũ hơn cho huấn luyện
        test_data = self.historical_data[:split_point]   # Dữ liệu mới hơn cho kiểm thử
        
        self.logger.info(f"Phân chia dữ liệu: {len(train_data)} mẫu huấn luyện, {len(test_data)} mẫu kiểm thử")
        return train_data, test_data
    
    def preprocess_data(self, data):
        """
        Tiền xử lý dữ liệu, bao gồm xử lý dữ liệu thiếu
        Args:
            data: Dữ liệu cần tiền xử lý
        Returns:
            Dữ liệu đã được tiền xử lý
        """
        if not data:
            return []
        
        preprocessed_data = []
        
        for record in data:
            # Bỏ qua bản ghi không có ngày
            if not hasattr(record, 'ngay') or not record.ngay:
                continue
                
            # Tạo bản sao để không ảnh hưởng đến dữ liệu gốc
            processed_record = {
                'ngay': record.ngay,
                'thu': getattr(record, 'thu', ''),
                'giai_db': getattr(record, 'giai_db', ''),
                'giai_1': getattr(record, 'giai_1', ''),
                # Thêm các trường khác
            }
            
            # Xử lý trường hợp giải đặc biệt bị thiếu
            if not processed_record['giai_db']:
                # Có thể sử dụng giá trị mặc định hoặc dự đoán từ các giải khác
                # Ví dụ đơn giản: sử dụng 2 số cuối của giải nhất nếu có
                if processed_record['giai_1'] and len(processed_record['giai_1']) >= 2:
                    processed_record['giai_db_imputed'] = processed_record['giai_1'][-2:]
                else:
                    processed_record['giai_db_imputed'] = '00'  # Giá trị mặc định
                    
            preprocessed_data.append(processed_record)
        
        self.logger.info(f"Đã tiền xử lý {len(preprocessed_data)} bản ghi")
        return preprocessed_data
    
    def save_model(self):
        """
        Lưu mô hình đã huấn luyện vào cả tệp tin và cơ sở dữ liệu
        Returns:
            Boolean: True nếu lưu thành công, False nếu thất bại
        """
        try:
            import joblib
            import os
            import json
            from datetime import datetime
            from django.utils import timezone
            from results.models import OptimizedWeights, AdvancedAnalysisResult

            # 1. Lưu mô hình vào tệp tin
            model_dir = os.path.join("models", "bach_thu_lo")
            os.makedirs(model_dir, exist_ok=True)
            
            # Tạo tên tệp tin có phiên bản và timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_filename = f"xgboost_{self.model_version}_{timestamp}.joblib"
            model_path = os.path.join(model_dir, model_filename)
            
            # Lưu mô hình
            joblib.dump(self.model, model_path)
            self.logger.info(f"Đã lưu mô hình vào tệp tin: {model_path}")
            
            # 2. Lưu thông tin mô hình vào cơ sở dữ liệu
            
            # Tạo metadata cho mô hình
            model_meta = {
                'version': self.model_version,
                'model_type': 'xgboost' if hasattr(self.model, 'get_booster') else type(self.model).__name__,
                'filename': model_filename,
                'path': model_path,
                'feature_names': self.feature_names,
                'parameters': self.model.get_params() if hasattr(self.model, 'get_params') else {},
                'created_at': timestamp,
                'history_days': self.history_days,
                'target_date': self.target_date.strftime('%Y-%m-%d')
            }
            
            # 3. Lưu thông tin trọng số tối ưu
            method_weights = self.calculate_method_weights()
            
            # Lưu vào OptimizedWeights
            optimized_weights = OptimizedWeights.objects.create(
                weights=method_weights,
                meta_info={
                    'model_info': model_meta,
                    'calculation_method': 'BachThuLoPredictor',
                    'history_days': self.history_days,
                    'target_date': self.target_date.strftime('%Y-%m-%d')
                }
            )
            
            self.logger.info(f"Đã lưu trọng số tối ưu vào cơ sở dữ liệu: ID={optimized_weights.id}")
            
            # 4. Lưu các dự đoán và phân tích hiện tại (nếu có)
            try:
                # Thực hiện phân tích nếu chưa có
                if not hasattr(self, '_current_analysis') or not self._current_analysis:
                    self._current_analysis = {
                        'frequency_cycles': self.analyze_frequency_cycles(),
                        'number_relationships': self.analyze_number_relationships(),
                        'result_patterns': self.analyze_result_patterns(),
                        'related_sets': self.analyze_related_number_sets()
                    }
                    
                    # Thử thêm phân tích nâng cao nếu có thể
                    try:
                        self._current_analysis['spectral'] = self.perform_spectral_analysis()
                    except:
                        pass
                    
                    try:
                        self._current_analysis['graph'] = self.perform_graph_analysis()
                    except:
                        pass
                
                # Lấy dự đoán từ các phương pháp ML nếu có
                ml_predictions = {}
                
                # SHAP prediction
                try:
                    shap_result = self.get_shap_prediction()
                    if shap_result and 'predicted_numbers' in shap_result:
                        ml_predictions['shap'] = shap_result
                except:
                    pass
                    
                # LSTM prediction
                try:
                    lstm_numbers = self.train_lstm_model()
                    if lstm_numbers:
                        ml_predictions['lstm'] = {
                            'predicted_numbers': lstm_numbers,
                            'confidence_scores': {num: 0.8 for num in lstm_numbers}
                        }
                except:
                    pass
                    
                # RL prediction
                try:
                    rl_numbers = self.train_rl_agent()
                    if rl_numbers:
                        ml_predictions['rl'] = {
                            'predicted_numbers': rl_numbers,
                            'confidence_scores': {num: 0.75 for num in rl_numbers}
                        }
                except:
                    pass
                
                # Lấy dự đoán kết hợp cuối cùng
                final_predictions = self.generate_27_predictions()
                
                # Lưu vào AdvancedAnalysisResult
                analysis_result, created = AdvancedAnalysisResult.objects.update_or_create(
                    analysis_date=timezone.now().date(),
                    target_date=self.target_date,
                    defaults={
                        'frequency_cycle_analysis': self._current_analysis.get('frequency_cycles', []),
                        'number_relationship_analysis': self._current_analysis.get('number_relationships', []),
                        'pattern_analysis': self._current_analysis.get('result_patterns', []),
                        'related_set_analysis': self._current_analysis.get('related_sets', []),
                        'spectral_analysis': self._current_analysis.get('spectral', []),
                        'graph_analysis': self._current_analysis.get('graph', []),
                        'shap_prediction': ml_predictions.get('shap', {}),
                        'lstm_prediction': ml_predictions.get('lstm', {}),
                        'rl_prediction': ml_predictions.get('rl', {}),
                        'combined_predictions': final_predictions,
                        'prediction_weights': method_weights
                    }
                )
                
                self.logger.info(f"Đã lưu kết quả phân tích vào cơ sở dữ liệu: ID={analysis_result.id}")
                
            except Exception as analysis_error:
                self.logger.warning(f"Không thể lưu phân tích hiện tại: {analysis_error}", exc_info=True)
            
            # 5. Cập nhật thông tin chu kỳ hiệu suất cho các phương pháp
            try:
                from results.models import MethodCyclicalPerformance
                
                # Lấy tháng và năm hiện tại
                current_month = self.target_date.month
                current_year = self.target_date.year
                
                # Xác định giai đoạn trong tháng (đầu, giữa, cuối)
                day_of_month = self.target_date.day
                if day_of_month <= 10:
                    period = 'early_month_performance'
                elif day_of_month <= 20:
                    period = 'mid_month_performance'
                else:
                    period = 'late_month_performance'
                
                # Cập nhật hiệu suất chu kỳ cho mỗi phương pháp
                for method_name, weight in method_weights.items():
                    # Tìm hoặc tạo bản ghi
                    performance, created = MethodCyclicalPerformance.objects.get_or_create(
                        method_name=method_name,
                        year=current_year,
                        month=current_month
                    )
                    
                    # Lấy hiệu suất hiện tại của giai đoạn
                    period_performance = getattr(performance, period, {})
                    if not isinstance(period_performance, dict):
                        period_performance = {}
                    
                    # Cập nhật thông tin hiệu suất
                    if hasattr(self, '_method_performance') and method_name in self._method_performance:
                        method_perf = self._method_performance[method_name]
                        
                        # Cập nhật hiệu suất giai đoạn
                        today_str = self.target_date.strftime('%Y-%m-%d')
                        period_performance[today_str] = {
                            'weight': weight,
                            'hit_rate': method_perf.get('hit_rate', 0),
                            'hit_count': method_perf.get('hit_count', 0),
                            'total_predictions': method_perf.get('total_predictions', 0)
                        }
                        
                        # Cập nhật trường giai đoạn
                        setattr(performance, period, period_performance)
                        
                        # Cập nhật thống kê tổng thể
                        if method_perf.get('hit_count', 0) > 0:
                            performance.total_hit_days += 1
                        performance.total_days += 1
                        
                        # Tính tỷ lệ trúng mới
                        if performance.total_days > 0:
                            performance.hit_rate = (performance.total_hit_days / performance.total_days) * 100
                        
                        # Kiểm tra ngưỡng mệt mỏi
                        if not performance.fatigue_threshold_reached and performance.total_days >= 19:
                            # Đánh giá hiệu suất 7 ngày gần nhất
                            recent_days = 0
                            recent_hits = 0
                            
                            for day_str, day_perf in period_performance.items():
                                if recent_days >= 7:
                                    break
                                recent_days += 1
                                if day_perf.get('hit_count', 0) > 0:
                                    recent_hits += 1
                            
                            # Nếu hiệu suất gần đây thấp (< 25%), đánh dấu đã đạt ngưỡng mệt mỏi
                            if recent_days > 0 and (recent_hits / recent_days) < 0.25:
                                performance.fatigue_threshold_reached = True
                                performance.fatigue_reached_on = timezone.now().date()
                                self.logger.info(f"Phương pháp {method_name} đã đạt ngưỡng mệt mỏi")
                    
                    # Lưu thay đổi
                    performance.save()
                    
            except Exception as cycle_error:
                self.logger.warning(f"Không thể cập nhật chu kỳ hiệu suất: {cycle_error}", exc_info=True)
            
            return True
        except Exception as e:
            self.logger.error(f"Lỗi khi lưu mô hình: {e}", exc_info=True)
            return False

    def load_model(self):
        """
        Nạp mô hình đã huấn luyện trước đó từ cả tệp tin và cơ sở dữ liệu
        Returns:
            Boolean: True nếu nạp thành công, False nếu thất bại
        """
        try:
            import joblib
            import os
            import json
            from results.models import OptimizedWeights, AdvancedAnalysisResult
            
            # 1. Thử tìm thông tin mô hình từ cơ sở dữ liệu trước
            latest_weights = OptimizedWeights.objects.filter(
                meta_info__model_info__version=self.model_version
            ).order_by('-calculation_date').first()
            
            if latest_weights:
                # Lấy thông tin mô hình từ metadata
                model_meta = latest_weights.meta_info.get('model_info', {})
                model_path = model_meta.get('path')
                
                # Kiểm tra xem tệp tin mô hình có tồn tại không
                if model_path and os.path.exists(model_path):
                    # Nạp mô hình từ tệp tin
                    self.model = joblib.load(model_path)
                    
                    # Nạp các thông tin khác
                    self.feature_names = model_meta.get('feature_names', self.feature_names)
                    
                    self.logger.info(f"Đã nạp mô hình từ cơ sở dữ liệu: {model_path}")
                    
                    # Nạp thông tin phân tích gần nhất
                    latest_analysis = AdvancedAnalysisResult.objects.filter(
                        target_date__lte=self.target_date
                    ).order_by('-target_date').first()
                    
                    if latest_analysis:
                        # Cache kết quả phân tích để sử dụng sau
                        self._current_analysis = {
                            'frequency_cycles': latest_analysis.frequency_cycle_analysis,
                            'number_relationships': latest_analysis.number_relationship_analysis,
                            'result_patterns': latest_analysis.pattern_analysis,
                            'related_sets': latest_analysis.related_set_analysis,
                            'spectral': latest_analysis.spectral_analysis,
                            'graph': latest_analysis.graph_analysis
                        }
                        
                        # Cache các dự đoán ML
                        self._ml_predictions = {
                            'shap': latest_analysis.shap_prediction,
                            'lstm': latest_analysis.lstm_prediction,
                            'rl': latest_analysis.rl_prediction
                        }
                        
                        self.logger.info(f"Đã nạp kết quả phân tích từ cơ sở dữ liệu: ID={latest_analysis.id}")
                    
                    # Nạp trọng số phương pháp
                    self._method_weights = latest_weights.weights
                    self.logger.info(f"Đã nạp trọng số phương pháp từ cơ sở dữ liệu")
                    
                    return True
            
            # 2. Nếu không tìm thấy trong cơ sở dữ liệu, thử tìm trong thư mục mô hình
            model_dir = os.path.join("models", "bach_thu_lo")
            if not os.path.exists(model_dir):
                self.logger.warning(f"Thư mục mô hình không tồn tại: {model_dir}")
                return False
            
            # Tìm tệp tin mô hình có phiên bản phù hợp
            model_files = [f for f in os.listdir(model_dir) if f.startswith(f"xgboost_{self.model_version}") and f.endswith(".joblib")]
            
            if not model_files:
                self.logger.warning(f"Không tìm thấy mô hình phiên bản {self.model_version} trong thư mục {model_dir}")
                return False
            
            # Sắp xếp theo thời gian tạo (mới nhất trước)
            model_files.sort(reverse=True)
            model_path = os.path.join(model_dir, model_files[0])
            
            # Nạp mô hình
            self.model = joblib.load(model_path)
            self.logger.info(f"Đã nạp mô hình từ tệp tin: {model_path}")
            
            return True
        except Exception as e:
            self.logger.error(f"Lỗi khi nạp mô hình: {e}", exc_info=True)
            return False
    
    def update_model_version(self):
        """
        Cập nhật phiên bản mô hình
        Returns:
            String: Phiên bản mới
        """
        from datetime import datetime
        
        # Tạo phiên bản dựa trên ngày và version hiện tại
        current_version = self.model_version.split('.')
        
        # Tăng version patch
        if len(current_version) >= 3:
            patch = int(current_version[2]) + 1
            current_version[2] = str(patch)
        else:
            # Thêm số phiên bản patch nếu chưa có
            current_version.append('1')
        
        # Cập nhật version
        self.model_version = '.'.join(current_version)
        
        self.logger.info(f"Đã cập nhật phiên bản mô hình: {self.model_version}")
        return self.model_version
    
    def predict(self):
        """
        Thực hiện dự đoán kết hợp từ nhiều phương pháp
        với điều chỉnh chu kỳ hiệu suất
        Returns:
            Dict chứa kết quả dự đoán
        """
        try:
            # Kiểm tra cache
            cache_key = f"basic_prediction_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                self.logger.info(f"Sử dụng kết quả dự đoán từ cache cho ngày {self.target_date}")
                return cached_result
            
            self.logger.info("Bắt đầu quá trình dự đoán")
            
            # Kiểm tra dữ liệu lịch sử
            if not self.historical_data:
                self.logger.warning("Không có dữ liệu lịch sử cho dự đoán")
                return None
            
            # Dự đoán từng phương pháp
            predictions = {}
            
            # Phương pháp lặp lại gần nhất
            recent_numbers = self.predict_recent()
            if recent_numbers:
                predictions['lap_lai_gan_nhat'] = recent_numbers
            
            # Phương pháp tần suất cao
            frequency_numbers = self.predict_frequency()
            if frequency_numbers:
                predictions['tan_so_cao'] = frequency_numbers
            
            # Phương pháp bóng số
            shadow_numbers = self.predict_shadow()
            if shadow_numbers:
                predictions['bong_so'] = shadow_numbers
            
            # Phương pháp khu vực
            region_numbers = self.predict_region()
            if region_numbers:
                predictions['khu_vuc'] = region_numbers
            
            # Phương pháp chu kỳ
            cycle_numbers = self.predict_cycle()
            if cycle_numbers:
                predictions['chu_ky'] = cycle_numbers
            
            # Điều chỉnh dự đoán dựa trên chu kỳ hiệu suất
            adjusted_results = self.apply_cyclical_adjustment(predictions, self.target_date)
            
            # Tính kết quả kết hợp với trọng số đã điều chỉnh
            recommended_numbers = self.calculate_combined_numbers(
                adjusted_results['predictions'],
                adjusted_results['method_weights']
            )
            
            # Chuẩn bị kết quả cuối cùng
            result = {
                'predictions': adjusted_results['predictions'],
                'method_weights': adjusted_results['method_weights'],
                'recommended_numbers': recommended_numbers,
                'cyclical_analysis': adjusted_results.get('cyclical_analysis')
            }
            
            # Cache kết quả
            self.cache_result(cache_key, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Lỗi trong phương thức predict: {e}", exc_info=True)
            return None
    
    def enhance_predict(self):
        """
        Phương pháp dự đoán nâng cao tích hợp tất cả các phân tích
        Returns:
            Dict chứa kết quả dự đoán nâng cao
        """
        try:
            # Kiểm tra cache
            cache_key = f"enhanced_prediction_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                self.logger.info(f"Sử dụng kết quả dự đoán nâng cao từ cache cho ngày {self.target_date}")
                return cached_result
            
            self.logger.info("Bắt đầu quy trình dự đoán nâng cao")
            
            # Bước 1: Phân tích cơ bản
            basic_predictions = self.predict()
            if not basic_predictions:
                return None
                
            # Bước 2: Phân tích tần suất chu kỳ
            cycle_numbers = self.analyze_frequency_cycles()
            
            # Bước 3: Phân tích mối quan hệ giữa các số
            relationship_numbers = self.analyze_number_relationships()
            
            # Bước 4: Phân tích mẫu kết quả
            pattern_numbers = self.analyze_result_patterns()
            
            # Bước 5: Phân tích bộ số liên quan
            related_numbers = self.analyze_related_number_sets()
            
            # Bước 6: Phân tích phổ (nếu thư viện có sẵn)
            try:
                spectral_numbers = self.perform_spectral_analysis() or []
            except Exception as e:
                self.logger.warning(f"Không thể thực hiện phân tích phổ: {e}")
                spectral_numbers = []
                
            # Bước 7: Phân tích đồ thị (nếu thư viện có sẵn)
            try:
                graph_numbers = self.perform_graph_analysis() or []
            except Exception as e:
                self.logger.warning(f"Không thể thực hiện phân tích đồ thị: {e}")
                graph_numbers = []
                
            # Bước 8: Dự đoán từ mô hình ML
            ml_predictions = {}
            
            # SHAP prediction
            shap_result = self.get_shap_prediction()
            if shap_result and 'predicted_numbers' in shap_result:
                ml_predictions['shap'] = {
                    'numbers': shap_result['predicted_numbers'],
                    'confidence': shap_result['confidence_scores']
                }
                
            # LSTM prediction
            lstm_numbers = self.train_lstm_model() or []
            if lstm_numbers:
                ml_predictions['lstm'] = {
                    'numbers': lstm_numbers,
                    'confidence': {num: 0.8 for num in lstm_numbers}  # Giá trị mặc định
                }
                
            # RL prediction
            rl_numbers = self.train_rl_agent() or []
            if rl_numbers:
                ml_predictions['rl'] = {
                    'numbers': rl_numbers,
                    'confidence': {num: 0.75 for num in rl_numbers}  # Giá trị mặc định
                }
            
            # Bước 9: Kết hợp và xếp hạng các dự đoán
            all_predictions = {
                'basic': basic_predictions,
                'advanced': {
                    'frequency_cycles': cycle_numbers,
                    'relationships': relationship_numbers,
                    'patterns': pattern_numbers,
                    'related_sets': related_numbers,
                    'spectral': spectral_numbers,
                    'graph': graph_numbers
                },
                'ml_models': ml_predictions
            }
            
            # Bước 10: Tạo danh sách 27 số cuối cùng với trọng số và xác suất
            final_predictions = self.generate_27_predictions()
            
            # Bước 11: Lưu kết quả phân tích vào cơ sở dữ liệu và cache
            self.save_analysis_result(all_predictions, final_predictions)
            
            # Tạo kết quả cuối cùng
            result = {
                'all_predictions': all_predictions,
                'final_predictions': final_predictions
            }
            
            # Cache kết quả
            self.cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Lỗi trong quy trình dự đoán nâng cao: {e}", exc_info=True)
            # Quay lại phương pháp dự đoán cơ bản nếu có lỗi
            return self.predict()
    
    def save_analysis_result(self, all_predictions, final_predictions):
        """
        Lưu kết quả phân tích vào cơ sở dữ liệu
        Args:
            all_predictions: Tất cả các dự đoán từ các phương pháp
            final_predictions: Danh sách 27 số cuối cùng với trọng số
        """
        try:
            from results.models import AdvancedAnalysisResult
            from django.utils import timezone
            
            # Kiểm tra nếu đã có phân tích cho ngày này
            existing = AdvancedAnalysisResult.objects.filter(
                analysis_date=timezone.now().date(),
                target_date=self.target_date
            ).first()
            
            # Chuẩn bị dữ liệu lưu trữ
            analysis_data = {
                'analysis_date': timezone.now().date(),
                'target_date': self.target_date,
                'frequency_cycle_analysis': all_predictions.get('advanced', {}).get('frequency_cycles', []),
                'number_relationship_analysis': all_predictions.get('advanced', {}).get('relationships', []),
                'pattern_analysis': all_predictions.get('advanced', {}).get('patterns', []),
                'related_set_analysis': all_predictions.get('advanced', {}).get('related_sets', []),
                'spectral_analysis': all_predictions.get('advanced', {}).get('spectral', []),
                'graph_analysis': all_predictions.get('advanced', {}).get('graph', []),
                'shap_prediction': all_predictions.get('ml_models', {}).get('shap', {}),
                'lstm_prediction': all_predictions.get('ml_models', {}).get('lstm', {}),
                'rl_prediction': all_predictions.get('ml_models', {}).get('rl', {}),
                'combined_predictions': final_predictions,
                'prediction_weights': all_predictions.get('basic', {}).get('method_weights', {})
            }
            
            # Cập nhật hoặc tạo mới
            if existing:
                for key, value in analysis_data.items():
                    if key != 'analysis_date' and key != 'target_date':
                        setattr(existing, key, value)
                existing.save()
                self.logger.info(f"Đã cập nhật kết quả phân tích cho ngày {self.target_date}")
            else:
                result = AdvancedAnalysisResult.objects.create(**analysis_data)
                self.logger.info(f"Đã lưu kết quả phân tích mới cho ngày {self.target_date}")
            
        except Exception as e:
            self.logger.error(f"Lỗi khi lưu kết quả phân tích: {e}", exc_info=True)
    
    def update_performance_with_actual_result(self, prediction_date, actual_result):
        """
        Cập nhật hiệu suất dự đoán với kết quả thực tế
        Args:
            prediction_date: Ngày dự đoán
            actual_result: Kết quả xổ số thực tế
        Returns:
            Boolean: True nếu cập nhật thành công, False nếu thất bại
        """
        try:
            from results.models import AdvancedAnalysisResult, MethodPerformanceHistory
            
            # Lấy phân tích cho ngày dự đoán
            analysis = AdvancedAnalysisResult.objects.filter(
                target_date=prediction_date
            ).first()
            
            if not analysis:
                self.logger.warning(f"Không tìm thấy phân tích cho ngày {prediction_date}")
                return False
            
            # Lấy các số thực tế
            actual_numbers = []
            if hasattr(actual_result, 'get_all_2digit_numbers'):
                actual_numbers = actual_result.get_all_2digit_numbers()
            
            # Nếu không có số thực tế, không thể đánh giá
            if not actual_numbers:
                self.logger.warning(f"Không có số thực tế cho ngày {prediction_date}")
                return False
            
            # Cập nhật kết quả thực tế và tính toán hiệu suất
            analysis.actual_results = actual_numbers
            
            # Tính hiệu suất cho từng phương pháp
            performance_metrics = {}
            
            # Đánh giá các dự đoán từ phương pháp cơ bản
            if analysis.combined_predictions:
                # Tính tỷ lệ trúng
                hit_count = sum(1 for pred in analysis.combined_predictions if pred[0] in actual_numbers)
                total_count = len(analysis.combined_predictions)
                
                if total_count > 0:
                    hit_rate = (hit_count / total_count) * 100
                else:
                    hit_rate = 0
                    
                performance_metrics['combined'] = {
                    'hit_count': hit_count,
                    'total_count': total_count,
                    'hit_rate': hit_rate
                }
            
            # Đánh giá các dự đoán từ các mô hình ML
            for model_type in ['shap', 'lstm', 'rl']:
                prediction_field = f"{model_type}_prediction"
                
                if hasattr(analysis, prediction_field) and getattr(analysis, prediction_field):
                    prediction = getattr(analysis, prediction_field)
                    
                    if 'predicted_numbers' in prediction:
                        numbers = prediction['predicted_numbers']
                        hit_count = sum(1 for num in numbers if num in actual_numbers)
                        total_count = len(numbers)
                        
                        if total_count > 0:
                            hit_rate = (hit_count / total_count) * 100
                        else:
                            hit_rate = 0
                            
                        performance_metrics[model_type] = {
                            'hit_count': hit_count,
                            'total_count': total_count,
                            'hit_rate': hit_rate
                        }
            
            # Lưu thông tin hiệu suất
            analysis.performance_metrics = performance_metrics
            analysis.save()
            
            # Cập nhật lịch sử hiệu suất của từng phương pháp
            for method, metrics in performance_metrics.items():
                MethodPerformanceHistory.objects.update_or_create(
                    method_name=method,
                    date=prediction_date,
                    defaults={
                        'prediction_count': metrics['total_count'],
                        'hit_count': metrics['hit_count'],
                        'hit_rate': metrics['hit_rate'],
                        'analysis': analysis
                    }
                )
            
            # Cập nhật trọng số dựa trên hiệu suất mới
            self.update_weights_based_on_performance()
            
            # Huấn luyện lại mô hình nếu có đủ dữ liệu mới
            self.update_model_if_needed()
            
            self.logger.info(f"Đã cập nhật hiệu suất cho dự đoán ngày {prediction_date}")
            return True
            
        except Exception as e:
            self.logger.error(f"Lỗi khi cập nhật hiệu suất: {e}", exc_info=True)
            return False
    
    def update_weights_based_on_performance(self):
        """
        Cập nhật trọng số của các phương pháp dựa trên hiệu suất
        """
        try:
            from results.models import MethodPerformanceHistory, OptimizedWeights
            
            # Lấy lịch sử hiệu suất 30 ngày gần nhất
            end_date = self.target_date
            start_date = end_date - timedelta(days=30)
            
            # Lấy hiệu suất cho từng phương pháp
            method_history = MethodPerformanceHistory.objects.filter(
                date__range=(start_date, end_date)
            ).order_by('method_name', 'date')
            
            if not method_history.exists():
                self.logger.warning("Không có đủ dữ liệu hiệu suất để cập nhật trọng số")
                return
            
            # Tính toán hiệu suất trung bình cho từng phương pháp
            method_performance = {}
            for history in method_history:
                method_name = history.method_name
                if method_name not in method_performance:
                    method_performance[method_name] = {
                        'total_predictions': 0,
                        'total_hits': 0,
                        'hit_rate': 0,
                        'confidence': 0
                    }
                
                # Cập nhật thống kê
                perf = method_performance[method_name]
                perf['total_predictions'] += history.prediction_count
                perf['total_hits'] += history.hit_count
                
                # Tính hiệu suất mới
                if perf['total_predictions'] > 0:
                    perf['hit_rate'] = (perf['total_hits'] / perf['total_predictions']) * 100
                    
                # Tính điểm tin cậy (sử dụng Wilson score)
                perf['confidence'] = self.calculate_wilson_score(
                    perf['total_hits'],
                    perf['total_predictions']
                )
            
            # Tính trọng số mới từ hiệu suất
            new_weights = {}
            total_confidence = sum(perf['confidence'] for perf in method_performance.values())
            
            if total_confidence > 0:
                for method, perf in method_performance.items():
                    # Trọng số tỷ lệ với điểm tin cậy
                    new_weights[method] = perf['confidence'] / total_confidence
            
            # Áp dụng điều chỉnh chu kỳ nếu có fatigue analyzer
            if hasattr(self, 'fatigue_analyzer') and self.fatigue_analyzer:
                try:
                    # Lấy khuyến nghị từ fatigue analyzer
                    recommendations = self.fatigue_analyzer.recommend_methods_for_date(self.target_date)
                    
                    # Điều chỉnh trọng số dựa trên khuyến nghị
                    for rec in recommendations.get('recommendations', []):
                        method = rec.get('method')
                        if method in new_weights:
                            # Điều chỉnh trọng số theo khuyến nghị
                            adjustment = rec.get('normalized_weight', 1.0)
                            new_weights[method] *= adjustment
                except Exception as e:
                    self.logger.warning(f"Không thể áp dụng điều chỉnh chu kỳ: {e}")
            
            # Chuẩn hóa trọng số để tổng bằng 1
            total_weight = sum(new_weights.values())
            if total_weight > 0:
                for method in new_weights:
                    new_weights[method] /= total_weight
            
            # Lưu trọng số mới
            OptimizedWeights.objects.create(
                weights=new_weights,
                meta_info={
                    'calculation_method': 'update_weights_based_on_performance',
                    'based_on_days': 30,
                    'target_date': self.target_date.strftime('%Y-%m-%d')
                }
            )
            
            # Cập nhật trọng số hiện tại
            self._method_weights = new_weights
            
            self.logger.info(f"Đã cập nhật trọng số mới dựa trên hiệu suất: {new_weights}")
            
        except Exception as e:
            self.logger.error(f"Lỗi khi cập nhật trọng số dựa trên hiệu suất: {e}", exc_info=True)
    
    def calculate_wilson_score(self, hits, total, confidence=0.95):
        """
        Tính toán Wilson score interval cho tỷ lệ tin cậy
        Args:
            hits: Số lần trúng
            total: Tổng số dự đoán
            confidence: Độ tin cậy (mặc định 0.95 tương ứng với 95%)
        Returns:
            float: Điểm Wilson score
        """
        import math
        import scipy.stats as st
        
        if total == 0:
            return 0
            
        z = st.norm.ppf(1 - (1 - confidence) / 2)  # z-score
        p = hits / total  # Tỷ lệ thành công
        
        # Tính Wilson score interval
        numerator = p + z*z/(2*total) - z * math.sqrt((p*(1-p) + z*z/(4*total)) / total)
        denominator = 1 + z*z/total
        
        return numerator / denominator
    
    def update_model_if_needed(self):
        """
        Kiểm tra và cập nhật mô hình nếu cần thiết
        """
        try:
            from results.models import KetQuaXoSo
            
            # Kiểm tra xem có đủ dữ liệu mới để cập nhật mô hình hay không
            last_training_date = self.target_date - timedelta(days=30)  # Giả sử mô hình được huấn luyện 30 ngày trước
            
            # Đếm số bản ghi mới từ lần huấn luyện cuối cùng
            new_records = KetQuaXoSo.objects.filter(
                ngay__gt=last_training_date,
                ngay__lt=self.target_date
            ).count()
            
            # Nếu có ít nhất 7 bản ghi mới, huấn luyện lại mô hình
            if new_records >= 7:
                self.logger.info(f"Phát hiện {new_records} bản ghi mới, bắt đầu huấn luyện lại mô hình")
                
                # Cập nhật phiên bản mô hình
                self.update_model_version()
                
                # Lấy dữ liệu mới
                self.historical_data = self.get_historical_data()
                
                # Huấn luyện mô hình mới
                success = self.train_models()
                
                if success:
                    # Lưu mô hình mới
                    self.save_model()
                    self.logger.info(f"Đã huấn luyện và lưu mô hình mới phiên bản {self.model_version}")
                else:
                    self.logger.warning("Không thể huấn luyện mô hình mới")
            else:
                self.logger.info(f"Chỉ có {new_records} bản ghi mới, chưa cần huấn luyện lại mô hình")
                
        except Exception as e:
            self.logger.error(f"Lỗi khi cập nhật mô hình: {e}", exc_info=True)
    
    def train_models(self):
        """
        Huấn luyện các mô hình dự đoán
        Returns:
            Boolean: True nếu huấn luyện thành công, False nếu thất bại
        """
        try:
            self.logger.info("Bắt đầu huấn luyện mô hình")
            
            # Phân chia dữ liệu thành tập huấn luyện và kiểm thử
            train_data, test_data = self.split_train_test_data()
            
            if not train_data or len(train_data) < 30:
                self.logger.warning(f"Không đủ dữ liệu huấn luyện: {len(train_data)} bản ghi")
                return False
            
            # Chuẩn bị dữ liệu huấn luyện
            X_train, y_train = self.prepare_data_for_model(train_data)
            
            if len(X_train) < 30 or len(y_train) < 30:
                self.logger.warning(f"Không đủ dữ liệu đã xử lý: X_train={len(X_train)}, y_train={len(y_train)}")
                return False
            
            # Khởi tạo mô hình nếu chưa có
            if self.model is None:
                self.init_models()
                
            if self.model is None:
                self.logger.error("Không thể khởi tạo mô hình")
                return False
            
            # Huấn luyện mô hình
            self.model.fit(X_train, y_train)
            
            # Đánh giá mô hình trên tập kiểm thử
            if test_data:
                X_test, y_test = self.prepare_data_for_model(test_data)
                
                if len(X_test) > 0 and len(y_test) > 0:
                    # Dự đoán trên tập kiểm thử
                    y_pred = self.model.predict(X_test)
                    
                    # Tính độ chính xác
                    from sklearn.metrics import mean_squared_error, r2_score
                    mse = mean_squared_error(y_test, y_pred)
                    r2 = r2_score(y_test, y_pred)
                    
                    self.logger.info(f"Đánh giá mô hình: MSE={mse:.4f}, R2={r2:.4f}")
            
            self.logger.info("Đã huấn luyện mô hình thành công")
            return True
            
        except Exception as e:
            self.logger.error(f"Lỗi khi huấn luyện mô hình: {e}", exc_info=True)
            return False
    
    def prepare_data_for_model(self, data):
        """
        Chuẩn bị dữ liệu cho mô hình ML
        Args:
            data: Dữ liệu cần chuẩn bị
        Returns:
            Tuple (X, y): Đặc trưng và nhãn
        """
        X = []  # Đặc trưng
        y = []  # Nhãn (số giải đặc biệt)
        
        for record in data:
            try:
                # Bỏ qua bản ghi không có ngày
                if not hasattr(record, 'ngay') or not record.ngay:
                    continue
                    
                # Tạo đặc trưng cơ bản
                features = [
                    record.ngay.day / 31.0,  # Ngày trong tháng
                    record.ngay.month / 12.0,  # Tháng
                    record.ngay.weekday() / 6.0,  # Thứ trong tuần
                ]
                
                # Thêm đặc trưng thời gian nâng cao
                features.extend([
                    (record.ngay.day % 2) / 1.0,  # Ngày chẵn/lẻ
                    (record.ngay.day % 5) / 4.0,  # Chu kỳ 5 ngày
                    (record.ngay.day % 10) / 9.0,  # Chu kỳ 10 ngày
                    math.sin(2 * math.pi * record.ngay.day / 31),  # Đặc trưng hình sin của ngày
                    math.cos(2 * math.pi * record.ngay.month / 12),  # Đặc trưng hình cos của tháng
                ])
                
                # Thêm đặc trưng từ lịch sử
                prev_features = self._get_previous_number_features(record.ngay)
                freq_features = self._get_frequency_pattern_features(record.ngay)
                
                if prev_features and freq_features:
                    features.extend(prev_features)
                    features.extend(freq_features)
                    
                    X.append(features)
                    
                    # Lấy số giải đặc biệt làm nhãn
                    if hasattr(record, 'giai_db') and record.giai_db and len(record.giai_db) >= 2:
                        # Lấy 2 số cuối của giải đặc biệt
                        label = int(record.giai_db[-2:])
                        y.append(label)
                    else:
                        # Bỏ qua mẫu này nếu không có giải đặc biệt
                        X.pop()
                
            except Exception as e:
                self.logger.warning(f"Lỗi khi xử lý bản ghi {record.ngay if hasattr(record, 'ngay') else 'unknown'}: {e}")
                continue
        
        return X, y
    
    def _get_previous_number_features(self, date):
        """
        Lấy đặc trưng từ các số trước đó
        Args:
            date: Ngày cần lấy đặc trưng
        Returns:
            List đặc trưng từ các số trước đó
        """
        try:
            # Tìm 3 bản ghi gần nhất trước ngày này
            prev_records = [r for r in self.historical_data if r.ngay < date]
            prev_records = sorted(prev_records, key=lambda r: r.ngay, reverse=True)[:3]
            
            if not prev_records:
                return []
                
            features = []
            for record in prev_records:
                if hasattr(record, 'giai_db') and record.giai_db and len(record.giai_db) >= 2:
                    # Lấy 2 số cuối của giải đặc biệt
                    last_2_digits = int(record.giai_db[-2:])
                    # Chuẩn hóa về khoảng [0, 1]
                    features.append(last_2_digits / 100.0)
                    
                    # Thêm đặc trưng từ chữ số riêng lẻ
                    if len(record.giai_db) >= 2:
                        try:
                            tens_digit = int(record.giai_db[-2])
                            units_digit = int(record.giai_db[-1])
                            features.append(tens_digit / 10.0)
                            features.append(units_digit / 10.0)
                        except:
                            features.extend([0.0, 0.0])
                else:
                    # Nếu không có giải đặc biệt, thêm các giá trị mặc định
                    features.extend([0.5, 0.5, 0.5])
                    
            return features
            
        except Exception as e:
            self.logger.warning(f"Lỗi khi lấy đặc trưng từ số trước đó: {e}")
            return []
    
    def _get_frequency_pattern_features(self, date):
        """
        Lấy đặc trưng từ mẫu tần suất
        Args:
            date: Ngày cần lấy đặc trưng
        Returns:
            List đặc trưng từ mẫu tần suất
        """
        try:
            # Lấy tất cả bản ghi trước ngày này
            prev_records = [r for r in self.historical_data if r.ngay < date]
            
            if not prev_records or len(prev_records) < 10:
                return []
                
            # Tính tần suất xuất hiện của các số
            number_counts = defaultdict(int)
            
            for record in prev_records:
                if hasattr(record, 'get_all_2digit_numbers'):
                    numbers = record.get_all_2digit_numbers()
                    for num in numbers:
                        number_counts[num] += 1
            
            # Lấy 5 số xuất hiện nhiều nhất
            top_numbers = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Tạo đặc trưng
            features = []
            for num, count in top_numbers:
                # Tần suất chuẩn hóa (chia cho tổng số bản ghi)
                norm_freq = count / len(prev_records)
                features.append(norm_freq)
                
                # Thêm số ở dạng chuẩn hóa
                try:
                    features.append(int(num) / 100.0)
                except:
                    features.append(0.5)
            
            # Đảm bảo độ dài cố định (10 đặc trưng cho 5 số hàng đầu)
            while len(features) < 10:
                features.append(0.0)
                
            return features
            
        except Exception as e:
            self.logger.warning(f"Lỗi khi lấy đặc trưng từ mẫu tần suất: {e}")
            return []
    
    def predict_recent(self):
        """
        Dự đoán dựa trên số xuất hiện gần đây
        Returns:
            List các số dự đoán
        """
        try:
            # Kiểm tra cache
            cache_key = f"predict_recent_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Lấy kết quả 7 ngày gần nhất
            recent_results = self.historical_data[:7]
            if not recent_results:
                return []
            
            # Đếm tần suất xuất hiện
            number_counts = {}
            for result in recent_results:
                if hasattr(result, 'get_all_2digit_numbers'):
                    numbers = result.get_all_2digit_numbers()
                    for num in numbers:
                        if num in number_counts:
                            number_counts[num] += 1
                        else:
                            number_counts[num] = 1
            
            # Sắp xếp theo tần suất giảm dần
            sorted_numbers = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Lấy top 10 số
            top_numbers = [num for num, _ in sorted_numbers[:10]]
            
            # Cache kết quả
            self.cache_result(cache_key, top_numbers)
            
            return top_numbers
        except Exception as e:
            self.logger.error(f"Lỗi trong predict_recent: {e}", exc_info=True)
            return []
    
    def predict_frequency(self):
        """
        Dự đoán dựa trên tần suất xuất hiện
        Returns:
            List các số dự đoán
        """
        try:
            # Kiểm tra cache
            cache_key = f"predict_frequency_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            if not self.historical_data:
                return []
            
            # Đếm tần suất xuất hiện
            number_counts = {}
            for result in self.historical_data:
                if hasattr(result, 'get_all_2digit_numbers'):
                    numbers = result.get_all_2digit_numbers()
                    for num in numbers:
                        if num in number_counts:
                            number_counts[num] += 1
                        else:
                            number_counts[num] = 1
            
            # Sắp xếp theo tần suất giảm dần
            sorted_numbers = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Lấy top 10 số
            top_numbers = [num for num, _ in sorted_numbers[:10]]
            
            # Cache kết quả
            self.cache_result(cache_key, top_numbers)
            
            return top_numbers
        except Exception as e:
            self.logger.error(f"Lỗi trong predict_frequency: {e}", exc_info=True)
            return []
    
    def predict_shadow(self):
        """
        Dự đoán dựa trên các cặp bóng số
        Returns:
            List các số dự đoán
        """
        try:
            # Kiểm tra cache
            cache_key = f"predict_shadow_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Ví dụ đơn giản về bóng số (đảo số)
            recent_results = self.historical_data[:5]
            if not recent_results:
                return []
                
            shadow_numbers = []
            for result in recent_results:
                if hasattr(result, 'get_all_2digit_numbers'):
                    numbers = result.get_all_2digit_numbers()
                    for num in numbers:
                        # Tạo bóng số (đảo ngược)
                        shadow = num[1] + num[0]
                        shadow_numbers.append(shadow)
            
            # Loại bỏ trùng lặp
            unique_shadows = list(set(shadow_numbers))
            
            # Lấy tối đa 10 số
            result = unique_shadows[:10]
            
            # Cache kết quả
            self.cache_result(cache_key, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Lỗi trong predict_shadow: {e}", exc_info=True)
            return []
    
    def predict_region(self):
        """
        Dự đoán dựa trên khu vực số
        Returns:
            List các số dự đoán
        """
        try:
            # Kiểm tra cache
            cache_key = f"predict_region_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Ví dụ đơn giản về khu vực số
            if not self.historical_data:
                return []
                
            # Chia số thành các khu vực (0-9, 10-19, 20-29, ...)
            region_counts = {i: 0 for i in range(10)}
            for result in self.historical_data[:10]:  # 10 ngày gần nhất
                if hasattr(result, 'get_all_2digit_numbers'):
                    numbers = result.get_all_2digit_numbers()
                    for num in numbers:
                        region = int(num[0])  # Lấy chữ số đầu tiên
                        region_counts[region] += 1
            
            # Sắp xếp theo tần suất giảm dần
            sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Lấy 3 khu vực phổ biến nhất
            top_regions = [region for region, _ in sorted_regions[:3]]
            
            # Tạo danh sách số dự đoán từ các khu vực
            region_numbers = []
            for region in top_regions:
                # Lấy 3 số từ mỗi khu vực
                for i in range(3):
                    num = f"{region}{i}"
                    region_numbers.append(num)
            
            # Cache kết quả
            self.cache_result(cache_key, region_numbers)
            
            return region_numbers
        except Exception as e:
            self.logger.error(f"Lỗi trong predict_region: {e}", exc_info=True)
            return []
    
    def predict_cycle(self):
        """
        Dự đoán dựa trên chu kỳ
        Returns:
            List các số dự đoán
        """
        try:
            # Kiểm tra cache
            cache_key = f"predict_cycle_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Ví dụ đơn giản về chu kỳ
            if not self.historical_data or len(self.historical_data) < 7:
                return []
                
            # Lấy số giải đặc biệt của 7 ngày cách nhau mỗi 7 ngày
            cycle_numbers = []
            for i in range(0, min(5, len(self.historical_data)), 7):
                if i < len(self.historical_data):
                    result = self.historical_data[i]
                    if hasattr(result, 'giai_db') and result.giai_db:
                        db = result.giai_db
                        if len(db) >= 2:
                            cycle_numbers.append(db[-2:])
            
            # Lấy thêm số từ các chu kỳ 3 ngày và 10 ngày
            for i in range(0, min(5, len(self.historical_data)), 3):
                if i < len(self.historical_data):
                    result = self.historical_data[i]
                    if hasattr(result, 'giai_1') and result.giai_1:
                        g1 = result.giai_1
                        if len(g1) >= 2:
                            cycle_numbers.append(g1[-2:])
                            
            for i in range(0, min(2, len(self.historical_data)), 10):
                if i < len(self.historical_data):
                    result = self.historical_data[i]
                    if hasattr(result, 'get_all_2digit_numbers'):
                        numbers = result.get_all_2digit_numbers()
                        cycle_numbers.extend(numbers[:3])
            
            # Loại bỏ trùng lặp
            unique_cycles = list(set(cycle_numbers))
            
            # Lấy tối đa 10 số
            result = unique_cycles[:10]
            
            # Cache kết quả
            self.cache_result(cache_key, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Lỗi trong predict_cycle: {e}", exc_info=True)
            return []
    
    def analyze_frequency_cycles(self):
        """Phân tích tần suất xuất hiện theo chu kỳ của các số"""
        try:
            # Kiểm tra cache
            cache_key = f"analyze_frequency_cycles_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Tạo dictionary để theo dõi lịch sử xuất hiện của mỗi số
            number_history = {f"{i:02d}": [] for i in range(100)}
            
            # Theo dõi ngày xuất hiện của từng số
            dates = []
            for i, result in enumerate(self.historical_data):
                dates.append(result.ngay)
                if hasattr(result, 'get_all_2digit_numbers'):
                    numbers = result.get_all_2digit_numbers()
                    for num in numbers:
                        # Lưu vị trí (index) xuất hiện
                        number_history[num].append(i)
            
            # Phân tích chu kỳ cho mỗi số
            cycle_predictions = {}
            for num, appearances in number_history.items():
                if len(appearances) >= 3:  # Cần ít nhất 3 lần xuất hiện để phân tích chu kỳ
                    # Tính khoảng cách giữa các lần xuất hiện
                    intervals = [appearances[i+1] - appearances[i] for i in range(len(appearances)-1)]
                    
                    # Đếm tần suất của mỗi khoảng cách
                    interval_counts = Counter(intervals)
                    
                    # Tìm chu kỳ phổ biến nhất
                    most_common_interval, frequency = interval_counts.most_common(1)[0]
                    
                    # Tính xác suất của chu kỳ này
                    probability = frequency / len(intervals) if intervals else 0
                    
                    # Dự đoán ngày tiếp theo dựa trên chu kỳ
                    if appearances and probability > 0.3:  # Chỉ dự đoán nếu chu kỳ có xác suất > 30%
                        last_appearance = appearances[-1]
                        next_predicted_day = last_appearance + most_common_interval
                        
                        # Nếu ngày dự đoán trùng với ngày cần dự đoán, thêm vào kết quả
                        target_index = len(self.historical_data)  # Vị trí của ngày cần dự đoán
                        if next_predicted_day == target_index:
                            cycle_predictions[num] = probability
            
            # Sắp xếp theo xác suất giảm dần
            sorted_predictions = sorted(cycle_predictions.items(), key=lambda x: x[1], reverse=True)
            
            # Trả về top 10 số có chu kỳ khớp với ngày dự đoán
            result = [num for num, _ in sorted_predictions[:10]]
            
            # Cache kết quả
            self.cache_result(cache_key, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Lỗi trong analyze_frequency_cycles: {e}", exc_info=True)
            return []
    
    def analyze_number_relationships(self):
        """Phân tích mối liên hệ giữa các số xuất hiện trong cùng một ngày"""
        try:
            # Kiểm tra cache
            cache_key = f"analyze_number_relationships_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Theo dõi các cặp số xuất hiện cùng nhau
            pair_counts = Counter()
            
            # Đếm số lần mỗi cặp số xuất hiện cùng nhau
            for result in self.historical_data:
                if hasattr(result, 'get_all_2digit_numbers'):
                    numbers = result.get_all_2digit_numbers()
                    
                    # Xét tất cả các cặp số
                    for i in range(len(numbers)):
                        for j in range(i+1, len(numbers)):
                            # Tạo cặp số theo thứ tự tăng dần
                            pair = tuple(sorted([numbers[i], numbers[j]]))
                            pair_counts[pair] += 1
            
            # Tìm các cặp số xuất hiện thường xuyên nhất
            common_pairs = pair_counts.most_common(20)
            
            # Phân tích số trong kết quả gần đây
            recent_numbers = set()
            for result in self.historical_data[:3]:  # 3 ngày gần nhất
                if hasattr(result, 'get_all_2digit_numbers'):
                    recent_numbers.update(result.get_all_2digit_numbers())
            
            # Dự đoán số ghép cặp với số gần đây
            paired_predictions = []
            for num in recent_numbers:
                for pair, _ in common_pairs:
                    if num in pair:
                        # Lấy số còn lại trong cặp
                        other_num = pair[0] if pair[1] == num else pair[1]
                        paired_predictions.append(other_num)
            
            # Loại bỏ trùng lặp và lấy top 10
            result = list(set(paired_predictions))[:10]
            
            # Cache kết quả
            self.cache_result(cache_key, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Lỗi trong analyze_number_relationships: {e}", exc_info=True)
            return []
    
    def analyze_result_patterns(self):
        """Phân tích mẫu số từ kết quả hiện tại so với ngày trước đó"""
        try:
            # Kiểm tra cache
            cache_key = f"analyze_result_patterns_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            pattern_counts = Counter()
            
            # Phân tích mối quan hệ giữa kết quả liên tiếp
            for i in range(1, len(self.historical_data)):
                current_day = self.historical_data[i-1]
                prev_day = self.historical_data[i]
                
                if (hasattr(current_day, 'get_all_2digit_numbers') and
                    hasattr(prev_day, 'get_all_2digit_numbers')):
                    current_numbers = set(current_day.get_all_2digit_numbers())
                    prev_numbers = set(prev_day.get_all_2digit_numbers())
                    
                    # Tìm các mẫu chuyển đổi
                    for prev_num in prev_numbers:
                        # Chuyển đổi số: lấy bóng, đảo, +1, -1, v.v.
                        transformations = self._generate_transformations(prev_num)
                        for trans_type, trans_num in transformations:
                            if trans_num in current_numbers:
                                pattern_counts[(prev_num, trans_type, trans_num)] += 1
            
            # Sắp xếp theo tần suất
            common_patterns = pattern_counts.most_common(30)
            
            # Áp dụng các mẫu phổ biến cho số gần đây
            recent_day = self.historical_data[0]
            pattern_predictions = []
            
            if hasattr(recent_day, 'get_all_2digit_numbers'):
                recent_numbers = recent_day.get_all_2digit_numbers()
                for num in recent_numbers:
                    for (prev_num, trans_type, _), _ in common_patterns:
                        if num == prev_num:
                            # Áp dụng cùng phép biến đổi
                            new_nums = [t[1] for t in self._generate_transformations(num) if t[0] == trans_type]
                            pattern_predictions.extend(new_nums)
            
            # Loại bỏ trùng lặp
            result = list(set(pattern_predictions))[:10]
            
            # Cache kết quả
            self.cache_result(cache_key, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Lỗi trong analyze_result_patterns: {e}", exc_info=True)
            return []
    
    def analyze_related_number_sets(self):
        """Tạo và phân tích bộ số liên quan"""
        try:
            # Kiểm tra cache
            cache_key = f"analyze_related_number_sets_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            success_rates = {}
            
            # Tạo danh sách tất cả các số
            all_numbers = [f"{i:02d}" for i in range(100)]
            
            # Tạo các bộ số liên quan
            number_sets = {}
            for num in all_numbers:
                # Tạo bộ số liên quan
                related_set = self._create_related_set(num)
                number_sets[num] = related_set
            
            # Phân tích tỉ lệ thành công của từng bộ số
            for base_num, related_nums in number_sets.items():
                # Đếm số ngày mà ít nhất một số trong bộ xuất hiện
                hit_days = 0
                for result in self.historical_data:
                    if hasattr(result, 'get_all_2digit_numbers'):
                        result_numbers = set(result.get_all_2digit_numbers())
                        if any(num in result_numbers for num in related_nums):
                            hit_days += 1
                
                # Tính tỉ lệ thành công
                if self.historical_data:
                    success_rate = hit_days / len(self.historical_data)
                    success_rates[base_num] = (success_rate, related_nums)
            
            # Sắp xếp theo tỉ lệ thành công
            sorted_sets = sorted(success_rates.items(), key=lambda x: x[1][0], reverse=True)
            
            # Lấy các bộ số có tỉ lệ thành công cao nhất
            top_related_numbers = []
            for _, (_, related_nums) in sorted_sets[:5]:
                top_related_numbers.extend(related_nums)
            
            # Loại bỏ trùng lặp
            result = list(set(top_related_numbers))[:10]
            
            # Cache kết quả
            self.cache_result(cache_key, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Lỗi trong analyze_related_number_sets: {e}", exc_info=True)
            return []
    
    def _create_related_set(self, num):
        """Tạo bộ số liên quan từ một số"""
        if len(num) != 2:
            return [num]
            
        related_set = [num]
        
        # Đảo số
        reversed_num = num[1] + num[0]
        related_set.append(reversed_num)
        
        # Các số bóng
        try:
            d1, d2 = int(num[0]), int(num[1])
            mirror1 = f"{(9-d1)%10}{d2}"
            mirror2 = f"{d1}{(9-d2)%10}"
            related_set.append(mirror1)
            related_set.append(mirror2)
            
            # Kết hợp đảo và bóng
            reversed_mirror1 = f"{(9-d2)%10}{d1}"
            reversed_mirror2 = f"{d2}{(9-d1)%10}"
            related_set.append(reversed_mirror1)
            related_set.append(reversed_mirror2)
        except:
            pass
        
        # Loại bỏ trùng lặp
        return list(set(related_set))
    
    def _generate_transformations(self, num):
        """Tạo các biến thể của số bằng các phép biến đổi khác nhau"""
        if len(num) != 2:
            return []
            
        transformations = []
        
        # Đảo số
        transformations.append(("reverse", num[1] + num[0]))
        
        # Bóng số (tổng = 9)
        try:
            d1 = int(num[0])
            d2 = int(num[1])
            transformations.append(("mirror1", str((9-d1) % 10) + num[1]))
            transformations.append(("mirror2", num[0] + str((9-d2) % 10)))
        except:
            pass
            
        # Tăng/giảm 1
        try:
            n = int(num)
            transformations.append(("plus1", f"{(n+1)%100:02d}"))
            transformations.append(("minus1", f"{(n-1)%100:02d}"))
        except:
            pass
            
        # Số kép tương ứng
        if num[0] == num[1]:
            pass  # Đã là số kép
        else:
            transformations.append(("double1", num[0] + num[0]))
            transformations.append(("double2", num[1] + num[1]))
            
        return transformations
    
    def perform_spectral_analysis(self):
        """Phân tích phổ để tìm chu kỳ ẩn trong dữ liệu"""
        try:
            # Kiểm tra cache
            cache_key = f"perform_spectral_analysis_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            import numpy as np
            from scipy import signal
            from scipy.fft import fft, fftfreq
            
            # Chuẩn bị dữ liệu cho phân tích phổ
            time_series = []
            for result in self.historical_data:
                if hasattr(result, 'giai_db') and result.giai_db and len(result.giai_db) >= 2:
                    time_series.append(int(result.giai_db[-2:]))
                else:
                    time_series.append(np.nan)
            
            # Xử lý giá trị thiếu
            time_series = np.array(time_series)
            time_series = np.interp(np.arange(len(time_series)),
                                   np.arange(len(time_series))[~np.isnan(time_series)],
                                   time_series[~np.isnan(time_series)])
            
            # Thực hiện FFT
            fft_result = fft(time_series)
            N = len(time_series)
            freqs = fftfreq(N)
            
            # Lấy biên độ
            amplitudes = np.abs(fft_result)
            
            # Loại bỏ thành phần DC (tần số 0)
            freqs = freqs[1:N//2]
            amplitudes = amplitudes[1:N//2]
            
            # Tìm các đỉnh (chu kỳ mạnh nhất)
            peaks, _ = signal.find_peaks(amplitudes)
            
            # Sắp xếp theo biên độ
            sorted_peaks = sorted([(freqs[p], amplitudes[p], 1/freqs[p]) for p in peaks],
                                key=lambda x: x[1], reverse=True)
            
            # Tìm các chu kỳ chính
            main_cycles = []
            for _, _, period in sorted_peaks[:5]:
                if period > 1:  # Chỉ xét chu kỳ > 1
                    main_cycles.append(round(period))
            
            # Dự đoán dựa trên chu kỳ
            predictions = []
            for cycle in main_cycles:
                if len(time_series) > cycle:
                    cycle_pred = time_series[-cycle]
                    predictions.append(f"{int(cycle_pred):02d}")
            
            # Loại bỏ trùng lặp
            result = list(set(predictions))
            
            # Cache kết quả
            self.cache_result(cache_key, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Lỗi trong perform_spectral_analysis: {e}", exc_info=True)
            return []
    
    def perform_graph_analysis(self):
        """Sử dụng phân tích đồ thị để tìm mối liên hệ giữa các số"""
        try:
            # Kiểm tra cache
            cache_key = f"perform_graph_analysis_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            import networkx as nx
            import numpy as np
            
            # Tạo đồ thị
            G = nx.Graph()
            
            # Thêm nút cho mỗi số từ 00-99
            for i in range(100):
                G.add_node(f"{i:02d}")
            
            # Thêm cạnh giữa các số xuất hiện cùng nhau
            for result in self.historical_data:
                if hasattr(result, 'get_all_2digit_numbers'):
                    numbers = result.get_all_2digit_numbers()
                    
                    # Thêm cạnh giữa mỗi cặp số
                    for i in range(len(numbers)):
                        for j in range(i+1, len(numbers)):
                            if G.has_edge(numbers[i], numbers[j]):
                                # Tăng trọng số nếu cạnh đã tồn tại
                                G[numbers[i]][numbers[j]]['weight'] += 1
                            else:
                                # Tạo cạnh mới với trọng số 1
                                G.add_edge(numbers[i], numbers[j], weight=1)
            
            # Tìm số có độ trung tâm cao nhất
            centrality = nx.degree_centrality(G)
            
            # Lấy số gần đây
            recent_numbers = []
            for result in self.historical_data[:3]:  # 3 ngày gần nhất
                if hasattr(result, 'get_all_2digit_numbers'):
                    recent_numbers.extend(result.get_all_2digit_numbers())
            
            # Dự đoán dựa trên số có liên kết mạnh với số gần đây
            predictions = []
            for recent in recent_numbers:
                if recent in G:
                    # Lấy các số liên kết với số gần đây
                    neighbors = [(n, G[recent][n]['weight']) for n in G.neighbors(recent)]
                    
                    # Sắp xếp theo trọng số giảm dần
                    sorted_neighbors = sorted(neighbors, key=lambda x: x[1], reverse=True)
                    
                    # Thêm các số liên kết mạnh nhất
                    for neighbor, _ in sorted_neighbors[:3]:
                        predictions.append(neighbor)
            
            # Loại bỏ trùng lặp và lấy top 10
            result = list(set(predictions))[:10]
            
            # Cache kết quả
            self.cache_result(cache_key, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Lỗi trong perform_graph_analysis: {e}", exc_info=True)
            return []
    
    def get_shap_prediction(self):
        """
        Lấy dự đoán dựa trên SHAP với caching và xử lý lỗi tốt hơn
        Returns:
            Dict chứa thông tin dự đoán SHAP hoặc None nếu không thể tạo
        """
        try:
            # Kiểm tra cache
            cache_key = f"shap_prediction_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                self.logger.info(f"Sử dụng kết quả SHAP từ cache cho ngày {self.target_date}")
                return cached_result
            
            # Kiểm tra thư viện SHAP
            try:
                import shap
                import numpy as np
                from sklearn.ensemble import RandomForestRegressor
            except ImportError as e:
                self.logger.warning(f"Thư viện không khả dụng cho SHAP: {e}")
                return self.get_fallback_prediction("SHAP")
            
            self.logger.info("Bắt đầu dự đoán SHAP")
            
            # Tách dữ liệu huấn luyện và kiểm thử
            train_data, test_data = self.split_train_test_data()
            if not train_data or len(train_data) < 10:
                self.logger.warning(f"Không đủ dữ liệu để huấn luyện mô hình SHAP: {len(train_data) if train_data else 0} bản ghi")
                return self.get_fallback_prediction("SHAP")
            
            # Chuẩn bị dữ liệu cho mô hình
            X, y = self.prepare_data_for_model(train_data)
            
            # Kiểm tra đủ dữ liệu
            if len(X) < 10 or len(y) < 10:
                self.logger.warning(f"Không đủ dữ liệu đã xử lý cho SHAP: X={len(X)}, y={len(y)}")
                return self.get_fallback_prediction("SHAP")
            
            # Chuyển thành mảng numpy
            X = np.array(X)
            y = np.array(y)
            
            self.logger.info(f"Huấn luyện mô hình SHAP với {len(X)} mẫu")
            
            # Huấn luyện mô hình (sử dụng RandomForest vì nó hoạt động tốt với SHAP)
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Tạo giải thích SHAP
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X)
            
            # Tạo đầu vào kiểm thử
            test_inputs = self.generate_test_inputs()
            
            # Dự đoán
            predictions = model.predict(test_inputs)
            
            # Chuyển dự đoán thành số 2 chữ số
            predicted_numbers = [str(int(round(p)) % 100).zfill(2) for p in predictions]
            
            # Loại bỏ trùng lặp
            predicted_numbers = list(set(predicted_numbers))
            
            # Tính điểm tin cậy
            confidence_scores = self.calculate_confidence_scores(predicted_numbers)
            
            # Tạo kết quả SHAP
            result = {
                'predicted_numbers': predicted_numbers[:10],  # Giới hạn 10 số
                'confidence_scores': confidence_scores,
                'shap_values': shap_values.tolist() if hasattr(shap_values, 'tolist') else shap_values,
                'base_value': float(explainer.expected_value) if hasattr(explainer, 'expected_value') else 0,
                'feature_names': self.feature_names
            }
            
            # Lưu vào cache
            self.cache_result(cache_key, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Lỗi trong get_shap_prediction: {e}", exc_info=True)
            return self.get_fallback_prediction("SHAP")
    
    def generate_test_inputs(self):
        """
        Tạo các đầu vào kiểm thử cho mô hình dự đoán
        Returns:
            List các đầu vào kiểm thử
        """
        import numpy as np
        
        # Tạo đặc trưng cơ bản từ ngày cần dự đoán
        weekday = self.target_date.weekday() / 6.0
        day = self.target_date.day / 31.0
        month = self.target_date.month / 12.0
        
        # Tạo nhiều biến thể hơn cho dự đoán
        test_inputs = []
        
        # Thêm nhiều biến thể từ ngày hiện tại
        factors = [0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15]
        for day_factor in factors:
            for month_factor in [0.9, 1.0, 1.1]:
                for weekday_factor in [0.9, 1.0, 1.1]:
                    # Tạo đặc trưng cơ bản
                    test_input = [
                        day * day_factor,
                        month * month_factor,
                        weekday * weekday_factor
                    ]
                    
                    # Thêm các đặc trưng thời gian nâng cao
                    test_input.extend([
                        (self.target_date.day % 2) / 1.0,  # Ngày chẵn/lẻ
                        (self.target_date.day % 5) / 4.0,  # Chu kỳ 5 ngày
                        (self.target_date.day % 10) / 9.0,  # Chu kỳ 10 ngày
                        np.sin(2 * np.pi * self.target_date.day / 31),  # Đặc trưng hình sin của ngày
                        np.cos(2 * np.pi * self.target_date.month / 12),  # Đặc trưng hình cos của tháng
                    ])
                    
                    # Thêm đặc trưng từ lịch sử
                    if hasattr(self, '_previous_number_features'):
                        test_input.extend(self._previous_number_features)
                    else:
                        # Thêm giá trị mặc định nếu không có
                        test_input.extend([0.5] * 9)  # 3 bản ghi x 3 đặc trưng
                        
                    if hasattr(self, '_frequency_pattern_features'):
                        test_input.extend(self._frequency_pattern_features)
                    else:
                        # Thêm giá trị mặc định nếu không có
                        test_input.extend([0.5] * 10)  # 5 số x 2 đặc trưng
                    
                    test_inputs.append(test_input)
        
        return test_inputs
    
    def calculate_confidence_scores(self, numbers):
        """
        Tính điểm tin cậy cho các số dự đoán
        Args:
            numbers: Danh sách các số dự đoán
        Returns:
            Dict chứa điểm tin cậy cho mỗi số
        """
        confidence_scores = {}
        
        for num in numbers:
            # Điểm cơ bản là 0.7
            base_confidence = 0.7
            
            # Tăng điểm nếu số này cũng được dự đoán bởi các phương pháp khác
            freq_bonus = 0.1 if num in self.predict_frequency()[:10] else 0
            recent_bonus = 0.1 if num in self.predict_recent()[:10] else 0
            
            # Tính điểm cuối cùng và chuẩn hóa về khoảng [0, 1]
            confidence_scores[num] = min(0.95, base_confidence + freq_bonus + recent_bonus)
        
        return confidence_scores
    
    def get_fallback_prediction(self, method_name):
        """
        Trả về dự đoán dự phòng khi phương pháp chính thất bại
        Args:
            method_name: Tên phương pháp đã thất bại
        Returns:
            Dict chứa dự đoán dự phòng
        """
        self.logger.info(f"Sử dụng dự đoán dự phòng cho {method_name}")
        
        # Lấy top 5 số từ phương pháp tần suất
        top_numbers = self.predict_frequency()[:5]
        
        return {
            'predicted_numbers': top_numbers,
            'confidence_scores': {num: 0.6 for num in top_numbers},  # Giảm độ tin cậy vì đây là dự phòng
            'is_fallback': True,  # Đánh dấu đây là dự đoán dự phòng
            'fallback_reason': f"{method_name} failed"
        }
    
    def train_lstm_model(self):
        """Huấn luyện mô hình LSTM cho dự đoán chuỗi thời gian"""
        try:
            # Kiểm tra cache
            cache_key = f"lstm_prediction_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            try:
                import tensorflow as tf
                from keras.models import Sequential
                from keras.layers import LSTM, Dense, Dropout
                import numpy as np
            except ImportError as e:
                self.logger.warning(f"Không thể tải thư viện cần thiết cho LSTM: {e}")
                return None
            
            # Chuẩn bị dữ liệu cho LSTM
            sequence_length = 10  # Độ dài chuỗi đầu vào
            X, y = [], []
            
            for i in range(len(self.historical_data) - sequence_length):
                # Lấy chuỗi kết quả liên tiếp
                sequence = []
                for j in range(i, i + sequence_length):
                    if hasattr(self.historical_data[j], 'giai_db') and self.historical_data[j].giai_db:
                        db = self.historical_data[j].giai_db[-2:] if len(self.historical_data[j].giai_db) >= 2 else "00"
                        sequence.append(int(db))
                    else:
                        sequence.append(0)
                
                # Đầu vào: chuỗi 10 ngày liên tiếp
                X.append(sequence)
                
                # Đầu ra: kết quả của ngày tiếp theo
                next_day = self.historical_data[i + sequence_length]
                if hasattr(next_day, 'giai_db') and next_day.giai_db and len(next_day.giai_db) >= 2:
                    y.append(int(next_day.giai_db[-2:]))
                else:
                    y.append(0)
            
            # Kiểm tra đủ dữ liệu
            if len(X) < 20 or len(y) < 20:
                self.logger.warning(f"Không đủ dữ liệu cho LSTM: X={len(X)}, y={len(y)}")
                return None
            
            # Chuyển thành mảng numpy và chuẩn hóa
            X = np.array(X) / 100.0  # Chuẩn hóa về khoảng [0, 1]
            y = np.array(y) / 100.0
            
            # Reshape cho LSTM: [samples, time steps, features]
            X = X.reshape(X.shape[0], X.shape[1], 1)
            
            # Tạo mô hình LSTM
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)),
                Dropout(0.2),
                LSTM(50),
                Dropout(0.2),
                Dense(1)
            ])
            
            # Biên dịch mô hình
            model.compile(optimizer='adam', loss='mse')
            
            # Huấn luyện mô hình
            model.fit(X, y, epochs=100, batch_size=32, verbose=0)
            
            # Dự đoán
            recent_sequence = []
            for i in range(sequence_length):
                idx = min(i, len(self.historical_data) - 1)
                if hasattr(self.historical_data[idx], 'giai_db') and self.historical_data[idx].giai_db:
                    db = self.historical_data[idx].giai_db[-2:] if len(self.historical_data[idx].giai_db) >= 2 else "00"
                    recent_sequence.append(int(db))
                else:
                    recent_sequence.append(0)
            
            # Chuẩn hóa và reshape
            recent_sequence = np.array(recent_sequence) / 100.0
            recent_sequence = recent_sequence.reshape(1, sequence_length, 1)
            
            # Dự đoán
            prediction = model.predict(recent_sequence)[0][0]
            
            # Chuyển về số 2 chữ số
            predicted_number = str(int(round(prediction * 100)) % 100).zfill(2)
            
            # Tạo một số biến thể bằng cách thêm/bớt 1
            variations = [
                str(int(predicted_number) % 100).zfill(2),
                str((int(predicted_number) + 1) % 100).zfill(2),
                str((int(predicted_number) - 1) % 100).zfill(2),
                str((int(predicted_number) + 10) % 100).zfill(2),
                str((int(predicted_number) - 10) % 100).zfill(2)
            ]
            
            # Loại bỏ trùng lặp
            result = list(set(variations))
            
            # Cache kết quả
            self.cache_result(cache_key, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Lỗi trong train_lstm_model: {e}", exc_info=True)
            return None
    
    def train_rl_agent(self):
        """Huấn luyện agent RL để lựa chọn số tối ưu"""
        try:
            # Kiểm tra cache
            cache_key = f"rl_prediction_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            try:
                import numpy as np
                from sklearn.preprocessing import StandardScaler
            except ImportError as e:
                self.logger.warning(f"Không thể tải thư viện cần thiết cho RL: {e}")
                return None
            
            # Tạo ma trận trạng thái-hành động (Q-matrix)
            Q = np.zeros((100, 100))  # 100 trạng thái x 100 hành động (số từ 00-99)
            
            # Tính toán phần thưởng dựa trên lịch sử
            for i in range(1, len(self.historical_data)):
                prev_day = self.historical_data[i]
                current_day = self.historical_data[i-1]
                
                if (hasattr(prev_day, 'giai_db') and prev_day.giai_db and
                    hasattr(current_day, 'giai_db') and current_day.giai_db):
                    prev_num = int(prev_day.giai_db[-2:]) if len(prev_day.giai_db) >= 2 else 0
                    current_num = int(current_day.giai_db[-2:]) if len(current_day.giai_db) >= 2 else 0
                    
                    # Tăng giá trị Q cho cặp (prev_num, current_num)
                    Q[prev_num, current_num] += 1
            
            # Chuẩn hóa ma trận Q
            row_sums = Q.sum(axis=1, keepdims=True)
            Q_norm = np.divide(Q, row_sums, out=np.zeros_like(Q), where=row_sums!=0)
            
            # Lấy số gần nhất từ lịch sử
            if self.historical_data and hasattr(self.historical_data[0], 'giai_db') and self.historical_data[0].giai_db:
                last_num = int(self.historical_data[0].giai_db[-2:]) if len(self.historical_data[0].giai_db) >= 2 else 0
                
                # Lấy các số có xác suất cao nhất từ ma trận Q
                best_actions = np.argsort(Q_norm[last_num])[::-1][:10]
                
                # Chuyển về định dạng chuẩn
                result = [f"{action:02d}" for action in best_actions]
                
                # Cache kết quả
                self.cache_result(cache_key, result)
                
                return result
            
            # Nếu không có dữ liệu, trả về rỗng
            return []
        except Exception as e:
            self.logger.error(f"Lỗi trong train_rl_agent: {e}", exc_info=True)
            return []
    
    def generate_27_predictions(self):
        """Tạo 27 số dự đoán với độ tin cậy cao bằng cách kết hợp nhiều phương pháp"""
        try:
            # Kiểm tra cache
            cache_key = f"generate_27_predictions_{self.target_date.strftime('%Y%m%d')}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            predictions = {}  # Dict để lưu số và điểm
            
            # 1. Dự đoán SHAP
            shap_pred = self.get_shap_prediction()
            if shap_pred and 'predicted_numbers' in shap_pred:
                for num in shap_pred['predicted_numbers']:
                    confidence = shap_pred['confidence_scores'].get(num, 0.7)
                    predictions[num] = predictions.get(num, 0) + confidence * 1.2  # Trọng số cao hơn cho SHAP
            
            # 2. Các phương pháp truyền thống
            traditional_methods = [
                (self.predict_frequency, 0.6),
                (self.predict_recent, 0.8),
                (self.predict_shadow, 0.7),
                (self.predict_region, 0.5),
                (self.predict_cycle, 0.7)
            ]
            
            for method, weight in traditional_methods:
                try:
                    method_predictions = method()
                    for num in method_predictions:
                        predictions[num] = predictions.get(num, 0) + weight
                except Exception as e:
                    self.logger.error(f"Lỗi trong phương pháp {method.__name__}: {e}")
            
            # 3. Phương pháp phân tích chu kỳ
            try:
                cycle_predictions = self.analyze_frequency_cycles()
                for num in cycle_predictions:
                    predictions[num] = predictions.get(num, 0) + 0.9  # Trọng số cao cho chu kỳ
            except Exception as e:
                self.logger.error(f"Lỗi trong analyze_frequency_cycles: {e}")
            
            # 4. Phân tích mối liên hệ giữa các số
            try:
                relationship_predictions = self.analyze_number_relationships()
                for num in relationship_predictions:
                    predictions[num] = predictions.get(num, 0) + 0.75
            except Exception as e:
                self.logger.error(f"Lỗi trong analyze_number_relationships: {e}")
            
            # 5. Phân tích ngược từ kết quả
            try:
                pattern_predictions = self.analyze_result_patterns()
                for num in pattern_predictions:
                    predictions[num] = predictions.get(num, 0) + 0.85
            except Exception as e:
                self.logger.error(f"Lỗi trong analyze_result_patterns: {e}")
            
            # 6. Bộ số liên quan
            try:
                related_predictions = self.analyze_related_number_sets()
                for num in related_predictions:
                    predictions[num] = predictions.get(num, 0) + 0.8
            except Exception as e:
                self.logger.error(f"Lỗi trong analyze_related_number_sets: {e}")
            
            # 7. Deep Learning (LSTM)
            try:
                lstm_predictions = self.train_lstm_model()
                if lstm_predictions:
                    for num in lstm_predictions:
                        predictions[num] = predictions.get(num, 0) + 1.0  # Trọng số cao cho LSTM
            except Exception as e:
                self.logger.error(f"Lỗi trong train_lstm_model: {e}")
            
            # 8. Reinforcement Learning
            try:
                rl_predictions = self.train_rl_agent()
                if rl_predictions:
                    for num in rl_predictions:
                        predictions[num] = predictions.get(num, 0) + 0.9
            except Exception as e:
                self.logger.error(f"Lỗi trong train_rl_agent: {e}")
            
            # 9. Phân tích phổ
            try:
                spectral_predictions = self.perform_spectral_analysis()
                if spectral_predictions:
                    for num in spectral_predictions:
                        predictions[num] = predictions.get(num, 0) + 0.85
            except Exception as e:
                self.logger.error(f"Lỗi trong perform_spectral_analysis: {e}")
            
            # 10. Phân tích đồ thị
            try:
                graph_predictions = self.perform_graph_analysis()
                if graph_predictions:
                    for num in graph_predictions:
                        predictions[num] = predictions.get(num, 0) + 0.8
            except Exception as e:
                self.logger.error(f"Lỗi trong perform_graph_analysis: {e}")
            
            # Sắp xếp theo điểm giảm dần
            sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
            
            # Lấy 27 số với điểm cao nhất
            top_27 = sorted_predictions[:27] if len(sorted_predictions) >= 27 else sorted_predictions
            
            # Cache kết quả
            self.cache_result(cache_key, top_27)
            
            return top_27
        except Exception as e:
            self.logger.error(f"Lỗi trong generate_27_predictions: {e}", exc_info=True)
            return []
    
    def apply_cyclical_adjustment(self, predictions, target_date):
        """
        Điều chỉnh dự đoán dựa trên chu kỳ hiệu suất
        Args:
            predictions: Dict chứa dự đoán của các phương pháp
            target_date: Ngày cần dự đoán
        Returns:
            Dict chứa dự đoán đã điều chỉnh
        """
        try:
            # Kiểm tra nếu có fatigue_analyzer
            if not hasattr(self, 'fatigue_analyzer') or not self.fatigue_analyzer:
                # Sử dụng trọng số đã tính sẵn
                adjusted_weights = self.calculate_method_weights()
                return {
                    'predictions': predictions,
                    'method_weights': adjusted_weights
                }
            
            # Phân tích chu kỳ hiệu suất
            recommendations = self.fatigue_analyzer.recommend_methods_for_date(target_date)
            
            # Tạo dict trọng số từ recommendations
            weights = {rec['method']: rec['normalized_weight'] for rec in recommendations['recommendations']}
            
            # Áp dụng trọng số mới cho các phương pháp
            adjusted_predictions = {}
            for method, numbers in predictions.items():
                # Chuyển đổi tên phương pháp nếu cần
                method_key = self._convert_method_name(method)
                
                # Lưu dự đoán với trọng số mới
                adjusted_predictions[method] = numbers
            
            # Cập nhật trọng số mới
            adjusted_weights = self.calculate_method_weights()
            for method in adjusted_weights:
                method_key = self._convert_method_name(method)
                if method_key in weights:
                    adjusted_weights[method] = weights[method_key]
            
            return {
                'predictions': adjusted_predictions,
                'method_weights': adjusted_weights,
                'cyclical_analysis': recommendations
            }
        except Exception as e:
            self.logger.error(f"Lỗi trong apply_cyclical_adjustment: {e}", exc_info=True)
            
            # Trả về dự đoán gốc nếu có lỗi
            adjusted_weights = self.calculate_method_weights()
            return {
                'predictions': predictions,
                'method_weights': adjusted_weights
            }
    
    def _convert_method_name(self, method_name):
        """Chuyển đổi tên phương pháp giữa các định dạng khác nhau"""
        # Map giữa tên phương pháp trong predictor và tên trong analyzer
        method_map = {
            'lap_lai_gan_nhat': 'predict_recent',
            'tan_so_cao': 'predict_frequency',
            'bong_so': 'predict_shadow',
            'khu_vuc': 'predict_region',
            'chu_ky': 'predict_cycle'
        }
        
        # Chuyển đổi từ tên trong predictor sang tên trong analyzer
        return method_map.get(method_name, method_name)
    
    def get_optimal_weights(self):
        """Lấy trọng số tối ưu từ DB"""
        try:
            from results.models import OptimizedWeights
            
            # Lấy bản ghi trọng số mới nhất
            latest_weights = OptimizedWeights.objects.order_by('-calculation_date').first()
            if latest_weights:
                return latest_weights.weights
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy trọng số tối ưu: {e}")
        
        
    
    def calculate_method_weights(self):
        """
        Tính trọng số cho các phương pháp
        Returns:
            Dict chứa trọng số của từng phương pháp
        """
        # Thử lấy trọng số tối ưu từ DB hoặc cache
        if hasattr(self, '_method_weights') and self._method_weights:
            return self._method_weights
        
        optimal_weights = self.get_optimal_weights()
        
        # Nếu có trọng số tối ưu, sử dụng nó
        if optimal_weights:
            # Kiểm tra đảm bảo tất cả phương pháp cần thiết đều có trong optimal_weights
            default_weights = {
                'lap_lai_gan_nhat': 0.8,
                'tan_so_cao': 0.6,
                'bong_so': 0.7,
                'khu_vuc': 0.5,
                'chu_ky': 0.7
            }
            
            # Kết hợp với trọng số mặc định để đảm bảo không thiếu phương pháp
            for method in default_weights:
                if method not in optimal_weights:
                    optimal_weights[method] = default_weights[method]
            
            # Cache trọng số cho sử dụng sau
            self._method_weights = optimal_weights
            
            return optimal_weights
        
        # Trọng số mặc định nếu không có trọng số tối ưu
        default_weights = {
            'lap_lai_gan_nhat': 0.8,
            'tan_so_cao': 0.6,
            'bong_so': 0.7,
            'khu_vuc': 0.5,
            'chu_ky': 0.7
        }
        
        # Cache trọng số cho sử dụng sau
        self._method_weights = default_weights
        
        return default_weights
    
    def calculate_combined_numbers(self, predictions, method_weights):
        """
        Tính kết quả kết hợp từ các phương pháp
        Args:
            predictions: Dict chứa kết quả dự đoán của từng phương pháp
            method_weights: Dict chứa trọng số của từng phương pháp
        Returns:
            List các cặp (số, điểm) được sắp xếp theo điểm giảm dần
        """
        from collections import defaultdict
        
        # Tính điểm cho mỗi số
        number_scores = defaultdict(float)
        for method, numbers in predictions.items():
            weight = method_weights.get(method, 0.5)
            for num in numbers:
                number_scores[num] += weight
        
        # Sắp xếp theo điểm giảm dần
        sorted_numbers = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Lấy top 10 số
        return sorted_numbers[:10]
    
    def evaluate_method_performance(self, date_range=30):
        """
        Đánh giá hiệu suất của các phương pháp dự đoán trong khoảng thời gian
        Args:
            date_range: Số ngày để đánh giá (mặc định 30 ngày)
        Returns:
            Dict chứa thông tin hiệu suất của từng phương pháp
        """
        try:
            from django.utils import timezone
            from datetime import timedelta
            from results.models import KetQuaXoSo, PredictionStatistic
            
            end_date = self.target_date - timedelta(days=1)
            start_date = end_date - timedelta(days=date_range)
            
            # Lấy kết quả xổ số trong khoảng thời gian
            results = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by('ngay')
            
            # Lấy thống kê dự đoán đã lưu
            statistics = PredictionStatistic.objects.filter(
                date__range=(start_date, end_date)
            ).order_by('date')
            
            # Nếu không có đủ dữ liệu thống kê, tạo thống kê mới
            if len(statistics) < len(results) * 0.8:  # Yêu cầu ít nhất 80% ngày có thống kê
                self.logger.info(f"Không đủ dữ liệu thống kê, tạo mới...")
                self.generate_historical_statistics(start_date, end_date)
                
                # Lấy lại thống kê sau khi tạo
                statistics = PredictionStatistic.objects.filter(
                    date__range=(start_date, end_date)
                ).order_by('date')
            
            # Phân tích hiệu suất
            performance = {}
            
            # Gom nhóm thống kê theo phương pháp
            method_stats = {}
            for stat in statistics:
                if stat.method not in method_stats:
                    method_stats[stat.method] = []
                method_stats[stat.method].append(stat)
            
            # Tính hiệu suất cho từng phương pháp
            for method, stats in method_stats.items():
                total_predicted = sum(stat.total_predicted for stat in stats)
                total_hit = sum(stat.total_hit for stat in stats)
                
                if total_predicted > 0:
                    accuracy = (total_hit / total_predicted) * 100
                else:
                    accuracy = 0
                    
                # Phân tích xu hướng
                trend = self.analyze_performance_trend(stats)
                
                performance[method] = {
                    'total_days': len(stats),
                    'total_predicted': total_predicted,
                    'total_hit': total_hit,
                    'accuracy': accuracy,
                    'trend': trend
                }
            
            # Cache kết quả hiệu suất cho sử dụng sau
            self._method_performance = performance
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Lỗi khi đánh giá hiệu suất: {e}", exc_info=True)
            return {}
    
    def analyze_performance_trend(self, statistics):
        """
        Phân tích xu hướng hiệu suất dựa trên thống kê
        Args:
            statistics: Danh sách các thống kê dự đoán
        Returns:
            Dict chứa thông tin xu hướng
        """
        if not statistics or len(statistics) < 7:
            return {'direction': 'unknown', 'strength': 0}
        
        # Sắp xếp theo ngày
        sorted_stats = sorted(statistics, key=lambda x: x.date)
        
        # Tính độ chính xác theo ngày
        daily_accuracy = []
        for stat in sorted_stats:
            if stat.total_predicted > 0:
                daily_accuracy.append(stat.total_hit / stat.total_predicted)
            else:
                daily_accuracy.append(0)
        
        # Tính xu hướng (đơn giản là so sánh nửa đầu và nửa sau)
        mid_point = len(daily_accuracy) // 2
        first_half_avg = sum(daily_accuracy[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(daily_accuracy[mid_point:]) / (len(daily_accuracy) - mid_point) if len(daily_accuracy) > mid_point else 0
        
        diff = second_half_avg - first_half_avg
        
        # Xác định hướng và độ mạnh của xu hướng
        if diff > 0.05:
            direction = 'up'
            strength = min(1.0, diff * 5)  # Chuẩn hóa về khoảng [0, 1]
        elif diff < -0.05:
            direction = 'down'
            strength = min(1.0, abs(diff) * 5)
        else:
            direction = 'stable'
            strength = 0
        
        return {
            'direction': direction,
            'strength': strength,
            'first_half_avg': first_half_avg,
            'second_half_avg': second_half_avg,
            'diff': diff
        }
    
    def generate_historical_statistics(self, start_date, end_date):
        """
        Tạo thống kê lịch sử cho khoảng thời gian đã chỉ định
        Args:
            start_date: Ngày bắt đầu
            end_date: Ngày kết thúc
        """
        try:
            from results.models import KetQuaXoSo, PredictionStatistic
            
            # Lấy kết quả xổ số trong khoảng thời gian
            results = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by('ngay')
            
            # Tạo thống kê cho từng ngày
            for result in results:
                # Tạo predictor mới cho ngày này
                predictor = BachThuLoPredictor(
                    target_date=result.ngay,
                    history_days=self.history_days
                )
                
                # Lấy dự đoán cho ngày này
                prediction = predictor.predict()
                
                if not prediction:
                    continue
                
                # Lấy kết quả thực tế
                actual_numbers = result.get_all_2digit_numbers() if hasattr(result, 'get_all_2digit_numbers') else []
                
                # Tính toán độ chính xác cho từng phương pháp
                for method, numbers in prediction['predictions'].items():
                    # Đếm số lượng trúng
                    hit_count = sum(1 for num in numbers if num in actual_numbers)
                    
                    # Tạo hoặc cập nhật thống kê
                    PredictionStatistic.objects.update_or_create(
                        date=result.ngay,
                        method=method,
                        defaults={
                            'total_predicted': len(numbers),
                            'total_hit': hit_count,
                            'accuracy': (hit_count / len(numbers) * 100) if numbers else 0
                        }
                    )
            
            self.logger.info(f"Đã tạo thống kê lịch sử từ {start_date} đến {end_date}")
            
        except Exception as e:
            self.logger.error(f"Lỗi khi tạo thống kê lịch sử: {e}", exc_info=True)
    
    def cache_result(self, key, data):
        """
        Lưu kết quả vào cache
        Args:
            key: Khóa cache
            data: Dữ liệu cần lưu
        """
        try:
            import pickle
            import os
            
            # Tạo thư mục cache nếu chưa tồn tại
            cache_dir = os.path.join("cache", "predictions")
            os.makedirs(cache_dir, exist_ok=True)
            
            # Lưu dữ liệu
            cache_path = os.path.join(cache_dir, f"{key}.pkl")
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
                
            self.logger.debug(f"Đã lưu kết quả vào cache: {key}")
            
            # Lưu vào bộ nhớ
            self._cache[key] = data
            
            return True
        except Exception as e:
            self.logger.warning(f"Không thể lưu vào cache: {e}")
            return False
    
    def get_cached_result(self, key):
        """
        Lấy kết quả từ cache
        Args:
            key: Khóa cache
        Returns:
            Dữ liệu từ cache hoặc None nếu không tìm thấy
        """
        # Kiểm tra trong bộ nhớ trước
        if key in self._cache:
            return self._cache[key]
            
        try:
            import pickle
            import os
            import time
            
            cache_path = os.path.join("cache", "predictions", f"{key}.pkl")
            
            if not os.path.exists(cache_path):
                return None
                
            # Kiểm tra thời gian tạo file
            file_age = time.time() - os.path.getmtime(cache_path)
            if file_age > 86400:  # 24 giờ
                self.logger.debug(f"Cache quá hạn: {key}")
                return None
                
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
                
            self.logger.debug(f"Đã lấy kết quả từ cache: {key}")
            
            # Lưu vào bộ nhớ
            self._cache[key] = data
            
            return data
        except Exception as e:
            self.logger.warning(f"Không thể đọc từ cache: {e}")
            return None
        
# Add this HybridPredictor class to your existing predictors.py file

import logging
from collections import defaultdict
from datetime import date, timedelta
from itertools import combinations
import numpy as np
from django.db.models import Q, Avg
from django.utils import timezone

# Import your existing models
from ..models import KetQuaXoSo, CycleAccuracy, PredictionRecord, PredictionModel

logger = logging.getLogger(__name__)

class HybridPredictor:
    """
    Hybrid predictor kết hợp nhiều phương pháp dự đoán cho xổ số
    Trả về dict rõ ràng theo quy tắc phát triển
    """
    
    def __init__(self, target_date=None):
        self.target_date = target_date or timezone.now().date()
        self.cycle_weights = self.load_dynamic_weights()
        self.model_name = "HybridPredictor"
        self.version = "1.0"
        
        # Initialize prediction data storage
        self.prediction_data = {
            'cycle_predictions': {},
            'frequency_analysis': {},
            'gap_analysis': {},
            'final_predictions': []
        }
        
        logger.info(f"HybridPredictor initialized for date: {self.target_date}")
    
    def load_dynamic_weights(self) -> dict:
        """
        Tải trọng số động từ database hoặc sử dụng mặc định
        Trả về: dict với key là cycle_type và value là trọng số
        """
        default_weights = {
            '1_ngay': 0.35,
            '3_ngay': 0.25,
            '7_ngay': 0.20,
            '14_ngay': 0.15,
            '30_ngay': 0.05
        }
        
        try:
            # Lấy từ database nếu có
            cycle_accuracies = CycleAccuracy.objects.all()
            if cycle_accuracies.exists():
                total_accuracy = sum(c.accuracy for c in cycle_accuracies)
                if total_accuracy > 0:
                    weights = {}
                    for cycle in cycle_accuracies:
                        weights[cycle.cycle_type] = cycle.accuracy / total_accuracy
                    return weights
            
            return default_weights
            
        except Exception as e:
            logger.warning(f"Could not load dynamic weights: {e}, using defaults")
            return default_weights
    
    def get_historical_data(self, days=90) -> list:
        """
        Lấy dữ liệu lịch sử
        Trả về: list các dict chứa thông tin kết quả xổ số
        """
        try:
            end_date = self.target_date - timedelta(days=1)
            start_date = end_date - timedelta(days=days)
            
            results = KetQuaXoSo.objects.filter(
                ngay__range=[start_date, end_date]
            ).order_by('ngay')
            
            historical_data = []
            for result in results:
                # Lấy tất cả số 2 chữ số từ kết quả
                numbers = result.get_all_2digit_numbers() if hasattr(result, 'get_all_2digit_numbers') else []
                historical_data.append({
                    'date': result.ngay,
                    'numbers': numbers,
                    'giai_db': result.giai_db,
                    'giai_nhat': result.giai_nhat
                })
            
            logger.info(f"Retrieved {len(historical_data)} historical records")
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []
    
    def analyze_cycles(self, history_data: list) -> dict:
        """
        Phân tích chu kỳ xuất hiện của các số
        Trả về: dict chứa thông tin phân tích chu kỳ
        """
        if not history_data:
            return {'predictions': [], 'confidence': 0.0}
        
        try:
            # Phân tích chu kỳ cho từng loại
            cycle_results = {}
            
            for cycle_type, weight in self.cycle_weights.items():
                cycle_days = int(cycle_type.split('_')[0])
                cycle_predictions = self._analyze_single_cycle(history_data, cycle_days)
                
                cycle_results[cycle_type] = {
                    'predictions': cycle_predictions,
                    'weight': weight,
                    'cycle_days': cycle_days
                }
            
            # Kết hợp các dự đoán chu kỳ
            combined_predictions = self._combine_cycle_predictions(cycle_results)
            
            return {
                'cycle_results': cycle_results,
                'combined_predictions': combined_predictions,
                'confidence': self._calculate_cycle_confidence(cycle_results)
            }
            
        except Exception as e:
            logger.error(f"Error in cycle analysis: {e}")
            return {'predictions': [], 'confidence': 0.0}
    
    def _analyze_single_cycle(self, history_data: list, cycle_days: int) -> list:
        """
        Phân tích chu kỳ cho một khoảng thời gian cụ thể
        """
        try:
            if len(history_data) < cycle_days:
                return []
            
            # Lấy dữ liệu trong chu kỳ
            recent_data = history_data[-cycle_days:]
            number_frequency = defaultdict(int)
            
            for record in recent_data:
                for number in record.get('numbers', []):
                    number_frequency[number] += 1
            
            # Sắp xếp theo tần suất
            sorted_numbers = sorted(
                number_frequency.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Trả về top 10 số có tần suất cao nhất
            return [{'number': num, 'frequency': freq} for num, freq in sorted_numbers[:10]]
            
        except Exception as e:
            logger.error(f"Error in single cycle analysis: {e}")
            return []
    
    def _combine_cycle_predictions(self, cycle_results: dict) -> list:
        """
        Kết hợp các dự đoán từ các chu kỳ khác nhau
        """
        try:
            combined_scores = defaultdict(float)
            
            for cycle_type, result in cycle_results.items():
                weight = result['weight']
                predictions = result['predictions']
                
                for pred in predictions:
                    number = pred['number']
                    frequency = pred['frequency']
                    combined_scores[number] += frequency * weight
            
            # Sắp xếp theo điểm số tổng hợp
            sorted_predictions = sorted(
                combined_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return [
                {'number': num, 'score': score, 'confidence': min(score/10, 1.0)}
                for num, score in sorted_predictions[:20]
            ]
            
        except Exception as e:
            logger.error(f"Error combining cycle predictions: {e}")
            return []
    
    def _calculate_cycle_confidence(self, cycle_results: dict) -> float:
        """
        Tính toán độ tin cậy của dự đoán chu kỳ
        """
        try:
            total_weight = sum(result['weight'] for result in cycle_results.values())
            total_predictions = sum(len(result['predictions']) for result in cycle_results.values())
            
            if total_predictions == 0:
                return 0.0
            
            # Tính confidence dựa trên số lượng dự đoán và trọng số
            confidence = min(total_weight * (total_predictions / 50), 1.0)
            return round(confidence, 3)
            
        except Exception as e:
            logger.error(f"Error calculating cycle confidence: {e}")
            return 0.0
    
    def predict(self) -> dict:
        """
        Thực hiện dự đoán chính
        Trả về: dict chứa kết quả dự đoán đầy đủ
        """
        try:
            logger.info(f"Starting prediction for {self.target_date}")
            
            # 1. Lấy dữ liệu lịch sử
            history_data = self.get_historical_data()
            if not history_data:
                return self._empty_prediction_result("No historical data available")
            
            # 2. Phân tích chu kỳ
            cycle_analysis = self.analyze_cycles(history_data)
            
            # 3. Phân tích tần suất
            frequency_analysis = self._analyze_frequency(history_data)
            
            # 4. Phân tích khoảng cách
            gap_analysis = self._analyze_gaps(history_data)
            
            # 5. Kết hợp tất cả phương pháp
            final_predictions = self._combine_all_methods(
                cycle_analysis, frequency_analysis, gap_analysis
            )
            
            # 6. Tạo kết quả cuối cùng
            result = {
                'target_date': self.target_date.strftime('%Y-%m-%d'),
                'model_name': self.model_name,
                'version': self.version,
                'cycle_analysis': cycle_analysis,
                'frequency_analysis': frequency_analysis,
                'gap_analysis': gap_analysis,
                'final_predictions': final_predictions,
                'prediction_count': len(final_predictions),
                'overall_confidence': self._calculate_overall_confidence(
                    cycle_analysis, frequency_analysis, gap_analysis
                ),
                'generated_at': timezone.now().isoformat()
            }
            
            logger.info(f"Prediction completed successfully for {self.target_date}")
            return result
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return self._empty_prediction_result(f"Prediction error: {str(e)}")
    
    def _analyze_frequency(self, history_data: list) -> dict:
        """
        Phân tích tần suất xuất hiện
        """
        try:
            number_frequency = defaultdict(int)
            total_draws = len(history_data)
            
            for record in history_data:
                for number in record.get('numbers', []):
                    number_frequency[number] += 1
            
            # Tính tỷ lệ phần trăm
            frequency_analysis = []
            for number, count in number_frequency.items():
                percentage = (count / total_draws) * 100 if total_draws > 0 else 0
                frequency_analysis.append({
                    'number': number,
                    'count': count,
                    'percentage': round(percentage, 2)
                })
            
            # Sắp xếp theo tần suất
            frequency_analysis.sort(key=lambda x: x['count'], reverse=True)
            
            return {
                'analysis': frequency_analysis[:20],
                'total_draws': total_draws,
                'confidence': min(total_draws / 100, 1.0)
            }
            
        except Exception as e:
            logger.error(f"Error in frequency analysis: {e}")
            return {'analysis': [], 'total_draws': 0, 'confidence': 0.0}
    
    def _analyze_gaps(self, history_data: list) -> dict:
        """
        Phân tích khoảng cách giữa các lần xuất hiện
        """
        try:
            number_positions = defaultdict(list)
            
            # Ghi lại vị trí xuất hiện của mỗi số
            for i, record in enumerate(history_data):
                for number in record.get('numbers', []):
                    number_positions[number].append(i)
            
            gap_analysis = []
            for number, positions in number_positions.items():
                if len(positions) >= 2:
                    gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
                    avg_gap = sum(gaps) / len(gaps)
                    last_position = positions[-1]
                    current_gap = len(history_data) - 1 - last_position
                    
                    gap_analysis.append({
                        'number': number,
                        'avg_gap': round(avg_gap, 2),
                        'current_gap': current_gap,
                        'gap_ratio': round(current_gap / avg_gap, 2) if avg_gap > 0 else 0,
                        'prediction_strength': max(0, min(1, (current_gap / avg_gap - 0.5) * 2)) if avg_gap > 0 else 0
                    })
            
            # Sắp xếp theo strength
            gap_analysis.sort(key=lambda x: x['prediction_strength'], reverse=True)
            
            return {
                'analysis': gap_analysis[:15],
                'confidence': 0.7  # Fixed confidence for gap analysis
            }
            
        except Exception as e:
            logger.error(f"Error in gap analysis: {e}")
            return {'analysis': [], 'confidence': 0.0}
    
    def _combine_all_methods(self, cycle_analysis: dict, frequency_analysis: dict, gap_analysis: dict) -> list:
        """
        Kết hợp tất cả các phương pháp phân tích
        """
        try:
            combined_scores = defaultdict(float)
            
            # Trọng số cho từng phương pháp
            weights = {
                'cycle': 0.4,
                'frequency': 0.35,
                'gap': 0.25
            }
            
            # Kết hợp cycle analysis
            for pred in cycle_analysis.get('combined_predictions', []):
                number = pred['number']
                score = pred['score']
                combined_scores[number] += score * weights['cycle']
            
            # Kết hợp frequency analysis
            for pred in frequency_analysis.get('analysis', [])[:15]:
                number = pred['number']
                score = pred['percentage'] / 100  # Normalize to 0-1
                combined_scores[number] += score * weights['frequency']
            
            # Kết hợp gap analysis
            for pred in gap_analysis.get('analysis', []):
                number = pred['number']
                score = pred['prediction_strength']
                combined_scores[number] += score * weights['gap']
            
            # Sắp xếp và tạo kết quả cuối cùng
            sorted_predictions = sorted(
                combined_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            final_predictions = []
            for i, (number, score) in enumerate(sorted_predictions[:15]):
                final_predictions.append({
                    'rank': i + 1,
                    'number': number,
                    'combined_score': round(score, 4),
                    'confidence': min(score, 1.0),
                    'recommendation': 'high' if score > 0.7 else 'medium' if score > 0.4 else 'low'
                })
            
            return final_predictions
            
        except Exception as e:
            logger.error(f"Error combining methods: {e}")
            return []
    
    def _calculate_overall_confidence(self, cycle_analysis: dict, frequency_analysis: dict, gap_analysis: dict) -> float:
        """
        Tính toán độ tin cậy tổng thể
        """
        try:
            confidences = [
                cycle_analysis.get('confidence', 0),
                frequency_analysis.get('confidence', 0),
                gap_analysis.get('confidence', 0)
            ]
            
            overall_confidence = sum(confidences) / len(confidences)
            return round(overall_confidence, 3)
            
        except Exception as e:
            logger.error(f"Error calculating overall confidence: {e}")
            return 0.0
    
    def _empty_prediction_result(self, reason: str) -> dict:
        """
        Trả về kết quả rỗng khi có lỗi
        """
        return {
            'target_date': self.target_date.strftime('%Y-%m-%d'),
            'model_name': self.model_name,
            'version': self.version,
            'error': reason,
            'cycle_analysis': {'predictions': [], 'confidence': 0.0},
            'frequency_analysis': {'analysis': [], 'confidence': 0.0},
            'gap_analysis': {'analysis': [], 'confidence': 0.0},
            'final_predictions': [],
            'prediction_count': 0,
            'overall_confidence': 0.0,
            'generated_at': timezone.now().isoformat()
        }
    
    def get_all_2digit_numbers(self) -> list:
        """
        Trả về tất cả số 2 chữ số có thể (00-99)
        """
        return [f"{i:02d}" for i in range(100)]

# Thêm vào cuối file predictors.py