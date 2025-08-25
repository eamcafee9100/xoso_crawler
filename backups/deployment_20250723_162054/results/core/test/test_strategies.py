from django.test import TestCase
from datetime import date, timedelta
import numpy as np

from ..services.strategies import (
    detect_cycle_fft, phase_wilson_scores, gap_analysis, 
    frequency_analysis, pattern_mining
)

class StrategiesTestCase(TestCase):
    
    def test_detect_cycle_fft(self):
        """Test FFT cycle detection"""
        # Tạo chuỗi có chu kỳ rõ ràng
        hit_sequence = [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]  # Chu kỳ 3
        
        result = detect_cycle_fft(hit_sequence)
        
        self.assertIsInstance(result, dict)
        self.assertIn('dominant_period', result)
        self.assertIn('strength', result)
        self.assertIn('confidence', result)
        
        # Chu kỳ nên gần 3
        self.assertAlmostEqual(result['dominant_period'], 3.0, delta=0.5)
        self.assertGreater(result['confidence'], 0.1)
    
    def test_phase_wilson_scores(self):
        """Test Wilson scores cho các pha"""
        hit_sequence = [1, 0, 1, 1, 0, 1, 1, 0, 1]
        period = 3
        
        result = phase_wilson_scores(hit_sequence, period)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), period)
        
        for phase, score in result.items():
            self.assertIsInstance(phase, int)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 1)
    
    def test_gap_analysis(self):
        """Test phân tích khoảng cách"""
        today = date.today()
        number_history = {
            '12': [today - timedelta(days=5), today - timedelta(days=2)],
            '34': [today - timedelta(days=10)],
            '56': []
        }
        
        result = gap_analysis(number_history)
        
        self.assertIsInstance(result, dict)
        self.assertIn('12', result)
        self.assertIn('34', result)
        self.assertIn('56', result)
        
        for number, analysis in result.items():
            self.assertIn('avg_gap', analysis)
            self.assertIn('last_gap', analysis)
            self.assertIn('overdue_score', analysis)
    
    def test_frequency_analysis(self):
        """Test phân tích tần suất"""
        numbers_data = [('12', 10), ('34', 5), ('56', 8), ('78', 3)]
        
        result = frequency_analysis(numbers_data)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 4)
        
        # Kiểm tra số có tần suất cao nhất có rank = 1
        self.assertEqual(result['12']['rank'], 1)
        self.assertEqual(result['12']['frequency'], 10)
        self.assertAlmostEqual(result['12']['percentile'], 1.0)
    
    def test_pattern_mining(self):
        """Test khai thác mẫu"""
        sequences = [
            ['12', '34', '56'],
            ['12', '34', '78'],
            ['12', '90', '56'],
            ['34', '56', '78']
        ]
        
        result = pattern_mining(sequences)
        
        self.assertIsInstance(result, dict)
        
        for number, analysis in result.items():
            self.assertIn('companions', analysis)
            self.assertIn('strength', analysis)
            self.assertIsInstance(analysis['companions'], list)
            self.assertIsInstance(analysis['strength'], float)

