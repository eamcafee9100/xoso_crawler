import sys
import types
import datetime

# Mock minimal Django modules required for import
django = types.ModuleType('django')
sys.modules['django'] = django
sys.modules['django.db'] = types.ModuleType('django.db')
sys.modules['django.db.models'] = types.SimpleNamespace(Q=None, Count=None, Max=None, Min=None)
utils = types.ModuleType('django.utils')
utils.timezone = types.SimpleNamespace(now=lambda: datetime.datetime.now())
sys.modules['django.utils'] = utils
sys.modules['django.utils.timezone'] = utils.timezone

# Mock results.models dependencies
results_models = types.ModuleType('results.models')
results_models.NumberFrequencyStats = object
results_models.NumberAnalysisCache = object
results_models.NumberAnalysisDetail = object
results_models.KetQuaXoSo = object
sys.modules['results.models'] = results_models

from results.services.frequency_analysis_service import FrequencyAnalysisService


def test_returns_baseline_when_no_data(monkeypatch):
    monkeypatch.setenv('PREDICTION_BASELINE', '2.5')
    service = FrequencyAnalysisService()
    analysis_data = {
        'gan_analysis': {'current_gan_days': 0, 'max_gan_days': 0},
        'cycle_analysis': {'avg_cycle': 0}
    }
    probabilities = service._calculate_prediction_probabilities(analysis_data, [])
    assert probabilities == {
        'cycle_based': 2.5,
        'max_gan_based': 2.5,
        'combined': 2.5
    }
