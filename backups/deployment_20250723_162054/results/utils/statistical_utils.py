"""
Statistical analysis utilities for ensemble prediction
Provides various statistical functions for lottery number analysis
"""
import numpy as np
import logging
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
from datetime import date, timedelta

logger = logging.getLogger(__name__)

def gap_analysis(number_dates: Dict[str, List[date]]) -> Dict[str, Dict[str, float]]:
    """
    Analyze gaps between number appearances
    
    Args:
        number_dates: Dictionary mapping numbers to their appearance dates
        
    Returns:
        Dictionary with gap analysis results for each number
    """
    results = {}
    
    for number, dates in number_dates.items():
        if len(dates) < 2:
            results[number] = {
                'avg_gap': 0,
                'last_gap': 0,
                'overdue_score': 0,
                'gap_variance': 0
            }
            continue
        
        # Sort dates
        sorted_dates = sorted(dates)
        
        # Calculate gaps in days
        gaps = []
        for i in range(1, len(sorted_dates)):
            gap = (sorted_dates[i] - sorted_dates[i-1]).days
            gaps.append(gap)
        
        if gaps:
            avg_gap = np.mean(gaps)
            gap_variance = np.var(gaps)
            last_gap = (date.today() - sorted_dates[-1]).days
            
            # Overdue score: how much longer than average since last appearance
            overdue_score = max(0, (last_gap - avg_gap) / avg_gap) if avg_gap > 0 else 0
            
            results[number] = {
                'avg_gap': float(avg_gap),
                'last_gap': int(last_gap),
                'overdue_score': float(overdue_score),
                'gap_variance': float(gap_variance)
            }
        else:
            results[number] = {
                'avg_gap': 0,
                'last_gap': 0,
                'overdue_score': 0,
                'gap_variance': 0
            }
    
    return results

def frequency_analysis(numbers: List[str], window_size: int = 30) -> Dict[str, float]:
    """
    Analyze frequency of number appearances
    
    Args:
        numbers: List of numbers that appeared
        window_size: Size of analysis window
        
    Returns:
        Dictionary mapping numbers to their frequency scores
    """
    if not numbers:
        return {}
    
    # Count frequencies
    counter = Counter(numbers)
    max_count = max(counter.values()) if counter else 1
    
    # Normalize to 0-1 range
    frequency_scores = {}
    for number, count in counter.items():
        frequency_scores[number] = count / max_count
    
    return frequency_scores

def pattern_mining(sequences: List[List[str]], min_support: float = 0.1) -> List[Dict[str, Any]]:
    """
    Mine frequent patterns from sequences
    
    Args:
        sequences: List of number sequences
        min_support: Minimum support threshold
        
    Returns:
        List of patterns with support and confidence metrics
    """
    if not sequences:
        return []
    
    patterns = []
    
    # Simple 2-gram pattern mining
    bigrams = defaultdict(int)
    total_bigrams = 0
    
    for sequence in sequences:
        if len(sequence) >= 2:
            for i in range(len(sequence) - 1):
                bigram = (sequence[i], sequence[i + 1])
                bigrams[bigram] += 1
                total_bigrams += 1
    
    # Filter by minimum support
    min_count = int(min_support * total_bigrams)
    
    for bigram, count in bigrams.items():
        if count >= min_count:
            support = count / total_bigrams
            confidence = count / max(1, sum(1 for seq in sequences for i in range(len(seq)-1) if seq[i] == bigram[0]))
            
            patterns.append({
                'sequence': list(bigram),
                'support': float(support),
                'confidence': float(confidence),
                'count': int(count)
            })
    
    # Sort by support descending
    patterns.sort(key=lambda x: x['support'], reverse=True)
    
    return patterns[:10]  # Return top 10 patterns

def ensemble_diversity_score(strategy_predictions: Dict[str, List[str]]) -> float:
    """
    Calculate diversity score for ensemble predictions
    
    Args:
        strategy_predictions: Dict mapping strategy names to their predictions
        
    Returns:
        Diversity score between 0 and 1 (higher = more diverse)
    """
    if not strategy_predictions or len(strategy_predictions) < 2:
        return 0.0
    
    strategies = list(strategy_predictions.keys())
    total_pairs = 0
    total_diversity = 0.0
    
    # Calculate pairwise diversity
    for i in range(len(strategies)):
        for j in range(i + 1, len(strategies)):
            pred1 = set(strategy_predictions[strategies[i]])
            pred2 = set(strategy_predictions[strategies[j]])
            
            if not pred1 and not pred2:
                continue
            
            # Jaccard diversity = 1 - Jaccard similarity
            intersection = len(pred1 & pred2)
            union = len(pred1 | pred2)
            
            if union > 0:
                jaccard_similarity = intersection / union
                diversity = 1 - jaccard_similarity
                total_diversity += diversity
                total_pairs += 1
    
    return total_diversity / total_pairs if total_pairs > 0 else 0.0

