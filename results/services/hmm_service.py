import numpy as np
from hmmlearn import hmm
import pickle
import os
from datetime import datetime
import logging
from .state_analysis_service import StateAnalysisService

logger = logging.getLogger(__name__)

class HMMService(StateAnalysisService):
    """Service cho Hidden Markov Model"""
    
    def encode_states_for_hmm(self, states):
        """Mã hóa states cho HMM"""
        state_sequence = [state for _, state in states]
        unique_states = sorted(set(state_sequence))
        
        mapping = {state: idx for idx, state in enumerate(unique_states)}
        reverse_mapping = {idx: state for state, idx in mapping.items()}
        
        encoded = np.array([mapping[s] for s in state_sequence])
        return encoded, mapping, reverse_mapping
    
    def train_hmm_model(self, states, n_hidden_states=5, n_iter=100):
        """Huấn luyện HMM model"""
        try:
            # Encode states
            encoded_states, mapping, reverse_mapping = self.encode_states_for_hmm(states)
            
            # Reshape cho hmmlearn
            X = encoded_states.reshape(-1, 1)
            
            # Khởi tạo model
            model = hmm.MultinomialHMM(
                n_components=n_hidden_states, 
                n_iter=n_iter, 
                random_state=42
            )
            model.n_features = len(np.unique(encoded_states))
            
            # Huấn luyện
            model.fit(X)
            
            # Tạo model data
            model_data = {
                'hmm_model': model,
                'state_mapping': mapping,
                'reverse_mapping': reverse_mapping,
                'n_hidden_states': n_hidden_states,
                'n_features': model.n_features,
                'training_size': len(states)
            }
            
            return model_data
            
        except Exception as e:
            logger.error(f"Error training HMM model: {e}")
            return None
    
    def predict_with_hmm(self, model_data, current_state, sequence_length=5):
        """Dự đoán với HMM"""
        try:
            hmm_model = model_data['hmm_model']
            state_mapping = model_data['state_mapping']
            reverse_mapping = model_data['reverse_mapping']
            
            if current_state not in state_mapping:
                return None, 0.0
            
            # Encode current state
            encoded_state = state_mapping[current_state]
            
            # Tạo sequence để dự đoán (có thể mở rộng với context)
            X = np.array([encoded_state] * sequence_length).reshape(-1, 1)
            
            # Dự đoán hidden states
            logprob, hidden_states = hmm_model.decode(X)
            
            # Lấy xác suất emission từ hidden state cuối
            last_hidden_state = hidden_states[-1]
            emission_probs = hmm_model.emissionprob_[last_hidden_state]
            
            # Tìm state có xác suất cao nhất
            predicted_encoded = np.argmax(emission_probs)
            predicted_state = reverse_mapping.get(predicted_encoded)
            confidence = emission_probs[predicted_encoded]
            
            return predicted_state, float(confidence)
            
        except Exception as e:
            logger.error(f"Error predicting with HMM: {e}")
            return None, 0.0
    
    def evaluate_hmm_model(self, model_data, test_states):
        """Đánh giá độ chính xác của HMM model"""
        correct_predictions = 0
        total_predictions = 0
        
        state_sequence = [state for _, state in test_states]
        
        for i in range(len(state_sequence) - 1):
            current_state = state_sequence[i]
            actual_next_state = state_sequence[i + 1]
            
            predicted_state, confidence = self.predict_with_hmm(
                model_data, current_state
            )
            
            if predicted_state is not None:
                total_predictions += 1
                if predicted_state == actual_next_state:
                    correct_predictions += 1
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        return accuracy, correct_predictions, total_predictions