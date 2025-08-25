from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from results.tasks import update_daily_analysis_cache

class Command(BaseCommand):
    help = 'Update daily analysis cache for specified date range'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Specific date to update (YYYY-MM-DD format)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to update (from today backwards)'
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run as async task'
        )

    def handle(self, *args, **options):
        if options['date']:
            # Update specific date
            target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            dates_to_update = [target_date]
        else:
            # Update last N days
            end_date = timezone.now().date()
            dates_to_update = [
                end_date - timedelta(days=i) 
                for i in range(options['days'])
            ]

        self.stdout.write(f"Updating analysis cache for {len(dates_to_update)} dates...")

        for date in dates_to_update:
            date_str = date.strftime('%Y-%m-%d')
            
            if options['async']:
                # Run as async task
                task = update_daily_analysis_cache.delay(date_str)
                self.stdout.write(f"Queued async update for {date_str} (Task ID: {task.id})")
            else:
                # Run synchronously
                try:
                    result = update_daily_analysis_cache(date_str)
                    self.stdout.write(
                        self.style.SUCCESS(f"Updated cache for {date_str}: {result}")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to update cache for {date_str}: {str(e)}")
                    )

        self.stdout.write(self.style.SUCCESS("Cache update completed!"))