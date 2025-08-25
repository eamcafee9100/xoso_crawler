#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 SIMPLE TEST: Test the Ultimate Prediction System
Quick test script for the prediction API
"""

import requests
import json

def simple_test():
    """Simple test of the prediction API"""
    
    url = "http://127.0.0.1:8000/analytic-frequence/ajax-prediction/"
    
    test_data = {
        "prediction_date": "2025-08-13",
        "prediction_horizon": 5,
        "use_real_data": True
    }
    
    print("🧪 Testing Prediction API...")
    print(f"URL: {url}")
    print(f"Data: {test_data}")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Response keys: {list(data.keys())}")
            
            if 'prediction_data' in data:
                pred_data = data['prediction_data']
                print(f"Predictions: {len(pred_data.get('predictions', []))}")
                print(f"Confidence: {pred_data.get('confidence_score')}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    simple_test()
