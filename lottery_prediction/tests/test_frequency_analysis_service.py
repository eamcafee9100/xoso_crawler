import pytest
from datetime import date, timedelta

from results.models import NumberFrequencyStats
from results.services.frequency_analysis_service import get_frequency_analysis_service


@pytest.mark.django_db
def test_probability_reduced_without_consecutive():
    analysis_date = date(2023, 1, 10)
    number = "12"

    for offset in [1, 4, 7]:
        dt = analysis_date - timedelta(days=offset)
        NumberFrequencyStats.objects.create(
            number=number,
            date=dt,
            appeared_in_special=False,
            appeared_in_first=False,
            appeared_in_other=True,
            day_of_week=dt.weekday(),
            day_of_month=dt.day,
            week_of_month=(dt.day - 1) // 7 + 1,
            month=dt.month,
            year=dt.year,
        )

    service = get_frequency_analysis_service()
    analysis = service.get_comprehensive_analysis(number, analysis_date=analysis_date)

    assert analysis["gan_analysis"]["current_gan_days"] == 1
    assert analysis["consecutive_analysis"]["max_consecutive_days"] == 0
    assert analysis["prediction_probabilities"]["combined"] < 30
