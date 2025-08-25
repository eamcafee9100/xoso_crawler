#!/usr/bin/env python
"""
🔧 DETAILED DEBUG: StandardScaler Feature Mismatch Analysis
"""

import logging
import os
import sys
from datetime import date, timedelta

import django
import numpy as np

# Setup Django
sys.path.append("c:\\Users\\n2t\\Documents\\xoso_crawler")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from predictions_tracker.ensemble_ml_foundation import EnsembleLotteryPredictor


def debug_standardscaler_issue():
    """Phân tích chi tiết StandardScaler feature mismatch"""
    print("🔧 === STANDARDSCALER FEATURE MISMATCH ANALYSIS ===")

    # Initialize predictor
    ensemble_predictor = EnsembleLotteryPredictor(random_state=42)

    print("📊 Phase 1: Training with different feature dimensions")

    # Test với feature dimensions khác nhau
    feature_dims = [4, 65, 73]

    for dim in feature_dims:
        print(f"\n🎯 Testing with {dim} features:")

        # Create training data
        X_train = np.random.randn(100, dim)
        y_train = np.random.randn(100)

        try:
            # Train models
            results = ensemble_predictor.train_ensemble(
                X_train, y_train, validation_split=0.2
            )
            print(f"   ✅ Training successful with {dim} features")

            # Check StandardScaler state
            if (
                hasattr(ensemble_predictor, "meta_scaler")
                and ensemble_predictor.meta_scaler is not None
            ):
                expected_features = ensemble_predictor.meta_scaler.n_features_in_
                print(f"   📏 StandardScaler expects: {expected_features} features")

            # Test prediction with same dimension
            X_test = np.random.randn(1, dim)
            try:
                pred = ensemble_predictor.predict_ensemble(X_test)
                print(f"   ✅ Prediction successful: {pred[0]:.4f}")
            except Exception as pred_e:
                print(f"   ❌ Prediction failed: {pred_e}")

        except Exception as e:
            print(f"   ❌ Training failed with {dim} features: {e}")

    print("\n📊 Phase 2: Meta-learner Feature Analysis")

    # Phân tích meta-learner features
    print("🧠 Meta-learner should use predictions from 4 base models as features")
    print(
        "   Expected meta-learner input: [rf_pred, xgb_pred, gb_pred, nn_pred] = 4 features"
    )
    print("   But getting 73 features from statistical pipeline instead!")

    # Test correct meta-learner flow
    print("\n🔄 Testing correct meta-learner flow:")

    # Train with statistical features (73 dims)
    X_statistical = np.random.randn(100, 73)
    y_target = np.random.randn(100)

    try:
        ensemble_predictor.train_ensemble(X_statistical, y_target, validation_split=0.2)
        print("✅ Base models trained with 73 statistical features")

        # Meta-learner should be trained with 4 base model predictions
        base_predictions = np.random.randn(100, 4)  # 4 base model predictions

        # Check if meta_scaler was trained correctly
        if (
            hasattr(ensemble_predictor, "meta_scaler")
            and ensemble_predictor.meta_scaler is not None
        ):
            try:
                # This should work - 4 features for meta-learner
                scaled_meta = ensemble_predictor.meta_scaler.transform(base_predictions)
                print("✅ Meta-learner scaler works with 4 features")
            except Exception as meta_e:
                print(f"❌ Meta-learner scaler issue: {meta_e}")

        # The bug: trying to use 73 statistical features for meta-learner
        statistical_features = np.random.randn(1, 73)
        try:
            if (
                hasattr(ensemble_predictor, "meta_scaler")
                and ensemble_predictor.meta_scaler is not None
            ):
                scaled_wrong = ensemble_predictor.meta_scaler.transform(
                    statistical_features
                )
                print("🚨 This shouldn't work but did...")
        except Exception as bug_e:
            print(f"🎯 FOUND THE BUG: {bug_e}")
            print(
                "   Meta-learner scaler was trained with 4 features (base model predictions)"
            )
            print(
                "   But predict_ensemble is trying to pass 73 statistical features to it"
            )

    except Exception as e:
        print(f"❌ Analysis failed: {e}")


def debug_prediction_flow():
    """Phân tích prediction flow để hiểu bug"""
    print("\n🔍 === PREDICTION FLOW ANALYSIS ===")

    print("📋 Current (buggy) flow:")
    print("1. Statistical features extracted: 73 features")
    print("2. Base models predict using 73 features ✅")
    print("3. Meta-learner tries to use 73 features ❌ (expects 4)")
    print("")
    print("📋 Correct flow should be:")
    print("1. Statistical features extracted: 73 features")
    print("2. Base models predict using 73 features ✅")
    print("3. Collect 4 base model predictions")
    print("4. Meta-learner uses 4 base predictions ✅")

    # Demonstrate correct flow
    print("\n🚀 Demonstrating correct flow:")

    ensemble_predictor = EnsembleLotteryPredictor(random_state=42)

    # Train with statistical features
    X_train = np.random.randn(100, 73)
    y_train = np.random.randn(100)

    ensemble_predictor.train_ensemble(X_train, y_train, validation_split=0.2)

    # Test prediction - should collect base model predictions first
    X_test = np.random.randn(1, 73)

    # Simulate what should happen
    base_predictions = []

    # Get predictions from base models
    for model_name, model in [
        ("random_forest", ensemble_predictor.random_forest),
        ("xgboost", ensemble_predictor.xgboost),
        ("gradient_boost", ensemble_predictor.gradient_boost),
        ("neural_network", ensemble_predictor.neural_network),
    ]:
        if model is not None:
            try:
                pred = model.predict(X_test)[0]
                base_predictions.append(pred)
                print(f"   {model_name}: {pred:.4f}")
            except:
                base_predictions.append(0.0)
                print(f"   {model_name}: 0.0000 (fallback)")

    # Now meta-learner should use these 4 predictions
    meta_input = np.array([base_predictions])
    print(f"\n🧠 Meta-learner input shape: {meta_input.shape} (should be (1, 4))")

    if (
        hasattr(ensemble_predictor, "meta_learner")
        and ensemble_predictor.meta_learner is not None
    ):
        try:
            if (
                hasattr(ensemble_predictor, "meta_scaler")
                and ensemble_predictor.meta_scaler is not None
            ):
                scaled_meta = ensemble_predictor.meta_scaler.transform(meta_input)
                meta_pred = ensemble_predictor.meta_learner.predict(scaled_meta)[0]
                print(f"✅ Meta-learner prediction: {meta_pred:.4f}")
        except Exception as e:
            print(f"❌ Meta-learner prediction failed: {e}")


def main():
    """Main debug function"""
    print("🔧 STANDARDSCALER FEATURE MISMATCH DEBUG")
    print("=" * 50)

    debug_standardscaler_issue()
    debug_prediction_flow()

    print("\n📋 === CONCLUSION ===")
    print("🎯 ROOT CAUSE: Meta-learner is receiving wrong input")
    print("   - Meta-learner scaler trained with 4 features (base model predictions)")
    print("   - But predict_ensemble passes 73 statistical features")
    print(
        "   - Need to fix predict_ensemble to use base model predictions for meta-learner"
    )
    print("")
    print("🔧 SOLUTION: Fix predict_ensemble method to:")
    print("   1. Get predictions from 4 base models using 73 features")
    print("   2. Use those 4 predictions as input to meta-learner")
    print("   3. Don't pass statistical features directly to meta-learner")


if __name__ == "__main__":
    main()
