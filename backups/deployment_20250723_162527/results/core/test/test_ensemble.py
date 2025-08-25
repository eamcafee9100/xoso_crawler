# filepath: results/core/tests/test_ensemble.py
from django.test import TestCase
from datetime import date
from unittest.mock import patch, MagicMock

from ..services.ensemble import combine_strategies, get_historical_hits

class EnsembleTestCase(TestCase):
    
    @patch('results.core.services.ensemble.get_historical_hits')
    def test_combine_strategies(self, mock_get_historical_hits):
        """Test kết hợp chiến lược"""
        # Mock dữ liệu
        mock_get_historical_hits.return_value = {
            'method1': [
                {
                    'date': date.today(),
                    'predicted_numbers': ['12', '34'],
                    'winning_numbers': ['12'],
                    'hit_count': 1
                }
            ]
        }
        
        analysis_date = date.today()
        history_data = {'method1': []}
        
        result = combine_strategies(analysis_date, history_data)
        
        self.assertIsInstance(result, list)
        
        if result:  # Nếu có kết quả
            for item in result:
                self.assertIn('number', item)
                self.assertIn('score', item)
                self.assertIn('strategies', item)
                self.assertIsInstance(item['score'], float)
                self.assertIsInstance(item['strategies'], dict)
    
    def test_get_historical_hits(self):
        """Test lấy dữ liệu lịch sử"""
        analysis_date = date.today()
        
        # Test với database trống
        result = get_historical_hits(analysis_date)
        
        self.assertIsInstance(result, dict)
        # Với database trống, kết quả có thể rỗng