# Django Development Excellence Guide

## 🔧 Environment Setup (MANDATORY)

### Virtual Environment Activation
```bash
# ALWAYS activate virtual environment before ANY Django operation
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Verify activation
which python  # Should point to .venv/bin/python
pip list      # Should show Django and project dependencies
```

**Rule**: Never run Django commands, install packages, or debug without activating `.venv` first.

---

## 📁 Project Structure (Non-negotiable)

```
project_name/
├── manage.py
├── requirements.txt
├── .venv/                 # Virtual environment
├── project_name/          # Main project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── apps/
    └── app_name/          # Each Django app
        ├── __init__.py
        ├── models.py      # Data models
        ├── views.py       # Business logic
        ├── urls.py        # URL routing
        ├── forms.py       # Input validation
        ├── serializers.py # API serialization
        ├── services.py    # Core business services
        ├── admin.py       # Admin interface
        ├── apps.py        # App configuration
        ├── migrations/    # Database migrations
        ├── templates/     # HTML templates
        │   └── app_name/
        ├── static/        # CSS, JS, images
        │   └── app_name/
        │       ├── css/
        │       ├── js/
        │       └── img/
        └── tests/         # All tests in one place
            ├── __init__.py
            ├── test_models.py
            ├── test_views.py
            ├── test_services.py
            └── test_forms.py
```

---

## 🏗️ Architecture Principles

### 1. Service Layer Pattern
```python
# apps/lottery/services.py
from typing import Optional, List
from dataclasses import dataclass
from datetime import date
from .models import KetQua

@dataclass(frozen=True)
class KetQuaData:
    """Immutable data contract"""
    ngay: date
    giai_db: str
    cham_dau: int
    cham_duoi: int

class KetQuaService:
    """Business logic layer - independent of views/forms"""
    
    def get_by_date(self, date: date) -> Optional[KetQuaData]:
        try:
            result = KetQua.objects.get(ngay=date)
            return KetQuaData(
                ngay=result.ngay,
                giai_db=result.giai_db,
                cham_dau=int(result.giai_db[0]),
                cham_duoi=int(result.giai_db[-1])
            )
        except KetQua.DoesNotExist:
            return None
    
    def get_recent(self, days: int = 7) -> List[KetQuaData]:
        from datetime import timedelta
        from django.utils import timezone
        
        cutoff = timezone.now().date() - timedelta(days=days)
        results = KetQua.objects.filter(ngay__gte=cutoff).order_by('-ngay')
        
        return [
            KetQuaData(
                ngay=r.ngay,
                giai_db=r.giai_db,
                cham_dau=int(r.giai_db[0]),
                cham_duoi=int(r.giai_db[-1])
            )
            for r in results
        ]
```

### 2. Models with Business Logic
```python
# apps/lottery/models.py
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class KetQua(models.Model):
    ngay = models.DateField(unique=True, db_index=True)
    giai_db = models.CharField(
        max_length=5,
        validators=[RegexValidator(r'^\d{5}$', 'Must be 5 digits')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ketqua'
        ordering = ['-ngay']
        verbose_name = 'Kết quả'
        verbose_name_plural = 'Kết quả'
        indexes = [
            models.Index(fields=['ngay', 'giai_db']),
        ]
    
    def __str__(self):
        return f"KetQua({self.ngay}, {self.giai_db})"
    
    @property
    def cham_dau(self):
        return int(self.giai_db[0])
    
    @property
    def cham_duoi(self):
        return int(self.giai_db[-1])
    
    def clean(self):
        from django.utils import timezone
        if self.ngay and self.ngay > timezone.now().date():
            raise ValidationError("Cannot create future results")
```

