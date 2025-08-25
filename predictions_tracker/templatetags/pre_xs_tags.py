import itertools
import json
from datetime import timedelta
from itertools import combinations as itertools_combinations

from django import template
from django.template.defaultfilters import floatformat
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def format_confidence(confidence):
    """Format confidence as percentage"""
    try:
        return f"{float(confidence) * 100:.1f}%"
    except (TypeError, ValueError):
        return "0%"


@register.filter
def extract_number(prediction):
    """Extract number from prediction object or string"""
    if isinstance(prediction, dict):
        return prediction.get("number", prediction.get("value", ""))
    return str(prediction)


@register.filter
def prediction_class(confidence):
    """Get CSS class based on confidence level"""
    try:
        conf = float(confidence)
        if conf >= 0.7:
            return "confidence-high"
        elif conf >= 0.4:
            return "confidence-medium"
        else:
            return "confidence-low"
    except (TypeError, ValueError):
        return "confidence-low"


@register.filter
def get_matched_predictions(predictions, actual_numbers):
    """Lấy danh sách predictions trùng với kết quả thực tế"""
    if not predictions or not actual_numbers:
        return []

    matched = []
    actual_set = set(str(num) for num in actual_numbers)

    for pred in predictions:
        pred_number = str(pred.get("number", pred) if isinstance(pred, dict) else pred)
        if pred_number in actual_set:
            matched.append(pred)

    return matched


@register.filter
def filter_confidence(predictions, min_confidence):
    """Lọc predictions theo confidence tối thiểu"""
    if not predictions:
        return []

    try:
        min_conf = float(min_confidence)
        return [p for p in predictions if p.get("confidence", 0) >= min_conf]
    except (ValueError, TypeError):
        return predictions


@register.filter
def to_json(value):
    """Convert value to JSON"""
    try:
        return mark_safe(json.dumps(value))
    except (TypeError, ValueError):
        return "{}"


@register.filter
def replace(value, args):
    """Replace a string in the value with another string"""
    try:
        if "," in args:
            old, new = args.split(",", 1)
            return str(value).replace(old, new)
        return value
    except (ValueError, TypeError):
        return value


@register.filter
def avg_confidence(predictions):
    if not predictions:
        return 0
    total = sum(float(pred["confidence"]) for pred in predictions)
    return total / len(predictions)


@register.filter
def count_hits(predictions):
    if not predictions:
        return 0
    return sum(1 for pred in predictions if pred["is_hit"])


@register.filter
def absolute(value):
    """Get absolute value with error handling"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0


@register.filter
def map(value, key):
    """Map a list of dicts or tuples by key or index"""
    try:
        if isinstance(value, list):
            if value and isinstance(value[0], dict):
                return [item[key] for item in value]
            elif value and isinstance(value[0], tuple):
                idx = int(key) if isinstance(key, str) and key.isdigit() else key
                return [item[idx] for item in value]
        return []
    except (KeyError, IndexError, TypeError):
        return []


@register.filter
def get_method_names(method_accuracy):
    """Get list of method names from method accuracy data"""
    try:
        return json.dumps(list(method_accuracy.keys()))
    except:
        return "[]"


@register.filter
def get_accuracy_values(method_accuracy):
    """Get list of accuracy values from method accuracy data"""
    try:
        return json.dumps([data["accuracy"] for data in method_accuracy.values()])
    except:
        return "[]"


@register.simple_tag
def debug_data(value):
    """Print debug info about the variable"""
    try:
        if isinstance(value, dict):
            return json.dumps(value, indent=2)
        return str(value)
    except Exception as e:
        return f"Error debugging value: {str(e)}"


@register.filter
def percentage(count, items):
    """Calculate percentage of count from sum of all counts in items list"""
    if not items:
        return 0
    total = sum(count for _, count in items)
    if total == 0:
        return 0
    return (count / total) * 100


@register.filter
def format_percentage(value):
    """Format number as percentage"""
    try:
        return f"{float(value):.1f}%"
    except (ValueError, TypeError):
        return "0.0%"


@register.filter
def dict_to_list(value, key):
    """Chuyển dictionary items thành list theo key"""
    return [item[int(key)] for item in value]


@register.filter
def intersect(list1, list2):
    """Tìm phần tử chung của 2 list"""
    return list(set(list1) & set(list2))


@register.filter
def divide(value, arg):
    """Tính tỷ lệ phần trăm (arg/value)*100"""
    try:
        return (float(arg) / float(value)) * 100 if value else 0
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def calculate_match_rate(top_numbers, matches):
    """Tính tỷ lệ trùng khớp được tối ưu"""
    try:
        if not matches:
            return 0
        return (len(matches) / len(top_numbers)) * 100
    except (TypeError, ZeroDivisionError):
        return 0


@register.filter(name="combinations")
def make_combinations(items, r):
    """Tạo các tổ hợp từ list (đổi tên để tránh trùng lặp)"""
    try:
        items = list(items)
        return list(itertools_combinations(items, int(r)))
    except:
        return []


# results/templatetags/xs_tags.py
@register.filter
def get_item_dict(dictionary, key):
    """
    Lấy giá trị từ dictionary theo key, an toàn với None
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def get_item(collection, key):
    if isinstance(collection, dict):
        return collection.get(key)
    elif isinstance(collection, list):
        try:
            return collection[int(key)]  # Access list by index
        except (IndexError, ValueError):
            return None
    return None


