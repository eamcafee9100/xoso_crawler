
import re
import ast

def clean_predictions_data(final_predictions):
    """
    Làm sạch dữ liệu final_predictions để đảm bảo number là số đơn giản
    """
    cleaned_predictions = []
    
    for prediction in final_predictions:
        cleaned_prediction = prediction.copy()
        
        # Kiểm tra nếu number là string phức tạp
        if isinstance(prediction['number'], str) and prediction['number'].startswith('{'):
            try:
                # Trích xuất số từ string phức tạp
                # Tìm pattern như "('06', 0.0)" hoặc "('34', 0.0)"
                match = re.search(r"\('(\d+)',", prediction['number'])
                if match:
                    cleaned_prediction['number'] = match.group(1)
                else:
                    # Backup: thử parse JSON-like string
                    # Chuyển single quotes thành double quotes
                    json_str = prediction['number'].replace("'", '"')
                    try:
                        parsed = ast.literal_eval(prediction['number'])
                        if 'number' in parsed:
                            # Trích xuất số từ tuple
                            number_tuple = parsed['number']
                            if isinstance(number_tuple, str):
                                # Parse tuple string như "('06', 0.0)"
                                tuple_match = re.search(r"\('(\d+)',", number_tuple)
                                if tuple_match:
                                    cleaned_prediction['number'] = tuple_match.group(1)
                    except:
                        # Nếu không parse được, bỏ qua item này
                        continue
            except:
                # Nếu có lỗi, bỏ qua item này
                continue
        
        # Đảm bảo number là string 2 chữ số
        if isinstance(cleaned_prediction['number'], str):
            number = cleaned_prediction['number'].zfill(2)  # Thêm số 0 phía trước nếu cần
            cleaned_prediction['number'] = number
        
        cleaned_predictions.append(cleaned_prediction)
    
    return cleaned_predictions

test_data = [
    {'number': '{\'number\': "(\'01\', 0.0)", \'confidence\': 0.5, \'method\': \'recommended_numbers\', \'probability\': 0.5}', 'confidence': 0.8},
    {'number': '81', 'confidence': 0.6}
]

cleaned = clean_predictions_data(test_data)
print(cleaned)