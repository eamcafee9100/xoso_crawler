# management/commands/analyze_lottery_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
from results.models import KetQuaXoSo, NumberFrequencyStats
import json


class Command(BaseCommand):
    help = 'Analyze lottery data and generate comprehensive EDA report'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days to analyze (default: 365)'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='eda_report.json',
            help='Output file for EDA report'
        )
        parser.add_argument(
            '--populate-stats',
            action='store_true',
            help='Populate NumberFrequencyStats model'
        )

    def handle(self, *args, **options):
        days = options['days']
        output_file = options['output']
        populate_stats = options['populate_stats']
        
        self.stdout.write(f"Analyzing lottery data for the last {days} days...")
        
        # Get data
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        queryset = KetQuaXoSo.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).order_by('ngay')
        
        if not queryset.exists():
            self.stdout.write(
                self.style.ERROR('No lottery data found in the specified date range')
            )
            return
        
        # Perform analysis
        analysis_results = self.perform_eda(queryset)
        
        # Populate NumberFrequencyStats if requested
        if populate_stats:
            self.populate_frequency_stats(queryset)
        
        # Save results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False, default=str)
        
        self.stdout.write(
            self.style.SUCCESS(f'EDA completed. Results saved to {output_file}')
        )
        
        # Print summary
        self.print_summary(analysis_results)

    def perform_eda(self, queryset):
        """Perform comprehensive EDA on lottery data"""
        results = {
            'analysis_date': timezone.now().isoformat(),
            'data_summary': {},
            'number_frequency_analysis': {},
            'day_of_week_analysis': {},
            'temporal_patterns': {},
            'statistical_insights': {},
            'data_quality': {}
        }
        
        # Basic data summary
        results['data_summary'] = self.analyze_data_summary(queryset)
        
        # Number frequency analysis
        results['number_frequency_analysis'] = self.analyze_number_frequency(queryset)
        
        # Day of week patterns
        results['day_of_week_analysis'] = self.analyze_day_patterns(queryset)
        
        # Temporal patterns
        results['temporal_patterns'] = self.analyze_temporal_patterns(queryset)
        
        # Statistical insights
        results['statistical_insights'] = self.analyze_statistical_patterns(queryset)
        
        # Data quality assessment
        results['data_quality'] = self.assess_data_quality(queryset)
        
        return results

    def analyze_data_summary(self, queryset):
        """Basic data summary statistics"""
        total_records = queryset.count()
        date_range = {
            'start_date': queryset.first().ngay,
            'end_date': queryset.last().ngay,
            'total_days': total_records
        }
        
        # Count total numbers extracted
        all_numbers = []
        for record in queryset:
            numbers = record.get_all_2digit_numbers()
            all_numbers.extend(numbers)
        
        return {
            'total_records': total_records,
            'date_range': date_range,
            'total_numbers_extracted': len(all_numbers),
            'unique_numbers_seen': len(set(all_numbers)),
            'avg_numbers_per_day': len(all_numbers) / total_records if total_records > 0 else 0
        }

    def analyze_number_frequency(self, queryset):
        """Analyze frequency of each number (00-99)"""
        number_counts = Counter()
        number_last_seen = {}
        number_gaps = defaultdict(list)
        
        for record in queryset:
            numbers = record.get_all_2digit_numbers()
            date = record.ngay
            
            for number in numbers:
                number_counts[number] += 1
                
                # Track gaps between appearances
                if number in number_last_seen:
                    gap = (date - number_last_seen[number]).days
                    number_gaps[number].append(gap)
                
                number_last_seen[number] = date
        
        # Calculate statistics for each number
        number_stats = {}
        total_days = queryset.count()
        
        for number in [f"{i:02d}" for i in range(100)]:  # 00-99
            count = number_counts.get(number, 0)
            gaps = number_gaps.get(number, [])
            
            number_stats[number] = {
                'total_appearances': count,
                'frequency_rate': count / total_days if total_days > 0 else 0,
                'last_seen': number_last_seen.get(number),
                'avg_gap': np.mean(gaps) if gaps else None,
                'min_gap': min(gaps) if gaps else None,
                'max_gap': max(gaps) if gaps else None,
                'gap_std': np.std(gaps) if gaps else None,
                'days_since_last': (queryset.last().ngay - number_last_seen[number]).days 
                                  if number in number_last_seen else None
            }
        
        # Top and bottom performers
        sorted_by_frequency = sorted(
            number_stats.items(), 
            key=lambda x: x[1]['total_appearances'], 
            reverse=True
        )
        
        return {
            'individual_stats': number_stats,
            'top_10_frequent': sorted_by_frequency[:10],
            'bottom_10_frequent': sorted_by_frequency[-10:],
            'never_appeared': [num for num, stats in number_stats.items() 
                             if stats['total_appearances'] == 0],
            'frequency_distribution': {
                'mean': np.mean([stats['total_appearances'] for stats in number_stats.values()]),
                'median': np.median([stats['total_appearances'] for stats in number_stats.values()]),
                'std': np.std([stats['total_appearances'] for stats in number_stats.values()])
            }
        }

    def analyze_day_patterns(self, queryset):
        """Analyze patterns by day of week"""
        day_patterns = defaultdict(lambda: defaultdict(int))
        day_counts = defaultdict(int)
        
        day_names = {
            0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday',
            4: 'Friday', 5: 'Saturday', 6: 'Sunday'
        }
        
        for record in queryset:
            day_of_week = record.ngay.weekday()
            day_counts[day_of_week] += 1
            numbers = record.get_all_2digit_numbers()
            
            for number in numbers:
                day_patterns[day_of_week][number] += 1
        
        # Calculate day-specific statistics
        day_analysis = {}
        for day_num in range(7):
            day_name = day_names[day_num]
            day_numbers = day_patterns[day_num]
            total_days = day_counts[day_num]
            
            if total_days == 0:
                continue
            
            # Top numbers for this day
            sorted_numbers = sorted(
                day_numbers.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            day_analysis[day_name] = {
                'total_lottery_days': total_days,
                'total_numbers': sum(day_numbers.values()),
                'avg_numbers_per_day': sum(day_numbers.values()) / total_days,
                'top_10_numbers': sorted_numbers[:10],
                'unique_numbers_appeared': len(day_numbers)
            }
        
        return day_analysis

    def analyze_temporal_patterns(self, queryset):
        """Analyze temporal patterns (monthly, seasonal)"""
        monthly_patterns = defaultdict(lambda: defaultdict(int))
        yearly_patterns = defaultdict(lambda: defaultdict(int))
        
        for record in queryset:
            month = record.ngay.month
            year = record.ngay.year
            numbers = record.get_all_2digit_numbers()
            
            for number in numbers:
                monthly_patterns[month][number] += 1
                yearly_patterns[year][number] += 1
        
        # Monthly analysis
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        
        monthly_analysis = {}
        for month_num in range(1, 13):
            month_name = month_names[month_num]
            month_numbers = monthly_patterns[month_num]
            
            if not month_numbers:
                continue
            
            sorted_numbers = sorted(
                month_numbers.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            monthly_analysis[month_name] = {
                'total_numbers': sum(month_numbers.values()),
                'top_5_numbers': sorted_numbers[:5],
                'unique_numbers': len(month_numbers)
            }
        
        return {
            'monthly_patterns': monthly_analysis,
            'yearly_patterns': {
                str(year): {
                    'total_numbers': sum(numbers.values()),
                    'unique_numbers': len(numbers)
                } for year, numbers in yearly_patterns.items()
            }
        }

    def analyze_statistical_patterns(self, queryset):
        """Advanced statistical pattern analysis"""
        all_sequences = []
        number_transitions = defaultdict(lambda: defaultdict(int))
        
        for record in queryset:
            numbers = list(record.get_all_2digit_numbers())
            all_sequences.append(numbers)
            
            # Analyze number transitions (what numbers tend to appear together)
            for i in range(len(numbers)):
                for j in range(i + 1, len(numbers)):
                    number_transitions[numbers[i]][numbers[j]] += 1
                    number_transitions[numbers[j]][numbers[i]] += 1
        
        # Calculate digit distribution (0-9 frequency in each position)
        first_digit_dist = defaultdict(int)
        second_digit_dist = defaultdict(int)
        
        for sequence in all_sequences:
            for number in sequence:
                if len(number) == 2:
                    first_digit_dist[number[0]] += 1
                    second_digit_dist[number[1]] += 1
        
        # Sum patterns (what sums are most common)
        sum_distribution = defaultdict(int)
        for sequence in all_sequences:
            for number in sequence:
                if len(number) == 2 and number.isdigit():
                    digit_sum = int(number[0]) + int(number[1])
                    sum_distribution[digit_sum] += 1
        
        return {
            'digit_distributions': {
                'first_digit': dict(first_digit_dist),
                'second_digit': dict(second_digit_dist)
            },
            'sum_patterns': dict(sorted(sum_distribution.items(), 
                                       key=lambda x: x[1], reverse=True)),
            'most_common_transitions': {
                number: dict(sorted(transitions.items(), 
                                   key=lambda x: x[1], reverse=True)[:5])
                for number, transitions in number_transitions.items()
                if sum(transitions.values()) > 5  # Only numbers with significant transitions
            }
        }

    def assess_data_quality(self, queryset):
        """Assess data quality and completeness"""
        quality_issues = []
        total_records = queryset.count()
        
        # Check for missing data
        records_with_no_numbers = 0
        records_with_few_numbers = 0
        
        for record in queryset:
            numbers = record.get_all_2digit_numbers()
            if len(numbers) == 0:
                records_with_no_numbers += 1
            elif len(numbers) < 5:  # Assuming normal should have more numbers
                records_with_few_numbers += 1
        
        if records_with_no_numbers > 0:
            quality_issues.append(f"{records_with_no_numbers} records with no extractable numbers")
        
        if records_with_few_numbers > 0:
            quality_issues.append(f"{records_with_few_numbers} records with unusually few numbers")
        
        # Check for date gaps
        dates = [record.ngay for record in queryset.order_by('ngay')]
        gaps = []
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            if gap > 1:
                gaps.append(gap)
        
        if gaps:
            quality_issues.append(f"Found {len(gaps)} date gaps, largest gap: {max(gaps)} days")
        
        return {
            'total_records': total_records,
            'records_with_no_numbers': records_with_no_numbers,
            'records_with_few_numbers': records_with_few_numbers,
            'date_gaps': len(gaps),
            'quality_score': max(0, 100 - len(quality_issues) * 10),
            'issues': quality_issues
        }

    def populate_frequency_stats(self, queryset):
        """Populate NumberFrequencyStats model"""
        self.stdout.write("Populating NumberFrequencyStats model...")
        
        # Clear existing data for the date range
        start_date = queryset.first().ngay
        end_date = queryset.last().ngay
        
        NumberFrequencyStats.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).delete()
        
        batch_size = 1000
        stats_to_create = []
        
        for record in queryset:
            numbers = record.get_all_2digit_numbers()
            date = record.ngay
            
            for number in numbers:
                # Determine where the number appeared
                appeared_in_special = number in record.giai_db if record.giai_db else False
                appeared_in_first = number in record.giai_1 if record.giai_1 else False
                appeared_in_other = not (appeared_in_special or appeared_in_first)
                
                stat = NumberFrequencyStats(
                    number=number,
                    date=date,
                    appeared_in_special=appeared_in_special,
                    appeared_in_first=appeared_in_first,
                    appeared_in_other=appeared_in_other,
                    day_of_week=date.weekday(),
                    day_of_month=date.day,
                    week_of_month=((date.day - 1) // 7) + 1,
                    month=date.month,
                    year=date.year
                )
                stats_to_create.append(stat)
                
                if len(stats_to_create) >= batch_size:
                    NumberFrequencyStats.objects.bulk_create(
                        stats_to_create, ignore_conflicts=True
                    )
                    stats_to_create = []
        
        # Create remaining records
        if stats_to_create:
            NumberFrequencyStats.objects.bulk_create(
                stats_to_create, ignore_conflicts=True
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {NumberFrequencyStats.objects.filter(date__gte=start_date, date__lte=end_date).count()} frequency stat records"
            )
        )

    def print_summary(self, results):
        """Print analysis summary to console"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("LOTTERY DATA ANALYSIS SUMMARY"))
        self.stdout.write("="*60)
        
        # Data Summary
        summary = results['data_summary']
        self.stdout.write(f"\n📊 DATA OVERVIEW:")
        self.stdout.write(f"  • Total records: {summary['total_records']}")
        self.stdout.write(f"  • Date range: {summary['date_range']['start_date']} to {summary['date_range']['end_date']}")
        self.stdout.write(f"  • Numbers extracted: {summary['total_numbers_extracted']}")
        self.stdout.write(f"  • Unique numbers seen: {summary['unique_numbers_seen']}/100")
        self.stdout.write(f"  • Avg numbers/day: {summary['avg_numbers_per_day']:.1f}")
        
        # Top frequent numbers
        freq_analysis = results['number_frequency_analysis']
        self.stdout.write(f"\n🔢 TOP 10 MOST FREQUENT NUMBERS:")
        for i, (number, stats) in enumerate(freq_analysis['top_10_frequent'], 1):
            self.stdout.write(f"  {i:2d}. {number}: {stats['total_appearances']} times ({stats['frequency_rate']:.3f})")
        
        # Day patterns
        day_analysis = results['day_of_week_analysis']
        self.stdout.write(f"\n📅 DAY OF WEEK PATTERNS:")
        for day, stats in day_analysis.items():
            if stats['total_lottery_days'] > 0:
                self.stdout.write(f"  • {day}: {stats['total_lottery_days']} lottery days, avg {stats['avg_numbers_per_day']:.1f} numbers/day")
        
        # Data Quality
        quality = results['data_quality']
        self.stdout.write(f"\n✅ DATA QUALITY SCORE: {quality['quality_score']}/100")
        if quality['issues']:
            self.stdout.write("  Issues found:")
            for issue in quality['issues']:
                self.stdout.write(f"    - {issue}")
        
        self.stdout.write("\n" + "="*60)