"""
Ví dụ sử dụng hmmlearn để xây dựng mô hình Markov ẩn (HMM) cho việc dự đoán state.
Giả sử bạn đã có chuỗi các state được trích xuất (vd. từ hàm get_historical_states) dưới dạng danh sách các ký tự.
"""
import numpy as np
from hmmlearn import hmm
from collections import defaultdict

# Giả sử chúng ta có chuỗi các state đã được chuyển đổi sang dạng số (ví dụ: map state '01', '12', v.v.)
# Ta sẽ ánh xạ các state rời rạc sang số nguyên.
def encode_states(states):
    unique_states = sorted(set(states))
    mapping = {state: idx for idx, state in enumerate(unique_states)}
    encoded = np.array([mapping[s] for s in states])
    return encoded, mapping

def train_hmm_model(state_sequence, n_hidden_states=3, n_iter=100):
    """
    Huấn luyện mô hình HMM với số lượng state ẩn n_hidden_states và số vòng lặp n_iter.
    state_sequence: chuỗi các state đã được mã hóa (encoded) dạng 1D numpy array.
    """
    # reshape data cho hmmlearn
    X = state_sequence.reshape(-1, 1)
    
    # Khởi tạo mô hình Multinomial HMM
    model = hmm.MultinomialHMM(n_components=n_hidden_states, n_iter=n_iter, random_state=42)
    # Số lượng các phép quan sát khác nhau (số lượng unique state)
    model.n_features = len(np.unique(state_sequence))
    
    # Huấn luyện mô hình
    model.fit(X)
    
    return model

if __name__ == '__main__':
    # Ví dụ: chuỗi state lịch sử, có thể lấy từ file log hoặc database sau khi trích xuất
    historical_states = ['01', '12', '03', '01', '02', '12', '03', '02', '01', '03', '03', '02', '01']
    encoded_states, mapping = encode_states(historical_states)
    print("Mapping giữa state và mã số:", mapping)
    
    model = train_hmm_model(encoded_states, n_hidden_states=3, n_iter=200)
    
    # Dự đoán state ẩn cho chuỗi dữ liệu
    logprob, hidden_states = model.decode(encoded_states.reshape(-1,1))
    print("Các state ẩn được dự đoán:", hidden_states)
    
    # Dự đoán state cho lần quan sát tiếp theo dựa trên xác suất chuyển đổi
    # Lấy xác suất chuyển đổi từ state cuối cùng
    next_prob = model.transmat_[hidden_states[-1]]
    print("Xác suất chuyển đổi từ state ẩn hiện tại:", next_prob)