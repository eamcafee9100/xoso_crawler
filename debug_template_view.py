#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug script for template view
"""
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory

from analytic_frequence.template_views import UltimatePredictionTemplateView


def debug_template_view():
    print("=== TEMPLATE VIEW DEBUG ===")

    # Create a view instance
    view = UltimatePredictionTemplateView()
    view.setup(RequestFactory().get("/"))

    # Get context data
    context = view.get_context_data()
    sample_prediction = context.get("sample_prediction")

    if sample_prediction:
        print(f"Sample prediction found!")
        print(f'Predictions: {sample_prediction.get("predictions")}')
        print(f'Type: {type(sample_prediction.get("predictions"))}')

        predictions = sample_prediction.get("predictions", [])
        if predictions:
            print(f"Number of predictions: {len(predictions)}")
            for i, pred in enumerate(predictions):
                print(f"  Prediction {i}: {pred} (type: {type(pred)})")
                if hasattr(pred, "__dict__"):
                    print(f"    Attributes: {pred.__dict__}")
                elif hasattr(pred, "number"):
                    print(f"    Number: {pred.number}")
        else:
            print("Predictions list is empty")
    else:
        print("No sample prediction found")


if __name__ == "__main__":
    debug_template_view()
