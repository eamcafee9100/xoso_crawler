# results/calculation_methods.py

CALCULATION_METHODS = {
    '36': {
        'function': 'calculate_36_method',
        'args': ['giai_1', 'giai_2', 'giai_4', 'giai_6'],
        'description': 'Phương pháp 36: Lấy số từ giải 1 + 6.1 là đuôi, 2.2 + 4.4 là đầu.',
    },
    'tu_thu_de': {
        'function': 'calculate_two_digits',
        'args': ['giai_4', 'giai_5'],
        'description': 'Tứ thủ đề: Tạo bộ số từ giải 4 và giải 5.',
    },
    '3_cang': {
        'function': 'calculate_three_digits',
        'args': ['giai_4', 'giai_5'],
        'description': 'giải 24_3 càng: Tạo bộ số 3 chữ số từ giải 4.1, + 5.5 và 4.4 là càng đầu.',
    },
    'giai_db': {
        'function': 'calculate_special_prize_method',
        'args': ['giai_db'],
        'description': 'Dựa trên giải đặc biệt: Lấy 2 số cuối và bóng của chúng.',
    },
    '_105_de_4_so': {
        'function': '_105_de_4_so',
        'args': ['giai_3', 'giai_4', 'giai_6'],
        'description': 'Dựa trên giải 3.1, 4.1 và 6.3,3.6: Tạo bộ đề 4 số từ các giải này. Ghép càng',
    },
    'pascal': {
        'function': 'calculate_pascal_method',
        'args': ['giai_db', 'giai_1'],
        'description': 'Soi cầu Pascal: Dùng tam giác Pascal từ giải đặc biệt và giải nhất',
    },

}

def calculate_36_method(giai1, giai2, giai4, giai6):
    from .models import DanDeDacBiet  # Nhập tại đây để tránh vòng lặp
    return DanDeDacBiet.calculate_36_method(giai1, giai2, giai4, giai6)

def calculate_two_digits(giai4, giai5):
    from .models import DanDeDacBiet
    return DanDeDacBiet.calculate_two_digits(giai4, giai5)

def calculate_three_digits(giai4, giai5):
    from .models import DanDeDacBiet
    return DanDeDacBiet.calculate_three_digits(giai4, giai5)

def calculate_special_prize_method(giai_db):
    from .models import DanDeDacBiet
    return DanDeDacBiet.calculate_special_prize_method(giai_db)

def _105_de_4_so(giai3, giai4, giai6):
    from .models import DanDeDacBiet
    return DanDeDacBiet._105_de_4_so(giai3, giai4, giai6)

def calculate_pascal_method(giai_db, giai_1):
    from .models import DanDeDacBiet
    return DanDeDacBiet.calculate_pascal_method(giai_db, giai_1)