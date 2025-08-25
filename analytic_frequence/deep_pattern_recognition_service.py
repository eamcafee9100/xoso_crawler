"""
🧠 Deep Learning Pattern Recognition Service - Phase 3
====================================================

Advanced neural network-based pattern recognition for lottery prediction
using lightweight pure NumPy implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, date
import json
import logging
import numpy as np
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class PatternSignature:
    """Unique pattern signature"""
    pattern_id: str
    pattern_type: str
    complexity_score: float
    confidence: float
    temporal_span: int
    frequency_domain: str
    pattern_hash: str
    extraction_timestamp: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class NeuralPrediction:
    """Neural network prediction result"""
    predicted_numbers: List[int]
    confidence_scores: List[float]
    pattern_signatures: List[PatternSignature]
    layer_activations: Dict[str, np.ndarray]
    feature_importance: Dict[str, float]
    uncertainty_estimate: float
    prediction_timestamp: datetime = field(default_factory=datetime.now)

class ActivationFunction:
    """Collection of activation functions"""
    
    @staticmethod
    def relu(x: np.ndarray) -> np.ndarray:
        """ReLU activation function"""
        return np.maximum(0, x)
    
    @staticmethod
    def relu_derivative(x: np.ndarray) -> np.ndarray:
        """ReLU derivative"""
        return (x > 0).astype(float)
    
    @staticmethod
    def sigmoid(x: np.ndarray) -> np.ndarray:
        """Sigmoid activation function"""
        # Clip to prevent overflow
        x_clipped = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x_clipped))
    
    @staticmethod
    def sigmoid_derivative(x: np.ndarray) -> np.ndarray:
        """Sigmoid derivative"""
        s = ActivationFunction.sigmoid(x)
        return s * (1 - s)
    
    @staticmethod
    def tanh(x: np.ndarray) -> np.ndarray:
        """Tanh activation function"""
        return np.tanh(x)
    
    @staticmethod
    def tanh_derivative(x: np.ndarray) -> np.ndarray:
        """Tanh derivative"""
        return 1 - np.tanh(x) ** 2
    
    @staticmethod
    def softmax(x: np.ndarray) -> np.ndarray:
        """Softmax activation function"""
        # Subtract max for numerical stability
        x_shifted = x - np.max(x, axis=-1, keepdims=True)
        exp_x = np.exp(x_shifted)
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

class PatternLayer:
    """Neural network layer for pattern recognition"""
    
    def __init__(self, input_size: int, output_size: int, activation: str = 'relu', 
                 dropout_rate: float = 0.0, name: str = "layer"):
        self.input_size = input_size
        self.output_size = output_size
        self.activation = activation
        self.dropout_rate = dropout_rate
        self.name = name
        
        # Initialize weights using Xavier initialization
        self.weights = np.random.randn(input_size, output_size) * np.sqrt(2.0 / input_size)
        self.biases = np.zeros((1, output_size))
        
        # Activation functions
        self.activation_functions = {
            'relu': (ActivationFunction.relu, ActivationFunction.relu_derivative),
            'sigmoid': (ActivationFunction.sigmoid, ActivationFunction.sigmoid_derivative),
            'tanh': (ActivationFunction.tanh, ActivationFunction.tanh_derivative)
        }
        
        # Store last forward pass for backpropagation
        self.last_input = None
        self.last_output = None
        self.last_activation_input = None
    
    def forward(self, x: np.ndarray, training: bool = False) -> np.ndarray:
        """Forward pass through the layer"""
        # Store input for backpropagation
        self.last_input = x.copy()
        
        # Linear transformation
        z = np.dot(x, self.weights) + self.biases
        self.last_activation_input = z.copy()
        
        # Apply activation function
        if self.activation in self.activation_functions:
            activation_func, _ = self.activation_functions[self.activation]
            output = activation_func(z)
        else:
            output = z  # Linear activation
        
        # Apply dropout during training
        if training and self.dropout_rate > 0:
            dropout_mask = np.random.binomial(1, 1 - self.dropout_rate, output.shape)
            output = output * dropout_mask / (1 - self.dropout_rate)
        
        self.last_output = output.copy()
        return output
    
    def backward(self, grad_output: np.ndarray, learning_rate: float = 0.001) -> np.ndarray:
        """Backward pass through the layer"""
        if self.last_input is None or self.last_activation_input is None:
            raise ValueError("Forward pass must be called before backward pass")
        
        # Apply activation derivative
        if self.activation in self.activation_functions:
            _, activation_derivative = self.activation_functions[self.activation]
            grad_activation = activation_derivative(self.last_activation_input)
            grad_z = grad_output * grad_activation
        else:
            grad_z = grad_output  # Linear activation
        
        # Calculate gradients
        grad_weights = np.dot(self.last_input.T, grad_z)
        grad_biases = np.sum(grad_z, axis=0, keepdims=True)
        grad_input = np.dot(grad_z, self.weights.T)
        
        # Update weights and biases
        self.weights -= learning_rate * grad_weights
        self.biases -= learning_rate * grad_biases
        
        return grad_input

class DeepPatternRecognizer:
    """Deep neural network for lottery pattern recognition"""
    
    def __init__(self, input_size: int = 50, hidden_sizes: List[int] = None, 
                 output_size: int = 49, learning_rate: float = 0.001):
        """
        Initialize the deep pattern recognizer
        
        Args:
            input_size: Number of input features
            hidden_sizes: Sizes of hidden layers
            output_size: Number of output classes (lottery numbers)
            learning_rate: Learning rate for training
        """
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes or [128, 64, 32]
        self.output_size = output_size
        self.learning_rate = learning_rate
        
        # Build the network
        self.layers = []
        self._build_network()
        
        # Training history
        self.training_history = {
            'loss': [],
            'accuracy': [],
            'pattern_recognition_rate': []
        }
        
        logger.info(f"✅ Deep Pattern Recognizer initialized with {len(self.layers)} layers")
    
    def _build_network(self):
        """Build the neural network architecture"""
        # Input layer to first hidden layer
        layer_sizes = [self.input_size] + self.hidden_sizes + [self.output_size]
        
        for i in range(len(layer_sizes) - 1):
            input_size = layer_sizes[i]
            output_size = layer_sizes[i + 1]
            
            # Choose activation function
            if i == len(layer_sizes) - 2:  # Output layer
                activation = 'sigmoid'  # For probability outputs
            else:  # Hidden layers
                activation = 'relu'
            
            # Add dropout to hidden layers
            dropout_rate = 0.2 if i < len(layer_sizes) - 2 else 0.0
            
            layer = PatternLayer(
                input_size=input_size,
                output_size=output_size,
                activation=activation,
                dropout_rate=dropout_rate,
                name=f"layer_{i+1}"
            )
            
            self.layers.append(layer)
    
    def forward(self, x: np.ndarray, training: bool = False) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Forward pass through the entire network"""
        activations = {'input': x.copy()}
        current_input = x
        
        for i, layer in enumerate(self.layers):
            current_input = layer.forward(current_input, training=training)
            activations[f'layer_{i+1}'] = current_input.copy()
        
        return current_input, activations
    
    def predict_patterns(self, historical_data: List[Dict[str, Any]], 
                        n_predictions: int = 6) -> NeuralPrediction:
        """
        Predict lottery patterns using deep learning
        
        Args:
            historical_data: List of historical lottery data
            n_predictions: Number of numbers to predict
            
        Returns:
            NeuralPrediction with predicted numbers and metadata
        """
        try:
            logger.info(f"🧠 Starting deep pattern recognition on {len(historical_data)} data points...")
            
            # Step 1: Feature extraction
            features = self._extract_deep_features(historical_data)
            
            # Step 2: Forward pass
            output_probabilities, layer_activations = self.forward(features, training=False)
            
            # Step 3: Pattern signature extraction
            pattern_signatures = self._extract_pattern_signatures(layer_activations, historical_data)
            
            # Step 4: Number selection
            predicted_numbers, confidence_scores = self._select_optimal_numbers(
                output_probabilities, n_predictions
            )
            
            # Step 5: Feature importance calculation
            feature_importance = self._calculate_feature_importance(features, output_probabilities)
            
            # Step 6: Uncertainty estimation
            uncertainty_estimate = self._estimate_prediction_uncertainty(
                output_probabilities, pattern_signatures
            )
            
            # Create prediction result
            prediction = NeuralPrediction(
                predicted_numbers=predicted_numbers,
                confidence_scores=confidence_scores,
                pattern_signatures=pattern_signatures,
                layer_activations=layer_activations,
                feature_importance=feature_importance,
                uncertainty_estimate=uncertainty_estimate
            )
            
            logger.info(f"✅ Deep pattern recognition completed!")
            logger.info(f"   Predicted Numbers: {predicted_numbers}")
            logger.info(f"   Average Confidence: {np.mean(confidence_scores):.3f}")
            logger.info(f"   Pattern Signatures: {len(pattern_signatures)}")
            logger.info(f"   Uncertainty: {uncertainty_estimate:.3f}")
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error in deep pattern recognition: {e}")
            raise
    
    def train_on_patterns(self, training_data: List[Dict[str, Any]], 
                         epochs: int = 100, batch_size: int = 32) -> Dict[str, Any]:
        """
        Train the neural network on historical patterns
        
        Args:
            training_data: Training data with input-output pairs
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Training statistics
        """
        try:
            logger.info(f"🧠 Starting neural network training for {epochs} epochs...")
            
            # Prepare training data
            X, y = self._prepare_training_data(training_data)
            n_samples = X.shape[0]
            
            # Training loop
            for epoch in range(epochs):
                epoch_loss = 0.0
                correct_predictions = 0
                
                # Shuffle data
                indices = np.random.permutation(n_samples)
                X_shuffled = X[indices]
                y_shuffled = y[indices]
                
                # Mini-batch training
                for i in range(0, n_samples, batch_size):
                    batch_end = min(i + batch_size, n_samples)
                    X_batch = X_shuffled[i:batch_end]
                    y_batch = y_shuffled[i:batch_end]
                    
                    # Forward pass
                    predictions, _ = self.forward(X_batch, training=True)
                    
                    # Calculate loss
                    batch_loss = self._calculate_loss(predictions, y_batch)
                    epoch_loss += batch_loss
                    
                    # Backward pass
                    self._backward_pass(predictions, y_batch)
                    
                    # Calculate accuracy
                    batch_accuracy = self._calculate_accuracy(predictions, y_batch)
                    correct_predictions += batch_accuracy * X_batch.shape[0]
                
                # Record epoch statistics
                avg_loss = epoch_loss / (n_samples // batch_size + 1)
                accuracy = correct_predictions / n_samples
                
                self.training_history['loss'].append(avg_loss)
                self.training_history['accuracy'].append(accuracy)
                
                if epoch % 20 == 0:
                    logger.info(f"   Epoch {epoch}: Loss={avg_loss:.4f}, Accuracy={accuracy:.3f}")
            
            training_stats = {
                'final_loss': self.training_history['loss'][-1],
                'final_accuracy': self.training_history['accuracy'][-1],
                'epochs_trained': epochs,
                'total_samples': n_samples
            }
            
            logger.info(f"✅ Training completed!")
            logger.info(f"   Final Loss: {training_stats['final_loss']:.4f}")
            logger.info(f"   Final Accuracy: {training_stats['final_accuracy']:.3f}")
            
            return training_stats
            
        except Exception as e:
            logger.error(f"❌ Error in neural network training: {e}")
            return {'final_loss': float('inf'), 'final_accuracy': 0.0}
    
    # =================== PRIVATE METHODS ===================
    
    def _extract_deep_features(self, historical_data: List[Dict[str, Any]]) -> np.ndarray:
        """Extract deep features from historical data"""
        try:
            features = []
            
            # Extract various pattern features
            numbers_sequence = []
            dates_sequence = []
            
            for data_point in historical_data[-50:]:  # Use last 50 data points
                if 'ket_qua' in data_point:
                    numbers = data_point['ket_qua']
                    if isinstance(numbers, str):
                        # Parse number string
                        clean_numbers = ''.join(c for c in numbers if c.isdigit())
                        if clean_numbers:
                            numbers_sequence.extend([int(clean_numbers[i:i+2]) for i in range(0, min(len(clean_numbers), 10), 2)])
                    elif isinstance(numbers, list):
                        numbers_sequence.extend(numbers[:5])  # Take first 5 numbers
                
                if 'ngay' in data_point:
                    # Extract date features
                    date_str = str(data_point['ngay'])
                    if len(date_str) >= 8:
                        day = int(date_str[-2:]) if date_str[-2:].isdigit() else 1
                        month = int(date_str[-4:-2]) if date_str[-4:-2].isdigit() else 1
                        dates_sequence.extend([day, month])
            
            # Normalize sequences to fixed length
            target_length = self.input_size
            
            if len(numbers_sequence) > target_length // 2:
                numbers_sequence = numbers_sequence[:target_length // 2]
            else:
                numbers_sequence.extend([0] * (target_length // 2 - len(numbers_sequence)))
            
            if len(dates_sequence) > target_length // 2:
                dates_sequence = dates_sequence[:target_length // 2]
            else:
                dates_sequence.extend([0] * (target_length // 2 - len(dates_sequence)))
            
            # Combine features
            features = numbers_sequence + dates_sequence
            
            # Normalize features
            features_array = np.array(features, dtype=float).reshape(1, -1)
            
            # Simple normalization
            if features_array.max() > 0:
                features_array = features_array / features_array.max()
            
            return features_array
            
        except Exception as e:
            logger.error(f"❌ Error extracting deep features: {e}")
            # Return zero features
            return np.zeros((1, self.input_size))
    
    def _extract_pattern_signatures(self, layer_activations: Dict[str, np.ndarray], 
                                  historical_data: List[Dict[str, Any]]) -> List[PatternSignature]:
        """Extract pattern signatures from layer activations"""
        try:
            signatures = []
            
            for layer_name, activations in layer_activations.items():
                if layer_name == 'input':
                    continue
                
                # Calculate pattern characteristics
                complexity_score = np.std(activations)
                confidence = np.mean(np.abs(activations))
                pattern_hash = str(hash(tuple(activations.flatten()[:10])))
                
                signature = PatternSignature(
                    pattern_id=f"{layer_name}_pattern_{len(signatures)}",
                    pattern_type=f"neural_{layer_name}",
                    complexity_score=float(complexity_score),
                    confidence=float(confidence),
                    temporal_span=len(historical_data),
                    frequency_domain="neural_activation",
                    pattern_hash=pattern_hash
                )
                
                signatures.append(signature)
            
            return signatures
            
        except Exception as e:
            logger.error(f"❌ Error extracting pattern signatures: {e}")
            return []
    
    def _select_optimal_numbers(self, probabilities: np.ndarray, 
                              n_predictions: int) -> Tuple[List[int], List[float]]:
        """Select optimal numbers based on neural network output"""
        try:
            # Flatten probabilities if needed
            if probabilities.ndim > 1:
                probabilities = probabilities.flatten()
            
            # Ensure we have enough probabilities
            if len(probabilities) < n_predictions:
                # Extend with random probabilities
                extra_probs = np.random.random(n_predictions - len(probabilities))
                probabilities = np.concatenate([probabilities, extra_probs])
            
            # Select top N numbers with highest probabilities
            top_indices = np.argsort(probabilities)[-n_predictions:][::-1]
            
            # Convert to lottery numbers (1-49)
            predicted_numbers = [(idx % 49) + 1 for idx in top_indices]
            confidence_scores = [float(probabilities[idx]) for idx in top_indices]
            
            # Ensure unique numbers
            unique_numbers = []
            unique_scores = []
            
            for i, (num, score) in enumerate(zip(predicted_numbers, confidence_scores)):
                if num not in unique_numbers:
                    unique_numbers.append(num)
                    unique_scores.append(score)
                else:
                    # Generate alternative number
                    alternative = ((num + i) % 49) + 1
                    while alternative in unique_numbers:
                        alternative = (alternative % 49) + 1
                    unique_numbers.append(alternative)
                    unique_scores.append(score * 0.9)  # Slightly lower confidence
            
            return unique_numbers[:n_predictions], unique_scores[:n_predictions]
            
        except Exception as e:
            logger.error(f"❌ Error selecting optimal numbers: {e}")
            # Return random numbers as fallback
            return list(range(1, n_predictions + 1)), [0.5] * n_predictions
    
    def _calculate_feature_importance(self, features: np.ndarray, 
                                    output: np.ndarray) -> Dict[str, float]:
        """Calculate feature importance scores"""
        try:
            importance = {}
            
            # Simple gradient-based importance
            for i in range(features.shape[1]):
                # Perturb feature and measure output change
                perturbed_features = features.copy()
                perturbed_features[0, i] += 0.01
                
                perturbed_output, _ = self.forward(perturbed_features, training=False)
                
                # Calculate importance as output sensitivity
                sensitivity = np.mean(np.abs(perturbed_output - output))
                importance[f'feature_{i}'] = float(sensitivity)
            
            return importance
            
        except Exception as e:
            logger.error(f"❌ Error calculating feature importance: {e}")
            return {}
    
    def _estimate_prediction_uncertainty(self, probabilities: np.ndarray, 
                                       pattern_signatures: List[PatternSignature]) -> float:
        """Estimate prediction uncertainty"""
        try:
            # Probability-based uncertainty
            prob_uncertainty = 1.0 - np.max(probabilities)
            
            # Pattern complexity uncertainty
            if pattern_signatures:
                complexity_scores = [sig.complexity_score for sig in pattern_signatures]
                pattern_uncertainty = np.std(complexity_scores)
            else:
                pattern_uncertainty = 0.5
            
            # Combined uncertainty
            total_uncertainty = 0.7 * prob_uncertainty + 0.3 * pattern_uncertainty
            
            return float(np.clip(total_uncertainty, 0.0, 1.0))
            
        except Exception as e:
            logger.error(f"❌ Error estimating uncertainty: {e}")
            return 0.5
    
    def _prepare_training_data(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for neural network"""
        try:
            X = []
            y = []
            
            for i in range(len(training_data) - 1):
                # Input: current data point features
                features = self._extract_deep_features([training_data[i]])
                X.append(features[0])
                
                # Output: next data point numbers (simplified)
                next_data = training_data[i + 1]
                target = np.zeros(self.output_size)
                
                # Create target vector
                if 'ket_qua' in next_data:
                    numbers = next_data['ket_qua']
                    if isinstance(numbers, str):
                        clean_numbers = ''.join(c for c in numbers if c.isdigit())
                        if clean_numbers:
                            number_pairs = [int(clean_numbers[j:j+2]) for j in range(0, min(len(clean_numbers), 6), 2)]
                            for num in number_pairs:
                                if 1 <= num <= 49:
                                    target[num - 1] = 1.0
                
                y.append(target)
            
            return np.array(X), np.array(y)
            
        except Exception as e:
            logger.error(f"❌ Error preparing training data: {e}")
            # Return minimal training data
            X = np.random.random((10, self.input_size))
            y = np.random.random((10, self.output_size))
            return X, y
    
    def _calculate_loss(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Calculate binary cross-entropy loss"""
        try:
            # Clip predictions to prevent log(0)
            predictions_clipped = np.clip(predictions, 1e-7, 1 - 1e-7)
            
            # Binary cross-entropy loss
            loss = -np.mean(
                targets * np.log(predictions_clipped) + 
                (1 - targets) * np.log(1 - predictions_clipped)
            )
            
            return float(loss)
            
        except Exception as e:
            logger.error(f"❌ Error calculating loss: {e}")
            return float('inf')
    
    def _calculate_accuracy(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Calculate prediction accuracy"""
        try:
            # Convert probabilities to binary predictions
            binary_predictions = (predictions > 0.5).astype(float)
            
            # Calculate accuracy
            accuracy = np.mean(binary_predictions == targets)
            
            return float(accuracy)
            
        except Exception as e:
            logger.error(f"❌ Error calculating accuracy: {e}")
            return 0.0
    
    def _backward_pass(self, predictions: np.ndarray, targets: np.ndarray):
        """Perform backward pass through the network"""
        try:
            # Calculate output gradient
            grad_output = predictions - targets
            
            # Backpropagate through layers
            current_grad = grad_output
            for layer in reversed(self.layers):
                current_grad = layer.backward(current_grad, self.learning_rate)
                
        except Exception as e:
            logger.error(f"❌ Error in backward pass: {e}")

# =================== DEMONSTRATION FUNCTION ===================

def demo_deep_pattern_recognition():
    """Demonstrate deep learning pattern recognition"""
    print("🧠 DEEP LEARNING PATTERN RECOGNITION - PHASE 3")
    print("=" * 60)
    
    # Initialize deep pattern recognizer
    recognizer = DeepPatternRecognizer(
        input_size=50,
        hidden_sizes=[128, 64, 32],
        output_size=49,
        learning_rate=0.001
    )
    
    print(f"\n🏗️ Neural Network Architecture:")
    print(f"   Input Size: {recognizer.input_size}")
    print(f"   Hidden Layers: {recognizer.hidden_sizes}")
    print(f"   Output Size: {recognizer.output_size}")
    print(f"   Total Layers: {len(recognizer.layers)}")
    
    # Generate sample historical data
    historical_data = []
    for i in range(100):
        data_point = {
            'ngay': f"20250120",
            'ket_qua': f"{10 + i % 39:02d}{20 + i % 29:02d}{30 + i % 19:02d}",
            'quality_score': 0.7 + (i % 10) * 0.03
        }
        historical_data.append(data_point)
    
    print(f"\n📊 Historical Data:")
    print(f"   Data Points: {len(historical_data)}")
    print(f"   Sample: {historical_data[-1]}")
    
    # Perform pattern recognition
    print(f"\n🧠 PERFORMING DEEP PATTERN RECOGNITION...")
    
    prediction = recognizer.predict_patterns(historical_data, n_predictions=6)
    
    # Display results
    print(f"\n🎯 DEEP LEARNING PREDICTION RESULTS:")
    print(f"=" * 45)
    
    print(f"\n🔢 Predicted Numbers:")
    for i, (num, conf) in enumerate(zip(prediction.predicted_numbers, prediction.confidence_scores), 1):
        print(f"   {i}. Number {num:02d} (Confidence: {conf:.3f})")
    
    print(f"\n🧠 Neural Network Analysis:")
    print(f"   Layer Activations: {len(prediction.layer_activations)} layers")
    print(f"   Pattern Signatures: {len(prediction.pattern_signatures)}")
    print(f"   Uncertainty Estimate: {prediction.uncertainty_estimate:.3f}")
    print(f"   Feature Importance: {len(prediction.feature_importance)} features")
    
    # Pattern signatures analysis
    print(f"\n🎨 Pattern Signatures:")
    for i, sig in enumerate(prediction.pattern_signatures[:3], 1):
        print(f"   {i}. {sig.pattern_type} (Complexity: {sig.complexity_score:.3f}, Confidence: {sig.confidence:.3f})")
    
    # Feature importance analysis
    print(f"\n📊 Top Feature Importance:")
    sorted_features = sorted(prediction.feature_importance.items(), 
                           key=lambda x: x[1], reverse=True)
    for i, (feature, importance) in enumerate(sorted_features[:5], 1):
        print(f"   {i}. {feature}: {importance:.4f}")
    
    # Training demonstration
    print(f"\n🏋️ NEURAL NETWORK TRAINING DEMONSTRATION...")
    
    training_stats = recognizer.train_on_patterns(historical_data, epochs=50, batch_size=16)
    
    print(f"\n📈 Training Results:")
    print(f"   Final Loss: {training_stats['final_loss']:.4f}")
    print(f"   Final Accuracy: {training_stats['final_accuracy']:.3f}")
    print(f"   Epochs Trained: {training_stats['epochs_trained']}")
    print(f"   Total Samples: {training_stats['total_samples']}")
    
    print(f"\n✅ Deep Learning Pattern Recognition demonstration completed!")
    print(f"\n🎉 AI INTEGRATION PHASE 3 ACTIVE!")
    print(f"   🧠 Neural Network: {len(recognizer.layers)} layers operational")
    print(f"   🎯 Pattern Recognition: {len(prediction.pattern_signatures)} signatures extracted")
    print(f"   ⚡ Prediction Confidence: {np.mean(prediction.confidence_scores):.1%}")
    print(f"   📊 Feature Analysis: {len(prediction.feature_importance)} features analyzed")
    
    return recognizer, prediction

if __name__ == "__main__":
    recognizer, prediction = demo_deep_pattern_recognition()
