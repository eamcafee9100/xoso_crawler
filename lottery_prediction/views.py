from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone


def index(request):
    """Render the main prediction interface"""
    default_date = timezone.now().date() + timedelta(days=1)

    context = {
        "default_date": default_date,
    }

    return render(request, "prediction/index.html", context)
