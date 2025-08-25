from django.core.management.base import BaseCommand
from predictions_tracker.models import TrackingEvaluation, PredictionMethod, DailyTrackingSession
from predictions_tracker.core.services.DataService import data_service
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Train ML models for hit probability prediction'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--months-back',
            type=int,
            default=12,
            help='Number of months of data to use for training'
        )
        parser.add_argument(
            '--min-samples',
            type=int,
            default=20,
            help='Minimum samples per method to include in training'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force retrain even if models exist'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🔍 Debugging training data...")
        
        # 1. Kiểm tra có evaluations không
        total_evals = TrackingEvaluation.objects.count()
        self.stdout.write(f"📊 Total evaluations in DB: {total_evals}")
        
        if total_evals == 0:
            self.stdout.write("❌ No evaluations found! Need to run evaluations first.")
            return
        
        # 2. Kiểm tra date range
        latest_eval = TrackingEvaluation.objects.order_by('-evaluation_date').first()
        earliest_eval = TrackingEvaluation.objects.order_by('evaluation_date').first()
        
        self.stdout.write(f"📅 Date range: {earliest_eval.evaluation_date} to {latest_eval.evaluation_date}")
        
        # 3. Kiểm tra recent evaluations
        end_date = date.today()
        start_date = end_date - timedelta(days=90)  # 3 months
        
        recent_evals = TrackingEvaluation.objects.filter(
            evaluation_date__range=[start_date, end_date]
        ).count()
        
        self.stdout.write(f"📈 Recent evaluations (last 3 months): {recent_evals}")
        
        # 4. Kiểm tra methods có predictions
        methods_with_predictions = TrackingEvaluation.objects.filter(
            evaluation_date__range=[start_date, end_date],
            method_result__base_prediction_numbers__isnull=False
        ).values_list('method_result__method__id', flat=True).distinct()
        
        self.stdout.write(f"🎯 Methods with predictions: {list(methods_with_predictions)}")
        
        # 5. Test DataService
        try:
            training_data = data_service.get_training_data_for_ml(
                months_back=3,
                min_samples_per_method=5  # Lower threshold for testing
            )
            
            self.stdout.write(f"✅ DataService returned {len(training_data)} training samples")
            
            if training_data:
                sample = training_data[0]
                self.stdout.write(f"📋 Sample data structure:")
                for key, value in sample.items():
                    if key == 'features':
                        self.stdout.write(f"  {key}: {len(value)} features")
                    else:
                        self.stdout.write(f"  {key}: {value}")
        
        except Exception as e:
            self.stdout.write(f"❌ DataService error: {e}")
        
        # 6. Suggest solutions
        self.stdout.write("\n💡 Suggestions:")
        if recent_evals == 0:
            self.stdout.write("  - Run tracking evaluations for recent dates")
            self.stdout.write("  - Check if sessions have method_results with predictions")
        else:
            self.stdout.write("  - Lower min_samples_per_method threshold")
            self.stdout.write("  - Increase months_back parameter")
            self.stdout.write("  - Check if predicted_numbers are being saved correctly")