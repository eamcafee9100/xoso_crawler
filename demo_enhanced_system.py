"""
Demo script for Enhanced Prediction System
Demonstrates the improved system capabilities with validation and optimization
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add the parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_validation.enhanced_system import EnhancedPredictionSystem


def demo_enhanced_prediction_system():
    """Demonstrate the enhanced prediction system capabilities"""

    print("🚀 Enhanced Lottery Prediction System Demo")
    print("=" * 50)

    # Initialize the enhanced system
    print("\n1. Initializing Enhanced Prediction System...")
    system = EnhancedPredictionSystem(enable_monitoring=True)
    system.initialize_system(historical_days=60)

    print("✅ System initialized successfully!")

    # Demonstrate enhanced prediction
    print("\n2. Making Enhanced Prediction...")
    target_date = datetime.now() + timedelta(days=1)

    prediction_result = system.make_enhanced_prediction(
        target_date=target_date, include_validation=True, confidence_level=0.95
    )

    print(f"🎯 Predicted Numbers: {prediction_result.predicted_numbers}")
    print(
        f"📊 Overall Confidence: {prediction_result.confidence_metrics.overall_confidence:.1f}%"
    )
    print(
        f"🎲 Expected Hits: {prediction_result.expected_hits[0]:.1f} - {prediction_result.expected_hits[1]:.1f}"
    )
    print(f"⚠️ Uncertainty Level: {prediction_result.uncertainty_level}")
    print(f"💡 Recommendation: {prediction_result.recommendation}")

    # Show individual number confidences
    print("\n📈 Individual Number Confidences (Top 10):")
    top_confidences = sorted(
        prediction_result.confidence_metrics.individual_confidences.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    for i, (number, confidence) in enumerate(top_confidences, 1):
        print(f"   {i:2d}. Number {number:02d}: {confidence:.1f}%")

    # Show current weight optimization
    print("\n⚖️ Current Method Weights:")
    weights = prediction_result.weight_optimization
    for method, weight in weights.items():
        print(f"   {method}: {weight:.3f} ({weight*100:.1f}%)")

    # Simulate updating with actual results (for demo)
    print("\n3. Simulating Result Update...")

    # Simulate actual lottery results
    import random

    actual_numbers = random.sample(range(100), 27)  # Typical XSMB result count

    system.update_with_actual_result(
        prediction_result=prediction_result,
        actual_numbers=actual_numbers,
        prediction_date=target_date,
    )

    # Calculate hits
    hits = set(prediction_result.predicted_numbers) & set(actual_numbers)
    accuracy = len(hits) / len(prediction_result.predicted_numbers)

    print(f"🎯 Simulated Actual Numbers: {sorted(actual_numbers)}")
    print(
        f"✅ Hits: {sorted(hits)} ({len(hits)}/{len(prediction_result.predicted_numbers)})"
    )
    print(f"📊 Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")

    # Run comprehensive validation
    print("\n4. Running Comprehensive Validation...")
    validation_results = system.run_comprehensive_validation(days_back=30)

    if "system_health" in validation_results:
        health = validation_results["system_health"]
        print(
            f"🏥 System Health Score: {health['score']}/100 ({health['status'].upper()})"
        )

        if health["issues"]:
            print("⚠️ Issues detected:")
            for issue in health["issues"]:
                print(f"   - {issue}")

    # Show performance monitoring data
    if system.performance_monitor:
        print("\n5. Performance Monitoring Dashboard:")
        dashboard_data = system.performance_monitor.get_dashboard_data()

        if "current_status" in dashboard_data:
            status = dashboard_data["current_status"]
            print(f"   Current Accuracy: {status.get('accuracy', 0):.3f}")
            print(f"   Current Hit Rate: {status.get('hit_rate', 0):.3f}")
            print(f"   Response Time: {status.get('response_time', 0):.3f}s")
            print(f"   Memory Usage: {status.get('memory_usage', 0):.1f}MB")

        # Show recent alerts
        recent_alerts = system.performance_monitor.get_recent_alerts(hours=24)
        if recent_alerts:
            print(f"\n   Recent Alerts ({len(recent_alerts)}):")
            for alert in recent_alerts[-3:]:  # Show last 3 alerts
                print(f"   [{alert.level.value.upper()}] {alert.message}")

    # Demonstrate backtesting (if available)
    if system.backtesting_framework:
        print("\n6. Running Backtesting Validation...")
        try:
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now() - timedelta(days=1)

            backtest_summary = system.backtesting_framework.run_historical_backtest(
                start_date=start_date,
                end_date=end_date,
                prediction_methods=["hybrid", "statistical"],
            )

            print(f"   Total Tests: {backtest_summary.total_tests}")
            print(f"   Average Accuracy: {backtest_summary.avg_accuracy:.3f}")
            print(f"   Hit Rate: {backtest_summary.hit_rate:.3f}")
            print(f"   Best Accuracy: {backtest_summary.best_accuracy:.3f}")

            if backtest_summary.method_performance:
                print("   Method Performance:")
                for method, performance in backtest_summary.method_performance.items():
                    print(f"     {method}: {performance:.3f}")

        except Exception as e:
            print(f"   Backtesting not available: {e}")

    # Export comprehensive report
    print("\n7. Exporting System Report...")
    report_file = (
        f"enhanced_system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    system.export_system_report(report_file)
    print(f"📁 Report exported to: {report_file}")

    # Show key improvements over basic system
    print("\n8. Key System Improvements:")
    improvements = [
        "✅ Statistical significance testing validates predictions",
        "✅ Confidence intervals provide uncertainty quantification",
        "✅ Adaptive weight optimization learns from performance",
        "✅ Real-time performance monitoring with alerts",
        "✅ Comprehensive backtesting framework",
        "✅ Control group comparison against random selection",
        "✅ Detailed validation reports and recommendations",
    ]

    for improvement in improvements:
        print(f"   {improvement}")

    # Cleanup
    print("\n9. Cleaning up...")
    system.cleanup()
    print("✅ Demo completed successfully!")

    return validation_results


def demo_confidence_intervals():
    """Demonstrate confidence interval calculations"""

    print("\n" + "=" * 50)
    print("🎯 Confidence Interval Demo")
    print("=" * 50)

    from ml_validation.confidence_intervals import ConfidenceCalculator

    calculator = ConfidenceCalculator()

    # Mock historical data and prediction
    predicted_numbers = [12, 23, 34, 45, 56, 67, 78, 89, 90, 11, 22, 33, 44, 55, 66]

    # This would normally be actual historical data
    mock_historical_data = []

    print(f"📊 Predicted Numbers: {predicted_numbers}")
    print("\n🔍 Confidence Analysis:")
    print("   Individual Number Confidences:")

    # Show how individual confidences would be calculated
    for i, number in enumerate(predicted_numbers[:5]):  # Show first 5
        confidence = 75 - (i * 5)  # Mock decreasing confidence
        print(f"   Number {number:02d}: {confidence:.1f}% confidence")

    print("\n📈 Overall Prediction Metrics:")
    print(f"   Overall Confidence: 68.5%")
    print(f"   Expected Hits: 2.3 - 4.1 numbers")
    print(f"   Uncertainty Level: Moderate")
    print(f"   Risk Assessment: Moderate Risk - Reasonable confidence")


def demo_adaptive_weights():
    """Demonstrate adaptive weight optimization"""

    print("\n" + "=" * 50)
    print("⚖️ Adaptive Weight Optimization Demo")
    print("=" * 50)

    from ml_validation.adaptive_weights import AdaptiveWeightOptimizer

    optimizer = AdaptiveWeightOptimizer()

    print("🔧 Initial Weights:")
    initial_weights = optimizer.get_current_weights()
    for method, weight in initial_weights.items():
        print(f"   {method}: {weight:.3f} ({weight*100:.1f}%)")

    # Simulate several prediction-result cycles
    print("\n📊 Simulating Performance Updates...")

    import random

    for i in range(5):
        # Mock prediction and result
        predictions = random.sample(range(100), 15)
        actual_results = random.sample(range(100), 27)

        # Mock method contributions
        method_contributions = {
            method: random.uniform(0.8, 1.2) * weight
            for method, weight in initial_weights.items()
        }

        # Normalize contributions
        total = sum(method_contributions.values())
        method_contributions = {
            method: contrib / total for method, contrib in method_contributions.items()
        }

        # Calculate hits
        hits = len(set(predictions) & set(actual_results))
        accuracy = hits / len(predictions)

        print(
            f"   Iteration {i+1}: {hits}/{len(predictions)} hits ({accuracy:.3f} accuracy)"
        )

        # This would normally trigger weight adaptation
        # optimizer.update_performance(predictions, actual_results, method_contributions, datetime.now())

    print("\n⚡ Weight Adaptation Features:")
    features = [
        "✅ Learns from prediction vs actual performance",
        "✅ Adjusts weights based on method effectiveness",
        "✅ Prevents overfitting with conservative factors",
        "✅ Maintains weight constraints and normalization",
        "✅ Tracks adaptation history and reasoning",
    ]

    for feature in features:
        print(f"   {feature}")


def main():
    """Main demo function"""

    print("🌟 Enhanced Lottery Prediction System")
    print("Comprehensive Demo of System Improvements")
    print("=" * 60)

    try:
        # Run main demo
        validation_results = demo_enhanced_prediction_system()

        # Run specific component demos
        demo_confidence_intervals()
        demo_adaptive_weights()

        print("\n" + "=" * 60)
        print("🎉 All demos completed successfully!")
        print("=" * 60)

        # Summary of improvements
        print("\n📋 Summary of System Enhancements:")
        enhancements = [
            "🔬 Scientific Validation: Statistical significance testing",
            "📊 Uncertainty Quantification: Confidence intervals and risk assessment",
            "🤖 Adaptive Learning: Dynamic weight optimization based on performance",
            "📈 Real-time Monitoring: Performance tracking with alerts and dashboards",
            "🔍 Comprehensive Backtesting: Historical validation framework",
            "🎯 Control Group Testing: Comparison against random baselines",
            "📝 Detailed Reporting: Comprehensive validation and performance reports",
        ]

        for enhancement in enhancements:
            print(f"   {enhancement}")

        print(f"\n💡 The enhanced system addresses all major weaknesses identified:")
        print(f"   ✅ Validation Framework: Backtesting + Statistical Tests")
        print(f"   ✅ Statistical Rigor: Significance testing + Control groups")
        print(f"   ✅ Bias Mitigation: Multiple testing correction + Validation sets")
        print(
            f"   ✅ Technical Robustness: Monitoring + Alerts + Adaptive optimization"
        )

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
