import os
import sys
import traceback

import django

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
sys.path.append(".")
django.setup()

from data_integration_service import RealDataIntegrationService

from analytic_frequence.ultimate_prediction_system import UltimatePredictionSystem


def debug_insights_types():
    """Debug what insights are actually returning"""
    print("=== DEBUGGING INSIGHTS TYPES ===")

    try:
        # Get data
        data_service = RealDataIntegrationService()
        sample_data = data_service.get_recent_lottery_numbers(limit=50)
        print(f"Sample data: {sample_data[:10]}")

        # Create system
        system = UltimatePredictionSystem()

        # Test each insight individually
        print("\n--- INFORMATION INSIGHTS ---")
        info_insights = system._analyze_information_patterns(sample_data)
        print(f"Type: {type(info_insights)}")
        print(f"Content: {info_insights}")

        print("\n--- TIME CRYSTAL INSIGHTS ---")
        time_insights = system._analyze_time_crystal_properties(sample_data)
        print(f"Type: {type(time_insights)}")
        print(f"Content: {time_insights}")

        print("\n--- QUANTUM INSIGHTS ---")
        quantum_insights = system._analyze_quantum_entanglement(sample_data)
        print(f"Type: {type(quantum_insights)}")
        print(f"Content: {quantum_insights}")

        print("\n--- NEURAL INSIGHTS ---")
        neural_insights = system._analyze_neural_patterns(sample_data)
        print(f"Type: {type(neural_insights)}")
        print(f"Content: {neural_insights}")

        print("\n--- ENSEMBLE INSIGHTS ---")
        ensemble_insights = system._analyze_ensemble_consensus(sample_data)
        print(f"Type: {type(ensemble_insights)}")
        print(f"Content: {ensemble_insights}")

        print("\n--- CONSCIOUSNESS INSIGHTS ---")
        consciousness_insights = system._simulate_consciousness_analysis(sample_data)
        print(f"Type: {type(consciousness_insights)}")
        print(f"Content: {consciousness_insights}")

    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    debug_insights_types()
