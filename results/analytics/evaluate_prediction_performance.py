from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

from .performance_evaluator import PerformanceEvaluator

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Evaluates the performance of prediction methods on historical data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to analyze'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date for analysis (YYYY-MM-DD), defaults to yesterday'
        )
        # Thêm tham số --force
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-evaluation of dates that already have statistics'
        )

    def handle(self, *args, **options):
        days = options['days']
        end_date = None
        force = options['force']  # Lấy giá trị của tham số force
        
        if options['end_date']:
            try:
                from datetime import datetime
                end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').date()
            except Exception as e:
                self.stderr.write(f"Error parsing end date: {e}")
                end_date = timezone.now().date() - timedelta(days=1)
        else:
            end_date = timezone.now().date() - timedelta(days=1)
            
        self.stdout.write(f"Evaluating prediction performance for the last {days} days ending on {end_date}")
        
        # Truyền tham số force cho PerformanceEvaluator
        evaluator = PerformanceEvaluator(historical_days=days, force_evaluation=force)
        
        try:
            results = evaluator.run_historical_evaluation(end_date=end_date, days=days)
            
            self.stdout.write(self.style.SUCCESS(f"Evaluation completed successfully"))
            
            # Print summary statistics
            self.stdout.write("\nOverall statistics:")
            overall_stats = results.get('overall_stats', {})
            
            for method, stats in overall_stats.get('method_stats', {}).items():
                self.stdout.write(f"Method: {method}")
                self.stdout.write(f"  Hit rate: {stats.get('hit_rate', 0):.2f}%")
                self.stdout.write(f"  Day hit rate: {stats.get('day_hit_rate', 0):.2f}%")
                self.stdout.write(f"  Tired rate: {stats.get('tired_rate', 0):.2f}%")
                self.stdout.write(f"  Total hits: {stats.get('correct_predictions', 0)}/{stats.get('total_predictions', 0)}")
                
            # Print updated weights
            self.stdout.write("\nUpdated method weights:")
            weights = evaluator.get_current_method_weights()
            
            for method, weight in weights.items():
                self.stdout.write(f"  {method}: {weight:.2f}")
                
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during evaluation: {e}"))
            logger.error(f"Error in evaluate_prediction_performance command: {e}", exc_info=True)