import numpy as np
from datetime import timedelta
from collections import defaultdict
from django.utils import timezone
from results.models import KetQuaXoSo

def extract_state_from_day(record):
    """
    Hàm trích xuất state từ 1 bản ghi KetQuaXoSo theo quy tắc ví dụ:
    - Từ Giải bảy, lấy chữ số đầu tiên của giai_7_2 và chữ số đầu tiên của giai_7_3.
    Nếu không đủ số liệu thì trả về None.
    """
    try:
        # Lấy kết quả của Giải bảy 2 và Giải bảy 3, định dạng đảm bảo 2 ký tự (ví dụ "08", "95")
        num_7_2 = record.giai_7_2
        num_7_3 = record.giai_7_3
        if num_7_2 is None or num_7_3 is None:
            return None
        str_7_2 = str(num_7_2).zfill(2)
        str_7_3 = str(num_7_3).zfill(2)
        # Quy tắc: lấy chữ số đầu của giai_7_2 và chữ số đầu của giai_7_3, ghép lại thành state
        state = str_7_2[0] + str_7_3[0]
        return state
    except Exception as e:
        return None

def get_historical_states(days=60):
    """
    Truy xuất các bản ghi KetQuaXoSo từ quá khứ (days) sắp xếp theo ngày tăng dần, 
    sau đó trích xuất state từ bản ghi theo hàm extract_state_from_day.
    
    Trả về:
        List các tuple (ngày, state)
    """
    from_date = timezone.now().date() - timedelta(days=days)
    queryset = KetQuaXoSo.objects.filter(ngay__gte=from_date).order_by('ngay')
    states = []
    for record in queryset.iterator():
        state = extract_state_from_day(record)
        if state:
            states.append( (record.ngay, state) )
    return states

def build_transition_matrix(states):
    """
    Xây dựng ma trận chuyển đổi (transition matrix) dựa trên danh sách states liên tiếp theo ngày.
    states: list các tuple (date, state) đã sắp xếp tăng dần theo ngày.
    
    Trả về:
        transition_matrix: dict dạng {state: {next_state: count, ...}, ...}
    """
    matrix = defaultdict(lambda: defaultdict(int))
    
    # Duyệt qua danh sách số ngày liên tiếp
    for i in range(len(states) - 1):
        current_state = states[i][1]
        next_state = states[i+1][1]
        matrix[current_state][next_state] += 1
    
    return matrix

def normalize_transition_matrix(matrix):
    """
    Chuẩn hóa transition matrix thành tỉ lệ phần trăm hay xác suất chuyển đổi.
    Trả về:
        dict dạng {state: {next_state: probability, ...}, ...}
    """
    norm_matrix = {}
    for state, transitions in matrix.items():
        total = sum(transitions.values())
        norm_matrix[state] = { next_state: count/total for next_state, count in transitions.items() }
    return norm_matrix

def print_transition_matrix(norm_matrix):
    """
    In ra transition matrix theo định dạng dễ đọc.
    """
    for state, transitions in norm_matrix.items():
        print(f"State '{state}':")
        for next_state, prob in transitions.items():
            print(f"   -> {next_state}: {prob:.2%}")
        print("")

def build_ngram_model(states, n=2):
    """
    Xây dựng mô hình n-gram (trong trường hợp này n=2 tương đương với bigram) từ chuỗi states.
    Trả về:
       dict dạng { n-gram tuple: occurrence counts }
    """
    ngram_counts = defaultdict(int)
    # Tạo n-gram từ danh sách state (chỉ lấy state thôi)
    state_seq = [s for _, s in states]
    for i in range(len(state_seq) - n + 1):
        ngram = tuple(state_seq[i:i+n])
        ngram_counts[ngram] += 1
    return ngram_counts

def predict_next_state(current_state, norm_matrix):
    """
    Dựa vào transition matrix, dự đoán state tiếp theo cho current_state.
    Trả về state dự đoán (dựa vào xác suất cao nhất) hoặc None.
    """
    if current_state not in norm_matrix:
        return None
    next_transitions = norm_matrix[current_state]
    # Dự đoán theo xác suất cao nhất
    predicted_state = max(next_transitions, key=next_transitions.get)
    return predicted_state

def run_markov_analysis(days=60):
    """
    Chạy toàn bộ phân tích Markov:
      - Truy xuất dữ liệu lịch sử
      - Xây dựng transition matrix và normalize thành xác suất
      - Xây dựng mô hình bigram (n-gram 2)
      - Dự đoán state tiếp theo cho state cuối cùng trong dữ liệu
    """
    # Lấy các state lịch sử theo ngày
    historical_states = get_historical_states(days)
    if len(historical_states) < 2:
        print("Không đủ dữ liệu lịch sử để xây dựng mô hình.")
        return

    # Xây dựng transition matrix
    matrix = build_transition_matrix(historical_states)
    norm_matrix = normalize_transition_matrix(matrix)
    print("Ma trận chuyển đổi (transition matrix):")
    print_transition_matrix(norm_matrix)

    # Xây dựng mô hình n-gram (bigram)
    bigram_model = build_ngram_model(historical_states, n=2)
    print("Mô hình Bigram:")
    for gram, count in bigram_model.items():
        print(f"{gram}: {count}")
    print("")

    # Dự đoán state tiếp theo dựa vào state cuối cùng trong dữ liệu lịch sử
    current_state = historical_states[-1][1]
    predicted = predict_next_state(current_state, norm_matrix)
    print(f"Dựa trên state hiện tại '{current_state}', dự đoán state tiếp theo là: {predicted}")

if __name__ == "__main__":
    # Chạy phân tích cho 60 ngày lịch sử (có thể điều chỉnh tham số)
    run_markov_analysis(days=60)