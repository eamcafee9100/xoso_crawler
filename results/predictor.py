import logging
import joblib
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
from datetime import timedelta, datetime, date
from itertools import combinations
from typing import Dict, List, Tuple, Optional, Any

from django.utils import timezone
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

logger = logging.getLogger(__name__)

class EnhancedCyclePredictor:
    """
    ✅ MAIN PREDICTOR CLASS - Tối ưu và đầy đủ tính năng
    """
    
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'ensemble': None  # Will be created when needed
        }
        self.scaler = StandardScaler()
        self.weights = defaultdict(float)
        self.is_trained = False
        self._last_trained = timezone.now()
        self.feature_names = [
            'frequency_analysis',
            'recency_analysis', 
            'cycle_detection',
            'pair_analysis',
            'temporal_features'
        ]
        self.performance_history = []
        
    @property
    def version(self) -> str:
        """Model version"""
        return "2.1.0"
    
    @property
    def last_trained(self) -> timezone.datetime:
        """Last training timestamp"""
        return self._last_trained
    
    @property
    def used_features(self) -> List[str]:
        """Features used by model"""
        return self.feature_names
    
    def get_metadata(self) -> Dict:
        """Get model metadata"""
        return {
            'version': self.version,
            'last_trained': self.last_trained.isoformat(),
            'features': self.used_features,
            'is_trained': self.is_trained,
            'models_available': list(self.models.keys()),
            'performance_history_length': len(self.performance_history)
        }
    
    def get_model_id(self) -> str:
        """Get unique model identifier"""
        return f"enhanced_cycle_predictor_{self.version}"
    
    def predict_for_date(self, history_data: List, target_date: date) -> Dict[str, float]:
        """
        ✅ SỬA: Main prediction với data order validation
        """
        try:
            # Validate input
            if not history_data:
                raise ValueError("History data cannot be empty")
            
            # ✅ VALIDATE: Kiểm tra thứ tự dữ liệu đầu vào
            if len(history_data) >= 2:
                first_date = history_data[0].ngay
                last_date = history_data[-1].ngay
                
                # history_data từ EnhancedPredictView có thứ tự: mới nhất đầu tiên
                if first_date < last_date:
                    logger.warning("⚠️ Data order might be incorrect - first date older than last")
                
                logger.info(f"📅 Input data range: {last_date} to {first_date} ({len(history_data)} days)")
            
            # ✅ CHUẨN BỊ: Đảo ngược để có thứ tự cũ -> mới cho feature extraction
            chronological_data = list(reversed(history_data))
            
            # Extract features với data đã sắp xếp đúng
            features = self._extract_comprehensive_features(chronological_data, target_date)
            
            # Ensure model is trained với data đúng thứ tự
            if not self.is_trained:
                self._train_models(history_data)  # Truyền data gốc, sẽ được xử lý trong _prepare_training_data
            
            # Generate predictions
            predictions = self._generate_ensemble_predictions(features, chronological_data)
            
            # Apply reinforcement learning weights
            predictions = self._apply_rl_weights(predictions)
            
            # Validate results
            validated_predictions = self._validate_and_normalize_predictions(predictions)
            
            logger.info(f"Generated {len(validated_predictions)} predictions for {target_date}")
            return validated_predictions
            
        except Exception as e:
            logger.error(f"Error in predict_for_date: {e}", exc_info=True)
            return self._get_fallback_predictions()
        
    def _extract_comprehensive_features(self, history_data: List, target_date: date) -> np.ndarray:
        """
        ✅ SỬA LỖI: Extract features với thứ tự dữ liệu đúng
        """
        try:
            feature_vector = []
            
            # ✅ ASSUMPTION: history_data đã được sắp xếp cũ -> mới (từ _prepare_training_data)
            
            # 1. Frequency analysis (30 ngày gần nhất)
            frequency_features = self._extract_frequency_features(history_data[-30:])  # ✅ ĐÚNG
            feature_vector.extend(frequency_features)
            
            # 2. Recency analysis (14 ngày gần nhất)
            recency_features = self._extract_recency_features(history_data[-14:])  # ✅ ĐÚNG
            feature_vector.extend(recency_features)
            
            # 3. Cycle detection
            cycle_features = self._extract_cycle_features(history_data)
            feature_vector.extend(cycle_features)
            
            # 4. Pair analysis (21 ngày gần nhất)
            pair_features = self._extract_pair_features(history_data[-21:])  # ✅ ĐÚNG
            feature_vector.extend(pair_features)
            
            # 5. Temporal features
            temporal_features = self._extract_temporal_features(target_date)
            feature_vector.extend(temporal_features)
            
            return np.array(feature_vector).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            return np.zeros((1, 50))
        
    def _extract_frequency_features(self, recent_data: List) -> List[float]:
        """Extract frequency-based features"""
        try:
            number_counts = defaultdict(int)
            
            for record in recent_data:
                numbers = record.get_all_2digit_numbers()
                for num in numbers:
                    number_counts[num] += 1
            
            # Convert to feature vector (top 20 most frequent)
            sorted_numbers = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)
            features = []
            
            for i in range(20):
                if i < len(sorted_numbers):
                    # Normalize frequency
                    freq = sorted_numbers[i][1] / len(recent_data)
                    features.append(freq)
                else:
                    features.append(0.0)
            
            return features
            
        except Exception as e:
            logger.error(f"Frequency feature extraction error: {e}")
            return [0.0] * 20
    
    def _extract_recency_features(self, recent_data: List) -> List[float]:
        """
        ✅ SỬA LỖI: Extract recency features với thứ tự đúng
        """
        try:
            features = []
            
            # ✅ ASSUMPTION: recent_data đã được sắp xếp cũ -> mới
            # Phân tích 3 ngày gần nhất
            for i in range(min(3, len(recent_data))):
                day_index = len(recent_data) - 1 - i  # ✅ Lấy từ cuối về đầu (mới -> cũ)
                
                if day_index >= 0:
                    numbers = recent_data[day_index].get_all_2digit_numbers()
                    # Encode presence of top numbers
                    day_features = [1.0 if f"{n:02d}" in numbers else 0.0 for n in range(10)]
                    features.extend(day_features)
                else:
                    features.extend([0.0] * 10)
            
            return features
            
        except Exception as e:
            logger.error(f"Recency feature extraction error: {e}")
            return [0.0] * 30
        
    def _extract_cycle_features(self, history_data: List) -> List[float]:
        """Extract cycle-based features"""
        try:
            features = []
            
            # Analyze different cycle lengths
            cycle_lengths = [1, 3, 7, 14]
            
            for cycle_len in cycle_lengths:
                if len(history_data) >= cycle_len:
                    cycle_data = history_data[-cycle_len:]
                    
                    # Count unique numbers in cycle
                    all_numbers = set()
                    for record in cycle_data:
                        all_numbers.update(record.get_all_2digit_numbers())
                    
                    # Normalize by cycle length
                    cycle_density = len(all_numbers) / (cycle_len * 20)  # Assuming ~20 numbers per day
                    features.append(cycle_density)
                else:
                    features.append(0.0)
            
            return features
            
        except Exception as e:
            logger.error(f"Cycle feature extraction error: {e}")
            return [0.0] * 4
    
    def _extract_pair_features(self, recent_data: List) -> List[float]:
        """Extract pair analysis features"""
        try:
            pair_counts = defaultdict(int)
            
            for record in recent_data:
                numbers = record.get_all_2digit_numbers()
                for pair in combinations(sorted(numbers), 2):
                    pair_counts[pair] += 1
            
            # Get top 5 pairs and their frequencies
            top_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            features = []
            for i in range(5):
                if i < len(top_pairs):
                    # Normalize frequency
                    freq = top_pairs[i][1] / len(recent_data)
                    features.append(freq)
                else:
                    features.append(0.0)
            
            return features
            
        except Exception as e:
            logger.error(f"Pair feature extraction error: {e}")
            return [0.0] * 5
    
    def _extract_temporal_features(self, target_date: date) -> List[float]:
        """Extract temporal features"""
        try:
            return [
                float(target_date.weekday()) / 6.0,  # Day of week (0-6) normalized
                float(target_date.day) / 31.0,       # Day of month normalized
                float(target_date.month) / 12.0,     # Month normalized
                float((target_date.month - 1) // 3) / 3.0  # Quarter normalized
            ]
        except Exception as e:
            logger.error(f"Temporal feature extraction error: {e}")
            return [0.0] * 4
    
    def _train_models(self, history_data: List) -> bool:
        """Train all models with historical data"""
        try:
            logger.info("Training models with enhanced features...")
            
            # Prepare training data
            X, y = self._prepare_training_data(history_data)
            
            if len(X) < 10:
                logger.warning("Insufficient training data")
                return False
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train Random Forest
            self.models['random_forest'].fit(X_scaled, y)
            
            # Validate training
            cv_scores = cross_val_score(self.models['random_forest'], X_scaled, y, cv=5)
            logger.info(f"Cross-validation scores: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
            
            # Create ensemble model
            self.models['ensemble'] = self._create_ensemble_model(X_scaled, y)
            
            self.is_trained = True
            self._last_trained = timezone.now()
            
            # Save model
            self._save_model()
            
            logger.info("Model training completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
    
    def _prepare_training_data(self, history_data: List) -> Tuple[np.ndarray, np.ndarray]:
        """
        ✅ SỬA LỖI: Chuẩn bị dữ liệu training với thứ tự đúng
        
        Logic đúng:
        - history_data[0] = ngày mới nhất
        - history_data[-1] = ngày cũ nhất
        - Training: dùng 30 ngày cũ để predict ngày mới hơn
        """
        try:
            X, y = [], []
            
            # ✅ SỬA: Đảo ngược data để có thứ tự cũ -> mới
            reversed_data = list(reversed(history_data))
            # Giờ: reversed_data[0] = ngày cũ nhất, reversed_data[-1] = ngày mới nhất
            
            # Create training samples từ cũ đến mới
            for i in range(30, len(reversed_data)):
                # ✅ ĐÚNG: window từ ngày cũ để predict ngày mới hơn
                window_data = reversed_data[i-30:i]  # 30 ngày cũ
                target_record = reversed_data[i]      # Ngày mới hơn để predict
                
                # Extract features từ 30 ngày cũ
                features = self._extract_comprehensive_features(window_data, target_record.ngay)
                X.append(features.flatten())
                
                # Target: numbers của ngày cần predict
                target_numbers = target_record.get_all_2digit_numbers()
                target_vector = [1 if f"{n:02d}" in target_numbers else 0 for n in range(100)]
                y.append(target_vector)
            
            logger.info(f"✅ Prepared {len(X)} training samples with correct temporal order")
            return np.array(X), np.array(y)
            
        except Exception as e:
            logger.error(f"Training data preparation error: {e}")
            return np.array([]), np.array([])
        
    def _generate_ensemble_predictions(self, features: np.ndarray, history_data: List) -> Dict[str, float]:
        """Generate predictions using ensemble of models"""
        try:
            predictions = {}
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Random Forest predictions
            if self.models['random_forest']:
                rf_pred = self.models['random_forest'].predict(features_scaled)[0]
                
                # Convert to number predictions
                for i, confidence in enumerate(rf_pred):
                    number = f"{i:02d}"
                    predictions[number] = float(confidence)
            
            # Add statistical baseline
            stat_predictions = self._get_statistical_predictions(history_data)
            
            # Combine predictions with weights
            combined = {}
            for num in range(100):
                num_str = f"{num:02d}"
                ml_conf = predictions.get(num_str, 0.0)
                stat_conf = stat_predictions.get(num_str, 0.0)
                
                # Weighted combination
                combined[num_str] = 0.7 * ml_conf + 0.3 * stat_conf
            
            return combined
            
        except Exception as e:
            logger.error(f"Ensemble prediction error: {e}")
            return self._get_statistical_predictions(history_data)
    
    def _get_statistical_predictions(self, history_data: List) -> Dict[str, float]:
        """Statistical fallback predictions"""
        try:
            number_counts = defaultdict(int)
            
            # Count frequencies in recent data
            for record in history_data[-30:]:
                for num in record.get_all_2digit_numbers():
                    number_counts[num] += 1
            
            # Normalize to probabilities
            total_count = sum(number_counts.values())
            predictions = {}
            
            for num in range(100):
                num_str = f"{num:02d}"
                count = number_counts.get(num_str, 0)
                predictions[num_str] = count / total_count if total_count > 0 else 0.01
            
            return predictions
            
        except Exception as e:
            logger.error(f"Statistical prediction error: {e}")
            return {f"{i:02d}": 0.01 for i in range(100)}
    
    def _apply_rl_weights(self, predictions: Dict[str, float]) -> Dict[str, float]:
        """Apply reinforcement learning weights"""
        try:
            adjusted = {}
            
            for number, confidence in predictions.items():
                # Apply learned weights
                weight_factor = 1.0 + self.weights.get(number, 0.0)
                adjusted[number] = confidence * weight_factor
            
            return adjusted
            
        except Exception as e:
            logger.error(f"RL weight application error: {e}")
            return predictions
    
    def _validate_and_normalize_predictions(self, predictions: Dict[str, float]) -> Dict[str, float]:
        """Validate and normalize predictions"""
        try:
            # Remove invalid predictions
            valid_predictions = {}
            
            for number, confidence in predictions.items():
                # Validate number format
                if isinstance(number, str) and len(number) == 2 and number.isdigit():
                    # Validate confidence
                    if isinstance(confidence, (int, float)) and 0 <= confidence <= 1:
                        valid_predictions[number] = float(confidence)
            
            if not valid_predictions:
                return self._get_fallback_predictions()
            
            # Normalize so top predictions sum to reasonable value
            max_conf = max(valid_predictions.values())
            if max_conf > 0:
                normalized = {
                    num: conf / max_conf * 0.9  # Scale to max 0.9
                    for num, conf in valid_predictions.items()
                }
            else:
                normalized = valid_predictions
            
            # Sort and return top 20
            sorted_preds = sorted(normalized.items(), key=lambda x: x[1], reverse=True)
            return dict(sorted_preds[:20])
            
        except Exception as e:
            logger.error(f"Prediction validation error: {e}")
            return self._get_fallback_predictions()
    
    def update_weights_from_feedback(self, predictions: Dict[str, float], actual_numbers: List[str]):
        """Update RL weights based on actual results"""
        try:
            learning_rate = 0.1
            
            for number, predicted_conf in predictions.items():
                if number in actual_numbers:
                    # Positive feedback - increase weight
                    self.weights[number] = min(2.0, self.weights[number] + learning_rate)
                else:
                    # Negative feedback - decrease weight
                    self.weights[number] = max(-0.5, self.weights[number] - learning_rate * 0.5)
            
            logger.info(f"Updated weights for {len(predictions)} predictions")
            
        except Exception as e:
            logger.error(f"Weight update error: {e}")
    
    def retrain_with_data(self, new_data: List) -> bool:
        """Retrain model with new data"""
        try:
            logger.info("Retraining model with new data...")
            return self._train_models(new_data)
        except Exception as e:
            logger.error(f"Retrain error: {e}")
            return False
    
    def _get_fallback_predictions(self) -> Dict[str, float]:
        """Fallback predictions when all else fails"""
        # Simple uniform distribution for safety
        return {f"{i:02d}": 0.05 for i in range(20)}
    
    def _save_model(self):
        """Save trained model to disk"""
        try:
            model_data = {
                'models': self.models,
                'scaler': self.scaler,
                'weights': dict(self.weights),
                'version': self.version,
                'trained_at': self._last_trained
            }
            joblib.dump(model_data, f"enhanced_predictor_{self.version}.pkl")
        except Exception as e:
            logger.warning(f"Model save failed: {e}")
    
    def _create_ensemble_model(self, X: np.ndarray, y: np.ndarray):
        """Create ensemble model (placeholder for future enhancement)"""
        # For now, return the trained RF model
        return self.models['random_forest']

class AdvancedLotteryPredictor:
    """
    ✅ TRADITIONAL METHODS PREDICTOR - Simplified and focused
    """
    
    def __init__(self):
        self.methods = {
            "frequency": self._frequency_analysis,
            "pattern": self._pattern_analysis,
            "statistical": self._statistical_analysis
        }
    
    def predict_next_day(self, history_data: List, days: int = 30) -> pd.DataFrame:
        """Predict using traditional methods"""
        try:
            results = []
            
            for method_name, method_func in self.methods.items():
                try:
                    numbers, confidence = method_func(history_data[-days:])
                    results.append({
                        "method": method_name,
                        "numbers": numbers,
                        "confidence": confidence
                    })
                except Exception as e:
                    logger.warning(f"Method {method_name} failed: {e}")
                    results.append({
                        "method": method_name,
                        "numbers": [],
                        "confidence": 0.0
                    })
            
            return pd.DataFrame(results)
            
        except Exception as e:
            logger.error(f"Traditional prediction error: {e}")
            return pd.DataFrame()
    
    def _frequency_analysis(self, data: List) -> Tuple[List[str], float]:
        """Frequency-based analysis"""
        freq = Counter()
        for record in data:
            for num in record.get_all_2digit_numbers():
                freq[num] += 1
        
        top_numbers = [num for num, _ in freq.most_common(10)]
        return top_numbers, 0.6
    
    def _pattern_analysis(self, data: List) -> Tuple[List[str], float]:
        """Pattern-based analysis"""
        if len(data) < 7:
            return [], 0.0
        
        recent_numbers = set()
        for record in data[-7:]:
            recent_numbers.update(record.get_all_2digit_numbers())
        
        return list(recent_numbers)[:8], 0.5
    
    def _statistical_analysis(self, data: List) -> Tuple[List[str], float]:
        """Statistical analysis"""
        number_stats = Counter()
        for record in data:
            for num in record.get_all_2digit_numbers():
                number_stats[num] += 1
        
        avg_freq = sum(number_stats.values()) / len(number_stats) if number_stats else 0
        
        # Numbers with frequency around average
        balanced_numbers = []
        for num, freq in number_stats.items():
            if avg_freq * 0.7 <= freq <= avg_freq * 1.3:
                balanced_numbers.append(num)
        
        return balanced_numbers[:6], 0.4
