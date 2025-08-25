# context_processors.py
def version_context(request):
    """Thêm thông tin phiên bản vào context mọi template"""
    from .models import SoiCauBacNho
    
    # Lấy phiên bản đã chọn từ session hoặc mặc định
    selected_version = request.session.get('selected_version', 'v1')
    
    return {
        'available_versions': SoiCauBacNho.VERSION_CHOICES,
        'selected_version': selected_version
    }