import json
import logging
import os
import sys
from datetime import datetime

import django

# Setup logging first
logging.basicConfig(level=logging.DEBUG)

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
sys.path.append(".")
django.setup()

from django.http import JsonResponse
from django.test import RequestFactory

# Import the view
from analytic_frequence.template_views import ajax_prediction_api


def test_ajax_with_debug():
    """Test AJAX with debug logging"""
    print("=== TESTING AJAX WITH DEBUG LOGS ===")

    # Create a mock request
    factory = RequestFactory()

    # Test data
    test_date = "2025-08-12"

    # Create POST request with JSON data
    import json

    request = factory.post(
        "/ajax/prediction/",
        data=json.dumps({"prediction_date": test_date}),
        content_type="application/json",
    )

    try:
        # Call the view
        response = ajax_prediction_api(request)

        print(f"Response type: {type(response)}")
        print(f"Status code: {response.status_code}")

        if hasattr(response, "content"):
            content = response.content.decode("utf-8")
            print(f"Response length: {len(content)}")

            try:
                data = json.loads(content)
                if "error" in data:
                    print(f"ERROR: {data['error']}")
                elif "prediction_data" in data:
                    predictions = data["prediction_data"].get("predictions", [])
                    print(f"Predictions count: {len(predictions)}")
                    print(
                        f"First prediction: {predictions[0] if predictions else 'None'}"
                    )

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")

    except Exception as e:
        print(f"ERROR calling ajax_prediction_api: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_ajax_with_debug()
