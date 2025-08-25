import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Embedding
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import pickle
import os
from datetime import datetime
import logging
from .state_analysis_service import StateAnalysisService

logger = logging.getLogger(__name__)

class LSTMService(StateAnalysisService):
    """Service cho LSTM Neural Network"""
    
    def train_lstm_model(self, states, sequence_length=10, epochs=50, batch_size=32):
        """Huấn luyện LSTM model"""
        try:
            # Chuẩn bị dữ liệu
            X, y, state_to_int, int_to_state, vocab_size = self.prepare_sequences_for_lstm(
                states, sequence_length
            )
            
            if len(X) == 0:
                logger.error("Không đủ dữ liệu để huấn luyện LSTM")
                return None
            
            # One-hot encode labels
            y_categorical = to_categorical(y, num_classes=vocab_size)
            
            # Chia train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_categorical, test_size=0.2, random_state=42
            )
            
            # Xây dựng model
            model = Sequential([
                Embedding(
                    input_dim=vocab_size, 
                    output_dim=min(50, vocab_size * 2), 
                    input_length=sequence_length
                ),
                LSTM(64, return_sequences=False, dropout=0.2, recurrent_dropout=0.2),
                Dropout(0.3),
                Dense(32, activation='relu'),
                Dropout(0.2),
                Dense(vocab_size, activation='softmax')
            ])
            
            model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Huấn luyện
            history = model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=(X_test, y_test),
                verbose=1
            )
            
            # Đánh giá
            test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
            
            # Tạo model data
            model_data = {
                'keras_model': model,
                'state_to_int': state_to_int,
                'int_to_state': int_to_state,
                'vocab_size': vocab_size,
                'sequence_length': sequence_length,
                'test_accuracy': test_accuracy,
                'test_loss': test_loss,
                'training_history': history.history,
                'training_size': len(states)
            }
            
            return model_data
            
        except Exception as e:
            logger.error(f"Error training LSTM model: {e}")
            return None
    
    def predict_with_lstm(self, model_data, recent_states):
        """Dự đoán với LSTM"""
        try:
            keras_model = model_data['keras_model']
            state_to_int = model_data['state_to_int']
            int_to_state = model_data['int_to_state']
            sequence_length = model_data['sequence_length']
            
            # Chuẩn bị input sequence
            if len(recent_states) < sequence_length:
                # Pad với state đầu tiên nếu không đủ dữ liệu
                padding = [recent_states[0]] * (sequence_length - len(recent_states))
                recent_states = padding + recent_states
            else:
                recent_states = recent_states[-sequence_length:]
            
            # Encode states
            encoded_sequence = []
            for state in recent_states:
                if state in state_to_int:
                    encoded_sequence.append(state_to_int[state])
                else:
                    # Sử dụng state mặc định nếu không tìm thấy
                    encoded_sequence.append(0)
            
            # Reshape cho prediction
            X = np.array(encoded_sequence).reshape(1, sequence_length)
            
            # Dự đoán
            predictions = keras_model.predict(X, verbose=0)
            predicted_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_idx])
            
            predicted_state = int_to_state.get(predicted_idx)
            
            return predicted_state, confidence
            
        except Exception as e:
            logger.error(f"Error predicting with LSTM: {e}")
            return None, 0.0
    
    def evaluate_lstm_model(self, model_data, test_states):
        """Đánh giá độ chính xác của LSTM model"""
        try:
            sequence_length = model_data['sequence_length']
            correct_predictions = 0
            total_predictions = 0
            
            state_sequence = [state for _, state in test_states]
            
            for i in range(sequence_length, len(state_sequence) - 1):
                # Lấy sequence để dự đoán
                input_sequence = state_sequence[i-sequence_length:i]
                actual_next_state = state_sequence[i]
                
                predicted_state, confidence = self.predict_with_lstm(
                    model_data, input_sequence
                )
                
                if predicted_state is not None:
                    total_predictions += 1
                    if predicted_state == actual_next_state:
                        correct_predictions += 1
            
            accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
            return accuracy, correct_predictions, total_predictions
            
        except Exception as e:
            logger.error(f"Error evaluating LSTM model: {e}")
            return 0.0, 0, 0
    
    def save_lstm_model(self, model_data, model_type='lstm'):
        """Lưu LSTM model (riêng biệt vì Keras model)"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Lưu Keras model
        keras_model_path = os.path.join(
            self.models_dir, f"{model_type}_keras_{timestamp}.h5"
        )
        model_data['keras_model'].save(keras_model_path)
        
        # Lưu metadata và mappings
        metadata_path = os.path.join(
            self.models_dir, f"{model_type}_metadata_{timestamp}.pkl"
        )
        
        metadata = {
            'state_to_int': model_data['state_to_int'],
            'int_to_state': model_data['int_to_state'],
            'vocab_size': model_data['vocab_size'],
            'sequence_length': model_data['sequence_length'],
            'test_accuracy': model_data.get('test_accuracy'),
            'training_size': model_data.get('training_size'),
            'keras_model_path': keras_model_path,
            'created_at': datetime.now(),
            'model_type': model_type
        }
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        return metadata_path
    
    def load_lstm_model(self, metadata_path):
        """Load LSTM model"""
        try:
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            keras_model_path = metadata['keras_model_path']
            if os.path.exists(keras_model_path):
                keras_model = tf.keras.models.load_model(keras_model_path)
                
                model_data = {
                    'keras_model': keras_model,
                    'state_to_int': metadata['state_to_int'],
                    'int_to_state': metadata['int_to_state'],
                    'vocab_size': metadata['vocab_size'],
                    'sequence_length': metadata['sequence_length'],
                    'test_accuracy': metadata.get('test_accuracy'),
                    'training_size': metadata.get('training_size')
                }
                
                return model_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading LSTM model: {e}")
            return None