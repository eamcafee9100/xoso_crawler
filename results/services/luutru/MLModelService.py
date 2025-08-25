import os
import pickle
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from django.utils import timezone
from django.core.cache import cache
from results.models import KetQuaXoSo, PredictionPerformanceMetrics
import shap

logger = logging.getLogger(__name__)

class MLModelService:
    """
    Service class để quản lý việc huấn luyện và sử dụng các ML models
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLModelService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.models = {}
        self.scalers = {}
        self.models_dir = 'data/predictor_models'
        self.feature_names = [
            'number_value', 'frequency_last_30days', 'frequency_last_7days', 
            'days_since_last', 'frequency_overall', 'position_frequency',
            'weekday', 'day_of_month', 'recent_trend', 'digit_sum',
            'first_digit', 'second_digit', 'is_even', 'is_palindrome'
        ]
        self.model_versions = {}
        self.load_models()
        self._initialized = True
    
    def load_models(self):
        """Load pre-trained models with better error handling and version compatibility"""
        model_dir = self.models_dir
        if not os.path.exists(model_dir):
            logger.warning(f"Model directory {model_dir} does not exist")
            return
        
        model_files = {
            'random_forest': 'random_forest_*.pkl',
            'gradient_boosting': 'gradient_boosting_*.pkl', 
            'extra_trees': 'extra_trees_*.pkl',
            'ridge': 'ridge_*.pkl'
        }
        
        # Track version incompatibility
        version_warnings = 0
        
        for model_name, pattern in model_files.items():
            try:
                # Find the most recent model file
                import glob
                files = glob.glob(os.path.join(model_dir, pattern))
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    
                    # Try multiple loading methods
                    model = None
                    
                    # Method 1: Standard pickle
                    try:
                        with open(latest_file, 'rb') as f:
                            model = pickle.load(f)
                    except Exception as e1:
                        logger.warning(f"Pickle load failed for {model_name}: {e1}")
                        
                        # Method 2: Try joblib
                        try:
                            import joblib
                            model = joblib.load(latest_file)
                            logger.info(f"Loaded {model_name} with joblib (scikit-learn version warning expected)")
                            # Count version warnings
                            if "version" in str(e1).lower():
                                version_warnings += 1
                        except Exception as e2:
                            logger.error(f"Both pickle and joblib failed for {model_name}: {e2}")
                            continue
                    
                    if model is not None:
                        self.models[model_name] = model
                        logger.info(f"Loaded {model_name} from {os.path.basename(latest_file)}")
                        self.model_versions[model_name] = os.path.basename(latest_file)
                        
            except Exception as e:
                logger.error(f"Failed to load {model_name}: {e}")
        
        logger.info(f"Successfully loaded {len(self.models)} models")
        
        # If we detected version incompatibility issues, recommend retraining
        if version_warnings > 0:
            logger.warning(f"Detected {version_warnings} version compatibility warnings. Consider retraining models.")
        
        # If no models loaded, try to trigger training
        if not self.models:
            logger.info("No models loaded, attempting to train new models")
            try:
                from results.services.EnhancedMLModelTrainer import EnhancedMLModelTrainer
                trainer = EnhancedMLModelTrainer()
                if trainer.train_all_models(force_retrain=True):
                    # Try loading again after training
                    self._load_models()
            except Exception as e:
                logger.error(f"Failed to train models: {e}")
    
    def fix_version_compatibility(self):
        """Fix scikit-learn version compatibility by retraining models"""
        try:
            logger.info("Fixing scikit-learn version compatibility by retraining models...")
            
            # Force retrain all models with current version
            success = self.train_models(force_retrain=True)
            
            if success:
                logger.info("✅ Models successfully retrained with current scikit-learn version")
                return True
            else:
                logger.error("❌ Failed to retrain models")
                return False
                
        except Exception as e:
            logger.error(f"Error fixing version compatibility: {e}")
            return False

    def check_version_compatibility(self):
        """Check if models need retraining due to version incompatibility"""
        try:
            import warnings
            
            # Capture warnings during model loading
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                # Try to use a model for prediction
                if self.models:
                    model_name = list(self.models.keys())[0]
                    model = self.models[model_name]
                    
                    # Test prediction with dummy data
                    dummy_data = np.array([[0.5] * len(self.feature_names)])
                    _ = model.predict(dummy_data)
                    
                    # Check for version warnings
                    version_warnings = [warning for warning in w 
                                    if 'InconsistentVersionWarning' in str(warning.category)]
                    
                    return len(version_warnings) > 0
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking version compatibility: {e}")
            return True  # Assume incompatible if we can't check
    
    def _ensure_models_dir(self):
        """Tạo thư mục models nếu chưa tồn tại"""
        os.makedirs(self.models_dir, exist_ok=True)
        
    def prepare_features_for_prediction(self, historical_data, target_date):
        """
        Chuẩn bị features cho dự đoán ngày kế tiếp
        Args:
            historical_data: Dữ liệu lịch sử
            target_date: Ngày dự đoán
        Returns:
            X: Features matrix, y: Target values (các số 2 chữ số xuất hiện)
        """
        try:
            X = []
            y = []
            
            # Tạo mapping số xuất hiện theo ngày
            number_history = {}
            for i, record in enumerate(historical_data):
                date = record.ngay
                numbers = record.get_all_2digit_numbers()
                
                for num in range(100):  # 00-99
                    num_str = f"{num:02d}"
                    
                    # Tính features cho số này
                    features = self._calculate_number_features(
                        num_str, historical_data[:i], date
                    )
                    
                    # Target: 1 nếu số xuất hiện ngày hôm sau, 0 nếu không
                    target = 1 if num_str in numbers else 0
                    
                    X.append(features)
                    y.append(target)
                    
            return np.array(X), np.array(y)
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None, None
    
    def _calculate_number_features(self, number, historical_subset, current_date):
        """
        Tính toán features cho một số cụ thể
        """
        features = []
        
        # 1. Giá trị số (0-99)
        features.append(int(number) / 99.0)
        
        # 2. Số ngày kể từ lần xuất hiện cuối
        days_since_last = self._get_days_since_last_appearance(number, historical_subset)
        features.append(min(days_since_last / 30.0, 1.0))  # Normalize
        
        # 3. Tần suất xuất hiện 30 ngày gần nhất
        freq_30 = self._get_frequency(number, historical_subset[-30:])
        features.append(freq_30)
        
        # 4. Tần suất xuất hiện 7 ngày gần nhất  
        freq_7 = self._get_frequency(number, historical_subset[-7:])
        features.append(freq_7)
        
        # 5. Tần suất theo thứ trong tuần
        weekday_freq = self._get_weekday_frequency(number, historical_subset, current_date.weekday())
        features.append(weekday_freq)
        
        # 6. Tần suất theo tháng
        month_freq = self._get_month_frequency(number, historical_subset, current_date.month)
        features.append(month_freq)
        
        # 7. Vị trí trong giải thưởng (0-1)
        position_freq = self._get_position_frequency(number, historical_subset)
        features.append(position_freq)
        
        # 8. Tần suất cặp số
        pair_freq = self._get_pair_frequency(number, historical_subset)
        features.append(pair_freq)
        
        # 9. Tần suất tổng chữ số
        sum_digit_freq = self._get_sum_digit_frequency(number, historical_subset)
        features.append(sum_digit_freq)
        
        # 10. Chỉ số nóng/lạnh
        hot_cold_index = self._get_hot_cold_index(number, historical_subset)
        features.append(hot_cold_index)
        
        return features
    
    def _get_days_since_last_appearance(self, number, historical_data):
        """Tính số ngày kể từ lần xuất hiện cuối cùng"""
        for i, record in enumerate(historical_data):
            if number in record.get_all_2digit_numbers():
                return i
        return len(historical_data)
    
    def _get_frequency(self, number, historical_data):
        """Tính tần suất xuất hiện"""
        if not historical_data:
            return 0.0
        count = sum(1 for record in historical_data if number in record.get_all_2digit_numbers())
        return count / len(historical_data)
    
    def _get_weekday_frequency(self, number, historical_data, target_weekday):
        """Tính tần suất xuất hiện theo thứ"""
        weekday_records = [r for r in historical_data if r.ngay.weekday() == target_weekday]
        return self._get_frequency(number, weekday_records)
    
    def _get_month_frequency(self, number, historical_data, target_month):
        """Tính tần suất xuất hiện theo tháng"""
        month_records = [r for r in historical_data if r.ngay.month == target_month]
        return self._get_frequency(number, month_records)
    
    def _get_position_frequency(self, number, historical_data):
        """Tính tần suất xuất hiện theo vị trí giải"""
        # Simplified: check if appears in special prizes more often
        special_count = 0
        total_count = 0
        
        for record in historical_data:
            if number in record.get_all_2digit_numbers():
                total_count += 1
                # Check if in special positions (DB, G1)
                if (hasattr(record, 'giai_db') and number in record.giai_db[-2:]) or \
                   (hasattr(record, 'giai_1') and number in record.giai_1[-2:]):
                    special_count += 1
                    
        return special_count / total_count if total_count > 0 else 0.0
    
    def _get_pair_frequency(self, number, historical_data):
        """Tính tần suất xuất hiện cùng với các số khác"""
        # Simplified: check frequency of appearing with consecutive numbers
        if not historical_data:
            return 0.0
            
        pair_count = 0
        appearance_count = 0
        
        for record in historical_data:
            numbers = record.get_all_2digit_numbers()
            if number in numbers:
                appearance_count += 1
                # Check if appears with consecutive numbers
                num_val = int(number)
                consecutive_nums = [f"{(num_val-1):02d}", f"{(num_val+1):02d}"]
                if any(cn in numbers for cn in consecutive_nums):
                    pair_count += 1
                    
        return pair_count / appearance_count if appearance_count > 0 else 0.0
    def get_model_versions(self):
        """
        Get versions of loaded models
        """
        try:
            versions = {}
            for model_name, model in self.models.items():
                versions[model_name] = type(model).__name__
            return versions
            
        except Exception as e:
            logger.error(f"Error getting model versions: {e}")
            return {}
        
    def _get_sum_digit_frequency(self, number, historical_data):
        """Tính tần suất theo tổng chữ số"""
        sum_digits = sum(int(d) for d in number)
        same_sum_count = 0
        total_numbers = 0
        
        for record in historical_data:
            numbers = record.get_all_2digit_numbers()
            total_numbers += len(numbers)
            same_sum_count += sum(1 for n in numbers if sum(int(d) for d in n) == sum_digits)
            
        return same_sum_count / total_numbers if total_numbers > 0 else 0.0
    
    def _get_hot_cold_index(self, number, historical_data):
        """Tính chỉ số nóng/lạnh"""
        if not historical_data:
            return 0.5
            
        # Tính tần suất gần đây vs tần suất tổng thể
        recent_freq = self._get_frequency(number, historical_data[-10:])
        overall_freq = self._get_frequency(number, historical_data)
        
        if overall_freq == 0:
            return 0.5
            
        # Tỷ lệ > 1 = hot, < 1 = cold
        ratio = recent_freq / overall_freq if overall_freq > 0 else 1
        return min(ratio / 2.0, 1.0)  # Normalize to 0-1
    
    def train_models(self, force_retrain=False):
        """Train models using EnhancedMLModelTrainer"""
        try:
            from results.services.EnhancedMLModelTrainer import EnhancedMLModelTrainer
            
            trainer = EnhancedMLModelTrainer()
            success = trainer.train_all_models(force_retrain=force_retrain)
            
            if success:
                # Clear existing models and reload
                self.models.clear()
                self.model_versions.clear()
                
                # Reload models after training
                self.load_models()
                logger.info("Models trained and loaded successfully")
                return True
            else:
                logger.warning("Model training failed")
                return False
                
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return False
    
    def validate_models(self):
        """Validate that models are working correctly"""
        try:
            if not self.models:
                return "No models loaded"
            
            # Test with dummy data
            dummy_features = pd.DataFrame([{feature: 0 for feature in self.feature_names}])
            
            working_models = 0
            for model_name, model in self.models.items():
                try:
                    if hasattr(model, 'predict'):
                        prediction = model.predict(dummy_features)
                        if prediction is not None:
                            working_models += 1
                except:
                    continue
            
            return f"{working_models}/{len(self.models)} models working"
            
        except Exception as e:
            return f"Validation error: {str(e)}"
    

    def _save_models(self):
        """Lưu models vào file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Lưu models
            for name, model in self.models.items():
                model_path = os.path.join(self.models_dir, f"{name}_{timestamp}.pkl")
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                logger.info(f"Saved {name} model to {model_path}")
            
            # Lưu scalers
            scaler_path = os.path.join(self.models_dir, f"scaler_{timestamp}.pkl")
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scalers, f)
                
            # Lưu metadata
            metadata = {
                'timestamp': timestamp,
                'feature_names': self.feature_names,
                'model_versions': {name: type(model).__name__ for name, model in self.models.items()}
            }
            metadata_path = os.path.join(self.models_dir, f"metadata_{timestamp}.pkl")
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
                
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self):
        """Load pre-trained models with better error handling and version compatibility"""
        model_dir = self.models_dir
        if not os.path.exists(model_dir):
            logger.warning(f"Model directory {model_dir} does not exist")
            return
        
        model_files = {
            'random_forest': 'random_forest_*.pkl',
            'gradient_boosting': 'gradient_boosting_*.pkl', 
            'extra_trees': 'extra_trees_*.pkl',
            'ridge': 'ridge_*.pkl'
        }
        
        # Check if we need to retrain due to version incompatibility
        need_retrain = False
        
        for model_name, pattern in model_files.items():
            try:
                # Find the most recent model file
                import glob
                files = glob.glob(os.path.join(model_dir, pattern))
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    
                    # Try multiple loading methods
                    model = None
                    
                    # Method 1: Standard pickle
                    try:
                        with open(latest_file, 'rb') as f:
                            model = pickle.load(f)
                    except Exception as e1:
                        logger.warning(f"Pickle load failed for {model_name}: {e1}")
                        
                        # Method 2: Try joblib
                        try:
                            import joblib
                            model = joblib.load(latest_file)
                            logger.info(f"Loaded {model_name} with joblib (scikit-learn version warning expected)")
                        except Exception as e2:
                            logger.error(f"Both pickle and joblib failed for {model_name}: {e2}")
                            need_retrain = True
                            continue
                    
                    if model is not None:
                        self.models[model_name] = model
                        logger.info(f"Loaded {model_name} from {os.path.basename(latest_file)}")
                        self.model_versions[model_name] = os.path.basename(latest_file)
                        
            except Exception as e:
                logger.error(f"Failed to load {model_name}: {e}")
                need_retrain = True
        
        logger.info(f"Successfully loaded {len(self.models)} models")
        
        # If we have version incompatibility warnings or failed to load models, retrain
        if need_retrain or len(self.models) == 0:
            logger.info("Retraining models due to version incompatibility or loading failures")
            try:
                from results.services.EnhancedMLModelTrainer import EnhancedMLModelTrainer
                trainer = EnhancedMLModelTrainer()
                if trainer.train_all_models(force_retrain=True):
                    # Clear old models and reload
                    self.models.clear()
                    self._load_models()
            except Exception as e:
                logger.error(f"Failed to retrain models: {e}")


    def predict_numbers(self, historical_data, target_date, top_k=20):
        """
        Dự đoán các số 2 chữ số có xác suất cao
        
        Args:
            historical_data: Dữ liệu lịch sử
            target_date: Ngày cần dự đoán
            top_k: Số lượng số cần trả về
            
        Returns:
            List of predictions với format {'number': str, 'confidence': float}
        """
        try:
            if not self.models:
                logger.warning("No ML models available for prediction")
                return []
            
            # Chuẩn bị features cho tất cả các số từ 00-99
            all_predictions = []
            
            for number in range(100):
                number_str = f"{number:02d}"
                
                # Tạo features cho số này
                features = self._create_number_features(number_str, historical_data, target_date)
                
                if features:
                    # Dự đoán với tất cả models
                    model_predictions = []
                    
                    for model_name, model in self.models.items():
                        try:
                            # Chuẩn bị input data
                            feature_df = pd.DataFrame([features])
                            
                            # Đảm bảo có đúng features
                            for feature_name in self.feature_names:
                                if feature_name not in feature_df.columns:
                                    feature_df[feature_name] = 0
                            
                            feature_df = feature_df[self.feature_names]
                            
                            # Dự đoán
                            prediction = model.predict(feature_df)[0]
                            model_predictions.append(prediction)
                            
                        except Exception as e:
                            logger.error(f"Error predicting with {model_name}: {e}")
                            continue
                    
                    if model_predictions:
                        # Tính trung bình confidence từ các models
                        avg_confidence = np.mean(model_predictions)
                        all_predictions.append({
                            'number': number_str,
                            'confidence': float(avg_confidence)
                        })
            
            # Sắp xếp theo confidence giảm dần và lấy top_k
            all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
            return all_predictions[:top_k]
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            return []
        
    def predict_for_date(self, target_date, historical_data):
        """Generate predictions for a specific date"""
        try:
            if not self.models:
                logger.warning("No models loaded")
                return []
            
            # Prepare features for prediction
            features_df = self._prepare_features_for_prediction(historical_data, target_date)
            
            if features_df.empty:
                logger.warning("No features prepared for prediction")
                return []
            
            # Generate predictions from all models
            all_predictions = {}
            
            for model_name, model in self.models.items():
                try:
                    if hasattr(model, 'predict'):
                        predictions = model.predict(features_df)
                        
                        # Convert predictions to number format
                        for i, prediction in enumerate(predictions):
                            number = str(int(abs(prediction) % 100)).zfill(2)
                            
                            if number not in all_predictions:
                                all_predictions[number] = {
                                    'votes': 0,
                                    'confidence': 0,
                                    'models': []
                                }
                            
                            all_predictions[number]['votes'] += 1
                            all_predictions[number]['models'].append(model_name)
                            
                            # Calculate confidence based on prediction strength
                            confidence = min(0.95, abs(prediction) / 100)
                            all_predictions[number]['confidence'] = max(
                                all_predictions[number]['confidence'], confidence
                            )
                            
                except Exception as e:
                    logger.error(f"Error with model {model_name}: {e}")
                    continue
            
            # Convert to final prediction format
            final_predictions = []
            for number, data in all_predictions.items():
                final_predictions.append({
                    'number': number,
                    'confidence': data['confidence'],
                    'votes': data['votes'],
                    'models': data['models']
                })
            
            # Sort by votes and confidence
            final_predictions.sort(key=lambda x: (x['votes'], x['confidence']), reverse=True)
            
            return final_predictions[:15]  # Return top 15 predictions
            
        except Exception as e:
            logger.error(f"Error in predict_for_date: {e}")
            return []

    def _extract_features_for_number(self, number, date, historical_data):
        """Extract features for a specific number - Missing method implementation"""
        try:
            features = {}
            
            # Basic number features
            features['number_value'] = int(str(number)[-2:]) if len(str(number)) >= 2 else int(number)
            features['number_digit_1'] = int(str(number).zfill(2)[0])
            features['number_digit_2'] = int(str(number).zfill(2)[1])
            features['number_sum'] = features['number_digit_1'] + features['number_digit_2']
            
            # Historical frequency features
            all_numbers = []
            for data in historical_data[-30:]:  # Last 30 days
                if isinstance(data, dict):
                    all_numbers.extend(data.get('numbers', []))
                else:
                    # Handle Django model objects
                    numbers = self._extract_numbers_from_result(data)
                    all_numbers.extend(numbers)
            
            number_str = str(number).zfill(2)
            features['frequency_last_30days'] = all_numbers.count(number_str)
            features['frequency_last_7days'] = sum(
                data.get('numbers', []).count(number_str) if isinstance(data, dict) else 
                self._extract_numbers_from_result(data).count(number_str)
                for data in historical_data[-7:]
            )
            
            # Days since last appearance
            days_since = 999
            for i, data in enumerate(reversed(historical_data)):
                data_numbers = data.get('numbers', []) if isinstance(data, dict) else self._extract_numbers_from_result(data)
                if number_str in data_numbers:
                    days_since = i
                    break
            
            features['days_since_last'] = min(days_since, 365)
            
            # Pattern features
            features['is_consecutive'] = abs(features['number_digit_1'] - features['number_digit_2']) == 1
            features['is_double'] = features['number_digit_1'] == features['number_digit_2']
            features['is_even_sum'] = features['number_sum'] % 2 == 0
            
            # Week and month features
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()
            
            features['day_of_week'] = date.weekday()
            features['day_of_month'] = date.day
            features['month'] = date.month
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features for number {number}: {e}")
            return {}

    def _prepare_features_for_prediction(self, historical_data, target_date):
        """Chuẩn bị features cho dự đoán"""
        try:
            # Tương tự như trong EnhancedMLModelTrainer
            features_list = []
            
            # Get all unique numbers from historical data
            all_numbers = set()
            for data_point in historical_data:
                numbers = data_point.get('numbers', [])
                for num in numbers:
                    if isinstance(num, str) and len(num) == 2 and num.isdigit():
                        all_numbers.add(num)
                    elif isinstance(num, int) and 0 <= num <= 99:
                        all_numbers.add(str(num).zfill(2))
            
            # Create features for each number
            for number in list(all_numbers)[:100]:  # Limit to 100 numbers to avoid memory issues
                features = self._extract_features_for_number(number, target_date, historical_data)
                if features:
                    features_list.append(features)
            
            if not features_list:
                return pd.DataFrame()
            
            # Tạo DataFrame
            df = pd.DataFrame(features_list)
            
            # Đảm bảo có đúng các features cần thiết
            required_features = self.feature_names
            for feature in required_features:
                if feature not in df.columns:
                    df[feature] = 0
            
            return df[required_features]
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return pd.DataFrame()

    def _create_number_features(self, number_str, historical_data, target_date):
        """Tạo features cho một số cụ thể - Fixed date handling"""
        try:
            features = {}
            
            # Basic number features
            features['number_value'] = int(number_str)
            
            # Historical frequency features
            all_numbers = []
            for data in historical_data[-30:]:  # Last 30 days
                if isinstance(data, dict):
                    numbers = data.get('numbers', [])
                else:
                    # Handle Django model objects
                    numbers = self._extract_numbers_from_result(data)
                
                if isinstance(numbers, list):
                    all_numbers.extend(numbers)
            
            features['frequency_last_30days'] = all_numbers.count(number_str)
            
            # Last 7 days frequency
            last_7_numbers = []
            for data in historical_data[-7:]:
                if isinstance(data, dict):
                    numbers = data.get('numbers', [])
                else:
                    numbers = self._extract_numbers_from_result(data)
                
                if isinstance(numbers, list):
                    last_7_numbers.extend(numbers)
            
            features['frequency_last_7days'] = last_7_numbers.count(number_str)
            
            # Days since last appearance
            days_since = 999
            for i, data in enumerate(reversed(historical_data)):
                if isinstance(data, dict):
                    numbers = data.get('numbers', [])
                    data_date = data.get('date')
                else:
                    # Handle Django model objects
                    numbers = self._extract_numbers_from_result(data)
                    data_date = data.ngay if hasattr(data, 'ngay') else None
                
                if isinstance(numbers, list) and number_str in numbers:
                    days_since = i
                    break
            
            features['days_since_last'] = days_since
            
            # Position frequency (xuất hiện ở vị trí nào nhiều nhất)
            position_count = 0
            for data in historical_data[-30:]:
                if isinstance(data, dict):
                    numbers = data.get('numbers', [])
                else:
                    numbers = self._extract_numbers_from_result(data)
                
                if isinstance(numbers, list) and number_str in numbers:
                    position_count += 1
            
            features['position_frequency'] = position_count
            
            # Date features - Handle both date objects and datetime objects
            if isinstance(target_date, str):
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            elif hasattr(target_date, 'date'):
                target_date = target_date.date()
            
            features['weekday'] = target_date.weekday()
            features['day_of_month'] = target_date.day
            features['is_weekend'] = 1 if target_date.weekday() >= 5 else 0
            
            # Gap analysis - Fixed date handling
            gaps = []
            last_appearance = None
            for data in historical_data:
                if isinstance(data, dict):
                    numbers = data.get('numbers', [])
                    data_date = data.get('date')
                    if isinstance(data_date, str):
                        data_date = datetime.strptime(data_date, '%Y-%m-%d').date()
                else:
                    # Handle Django model objects
                    numbers = self._extract_numbers_from_result(data)
                    data_date = data.ngay if hasattr(data, 'ngay') else None
                
                if isinstance(numbers, list) and number_str in numbers and data_date:
                    if last_appearance is not None:
                        gap = (data_date - last_appearance).days
                        gaps.append(gap)
                    last_appearance = data_date
            
            if gaps:
                features['avg_gap'] = np.mean(gaps)
                features['max_gap'] = max(gaps)
                features['min_gap'] = min(gaps)
            else:
                features['avg_gap'] = 0
                features['max_gap'] = 0
                features['min_gap'] = 0
            
            return features
            
        except Exception as e:
            logger.error(f"Error creating features for {number_str}: {e}")
            return None

    def _combine_model_predictions(self, predictions):
        """Kết hợp predictions từ nhiều models"""
        if not predictions:
            return []
        
        # Nếu chỉ có 1 model
        if len(predictions) == 1:
            return predictions[0]
        
        # Kết hợp predictions từ nhiều models
        combined = {}
        for model_pred in predictions:
            for pred in model_pred:
                number = pred['number']
                confidence = pred['confidence']
                
                if number in combined:
                    combined[number]['confidence'] += confidence
                    combined[number]['count'] += 1
                else:
                    combined[number] = {'confidence': confidence, 'count': 1}
        
        # Tính trung bình confidence
        result = []
        for number, data in combined.items():
            avg_confidence = data['confidence'] / data['count']
            result.append({'number': number, 'confidence': avg_confidence})
        
        # Sắp xếp theo confidence
        result.sort(key=lambda x: x['confidence'], reverse=True)
        return result
    
    def _get_recent_data(self, target_date, days=90):
        """Lấy dữ liệu gần đây để dự đoán"""
        try:
            from results.models import KetQuaXoSo
            from datetime import timedelta
            
            end_date = target_date - timedelta(days=1)
            start_date = end_date - timedelta(days=days)
            
            results = KetQuaXoSo.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date
            ).order_by('-ngay')
            
            historical_data = []
            for result in results:
                numbers = self._extract_numbers_from_result(result)
                historical_data.append({
                    'date': result.ngay,
                    'numbers': numbers,
                    'special_prize': result.giai_db,
                    'first_prize': result.giai_1
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting recent data: {e}")
            return []
    
    def _extract_numbers_from_result(self, result):
        """Extract numbers from Django model result object"""
        try:
            numbers = []
            
            # Extract from all prize fields
            for field_name in ['giai_db', 'giai_nhat', 'giai_nhi', 'giai_ba', 'giai_tu', 
                             'giai_nam', 'giai_sau', 'giai_bay', 'giai_tam']:
                if hasattr(result, field_name):
                    field_value = getattr(result, field_name)
                    if field_value:
                        two_digit_numbers = self._extract_two_digits(str(field_value))
                        numbers.extend(two_digit_numbers)
            
            return list(set(numbers))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting numbers from result: {e}")
            return []
    
    def _extract_two_digits(self, text):
        """Extract 2-digit numbers from text"""
        if not text:
            return []
        
        try:
            # Clean and extract digits
            digits_only = ''.join(c for c in text if c.isdigit())
            
            numbers = []
            if len(digits_only) >= 2:
                # Get last 2 digits
                numbers.append(digits_only[-2:])
                
                # If string is longer, get 2-digit pairs
                for i in range(0, len(digits_only) - 1, 2):
                    if i + 1 < len(digits_only):
                        numbers.append(digits_only[i:i+2])
            
            return [num for num in numbers if len(num) == 2]
        except Exception as e:
            logger.warning(f"Error extracting 2-digit numbers from '{text}': {e}")
            return []
    def get_recent_accuracy(self):
        """
        Get recent model accuracy
        """
        try:
            # Get recent performance metrics
            recent_metrics = PredictionPerformanceMetrics.objects.filter(
                analysis_date__gte=timezone.now().date() - timedelta(days=7),
                method_name__in=['ml_model', 'random_forest', 'gradient_boosting']
            ).order_by('-analysis_date')
            
            if not recent_metrics:
                return 0.5  # Default accuracy
                
            total_accuracy = sum(m.hit_rate for m in recent_metrics)
            return total_accuracy / len(recent_metrics)
            
        except Exception as e:
            logger.error(f"Error getting recent accuracy: {e}")
            return 0.5
    def get_model_info(self):
        """Get information about loaded models"""
        return {
            'loaded_models': list(self.models.keys()),
            'model_versions': self.model_versions,
            'feature_count': len(self.feature_names)
        }
    def get_feature_importance(self):
        """Get feature importance from models"""
        try:
            importance_dict = {}
            
            for model_name, model in self.models.items():
                if hasattr(model, 'feature_importances_'):
                    importance_dict[model_name] = dict(zip(
                        self.feature_names, 
                        model.feature_importances_
                    ))
            
            return importance_dict
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {}
        
    def get_last_training_date(self):
        """
        Get last training date of models
        """
    def get_last_training_date(self):
        """Get last training date"""
        try:
            # Check file modification dates
            model_dir = os.path.join('results', 'ml_models')
            if os.path.exists(model_dir):
                files = os.listdir(model_dir)
                if files:
                    latest_file = max([os.path.join(model_dir, f) for f in files], key=os.path.getctime)
                    return datetime.fromtimestamp(os.path.getctime(latest_file)).date()
        
            
        except Exception as e:
            logger.error(f"Error getting last training date: {e}")
            return None
       

class SHAPAnalysisService:
    """
    Service class để thực hiện phân tích SHAP
    """
    
    def __init__(self, ml_service):
        self.ml_service = ml_service
        self.explainers = {}
    def analyze_predictions(self, historical_data):
        """Analyze predictions using SHAP"""
        try:
            if not self.ml_service.models:
                return {'error': 'No ML models available for SHAP analysis'}
            
            # Prepare features
            features_df = self.ml_service._prepare_features_for_prediction(historical_data, timezone.now().date())
            
            if features_df.empty:
                return {'error': 'No features available for SHAP analysis'}
            
            shap_results = {}
            
            # Analyze each model
            for model_name, model in self.ml_service.models.items():
                if hasattr(model, 'predict') and model_name not in ['ridge']:  # Skip Ridge for SHAP
                    try:
                        # Create SHAP explainer
                        if model_name not in self.explainers:
                            if hasattr(model, 'predict_proba'):
                                self.explainers[model_name] = shap.TreeExplainer(model)
                            else:
                                self.explainers[model_name] = shap.Explainer(model)
                        
                        # Get SHAP values
                        explainer = self.explainers[model_name]
                        shap_values = explainer.shap_values(features_df.iloc[:10])  # Limit to 10 samples
                        
                        # Get feature contributions
                        feature_contributions = {}
                        if isinstance(shap_values, list):
                            shap_values = shap_values[0]  # Take first class for multi-class
                        
                        mean_contributions = np.abs(shap_values).mean(axis=0)
                        
                        for i, feature_name in enumerate(self.ml_service.feature_names):
                            if i < len(mean_contributions):
                                feature_contributions[feature_name] = float(mean_contributions[i])
                        
                        shap_results[model_name] = {
                            'feature_contributions': feature_contributions,
                            'top_features': sorted(feature_contributions.items(), 
                                                 key=lambda x: x[1], reverse=True)[:5]
                        }
                        
                    except Exception as e:
                        logger.error(f"SHAP analysis failed for {model_name}: {e}")
                        shap_results[model_name] = {'error': str(e)}
            
            return {
                'model_explanations': shap_results,
                'overall_top_features': self._get_overall_top_features(shap_results)
            }
            
        except Exception as e:
            logger.error(f"SHAP analysis failed: {e}")
            return {'error': str(e)}
    def _get_overall_top_features(self, shap_results):
        """Get overall top features across all models"""
        try:
            feature_scores = {}
            
            for model_results in shap_results.values():
                if 'feature_contributions' in model_results:
                    for feature, score in model_results['feature_contributions'].items():
                        if feature not in feature_scores:
                            feature_scores[feature] = []
                        feature_scores[feature].append(score)
            
            # Average scores across models
            avg_scores = {}
            for feature, scores in feature_scores.items():
                avg_scores[feature] = np.mean(scores)
            
            return sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            
        except Exception as e:
            logger.error(f"Error getting overall top features: {e}")
            return []        
    def calculate_shap_values(self, model_name, X_sample, feature_names=None):
        """
        Tính SHAP values cho model
        """
        try:
            if model_name not in self.ml_service.models:
                logger.warning(f"Model {model_name} not found")
                return None
            
            model = self.ml_service.models[model_name]
            
            # Tạo explainer nếu chưa có
            if model_name not in self.explainers:
                # Sử dụng TreeExplainer cho tree-based models
                if hasattr(model, 'estimators_'):
                    self.explainers[model_name] = shap.TreeExplainer(model)
                else:
                    # Fallback to KernelExplainer
                    background = shap.sample(X_sample, 100)
                    self.explainers[model_name] = shap.KernelExplainer(
                        model.predict, background
                    )
            
            # Tính SHAP values
            explainer = self.explainers[model_name]
            shap_values = explainer.shap_values(X_sample)
            
            # Tính feature importance
            feature_names = feature_names or self.ml_service.feature_names
            feature_importance = {}
            
            if len(shap_values.shape) == 2:
                for i, name in enumerate(feature_names):
                    if i < shap_values.shape[1]:
                        importance = np.abs(shap_values[:, i]).mean()
                        feature_importance[name] = float(importance)
            
            return {
                'shap_values': shap_values.tolist() if hasattr(shap_values, 'tolist') else shap_values,
                'feature_importance': feature_importance,
                'base_value': float(explainer.expected_value) if hasattr(explainer, 'expected_value') else 0.0,
                'feature_names': feature_names
            }
            
        except Exception as e:
            logger.error(f"Error calculating SHAP values: {e}")
            return None
    
    def get_feature_importance_description(self, feature_importance):
        """
        Tạo mô tả dễ hiểu về feature importance
        """
        descriptions = []
        sorted_features = sorted(
            feature_importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        feature_descriptions = {
            'number_value': 'Giá trị số',
            'days_since_last_appearance': 'Số ngày kể từ lần xuất hiện cuối',
            'frequency_last_30days': 'Tần suất 30 ngày gần nhất',
            'frequency_last_7days': 'Tần suất 7 ngày gần nhất',
            'weekday_frequency': 'Tần suất theo thứ trong tuần',
            'month_frequency': 'Tần suất theo tháng',
            'position_in_prize': 'Vị trí trong giải thưởng',
            'pair_frequency': 'Tần suất xuất hiện cùng với số khác',
            'sum_digit_frequency': 'Tần suất theo tổng chữ số',
            'hot_cold_index': 'Chỉ số nóng/lạnh'
        }
        
        for feature, importance in sorted_features[:5]:
            desc = feature_descriptions.get(feature, feature)
            descriptions.append(
                f"{desc} có mức ảnh hưởng {importance:.3f} đến kết quả dự đoán"
            )
        
        return "\n".join(descriptions)
    
    def predict_for_date(self, target_date, historical_data):
        """Generate predictions for a specific date"""
        try:
            if not self.models:
                logger.warning("No models loaded")
                return []
            
            # Prepare features for prediction
            features_df = self._prepare_features_for_prediction(historical_data, target_date)
            
            if features_df.empty:
                logger.warning("No features prepared for prediction")
                return []
            
            # Generate predictions from all models
            all_predictions = {}
            
            for model_name, model in self.models.items():
                try:
                    if hasattr(model, 'predict'):
                        predictions = model.predict(features_df)
                        
                        # Convert predictions to number format
                        for i, prediction in enumerate(predictions):
                            number = str(int(abs(prediction) % 100)).zfill(2)
                            
                            if number not in all_predictions:
                                all_predictions[number] = {
                                    'votes': 0,
                                    'confidence': 0,
                                    'models': []
                                }
                            
                            all_predictions[number]['votes'] += 1
                            all_predictions[number]['models'].append(model_name)
                            
                            # Calculate confidence based on prediction strength
                            confidence = min(0.95, abs(prediction) / 100)
                            all_predictions[number]['confidence'] = max(
                                all_predictions[number]['confidence'], confidence
                            )
                            
                except Exception as e:
                    logger.error(f"Error with model {model_name}: {e}")
                    continue
            
            # Convert to final prediction format
            final_predictions = []
            for number, data in all_predictions.items():
                final_predictions.append({
                    'number': number,
                    'confidence': data['confidence'],
                    'votes': data['votes'],
                    'models': data['models']
                })
            
            # Sort by votes and confidence
            final_predictions.sort(key=lambda x: (x['votes'], x['confidence']), reverse=True)
            
            return final_predictions[:15]  # Return top 15 predictions
            
        except Exception as e:
            logger.error(f"Error in predict_for_date: {e}")
            return []
    
    def get_model_info(self):
        """
        Get information about loaded models
        """
        try:
            info = {
                'models_loaded': len(self.models),
                'model_types': list(self.models.keys()),
                'feature_count': len(self.feature_names),
                'scalers_loaded': len(self.scalers)
            }
            
            # Add model-specific info if available
            for name, model in self.models.items():
                if hasattr(model, 'get_params'):
                    info[f'{name}_params'] = str(type(model).__name__)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {}
    
    def get_feature_importance(self, model_name, data):
        """Lấy feature importance từ SHAP values"""
        try:
            explanation = self.explain_predictions(model_name, data)
            if not explanation:
                return None
            
            shap_values = explanation['shap_values']
            feature_names = explanation['feature_names']
            
            # Tính trung bình absolute SHAP values cho mỗi feature
            mean_shap = np.mean(np.abs(shap_values), axis=0)
            
            # Tạo dictionary feature importance
            importance = {}
            for i, feature_name in enumerate(feature_names):
                importance[feature_name] = float(mean_shap[i])
            
            # Sắp xếp theo importance
            sorted_importance = sorted(
                importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return {
                'feature_importance': dict(sorted_importance),
                'total_features': len(feature_names)
            }
            
        except Exception as e:
            logger.error(f"Error getting feature importance for {model_name}: {e}")
            return None
    def create_explainer(self, model_name, background_data):
        """Tạo SHAP explainer cho model"""
        try:
            if model_name not in self.ml_service.models:
                return None
            
            model = self.ml_service.models[model_name]
            
            # Tạo explainer dựa trên loại model
            if hasattr(model, 'predict_proba'):
                explainer = shap.Explainer(model, background_data)
            else:
                explainer = shap.Explainer(model.predict, background_data)
            
            self.explainers[model_name] = explainer
            return explainer
            
        except Exception as e:
            logger.error(f"Error creating SHAP explainer for {model_name}: {e}")
            return None
           
    def explain_predictions(self, model_name, data):
        """Tạo SHAP explanations cho predictions"""
        try:
            if model_name not in self.explainers:
                return None
            
            explainer = self.explainers[model_name]
            shap_values = explainer(data)
            
            return {
                'shap_values': shap_values.values,
                'base_value': shap_values.base_values,
                'data': shap_values.data,
                'feature_names': self.ml_service.feature_names
            }
            
        except Exception as e:
            logger.error(f"Error explaining predictions for {model_name}: {e}")
            return None
            
    def get_recent_accuracy(self):
        """
        Get recent model accuracy
        """
        try:
            # Get recent performance metrics
            recent_metrics = PredictionPerformanceMetrics.objects.filter(
                analysis_date__gte=timezone.now().date() - timedelta(days=7),
                method_name__in=['ml_model', 'random_forest', 'gradient_boosting']
            ).order_by('-analysis_date')
            
            if not recent_metrics:
                return 0.5  # Default accuracy
                
            total_accuracy = sum(m.hit_rate for m in recent_metrics)
            return total_accuracy / len(recent_metrics)
            
        except Exception as e:
            logger.error(f"Error getting recent accuracy: {e}")
            return 0.5
    
    def get_model_accuracy(self):
        """
        Get current model accuracy (alias for get_recent_accuracy)
        """
        return self.get_recent_accuracy()
    
    def get_model_versions(self):
        """
        Get versions of loaded models
        """
        try:
            versions = {}
            for model_name, model in self.models.items():
                versions[model_name] = type(model).__name__
            return versions
            
        except Exception as e:
            logger.error(f"Error getting model versions: {e}")
            return {}
    
    def get_last_training_date(self):
        """
        Get last training date of models
        """
        try:
            model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.pkl')]
            if not model_files:
                return None
                
            # Get newest file
            newest_file = max(model_files, key=lambda f: os.path.getctime(
                os.path.join(self.models_dir, f)
            ))
            
            file_time = datetime.fromtimestamp(
                os.path.getctime(os.path.join(self.models_dir, newest_file))
            )
            
            return file_time.date()
            
        except Exception as e:
            logger.error(f"Error getting last training date: {e}")
            return None
    
    def validate_models(self):
        """
        Validate loaded models
        """
        try:
            if not self.models:
                if self._load_models():
                    return "models_loaded"
                else:
                    return "no_models_available"
            
            # Check if models can make predictions
            test_input = np.array([[0.5] * len(self.feature_names)])
            
            for name, model in self.models.items():
                try:
                    prediction = model.predict(test_input)
                    if prediction is None:
                        return f"model_{name}_invalid"
                except Exception:
                    return f"model_{name}_error"
            
            return "models_valid"
            
        except Exception as e:
            logger.error(f"Error validating models: {e}")
            return f"validation_error: {str(e)}"