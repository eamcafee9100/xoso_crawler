import os
import pickle
import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.linear_model import Ridge
from django.utils import timezone
from django.core.cache import cache
from results.models import KetQuaXoSo, PredictionPerformanceMetrics
import shap
from collections import Counter

logger = logging.getLogger(__name__)

class MLModelService:
    """
    Service class để quản lý việc huấn luyện và sử dụng các ML models
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = [
            'number_value', 'frequency_last_30days', 'frequency_last_7days', 
            'days_since_last', 'frequency_overall', 'position_frequency',
            'weekday', 'day_of_month', 'recent_trend', 'digit_sum',
            'first_digit', 'second_digit', 'is_even', 'is_palindrome'
        ]
        self.model_versions = {}
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models"""
        model_dir = os.path.join('results', 'ml_models')
        if not os.path.exists(model_dir):
            logger.warning(f"Model directory {model_dir} does not exist")
            return
        
        model_files = {
            'random_forest': 'random_forest_*.pkl',
            'gradient_boosting': 'gradient_boosting_*.pkl', 
            'extra_trees': 'extra_trees_*.pkl',
            'ridge': 'ridge_*.pkl'
        }
        
        for model_name, pattern in model_files.items():
            try:
                # Find the most recent model file
                import glob
                files = glob.glob(os.path.join(model_dir, pattern))
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    with open(latest_file, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
                    logger.info(f"Loaded {model_name} from {os.path.basename(latest_file)}")
                    self.model_versions[model_name] = os.path.basename(latest_file)
            except Exception as e:
                logger.error(f"Failed to load {model_name}: {e}")
        
        logger.info(f"Successfully loaded {len(self.models)} models")
    
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
    
    def _extract_features_for_number(self, number, target_date, historical_data):
        """Extract features for a specific number"""
        try:
            if not isinstance(number, str) or len(number) != 2:
                return None
            
            features = {}
            
            # Basic number features
            features['number_value'] = int(number)
            
            # Historical frequency features
            all_numbers_30d = []
            all_numbers_7d = []
            all_numbers_overall = []
            
            for i, data in enumerate(historical_data):
                numbers = data.get('numbers', [])
                all_numbers_overall.extend(numbers)
                
                if i < 30:  # Last 30 days
                    all_numbers_30d.extend(numbers)
                if i < 7:   # Last 7 days
                    all_numbers_7d.extend(numbers)
            
            features['frequency_last_30days'] = all_numbers_30d.count(number)
            features['frequency_last_7days'] = all_numbers_7d.count(number)
            features['frequency_overall'] = all_numbers_overall.count(number)
            
            # Days since last appearance
            days_since = 999
            for i, data in enumerate(historical_data):
                if number in data.get('numbers', []):
                    days_since = i
                    break
            features['days_since_last'] = days_since
            
            # Position frequency (assume random for now)
            features['position_frequency'] = features['frequency_overall'] / max(1, len(historical_data))
            
            # Date-based features
            features['weekday'] = target_date.weekday()
            features['day_of_month'] = target_date.day
            
            # Recent trend (frequency in last 7 days vs last 30 days)
            recent_freq = features['frequency_last_7days'] / max(1, 7)
            overall_freq = features['frequency_last_30days'] / max(1, 30)
            features['recent_trend'] = recent_freq - overall_freq
            
            # Number pattern features
            first_digit = int(number[0])
            second_digit = int(number[1])
            
            features['digit_sum'] = first_digit + second_digit
            features['first_digit'] = first_digit
            features['second_digit'] = second_digit
            features['is_even'] = 1 if int(number) % 2 == 0 else 0
            features['is_palindrome'] = 1 if number[0] == number[1] else 0
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features for number {number}: {e}")
            return None
    
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
    
    def get_recent_accuracy(self):
        """Get recent model accuracy"""
        try:
            # This would typically check against actual results
            # For now, return a placeholder
            return 0.65
        except:
            return 0.0
    
    def get_model_versions(self):
        """Get model version information"""
        return self.model_versions
    
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
        except:
            pass
        
        return None
    
    def get_model_accuracy(self):
        """Get overall model accuracy"""
        return 0.7  # Placeholder

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