### 3. API Views with Consistent Response
```python
# apps/lottery/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from .services import KetQuaService
from .serializers import KetQuaSerializer

class KetQuaAPIView(APIView):
    def get(self, request):
        """Always return consistent response shape"""
        date_str = request.query_params.get('date')
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            service = KetQuaService()
            result = service.get_by_date(target_date)
            
            return Response({
                "success": True,
                "data": KetQuaSerializer(result).data if result else None,
                "error": None,
                "meta": {
                    "timestamp": timezone.now().isoformat(),
                    "version": "v1"
                }
            })
            
        except (ValueError, TypeError):
            return Response({
                "success": False,
                "data": None,
                "error": "Invalid date format. Use YYYY-MM-DD",
                "meta": {"timestamp": timezone.now().isoformat()}
            }, status=400)
        except Exception as e:
            return Response({
                "success": False,
                "data": None,
                "error": "Internal server error",
                "meta": {"timestamp": timezone.now().isoformat()}
            }, status=500)
```

---

## 🎨 Frontend Excellence

### Template Structure
```html
<!-- apps/lottery/templates/lottery/base.html -->
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Lottery App{% endblock %}</title>
    
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    {% load static %}
    <link href="{% static 'lottery/css/style.css' %}" rel="stylesheet">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JS -->
    <script src="{% static 'lottery/js/app.js' %}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Modern CSS with Variables
```css
/* apps/lottery/static/lottery/css/style.css */
:root {
    --primary-color: #007bff;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --spacing: 1rem;
    --border-radius: 8px;
}

.ketqua-card {
    border-radius: var(--border-radius);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s ease;
}

.ketqua-card:hover {
    transform: translateY(-2px);
}

.ketqua-number {
    font-size: 2rem;
    font-weight: bold;
    color: var(--primary-color);
}
```

### Modern JavaScript
```javascript
// apps/lottery/static/lottery/js/app.js
class LotteryApp {
    constructor() {
        this.apiBase = '/api/lottery';
        this.init();
    }
    
    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.bindEvents();
        });
    }
    
    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="load-result"]')) {
                this.loadResult(e);
            }
        });
    }
    
    async loadResult(event) {
        event.preventDefault();
        const date = event.target.dataset.date;
        
        try {
            const response = await fetch(`${this.apiBase}/ketqua/?date=${date}`);
            const data = await response.json();
            
            if (data.success) {
                this.renderResult(data.data);
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            this.showError('Connection error');
        }
    }
    
    renderResult(data) {
        const container = document.querySelector('#result-container');
        container.innerHTML = `
            <div class="ketqua-card card">
                <div class="card-header">
                    <h5>Kết quả ${data.ngay}</h5>
                </div>
                <div class="card-body">
                    <div class="ketqua-number">${data.giai_db}</div>
                    <p>Chạm đầu: ${data.cham_dau} | Chạm đuôi: ${data.cham_duoi}</p>
                </div>
            </div>
        `;
    }
    
    showError(message) {
        // Bootstrap toast notification
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger border-0';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        new bootstrap.Toast(toast).show();
    }
}

new LotteryApp();
```

---

## 🧪 Testing Strategy

### Service Tests
```python
# apps/lottery/tests/test_services.py
from django.test import TestCase
from datetime import date
from ..models import KetQua
from ..services import KetQuaService, KetQuaData

class TestKetQuaService(TestCase):
    def setUp(self):
        self.service = KetQuaService()
        self.test_date = date(2025, 1, 15)
        KetQua.objects.create(ngay=self.test_date, giai_db="12345")
    
    def test_get_by_date_returns_correct_data(self):
        result = self.service.get_by_date(self.test_date)
        
        self.assertIsInstance(result, KetQuaData)
        self.assertEqual(result.ngay, self.test_date)
        self.assertEqual(result.giai_db, "12345")
        self.assertEqual(result.cham_dau, 1)
        self.assertEqual(result.cham_duoi, 5)
    
    def test_get_by_date_nonexistent_returns_none(self):
        result = self.service.get_by_date(date(2025, 12, 31))
        self.assertIsNone(result)
```

### API Tests
```python
# apps/lottery/tests/test_views.py
from rest_framework.test import APITestCase
from datetime import date
from ..models import KetQua

