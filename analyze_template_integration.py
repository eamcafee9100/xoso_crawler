"""
Comprehensive Template Analysis - Cyclical Intelligence Integration
"""

import json
import os
import re
import sys
from datetime import date, datetime

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()


def analyze_template_integration():
    """Phân tích tích hợp template với Cyclical Intelligence API"""

    print(f"🔍 COMPREHENSIVE TEMPLATE ANALYSIS - CYCLICAL INTELLIGENCE INTEGRATION")
    print("=" * 80)

    # 1. Kiểm tra API Cyclical response structure
    print(f"\n1️⃣ API CYCLICAL RESPONSE STRUCTURE ANALYSIS")
    print("-" * 50)

    from django.test import RequestFactory

    from predictions_tracker.views_dir.api_cyclical_prediction_by_date_v3 import (
        api_cyclical_prediction_by_date_v3,
    )

    factory = RequestFactory()
    analysis_date = date.today().strftime("%Y-%m-%d")

    request = factory.get(
        "/api/cyclical-prediction/",
        {"analysis_date": analysis_date, "limit": "15", "threshold": "60"},
    )

    response = api_cyclical_prediction_by_date_v3(request)
    api_data = json.loads(response.content.decode("utf-8"))

    print(f"✅ API Response Keys: {list(api_data.keys())}")

    if api_data.get("success"):
        # Phân tích cyclical_analysis
        cyclical_analysis = api_data.get("cyclical_analysis", {})
        print(f"📊 Cyclical Analysis Keys: {list(cyclical_analysis.keys())}")

        context_analysis = cyclical_analysis.get("context_analysis", {})
        print(f"🧠 Context Analysis: {list(context_analysis.keys())}")

        method_sync_matrix = cyclical_analysis.get("method_sync_matrix", {})
        print(f"🔗 Method Sync Matrix: {list(method_sync_matrix.keys())}")

        number_frequency_cycles = cyclical_analysis.get("number_frequency_cycles", {})
        print(f"🔢 Number Frequency Cycles: {list(number_frequency_cycles.keys())}")

        # Phân tích optimal_methods
        optimal_methods = api_data.get("optimal_methods", {})
        print(f"🎯 Optimal Methods: {list(optimal_methods.keys())}")

        cyclical_filtered = optimal_methods.get("cyclical_filtered", [])
        print(f"   - Cyclical Filtered: {len(cyclical_filtered)} methods")

        # Phân tích intelligent_predictions
        intelligent_predictions = api_data.get("intelligent_predictions", {})
        print(f"🤖 Intelligent Predictions: {list(intelligent_predictions.keys())}")

        # Phân tích performance_metrics
        performance_metrics = api_data.get("performance_metrics", {})
        print(f"📈 Performance Metrics: {list(performance_metrics.keys())}")
        print(
            f"   - Expected Accuracy: {performance_metrics.get('expected_accuracy')}%"
        )
        print(f"   - Confidence Level: {performance_metrics.get('confidence_level')}")
        print(f"   - Cyclical Strength: {performance_metrics.get('cyclical_strength')}")

    # 2. Phân tích template file
    print(f"\n2️⃣ TEMPLATE FILE ANALYSIS")
    print("-" * 50)

    template_path = "c:\\Users\\n2t\\Documents\\xoso_crawler\\predictions_tracker\\templates\\predictions_tracker\\monthly_report.html"

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        print(f"✅ Template file loaded: {len(template_content)} characters")

        # Tìm các API calls trong template
        api_calls = re.findall(
            r'fetch\([\'"]([^\'\"]*api[^\'"]*)[\'"]', template_content
        )
        print(f"🔍 API Calls found: {len(api_calls)}")
        for call in api_calls:
            print(f"   - {call}")

        # Tìm cyclical-related code
        cyclical_mentions = re.findall(
            r"cyclical[a-zA-Z_]*", template_content, re.IGNORECASE
        )
        print(f"🔄 Cyclical mentions: {len(set(cyclical_mentions))}")
        for mention in set(cyclical_mentions):
            print(f"   - {mention}")

        # Tìm prediction-related functions
        prediction_functions = re.findall(
            r"function\s+([a-zA-Z_]*[pP]rediction[a-zA-Z_]*)", template_content
        )
        print(f"🎯 Prediction functions: {len(prediction_functions)}")
        for func in prediction_functions:
            print(f"   - {func}")

    except Exception as e:
        print(f"❌ Template analysis failed: {e}")

    # 3. Kiểm tra integration gaps
    print(f"\n3️⃣ INTEGRATION GAPS ANALYSIS")
    print("-" * 50)

    # Các features từ API cần được sử dụng trong template
    required_features = {
        "cyclical_context": [
            "day_of_month_phase",
            "week_phase",
            "month_trend",
            "cycle_strength",
        ],
        "method_sync_matrix": ["cyclical_fitness", "phase_alignment", "fatigue_risk"],
        "intelligent_predictions": [
            "cyclical_numbers",
            "method_numbers",
            "fusion_numbers",
        ],
        "performance_metrics": [
            "expected_accuracy",
            "confidence_level",
            "cyclical_strength",
        ],
    }

    gaps_found = []

    for category, features in required_features.items():
        print(f"\n📋 Checking {category}:")
        for feature in features:
            if feature.lower() in template_content.lower():
                print(f"   ✅ {feature}: Found in template")
            else:
                print(f"   ❌ {feature}: Missing from template")
                gaps_found.append(f"{category}.{feature}")

    # 4. Recommendations
    print(f"\n4️⃣ INTEGRATION RECOMMENDATIONS")
    print("-" * 50)

    if gaps_found:
        print(f"❌ Found {len(gaps_found)} integration gaps:")
        for gap in gaps_found:
            print(f"   - Missing: {gap}")
    else:
        print(f"✅ All cyclical intelligence features are integrated!")

    return {
        "api_data": api_data,
        "template_analyzed": True,
        "gaps_found": gaps_found,
        "integration_score": max(0, 100 - len(gaps_found) * 10),
    }


