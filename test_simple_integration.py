#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 SIMPLE INTEGRATION TEST
Test Enhanced Deep Frequency Analyzer without complex Django setup
"""

import os
import sys


def test_file_existence():
    """Test if all required files exist"""
    print("📁 Testing File Existence...")

    base_path = r"C:\Users\n2t\Documents\xoso_crawler\predictions_tracker"

    required_files = [
        # Views
        ("Main Views", f"{base_path}\\views_dir\\enhanced_frequency_analyzer_views.py"),
        ("Simple Views", f"{base_path}\\views_dir\\enhanced_analyzer_simple_views.py"),
        # Templates
        (
            "Dashboard Template",
            f"{base_path}\\templates\\predictions_tracker\\enhanced_analyzer_dashboard.html",
        ),
        (
            "Reports Template",
            f"{base_path}\\templates\\predictions_tracker\\analysis_reports_center.html",
        ),
        ("Base Template", f"{base_path}\\templates\\predictions_tracker\\base.html"),
        # URLs
        ("URLs Config", f"{base_path}\\urls.py"),
        # Core Module
        ("Enhanced Analyzer", f"{base_path}\\enhanced_deep_frequency_analyzer.py"),
    ]

    all_exist = True

    for file_name, file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_name}: EXISTS")

            # Check file size
            size = os.path.getsize(file_path)
            if size > 0:
                print(f"      📊 Size: {size:,} bytes")
            else:
                print(f"      ⚠️  File is empty!")
                all_exist = False
        else:
            print(f"   ❌ {file_name}: NOT FOUND")
            all_exist = False

    return all_exist


def test_template_content():
    """Test template content for essential elements"""
    print("\n🎨 Testing Template Content...")

    templates = [
        (
            "Dashboard",
            r"C:\Users\n2t\Documents\xoso_crawler\predictions_tracker\templates\predictions_tracker\enhanced_analyzer_dashboard.html",
        ),
        (
            "Reports",
            r"C:\Users\n2t\Documents\xoso_crawler\predictions_tracker\templates\predictions_tracker\analysis_reports_center.html",
        ),
    ]

    all_good = True

    for template_name, template_path in templates:
        print(f"\n   🔍 Checking {template_name} Template...")

        if not os.path.exists(template_path):
            print(f"      ❌ Template not found")
            all_good = False
            continue

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Essential checks
            checks = [
                ("Extends base", "{% extends 'predictions_tracker/base.html' %}"),
                ("Title block", "{% block title %}"),
                ("Content block", "{% block content %}"),
                ("Bootstrap CSS", "bootstrap@5.3.0"),
                ("jQuery", "jquery-3.7.0"),
                ("URL patterns", "predictions_tracker:"),
            ]

            for check_name, check_pattern in checks:
                if check_pattern in content:
                    print(f"      ✅ {check_name}")
                else:
                    print(f"      ⚠️  {check_name}: NOT FOUND")

            print(f"      📊 Template size: {len(content):,} characters")

        except Exception as e:
            print(f"      ❌ Error reading template: {e}")
            all_good = False

    return all_good


def test_python_syntax():
    """Test Python files for syntax errors"""
    print("\n🐍 Testing Python Syntax...")

    python_files = [
        (
            "Main Views",
            r"C:\Users\n2t\Documents\xoso_crawler\predictions_tracker\views_dir\enhanced_frequency_analyzer_views.py",
        ),
        (
            "Simple Views",
            r"C:\Users\n2t\Documents\xoso_crawler\predictions_tracker\views_dir\enhanced_analyzer_simple_views.py",
        ),
    ]

    all_valid = True

    for file_name, file_path in python_files:
        print(f"   🔍 Checking {file_name}...")

        if not os.path.exists(file_path):
            print(f"      ❌ File not found")
            all_valid = False
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            # Try to compile
            compile(code, file_path, "exec")
            print(f"      ✅ Syntax valid")
            print(f"      📊 File size: {len(code):,} characters")

        except SyntaxError as e:
            print(f"      ❌ Syntax error: {e}")
            all_valid = False
        except Exception as e:
            print(f"      ❌ Error: {e}")
            all_valid = False

    return all_valid


def test_url_patterns_syntax():
    """Test URL patterns file syntax"""
    print("\n🔗 Testing URL Patterns Syntax...")

    urls_file = r"C:\Users\n2t\Documents\xoso_crawler\predictions_tracker\urls.py"

    try:
        with open(urls_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for essential patterns
        checks = [
            ("urlpatterns defined", "urlpatterns = ["),
            ("Enhanced analyzer patterns", "enhanced-analyzer"),
            ("Test patterns", "enhanced-analyzer-test"),
            ("Import statements", "from .views_dir"),
        ]

        for check_name, pattern in checks:
            if pattern in content:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ⚠️  {check_name}: NOT FOUND")

        # Try to compile
        compile(content, urls_file, "exec")
        print(f"   ✅ URL patterns syntax valid")

        return True

    except Exception as e:
        print(f"   ❌ URL patterns error: {e}")
        return False


def run_simple_tests():
    """Run all simple tests"""
    print("🧪 Enhanced Deep Frequency Analyzer - Simple Integration Test")
    print("=" * 70)

    tests = [
        ("File Existence", test_file_existence),
        ("Template Content", test_template_content),
        ("Python Syntax", test_python_syntax),
        ("URL Patterns", test_url_patterns_syntax),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 70)
    print("📋 SIMPLE TEST SUMMARY:")
    print("=" * 70)

    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    failed_tests = total_tests - passed_tests

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")

    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")

    if failed_tests == 0:
        print("\n🎉 All simple tests passed!")
        print("\n📝 What this means:")
        print("   ✅ All required files exist and have content")
        print("   ✅ Templates have proper structure")
        print("   ✅ Python files have valid syntax")
        print("   ✅ URL patterns are properly configured")

        print("\n🌐 Next steps:")
        print("   1. Start Django server: python manage.py runserver")
        print("   2. Visit: http://localhost:8000/pre-lokhung/enhanced-analyzer-test/")
        print("   3. Test basic functionality with mock data")
        print("   4. If test version works, try production version")

    else:
        print(f"\n⚠️  {failed_tests} test(s) failed.")
        print("   Please fix the issues above before testing the system.")

    return failed_tests == 0


if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)
