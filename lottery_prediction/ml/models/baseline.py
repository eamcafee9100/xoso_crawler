# ml/models/baseline.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
from collections import Counter, defaultdict
from abc import ABC, abstractmethod
from results.models import KetQuaXoSo, NumberFrequencyStats
import logging

logger = logging.getLogger(__name__)


class BasePredictionModel(ABC):
    """Abstract base class for all prediction models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.is_trained = False
        self.training_data_size = 0
        self.last_train_date = None
        
    @abstractmethod
    def fit(self, *args, **kwargs) -> None:
        """Train the model"""
        pass
    
    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict probabilities for each number"""
        pass
    
    def predict_top_k(self, X: pd.DataFrame, k: int = 10, **kwargs) -> List[Tuple[str, float]]:
        """Predict top k numbers with probabilities"""
        probabilities = self.predict_proba(X, **kwargs)
        
        # Get all numbers (00-99)
        numbers = [f"{i:02d}" for i in range(100)]
        
        # Combine numbers with probabilities
        number_probs = list(zip(numbers, probabilities))
        
        # Sort by probability and return top k
        sorted_predictions = sorted(number_probs, key=lambda x: x[1], reverse=True)
        
        return sorted_predictions[:k]
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'model_name': self.model_name,
            'is_trained': self.is_trained,
            'training_data_size': self.training_data_size,
            'last_train_date': self.last_train_date
        }


class RandomPredictor(BasePredictionModel):
    """Random baseline - predicts numbers randomly"""
    
    def __init__(self, seed: int = 42):
        super().__init__("RandomPredictor")
        self.seed = seed
        np.random.seed(seed)
        
    def fit(self, X: pd.DataFrame = None, y: pd.DataFrame = None, *args, **kwargs) -> None:
        """Random predictor doesn't need training"""
        self.is_trained = True
        self.training_data_size = len(X) if X is not None else 0
        self.last_train_date = datetime.now()
        logger.info(f"{self.model_name} 'trained' (random baseline)")
    
    def predict_proba(self, X: pd.DataFrame = None) -> np.ndarray:
        """Return random probabilities for all 100 numbers"""
        # Generate random probabilities that sum to 1
        probs = np.random.random(100)
        probs = probs / probs.sum()  # Normalize to sum to 1
        return probs


