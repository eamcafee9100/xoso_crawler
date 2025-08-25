#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 SIMPLE URL PATTERN TEST
Test Enhanced Deep Frequency Analyzer URLs and Views
"""

import os
import sys

import django
from django.conf import settings

# Add project path
project_path = r"C:\Users\n2t\Documents\xoso_crawler"
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)


def test_url_patterns():
    """Test URL patterns loading"""
    try:
        from predictions_tracker.urls import urlpatterns

        print(f"\n✅ URL Patterns loaded successfully")
        print(f"📊 Total patterns: {len(urlpatterns)}")

        # Find Enhanced Analyzer patterns
        analyzer_patterns = []
        for pattern in urlpatterns:
            if hasattr(pattern, "name") and pattern.name and "enhanced" in pattern.name:
                analyzer_patterns.append(pattern)

        print(f"\n🧠 Enhanced Analyzer patterns found: {len(analyzer_patterns)}")
        for pattern in analyzer_patterns:
            print(f"   - {pattern.name}: {pattern.pattern}")

        return True

    except Exception as e:
        print(f"❌ URL Patterns test failed: {e}")
        return False


def test_views_import():
    """Test views can be imported"""
    try:
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            enhanced_analyzer_dashboard,
            run_enhanced_analysis,
            validate_predictions,
        )

        print("\n✅ Main views imported successfully")

        from predictions_tracker.views_dir.enhanced_analyzer_simple_views import (
            enhanced_analyzer_dashboard_simple,
            run_enhanced_analysis_simple,
        )

        print("✅ Simple test views imported successfully")

        return True

    except Exception as e:
        print(f"❌ Views import test failed: {e}")
        return False


def test_enhanced_analyzer_module():
    """Test Enhanced Deep Frequency Analyzer module"""
    try:
        from analytic_frequence.enhanced_deep_frequency_analyzer import (
            EnhancedDeepFrequencyAnalyzer,
        )

        print("\n✅ Enhanced Deep Frequency Analyzer module imported successfully")

        # Try to create instance
        analyzer = EnhancedDeepFrequencyAnalyzer()
        print("✅ EnhancedDeepFrequencyAnalyzer instance created successfully")

        return True

    except Exception as e:
        print(f"❌ Enhanced Analyzer module test failed: {e}")
        return False


def test_django_reverse():
    """Test Django URL reversing"""
    try:
        from django.urls import reverse

        # Test main URLs
        test_urls = [
            "predictions_tracker:enhanced_analyzer_dashboard",
            "predictions_tracker:enhanced_analyzer_dashboard_test",
            "predictions_tracker:analysis_reports_center",
            "predictions_tracker:analysis_reports_center_test",
        ]

        print("\n🔗 Testing URL reversing:")
        for url_name in test_urls:
            try:
                reversed_url = reverse(url_name)
                print(f"   ✅ {url_name}: {reversed_url}")
            except Exception as e:
                print(f"   ❌ {url_name}: {e}")

        return True

    except Exception as e:
        print(f"❌ URL reverse test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Enhanced Deep Frequency Analyzer Tests")
    print("=" * 60)

    tests = [
        ("URL Patterns", test_url_patterns),
        ("Views Import", test_views_import),
        ("Enhanced Analyzer Module", test_enhanced_analyzer_module),
        ("Django URL Reverse", test_django_reverse),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    print("=" * 60)
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    failed_tests = total_tests - passed_tests

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")

    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")

    if failed_tests == 0:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🌐 You can now access:")
        print(
            "   - Dashboard: http://localhost:8000/predictions_tracker/enhanced-analyzer/"
        )
        print(
            "   - Test Dashboard: http://localhost:8000/predictions_tracker/enhanced-analyzer-test/"
        )
        print(
            "   - Reports: http://localhost:8000/predictions_tracker/enhanced-analyzer/reports/"
        )
        print(
            "   - Test Reports: http://localhost:8000/predictions_tracker/enhanced-analyzer-test/reports/"
        )
    else:
        print(f"⚠️  {failed_tests} test(s) failed. Please check the errors above.")

    return failed_tests == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
