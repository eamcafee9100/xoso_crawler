"""Quick test for TRANSCEND imports"""
import sys
import os

# Add path
transcend_path = os.path.join(os.path.dirname(__file__), 'analytic_frequence')
if transcend_path not in sys.path:
    sys.path.append(transcend_path)

print(f"Testing imports from: {transcend_path}")

try:
    from transcend_999_achievement_system import TranscendentPredictionSystem
    print('✅ TranscendentPredictionSystem imported successfully')
except ImportError as e:
    print(f'❌ TranscendentPredictionSystem import failed: {e}')

try:
    from quantum_ai_fusion_service import QuantumAIFusionEngine
    print('✅ QuantumAIFusionEngine imported successfully')
except ImportError as e:
    print(f'❌ QuantumAIFusionEngine import failed: {e}')

try:
    from quantum_algorithm_service import QuantumAnnealingOptimizer
    print('✅ QuantumAnnealingOptimizer imported successfully')
except ImportError as e:
    print(f'❌ QuantumAnnealingOptimizer import failed: {e}')

print("Import test completed!")
