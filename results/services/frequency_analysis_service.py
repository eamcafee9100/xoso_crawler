"""
Service for advanced lottery number frequency analysis
Provides comprehensive statistical analysis for lottery numbers
"""
import json
import logging
from collections import defaultdict, Counter
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Optional, Any
import statistics

from django.db.models import Q, Count, Max, Min
from django.utils import timezone

from results.models import NumberFrequencyStats, NumberAnalysisCache, NumberAnalysisDetail, KetQuaXoSo

logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and date objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def serialize_date_objects(data):
    """Convert date objects to strings for JSON serialization"""
    if isinstance(data, dict):
        return {key: serialize_date_objects(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_date_objects(item) for item in data]
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    else:
        return data


class FrequencyAnalysisService:
    """Service for performing advanced frequency analysis on lottery numbers"""
    
    def __init__(self):
        self.cache_validity_days = 1  # Cache validity period
    
    def get_comprehensive_analysis(self, number: str, analysis_date: date = None) -> Dict[str, Any]:
        """
        Get comprehensive analysis for a specific number
        Returns cached data if available and valid, otherwise calculates new analysis
        """
        if analysis_date is None:
            analysis_date = timezone.now().date()
        
        # Try to get cached analysis
        try:
            cached_analysis = NumberAnalysisCache.objects.get(
                number=number,
                analysis_date=analysis_date
            )
            
            # Check if cache is still valid
            cache_age = (timezone.now().date() - cached_analysis.updated_at.date()).days
            if cache_age <= self.cache_validity_days:
                return self._format_cached_analysis(cached_analysis)
        except NumberAnalysisCache.DoesNotExist:
            pass
        
        # Calculate new analysis
        return self._calculate_and_cache_analysis(number, analysis_date)
    
    def _calculate_and_cache_analysis(self, number: str, analysis_date: date) -> Dict[str, Any]:
        """Calculate comprehensive analysis and cache the results"""
        
        # Get historical data for this number
        frequency_data = NumberFrequencyStats.objects.filter(
            number=number,
            date__lte=analysis_date
        ).order_by('-date')
        
        if not frequency_data.exists():
            return self._empty_analysis(number)
        
        # Calculate various statistics
        analysis_result = {
            'number': number,
            'analysis_date': analysis_date,
            'basic_stats': self._calculate_basic_stats(frequency_data, analysis_date),
            'gan_analysis': self._calculate_gan_analysis(frequency_data, analysis_date),
            'cycle_analysis': self._calculate_cycle_analysis(frequency_data),
            'weekday_patterns': self._calculate_weekday_patterns(frequency_data),
            'companion_numbers': self._calculate_companion_numbers(number, analysis_date),
            'consecutive_analysis': self._calculate_consecutive_analysis(frequency_data),
            'predecessor_analysis': self._calculate_predecessor_analysis(number, analysis_date),
            'prediction_probabilities': {}
        }
        
        # Calculate prediction probabilities based on patterns
        analysis_result['prediction_probabilities'] = self._calculate_prediction_probabilities(
            analysis_result, frequency_data
        )
        
        # Cache the results
        self._cache_analysis_results(analysis_result)
        
        return analysis_result
    
    def _calculate_basic_stats(self, frequency_data, analysis_date: date) -> Dict[str, Any]:
        """Calculate basic frequency statistics"""
        
        # Get data for last 30 days and 1 year
        thirty_days_ago = analysis_date - timedelta(days=30)
        one_year_ago = analysis_date - timedelta(days=365)
        
        appearances_30d = frequency_data.filter(date__gte=thirty_days_ago).count()
        appearances_1y = frequency_data.filter(date__gte=one_year_ago).count()
        total_appearances = frequency_data.count()
        
        # Get last and first appearance as ISO strings for JSON serialization
        last_appearance = None
        first_appearance = None
        
        if frequency_data.exists():
            last_record = frequency_data.first()
            first_record = frequency_data.last()
            
            if last_record:
                last_appearance = last_record.date.isoformat()
            if first_record:
                first_appearance = first_record.date.isoformat()
        
        return {
            'appearances_30d': appearances_30d,
            'appearances_1y': appearances_1y,
            'total_appearances': total_appearances,
            'last_appearance': last_appearance,
            'first_appearance': first_appearance
        }
    
    def _calculate_gan_analysis(self, frequency_data, analysis_date: date) -> Dict[str, Any]:
        """Calculate 'gan' (absence) analysis"""
        
        if not frequency_data.exists():
            return {'current_gan_days': 0, 'max_gan_days': 0, 'gan_history': []}
        
        # Calculate current gan (days since last appearance)
        last_appearance = frequency_data.first().date
        current_gan_days = (analysis_date - last_appearance).days
        
        # Calculate historical gan periods
        dates = [item.date for item in frequency_data]
        dates.sort()
        
        gan_periods = []
        if len(dates) > 1:
            for i in range(len(dates) - 1):
                gap = (dates[i + 1] - dates[i]).days - 1
                if gap > 0:
                    # Convert dates to ISO format for JSON serialization
                    gan_periods.append({
                        'start_date': dates[i].isoformat(),
                        'end_date': dates[i + 1].isoformat(),
                        'days': gap
                    })
        
        max_gan_days = max([period['days'] for period in gan_periods]) if gan_periods else 0
        avg_gan_days = statistics.mean([period['days'] for period in gan_periods]) if gan_periods else 0
        
        return {
            'current_gan_days': current_gan_days,
            'max_gan_days': max_gan_days,
            'avg_gan_days': round(avg_gan_days, 2),
            'gan_history': gan_periods[-10:],  # Last 10 gan periods
            'gan_distribution': self._calculate_gan_distribution(gan_periods)
        }
    
    def _calculate_cycle_analysis(self, frequency_data) -> Dict[str, Any]:
        """Calculate cycle patterns (intervals between appearances)"""
        
        dates = [item.date for item in frequency_data]
        dates.sort()
        
        if len(dates) < 2:
            return {'avg_cycle': 0, 'median_cycle': 0, 'cycle_distribution': {}}
        
        cycles = []
        for i in range(len(dates) - 1):
            cycle = (dates[i + 1] - dates[i]).days
            cycles.append(cycle)
        
        avg_cycle = statistics.mean(cycles)
        median_cycle = statistics.median(cycles)
        
        # Cycle distribution
        cycle_distribution = Counter(cycles)
        
        return {
            'avg_cycle': round(avg_cycle, 2),
            'median_cycle': round(median_cycle, 2),
            'min_cycle': min(cycles),
            'max_cycle': max(cycles),
            'cycle_distribution': dict(cycle_distribution.most_common(10))
        }
    
    def _calculate_weekday_patterns(self, frequency_data) -> Dict[str, Any]:
        """Calculate patterns by day of week"""
        
        weekday_counts = defaultdict(int)
        for item in frequency_data:
            weekday_counts[item.day_of_week] += 1
        
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_analysis = {}
        
        total_appearances = sum(weekday_counts.values())
        
        for i, name in enumerate(weekday_names):
            count = weekday_counts[i]
            percentage = (count / total_appearances * 100) if total_appearances > 0 else 0
            weekday_analysis[name] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        return weekday_analysis
    
    def _calculate_companion_numbers(self, number: str, analysis_date: date) -> List[Dict[str, Any]]:
        """Calculate numbers that frequently appear together with the given number"""
        
        # Get dates when this number appeared
        appearance_dates = list(
            NumberFrequencyStats.objects.filter(
                number=number,
                date__lte=analysis_date
            ).values_list('date', flat=True)
        )

        if not appearance_dates:
            return []

        total_appearances = len(appearance_dates)

        # Query once for all companion numbers and aggregate
        companion_qs = (
            NumberFrequencyStats.objects.filter(date__in=appearance_dates)
            .exclude(number=number)
            .values('number')
            .annotate(co_occurrences=Count('id'))
            .order_by('-co_occurrences')[:10]
        )

        companions = [
            {
                'number': item['number'],
                'co_occurrences': item['co_occurrences'],
                'percentage': round(item['co_occurrences'] / total_appearances * 100, 2)
            }
            for item in companion_qs
        ]

        return companions
    
    def _calculate_consecutive_analysis(self, frequency_data) -> Dict[str, Any]:
        """Calculate consecutive appearance patterns"""
        
        dates = [item.date for item in frequency_data]
        dates.sort()
        
        consecutive_sequences = []
        current_sequence = []
        
        for i, date in enumerate(dates):
            if i == 0:
                current_sequence = [date]
            else:
                if (date - dates[i-1]).days == 1:
                    current_sequence.append(date)
                else:
                    if len(current_sequence) > 1:
                        # Convert dates to ISO format for JSON serialization
                        consecutive_sequences.append({
                            'start_date': current_sequence[0].isoformat(),
                            'end_date': current_sequence[-1].isoformat(),
                            'days': len(current_sequence)
                        })
                    current_sequence = [date]
        
        # Don't forget the last sequence
        if len(current_sequence) > 1:
            consecutive_sequences.append({
                'start_date': current_sequence[0].isoformat(),
                'end_date': current_sequence[-1].isoformat(),
                'days': len(current_sequence)
            })
        
        max_consecutive = max([seq['days'] for seq in consecutive_sequences]) if consecutive_sequences else 0
        
        return {
            'max_consecutive_days': max_consecutive,
            'consecutive_history': consecutive_sequences[-5:],  # Last 5 sequences
            'consecutive_distribution': dict(Counter([seq['days'] for seq in consecutive_sequences]))
        }
    
    def _calculate_predecessor_analysis(self, number: str, analysis_date: date) -> List[Dict[str, Any]]:
        """Calculate numbers that frequently appear before this number"""
        
        # Get dates when this number appeared
        appearance_dates = list(
            NumberFrequencyStats.objects.filter(
                number=number,
                date__lte=analysis_date
            ).values_list('date', flat=True)
        )

        if not appearance_dates:
            return []

        previous_dates = [d - timedelta(days=1) for d in appearance_dates]
        total_opportunities = len(appearance_dates)

        predecessor_qs = (
            NumberFrequencyStats.objects.filter(date__in=previous_dates)
            .values('number')
            .annotate(occurrences=Count('id'))
            .order_by('-occurrences')[:10]
        )

        predecessors = [
            {
                'number': item['number'],
                'occurrences': item['occurrences'],
                'percentage': round(item['occurrences'] / total_opportunities * 100, 2)
            }
            for item in predecessor_qs
        ]

        return predecessors
    
    def _calculate_prediction_probabilities(self, analysis_data: Dict, frequency_data) -> Dict[str, float]:
        """Calculate prediction probabilities based on patterns"""
        
        gan_analysis = analysis_data['gan_analysis']
        cycle_analysis = analysis_data['cycle_analysis']
        
        # Probability based on average cycle
        if cycle_analysis['avg_cycle'] > 0:
            cycle_probability = max(0, 100 - (gan_analysis['current_gan_days'] / cycle_analysis['avg_cycle'] * 100))
        else:
            cycle_probability = 50
        
        # Probability when approaching max gan
        if gan_analysis['max_gan_days'] > 0:
            max_gan_ratio = gan_analysis['current_gan_days'] / gan_analysis['max_gan_days']
            max_gan_probability = min(100, max_gan_ratio * 100)
        else:
            max_gan_probability = 50
        
        # Combined probability (weighted average)
        combined_probability = (cycle_probability * 0.6 + max_gan_probability * 0.4)
        
        return {
            'cycle_based': round(cycle_probability, 2),
            'max_gan_based': round(max_gan_probability, 2),
            'combined': round(combined_probability, 2)
        }
    
    def _calculate_gan_distribution(self, gan_periods: List[Dict]) -> Dict[str, int]:
        """Calculate distribution of gan periods"""
        
        if not gan_periods:
            return {}
        
        # Group gan periods into ranges
        distribution = {
            '1-5 days': 0,
            '6-10 days': 0,
            '11-20 days': 0,
            '21-30 days': 0,
            '31+ days': 0
        }
        
        for period in gan_periods:
            days = period['days']
            if days <= 5:
                distribution['1-5 days'] += 1
            elif days <= 10:
                distribution['6-10 days'] += 1
            elif days <= 20:
                distribution['11-20 days'] += 1
            elif days <= 30:
                distribution['21-30 days'] += 1
            else:
                distribution['31+ days'] += 1
        
        return distribution
    
    def _cache_analysis_results(self, analysis_data: Dict[str, Any]) -> None:
        """Cache analysis results for performance"""
        
        try:
            # Serialize date objects before caching
            serialized_weekday_analysis = serialize_date_objects(analysis_data['weekday_patterns'])
            serialized_companion_numbers = serialize_date_objects(analysis_data['companion_numbers'])
            serialized_consecutive_history = serialize_date_objects(analysis_data['consecutive_analysis']['consecutive_history'])
            serialized_predecessor_analysis = serialize_date_objects(analysis_data['predecessor_analysis'])
            
            # Handle max_gan dates
            max_gan_start_date = None
            max_gan_end_date = None
            if analysis_data['gan_analysis']['gan_history']:
                # Get the period with max gan
                max_gan_period = max(analysis_data['gan_analysis']['gan_history'], 
                                   key=lambda x: x.get('days', 0), default={})
                if max_gan_period:
                    max_gan_start_date = max_gan_period.get('start_date')
                    max_gan_end_date = max_gan_period.get('end_date')
            
            # Create or update cache entry
            cache_obj, created = NumberAnalysisCache.objects.update_or_create(
                number=analysis_data['number'],
                analysis_date=analysis_data['analysis_date'],
                defaults={
                    'appearances_30d': analysis_data['basic_stats']['appearances_30d'],
                    'appearances_total': analysis_data['basic_stats']['total_appearances'],
                    'avg_cycle_days': analysis_data['cycle_analysis']['avg_cycle'],
                    'median_cycle_days': analysis_data['cycle_analysis']['median_cycle'],
                    'current_gan_days': analysis_data['gan_analysis']['current_gan_days'],
                    'max_gan_days': analysis_data['gan_analysis']['max_gan_days'],
                    'max_gan_start_date': max_gan_start_date,
                    'max_gan_end_date': max_gan_end_date,
                    'probability_next_appearance': analysis_data['prediction_probabilities']['combined'],
                    'probability_when_max_gan': analysis_data['prediction_probabilities']['max_gan_based'],
                    'weekday_analysis': serialized_weekday_analysis,
                    'companion_numbers': serialized_companion_numbers,
                    'max_consecutive_days': analysis_data['consecutive_analysis']['max_consecutive_days'],
                    'consecutive_history': serialized_consecutive_history,
                    'predecessor_analysis': serialized_predecessor_analysis
                }
            )
            
            # Cache detailed analysis with serialized data
            details_to_cache = [
                ('gan_history', serialize_date_objects(analysis_data['gan_analysis']['gan_history'])),
                ('cycle_pattern', serialize_date_objects(analysis_data['cycle_analysis'])),
                ('companion_detail', serialized_companion_numbers),
                ('consecutive_events', serialize_date_objects(analysis_data['consecutive_analysis']))
            ]
            
            for detail_type, data in details_to_cache:
                NumberAnalysisDetail.objects.update_or_create(
                    cache=cache_obj,
                    detail_type=detail_type,
                    defaults={'data': data}
                )
                
        except Exception as e:
            logger.error(f"Error caching analysis for {analysis_data['number']}: {e}")
            # Log more details for debugging
            logger.error(f"Analysis data keys: {list(analysis_data.keys())}")
            if 'gan_analysis' in analysis_data:
                logger.error(f"Gan history sample: {analysis_data['gan_analysis']['gan_history'][:1] if analysis_data['gan_analysis']['gan_history'] else 'empty'}")
    
    def _format_cached_analysis(self, cached_analysis: NumberAnalysisCache) -> Dict[str, Any]:
        """Format cached analysis into the expected structure"""
        
        # Get detailed analysis
        details = {}
        for detail in cached_analysis.details.all():
            details[detail.detail_type] = detail.data
        
        # Get last appearance from basic stats
        last_appearance = None
        if cached_analysis.appearances_total > 0:
            # Try to get from gan history
            gan_history = details.get('gan_history', [])
            if gan_history:
                # Get the most recent end date
                try:
                    recent_dates = []
                    for period in gan_history:
                        if 'end_date' in period:
                            end_date = period['end_date']
                            if isinstance(end_date, str):
                                from datetime import datetime
                                end_date = datetime.fromisoformat(end_date).date()
                            recent_dates.append(end_date)
                    if recent_dates:
                        last_appearance = max(recent_dates)
                except Exception as e:
                    logger.warning(f"Error parsing last appearance date: {e}")
        
        return {
            'number': cached_analysis.number,
            'analysis_date': cached_analysis.analysis_date,
            'basic_stats': {
                'appearances_30d': cached_analysis.appearances_30d,
                'total_appearances': cached_analysis.appearances_total,
                'last_appearance': last_appearance
            },
            'gan_analysis': {
                'current_gan_days': cached_analysis.current_gan_days,
                'max_gan_days': cached_analysis.max_gan_days,
                'gan_history': details.get('gan_history', [])
            },
            'cycle_analysis': details.get('cycle_pattern', {}),
            'weekday_patterns': cached_analysis.weekday_analysis,
            'companion_numbers': cached_analysis.companion_numbers,
            'consecutive_analysis': details.get('consecutive_events', {}),
            'predecessor_analysis': cached_analysis.predecessor_analysis,
            'prediction_probabilities': {
                'combined': cached_analysis.probability_next_appearance,
                'max_gan_based': cached_analysis.probability_when_max_gan
            }
        }
    
    def _empty_analysis(self, number: str) -> Dict[str, Any]:
        """Return empty analysis structure when no data is available"""
        
        return {
            'number': number,
            'analysis_date': timezone.now().date(),
            'basic_stats': {'appearances_30d': 0, 'total_appearances': 0, 'last_appearance': None},
            'gan_analysis': {'current_gan_days': 0, 'max_gan_days': 0, 'gan_history': []},
            'cycle_analysis': {'avg_cycle': 0, 'median_cycle': 0, 'cycle_distribution': {}},
            'weekday_patterns': {},
            'companion_numbers': [],
            'consecutive_analysis': {'max_consecutive_days': 0, 'consecutive_history': []},
            'predecessor_analysis': [],
            'prediction_probabilities': {'combined': 0, 'max_gan_based': 0}
        }
    
    def get_batch_analysis_summary(self, numbers: List[str], analysis_date: date = None) -> Dict[str, Dict]:
        """Get summary analysis for multiple numbers"""
        
        if analysis_date is None:
            analysis_date = timezone.now().date()
        
        results = {}
        for number in numbers:
            try:
                analysis = self.get_comprehensive_analysis(number, analysis_date)
                results[number] = {
                    'current_gan_days': analysis['gan_analysis']['current_gan_days'],
                    'max_gan_days': analysis['gan_analysis']['max_gan_days'],
                    'probability': analysis['prediction_probabilities']['combined'],
                    'appearances_30d': analysis['basic_stats']['appearances_30d'],
                    'avg_cycle': analysis['cycle_analysis']['avg_cycle']
                }
            except Exception as e:
                logger.error(f"Error analyzing number {number}: {e}")
                results[number] = {
                    'current_gan_days': 0,
                    'max_gan_days': 0,
                    'probability': 0,
                    'appearances_30d': 0,
                    'avg_cycle': 0
                }
        
        return results


# Singleton instance
_frequency_service_instance = None

def get_frequency_analysis_service() -> FrequencyAnalysisService:
    """Get singleton instance of frequency analysis service"""
    global _frequency_service_instance
    if _frequency_service_instance is None:
        _frequency_service_instance = FrequencyAnalysisService()
    return _frequency_service_instance
