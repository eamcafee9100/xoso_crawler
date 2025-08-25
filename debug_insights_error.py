import os
import sys

import django

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
sys.path.append(".")
django.setup()

from analytic_frequence.services import (
    ConsciousnessSimulator,
    InformationTheoryAnalyzer,
    QuantumEntanglementAnalyzer,
    RealDataIntegrationService,
    TimeCrystalAnalyzer,
)
from analytic_frequence.ultimate_prediction_system import UltimatePredictionSystem


def debug_insights():
    """Debug insights returning wrong types"""
    print("=== INSIGHTS DEBUG ===")

    # Get sample data
    data_service = RealDataIntegrationService()
    sample_data = data_service.get_recent_lottery_numbers(limit=50)

    if not sample_data:
        print("No data available")
        return

    print(f"Sample data: {sample_data[:10]}")

    # Test each analyzer
    analyzers = {
        "information": InformationTheoryAnalyzer(),
        "time_crystal": TimeCrystalAnalyzer(),
        "quantum": QuantumEntanglementAnalyzer(),
        "consciousness": ConsciousnessSimulator(),
    }

    for name, analyzer in analyzers.items():
        try:
            print(f"\n--- {name.upper()} ANALYZER ---")

            if name == "information":
                result = analyzer.analyze_information_content(sample_data)
            elif name == "time_crystal":
                result = analyzer.analyze_time_crystal_properties(sample_data)
            elif name == "quantum":
                result = analyzer.analyze_quantum_properties(sample_data)
            elif name == "consciousness":
                result = analyzer.simulate_consciousness_pattern(sample_data)

            print(f"Result type: {type(result)}")
            print(f"Result: {result}")

            if isinstance(result, dict):
                print("Dict keys and types:")
                for key, value in result.items():
                    print(f"  {key}: {type(value)} = {value}")

        except Exception as e:
            print(f"ERROR in {name}: {e}")


if __name__ == "__main__":
    debug_insights()