class FrequencyBasedPredictor(BasePredictionModel):
    """Predicts based on historical frequency of numbers"""
    
    def __init__(self, lookback_days: int = 90):
        super().__init__("FrequencyBasedPredictor")
        self.lookback_days = lookback_days
        self.frequency_dict = {}
        
    def fit(self, X: pd.DataFrame = None, y: pd.DataFrame = None, 
            start_date: datetime.date = None, end_date: datetime.date = None) -> None:
        """Train based on historical frequency"""
        if X is not None and y is not None:
            # Train with provided features/labels
            self._fit_with_features(X, y)
        elif start_date is not None and end_date is not None:
            # Train with date range
            self._fit_with_dates(start_date, end_date)
        else:
            # Default to lookback_days from yesterday
            end_date = datetime.now().date() - timedelta(days=1)
            start_date = end_date - timedelta(days=self.lookback_days)
            self._fit_with_dates(start_date, end_date)
    
    def _fit_with_dates(self, start_date: datetime.date, end_date: datetime.date) -> None:
        """Train using date range"""
        from django.db.models import Count
        
        # Count frequency of each number
        frequency_stats = NumberFrequencyStats.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).values('number').annotate(count=Count('id'))
        
        # Convert to dictionary
        self.frequency_dict = {stat['number']: stat['count'] for stat in frequency_stats}
        
        # Ensure all numbers 00-99 are present
        for i in range(100):
            number = f"{i:02d}"
            if number not in self.frequency_dict:
                self.frequency_dict[number] = 0
        
        self.is_trained = True
        self.training_data_size = sum(self.frequency_dict.values())
        self.last_train_date = datetime.now()
        
        logger.info(f"{self.model_name} trained on {self.training_data_size} historical occurrences")
    
    def _fit_with_features(self, X: pd.DataFrame, y: pd.DataFrame) -> None:
        """Train using provided features/labels (not implemented for this simple model)"""
        # For compatibility with sklearn interfaces
        self._fit_with_dates(
            start_date=X['date'].min(),
            end_date=X['date'].max()
        )
        
    def predict_proba(self, X: pd.DataFrame = None, **kwargs) -> np.ndarray:
        """Return probabilities based on historical frequency"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Get frequencies for all numbers in order 00-99
        frequencies = np.array([self.frequency_dict[f"{i:02d}"] for i in range(100)])
        
        # Convert to probabilities (add small epsilon to avoid zeros)
        epsilon = 1e-8
        probabilities = frequencies + epsilon
        probabilities = probabilities / probabilities.sum()
        
        return probabilities


class DayOfWeekPredictor(BasePredictionModel):
    """Predicts based on day-of-week patterns"""
    
    def __init__(self, lookback_days: int = 180):
        super().__init__("DayOfWeekPredictor")
        self.lookback_days = lookback_days
        self.day_patterns = {}  # day_of_week -> {number: frequency}
        
    def fit(self, X: pd.DataFrame = None, y: pd.DataFrame = None,
            start_date: datetime.date = None, end_date: datetime.date = None) -> None:
        """Train based on day-of-week patterns"""
        if X is not None and y is not None:
            # Train with provided features/labels
            self._fit_with_features(X, y)
        elif start_date is not None and end_date is not None:
            # Train with date range
            self._fit_with_dates(start_date, end_date)
        else:
            # Default to lookback_days from yesterday
            end_date = datetime.now().date() - timedelta(days=1)
            start_date = end_date - timedelta(days=self.lookback_days)
            self._fit_with_dates(start_date, end_date)

    def _fit_with_dates(self, start_date: datetime.date, end_date: datetime.date) -> None:
        """Train using date range"""
        from django.db.models import Count
        
        # Get day-of-week patterns
        day_stats = NumberFrequencyStats.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).values('day_of_week', 'number').annotate(count=Count('id'))
        
        # Organize by day of week - FIX: Replace lambda with regular dict
        self.day_patterns = {}
        for day in range(7):
            self.day_patterns[day] = {}
        
        for stat in day_stats:
            day = stat['day_of_week']
            number = stat['number']
            count = stat['count']
            if day not in self.day_patterns:
                self.day_patterns[day] = {}
            self.day_patterns[day][number] = count
        
        # Ensure all days and numbers are represented
        for day in range(7):
            for i in range(100):
                number = f"{i:02d}"
                if number not in self.day_patterns[day]:
                    self.day_patterns[day][number] = 0
        
        self.is_trained = True
        self.training_data_size = sum(
            sum(day_dict.values()) for day_dict in self.day_patterns.values()
        )
        self.last_train_date = datetime.now()
        
        logger.info(f"{self.model_name} trained on day-of-week patterns")
    
    def _fit_with_features(self, X: pd.DataFrame, y: pd.DataFrame) -> None:
        """Train using provided features/labels (not implemented for this simple model)"""
        # For compatibility with sklearn interfaces
        self._fit_with_dates(
            start_date=X['date'].min(),
            end_date=X['date'].max()
        )
        
    def predict_proba(self, X: pd.DataFrame = None, **kwargs) -> np.ndarray:
        """Return probabilities based on target day of week"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        target_date = kwargs.get('target_date')
        if target_date is None:
            target_date = datetime.now().date() + timedelta(days=1)
        
        target_day = target_date.weekday()
        
        # Get frequencies for this day of week
        day_frequencies = self.day_patterns[target_day]
        frequencies = np.array([day_frequencies[f"{i:02d}"] for i in range(100)])
        
        # Convert to probabilities
        epsilon = 1e-8
        probabilities = frequencies + epsilon
        probabilities = probabilities / probabilities.sum()
        
        return probabilities


