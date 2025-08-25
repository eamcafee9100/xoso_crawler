#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎨 TEMPLATE RENDERING TEST
Test Enhanced Deep Frequency Analyzer Templates
"""

import os
import sys

# Add project path
project_path = r"C:\Users\n2t\Documents\xoso_crawler"
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Configure Django settings BEFORE importing django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")

import django
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)


def test_template_rendering():
    """Test template rendering"""
    try:
        # Create request factory
        factory = RequestFactory()

        # Test dashboard template
        print("\n🎨 Testing Dashboard Template Rendering...")
        request = factory.get("/enhanced-analyzer/")
        request.user = AnonymousUser()

        from predictions_tracker.views_dir.enhanced_analyzer_simple_views import (
            enhanced_analyzer_dashboard_simple,
        )

        response = enhanced_analyzer_dashboard_simple(request)

        if response.status_code == 200:
            print("✅ Dashboard template renders successfully")
            print(f"   Response size: {len(response.content)} bytes")
        else:
            print(f"❌ Dashboard template failed: Status {response.status_code}")
            return False

        # Test reports template
        print("\n📊 Testing Reports Template Rendering...")
        from predictions_tracker.views_dir.enhanced_analyzer_simple_views import (
            analysis_reports_center_simple,
        )

        response = analysis_reports_center_simple(request)

        if response.status_code == 200:
            print("✅ Reports template renders successfully")
            print(f"   Response size: {len(response.content)} bytes")
        else:
            print(f"❌ Reports template failed: Status {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"❌ Template rendering test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_ajax_endpoints():
    """Test AJAX endpoints"""
    try:
        print("\n⚡ Testing AJAX Endpoints...")
        factory = RequestFactory()

        # Test run analysis endpoint
        import json

        from predictions_tracker.views_dir.enhanced_analyzer_simple_views import (
            run_enhanced_analysis_simple,
        )

        test_data = {
            "start_date": "2025-07-01",
            "end_date": "2025-08-01",
            "significance_level": 0.05,
            "enable_full_pipeline": True,
        }

        request = factory.post(
            "/enhanced-analyzer/run-analysis/",
            data=json.dumps(test_data),
            content_type="application/json",
        )
        request.user = AnonymousUser()

        response = run_enhanced_analysis_simple(request)

        if response.status_code == 200:
            print("✅ Analysis endpoint works successfully")
            response_data = json.loads(response.content)
            if response_data.get("status") == "success":
                print("✅ Analysis returns success response")
            else:
                print("❌ Analysis returns error response")
                return False
        else:
            print(f"❌ Analysis endpoint failed: Status {response.status_code}")
            return False

        # Test validation endpoint
        from predictions_tracker.views_dir.enhanced_analyzer_simple_views import (
            validate_predictions_simple,
        )

        validation_data = {
            "prediction_date": "2025-08-01",
            "actual_results": ["01", "23", "45", "67", "89"],
        }

        request = factory.post(
            "/enhanced-analyzer/validate-predictions/",
            data=json.dumps(validation_data),
            content_type="application/json",
        )
        request.user = AnonymousUser()

        response = validate_predictions_simple(request)

        if response.status_code == 200:
            print("✅ Validation endpoint works successfully")
        else:
            print(f"❌ Validation endpoint failed: Status {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"❌ AJAX endpoints test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_static_files():
    """Test static files references"""
    try:
        print("\n📁 Testing Static Files References...")

        # Check if templates contain proper static references
        dashboard_template = r"C:\Users\n2t\Documents\xoso_crawler\predictions_tracker\templates\predictions_tracker\enhanced_analyzer_dashboard.html"
        reports_template = r"C:\Users\n2t\Documents\xoso_crawler\predictions_tracker\templates\predictions_tracker\analysis_reports_center.html"

        templates_to_check = [
            ("Dashboard Template", dashboard_template),
            ("Reports Template", reports_template),
        ]

        for template_name, template_path in templates_to_check:
            if os.path.exists(template_path):
                print(f"✅ {template_name} exists")

                with open(template_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for essential elements
                checks = [
                    ("Bootstrap CSS", "bootstrap@5.3.0"),
                    ("jQuery", "jquery-3.7.0"),
                    ("DataTables", "datatables.net"),
                    ("Font Awesome", "font-awesome"),
                    ("Chart.js", "chart.js"),
                ]

                for check_name, check_pattern in checks:
                    if check_pattern in content:
                        print(f"   ✅ {check_name} reference found")
                    else:
                        print(f"   ⚠️  {check_name} reference not found")
            else:
                print(f"❌ {template_name} not found at {template_path}")
                return False

        return True

    except Exception as e:
        print(f"❌ Static files test failed: {e}")
        return False


def run_template_tests():
    """Run all template tests"""
    print("🎨 Starting Template Tests")
    print("=" * 60)

    tests = [
        ("Template Rendering", test_template_rendering),
        ("AJAX Endpoints", test_ajax_endpoints),
        ("Static Files", test_static_files),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 60)
    print("📋 TEMPLATE TEST SUMMARY:")
    print("=" * 60)
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    failed_tests = total_tests - passed_tests

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")

    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")

    if failed_tests == 0:
        print("🎉 All template tests passed! Templates are ready to use.")
    else:
        print(f"⚠️  {failed_tests} test(s) failed. Please check the errors above.")

    return failed_tests == 0


if __name__ == "__main__":
    success = run_template_tests()
    sys.exit(0 if success else 1)
