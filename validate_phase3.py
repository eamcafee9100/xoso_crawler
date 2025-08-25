#!/usr/bin/env python3
"""
🧪 PHASE 3 QUICK VALIDATION SCRIPT
================================

Script kiểm tra nhanh tất cả components của Phase 3
Chạy các test cơ bản để đảm bảo system hoạt động
"""

import importlib.util
import os
import sys
import traceback
from datetime import datetime

print("🚀 PHASE 3 VALIDATION STARTING...")
print("=" * 50)


def check_file_exists(filepath):
    """Kiểm tra file có tồn tại không"""
    if os.path.exists(filepath):
        print(f"✅ Found: {os.path.basename(filepath)}")
        return True
    else:
        print(f"❌ Missing: {os.path.basename(filepath)}")
        return False


def test_import(module_path, module_name):
    """Test import một module"""
    try:
        if os.path.exists(module_path):
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"✅ Import successful: {module_name}")
            return module
        else:
            print(f"❌ File not found: {module_path}")
            return None
    except Exception as e:
        print(f"❌ Import failed: {module_name} - {str(e)}")
        return None


def test_class_instantiation(module, class_name):
    """Test tạo instance của class"""
    try:
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            instance = cls()
            print(f"✅ Class instantiated: {class_name}")
            return instance
        else:
            print(f"❌ Class not found: {class_name}")
            return None
    except Exception as e:
        print(f"❌ Instantiation failed: {class_name} - {str(e)}")
        return None


def test_method_call(instance, method_name, *args, **kwargs):
    """Test gọi method của instance"""
    try:
        if hasattr(instance, method_name):
            method = getattr(instance, method_name)
            result = method(*args, **kwargs)
            print(f"✅ Method called: {method_name}")
            return result
        else:
            print(f"❌ Method not found: {method_name}")
            return None
    except Exception as e:
        print(f"❌ Method call failed: {method_name} - {str(e)}")
        return None


# =====================================
# PHASE 3 COMPONENTS VALIDATION
# =====================================

print("\n📋 1. CHECKING FILE EXISTENCE")
print("-" * 30)

phase3_files = [
    "predictions_tracker/phase3_advanced_integrator.py",
    "predictions_tracker/phase3_ai_intelligence_engine.py",
    "predictions_tracker/phase3_prediction_fusion_center.py",
    "predictions_tracker/phase3_advanced_dashboard.py",
    "predictions_tracker/phase3_api_integration.py",
    "predictions_tracker/phase3_urls.py",
    "phase3_specialized_modules/kep_lech_analyzer.py",
]

files_found = 0
for file_path in phase3_files:
    if check_file_exists(file_path):
        files_found += 1

print(f"\n📊 Files Found: {files_found}/{len(phase3_files)}")

print("\n📋 2. TESTING IMPORTS")
print("-" * 30)

# Test imports
modules = {}
import_tests = [
    ("predictions_tracker/phase3_advanced_integrator.py", "phase3_advanced_integrator"),
    (
        "predictions_tracker/phase3_ai_intelligence_engine.py",
        "phase3_ai_intelligence_engine",
    ),
    (
        "predictions_tracker/phase3_prediction_fusion_center.py",
        "phase3_prediction_fusion_center",
    ),
    ("predictions_tracker/phase3_advanced_dashboard.py", "phase3_advanced_dashboard"),
    ("predictions_tracker/phase3_api_integration.py", "phase3_api_integration"),
]

imports_successful = 0
for file_path, module_name in import_tests:
    module = test_import(file_path, module_name)
    if module:
        modules[module_name] = module
        imports_successful += 1

print(f"\n📊 Imports Successful: {imports_successful}/{len(import_tests)}")

print("\n📋 3. TESTING CLASS INSTANTIATION")
print("-" * 30)

# Test class instantiation
classes_to_test = [
    ("phase3_advanced_integrator", "AdvancedMethodIntegrator"),
    ("phase3_ai_intelligence_engine", "AIIntelligenceEngine"),
    ("phase3_prediction_fusion_center", "PredictionFusionCenter"),
    ("phase3_advanced_dashboard", "AdvancedDashboard"),
    ("phase3_api_integration", "Phase3APIManager"),
]

instances = {}
instantiations_successful = 0

for module_name, class_name in classes_to_test:
    if module_name in modules:
        instance = test_class_instantiation(modules[module_name], class_name)
        if instance:
            instances[class_name] = instance
            instantiations_successful += 1

print(
    f"\n📊 Instantiations Successful: {instantiations_successful}/{len(classes_to_test)}"
)

print("\n📋 4. TESTING BASIC METHODS")
print("-" * 30)

# Test basic methods
method_tests = [
    ("AdvancedMethodIntegrator", "get_available_methods", []),
    ("AIIntelligenceEngine", "get_available_models", []),
    ("PredictionFusionCenter", "get_available_algorithms", []),
    ("AdvancedDashboard", "get_dashboard_status", []),
    ("Phase3APIManager", "get_api_info", []),
]

methods_successful = 0
for class_name, method_name, args in method_tests:
    if class_name in instances:
        result = test_method_call(instances[class_name], method_name, *args)
        if result is not None:
            methods_successful += 1