def calculate_ensemble_confidence(scores: List[float]) -> float:
    """
    Calculate confidence score for ensemble predictions
    
    Args:
        scores: List of prediction scores
        
    Returns:
        Confidence score between 0 and 100
    """
    if not scores:
        return 0.0
    
    mean_score = np.mean(scores)
    std_score = np.std(scores)
    
    # Higher mean and lower std = higher confidence
    confidence = mean_score * 100 * (1 - min(std_score, 0.5))
    
    return min(max(confidence, 0.0), 100.0)

def detect_cycles_autocorr(series: List[float], max_lag: int = None) -> List[Dict[str, Any]]:
    """
    Detect cycles using autocorrelation
    
    Args:
        series: Time series data
        max_lag: Maximum lag to consider
        
    Returns:
        List of detected cycles with periods and confidence
    """
    if len(series) < 4:
        return []
    
    if max_lag is None:
        max_lag = min(len(series) // 2, 50)
    
    # Calculate autocorrelation
    series_array = np.array(series)
    mean_series = np.mean(series_array)
    series_centered = series_array - mean_series
    
    cycles = []
    
    try:
        # Calculate autocorrelation for different lags
        autocorr_values = []
        for lag in range(1, max_lag + 1):
            if lag >= len(series):
                break
            
            # Autocorrelation calculation
            numerator = np.sum(series_centered[:-lag] * series_centered[lag:])
            denominator = np.sum(series_centered ** 2)
            
            if denominator > 0:
                autocorr = numerator / denominator
                autocorr_values.append((lag, autocorr))
        
        # Find peaks in autocorrelation
        threshold = 0.3  # Minimum autocorrelation for cycle detection
        
        for lag, autocorr in autocorr_values:
            if autocorr > threshold:
                confidence = min(autocorr, 0.95)
                cycles.append({
                    'period': lag,
                    'confidence': float(confidence),
                    'autocorr_value': float(autocorr)
                })
        
        # Sort by confidence
        cycles.sort(key=lambda x: x['confidence'], reverse=True)
        
    except Exception as e:
        logger.error(f"Error in cycle detection: {e}")
    
    return cycles[:5]  # Return top 5 cycles

def wilson_score_interval(successes: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate Wilson score confidence interval
    
    Args:
        successes: Number of successes
        total: Total number of trials
        confidence: Confidence level (0-1)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if total == 0:
        return (0.0, 0.0)
    
    from scipy import stats
    
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p = successes / total
    
    denominator = 1 + z**2 / total
    centre_adjusted_probability = (p + z**2 / (2 * total)) / denominator
    adjusted_standard_deviation = np.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denominator
    
    lower_bound = centre_adjusted_probability - z * adjusted_standard_deviation
    upper_bound = centre_adjusted_probability + z * adjusted_standard_deviation
    
    return (max(0.0, lower_bound), min(1.0, upper_bound))

def moving_average(data: List[float], window: int) -> List[float]:
    """
    Calculate moving average of data
    
    Args:
        data: Input data
        window: Moving window size
        
    Returns:
        List of moving averages
    """
    if len(data) < window:
        return data.copy()
    
    result = []
    for i in range(len(data)):
        if i < window - 1:
            # For initial values, use available data
            avg = np.mean(data[:i+1])
        else:
            # Moving average
            avg = np.mean(data[i-window+1:i+1])
        result.append(float(avg))
    
    return result

def trend_analysis(data: List[float], window: int = 7) -> Dict[str, float]:
    """
    Analyze trend in data
    
    Args:
        data: Time series data
        window: Window size for trend calculation
        
    Returns:
        Dictionary with trend metrics
    """
    if len(data) < 2:
        return {
            'trend_slope': 0.0,
            'trend_strength': 0.0,
            'trend_direction': 'stable'
        }
    
    # Calculate moving averages
    ma = moving_average(data, window)
    
    if len(ma) < 2:
        return {
            'trend_slope': 0.0,
            'trend_strength': 0.0,
            'trend_direction': 'stable'
        }
    
    # Linear regression on recent moving averages
    recent_ma = ma[-min(len(ma), window * 2):]
    x = np.arange(len(recent_ma))
    
    if len(recent_ma) >= 2:
        slope = np.polyfit(x, recent_ma, 1)[0]
        
        # R-squared for trend strength
        y_pred = np.polyval([slope, recent_ma[0]], x)
        ss_res = np.sum((recent_ma - y_pred) ** 2)
        ss_tot = np.sum((recent_ma - np.mean(recent_ma)) ** 2)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Determine direction
        if abs(slope) < 0.01:
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        return {
            'trend_slope': float(slope),
            'trend_strength': float(max(0, r_squared)),
            'trend_direction': direction
        }
    
    return {
        'trend_slope': 0.0,
        'trend_strength': 0.0,
        'trend_direction': 'stable'
    }