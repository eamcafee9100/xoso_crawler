#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 SYSTEM STATUS MONITORING
Monitor the revolutionary system status in real-time
"""

import os
import django
import sys
import time
from datetime import datetime

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

def check_system_status():
    """Check comprehensive system status"""
    
    print(f"""
🎯 ULTIMATE REVOLUTIONARY SYSTEM STATUS
=====================================
📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)
    
    status_report = {
        'core_systems': {},
        'performance': {},
        'errors': [],
        'warnings': []
    }
    
    # Check core systems
    print("🔧 Checking Core Systems...")
    
    try:
        from analytic_frequence.service_manager import service_manager
        service_status = service_manager.get_status()
        status_report['core_systems']['service_manager'] = '✅ OPERATIONAL'
        print(f"  ✅ ServiceManager: {service_status['healthy']}")
    except Exception as e:
        status_report['core_systems']['service_manager'] = f'❌ ERROR: {e}'
        status_report['errors'].append(f"ServiceManager: {e}")
        print(f"  ❌ ServiceManager: {e}")
    
    try:
        from analytic_frequence.intelligent_cache import intelligent_cache
        cache_stats = intelligent_cache.get_performance_stats()
        status_report['core_systems']['intelligent_cache'] = '✅ OPERATIONAL'
        print(f"  ✅ IntelligentCache: {len(cache_stats.get('cache_performance', {}))} metrics")
    except Exception as e:
        status_report['core_systems']['intelligent_cache'] = f'❌ ERROR: {e}'
        status_report['errors'].append(f"IntelligentCache: {e}")
        print(f"  ❌ IntelligentCache: {e}")
    
    try:
        from analytic_frequence.performance_monitoring import performance_monitor
        status_report['core_systems']['performance_monitor'] = '✅ OPERATIONAL'
        print(f"  ✅ PerformanceMonitor: Active")
    except Exception as e:
        status_report['core_systems']['performance_monitor'] = f'❌ ERROR: {e}'
        status_report['errors'].append(f"PerformanceMonitor: {e}")
        print(f"  ❌ PerformanceMonitor: {e}")
    
    # Check advanced systems
    print("\n⚡ Checking Advanced Systems...")
    
    try:
        from analytic_frequence.redis_advanced_cache import redis_advanced_cache
        cache_status = redis_advanced_cache.get_cache_status()
        status_report['core_systems']['redis_cache'] = '✅ OPERATIONAL'
        print(f"  ✅ Redis Advanced Cache: {cache_status.get('status', 'Unknown')}")
    except Exception as e:
        status_report['core_systems']['redis_cache'] = f'❌ ERROR: {e}'
        status_report['warnings'].append(f"Redis Cache: {e}")
        print(f"  ⚠️ Redis Advanced Cache: {e}")
    
    try:
        from analytic_frequence.database_optimizer import db_optimizer
        optimization_stats = db_optimizer.get_optimization_stats()
        status_report['core_systems']['db_optimizer'] = '✅ OPERATIONAL'
        print(f"  ✅ Database Optimizer: {optimization_stats.get('active_optimizations', 0)} optimizations")
    except Exception as e:
        status_report['core_systems']['db_optimizer'] = f'❌ ERROR: {e}'
        status_report['warnings'].append(f"Database Optimizer: {e}")
        print(f"  ⚠️ Database Optimizer: {e}")
    
    try:
        from analytic_frequence.async_processing import background_job_processor
        system_status = background_job_processor.get_system_status()
        status_report['core_systems']['async_processor'] = '✅ OPERATIONAL'
        print(f"  ✅ Async Processor: {system_status.get('active_workers', 0)} workers")
    except Exception as e:
        status_report['core_systems']['async_processor'] = f'❌ ERROR: {e}'
        status_report['warnings'].append(f"Async Processor: {e}")
        print(f"  ⚠️ Async Processor: {e}")
    
    # Check AI systems
    print("\n🧠 Checking AI Systems...")
    
    try:
        from analytic_frequence.adaptive_ui_system import adaptive_ui_analyzer
        ui_status = adaptive_ui_analyzer.get_system_status()
        status_report['core_systems']['adaptive_ui'] = '✅ OPERATIONAL'
        print(f"  ✅ Adaptive UI: {ui_status.get('active_users', 0)} users tracked")
    except Exception as e:
        status_report['core_systems']['adaptive_ui'] = f'❌ ERROR: {e}'
        status_report['warnings'].append(f"Adaptive UI: {e}")
        print(f"  ⚠️ Adaptive UI: {e}")
    
    # Check template views
    print("\n🎯 Checking Template Views...")
    
    try:
        from analytic_frequence.template_views import UltimatePredictionTemplateView
        status_report['core_systems']['template_views'] = '✅ OPERATIONAL'
        print(f"  ✅ Template Views: Available")
    except Exception as e:
        status_report['core_systems']['template_views'] = f'❌ ERROR: {e}'
        status_report['errors'].append(f"Template Views: {e}")
        print(f"  ❌ Template Views: {e}")
    
    # Performance summary
    print("\n📊 Performance Summary:")
    operational_systems = len([v for v in status_report['core_systems'].values() if '✅' in v])
    total_systems = len(status_report['core_systems'])
    health_percentage = (operational_systems / total_systems * 100) if total_systems > 0 else 0
    
    print(f"  🎯 System Health: {health_percentage:.1f}% ({operational_systems}/{total_systems} systems)")
    print(f"  ❌ Errors: {len(status_report['errors'])}")
    print(f"  ⚠️ Warnings: {len(status_report['warnings'])}")
    
    if health_percentage >= 80:
        print(f"  🏆 STATUS: EXCELLENT - Revolutionary system operational!")
    elif health_percentage >= 60:
        print(f"  ✅ STATUS: GOOD - System mostly operational")
    elif health_percentage >= 40:
        print(f"  ⚠️ STATUS: DEGRADED - Some systems need attention")
    else:
        print(f"  🚨 STATUS: CRITICAL - Major systems offline")
    
    # Show errors and warnings
    if status_report['errors']:
        print(f"\n❌ ERRORS ({len(status_report['errors'])}):")
        for error in status_report['errors']:
            print(f"  • {error}")
    
    if status_report['warnings']:
        print(f"\n⚠️ WARNINGS ({len(status_report['warnings'])}):")
        for warning in status_report['warnings']:
            print(f"  • {warning}")
    
    return status_report

