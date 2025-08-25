"""
Ví dụ xây dựng mô hình LSTM với TensorFlow/Keras cho bài toán dự đoán state của kết quả xổ số.
Trong ví dụ này, ta giả sử dữ liệu đầu vào là chuỗi các state (đã được one-hot encode hoặc integer encode)
và mô hình sẽ dự đoán state tiếp theo dưới dạng phân loại.
"""
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Embedding
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

# Giả sử chúng ta sử dụng dữ liệu lịch sử đã mã hóa (integer encode các state)
# Ví dụ: chuỗi các state dưới dạng số
data_sequence = [0, 1, 2, 0, 1, 2, 0, 2, 0, 1, 2, 0, 1, 2, 1, 0, 2, 2, 1, 0]

# Thiết lập các tham số
sequence_length = 5  # số bước lịch sử để dự đoán state tiếp theo
vocab_size = len(set(data_sequence))
embedding_dim = 8

# Tạo tập dữ liệu đầu vào cho LSTM
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        seq = data[i:i+seq_length]
        label = data[i+seq_length]
        X.append(seq)
        y.append(label)
    return np.array(X), np.array(y)

X, y = create_sequences(data_sequence, sequence_length)
y_cat = to_categorical(y, num_classes=vocab_size)

# Chia dữ liệu thành training và testing
X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)

# Xây dựng mô hình LSTM
model = Sequential()
# Layer Embedding (nếu sử dụng integer encoded input)
model.add(Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=sequence_length))
model.add(LSTM(64, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(vocab_size, activation='softmax'))

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# Huấn luyện mô hình
model.fit(X_train, y_train, epochs=50, batch_size=4, validation_data=(X_test, y_test))

# Dự đoán state tiếp theo dựa trên chuỗi hiện tại
sample_sequence = np.array(X[-1]).reshape(1, sequence_length)
predicted_prob = model.predict(sample_sequence)
predicted_state = np.argmax(predicted_prob)
print("Chuỗi vào mẫu:", X[-1])
print("State dự đoán (số nguyên):", predicted_state)