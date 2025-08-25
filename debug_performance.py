"""
Debug chi tiết performance calculation
"""

import os
import sys
from datetime import date

import django
import numpy as np

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()


def debug_performance_calculation():
    """Debug chi tiết tính toán performance"""

    from predictions_tracker.views_dir.api_cyclical_prediction_by_date_v3 import (
        _analyze_cyclical_context_v3,
        _build_method_sync_matrix_v3,
        _calculate_overall_fatigue_risk,
        _filter_methods_by_cyclical_fitness_v3,
        _predict_cyclical_performance_v3,
        _predict_numbers_by_frequency_cycles_v3,
        _select_numbers_with_cyclical_intelligence_v3,
    )

    analysis_date = date.today()
    print(f"🔍 Debug Performance Calculation for: {analysis_date}")
    print("=" * 60)

    # Step 1: Get context
    context_analysis = _analyze_cyclical_context_v3(analysis_date)
    print(f"1️⃣ Context Analysis:")
    print(f"   - Cycle strength: {context_analysis.get('cycle_strength')}")

    # Step 2: Get sync matrix
    sync_matrix_data = _build_method_sync_matrix_v3(analysis_date, context_analysis)
    print(f"2️⃣ Sync Matrix:")
    print(f"   - Methods analyzed: {sync_matrix_data.get('total_methods_analyzed')}")

    # Step 3: Filter methods
    optimal_methods = _filter_methods_by_cyclical_fitness_v3(
        sync_matrix_data, 0.6, 15, analysis_date
    )
    print(f"3️⃣ Filtered Methods:")
    print(f"   - Candidates: {optimal_methods.get('total_candidates')}")
    print(f"   - Filtered count: {optimal_methods.get('filtered_count')}")

    filtered_methods = optimal_methods.get("cyclical_filtered", [])
    if filtered_methods:
        scores = [m["cyclical_score"] for m in filtered_methods]
        print(f"   - Score range: {min(scores):.1f} - {max(scores):.1f}")
        print(f"   - Average score: {np.mean(scores):.1f}")

    # Step 4: Get predictions
    cyclical_predictions = _predict_numbers_by_frequency_cycles_v3(analysis_date)
    intelligent_predictions = _select_numbers_with_cyclical_intelligence_v3(
        optimal_methods, cyclical_predictions, analysis_date
    )
    print(f"4️⃣ Intelligent Predictions:")
    print(
        f"   - Fusion numbers: {len(intelligent_predictions.get('fusion_numbers', []))}"
    )

    # Step 5: Manual performance calculation
    print(f"\n📊 Manual Performance Calculation:")
    print("-" * 40)

    cycle_strength = context_analysis.get("cycle_strength", 0.5)
    print(f"   - Cycle strength: {cycle_strength}")

    base_accuracy = min(0.6, cycle_strength * 0.8)
    print(f"   - Base accuracy: {base_accuracy:.3f} ({base_accuracy*100:.1f}%)")

    if filtered_methods:
        avg_cyclical_score = np.mean([m["cyclical_score"] for m in filtered_methods])
        method_bonus = min(0.2, avg_cyclical_score / 500)
        print(f"   - Avg cyclical score: {avg_cyclical_score:.1f}")
        print(f"   - Method bonus: {method_bonus:.3f} ({method_bonus*100:.1f}%)")
    else:
        method_bonus = 0
        print(f"   - Method bonus: 0 (no methods)")

    fusion_numbers = intelligent_predictions.get("fusion_numbers", [])
    fusion_bonus = min(0.1, len(fusion_numbers) / 150)
    print(f"   - Fusion numbers: {len(fusion_numbers)}")
    print(f"   - Fusion bonus: {fusion_bonus:.3f} ({fusion_bonus*100:.1f}%)")

    expected_accuracy = base_accuracy + method_bonus + fusion_bonus
    expected_accuracy = min(0.65, expected_accuracy)
    print(
        f"   - Total expected: {expected_accuracy:.3f} ({expected_accuracy*100:.1f}%)"
    )

    # Step 6: Compare with API function
    print(f"\n🔍 API Function Result:")
    print("-" * 40)

    performance_result = _predict_cyclical_performance_v3(
        optimal_methods, intelligent_predictions, context_analysis
    )

    api_accuracy = performance_result.get("expected_accuracy")
    print(f"   - API result: {api_accuracy}")
    print(f"   - Should be: {expected_accuracy*100:.1f}")

    if abs(api_accuracy - expected_accuracy * 100) > 0.1:
        print(
            f"   ❌ MISMATCH! Difference: {abs(api_accuracy - expected_accuracy*100):.1f}"
        )
    else:
        print(f"   ✅ MATCH!")

    print(f"\n📈 Performance Breakdown:")
    breakdown = performance_result.get("performance_breakdown", {})
    for key, value in breakdown.items():
        print(f"   - {key}: {value}")


if __name__ == "__main__":
    debug_performance_calculation()
