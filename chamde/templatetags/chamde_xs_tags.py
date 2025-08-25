from django import template
from django.template.defaultfilters import floatformat
from itertools import combinations as itertools_combinations
from datetime import timedelta
import itertools
import json

register = template.Library()
@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
@register.filter
def avg_confidence(predictions):
    if not predictions:
        return 0
    total = sum(float(pred['confidence']) for pred in predictions)
    return total / len(predictions)

@register.filter
def count_hits(predictions):
    if not predictions:
        return 0
    return sum(1 for pred in predictions if pred['is_hit'])    
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
        return '[]'

@register.filter
def get_accuracy_values(method_accuracy):
    """Get list of accuracy values from method accuracy data"""
    try:
        return json.dumps([data['accuracy'] for data in method_accuracy.values()])
    except:
        return '[]'
    
       
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

@register.filter(name='combinations')
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

@register.filter(name='split')
def split(value, delimiter=','):
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
    return method_data.get('so_luong_trung', 0) > 0
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
    nums7 = [n[0] for n in predictions['7_ngay']['top_numbers'] if str(n[0]).startswith(str(digit))]
    nums10 = [n[0] for n in predictions['10_ngay']['top_numbers'] if str(n[0]).startswith(str(digit))]
    nums20 = [n[0] for n in predictions['20_ngay']['top_numbers'] if str(n[0]).startswith(str(digit))]
    return list(set(nums7) & set(nums10) & set(nums20))

@register.simple_tag
def get_best_pairs(predictions):
    best_pairs = []
    
    # Kiểm tra và lấy dữ liệu từ predictions
    periods = ['7_ngay', '10_ngay', '20_ngay']
    
    for period in periods:
        if not hasattr(predictions, period):
            continue
            
        period_data = getattr(predictions, period)
        
        # Kiểm tra tồn tại pair_stats
        if not hasattr(period_data, 'pair_stats') or not period_data.pair_stats:
            continue
            
        # Lấy các cặp tốt nhất từ mỗi period
        for pair, count in period_data.pair_stats[:5]:  # Lấy top 5
            score = count / int(period.split('_')[0])  # Tính điểm chuẩn hóa
            best_pairs.append((pair, score))
    
    # Sắp xếp theo điểm giảm dần
    best_pairs.sort(key=lambda x: x[1], reverse=True)
    
    # Loại bỏ trùng lặp và giữ lại các cặp tốt nhất
    unique_pairs = {}
    for pair, score in best_pairs:
        pair_key = tuple(sorted(pair))
        if pair_key not in unique_pairs or score > unique_pairs[pair_key][1]:
            unique_pairs[pair_key] = (pair, score)
    
    return sorted(unique_pairs.values(), key=lambda x: x[1], reverse=True)[:10]  # Trả về top 10

@register.simple_tag
def get_best_triples(predictions):
    best_triples = []
    
    # Kiểm tra các period dự đoán
    periods = ['7_ngay', '10_ngay', '20_ngay']
    
    for period in periods:
        # Kiểm tra period có tồn tại không
        if not hasattr(predictions, period):
            continue
            
        period_data = getattr(predictions, period)
        
        # Kiểm tra triple_stats có tồn tại và có dữ liệu không
        if not hasattr(period_data, 'triple_stats') or not period_data.triple_stats:
            continue
            
        # Lấy top 3 bộ ba từ mỗi period
        for triple, count in period_data.triple_stats[:3]:
            # Tính điểm chuẩn hóa theo số ngày
            days = int(period.split('_')[0])
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
    
    return sorted(unique_triples.values(), key=lambda x: x[1], reverse=True)[:5]  # Trả về top 5

@register.filter
def div(value, arg):
    """Chia value cho arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
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
        return ''
    
@register.filter
def replace(value, arg):
    """
    Thay thế chuỗi trong template
    Usage: {{ value|replace:"old,new" }}
    """
    if len(arg.split(',')) != 2:
        return value
    old, new = arg.split(',')
    return value.replace(old, new)

@register.filter(name='format_float')
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
    total = sum(p['accuracy'] for p in performance_list)
    return total / len(performance_list)

@register.filter
def mul(value, arg):
    """Nhân giá trị với một số."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    
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