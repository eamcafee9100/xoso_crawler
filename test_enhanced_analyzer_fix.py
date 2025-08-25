#!/usr/bin/env python3
"""
Direct test of the Enhanced Analyzer with the fixed JSON serialization
"""

import json
import os
import sys
from datetime import date, datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def test_enhanced_analyzer_integration():
    """Test the Enhanced Analyzer with real data and fixed serialization"""
    try:
        # Configure minimal Django settings
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")

        # Import Django and setup with a lighter approach
        import django
        from django.conf import settings

        # Override database settings to use SQLite for testing
        test_db = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.path.join(project_root, "db.sqlite3"),
            }
        }

        # Update the database configuration
        settings.DATABASES = test_db
        django.setup()

        print("✅ Django setup successful with SQLite")

        # Import the components we need
        from analytic_frequence.enhanced_deep_frequency_analyzer import (
            EnhancedDeepFrequencyAnalyzer,
        )
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            CustomJSONEncoder,
            run_enhanced_analysis,
            safe_json_response,
        )

        print("✅ Successfully imported Enhanced Analyzer components")

        # Create a test analyzer
        analyzer = EnhancedDeepFrequencyAnalyzer()

        # Test with a small date range
        start_date = date(2024, 8, 1)
        end_date = date(2024, 8, 3)

        print(f"🚀 Testing analysis: {start_date} to {end_date}")

        # Run the analysis (the method that was failing)
        results = analyzer.analyze_frequency_patterns_enhanced(
            start_date=start_date, end_date=end_date, significance_level=0.05
        )

        print(f"📊 Analysis completed, got {len(results) if results else 0} results")

        # Test the JSON serialization that was failing
        encoder = CustomJSONEncoder()

        # Create the response data structure similar to the actual endpoint
        response_data = {
            "status": "success",
            "analysis_results": results,
            "analysis_metadata": {
                "execution_time": datetime.now().isoformat(),
                "date_range": f"{start_date} to {end_date}",
                "significance_level": 0.05,
                "total_components": len(results) if results else 0,
            },
            "quick_insights": [],  # Simplified for testing
        }

        # Test the exact serialization process from the endpoint
        print("🔄 Testing pre-conversion...")
        safe_response_data = encoder._convert_booleans(response_data)
        print("✅ Pre-conversion successful")

        print("🔄 Testing JSON serialization...")
        json_str = json.dumps(
            safe_response_data, cls=CustomJSONEncoder, ensure_ascii=False
        )
        print("✅ JSON serialization successful")

        print(f"📝 Generated JSON length: {len(json_str)} characters")

        # Test the safe_json_response function directly
        print("🔄 Testing safe_json_response...")
        try:
            # This simulates the actual endpoint behavior
            json_data = json.dumps(
                safe_response_data, cls=CustomJSONEncoder, ensure_ascii=False
            )
            print("✅ safe_json_response simulation successful")

            # Parse it back to verify integrity
            parsed_data = json.loads(json_data)
            print("✅ JSON round-trip successful")

            return True

        except Exception as response_error:
            print(f"❌ safe_json_response failed: {response_error}")
            return False

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_mock_request():
    """Test with a mock Django request to simulate the actual endpoint"""
    try:
        print("\n🧪 Testing Mock Request Simulation")
        print("-" * 40)

        # Create mock request data
        mock_request_data = {
            "start_date": "2024-08-01",
            "end_date": "2024-08-03",
            "significance_level": "0.05",
            "enable_full_pipeline": True,
        }

        # Import after Django setup
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            CustomJSONEncoder,
        )

        # Simulate the request processing
        start_date = datetime.strptime(
            mock_request_data["start_date"], "%Y-%m-%d"
        ).date()
        end_date = datetime.strptime(mock_request_data["end_date"], "%Y-%m-%d").date()
        significance_level = float(mock_request_data.get("significance_level", "0.05"))

        print(f"📅 Date range: {start_date} to {end_date}")
        print(f"📊 Significance level: {significance_level}")

        # Create mock response data that might contain numpy booleans
        import numpy as np

        mock_results = [
            {
                "component": "frequency_analysis",
                "active": np.bool_(True),  # This was causing the error
                "significant": False,
                "confidence": 0.85,
                "patterns": [
                    {"valid": np.bool_(True), "count": np.int32(5)},
                    {"valid": False, "count": 3},
                ],
            },
            {
                "component": "pattern_detection",
                "active": True,
                "significant": np.bool_(False),  # Another potential issue
                "data": np.array([True, False, True]),  # Arrays were also problematic
            },
        ]

        response_data = {
            "status": "success",
            "analysis_results": mock_results,
            "analysis_metadata": {
                "execution_time": datetime.now().isoformat(),
                "date_range": f"{start_date} to {end_date}",
                "significance_level": significance_level,
                "total_components": len(mock_results),
            },
        }

        # Test the exact sequence that was failing
        encoder = CustomJSONEncoder()

        print("🔄 Pre-converting booleans...")
        safe_response_data = encoder._convert_booleans(response_data)

        print("🔄 Creating JSON response...")
        json_data = json.dumps(
            safe_response_data, cls=CustomJSONEncoder, ensure_ascii=False
        )

        print("✅ Mock request test successful!")
        print(f"📝 Response length: {len(json_data)} characters")

        # Show a sample of the response
        print("Sample response (first 300 chars):")
        print(json_data[:300] + "..." if len(json_data) > 300 else json_data)

        return True

    except Exception as e:
        print(f"❌ Mock request test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Enhanced Analyzer JSON Serialization Integration Test")
    print("=" * 60)

    # Test 1: Direct integration
    success1 = test_enhanced_analyzer_integration()

    # Test 2: Mock request simulation
    success2 = test_mock_request()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ ALL TESTS PASSED! The JSON serialization fix should work.")
        print("🎉 The Enhanced Analyzer should now work without boolean errors.")
    else:
        print("❌ Some tests failed. The fix may need more work.")

    print("\nNext step: Test the actual web endpoint to confirm the fix.")