class TestKetQuaAPI(APITestCase):
    def test_get_success_response_format(self):
        KetQua.objects.create(ngay=date(2025, 1, 15), giai_db="12345")
        
        response = self.client.get('/api/lottery/ketqua/', {'date': '2025-01-15'})
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # Verify response structure
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertIn('error', data)
        self.assertIn('meta', data)
        
        # Verify success case
        self.assertTrue(data['success'])
        self.assertIsNone(data['error'])
        self.assertIsNotNone(data['data'])
```

---

## 🔧 Code Modification Rules

### Before Modifying ANY Code
1. **Activate `.venv`** - No exceptions
2. **Run existing tests** - `python manage.py test apps.lottery`
3. **Identify dependencies** - Who calls this function?
4. **Document changes** - Why are you changing it?

### Safe Modification Pattern
```python
# BEFORE: Original function
def get_ketqua_data(date):
    return KetQua.objects.get(ngay=date)

# AFTER: Backward-compatible modification
def get_ketqua_data(date, format='object'):
    """
    MODIFICATION LOG:
    - Added format parameter for API flexibility
    - Maintains backward compatibility with default 'object'
    - All existing callers continue to work
    
    Args:
        date: Target date
        format: 'object' (default), 'dict', 'serialized'
    """
    result = KetQua.objects.get(ngay=date)
    
    if format == 'dict':
        return {
            'ngay': result.ngay,
            'giai_db': result.giai_db,
            'cham_dau': result.cham_dau,
            'cham_duoi': result.cham_duoi
        }
    elif format == 'serialized':
        from .serializers import KetQuaSerializer
        return KetQuaSerializer(result).data
    else:  # 'object' - backward compatible
        return result
```

---

## 🚀 Performance & Security

### Database Optimization
```python
# apps/lottery/models.py
class KetQuaQuerySet(models.QuerySet):
    def recent(self, days=30):
        from datetime import timedelta
        from django.utils import timezone
        cutoff = timezone.now().date() - timedelta(days=days)
        return self.filter(ngay__gte=cutoff).select_related()

class KetQua(models.Model):
    objects = KetQuaQuerySet.as_manager()
    
    class Meta:
        indexes = [
            models.Index(fields=['-ngay']),  # Common query pattern
            models.Index(fields=['giai_db', 'ngay']),
        ]
```

### Security Checklist
```python
# apps/lottery/forms.py
from django import forms
from django.core.validators import RegexValidator
from django.utils.html import escape

class KetQuaForm(forms.ModelForm):
    giai_db = forms.CharField(
        validators=[RegexValidator(r'^\d{5}$', 'Must be 5 digits')],
        widget=forms.TextInput(attrs={
            'pattern': r'\d{5}',
            'maxlength': '5',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = KetQua
        fields = ['ngay', 'giai_db']
    
    def clean_giai_db(self):
        value = self.cleaned_data['giai_db']
        return escape(value)  # Prevent XSS
```

---

## 📋 Quick Commands

### Development Workflow
```bash
# 1. Always activate environment first
source .venv/bin/activate

# 2. Install/update dependencies
pip install -r requirements.txt

# 3. Database operations
python manage.py makemigrations
python manage.py migrate

# 4. Run tests
python manage.py test apps.lottery

# 5. Run development server
python manage.py runserver

# 6. Create superuser
python manage.py createsuperuser

# 7. Collect static files (production)
python manage.py collectstatic
```

### Testing Commands
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.lottery

# Run specific test file
python manage.py test apps.lottery.tests.test_services

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 🎯 Key Principles

1. **Environment First**: Always activate `.venv` before any Django operation
2. **Structure Matters**: Follow the app-based structure consistently
3. **Service Layer**: Business logic goes in services, not views
4. **Test Everything**: Tests go in `tests/` directory within each app
5. **Consistent APIs**: Always return the same response format
6. **Security by Default**: Validate and escape all inputs
7. **Performance Awareness**: Use proper indexing and query optimization
8. **Document Changes**: Every modification needs a clear reason

Remember: Write code that your future self (and teammates) will thank you for.