@register.filter(name="split")
def split(value, delimiter=","):
    """Split a string into a list using the given delimiter"""
    return value.split(delimiter)


@register.filter
def map_second(items):
    return [float(conf) for _, conf in items]


@register.filter
def average(values):
    if not values:
        return 0
    return sum(values) / len(values) * 100


@register.filter
def filter_hits(items, actual_numbers):
    return [num for num, _ in items if str(num).zfill(2) in actual_numbers]


@register.filter
def has_hits(cach_tinh_dict, method_ten):
    method_data = cach_tinh_dict.get(method_ten, {})
    return method_data.get("so_luong_trung", 0) > 0


@register.filter
def filter_by_first_digit(numbers, digit):
    """Lọc các số bắt đầu bằng chữ số chỉ định"""
    return [num for num in numbers if str(num).startswith(str(digit))]


@register.filter
def get_count_by_pair(pair_stats, pair_to_find):
    """Tìm count theo pair trong list pair_stats"""
    for pair, count in pair_stats:
        if pair == pair_to_find:
            return count
    return 0


@register.filter
def get_numbers(numbers_with_prob):
    """Lấy danh sách số từ list (number, probability)"""
    return [num for num, prob in numbers_with_prob]


@register.filter
def get_common_numbers(predictions, digit):
    """
    Lấy các số xuất hiện ở cả 3 chu kỳ dự đoán (7, 10, 20 ngày) cho đầu số 'digit'.
    predictions: dict chứa các keys '7_ngay', '10_ngay', '20_ngay', mỗi key có 'top_numbers'
    digit: chuỗi đầu số cần lọc (ví dụ: '0', '1', ...)
    """
    nums7 = [
        n[0]
        for n in predictions["7_ngay"]["top_numbers"]
        if str(n[0]).startswith(str(digit))
    ]
    nums10 = [
        n[0]
        for n in predictions["10_ngay"]["top_numbers"]
        if str(n[0]).startswith(str(digit))
    ]
    nums20 = [
        n[0]
        for n in predictions["20_ngay"]["top_numbers"]
        if str(n[0]).startswith(str(digit))
    ]
    return list(set(nums7) & set(nums10) & set(nums20))


@register.simple_tag
def get_best_pairs(predictions):
    best_pairs = []

    # Kiểm tra và lấy dữ liệu từ predictions
    periods = ["7_ngay", "10_ngay", "20_ngay"]

    for period in periods:
        if not hasattr(predictions, period):
            continue

        period_data = getattr(predictions, period)

        # Kiểm tra tồn tại pair_stats
        if not hasattr(period_data, "pair_stats") or not period_data.pair_stats:
            continue

        # Lấy các cặp tốt nhất từ mỗi period
        for pair, count in period_data.pair_stats[:5]:  # Lấy top 5
            score = count / int(period.split("_")[0])  # Tính điểm chuẩn hóa
            best_pairs.append((pair, score))

    # Sắp xếp theo điểm giảm dần
    best_pairs.sort(key=lambda x: x[1], reverse=True)

    # Loại bỏ trùng lặp và giữ lại các cặp tốt nhất
    unique_pairs = {}
    for pair, score in best_pairs:
        pair_key = tuple(sorted(pair))
        if pair_key not in unique_pairs or score > unique_pairs[pair_key][1]:
            unique_pairs[pair_key] = (pair, score)

    return sorted(unique_pairs.values(), key=lambda x: x[1], reverse=True)[
        :10
    ]  # Trả về top 10