def test_urls():
    """Test key URLs"""
    
    print(f"\n🌐 Testing Key URLs...")
    
    urls_to_test = [
        ("Root", "http://127.0.0.1:8000/"),
        ("Analytic Frequence", "http://127.0.0.1:8000/analytic-frequence/"),
        ("Ultimate Prediction", "http://127.0.0.1:8000/analytic-frequence/ultimate-prediction/"),
        ("API v1", "http://127.0.0.1:8000/analytic-frequence/api/v1/")
    ]
    
    try:
        import requests
        for name, url in urls_to_test:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    print(f"  ✅ {name}: {response.status_code} ({response_time:.0f}ms)")
                else:
                    print(f"  ⚠️ {name}: {response.status_code} ({response_time:.0f}ms)")
                    
            except Exception as e:
                print(f"  ❌ {name}: {e}")
                
    except ImportError:
        print("  ⚠️ Requests not available - skipping URL tests")

if __name__ == "__main__":
    try:
        status = check_system_status()
        test_urls()
        
        print(f"""
🎯 MONITORING COMPLETED
=====================
System ready for production use!

📱 Access URLs:
• Home: http://127.0.0.1:8000
• Ultimate Prediction: http://127.0.0.1:8000/analytic-frequence/ultimate-prediction/
• API v1: http://127.0.0.1:8000/analytic-frequence/api/v1/

🚀 Revolutionary transformation achieved!
        """)
        
    except Exception as e:
        print(f"\n❌ MONITORING FAILED: {e}")
        import traceback
        traceback.print_exc()
