#!/usr/bin/env python3
"""
Debug script to reproduce the exact JSON serialization error from Enhanced Analyzer
"""

import json
import logging
import os
import sys
from datetime import date, datetime

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_json_serialization():
    """Test the exact JSON serialization that's failing"""
    try:
        # Import the actual analyzer
        from analytic_frequence.enhanced_deep_frequency_analyzer import (
            EnhancedDeepFrequencyAnalyzer,
        )
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            CustomJSONEncoder,
            safe_json_response,
        )

        print("✅ Successfully imported analyzer and encoder")

        # Create analyzer and run a test analysis
        analyzer = EnhancedDeepFrequencyAnalyzer()

        # Run a small test analysis
        start_date = date(2024, 8, 1)
        end_date = date(2024, 8, 2)

        print(f"🚀 Running test analysis: {start_date} to {end_date}")

        # Test the analyze_frequency_patterns_enhanced method first
        results = analyzer.analyze_frequency_patterns_enhanced(
            start_date=start_date, end_date=end_date, significance_level=0.05
        )

        print(f"📊 Analysis completed, got {len(results) if results else 0} results")

        # Test JSON serialization of the results
        encoder = CustomJSONEncoder()

        # First check for any boolean values in the results
        def find_booleans(obj, path=""):
            """Recursively find all boolean values in the data structure"""
            booleans_found = []

            if isinstance(obj, bool):
                booleans_found.append((path, obj))
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    booleans_found.extend(find_booleans(value, new_path))
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    new_path = f"{path}[{i}]" if path else f"[{i}]"
                    booleans_found.extend(find_booleans(value, new_path))
            elif isinstance(obj, tuple):
                for i, value in enumerate(obj):
                    new_path = f"{path}({i})" if path else f"({i})"
                    booleans_found.extend(find_booleans(value, new_path))

            return booleans_found

        # Find all boolean values
        booleans = find_booleans(results, "results")
        if booleans:
            print(f"🔍 Found {len(booleans)} boolean values:")
            for path, value in booleans[:10]:  # Show first 10
                print(f"  - {path}: {value} ({type(value)})")
        else:
            print("✅ No boolean values found in results")

        # Test the CustomJSONEncoder directly
        try:
            json_str = json.dumps(results, cls=CustomJSONEncoder, ensure_ascii=False)
            print("✅ CustomJSONEncoder worked successfully")
        except Exception as e:
            print(f"❌ CustomJSONEncoder failed: {e}")

            # Try the conversion method
            try:
                safe_results = encoder._convert_booleans(results)
                json_str = json.dumps(safe_results, ensure_ascii=False)
                print("✅ Manual conversion + json.dumps worked")
            except Exception as e2:
                print(f"❌ Manual conversion also failed: {e2}")
                return False

        # Test the full response data structure
        response_data = {
            "status": "success",
            "analysis_results": results,
            "analysis_metadata": {
                "execution_time": datetime.now().isoformat(),
                "date_range": f"{start_date} to {end_date}",
                "significance_level": 0.05,
                "total_components": len(results) if results else 0,
            },
        }

        # Find booleans in full response
        response_booleans = find_booleans(response_data, "response_data")
        if response_booleans:
            print(f"🔍 Found {len(response_booleans)} boolean values in response_data:")
            for path, value in response_booleans[:10]:
                print(f"  - {path}: {value} ({type(value)})")

        # Test the safe_json_response function
        try:
            # Pre-convert booleans
            safe_response_data = encoder._convert_booleans(response_data)

            # Test direct JSON serialization
            json_str = json.dumps(
                safe_response_data, cls=CustomJSONEncoder, ensure_ascii=False
            )
            print("✅ Full response data serialization successful")

            return True

        except Exception as e:
            print(f"❌ Full response serialization failed: {e}")
            print(f"Error type: {type(e)}")

            # Show the problematic part
            try:
                # Try to isolate the problem
                for key, value in response_data.items():
                    try:
                        json.dumps(
                            {key: value}, cls=CustomJSONEncoder, ensure_ascii=False
                        )
                        print(f"✅ {key}: OK")
                    except Exception as key_error:
                        print(f"❌ {key}: {key_error}")

                        # Dive deeper into this key
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                try:
                                    json.dumps(
                                        {subkey: subvalue},
                                        cls=CustomJSONEncoder,
                                        ensure_ascii=False,
                                    )
                                    print(f"  ✅ {key}.{subkey}: OK")
                                except Exception as subkey_error:
                                    print(f"  ❌ {key}.{subkey}: {subkey_error}")
                                    print(f"    Type: {type(subvalue)}")
                                    print(f"    Value sample: {str(subvalue)[:100]}...")
            except Exception as debug_error:
                print(f"Debug error: {debug_error}")

            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Testing Enhanced Analyzer JSON Serialization")
    print("=" * 50)

    success = test_json_serialization()

    print("=" * 50)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed - JSON serialization issue found")