@register.simple_tag
def get_best_triples(predictions):
    best_triples = []

    # Kiểm tra các period dự đoán
    periods = ["7_ngay", "10_ngay", "20_ngay"]

    for period in periods:
        # Kiểm tra period có tồn tại không
        if not hasattr(predictions, period):
            continue

        period_data = getattr(predictions, period)

        # Kiểm tra triple_stats có tồn tại và có dữ liệu không
        if not hasattr(period_data, "triple_stats") or not period_data.triple_stats:
            continue

        # Lấy top 3 bộ ba từ mỗi period
        for triple, count in period_data.triple_stats[:3]:
            # Tính điểm chuẩn hóa theo số ngày
            days = int(period.split("_")[0])
            score = count / days
            best_triples.append((triple, score))

    # Sắp xếp theo điểm giảm dần
    best_triples.sort(key=lambda x: x[1], reverse=True)

    # Loại bỏ trùng lặp (giữ lại bộ có điểm cao nhất)
    unique_triples = {}
    for triple, score in best_triples:
        triple_key = tuple(sorted(triple))
        if triple_key not in unique_triples or score > unique_triples[triple_key][1]:
            unique_triples[triple_key] = (triple, score)

    return sorted(unique_triples.values(), key=lambda x: x[1], reverse=True)[
        :5
    ]  # Trả về top 5


@register.filter
def div(value, arg):
    """Chia value cho arg"""
    try:
        arg_val = float(arg)
        if arg_val == 0:
            return 0
        return float(value) / arg_val
    except (TypeError, ValueError):
        return 0


@register.filter
def unique(value):
    return list(set(value))


@register.filter
def subtract(value, arg):
    """Trừ value cho arg"""
    return int(value) - int(arg)


@register.filter
def center(value, arg):
    """Tạo list với độ dài arg chứa value"""
    return [value] * int(arg)


@register.filter
def get_loto_numbers(numbers):
    """Tổ chức các số lô tô theo đầu số"""
    loto_dict = {}
    for num in numbers:
        if len(num) == 2:
            first_digit = num[0]
            if first_digit not in loto_dict:
                loto_dict[first_digit] = []
            if num not in loto_dict[first_digit]:
                loto_dict[first_digit].append(num)
    # Sắp xếp các số trong mỗi đầu
    for digit in loto_dict:
        loto_dict[digit].sort()
    return loto_dict


@register.filter
def get_loto_gan(numbers, days=10):
    """Xác định các lô gan (lô lâu không về)"""
    # Logic xác định lô gan - cần triển khai thêm
    return []


@register.filter
def get_attribute(obj, attr):
    """
    Retrieves an attribute of an object dynamically using the attribute name provided.
    If the attribute does not exist, returns an empty string.
    """
    try:
        return getattr(obj, attr)
    except AttributeError:
        return ""


@register.filter(name="format_float")
def format_float(value, format_str):
    try:
        return format_str % float(value)
    except (ValueError, TypeError):
        return value


@register.filter
def get_hit_count(length, records):
    return sum(1 for r in records if r.hit_count > 0)


@register.filter
def get_hit_rate(length, records):
    hit_count = sum(1 for r in records if r.hit_count > 0)
    return round(hit_count / length * 100, 2) if length > 0 else 0


@register.filter
def get_winning_numbers(records):
    winning_numbers = []
    for record in records:
        if record.hit_count > 0:
            winning_numbers.extend(record.winning_numbers)
    return list(set(winning_numbers))  # Remove duplicates


@register.filter
def map_attribute(value, arg):
    """Lấy thuộc tính từ danh sách object"""
    return [getattr(item, arg) for item in value]


@register.filter
def avg_accuracy(performance_list):
    if not performance_list:
        return 0
    total = sum(p["accuracy"] for p in performance_list)
    return total / len(performance_list)


