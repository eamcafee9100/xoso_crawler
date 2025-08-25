#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug script to check prediction system output
"""

from analytic_frequence.data_integration_service import RealDataIntegrationService
from analytic_frequence.ultimate_prediction_system import (
    create_ultimate_prediction_system,
)


def debug_prediction_system():
    print("=== TESTING CURRENT PREDICTION SYSTEM ===")

    # Initialize services
    data_service = RealDataIntegrationService()
    ultimate_system = create_ultimate_prediction_system()

    # Get real data
    real_data = data_service.get_enhanced_lottery_input()
    sample_numbers = real_data.get("lottery_numbers", [])
    print(f"Input numbers: {sample_numbers[:10]}...")

    # Get prediction
    input_data = (
        sample_numbers[:20]
        if len(sample_numbers) >= 20
        else [12, 25, 34, 8, 41, 17, 29, 3, 36, 22]
    )
    print(f"Using input data: {input_data}")

    result = ultimate_system.ultimate_prediction_analysis(
        lottery_numbers=input_data, prediction_horizon=5, include_explanations=True
    )

    print(f"Primary predictions: {result.primary_predictions}")
    print(f"Prediction type: {type(result.primary_predictions)}")

    if hasattr(result.primary_predictions, "__len__"):
        print(f"Number of predictions: {len(result.primary_predictions)}")

        # Check individual predictions
        for i, pred in enumerate(result.primary_predictions):
            print(f"  Prediction {i}: {pred} (type: {type(pred)})")
            if hasattr(pred, "__dict__"):
                print(f"    Attributes: {pred.__dict__}")
    else:
        print("Predictions do not have length attribute")


if __name__ == "__main__":
    debug_prediction_system()
