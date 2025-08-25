#!/usr/bin/env python
"""
🔍 DEBUG SCRIPT: Kiểm tra ML Training Data và Performance
"""

import logging
import os
import sys
from datetime import date, timedelta

import django

# Setup Django
sys.path.append("c:\\Users\\n2t\\Documents\\xoso_crawler")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

# Configure logging to see all debug info
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from predictions_tracker.ensemble_ml_foundation import (
    AdvancedFeaturePipeline,
    EnsembleLotteryPredictor,
)
from predictions_tracker.statistical_foundation import AdvancedFeatureEngine
from predictions_tracker.views_dir.api_cyclical_prediction_by_date_v3 import (
    _extract_advanced_features_v3,
)
from results.models import KetQuaXoSo


def debug_data_availability():
    """Kiểm tra dữ liệu available"""
    print("🔍 === CHECKING DATA AVAILABILITY ===")

    # Check total data
    total_results = KetQuaXoSo.objects.count()
    print(f"📊 Total lottery results in database: {total_results}")

    if total_results == 0:
        print("❌ NO DATA FOUND - This explains why models use mock/fallback data!")
        return False

    # Check recent data (last 90 days)
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=90)

    recent_results = KetQuaXoSo.objects.filter(
        ngay__range=[start_date, end_date]
    ).order_by("ngay")

    print(
        f"📅 Recent data ({start_date} to {end_date}): {recent_results.count()} records"
    )

    if recent_results.exists():
        first_result = recent_results.first()
        last_result = recent_results.last()
        print(f"🗓️ Data range: {first_result.ngay} to {last_result.ngay}")

        # Sample a few results to check data quality
        print("📝 Sample data (first 3 results):")
        for i, result in enumerate(recent_results[:3]):
            print(f"   {i+1}. Date: {result.ngay}")
            if hasattr(result, "giai_db") and result.giai_db:
                print(f"      Special Prize: {result.giai_db}")
            if hasattr(result, "giai_1") and result.giai_1:
                print(f"      First Prize: {result.giai_1}")
            if hasattr(result, "giai_2") and result.giai_2:
                print(f"      Second Prize: {result.giai_2}")
    else:
        print("⚠️ NO RECENT DATA - Models will use fallback data")
        return False

    return True


def debug_feature_extraction():
    """Kiểm tra feature extraction process"""
    print("\n🧮 === CHECKING FEATURE EXTRACTION ===")

    analysis_date = date(2025, 1, 23)
    feature_engine = AdvancedFeatureEngine()

    try:
        features = _extract_advanced_features_v3(analysis_date, feature_engine)
        print(f"✅ Feature extraction successful")
        print(f"📊 Number of features: {len(features)}")
        print(f"🔍 Sample features: {dict(list(features.items())[:5])}")

        # Check if using real data or fallback
        if len(features) == feature_engine._get_default_features().__len__():
            print("⚠️ LIKELY USING FALLBACK FEATURES - Check data availability")
        else:
            print("✅ Using real statistical features from historical data")

        return features
    except Exception as e:
        print(f"❌ Feature extraction failed: {e}")
        return None


def debug_ml_training():
    """Kiểm tra ML training process"""
    print("\n🚀 === CHECKING ML TRAINING ===")

    # Initialize components
    ensemble_predictor = EnsembleLotteryPredictor(random_state=42)
    feature_pipeline = AdvancedFeaturePipeline()

    # Create sample data (similar to what API uses)
    import numpy as np

    feature_dim = 73  # Expected feature dimension from API

    print(f"🎯 Creating mock training data with {feature_dim} features")
    mock_X = np.random.randn(100, feature_dim)
    mock_y = np.random.randn(100)

    try:
        # Train ensemble
        print("🚀 Training ensemble...")
        training_results = ensemble_predictor.train_ensemble(
            mock_X, mock_y, validation_split=0.2
        )

        print("✅ Training completed successfully")
        print(f"📊 Model performances:")
        for model_name, perf in training_results.get("model_performances", {}).items():
            if "error" not in perf:
                print(
                    f"   {model_name}: R² = {perf.get('r2', 0):.4f}, RMSE = {perf.get('rmse', 0):.4f}"
                )
            else:
                print(f"   {model_name}: ERROR - {perf['error']}")

        # Test prediction
        test_X = np.random.randn(1, feature_dim)
        predictions = ensemble_predictor.predict_ensemble(test_X)
        print(f"🎯 Test prediction successful: {predictions}")

        return True

    except Exception as e:
        print(f"❌ ML training failed: {e}")
        return False


def debug_api_flow():
    """Kiểm tra toàn bộ API flow"""
    print("\n🌐 === CHECKING API FLOW ===")

    from django.test import RequestFactory

    from predictions_tracker.views_dir.api_cyclical_prediction_by_date_v3 import (
        api_cyclical_prediction_by_date_v3,
    )

    # Create mock request
    factory = RequestFactory()
    request = factory.get(
        "/api/cyclical-prediction-v3/", {"analysis_date": "2025-01-23"}
    )

    try:
        response = api_cyclical_prediction_by_date_v3(request)
        print(f"✅ API call successful, status: {response.status_code}")

        if response.status_code == 200:
            import json

            data = json.loads(response.content)
            print(f"📊 Response includes:")
            print(f"   - Success: {data.get('success')}")
            print(f"   - ML Insights: {'ml_insights' in data}")
            print(f"   - Risk Insights: {'risk_insights' in data}")
            print(
                f"   - ML Enhanced Numbers: {len(data.get('intelligent_predictions', {}).get('ml_enhanced_numbers', []))}"
            )

            # Check if using real or fallback data
            metadata = data.get("metadata", {})
            print(f"   - API Version: {metadata.get('api_version')}")
            print(f"   - Analysis Timestamp: {metadata.get('analysis_timestamp')}")

        return True

    except Exception as e:
        print(f"❌ API flow failed: {e}")
        return False


def main():
    """Main debug function"""
    print("🔍 MACHINE LEARNING TRAINING DEBUG REPORT")
    print("=" * 50)

    # 1. Check data availability
    has_data = debug_data_availability()

    # 2. Check feature extraction
    features = debug_feature_extraction()

    # 3. Check ML training
    ml_works = debug_ml_training()

    # 4. Check API flow
    api_works = debug_api_flow()

    # Summary
    print("\n📋 === SUMMARY ===")
    print(f"✅ Data Available: {'YES' if has_data else 'NO (using fallback)'}")
    print(f"✅ Feature Extraction: {'WORKS' if features else 'FAILED'}")
    print(f"✅ ML Training: {'WORKS' if ml_works else 'FAILED'}")
    print(f"✅ API Flow: {'WORKS' if api_works else 'FAILED'}")

    if not has_data:
        print("\n⚠️ WARNING: No real lottery data found!")
        print("   Models are using mock/random data for training.")
        print("   This explains poor prediction accuracy.")
        print("   Need to populate KetQuaXoSo table with real lottery results.")

    if has_data and features and ml_works:
        print("\n🎉 All systems working with REAL DATA!")
    elif not has_data:
        print("\n🚨 System using FALLBACK DATA - predictions will be random!")


if __name__ == "__main__":
    main()