def analyze_template_ui_enhancements():
    """Phân tích UI enhancements cần thiết cho Cyclical Intelligence"""

    print(f"\n5️⃣ UI ENHANCEMENTS ANALYSIS")
    print("-" * 50)

    # Đề xuất UI improvements
    ui_enhancements = {
        "Cyclical Context Display": {
            "description": "Hiển thị day/week/month phases",
            "priority": "High",
            "implementation": "Add context cards showing current phases",
        },
        "Method Sync Matrix": {
            "description": "Visualize method-cycle synchronization",
            "priority": "High",
            "implementation": "Add sync matrix heatmap",
        },
        "Cyclical Strength Indicator": {
            "description": "Show cycle strength visually",
            "priority": "Medium",
            "implementation": "Add progress bar or gauge",
        },
        "Intelligent Predictions Tabs": {
            "description": "Separate tabs for cyclical/method/fusion predictions",
            "priority": "High",
            "implementation": "Add tabbed interface",
        },
        "Performance Confidence": {
            "description": "Show confidence level with visual indicators",
            "priority": "Medium",
            "implementation": "Add confidence badges",
        },
        "Fatigue Risk Alerts": {
            "description": "Highlight methods with high fatigue risk",
            "priority": "High",
            "implementation": "Add warning indicators",
        },
    }

    for enhancement, details in ui_enhancements.items():
        print(f"🎨 {enhancement}:")
        print(f"   - Description: {details['description']}")
        print(f"   - Priority: {details['priority']}")
        print(f"   - Implementation: {details['implementation']}")
        print()


def check_template_performance():
    """Kiểm tra performance của template với Cyclical Intelligence"""

    print(f"\n6️⃣ TEMPLATE PERFORMANCE ANALYSIS")
    print("-" * 50)

    import time

    # Test API response time
    start_time = time.time()

    from django.test import RequestFactory

    from predictions_tracker.views_dir.api_cyclical_prediction_by_date_v3 import (
        api_cyclical_prediction_by_date_v3,
    )

    factory = RequestFactory()
    request = factory.get(
        "/api/cyclical-prediction/",
        {"analysis_date": date.today().strftime("%Y-%m-%d")},
    )

    response = api_cyclical_prediction_by_date_v3(request)
    api_time = time.time() - start_time

    print(f"⏱️ API Response Time: {api_time:.3f}s")

    # Analyze response size
    response_size = len(response.content)
    print(f"📦 Response Size: {response_size:,} bytes")

    # Parse response
    api_data = json.loads(response.content.decode("utf-8"))

    if api_data.get("success"):
        # Count data points
        optimal_methods = api_data.get("optimal_methods", {})
        cyclical_filtered = optimal_methods.get("cyclical_filtered", [])

        intelligent_predictions = api_data.get("intelligent_predictions", {})
        fusion_numbers = intelligent_predictions.get("fusion_numbers", [])

        print(f"📊 Data Points:")
        print(f"   - Filtered Methods: {len(cyclical_filtered)}")
        print(f"   - Fusion Numbers: {len(fusion_numbers)}")

        # Performance assessment
        if api_time < 2.0:
            performance_rating = "Excellent"
        elif api_time < 5.0:
            performance_rating = "Good"
        else:
            performance_rating = "Needs Optimization"

        print(f"🎯 Performance Rating: {performance_rating}")

    return {
        "api_time": api_time,
        "response_size": response_size,
        "performance_rating": performance_rating,
    }


if __name__ == "__main__":
    analysis_result = analyze_template_integration()
    analyze_template_ui_enhancements()
    performance_result = check_template_performance()

    print(f"\n" + "=" * 80)
    print(f"🏆 FINAL ASSESSMENT")
    print("-" * 50)

    integration_score = analysis_result.get("integration_score", 0)
    gaps_count = len(analysis_result.get("gaps_found", []))

    if integration_score >= 90:
        assessment = "EXCELLENT - Template fully utilizes Cyclical Intelligence"
        confidence = 95
    elif integration_score >= 70:
        assessment = "GOOD - Most features integrated, minor gaps"
        confidence = 80
    elif integration_score >= 50:
        assessment = "FAIR - Basic integration, needs improvements"
        confidence = 65
    else:
        assessment = "POOR - Major integration gaps identified"
        confidence = 40

    print(f"📊 Integration Score: {integration_score}/100")
    print(f"🎯 Assessment: {assessment}")
    print(f"🔍 Confidence Level: {confidence}%")
    print(f"⚠️ Gaps Found: {gaps_count}")

    if confidence >= 90:
        print(
            f"\n✅ READY FOR PRODUCTION - Template maximizes Cyclical Intelligence capabilities!"
        )
    else:
        print(
            f"\n⚠️ IMPROVEMENTS NEEDED - Template requires enhancements to fully utilize API power"
        )