class CyclicalPredictor(BasePredictionModel):
    """Predicts based on cyclical patterns of number appearances"""
    
    def __init__(self, lookback_days: int = 365):
        super().__init__("CyclicalPredictor")
        self.lookback_days = lookback_days
        self.cycle_patterns = {}  # number -> average_cycle_days
        self.last_appearances = {}  # number -> last_appearance_date
        
    def fit(self, X: pd.DataFrame = None, y: pd.DataFrame = None,
            start_date: datetime.date = None, end_date: datetime.date = None) -> None:
        """Train based on cyclical patterns"""
        if X is not None and y is not None:
            # Train with provided features/labels
            self._fit_with_features(X, y)
        elif start_date is not None and end_date is not None:
            # Train with date range
            self._fit_with_dates(start_date, end_date)
        else:
            # Default to lookback_days from yesterday
            end_date = datetime.now().date() - timedelta(days=1)
            start_date = end_date - timedelta(days=self.lookback_days)
            self._fit_with_dates(start_date, end_date)
    
    def _fit_with_dates(self, start_date: datetime.date, end_date: datetime.date) -> None:
        """Train using date range"""
        # Get all appearances for each number
        appearances = NumberFrequencyStats.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('number', 'date')
        
        # Group by number - FIX: Replace defaultdict with regular dict
        number_appearances = {}
        for appearance in appearances:
            if appearance.number not in number_appearances:
                number_appearances[appearance.number] = []
            number_appearances[appearance.number].append(appearance.date)
        
        # Calculate cycle patterns
        for number, dates in number_appearances.items():
            if len(dates) >= 2:
                # Calculate gaps between consecutive appearances
                gaps = []
                for i in range(1, len(dates)):
                    gap = (dates[i] - dates[i-1]).days
                    gaps.append(gap)
                
                # Average cycle
                self.cycle_patterns[number] = np.mean(gaps) if gaps else 30
                self.last_appearances[number] = dates[-1]
            else:
                self.cycle_patterns[number] = 30  # Default cycle
                self.last_appearances[number] = dates[0] if dates else end_date
        
        # Ensure all numbers are represented
        for i in range(100):
            number = f"{i:02d}"
            if number not in self.cycle_patterns:
                self.cycle_patterns[number] = 30
                self.last_appearances[number] = end_date - timedelta(days=30)
        
        self.is_trained = True
        self.training_data_size = len(appearances)
        self.last_train_date = datetime.now()
        
        logger.info(f"{self.model_name} trained on cyclical patterns")
    
    def _fit_with_features(self, X: pd.DataFrame, y: pd.DataFrame) -> None:
        """Train using provided features/labels (not implemented for this simple model)"""
        # For compatibility with sklearn interfaces
        self._fit_with_dates(
            start_date=X['date'].min(),
            end_date=X['date'].max()
        )
        
    def predict_proba(self, X: pd.DataFrame = None, **kwargs) -> np.ndarray:
        """Return probabilities based on cyclical patterns"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        target_date = kwargs.get('target_date')
        if target_date is None:
            target_date = datetime.now().date() + timedelta(days=1)
        
        probabilities = []
        
        for i in range(100):
            number = f"{i:02d}"
            
            # Days since last appearance
            days_since_last = (target_date - self.last_appearances[number]).days
            expected_cycle = self.cycle_patterns[number]
            
            # Probability based on how close we are to expected cycle
            if expected_cycle > 0:
                cycle_ratio = days_since_last / expected_cycle
                # Higher probability when we're close to or past the expected cycle
                probability = max(0, min(1, cycle_ratio))
            else:
                probability = 0.5
            
            probabilities.append(probability)
        
        # Normalize probabilities
        probabilities = np.array(probabilities)
        probabilities = probabilities / probabilities.sum()
        
        return probabilities


class EnsembleBaseline(BasePredictionModel):
    """Simple ensemble of baseline models"""
    
    def __init__(self, models: List[BasePredictionModel], weights: List[float] = None):
        super().__init__("EnsembleBaseline")
        self.models = models
        self.weights = weights or [1.0] * len(models)
        
        if len(self.weights) != len(self.models):
            raise ValueError("Number of weights must match number of models")
        
        # Normalize weights
        total_weight = sum(self.weights)
        self.weights = [w / total_weight for w in self.weights]
    
    def fit(self, X: pd.DataFrame = None, y: pd.DataFrame = None,
            start_date: datetime.date = None, end_date: datetime.date = None) -> None:
        """Train all constituent models"""
        logger.info(f"Training ensemble of {len(self.models)} models...")
        
        total_training_size = 0
        for model in self.models:
            model.fit(X=X, y=y, start_date=start_date, end_date=end_date)
            total_training_size += model.training_data_size
        
        self.is_trained = True
        self.training_data_size = total_training_size
        self.last_train_date = datetime.now()
        
        logger.info(f"Ensemble training completed")
    
    def predict_proba(self, X: pd.DataFrame = None, **kwargs) -> np.ndarray:
        """Ensemble prediction using weighted average"""
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before prediction")
        
        target_date = kwargs.get('target_date')
        ensemble_probs = np.zeros(100)
        
        for model, weight in zip(self.models, self.weights):
            if hasattr(model, 'predict_proba') and callable(getattr(model, 'predict_proba')):
                # Check if model supports target_date parameter
                try:
                    model_probs = model.predict_proba(X, target_date=target_date)
                except TypeError:
                    # Model doesn't support target_date parameter
                    model_probs = model.predict_proba(X)
                
                ensemble_probs += weight * model_probs
        
        # Ensure probabilities sum to 1
        ensemble_probs = ensemble_probs / ensemble_probs.sum()
        
        return ensemble_probs
    
    def get_model_info(self) -> Dict:
        """Get ensemble model information"""
        base_info = super().get_model_info()
        base_info['constituent_models'] = [
            {
                'name': model.model_name,
                'weight': weight,
                'info': model.get_model_info()
            }
            for model, weight in zip(self.models, self.weights)
        ]
        return base_info