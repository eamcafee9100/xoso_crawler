from datetime import date, timedelta
from django.test import TestCase
from results.models import NumberFrequencyStats
from results.services.frequency_analysis_service import FrequencyAnalysisService


class FrequencyAnalysisServiceQueryTests(TestCase):
    def setUp(self):
        self.service = FrequencyAnalysisService()

        def add_stat(number, d):
            NumberFrequencyStats.objects.create(
                number=number,
                date=d,
                appeared_in_special=False,
                appeared_in_first=False,
                appeared_in_other=True,
                day_of_week=d.weekday(),
                day_of_month=d.day,
                week_of_month=(d.day - 1) // 7 + 1,
                month=d.month,
                year=d.year,
            )

        d1 = date(2024, 1, 1)
        add_stat('01', d1)
        add_stat('02', d1)
        add_stat('03', d1)
        d2 = date(2024, 1, 3)
        add_stat('01', d2)
        add_stat('02', d2)
        add_stat('04', d2)
        add_stat('05', d1 - timedelta(days=1))
        add_stat('06', date(2024, 1, 2))
        add_stat('02', date(2024, 1, 2))

    def test_companion_numbers_queries(self):
        with self.assertNumQueries(2):
            companions = self.service._calculate_companion_numbers('01', date(2024, 1, 3))
        result = {c['number']: c['co_occurrences'] for c in companions}
        self.assertEqual(result.get('02'), 2)

    def test_predecessor_analysis_queries(self):
        with self.assertNumQueries(2):
            preds = self.service._calculate_predecessor_analysis('01', date(2024, 1, 3))
        result = {p['number']: p['occurrences'] for p in preds}
        self.assertEqual(result.get('05'), 1)
        self.assertEqual(result.get('06'), 1)
        self.assertEqual(result.get('02'), 1)
