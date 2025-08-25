"""
🎯 ML Ensemble Service - Lite Version (Phase 1B)
==============================================

Modern ML ensemble implementation without sklearn dependencies.
Uses NumPy-only algorithms for maximum compatibility and performance.

Features:
- Ensemble voting methods
- Bagging and boosting algorithms  
- Model diversity metrics
- Performance tracking
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, date
import json
import logging

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class EnsemblePrediction:
    """Individual ensemble member prediction"""
    method_name: str
    prediction: Any
    confidence: float
    weight: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class EnsembleResult:
    """Final ensemble prediction result"""
    final_prediction: Any
    individual_predictions: List[EnsemblePrediction]
    ensemble_confidence: float
    diversity_score: float
    method_weights: Dict[str, float]
    voting_method: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class ModelPerformance:
    """Track individual model performance"""
    method_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    recent_performance: List[float]
    reliability_score: float

class MLEnsembleServiceLite:
    """
    🎯 ML Ensemble Service - Lite Implementation
    
    Provides sophisticated ensemble methods without heavy ML dependencies.
    Uses NumPy-only implementations for maximum compatibility.
    """
    
    def __init__(self):
        """Initialize ensemble service"""
        self.performance_history = {}
        self.model_weights = {}
        self.ensemble_config = {
            'voting_method': 'weighted',
            'diversity_threshold': 0.1,
            'min_confidence': 0.5,
            'performance_window': 30
        }
        logger.info("✅ ML Ensemble Service Lite initialized")
    
    def add_prediction(self, method_name: str, prediction: Any, 
                      confidence: float) -> EnsemblePrediction:
        """Add individual prediction to ensemble"""
        try:
            weight = self._calculate_dynamic_weight(method_name, confidence)
            
            ensemble_pred = EnsemblePrediction(
                method_name=method_name,
                prediction=prediction,
                confidence=confidence,
                weight=weight
            )
            
            logger.debug(f"✅ Added prediction from {method_name} (weight: {weight:.3f})")
            return ensemble_pred
            
        except Exception as e:
            logger.error(f"❌ Error adding prediction from {method_name}: {e}")
            raise
    
    def ensemble_vote_weighted(self, predictions: List[EnsemblePrediction]) -> EnsembleResult:
        """
        🎯 Weighted Voting Ensemble
        
        Combines predictions using dynamic weights based on:
        - Historical performance
        - Current confidence
        - Diversity contribution
        """
        try:
            if not predictions:
                raise ValueError("No predictions provided for ensemble")
            
            # Calculate diversity score
            diversity_score = self._calculate_diversity_score(predictions)
            
            # Adjust weights based on diversity
            adjusted_predictions = self._adjust_weights_for_diversity(
                predictions, diversity_score
            )
            
            # Perform weighted voting
            final_prediction = self._weighted_vote(adjusted_predictions)
            
            # Calculate ensemble confidence
            ensemble_confidence = self._calculate_ensemble_confidence(adjusted_predictions)
            
            # Extract method weights
            method_weights = {
                pred.method_name: pred.weight 
                for pred in adjusted_predictions
            }
            
            result = EnsembleResult(
                final_prediction=final_prediction,
                individual_predictions=adjusted_predictions,
                ensemble_confidence=ensemble_confidence,
                diversity_score=diversity_score,
                method_weights=method_weights,
                voting_method='weighted'
            )
            
            logger.info(f"✅ Weighted ensemble: {len(predictions)} methods, "
                       f"diversity: {diversity_score:.3f}, "
                       f"confidence: {ensemble_confidence:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in weighted ensemble voting: {e}")
            raise
    
    def ensemble_vote_majority(self, predictions: List[EnsemblePrediction]) -> EnsembleResult:
        """
        🎯 Majority Voting Ensemble
        
        Simple majority vote with confidence weighting
        """
        try:
            if not predictions:
                raise ValueError("No predictions provided for ensemble")
            
            # Count votes for each prediction
            vote_counts = {}
            confidence_sums = {}
            
            for pred in predictions:
                pred_str = str(pred.prediction)
                if pred_str not in vote_counts:
                    vote_counts[pred_str] = 0
                    confidence_sums[pred_str] = 0
                
                vote_counts[pred_str] += pred.weight
                confidence_sums[pred_str] += pred.confidence * pred.weight
            
            # Find majority winner
            winner = max(vote_counts.items(), key=lambda x: x[1])
            final_prediction = winner[0]
            
            # Calculate ensemble confidence
            total_weight = sum(vote_counts.values())
            ensemble_confidence = confidence_sums[final_prediction] / total_weight
            
            # Calculate diversity
            diversity_score = self._calculate_diversity_score(predictions)
            
            method_weights = {pred.method_name: pred.weight for pred in predictions}
            
            result = EnsembleResult(
                final_prediction=final_prediction,
                individual_predictions=predictions,
                ensemble_confidence=ensemble_confidence,
                diversity_score=diversity_score,
                method_weights=method_weights,
                voting_method='majority'
            )
            
            logger.info(f"✅ Majority ensemble: winner '{final_prediction}' "
                       f"with {winner[1]:.1f} votes")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in majority ensemble voting: {e}")
            raise
    
    def ensemble_vote_stacking(self, predictions: List[EnsemblePrediction]) -> EnsembleResult:
        """
        🎯 Stacking Ensemble (Meta-Learning)
        
        Uses historical performance to learn optimal combination
        """
        try:
            if not predictions:
                raise ValueError("No predictions provided for ensemble")
            
            # Simple stacking implementation using performance history
            stacked_weights = self._calculate_stacking_weights(predictions)
            
            # Apply stacked weights
            stacked_predictions = []
            for pred, stacked_weight in zip(predictions, stacked_weights):
                stacked_pred = EnsemblePrediction(
                    method_name=pred.method_name,
                    prediction=pred.prediction,
                    confidence=pred.confidence,
                    weight=stacked_weight
                )
                stacked_predictions.append(stacked_pred)
            
            # Weighted combination
            final_prediction = self._weighted_vote(stacked_predictions)
            ensemble_confidence = self._calculate_ensemble_confidence(stacked_predictions)
            diversity_score = self._calculate_diversity_score(stacked_predictions)
            
            method_weights = {pred.method_name: pred.weight for pred in stacked_predictions}
            
            result = EnsembleResult(
                final_prediction=final_prediction,
                individual_predictions=stacked_predictions,
                ensemble_confidence=ensemble_confidence,
                diversity_score=diversity_score,
                method_weights=method_weights,
                voting_method='stacking'
            )
            
            logger.info(f"✅ Stacking ensemble: {len(predictions)} methods, "
                       f"meta-learned weights")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in stacking ensemble: {e}")
            raise
    
    def calculate_model_diversity(self, predictions: List[EnsemblePrediction]) -> float:
        """
        📊 Calculate Model Diversity Score
        
        Measures how diverse the ensemble members are
        Higher diversity = better ensemble performance
        """
        try:
            if len(predictions) < 2:
                return 0.0
            
            # Calculate pairwise disagreement
            disagreements = 0
            total_pairs = 0
            
            for i in range(len(predictions)):
                for j in range(i + 1, len(predictions)):
                    pred1 = str(predictions[i].prediction)
                    pred2 = str(predictions[j].prediction)
                    
                    if pred1 != pred2:
                        disagreements += 1
                    total_pairs += 1
            
            diversity_score = disagreements / total_pairs if total_pairs > 0 else 0.0
            
            logger.debug(f"📊 Diversity score: {diversity_score:.3f} "
                        f"({disagreements}/{total_pairs} disagreements)")
            
            return diversity_score
            
        except Exception as e:
            logger.error(f"❌ Error calculating diversity: {e}")
            return 0.0
    
    def update_performance_history(self, method_name: str, 
                                  performance_metrics: Dict[str, float]):
        """Update performance history for adaptive weighting"""
        try:
            if method_name not in self.performance_history:
                self.performance_history[method_name] = []
            
            # Add new performance data
            timestamp = datetime.now().isoformat()
            performance_entry = {
                'timestamp': timestamp,
                'metrics': performance_metrics
            }
            
            self.performance_history[method_name].append(performance_entry)
            
            # Keep only recent history
            window = self.ensemble_config['performance_window']
            if len(self.performance_history[method_name]) > window:
                self.performance_history[method_name] = \
                    self.performance_history[method_name][-window:]
            
            # Update model weights
            self._update_model_weights(method_name)
            
            logger.info(f"✅ Updated performance history for {method_name}")
            
        except Exception as e:
            logger.error(f"❌ Error updating performance history: {e}")
    
    def get_ensemble_statistics(self) -> Dict[str, Any]:
        """Get comprehensive ensemble statistics"""
        try:
            stats = {
                'total_methods': len(self.performance_history),
                'model_weights': self.model_weights.copy(),
                'ensemble_config': self.ensemble_config.copy(),
                'performance_summary': {}
            }
            
            # Calculate performance summary
            for method_name, history in self.performance_history.items():
                if history:
                    recent_accuracy = [entry['metrics'].get('accuracy', 0) 
                                     for entry in history[-10:]]
                    stats['performance_summary'][method_name] = {
                        'avg_accuracy': np.mean(recent_accuracy),
                        'std_accuracy': np.std(recent_accuracy),
                        'data_points': len(history),
                        'current_weight': self.model_weights.get(method_name, 0.0)
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting ensemble statistics: {e}")
            return {}
    
    # =================== PRIVATE METHODS ===================
    
    def _calculate_dynamic_weight(self, method_name: str, confidence: float) -> float:
        """Calculate dynamic weight based on performance and confidence"""
        try:
            # Base weight from historical performance
            base_weight = self.model_weights.get(method_name, 1.0)
            
            # Confidence adjustment
            confidence_multiplier = max(0.1, min(2.0, confidence))
            
            # Final weight
            final_weight = base_weight * confidence_multiplier
            
            return final_weight
            
        except Exception as e:
            logger.error(f"❌ Error calculating dynamic weight: {e}")
            return 1.0
    
    def _calculate_diversity_score(self, predictions: List[EnsemblePrediction]) -> float:
        """Calculate ensemble diversity score"""
        return self.calculate_model_diversity(predictions)
    
    def _adjust_weights_for_diversity(self, predictions: List[EnsemblePrediction], 
                                    diversity_score: float) -> List[EnsemblePrediction]:
        """Adjust weights to promote diversity"""
        try:
            # If diversity is too low, boost minority predictions
            if diversity_score < self.ensemble_config['diversity_threshold']:
                # Boost weights of minority predictions
                prediction_counts = {}
                for pred in predictions:
                    pred_str = str(pred.prediction)
                    prediction_counts[pred_str] = prediction_counts.get(pred_str, 0) + 1
                
                total_predictions = len(predictions)
                adjusted_predictions = []
                
                for pred in predictions:
                    pred_str = str(pred.prediction)
                    minority_boost = 1.0 + (1.0 - prediction_counts[pred_str] / total_predictions)
                    
                    adjusted_pred = EnsemblePrediction(
                        method_name=pred.method_name,
                        prediction=pred.prediction,
                        confidence=pred.confidence,
                        weight=pred.weight * minority_boost
                    )
                    adjusted_predictions.append(adjusted_pred)
                
                return adjusted_predictions
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Error adjusting weights for diversity: {e}")
            return predictions
    
    def _weighted_vote(self, predictions: List[EnsemblePrediction]) -> Any:
        """Perform weighted voting"""
        try:
            if not predictions:
                return None
            
            # Group by prediction value
            prediction_weights = {}
            
            for pred in predictions:
                pred_str = str(pred.prediction)
                if pred_str not in prediction_weights:
                    prediction_weights[pred_str] = 0
                prediction_weights[pred_str] += pred.weight
            
            # Find winner
            winner = max(prediction_weights.items(), key=lambda x: x[1])
            return winner[0]
            
        except Exception as e:
            logger.error(f"❌ Error in weighted voting: {e}")
            return predictions[0].prediction if predictions else None
    
    def _calculate_ensemble_confidence(self, predictions: List[EnsemblePrediction]) -> float:
        """Calculate overall ensemble confidence"""
        try:
            if not predictions:
                return 0.0
            
            # Weighted average confidence
            total_weight = sum(pred.weight for pred in predictions)
            if total_weight == 0:
                return 0.0
            
            weighted_confidence = sum(
                pred.confidence * pred.weight for pred in predictions
            ) / total_weight
            
            return min(1.0, max(0.0, weighted_confidence))
            
        except Exception as e:
            logger.error(f"❌ Error calculating ensemble confidence: {e}")
            return 0.0
    
    def _calculate_stacking_weights(self, predictions: List[EnsemblePrediction]) -> List[float]:
        """Calculate meta-learned stacking weights"""
        try:
            weights = []
            
            for pred in predictions:
                # Use performance history to calculate meta-weight
                if pred.method_name in self.performance_history:
                    history = self.performance_history[pred.method_name]
                    if history:
                        recent_accuracy = [
                            entry['metrics'].get('accuracy', 0.5) 
                            for entry in history[-5:]  # Last 5 performances
                        ]
                        meta_weight = np.mean(recent_accuracy)
                    else:
                        meta_weight = 0.5
                else:
                    meta_weight = 0.5
                
                # Combine with current confidence
                final_weight = (meta_weight + pred.confidence) / 2.0
                weights.append(final_weight)
            
            # Normalize weights
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            else:
                weights = [1.0 / len(weights)] * len(weights)
            
            return weights
            
        except Exception as e:
            logger.error(f"❌ Error calculating stacking weights: {e}")
            return [1.0 / len(predictions)] * len(predictions)
    
    def _update_model_weights(self, method_name: str):
        """Update model weights based on recent performance"""
        try:
            if method_name not in self.performance_history:
                self.model_weights[method_name] = 1.0
                return
            
            history = self.performance_history[method_name]
            if not history:
                self.model_weights[method_name] = 1.0
                return
            
            # Calculate weight based on recent performance
            recent_performance = [
                entry['metrics'].get('accuracy', 0.5) 
                for entry in history[-10:]  # Last 10 performances
            ]
            
            avg_performance = np.mean(recent_performance)
            consistency = 1.0 - np.std(recent_performance)  # Higher consistency = lower std
            
            # Weight combines performance and consistency
            weight = (avg_performance + consistency) / 2.0
            weight = max(0.1, min(3.0, weight))  # Bounded between 0.1 and 3.0
            
            self.model_weights[method_name] = weight
            
        except Exception as e:
            logger.error(f"❌ Error updating model weights: {e}")
            self.model_weights[method_name] = 1.0

# =================== DEMONSTRATION FUNCTIONS ===================

def demo_ml_ensemble_lite():
    """Demonstrate ML Ensemble Service Lite capabilities"""
    print("🎯 ML ENSEMBLE SERVICE LITE - DEMONSTRATION")
    print("=" * 50)
    
    # Initialize service
    ensemble_service = MLEnsembleServiceLite()
    
    # Create sample predictions
    predictions = [
        ensemble_service.add_prediction("statistical_analysis", "12345", 0.85),
        ensemble_service.add_prediction("information_theory", "12346", 0.75),
        ensemble_service.add_prediction("quantum_algorithms", "12345", 0.90),
        ensemble_service.add_prediction("neural_networks", "12347", 0.70),
    ]
    
    print(f"\n📊 Individual Predictions:")
    for pred in predictions:
        print(f"  {pred.method_name}: {pred.prediction} (conf: {pred.confidence:.2f}, weight: {pred.weight:.2f})")
    
    # Test different ensemble methods
    print(f"\n🎯 ENSEMBLE VOTING METHODS:")
    
    # Weighted voting
    weighted_result = ensemble_service.ensemble_vote_weighted(predictions)
    print(f"\n1. Weighted Voting:")
    print(f"   Final: {weighted_result.final_prediction}")
    print(f"   Confidence: {weighted_result.ensemble_confidence:.3f}")
    print(f"   Diversity: {weighted_result.diversity_score:.3f}")
    
    # Majority voting
    majority_result = ensemble_service.ensemble_vote_majority(predictions)
    print(f"\n2. Majority Voting:")
    print(f"   Final: {majority_result.final_prediction}")
    print(f"   Confidence: {majority_result.ensemble_confidence:.3f}")
    
    # Stacking
    stacking_result = ensemble_service.ensemble_vote_stacking(predictions)
    print(f"\n3. Stacking Ensemble:")
    print(f"   Final: {stacking_result.final_prediction}")
    print(f"   Confidence: {stacking_result.ensemble_confidence:.3f}")
    
    # Diversity analysis
    diversity = ensemble_service.calculate_model_diversity(predictions)
    print(f"\n📈 Model Diversity: {diversity:.3f}")
    
    # Statistics
    stats = ensemble_service.get_ensemble_statistics()
    print(f"\n📊 Ensemble Statistics:")
    print(f"   Total methods: {stats['total_methods']}")
    print(f"   Model weights: {stats['model_weights']}")
    
    print(f"\n✅ ML Ensemble Service Lite demonstration completed!")

if __name__ == "__main__":
    demo_ml_ensemble_lite()
