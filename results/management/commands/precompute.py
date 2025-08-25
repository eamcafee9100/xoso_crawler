# results/management/commands/generate_predictions.py
from django.core.management.base import BaseCommand
from datetime import date
from results.analytics.predictors import BachThuLoPredictor
from results.models import Prediction, EnhancedPrediction, PredictionMethod, KetQuaXoSo

class Command(BaseCommand):
    help = 'Generate predictions for today'

    def handle(self, *args, **kwargs):
        today = date.today()
        predictor = BachThuLoPredictor(target_date=today, history_days=90)

        # Tạo Prediction (SHAP)
        shap_numbers, shap_confidence = predictor._init_or_load_ml_model()
        actual_result = KetQuaXoSo.objects.filter(ngay=today).first()
        Prediction.objects.create(
            date=today,
            predicted_numbers=shap_numbers[:10] if shap_numbers else [],
            actual_result=actual_result,
            shap_values={"base_value": 0.5, "values": [], "features": []}
        )

        # Tạo EnhancedPrediction
        for method_name, method_func in predictor.methods.items():
            numbers, confidence = method_func()
            method, _ = PredictionMethod.objects.get_or_create(
                name=method_name,
                defaults={'description': method_name.replace('_', ' ').title()}
            )
            EnhancedPrediction.objects.create(
                date=today,
                method=method,
                numbers=numbers[:10],
                confidence_scores={num: confidence for num in numbers},
                accuracy=0.0
            )

        self.stdout.write(self.style.SUCCESS('Predictions generated successfully'))