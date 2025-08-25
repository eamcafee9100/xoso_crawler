#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TEST AJAX COMMAND: Django management command to test AJAX API
"""

from django.core.management.base import BaseCommand
from django.test import Client
import json


class Command(BaseCommand):
    help = 'Test AJAX prediction API with different dates'

    def handle(self, *args, **options):
        self.stdout.write("🧪 TESTING AJAX PREDICTION API")
        self.stdout.write("="*60)
        
        client = Client()
        test_dates = ['2025-08-12', '2025-08-06', '2025-07-15']
        results = {}
        
        for date in test_dates:
            self.stdout.write(f"\n📅 Testing date: {date}")
            self.stdout.write("-" * 40)
            
            test_data = {
                'prediction_date': date,
                'prediction_horizon': 3,
                'use_real_data': True
            }
            
            try:
                response = client.post(
                    '/analytic-frequence/ajax-prediction/',
                    data=json.dumps(test_data),
                    content_type='application/json'
                )
                
                self.stdout.write(f"📊 Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    success = data.get('success', False)
                    self.stdout.write(f"✅ Success: {success}")
                    
                    if success:
                        pred_data = data['prediction_data']
                        data_source = pred_data.get('data_source', 'unknown')
                        predictions = pred_data.get('predictions', [])
                        confidence = pred_data.get('confidence_score', 0)
                        
                        self.stdout.write(f"🔗 Data Source: {data_source}")
                        self.stdout.write(f"🎯 Predictions: {len(predictions)}")
                        self.stdout.write(f"🎖️ Confidence: {confidence}")
                        
                        results[date] = {
                            'data_source': data_source,
                            'confidence': confidence
                        }
                        
                        self.stdout.write(self.style.SUCCESS("✅ SUCCESS!"))
                    else:
                        error = data.get('error', 'Unknown error')
                        self.stdout.write(self.style.ERROR(f"❌ API Error: {error}"))
                else:
                    self.stdout.write(self.style.ERROR(f"❌ HTTP Error: {response.status_code}"))
                    content = response.content.decode()[:200]
                    self.stdout.write(f"📝 Response: {content}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Exception: {e}"))
        
        # Compare results
        if len(results) > 1:
            self.stdout.write(f"\n🔍 COMPARISON RESULTS:")
            self.stdout.write("="*60)
            
            data_sources = set()
            for date, result in results.items():
                data_sources.add(result['data_source'])
                self.stdout.write(f"📅 {date}: {result['data_source']}")
            
            if len(data_sources) > 1:
                self.stdout.write(self.style.SUCCESS("✅ SUCCESS: Different data sources!"))
                self.stdout.write(self.style.SUCCESS("✅ Date-specific analysis working!"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ Same data sources"))
        
        self.stdout.write("\n🏁 Testing completed")
