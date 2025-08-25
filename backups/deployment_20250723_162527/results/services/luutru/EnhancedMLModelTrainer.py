import os
import pickle
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from django.utils import timezone
from django.core.cache import cache
from results.models import KetQuaXoSo, PredictionPerformanceMetrics
import joblib

logger = logging.getLogger(__name__)

class EnhancedMLModelTrainer:
    """
    Enhanced ML Model Trainer với nhiều algorithms và tự động tối ưu parameters
    """
    
    def __init__(self):
        self.models_dir = 'data/predictor_models'
        self.performance_history_file = os.path.join(self.models_dir, 'performance_history.pkl')
        self.retrain_threshold = 0.15  # Retrain khi accuracy giảm > 15%
        self.min_training_data = 180  # Tối thiểu 180 ngày data
        
        # Model configurations
        self.model_configs = {
            'random_forest': {
                'model': RandomForestRegressor,
                'params': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                },
                'best_params': None
            },
            'gradient_boosting': {
                'model': GradientBoostingRegressor,
                'params': {
                    'n_estimators': [100, 200],
                    'learning_rate': [0.05, 0.1, 0.15],
                    'max_depth': [3, 5, 7],
                    'subsample': [0.8, 0.9, 1.0]
                },
                'best_params': None
            },
            'extra_trees': {
                'model': ExtraTreesRegressor,
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]
                },
                'best_params': None
            },
            'ridge': {
                'model': Ridge,
                'params': {
                    'alpha': [0.1, 1.0, 10.0, 100.0],
                    'solver': ['auto', 'saga']
                },
                'best_params': None
            }
        }
        
        self.feature_names = [
            'number_value', 'days_since_last_appearance', 'frequency_last_30days',
            'frequency_last_7days', 'weekday_frequency', 'month_frequency',
            'position_in_prize', 'pair_frequency', 'sum_digit_frequency',
            'hot_cold_index', 'trend_factor', 'cycle_position'
        ]
        
        self._ensure_models_dir()
        
    def _ensure_models_dir(self):
        """Tạo thư mục models nếu chưa tồn tại"""
        os.makedirs(self.models_dir, exist_ok=True)
        
    def should_retrain_models(self):
        """
        Quyết định có nên retrain models hay không dựa trên:
        1. Tuổi của models (file timestamp)
        2. Performance thực tế từ prediction results
        3. Có models hiện tại hay không
        """
        try:
            # 1. Kiểm tra xem có models hiện tại không
            if not self._has_trained_models():
                logger.info("No trained models found, triggering retrain")
                return True
            
            # 2. Kiểm tra tuổi của models dựa trên file timestamp
            model_age_days = self._get_model_age()
            max_model_age = 7  # Retrain sau 7 ngày
            
            if model_age_days >= max_model_age:
                logger.info(f"Models are {model_age_days} days old (max: {max_model_age}), triggering retrain")
                return True
            
            # 3. Kiểm tra performance của models từ actual usage
            # Sử dụng data từ việc sử dụng thực tế models, không phải training metrics
            recent_performance = self._get_actual_model_performance()
            
            if recent_performance and recent_performance < 0.3:  # Threshold 30%
                logger.info(f"Model performance dropped to {recent_performance:.3f}, triggering retrain")
                return True
            
            # 4. Kiểm tra xem có đủ data mới để retrain không
            new_data_count = self._count_new_training_data()
            if new_data_count > 50:  # Có 50+ kết quả mới
                logger.info(f"Found {new_data_count} new training samples, triggering retrain")
                return True
            
            logger.info(f"Models are up to date (age: {model_age_days} days, performance: {recent_performance or 'N/A'})")
            return False
            
        except Exception as e:
            logger.error(f"Error checking retrain condition: {e}")
            return True  # Conservative: retrain khi có lỗi
    def _has_trained_models(self):
        """Kiểm tra xem có models đã train hay không"""
        try:
            model_files = [f for f in os.listdir(self.models_dir) 
                          if f.endswith('.pkl') and not f.startswith('performance')]
            return len(model_files) > 0
        except:
            return False

    def _count_new_training_data(self):
        """Đếm số lượng data mới kể từ lần train cuối"""
        try:
            last_train_date = self._get_last_training_date()
            if not last_train_date:
                return 999  # Nhiều data mới nếu chưa có train date
                
            new_results = KetQuaXoSo.objects.filter(
                ngay__gt=last_train_date
            ).count()
            
            return new_results
            
        except Exception as e:
            logger.error(f"Error counting new training data: {e}")
            return 0

    def _get_last_training_date(self):
        """Lấy ngày train cuối cùng từ file timestamp hoặc training history"""
        try:
            # Method 1: From file timestamp
            model_files = [f for f in os.listdir(self.models_dir) 
                          if f.endswith('.pkl') and not f.startswith('performance')]
            
            if model_files:
                # Get newest model file
                newest_file = max(model_files, key=lambda f: os.path.getctime(
                    os.path.join(self.models_dir, f)
                ))
                
                file_time = datetime.fromtimestamp(
                    os.path.getctime(os.path.join(self.models_dir, newest_file))
                )
                
                return file_time.date()
            
            # Method 2: From training history file
            if os.path.exists(self.performance_history_file):
                with open(self.performance_history_file, 'rb') as f:
                    history = pickle.load(f)
                    if history:
                        last_entry = history[-1]
                        return last_entry['timestamp'].date()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting last training date: {e}")
            return None
    def train_all_models(self, force_retrain=False):
        """
        Huấn luyện tất cả models với tự động tối ưu parameters
        """
        try:
            if not force_retrain and not self.should_retrain_models():
                logger.info("Models are up to date, skipping retrain")
                return self._load_existing_models()
            
            # Chuẩn bị training data
            X, y = self._prepare_comprehensive_training_data()
            
            if X is None or len(X) < self.min_training_data:
                logger.error(f"Insufficient training data: {len(X) if X is not None else 0}")
                return False
            
            logger.info(f"Training models with {len(X)} samples and {X.shape[1]} features")
            
            # Split data với time series approach
            split_point = int(len(X) * 0.8)
            X_train, X_test = X[:split_point], X[split_point:]
            y_train, y_test = y[:split_point], y[split_point:]
            
            trained_models = {}
            performance_results = {}
            
            # Huấn luyện từng model
            for model_name, config in self.model_configs.items():
                logger.info(f"Training {model_name}...")
                
                model, performance = self._train_single_model(
                    model_name, config, X_train, y_train, X_test, y_test
                )
                
                if model:
                    trained_models[model_name] = model
                    performance_results[model_name] = performance
                    
                    # Lưu model
                    self._save_model(model_name, model)
            
            # Lưu performance history
            self._save_performance_history(performance_results)
            
            # ** QUAN TRỌNG: Cập nhật training record để tránh retrain liên tục **
            self._update_training_record(performance_results)
            
            # Chọn best model
            best_model_name = self._select_best_model(performance_results)
            logger.info(f"Best performing model: {best_model_name}")
            
            return len(trained_models) > 0
            
        except Exception as e:
            logger.error(f"Error training models: {e}", exc_info=True)
            return False

    def _update_training_record(self, performance_results):
        """Cập nhật record về việc training để tránh retrain liên tục"""
        try:
            # Tạo file marker với timestamp
            training_record_file = os.path.join(self.models_dir, 'last_training_info.json')
            
            training_info = {
                'timestamp': timezone.now().isoformat(),
                'date': timezone.now().date().isoformat(),
                'models_trained': list(performance_results.keys()),
                'best_model': self._select_best_model(performance_results),
                'performance_summary': {
                    model: {
                        'r2_score': perf['r2_score'],
                        'mse': perf['mse']
                    } for model, perf in performance_results.items()
                },
                'training_data_count': self._get_training_data_count()
            }
            
            with open(training_record_file, 'w') as f:
                import json
                json.dump(training_info, f, indent=2, default=str)
                
            logger.info(f"Updated training record: {training_record_file}")
            
        except Exception as e:
            logger.error(f"Error updating training record: {e}")

    def _get_training_data_count(self):
        """Lấy số lượng data đã dùng để training"""
        try:
            historical_data = KetQuaXoSo.objects.count()
            return historical_data
        except:
            return 0

    def _get_actual_model_performance(self):
        """
        Lấy performance thực tế từ việc sử dụng models
        Tính từ kết quả dự đoán gần đây vs kết quả thực tế
        """
        try:
            from results.models import DailyPredictionAnalysis
            
            # Lấy các prediction trong 7 ngày gần đây có kết quả thực tế
            recent_predictions = DailyPredictionAnalysis.objects.filter(
                analysis_date__gte=timezone.now().date() - timedelta(days=7),
                # Sửa: Sử dụng field đúng thay vì has_actual_results
                actual_numbers__isnull=False  # Có actual_numbers
            ).exclude(
                predictions_data__isnull=True
            )
            
            if not recent_predictions:
                return None
                
            total_predictions = 0
            correct_predictions = 0
            
            for pred_analysis in recent_predictions:
                if hasattr(pred_analysis, 'predictions_data') and pred_analysis.predictions_data:
                    # Parse predictions data
                    try:
                        import json
                        if isinstance(pred_analysis.predictions_data, str):
                            preds_data = json.loads(pred_analysis.predictions_data)
                        else:
                            preds_data = pred_analysis.predictions_data
                        
                        # Get ML predictions specifically
                        ml_preds = preds_data.get('ml', {}).get('numbers', [])
                        
                        # Get actual results
                        if hasattr(pred_analysis, 'actual_numbers') and pred_analysis.actual_numbers:
                            actual_numbers = pred_analysis.actual_numbers
                            if isinstance(actual_numbers, str):
                                actual_numbers = json.loads(actual_numbers)
                            
                            # Check top 10 ML predictions
                            for pred_number in ml_preds[:10]:
                                total_predictions += 1
                                if str(pred_number).zfill(2) in [str(n).zfill(2) for n in actual_numbers]:
                                    correct_predictions += 1
                                    
                    except Exception as e:
                        logger.warning(f"Error parsing prediction data: {e}")
                        continue
            
            if total_predictions > 0:
                performance = correct_predictions / total_predictions
                logger.info(f"Actual model performance: {correct_predictions}/{total_predictions} = {performance:.3f}")
                return performance
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting actual model performance: {e}")
            return None                        
           
    def _get_baseline_accuracy(self):
        """
        Lấy baseline accuracy từ performance history
        """
        try:
            # Lấy accuracy trung bình từ 30 ngày trước
            baseline_metrics = PredictionPerformanceMetrics.objects.filter(
                analysis_date__gte=timezone.now().date() - timedelta(days=60),
                analysis_date__lt=timezone.now().date() - timedelta(days=30)
            )
            
            if not baseline_metrics:
                return None
                
            return sum(m.hit_rate for m in baseline_metrics) / len(baseline_metrics)
            
        except Exception as e:
            logger.error(f"Error getting baseline accuracy: {e}")
            return None
    
    def _get_model_age(self):
        """
        Tính tuổi của models hiện tại
        """
        try:
            model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.pkl')]
            if not model_files:
                return 999  # Very old if no models exist
                
            # Tìm file mới nhất
            latest_file = max(model_files, key=lambda f: os.path.getctime(
                os.path.join(self.models_dir, f)
            ))
            
            file_time = datetime.fromtimestamp(
                os.path.getctime(os.path.join(self.models_dir, latest_file))
            )
            
            return (datetime.now() - file_time).days
            
        except Exception as e:
            logger.error(f"Error getting model age: {e}")
            return 999
    
    
    def _train_single_model(self, model_name, config, X_train, y_train, X_test, y_test):
        """
        Huấn luyện một model với grid search
        """
        try:
            # Tạo pipeline với scaler
            scaler = RobustScaler()  # Robust hơn StandardScaler cho outliers
            
            # Grid search với time series cross validation
            tscv = TimeSeriesSplit(n_splits=3)
            
            base_model = config['model']()
            pipeline = Pipeline([
                ('scaler', scaler),
                ('model', base_model)
            ])
            
            # Chuẩn bị parameters cho grid search
            grid_params = {}
            for param, values in config['params'].items():
                grid_params[f'model__{param}'] = values
            
            # Grid search
            grid_search = GridSearchCV(
                pipeline,
                grid_params,
                cv=tscv,
                scoring='r2',
                n_jobs=-1,
                verbose=0
            )
            
            # Fit model
            grid_search.fit(X_train, y_train)
            
            # Best model
            best_model = grid_search.best_estimator_
            
            # Predictions và evaluation
            y_pred = best_model.predict(X_test)
            
            performance = {
                'r2_score': r2_score(y_test, y_pred),
                'mse': mean_squared_error(y_test, y_pred),
                'mae': mean_absolute_error(y_test, y_pred),
                'best_params': grid_search.best_params_
            }
            
            # Lưu best params
            config['best_params'] = grid_search.best_params_
            
            logger.info(f"{model_name} - R2: {performance['r2_score']:.4f}, MSE: {performance['mse']:.4f}")
            
            return best_model, performance
            
        except Exception as e:
            logger.error(f"Error training {model_name}: {e}")
            return None, None
    
    def _prepare_comprehensive_training_data(self):
        """
        Chuẩn bị training data comprehensive với nhiều features
        """
        try:
            # Lấy dữ liệu lịch sử
            historical_data = list(KetQuaXoSo.objects.order_by('-ngay')[:500])
            
            if len(historical_data) < self.min_training_data:
                logger.error(f"Not enough historical data: {len(historical_data)}")
                return None, None
            
            X = []
            y = []
            
            # Tạo features cho mỗi ngày
            for i in range(30, len(historical_data)):  # Skip first 30 days for features
                current_result = historical_data[i]
                historical_subset = historical_data[i+1:]  # Data before current date
                
                # Get actual numbers for current day
                actual_numbers = self._extract_numbers_from_result(current_result)
                
                # Create features for each possible number (00-99)
                for num in range(100):
                    num_str = f"{num:02d}"
                    
                    features = self._calculate_enhanced_features(
                        num_str, historical_subset, current_result.ngay
                    )
                    
                    # Target: 1 if number appeared, 0 if not
                    target = 1 if num_str in actual_numbers else 0
                    
                    X.append(features)
                    y.append(target)
            
            return np.array(X), np.array(y)
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return None, None
    
    def _extract_numbers_from_result(self, result):
        """
        Trích xuất tất cả số 2 chữ số từ kết quả xổ số
        """
        try:
            if hasattr(result, 'get_all_2digit_numbers'):
                return result.get_all_2digit_numbers()
            
            # Fallback extraction
            numbers = []
            
            # Extract from all prizes
            for field_name in ['giai_db', 'giai_1', 'giai_2', 'giai_3', 'giai_4', 'giai_5', 'giai_6', 'giai_7']:
                if hasattr(result, field_name):
                    value = getattr(result, field_name)
                    if value:
                        # Get last 2 digits
                        str_value = str(value).strip()
                        if len(str_value) >= 2:
                            numbers.append(str_value[-2:])
            
            return list(set(numbers))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting numbers: {e}")
            return []
    
    def _calculate_enhanced_features(self, number, historical_data, current_date):
        """
        Tính toán features nâng cao cho một số
        """
        try:
            features = []
            
            # 1. Basic number value (0-1 normalized)
            features.append(int(number) / 99.0)
            
            # 2. Days since last appearance
            days_since = self._get_days_since_last_appearance(number, historical_data)
            features.append(min(days_since / 30.0, 1.0))
            
            # 3-4. Frequency features
            features.append(self._get_frequency(number, historical_data[-30:]))
            features.append(self._get_frequency(number, historical_data[-7:]))
            
            # 5-6. Time-based frequencies
            features.append(self._get_weekday_frequency(number, historical_data, current_date.weekday()))
            features.append(self._get_month_frequency(number, historical_data, current_date.month))
            
            # 7. Position frequency
            features.append(self._get_position_frequency(number, historical_data))
            
            # 8. Pair frequency
            features.append(self._get_pair_frequency(number, historical_data))
            
            # 9. Sum digit frequency
            features.append(self._get_sum_digit_frequency(number, historical_data))
            
            # 10. Hot/cold index
            features.append(self._get_hot_cold_index(number, historical_data))
            
            # 11. Trend factor (new)
            features.append(self._get_trend_factor(number, historical_data))
            
            # 12. Cycle position (new)
            features.append(self._get_cycle_position(number, historical_data))
            
            return features
            
        except Exception as e:
            logger.error(f"Error calculating features for {number}: {e}")
            return [0.0] * len(self.feature_names)
    
    def _get_days_since_last_appearance(self, number, historical_data):
        """Tính số ngày kể từ lần xuất hiện cuối"""
        for i, result in enumerate(historical_data):
            if number in self._extract_numbers_from_result(result):
                return i
        return len(historical_data)
    
    def _get_frequency(self, number, historical_data):
        """Tính tần suất xuất hiện"""
        if not historical_data:
            return 0.0
        count = sum(1 for result in historical_data 
                   if number in self._extract_numbers_from_result(result))
        return count / len(historical_data)
    
    def _get_weekday_frequency(self, number, historical_data, target_weekday):
        """Tính tần suất xuất hiện theo thứ"""
        weekday_data = [r for r in historical_data if r.ngay.weekday() == target_weekday]
        return self._get_frequency(number, weekday_data)
    
    def _get_month_frequency(self, number, historical_data, target_month):
        """Tính tần suất xuất hiện theo tháng"""
        month_data = [r for r in historical_data if r.ngay.month == target_month]
        return self._get_frequency(number, month_data)
    
    def _get_position_frequency(self, number, historical_data):
        """Tính tần suất xuất hiện ở vị trí đặc biệt"""
        special_count = 0
        total_count = 0
        
        for result in historical_data:
            numbers = self._extract_numbers_from_result(result)
            if number in numbers:
                total_count += 1
                # Check if in special positions
                if hasattr(result, 'giai_db') and result.giai_db and number in str(result.giai_db)[-2:]:
                    special_count += 1
                elif hasattr(result, 'giai_1') and result.giai_1 and number in str(result.giai_1)[-2:]:
                    special_count += 1
        
        return special_count / total_count if total_count > 0 else 0.0
    
    def _get_pair_frequency(self, number, historical_data):
        """Tính tần suất xuất hiện cùng với số liên tiếp"""
        if not historical_data:
            return 0.0
            
        pair_count = 0
        appearance_count = 0
        num_val = int(number)
        
        for result in historical_data:
            numbers = self._extract_numbers_from_result(result)
            if number in numbers:
                appearance_count += 1
                # Check consecutive numbers
                consecutive = [f"{(num_val-1):02d}", f"{(num_val+1):02d}"]
                if any(c in numbers for c in consecutive if 0 <= int(c) <= 99):
                    pair_count += 1
        
        return pair_count / appearance_count if appearance_count > 0 else 0.0
    
    def _get_sum_digit_frequency(self, number, historical_data):
        """Tính tần suất theo tổng chữ số"""
        target_sum = sum(int(d) for d in number)
        same_sum_count = 0
        total_numbers = 0
        
        for result in historical_data:
            numbers = self._extract_numbers_from_result(result)
            total_numbers += len(numbers)
            same_sum_count += sum(1 for n in numbers 
                                if sum(int(d) for d in n) == target_sum)
        
        return same_sum_count / total_numbers if total_numbers > 0 else 0.0
    
    def _get_hot_cold_index(self, number, historical_data):
        """Tính chỉ số nóng/lạnh"""
        if len(historical_data) < 20:
            return 0.5
            
        recent_freq = self._get_frequency(number, historical_data[:10])
        overall_freq = self._get_frequency(number, historical_data)
        
        if overall_freq == 0:
            return 0.5
            
        ratio = recent_freq / overall_freq
        return min(ratio / 2.0, 1.0)
    
    def _get_trend_factor(self, number, historical_data):
        """Tính hệ số xu hướng"""
        if len(historical_data) < 30:
            return 0.5
            
        # Chia thành 3 periods
        period1 = self._get_frequency(number, historical_data[:10])
        period2 = self._get_frequency(number, historical_data[10:20])
        period3 = self._get_frequency(number, historical_data[20:30])
        
        # Calculate trend
        if period3 > 0:
            trend = (period1 - period3) / period3
        else:
            trend = 0
            
        return (trend + 1) / 2  # Normalize to 0-1
    
    def _get_cycle_position(self, number, historical_data):
        """Tính vị trí trong chu kỳ"""
        appearances = []
        for i, result in enumerate(historical_data):
            if number in self._extract_numbers_from_result(result):
                appearances.append(i)
        
        if len(appearances) < 3:
            return 0.5
            
        # Calculate average cycle length
        intervals = [appearances[i] - appearances[i+1] for i in range(len(appearances)-1)]
        avg_interval = sum(intervals) / len(intervals) if intervals else 30
        
        # Position in current cycle
        days_since_last = appearances[0] if appearances else avg_interval
        cycle_position = days_since_last / avg_interval if avg_interval > 0 else 0.5
        
        return min(cycle_position, 1.0)
    
    def _save_model(self, model_name, model):
        """Lưu model vào file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_path = os.path.join(self.models_dir, f"{model_name}_{timestamp}.pkl")
            
            joblib.dump(model, model_path)
            logger.info(f"Saved {model_name} to {model_path}")
            
        except Exception as e:
            logger.error(f"Error saving {model_name}: {e}")
    
    def _save_performance_history(self, performance_results):
        """Lưu lịch sử performance"""
        try:
            history_entry = {
                'timestamp': datetime.now(),
                'performance': performance_results
            }
            
            # Load existing history
            history = []
            if os.path.exists(self.performance_history_file):
                with open(self.performance_history_file, 'rb') as f:
                    history = pickle.load(f)
            
            # Add new entry
            history.append(history_entry)
            
            # Keep only last 50 entries
            history = history[-50:]
            
            # Save back
            with open(self.performance_history_file, 'wb') as f:
                pickle.dump(history, f)
                
        except Exception as e:
            logger.error(f"Error saving performance history: {e}")
    
    def _select_best_model(self, performance_results):
        """Chọn model tốt nhất dựa trên performance"""
        if not performance_results:
            return None
            
        best_model = max(performance_results.items(), 
                        key=lambda x: x[1]['r2_score'] if x[1] else -1)
        return best_model[0]
    
    def _load_existing_models(self):
        """Load models hiện có"""
        try:
            model_files = [f for f in os.listdir(self.models_dir) 
                          if f.endswith('.pkl') and not f.startswith('performance')]
            return len(model_files) > 0
            
        except Exception as e:
            logger.error(f"Error loading existing models: {e}")
            return False
    
    def get_model_performance_summary(self):
        """Lấy tổng kết performance của models"""
        try:
            if not os.path.exists(self.performance_history_file):
                return {}
                
            with open(self.performance_history_file, 'rb') as f:
                history = pickle.load(f)
            
            if not history:
                return {}
                
            latest_entry = history[-1]
            return latest_entry['performance']
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}