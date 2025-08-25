import shap
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from .evaluator import MethodEvaluator
from datetime import datetime, timedelta

class ShapAnalyzer:
    def __init__(self, target_date):
        # Convert and store the date properly
        if isinstance(target_date, str):
            self.target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        elif isinstance(target_date, datetime):
            self.target_date = target_date.date()
        else:
            self.target_date = target_date  # assuming it's already a date object
            
        self.data = self._prepare_data()
    
    def analyze(self):
        if self.data.empty:
            return {
                'error': 'No data available for analysis',
                'feature_importance': pd.DataFrame(),
                'model_score': 0
            }

        X = self.data.drop('target', axis=1)
        y = self.data['target']
        
        # Handle case where there's only one class
        if len(y.unique()) < 2:
            return {
                'error': 'Insufficient target classes for modeling',
                'feature_importance': pd.DataFrame(columns=['feature', 'importance']),
                'model_score': 0
            }

        # Train model
        model = XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, 
                test_size=0.2,
                stratify=y,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            
            # SHAP analysis
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_test)
            
            return {
                'feature_importance': self._get_feature_importance(explainer, shap_values, X_test),
                'summary_plot': self._generate_summary_plot(shap_values, X_test),
                'model_score': model.score(X_test, y_test),
                'error': None
            }
        except Exception as e:
            return {
                'error': str(e),
                'feature_importance': pd.DataFrame(),
                'model_score': 0
            }
    
    def _prepare_data(self):
        """Prepare data for SHAP analysis"""
        try:
            historical_data = MethodEvaluator(self.target_date).get_training_data()
            
            features = []
            for record in historical_data:
                features.append({
                    'tong_dac_biet': int(record.get('special_sum', 0)),
                    'so_ngay_lap_lai': record.get('repeat_days', 0),
                    'tan_so_30_ngay': record.get('freq_30', 0),
                    'tan_so_90_ngay': record.get('freq_90', 0),
                    'vi_tri': record.get('position', 0),
                    'thu': record.get('weekday', 0),
                    'target': int(record.get('is_hit', 0))
                })
            
            return pd.DataFrame(features)
        except Exception as e:
            print(f"Error preparing data: {e}")
            return pd.DataFrame()
    
    def _get_feature_importance(self, explainer, shap_values, X_test):
        """Prepare feature importance data"""
        try:
            if isinstance(shap_values, list):
                shap_values = np.abs(shap_values[1]).mean(0)
            else:
                shap_values = np.abs(shap_values).mean(0)
                
            importance_df = pd.DataFrame({
                'feature': X_test.columns,
                'importance': shap_values
            }).sort_values('importance', ascending=False)
            
            return importance_df
        except Exception as e:
            print(f"Error getting feature importance: {e}")
            return pd.DataFrame(columns=['feature', 'importance'])
    
    def _generate_summary_plot(self, shap_values, X_test):
        """Generate SHAP summary plot with error handling"""
        try:
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            return shap.summary_plot(shap_values, X_test, show=False)
        except Exception as e:
            print(f"Error generating summary plot: {e}")
            return None