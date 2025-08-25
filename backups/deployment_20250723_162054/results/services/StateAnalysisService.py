import numpy as np
import pickle
import os
from datetime import timedelta, datetime
from collections import defaultdict
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class StateAnalysisService:
    """Service để phân tích và dự đoán state"""
    
    def __init__(self):
        self.models_dir = r'C:\Users\n2t\Documents\xoso_crawler\data\predictor_models'
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def extract_state_from_record(self, record):
        """Trích xuất state từ bản ghi KetQuaXoSo"""
        try:
            num_7_2 = record.giai_7_2
            num_7_3 = record.giai_7_3
            
            if num_7_2 is None or num_7_3 is None:
                return None
            
            str_7_2 = str(num_7_2).zfill(2)
            str_7_3 = str(num_7_3).zfill(2)
            state = str_7_2[0] + str_7_3[0]
            return state
        except Exception as e:
            logger.error(f"Error extracting state: {e}")
            return None
    
    def get_historical_states(self, days=365):
        """Lấy dữ liệu state lịch sử"""
        from results.models import KetQuaXoSo
        
        from_date = timezone.now().date() - timedelta(days=days)
        queryset = KetQuaXoSo.objects.filter(
            ngay__gte=from_date
        ).order_by('ngay')
        
        states = []
        for record in queryset.iterator():
            state = self.extract_state_from_record(record)
            if state:
                states.append((record.ngay, state))
        
        return states
    
    def prepare_sequences_for_lstm(self, states, sequence_length=10):
        """Chuẩn bị dữ liệu cho LSTM"""
        # Chỉ lấy state (bỏ ngày)
        state_sequence = [state for _, state in states]
        
        # Tạo mapping state -> integer
        unique_states = sorted(set(state_sequence))
        state_to_int = {state: i for i, state in enumerate(unique_states)}
        int_to_state = {i: state for state, i in state_to_int.items()}
        
        # Encode states
        encoded_states = [state_to_int[state] for state in state_sequence]
        
        # Tạo sequences
        X, y = [], []
        for i in range(len(encoded_states) - sequence_length):
            seq = encoded_states[i:i+sequence_length]
            label = encoded_states[i+sequence_length]
            X.append(seq)
            y.append(label)
        
        return (np.array(X), np.array(y), state_to_int, int_to_state, 
                len(unique_states))
    
    def build_markov_transition_matrix(self, states):
        """Xây dựng ma trận chuyển đổi Markov"""
        matrix = defaultdict(lambda: defaultdict(int))
        
        # Chỉ lấy state (bỏ ngày)
        state_sequence = [state for _, state in states]
        
        for i in range(len(state_sequence) - 1):
            current_state = state_sequence[i]
            next_state = state_sequence[i + 1]
            matrix[current_state][next_state] += 1
        
        # Normalize thành xác suất
        norm_matrix = {}
        for state, transitions in matrix.items():
            total = sum(transitions.values())
            if total > 0:
                norm_matrix[state] = {
                    next_state: count / total 
                    for next_state, count in transitions.items()
                }
        
        return norm_matrix
    
    def save_model(self, model, model_type, metadata=None):
        """Lưu model vào file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{model_type}_model_{timestamp}.pkl"
        filepath = os.path.join(self.models_dir, filename)
        
        model_data = {
            'model': model,
            'model_type': model_type,
            'created_at': datetime.now(),
            'metadata': metadata or {}
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        return filepath
    
    def load_model(self, filepath):
        """Load model từ file"""
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Error loading model from {filepath}: {e}")
            return None
    
    def predict_with_markov(self, transition_matrix, current_state):
        """Dự đoán với Markov chain"""
        if current_state not in transition_matrix:
            return None, 0.0
        
        next_transitions = transition_matrix[current_state]
        if not next_transitions:
            return None, 0.0
        
        # Lấy state có xác suất cao nhất
        predicted_state = max(next_transitions, key=next_transitions.get)
        confidence = next_transitions[predicted_state]
        
        return predicted_state, confidence