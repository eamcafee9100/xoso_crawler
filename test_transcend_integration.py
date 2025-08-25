"""
🌟 TRANSCEND 99.9% Integration Test
=================================

Test script để kiểm tra tích hợp TRANSCEND 99.9% vào API
"""

import os
import sys
import django

# Setup Django
sys.path.append('c:\\Users\\n2t\\Documents\\xoso_crawler')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

import requests
import json
from datetime import date, timedelta

def test_transcend_integration():
    """Test TRANSCEND 99.9% integration in API"""
    print("🌟 TESTING TRANSCEND 99.9% INTEGRATION")
    print("=" * 50)
    
    # Test date
    test_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # API endpoint
    api_url = "http://localhost:8000/predictions_tracker/api/method-analysis-by-date-v2/"
    
    # Test parameters
    params = {
        "analysis_date": test_date,
        "limit": 10,
        "threshold": 40,
        "hybrid": "true"
    }
    
    print(f"📊 Testing API with date: {test_date}")
    print(f"🔧 Parameters: {params}")
    
    try:
        # Make API request
        response = requests.get(api_url, params=params, timeout=30)
        
        print(f"\n📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if TRANSCEND is integrated
            transcend_integration = data.get("hybrid_analysis", {}).get("transcend_integration", {})
            
            print(f"\n🌟 TRANSCEND Integration Status:")
            print(f"   Available: {transcend_integration.get('available', False)}")
            print(f"   Enabled: {transcend_integration.get('enabled', False)}")
            print(f"   Status: {transcend_integration.get('status', 'Unknown')}")
            
            # Check algorithm version
            algorithm_version = data.get("metadata", {}).get("algorithm_version", "unknown")
            print(f"   Algorithm Version: {algorithm_version}")
            
            # Check for TRANSCEND data
            transcend_data = data.get("transcend_999_analysis")
            if transcend_data:
                print(f"\n🎯 TRANSCEND 99.9% Analysis Results:")
                transcendent_prediction = transcend_data.get("transcendent_prediction", {})
                print(f"   Transcendent Numbers: {transcendent_prediction.get('numbers', [])}")
                print(f"   Confidence: {transcendent_prediction.get('confidence', 0):.3f}")
                print(f"   Overall Transcendence: {transcendent_prediction.get('overall_transcendence', 0):.1%}")
                print(f"   Breakthrough Achieved: {transcendent_prediction.get('breakthrough_achieved', False)}")
                
                integration_info = transcend_data.get("integration_info", {})
                print(f"\n📊 Integration Metrics:")
                print(f"   Enhanced Methods: {integration_info.get('enhanced_methods', 0)}")
                print(f"   Transcend Boost Applied: {integration_info.get('transcend_boost_applied', False)}")
                print(f"   Risk Assessment Enhanced: {integration_info.get('risk_assessment_enhanced', False)}")
                
                phase_excellence = transcend_data.get("phase_excellence", {})
                print(f"\n🏆 Phase Excellence Scores:")
                for phase, score in phase_excellence.items():
                    print(f"   {phase}: {score:.1%}")
            else:
                print("\n⚠️  No TRANSCEND 99.9% analysis data found")
            
            # Check optimal methods for TRANSCEND enhancement
            optimal_methods = data.get("optimal_methods", {})
            transcend_enhanced_count = 0
            
            for day, methods in optimal_methods.items():
                for method in methods:
                    if method.get('transcend_metadata', {}).get('enhanced_by_transcend', False):
                        transcend_enhanced_count += 1
            
            print(f"\n📈 Methods Enhanced by TRANSCEND: {transcend_enhanced_count}")
            
            # Performance prediction
            performance_prediction = data.get("performance_prediction", {})
            print(f"\n🎯 Performance Prediction:")
            print(f"   Expected Hit Rate: {performance_prediction.get('expected_hit_rate', 0):.1%}")
            print(f"   Confidence Level: {performance_prediction.get('confidence_level', 'unknown')}")
            
            print(f"\n✅ TRANSCEND 99.9% Integration Test COMPLETED!")
            
            if transcend_data:
                print(f"🌟 TRANSCEND 99.9% Successfully Integrated!")
            else:
                print(f"⚠️  TRANSCEND 99.9% Integration Needs Attention")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        print(f"💡 Make sure Django server is running on localhost:8000")
        
    except Exception as e:
        print(f"❌ Test Error: {e}")

def test_transcend_availability():
    """Test if TRANSCEND components are available"""
    print("\n🔍 TESTING TRANSCEND 99.9% AVAILABILITY")
    print("=" * 45)
    
    try:
        # Test path setup
        transcend_path = 'c:\\Users\\n2t\\Documents\\xoso_crawler\\analytic_frequence'
        print(f"📁 TRANSCEND Path: {transcend_path}")
        print(f"   Path Exists: {os.path.exists(transcend_path)}")
        
        if transcend_path not in sys.path:
            sys.path.append(transcend_path)
            print(f"   Path Added to sys.path")
        
        # Test imports
        try:
            from transcend_999_achievement_system import TranscendentPredictionSystem
            print(f"✅ TranscendentPredictionSystem imported successfully")
        except ImportError as e:
            print(f"❌ TranscendentPredictionSystem import failed: {e}")
            
        try:
            from quantum_ai_fusion_service import QuantumAIFusionEngine
            print(f"✅ QuantumAIFusionEngine imported successfully")
        except ImportError as e:
            print(f"❌ QuantumAIFusionEngine import failed: {e}")
            
        try:
            from quantum_algorithm_service import QuantumAnnealingOptimizer
            print(f"✅ QuantumAnnealingOptimizer imported successfully")
        except ImportError as e:
            print(f"❌ QuantumAnnealingOptimizer import failed: {e}")
            
    except Exception as e:
        print(f"❌ Availability test error: {e}")

if __name__ == "__main__":
    test_transcend_availability()
    test_transcend_integration()
