import numpy as np
import pandas as pd
import shap
import logging
import pickle
import os
import warnings
from datetime import datetime, timedelta
from django.core.cache import cache
from sklearn.ensemble import RandomForestRegressor

logger = logging.getLogger(__name__)

class SHAPAnalysisService:
    """
    Service chuyên biệt cho phân tích SHAP
    Tương thích với MLModelService và EnhancedMLModelTrainer (12 features)
    """
    
    def __init__(self, ml_service=None):
        self.ml_service = ml_service
        self.cache_duration = 60 * 60 * 12  # 12 hours
        self.shap_cache_dir = 'shap_cache'
        self._ensure_cache_dir()
        self.explainers = {}
        
        # Synchronized feature names with MLModelService/EnhancedMLModelTrainer (12 features)
        self.feature_names = [
            'so_dau', 'so_cuoi', 'tong_giai_db', 'chu_so_cuoi', 
            'tong_cham_dau', 'tong_cham_duoi', 'cham_dau_unique',
            'cham_duoi_unique', 'tong_de', 'avg_tong_de_7days', 
            'std_tong_de_7days', 'pattern_score'
        ]
        
        # Feature descriptions for interpretation
        self.feature_descriptions = {
            'so_dau': 'Số đầu của giải đặc biệt',
            'so_cuoi': 'Số cuối của giải đặc biệt',
            'tong_giai_db': 'Tổng giải đặc biệt',
            'chu_so_cuoi': 'Chữ số cuối của tổng',
            'tong_cham_dau': 'Tổng số chạm đầu',
            'tong_cham_duoi': 'Tổng số chạm đuôi',
            'cham_dau_unique': 'Số loại chạm đầu unique',
            'cham_duoi_unique': 'Số loại chạm đuôi unique',
            'tong_de': 'Tổng đề',
            'avg_tong_de_7days': 'Trung bình tổng đề 7 ngày',
            'std_tong_de_7days': 'Độ lệch chuẩn tổng đề 7 ngày',
            'pattern_score': 'Điểm pattern'
        }

    def _ensure_cache_dir(self):
        """Tạo thư mục cache SHAP nếu chưa có"""
        try:
            os.makedirs(self.shap_cache_dir, exist_ok=True)
        except Exception as e:
            logger.warning(f"Cannot create SHAP cache directory: {e}")
        
    def calculate_shap_values(self, model_name, X_sample, feature_names=None):
        """
        Tính toán SHAP values cho model với enhanced error handling
        
        Args:
            model_name: Tên model (random_forest, gradient_boost, neural_network, ensemble)
            X_sample: Sample dữ liệu để tính SHAP
            feature_names: Danh sách tên features (optional)
            
        Returns:
            dict: Kết quả phân tích SHAP hoặc None nếu lỗi
        """
        try:
            # Validate inputs
            if not self.ml_service:
                logger.warning("ML service not available for SHAP analysis")
                return self._get_mock_shap_analysis()
                
            if model_name not in self.ml_service.models:
                logger.warning(f"Model {model_name} not available for SHAP analysis")
                return self._get_mock_shap_analysis()
                
            if X_sample is None or len(X_sample) == 0:
                logger.warning("No sample data provided for SHAP analysis")
                return self._get_mock_shap_analysis()
            
            # Check feature count compatibility
            expected_features = len(self.feature_names)
            if X_sample.shape[1] != expected_features:
                logger.warning(f"Feature count mismatch: expected {expected_features}, got {X_sample.shape[1]}")
                return self._get_mock_shap_analysis()
            
            # Kiểm tra cache trước
            cache_key = f"shap_{model_name}_{hash(str(X_sample.shape))}_{X_sample.shape[1]}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                logger.info(f"Retrieved SHAP analysis from cache for {model_name}")
                return cached_result
                
            model = self.ml_service.models[model_name]
            
            # Use provided feature names or default ones
            if feature_names is None:
                feature_names = self.feature_names
                
            # Validate feature names count
            if len(feature_names) != expected_features:
                logger.warning(f"Feature names count mismatch, using default names")
                feature_names = self.feature_names
            
            # Prepare sample data for SHAP (use last 20 samples)
            sample_size = min(20, len(X_sample))
            X_shap = X_sample[-sample_size:]
            
            # Calculate SHAP values with error handling
            try:
                if hasattr(model, 'predict') and callable(getattr(model, 'predict')):
                    # Test model prediction first
                    test_pred = model.predict(X_shap[:1])
                    
                    # Create appropriate explainer
                    if isinstance(model, RandomForestRegressor):
                        explainer = shap.TreeExplainer(model)
                        shap_values = explainer.shap_values(X_shap)
                    else:
                        # For other models, use a smaller background set
                        background_size = min(50, len(X_sample))
                        background = X_sample[-background_size:]
                        explainer = shap.KernelExplainer(model.predict, background)
                        shap_values = explainer.shap_values(X_shap)
                        
                else:
                    logger.warning(f"Model {model_name} doesn't have predict method")
                    return self._get_mock_shap_analysis()
                    
            except Exception as model_error:
                logger.warning(f"Error calculating SHAP values: {model_error}")
                return self._get_mock_shap_analysis()
            
            # Phân tích kết quả
            analysis_result = self._analyze_shap_values(
                shap_values, X_shap, feature_names
            )
            
            # Add model info
            analysis_result['model_name'] = model_name
            analysis_result['sample_size'] = sample_size
            analysis_result['calculation_method'] = 'TreeExplainer' if isinstance(model, RandomForestRegressor) else 'KernelExplainer'
            
            # Cache kết quả
            try:
                cache.set(cache_key, analysis_result, self.cache_duration)
            except Exception as cache_error:
                logger.warning(f"Failed to cache SHAP result: {cache_error}")
            
            logger.info(f"SHAP analysis completed for {model_name}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in SHAP analysis: {e}", exc_info=True)
            return self._get_mock_shap_analysis()
    
    def _analyze_shap_values(self, shap_values, X_sample, feature_names):
        """
        Phân tích SHAP values và tạo insights với enhanced processing
        """
        try:
            # Convert to numpy if needed
            if hasattr(shap_values, 'values'):
                shap_values = shap_values.values
            
            # Ensure we have 2D array
            if len(shap_values.shape) == 1:
                shap_values = shap_values.reshape(1, -1)
            
            # Feature importance (trung bình absolute SHAP values)
            feature_importance = np.mean(np.abs(shap_values), axis=0)
            
            # Handle potential NaN values
            feature_importance = np.nan_to_num(feature_importance, nan=0.0)
            
            # Tạo ranking features
            feature_ranking = []
            for i in np.argsort(feature_importance)[::-1]:
                feature_ranking.append({
                    'feature': feature_names[i],
                    'feature_description': self.feature_descriptions.get(feature_names[i], feature_names[i]),
                    'importance': float(feature_importance[i]),
                    'rank': len(feature_ranking) + 1
                })
            
            # Phân tích positive/negative impact
            positive_impact = np.mean(np.maximum(shap_values, 0), axis=0)
            negative_impact = np.mean(np.minimum(shap_values, 0), axis=0)
            
            # Handle NaN values
            positive_impact = np.nan_to_num(positive_impact, nan=0.0)
            negative_impact = np.nan_to_num(negative_impact, nan=0.0)
            
            # Top contributing features
            top_features = feature_ranking[:5]
            
            # Insights về patterns
            insights = self._generate_shap_insights(
                shap_values, X_sample, feature_names, feature_importance
            )
            
            return {
                'feature_ranking': feature_ranking,
                'top_features': top_features,
                'feature_importance': feature_importance.tolist(),
                'positive_impact': positive_impact.tolist(),
                'negative_impact': negative_impact.tolist(),
                'insights': insights,
                'sample_size': X_sample.shape[0],
                'num_features': len(feature_names),
                'total_importance': float(np.sum(feature_importance)),
                'calculation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing SHAP values: {e}")
            return self._get_default_analysis_result(feature_names)
    
    def _generate_shap_insights(self, shap_values, X_sample, feature_names, feature_importance):
        """
        Tạo insights từ SHAP analysis với enhanced interpretation
        """
        insights = []
        
        try:
            if len(feature_importance) == 0:
                return insights
                
            # 1. Feature quan trọng nhất
            most_important_idx = np.argmax(feature_importance)
            if most_important_idx < len(feature_names):
                most_important_feature = feature_names[most_important_idx]
                feature_desc = self.feature_descriptions.get(most_important_feature, most_important_feature)
                
                insights.append({
                    'type': 'most_important',
                    'message': f"Yếu tố quan trọng nhất: {feature_desc}",
                    'feature': most_important_feature,
                    'importance': float(feature_importance[most_important_idx]),
                    'percentage': float(feature_importance[most_important_idx] / np.sum(feature_importance) * 100) if np.sum(feature_importance) > 0 else 0
                })
            
            # 2. Features có impact tích cực
            positive_features = []
            for i, feature in enumerate(feature_names):
                if i < len(shap_values[0]):
                    avg_positive = np.mean(np.maximum(shap_values[:, i], 0))
                    if avg_positive > 0.01:  # Threshold
                        positive_features.append((feature, avg_positive))
            
            if positive_features:
                positive_features.sort(key=lambda x: x[1], reverse=True)
                top_positive = positive_features[0]
                feature_desc = self.feature_descriptions.get(top_positive[0], top_positive[0])
                
                insights.append({
                    'type': 'positive_impact',
                    'message': f"Tác động tích cực nhất: {feature_desc}",
                    'feature': top_positive[0],
                    'impact': float(top_positive[1])
                })
            
            # 3. Stability analysis
            if shap_values.shape[0] > 1:
                feature_std = np.std(shap_values, axis=0)
                avg_std = np.mean(feature_std)
                stable_features = [
                    feature_names[i] for i, std in enumerate(feature_std)
                    if i < len(feature_names) and std < avg_std * 0.5
                ]
                
                if stable_features:
                    stable_descriptions = [
                        self.feature_descriptions.get(f, f) for f in stable_features[:3]
                    ]
                    insights.append({
                        'type': 'stability',
                        'message': f"Yếu tố ổn định: {', '.join(stable_descriptions)}",
                        'features': stable_features[:3],
                        'count': len(stable_features)
                    })
            
            # 4. Overall pattern
            total_positive = np.sum(np.maximum(shap_values, 0))
            total_negative = np.sum(np.minimum(shap_values, 0))
            
            if abs(total_positive) > abs(total_negative):
                insights.append({
                    'type': 'overall_pattern',
                    'message': 'Các yếu tố chủ yếu có tác động tích cực đến dự đoán',
                    'positive_ratio': float(total_positive / (abs(total_positive) + abs(total_negative))) if (abs(total_positive) + abs(total_negative)) > 0 else 0.5
                })
            else:
                insights.append({
                    'type': 'overall_pattern',
                    'message': 'Các yếu tố chủ yếu có tác động tiêu cực đến dự đoán',
                    'positive_ratio': float(total_positive / (abs(total_positive) + abs(total_negative))) if (abs(total_positive) + abs(total_negative)) > 0 else 0.5
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating SHAP insights: {e}")
            return [{
                'type': 'error',
                'message': 'Không thể tạo insights từ SHAP analysis',
                'error': str(e)
            }]
    
    def _get_mock_shap_analysis(self):
        """Enhanced mock SHAP analysis với real feature names"""
        try:
            mock_importance = np.random.uniform(0.01, 0.3, len(self.feature_names))
            mock_importance = mock_importance / np.sum(mock_importance)  # Normalize
            
            feature_ranking = [
                {
                    'feature': self.feature_names[i],
                    'feature_description': self.feature_descriptions.get(self.feature_names[i], self.feature_names[i]),
                    'importance': float(mock_importance[i]),
                    'rank': i + 1
                }
                for i in np.argsort(mock_importance)[::-1]
            ]
            
            return {
                'feature_ranking': feature_ranking,
                'top_features': feature_ranking[:5],
                'feature_importance': mock_importance.tolist(),
                'positive_impact': (mock_importance * 0.6).tolist(),
                'negative_impact': (-mock_importance * 0.4).tolist(),
                'insights': self._generate_mock_insights(feature_ranking[0]),
                'sample_size': 20,
                'num_features': len(self.feature_names),
                'is_mock': True,
                'message': 'Sử dụng dữ liệu mô phỏng do không thể tính SHAP thực tế'
            }
        except Exception as e:
            logger.error(f"Error generating mock SHAP: {e}")
            return self._get_default_analysis_result(self.feature_names)
    
    def _generate_mock_insights(self, top_feature):
        """Generate mock insights"""
        return [
            {
                'type': 'most_important',
                'message': f"Yếu tố quan trọng nhất: {top_feature['feature_description']}",
                'feature': top_feature['feature'],
                'importance': top_feature['importance']
            },
            {
                'type': 'mock_analysis',
                'message': 'Đây là phân tích mô phỏng, cần dữ liệu thực để có kết quả chính xác'
            }
        ]
    
    def _get_default_analysis_result(self, feature_names):
        """Default analysis result when all else fails"""
        return {
            'feature_ranking': [],
            'top_features': [],
            'feature_importance': [0.0] * len(feature_names),
            'positive_impact': [0.0] * len(feature_names),
            'negative_impact': [0.0] * len(feature_names),
            'insights': [{
                'type': 'error',
                'message': 'Không thể thực hiện phân tích SHAP'
            }],
            'sample_size': 0,
            'num_features': len(feature_names),
            'error': True
        }

    def save_shap_plot(self, shap_values, X_sample, feature_names, plot_type='summary'):
        """
        Lưu SHAP plots với enhanced error handling
        """
        try:
            try:
                import matplotlib.pyplot as plt
            except ImportError:
                logger.warning("Matplotlib not available for SHAP plots")
                return None
                        
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"shap_{plot_type}_{timestamp}.png"
            filepath = os.path.join(self.shap_cache_dir, filename)
            
            plt.figure(figsize=(10, 6))
            
            if plot_type == 'summary':
                shap.summary_plot(shap_values, X_sample, feature_names, show=False)
            elif plot_type == 'bar':
                shap.plots.bar(shap_values, show=False)
                
            plt.savefig(filepath, bbox_inches='tight', dpi=150)
            plt.close()
            
            logger.info(f"SHAP plot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving SHAP plot: {e}")
            return None
    
    def cleanup_old_cache(self, days_old=7):
        """
        Dọn dẹp cache cũ với enhanced error handling
        """
        try:
            if not os.path.exists(self.shap_cache_dir):
                return
                
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            for filename in os.listdir(self.shap_cache_dir):
                try:
                    filepath = os.path.join(self.shap_cache_dir, filename)
                    
                    if os.path.isfile(filepath):
                        file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
                        
                        if file_date < cutoff_date:
                            os.remove(filepath)
                            cleaned_count += 1
                            logger.debug(f"Removed old SHAP cache: {filename}")
                except Exception as file_error:
                    logger.warning(f"Failed to process cache file {filename}: {file_error}")
                    
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old SHAP cache files")
                        
        except Exception as e:
            logger.error(f"Error cleaning up SHAP cache: {e}")

    def analyze_predictions(self, historical_data, model_name='ensemble'):
        """
        Analyze predictions using SHAP với enhanced integration
        """
        try:
            if not historical_data or len(historical_data) < 10:
                return {
                    'error': 'Insufficient data for SHAP analysis',
                    'feature_contributions': {},
                    'top_features': [],
                    'interpretation': 'Không đủ dữ liệu để phân tích SHAP',
                    'is_mock': True
                }
            
            # Try to get real SHAP analysis if ML service is available
            if self.ml_service and hasattr(self.ml_service, 'extract_features'):
                try:
                    # Extract features from historical data
                    features = self.ml_service.extract_features(historical_data)
                    
                    if len(features) > 0:
                        # Calculate SHAP values
                        shap_result = self.calculate_shap_values(model_name, features, self.feature_names)
                        
                        if shap_result and not shap_result.get('error'):
                            return {
                                'feature_contributions': {
                                    f['feature']: f['importance'] 
                                    for f in shap_result['feature_ranking']
                                },
                                'top_features': shap_result['top_features'],
                                'plots': {'summary_plot': None},  # Could implement plot generation
                                'interpretation': self._generate_interpretation_from_shap(shap_result),
                                'shap_analysis': shap_result,
                                'is_real': True
                            }
                except Exception as ml_error:
                    logger.warning(f"Failed to get real SHAP analysis: {ml_error}")
            
            # Fallback to enhanced mock analysis
            return self._get_enhanced_mock_analysis()
            
        except Exception as e:
            logger.error(f"SHAP analysis failed: {e}")
            return {
                'error': str(e),
                'feature_contributions': {},
                'top_features': [],
                'interpretation': 'Lỗi trong quá trình phân tích SHAP',
                'is_mock': True
            }
    
    def _get_enhanced_mock_analysis(self):
        """Enhanced mock analysis với realistic feature importance"""
        feature_contributions = {}
        
        # Realistic weights based on lottery analysis experience
        realistic_weights = {
            'tong_de': 0.25,
            'pattern_score': 0.18,
            'avg_tong_de_7days': 0.15,
            'tong_cham_dau': 0.12,
            'tong_cham_duoi': 0.10,
            'so_dau': 0.08,
            'so_cuoi': 0.06,
            'std_tong_de_7days': 0.04,
            'chu_so_cuoi': 0.02
        }
        
        # Assign weights to all features
        for feature in self.feature_names:
            weight = realistic_weights.get(feature, 0.01)
            feature_contributions[feature] = weight + np.random.uniform(-0.02, 0.02)
        
        # Normalize
        total = sum(feature_contributions.values())
        feature_contributions = {k: v/total for k, v in feature_contributions.items()}
        
        top_features = [
            {
                'name': feature,
                'impact': contribution,
                'description': self.feature_descriptions.get(feature, feature)
            }
            for feature, contribution in sorted(
                feature_contributions.items(), 
                key=lambda x: abs(x[1]), 
                reverse=True
            )[:5]
        ]
        
        interpretation = self._generate_interpretation(top_features)
        
        return {
            'feature_contributions': feature_contributions,
            'top_features': top_features,
            'plots': self._generate_mock_plots(),
            'interpretation': interpretation,
            'is_mock': True,
            'message': 'Sử dụng phân tích mô phỏng với trọng số thực tế'
        }
    
    def _generate_interpretation_from_shap(self, shap_result):
        """Generate interpretation from real SHAP results"""
        if not shap_result or not shap_result.get('insights'):
            return "Không thể tạo giải thích từ kết quả SHAP"
        
        insights = shap_result['insights']
        interpretation_parts = []
        
        for insight in insights:
            if insight.get('type') == 'most_important':
                interpretation_parts.append(insight['message'])
            elif insight.get('type') == 'positive_impact':
                interpretation_parts.append(insight['message'])
            elif insight.get('type') == 'overall_pattern':
                interpretation_parts.append(insight['message'])
        
        return ' '.join(interpretation_parts) if interpretation_parts else "Phân tích SHAP hoàn thành"
    
    def _get_top_features(self, contributions):
        """Get top contributing features"""
        sorted_features = sorted(
            contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        return [
            {
                'name': name,
                'impact': contribution,
                'description': self.feature_descriptions.get(name, name)
            }
            for name, contribution in sorted_features[:5]
        ]
    
    def _generate_interpretation(self, top_features):
        """Generate human-readable interpretation"""
        if not top_features:
            return "Không có đủ thông tin để phân tích"
        
        top_feature = top_features[0]
        interpretation = f"Yếu tố quan trọng nhất là '{top_feature['description']}' "
        interpretation += f"với mức độ ảnh hưởng {abs(top_feature['impact']):.3f}. "
        
        if top_feature['impact'] > 0:
            interpretation += "Yếu tố này có tác động tích cực đến khả năng xuất hiện của số."
        else:
            interpretation += "Yếu tố này có tác động tiêu cực đến khả năng xuất hiện của số."
            
        return interpretation
    
    def _generate_mock_plots(self):
        """Generate mock plot data"""
        return {
            'waterfall_plot': None,  # Would contain plot data
            'summary_plot': None,
            'dependence_plots': None
        }
    
    def get_feature_descriptions(self):
        """Get all feature descriptions"""
        return self.feature_descriptions.copy()
    
    def validate_compatibility(self):
        """Validate compatibility with current ML service"""
        try:
            if not self.ml_service:
                return {
                    'compatible': False,
                    'message': 'No ML service available',
                    'feature_count': len(self.feature_names)
                }
            
            ml_features = getattr(self.ml_service, 'feature_names', [])
            
            return {
                'compatible': len(ml_features) == len(self.feature_names),
                'shap_features': len(self.feature_names),
                'ml_features': len(ml_features),
                'message': 'Compatible' if len(ml_features) == len(self.feature_names) else 'Feature count mismatch'
            }
            
        except Exception as e:
            return {
                'compatible': False,
                'message': f'Validation error: {str(e)}',
                'feature_count': len(self.feature_names)
            }