@register.filter
def mul(value, arg):
    """Nhân giá trị với một số."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def increment(value):
    """Increments the given value by 1."""
    return int(value) + 1


@register.filter
def zip_lists(a, b):
    return zip(a, b)


@register.filter
def zip(a, b):
    """Zip two lists together"""
    return itertools.zip_longest(a, b)


@register.filter
def add_days(value, days):
    """Add/subtract days from a date"""
    try:
        return value + timedelta(days=int(days))
    except:
        return value


@register.filter
def last_two_chars(value):
    """Return the last two characters of a string, or the string if it's two characters or less."""
    if not value:  # Handle None or empty input
        return ""
    if not isinstance(value, str):  # Convert non-strings to string
        value = str(value)
    if len(value) < 2:  # Handle strings with fewer than 2 characters
        return value
    return value[-3:]


@register.filter
def sort_methods_numerical(methods):
    """Sort methods by numerical value of their name instead of alphabetical."""

    # ✅ FIX: Handle NoneType to prevent 'NoneType' object is not iterable
    if methods is None:
        return []

    def get_sort_key(method):
        try:
            # Try to extract number from method name
            import re

            # Find the first number in the method name
            match = re.search(r"\d+", method.name)
            if match:
                return int(match.group())
            else:
                # If no number found, sort alphabetically as fallback
                return float("inf"), method.name
        except (AttributeError, ValueError):
            # If any error, sort by name alphabetically
            return float("inf"), (
                str(method.name) if hasattr(method, "name") else str(method)
            )

    return sorted(methods, key=get_sort_key)


@register.simple_tag
def get_hit_badges_data(method_data):
    """
    ✅ Enhanced - So sánh từng prediction number với kết quả và tạo badges theo prediction index

    Returns: List[dict] với format:
        [
            {
                'day': int,                    # 1, 2, 3
                'prediction_index': int,       # 0 hoặc 1
                'prediction_number': str,      # Số dự đoán trúng
                'bg_color': str,              # Màu nền
                'text_color': str,            # Màu chữ
                'hit_numbers': List[str]       # Các số trúng
            }
        ]
    """
    if not method_data.get("has_data") or not method_data.get("predicted_numbers"):
        return []

    hit_badges = []
    predicted_numbers = method_data.get("predicted_numbers", [])

    # ✅ Định nghĩa màu theo prediction index và ngày
    PREDICTION_COLORS = {
        0: {  # method_data.predicted_numbers.0
            1: {"bg": "#28a745", "text": "white"},  # Xanh lá - Ngày 1
            2: {"bg": "#007bff", "text": "white"},  # Xanh dương - Ngày 2
            3: {"bg": "#ffc107", "text": "#000"},  # Vàng - Ngày 3
        },
        1: {  # method_data.predicted_numbers.1
            1: {"bg": "#2a482eff", "text": "white"},  # Xanh lá đậm - Ngày 1
            2: {"bg": "#364452ff", "text": "white"},  # Xanh dương đậm - Ngày 2
            3: {"bg": "#443e29ff", "text": "#000"},  # Vàng đậm - Ngày 3
        },
    }

    for tracking_result in method_data.get("tracking_results", []):
        if (
            not tracking_result.get("has_result")
            or tracking_result.get("hit_count", 0) <= 0
        ):
            continue

        day = tracking_result.get("day")
        hit_numbers = tracking_result.get("hit_numbers", [])
        hit_numbers_str = [str(num).zfill(2) for num in hit_numbers]

        # ✅ LOGIC MỚI: CHỈ 1 BADGE/NGÀY, PRIORITY INDEX 0 > INDEX 1
        badge_created = False

        # Kiểm tra predicted_numbers[0] trước (priority cao hơn)
        if len(predicted_numbers) > 0:
            pred_0_str = str(predicted_numbers[0]).zfill(2)
            if pred_0_str in hit_numbers_str:
                color_info = PREDICTION_COLORS.get(0, {}).get(day)
                if color_info:
                    hit_badges.append(
                        {
                            "day": day,
                            "prediction_index": 0,
                            "prediction_number": pred_0_str,
                            "bg_color": color_info["bg"],
                            "text_color": color_info["text"],
                            "hit_numbers": [pred_0_str],
                            "position": len(hit_badges) + 1,
                        }
                    )
                    badge_created = True

        # Chỉ kiểm tra predicted_numbers[1] nếu [0] không trúng
        if not badge_created and len(predicted_numbers) > 1:
            pred_1_str = str(predicted_numbers[1]).zfill(2)
            if pred_1_str in hit_numbers_str:
                color_info = PREDICTION_COLORS.get(1, {}).get(day)
                if color_info:
                    hit_badges.append(
                        {
                            "day": day,
                            "prediction_index": 1,
                            "prediction_number": pred_1_str,
                            "bg_color": color_info["bg"],
                            "text_color": color_info["text"],
                            "hit_numbers": [pred_1_str],
                            "position": len(hit_badges) + 1,
                        }
                    )

    return hit_badges