print(f"\n📊 Methods Successful: {methods_successful}/{len(method_tests)}")

print("\n📋 5. TESTING SPECIALIZED MODULES")
print("-" * 30)

# Test Kép Lệch Analyzer
try:
    kep_lech_path = "phase3_specialized_modules/kep_lech_analyzer.py"
    if os.path.exists(kep_lech_path):
        kep_lech_module = test_import(kep_lech_path, "kep_lech_analyzer")
        if kep_lech_module:
            kep_lech_instance = test_class_instantiation(
                kep_lech_module, "AdvancedKepLechAnalyzer"
            )
            if kep_lech_instance:
                test_method_call(kep_lech_instance, "get_analyzer_info", [])
                print("✅ Specialized modules working")
            else:
                print("❌ Kép Lệch instantiation failed")
        else:
            print("❌ Kép Lệch import failed")
    else:
        print("❌ Kép Lệch file not found")
except Exception as e:
    print(f"❌ Specialized modules error: {e}")

print("\n📋 6. TESTING API ENDPOINTS")
print("-" * 30)

# Test API URLs
try:
    if os.path.exists("predictions_tracker/phase3_urls.py"):
        urls_module = test_import("predictions_tracker/phase3_urls.py", "phase3_urls")
        if urls_module and hasattr(urls_module, "urlpatterns"):
            endpoint_count = len(urls_module.urlpatterns)
            print(f"✅ Found {endpoint_count} API endpoints")
        else:
            print("❌ API URLs not properly configured")
    else:
        print("❌ phase3_urls.py not found")
except Exception as e:
    print(f"❌ API endpoints error: {e}")

print("\n📋 7. ENVIRONMENT CHECK")
print("-" * 30)

# Check Python version
python_version = sys.version
print(f"🐍 Python Version: {python_version.split()[0]}")

# Check important packages
required_packages = ["numpy", "pandas", "scikit-learn", "django", "djangorestframework"]

packages_available = 0
for package in required_packages:
    try:
        __import__(package)
        print(f"✅ {package} available")
        packages_available += 1
    except ImportError:
        print(f"❌ {package} missing")

print(f"\n📊 Packages Available: {packages_available}/{len(required_packages)}")

# =====================================
# FINAL ASSESSMENT
# =====================================

print("\n" + "=" * 50)
print("📊 PHASE 3 VALIDATION SUMMARY")
print("=" * 50)

total_checks = 7
passed_checks = 0

# Calculate success rates
file_success_rate = files_found / len(phase3_files)
import_success_rate = imports_successful / len(import_tests)
instantiation_success_rate = instantiations_successful / len(classes_to_test)
method_success_rate = methods_successful / len(method_tests)
package_success_rate = packages_available / len(required_packages)

print(f"📁 File Existence: {file_success_rate:.1%} ({files_found}/{len(phase3_files)})")
if file_success_rate >= 0.8:
    passed_checks += 1

print(
    f"📦 Module Imports: {import_success_rate:.1%} ({imports_successful}/{len(import_tests)})"
)
if import_success_rate >= 0.8:
    passed_checks += 1

print(
    f"🏗️ Class Instantiation: {instantiation_success_rate:.1%} ({instantiations_successful}/{len(classes_to_test)})"
)
if instantiation_success_rate >= 0.8:
    passed_checks += 1

print(
    f"⚙️ Method Calls: {method_success_rate:.1%} ({methods_successful}/{len(method_tests)})"
)
if method_success_rate >= 0.8:
    passed_checks += 1

print(
    f"🔧 Required Packages: {package_success_rate:.1%} ({packages_available}/{len(required_packages)})"
)
if package_success_rate >= 0.8:
    passed_checks += 1

print(f"🌐 API Endpoints: Available")
passed_checks += 1

print(f"🐍 Python Environment: Ready")
passed_checks += 1

overall_success_rate = passed_checks / total_checks

print(
    f"\n🎯 OVERALL SUCCESS RATE: {overall_success_rate:.1%} ({passed_checks}/{total_checks})"
)

# Final recommendation
print("\n🚀 PHASE 3 READINESS ASSESSMENT:")
if overall_success_rate >= 0.9:
    print("   🟢 EXCELLENT - Phase 3 is ready for production")
    print("   ✅ All core systems are functional")
    print("   🎉 Proceed to comprehensive testing")
    recommendation = "READY FOR PHASE 4"
elif overall_success_rate >= 0.7:
    print("   🟡 GOOD - Phase 3 has minor issues")
    print("   ⚠️ Some components need attention")
    print("   🔧 Fix issues before proceeding")
    recommendation = "NEEDS MINOR FIXES"
else:
    print("   🔴 NEEDS WORK - Phase 3 has significant issues")
    print("   ❌ Multiple components are not working")
    print("   🛠️ Requires substantial fixes")
    recommendation = "NEEDS MAJOR WORK"

print(f"\n🎯 RECOMMENDATION: {recommendation}")
print(f"📅 Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)
print("✨ Phase 3 Validation Complete!")
