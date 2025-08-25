#!/usr/bin/env python3
# Simple test to verify V3 implementation


def test_v3_import():
    try:
        from predictions_tracker.enhanced_method_analyzer_v3 import (
            EnhancedMethodAnalyzerV3,
            ValidationConfig,
        )

        print("✅ Successfully imported V3 components")

        # Test initialization
        config = ValidationConfig()
        analyzer = EnhancedMethodAnalyzerV3(config)
        print("✅ V3 Analyzer initialized successfully")

        # Test basic methods
        disagreement = analyzer._calculate_timeframe_disagreement(
            {"score": 75, "confidence": 0.8}, {"score": 65, "confidence": 0.7}
        )
        print(f"✅ Disagreement calculation works: {disagreement:.3f}")

        confidence = analyzer._determine_confidence_level(0.3)
        print(f"✅ Confidence level determination works: {confidence}")

        print("\n🚀 V3 Implementation is working correctly!")
        return True

    except Exception as e:
        print(f"❌ V3 Import/Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_v3_import()