@register.filter
def avg_hit_rate(training_data):
    """
    Tính average hit rate của training data

    Args:
        training_data: List of training data points

    Returns:
        float: Average hit rate
    """
    if not training_data:
        return 0

    total_hit_rate = sum(point.get("hit_rate", 0) for point in training_data)
    return total_hit_rate / len(training_data)


@register.simple_tag
def format_weekly_predictions(sessions):
    """
    Format multiple WeeklyTrackingSession predictions for display in table cell

    Args:
        sessions: List of WeeklyTrackingSession objects

    Returns:
        dict: {
            "display_text": "12,34 | 56,78",
            "has_hits": bool,
            "hit_count": int,
            "total_predictions": int,
            "sessions_info": [session_data, ...]
        }
    """
    if not sessions:
        return {
            "display_text": "-",
            "has_hits": False,
            "hit_count": 0,
            "total_predictions": 0,
            "sessions_info": [],
        }

    predictions_text = []
    total_hits = 0
    total_predictions = 0
    sessions_info = []

    for session in sessions:
        # Format predicted numbers
        if session.predicted_numbers:
            pred_text = ",".join(map(str, session.predicted_numbers))
            predictions_text.append(pred_text)

        # Calculate totals
        if session.status == "completed":
            total_hits += session.hit_count
            total_predictions += session.total_predicted

        # Session info for tooltips/badges
        sessions_info.append(
            {
                "id": session.id,
                "predicted_numbers": session.predicted_numbers,
                "hit_numbers": session.hit_numbers,
                "hit_count": session.hit_count,
                "total_predicted": session.total_predicted,
                "hit_rate": session.hit_rate,
                "status": session.status,
                "prediction_date": session.prediction_date,
                "tracking_date": session.tracking_date,
            }
        )

    # Join multiple predictions with " | "
    display_text = " | ".join(predictions_text) if predictions_text else "-"

    return {
        "display_text": display_text,
        "has_hits": total_hits > 0,
        "hit_count": total_hits,
        "total_predictions": total_predictions,
        "sessions_info": sessions_info,
        "cell_class": (
            "hit-cell"
            if total_hits > 0
            else ("miss-cell" if total_predictions > 0 else "no-data-cell")
        ),
    }


@register.simple_tag
def get_weekly_hit_badges(sessions):
    """
    Generate hit badges for weekly tracking sessions (similar to monthly report)

    Args:
        sessions: List of WeeklyTrackingSession objects

    Returns:
        list: Badge data for template rendering
    """
    badges = []
    
    # ✅ Add None protection
    if not sessions:
        return badges

    for i, session in enumerate(sessions):
        if session.status == "completed" and session.hit_count > 0:
            # Create badge for each session with hits
            badge_data = {
                "session_index": i,
                "hit_count": session.hit_count,
                "prediction_date": session.prediction_date,
                "tracking_date": session.tracking_date,
                "hit_numbers": session.hit_numbers,
                "prediction_numbers": session.predicted_numbers,
                # Badge positioning
                "position_right": 2 + (i * 14),  # Stagger badges
                # Badge color based on hit count
                "bg_color": (
                    "#28a745"
                    if session.hit_count >= 2
                    else "#007bff" if session.hit_count == 1 else "#6c757d"
                ),
                "text_color": "white",
                "title": f"Session {i+1}: {session.hit_count} hits on {session.tracking_date.strftime('%d/%m')}",
            }
            badges.append(badge_data)

    return badges
