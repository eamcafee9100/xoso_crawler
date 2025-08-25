"""
Test TRANSCEND 99.9% API Integration
"""
import requests
import json
from datetime import date, timedelta

def test_api():
    # Test API
    test_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    api_url = 'http://localhost:8000/predictions_tracker/api/method-analysis-by-date-v2/'
    params = {
        'analysis_date': test_date, 
        'limit': 5, 
        'threshold': 40, 
        'hybrid': 'true'
    }

    print('🌟 Testing TRANSCEND 99.9% Integration...')
    print(f'📊 Testing date: {test_date}')

    try:
        response = requests.get(api_url, params=params, timeout=30)
        print(f'📡 Response Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            
            # Check TRANSCEND integration
            transcend_integration = data.get('hybrid_analysis', {}).get('transcend_integration', {})
            print(f'🌟 TRANSCEND Available: {transcend_integration.get("available", False)}')
            print(f'🌟 TRANSCEND Enabled: {transcend_integration.get("enabled", False)}')
            print(f'🌟 TRANSCEND Status: {transcend_integration.get("status", "Unknown")}')
            
            # Check algorithm version
            algorithm_version = data.get("metadata", {}).get("algorithm_version", "unknown")
            print(f'🌟 Algorithm Version: {algorithm_version}')
            
            # Check TRANSCEND data
            transcend_data = data.get('transcend_999_analysis')
            if transcend_data:
                print('✅ TRANSCEND 99.9% Analysis Data Found!')
                
                transcendent_prediction = transcend_data.get('transcendent_prediction', {})
                print(f'🎯 Transcendent Numbers: {transcendent_prediction.get("numbers", [])}')
                print(f'🎯 Confidence: {transcendent_prediction.get("confidence", 0):.3f}')
                print(f'🎯 Overall Transcendence: {transcendent_prediction.get("overall_transcendence", 0):.1%}')
                print(f'🎯 Breakthrough Achieved: {transcendent_prediction.get("breakthrough_achieved", False)}')
                
                # Phase excellence
                phase_excellence = transcend_data.get('phase_excellence', {})
                print(f'🏆 Phase Excellence Scores:')
                for phase, score in phase_excellence.items():
                    print(f'   {phase}: {score:.1%}')
                    
                # Integration info
                integration_info = transcend_data.get('integration_info', {})
                print(f'📊 Integration Info:')
                print(f'   Enhanced Methods: {integration_info.get("enhanced_methods", 0)}')
                print(f'   Transcend Boost Applied: {integration_info.get("transcend_boost_applied", False)}')
                print(f'   Risk Assessment Enhanced: {integration_info.get("risk_assessment_enhanced", False)}')
                
            else:
                print('⚠️ No TRANSCEND 99.9% data found')
                
            print('✅ Test completed successfully!')
            
        else:
            print(f'❌ API Error: {response.status_code}')
            print(f'Response: {response.text[:500]}')
            
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    test_api()
