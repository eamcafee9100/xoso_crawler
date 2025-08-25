#!/usr/bin/env python3
"""
🧪 SIMPLE IMPORT TEST - No heavy dependencies
"""

import sys
import os

# Add paths
project_root = r'c:\Users\n2t\Documents\xoso_crawler'
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'predictions_tracker'))

def test_simple_import():
    """Test simple import without sklearn"""
    print("Testing simple Python import...")
    
    try:
        print("Step 1: Test basic Python imports...")
        import numpy as np
        print("✅ NumPy imported")
        
        print("Step 2: Test dataclasses...")
        from dataclasses import dataclass
        print("✅ Dataclasses imported")
        
        print("Step 3: Test our module path...")
        import predictions_tracker
        print(f"✅ predictions_tracker imported from: {predictions_tracker}")
        
        print("Step 4: Test direct file import...")
        import sys
        portfolio_path = os.path.join(project_root, 'predictions_tracker', 'services', 'portfolio_optimization_service.py')
        print(f"File exists: {os.path.exists(portfolio_path)}")
        
        print("Step 5: Test minimal import...")
        # Try to import just the module without classes
        import predictions_tracker.services.portfolio_optimization_service as portfolio_module
        print("✅ Portfolio module imported")
        
        # Check what's available
        print("Available classes:", [name for name in dir(portfolio_module) if not name.startswith('_')])
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🔍 SIMPLE IMPORT TEST")
    print("=" * 40)
    test_simple_import()
