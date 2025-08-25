from django.core.management.base import BaseCommand
from django.utils import timezone
from results.services.hmm_service import HMMService
from results.services.lstm_service import LSTMService
from results.models import PredictionModel
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Huấn luyện các models để dự đoán state (HMM, LSTM, Markov)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Số ngày lịch sử để huấn luyện (mặc định: 365)'
        )
        parser.add_argument(
            '--model-types',
            nargs='+',
            default=['markov', 'hmm', 'lstm'],
            choices=['markov', 'hmm', 'lstm'],
            help='Các loại model cần huấn luyện'
        )
        parser.add_argument(
            '--hmm-states',
            type=int,
            default=5,
            help='Số hidden states cho HMM (mặc định: 5)'
        )
        parser.add_argument(
            '--lstm-epochs',
            type=int,
            default=50,
            help='Số epochs cho LSTM (mặc định: 50)'
        )
        parser.add_argument(
            '--sequence-length',
            type=int,
            default=10,
            help='Độ dài sequence cho LSTM (mặc định: 10)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        model_types = options['model_types']
        hmm_states = options['hmm_states']
        lstm_epochs = options['lstm_epochs']
        sequence_length = options['sequence_length']
        
        self.stdout.write(
            self.style.SUCCESS(f'Bắt đầu huấn luyện models với dữ liệu {days} ngày...')
        )
        
        # Khởi tạo services
        hmm_service = HMMService()
        lstm_service = LSTMService()
        
        # Lấy dữ liệu lịch sử
        self.stdout.write('Đang lấy dữ liệu lịch sử...')
        historical_states = hmm_service.get_historical_states(days)
        
        if len(historical_states) < 50:
            self.stdout.write(
                self.style.ERROR(f'Không đủ dữ liệu (chỉ có {len(historical_states)} bản ghi)')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Đã lấy {len(historical_states)} bản ghi dữ liệu')
        )
        
        # Chia dữ liệu train/test
        split_idx = int(len(historical_states) * 0.8)
        train_states = historical_states[:split_idx]
        test_states = historical_states[split_idx:]
        
        # Huấn luyện Markov Chain
        if 'markov' in model_types:
            self.stdout.write('Đang huấn luyện Markov Chain...')
            try:
                transition_matrix = hmm_service.build_markov_transition_matrix(train_states)
                
                # Đánh giá
                correct = 0
                total = 0
                state_sequence = [state for _, state in test_states]
                
                for i in range(len(state_sequence) - 1):
                    current_state = state_sequence[i]
                    actual_next = state_sequence[i + 1]
                    
                    predicted, confidence = hmm_service.predict_with_markov(
                        transition_matrix, current_state
                    )
                    
                    if predicted is not None:
                        total += 1
                        if predicted == actual_next:
                            correct += 1
                
                accuracy = correct / total if total > 0 else 0
                
                # Lưu model
                filepath = hmm_service.save_model(
                    transition_matrix, 
                    'markov',
                    {
                        'accuracy': accuracy,
                        'training_size': len(train_states),
                        'test_size': len(test_states)
                    }
                )
                
                # Tạo bản ghi trong database
                PredictionModel.objects.create_model_record(
                    model_type='markov',
                    file_path=filepath,
                    metadata={
                        'accuracy': accuracy,
                        'training_size': len(train_states),
                        'test_size': len(test_states),
                        'states_count': len(set([s for _, s in historical_states]))
                    }
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Markov Chain - Accuracy: {accuracy:.2%} - Saved: {filepath}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Lỗi huấn luyện Markov Chain: {e}')
                )
        
        # Huấn luyện HMM
        if 'hmm' in model_types:
            self.stdout.write('Đang huấn luyện Hidden Markov Model...')
            try:
                model_data = hmm_service.train_hmm_model(
                    train_states, 
                    n_hidden_states=hmm_states
                )
                
                if model_data:
                    # Đánh giá
                    accuracy, correct, total = hmm_service.evaluate_hmm_model(
                        model_data, test_states
                    )
                    
                    # Lưu model
                    model_data['metadata'] = {
                        'accuracy': accuracy,
                        'training_size': len(train_states),
                        'test_size': len(test_states),
                        'n_hidden_states': hmm_states
                    }
                    
                    filepath = hmm_service.save_model(model_data, 'hmm')
                    
                    # Tạo bản ghi trong database
                    PredictionModel.objects.create_model_record(
                        model_type='hmm',
                        file_path=filepath,
                        metadata=model_data['metadata']
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'HMM - Accuracy: {accuracy:.2%} - Saved: {filepath}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('Không thể huấn luyện HMM model')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Lỗi huấn luyện HMM: {e}')
                )
        
        # Huấn luyện LSTM
        if 'lstm' in model_types:
            self.stdout.write('Đang huấn luyện LSTM Neural Network...')
            try:
                model_data = lstm_service.train_lstm_model(
                    train_states,
                    sequence_length=sequence_length,
                    epochs=lstm_epochs
                )
                
                if model_data:
                    # Đánh giá trên test set
                    accuracy, correct, total = lstm_service.evaluate_lstm_model(
                        model_data, test_states
                    )
                    
                    # Lưu model
                    filepath = lstm_service.save_lstm_model(model_data, 'lstm')
                    
                    # Tạo bản ghi trong database
                    PredictionModel.objects.create_model_record(
                        model_type='lstm',
                        file_path=filepath,
                        metadata={
                            'accuracy': accuracy,
                            'training_size': len(train_states),
                            'test_size': len(test_states),
                            'sequence_length': sequence_length,
                            'epochs': lstm_epochs,
                            'test_accuracy': model_data.get('test_accuracy')
                        }
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'LSTM - Accuracy: {accuracy:.2%} - Saved: {filepath}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('Không thể huấn luyện LSTM model')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Lỗi huấn luyện LSTM: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Hoàn thành huấn luyện models!')
        )