#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧮 ADVANCED MATHEMATICAL PROCESSORS: Multi-Resolution Analysis
Implements wavelet decomposition, fractal analysis, and chaos theory for lottery pattern detection
"""

import logging
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Scientific computing imports
try:
    import scipy.signal as signal
    import scipy.stats as stats
    from scipy.fft import fft, ifft

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy not available. Some advanced features will be disabled.")

try:
    import pywt  # PyWavelets for wavelet decomposition

    WAVELET_AVAILABLE = True
except ImportError:
    WAVELET_AVAILABLE = False
    logging.warning("PyWavelets not available. Wavelet decomposition disabled.")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WaveletAnalysisResult:
    """Result of wavelet decomposition analysis"""

    coefficients: Dict[str, np.ndarray]
    scales: List[float]
    frequencies: List[float]
    energy_distribution: Dict[str, float]
    dominant_scales: List[Tuple[float, float]]  # (scale, energy)


@dataclass(frozen=True)
class FractalAnalysisResult:
    """Result of fractal dimension analysis"""

    fractal_dimension: float
    correlation_dimension: float
    box_counting_dimension: float
    detrended_fluctuation_alpha: float
    complexity_measure: float


@dataclass(frozen=True)
class ChaosAnalysisResult:
    """Result of chaos theory analysis"""

    lyapunov_exponent: float
    correlation_dimension: float
    embedding_dimension: int
    entropy_measures: Dict[str, float]
    attractiveness_score: float
    predictability_horizon: int


class MathematicalProcessor(ABC):
    """Abstract base class for mathematical processors"""

    @abstractmethod
    def process(self, data: np.ndarray) -> Dict[str, Any]:
        """Process input data and return analysis results"""
        pass


class WaveletProcessor(MathematicalProcessor):
    """
    🌊 WAVELET DECOMPOSITION PROCESSOR
    Implements multi-scale wavelet analysis for temporal pattern detection
    """

    def __init__(self, wavelet="db4", levels=6):
        """
        Initialize wavelet processor

        Args:
            wavelet: Wavelet type ('db4', 'haar', 'coif2', etc.)
            levels: Number of decomposition levels
        """
        self.wavelet = wavelet
        self.levels = levels
        self.available = WAVELET_AVAILABLE

        if not self.available:
            logger.warning("Wavelet processor not available - PyWavelets not installed")

    def process(self, data: np.ndarray) -> WaveletAnalysisResult:
        """
        Perform wavelet decomposition analysis

        Args:
            data: Input time series data

        Returns:
            WaveletAnalysisResult with decomposition results
        """
        if not self.available:
            return self._fallback_analysis(data)

        try:
            # Perform discrete wavelet transform
            coeffs = pywt.wavedec(data, self.wavelet, level=self.levels)

            # Calculate scales and frequencies
            scales = self._calculate_scales(len(data))
            frequencies = self._calculate_frequencies(scales, len(data))

            # Calculate energy distribution
            energy_dist = self._calculate_energy_distribution(coeffs)

            # Find dominant scales
            dominant_scales = self._find_dominant_scales(coeffs, scales)

            # Package coefficients
            coeff_dict = {
                "approximation": coeffs[0],
                "details": {
                    f"level_{i}": coeffs[i + 1] for i in range(len(coeffs) - 1)
                },
            }

            return WaveletAnalysisResult(
                coefficients=coeff_dict,
                scales=scales,
                frequencies=frequencies,
                energy_distribution=energy_dist,
                dominant_scales=dominant_scales,
            )

        except Exception as e:
            logger.error(f"Wavelet analysis failed: {e}")
            return self._fallback_analysis(data)

    def _calculate_scales(self, data_length: int) -> List[float]:
        """Calculate wavelet scales"""
        return [2**i for i in range(1, self.levels + 1)]

    def _calculate_frequencies(
        self, scales: List[float], data_length: int
    ) -> List[float]:
        """Calculate corresponding frequencies for scales"""
        return [1.0 / scale for scale in scales]

    def _calculate_energy_distribution(
        self, coeffs: List[np.ndarray]
    ) -> Dict[str, float]:
        """Calculate energy distribution across scales"""
        total_energy = sum(np.sum(c**2) for c in coeffs)

        energy_dist = {"approximation": np.sum(coeffs[0] ** 2) / total_energy}

        for i, detail in enumerate(coeffs[1:]):
            energy_dist[f"detail_level_{i+1}"] = np.sum(detail**2) / total_energy

        return energy_dist

    def _find_dominant_scales(
        self, coeffs: List[np.ndarray], scales: List[float]
    ) -> List[Tuple[float, float]]:
        """Find scales with highest energy"""
        energies = [
            (scales[i] if i < len(scales) else 1.0, np.sum(c**2))
            for i, c in enumerate(coeffs[1:])
        ]
        return sorted(energies, key=lambda x: x[1], reverse=True)[:3]

    def _fallback_analysis(self, data: np.ndarray) -> WaveletAnalysisResult:
        """Fallback analysis when PyWavelets not available"""
        logger.info("Using fallback wavelet analysis")

        # Simple multi-scale analysis using moving averages
        scales = [2, 4, 8, 16, 32, 64]
        coeffs = {}

        for scale in scales:
            if scale < len(data):
                # Simple smoothing as approximation
                smoothed = np.convolve(data, np.ones(scale) / scale, mode="same")
                coeffs[f"scale_{scale}"] = smoothed

        return WaveletAnalysisResult(
            coefficients=coeffs,
            scales=scales,
            frequencies=[1.0 / s for s in scales],
            energy_distribution={"fallback": 1.0},
            dominant_scales=[(scales[0], 1.0)],
        )


class FractalProcessor(MathematicalProcessor):
    """
    📐 FRACTAL DIMENSION PROCESSOR
    Implements multiple fractal dimension calculation methods
    """

    def __init__(self):
        self.available = SCIPY_AVAILABLE

        if not self.available:
            logger.warning("Fractal processor limited - SciPy not available")

    def process(self, data: np.ndarray) -> FractalAnalysisResult:
        """
        Perform fractal dimension analysis

        Args:
            data: Input time series data

        Returns:
            FractalAnalysisResult with fractal measures
        """
        try:
            # Ensure data is numpy array
            if not isinstance(data, np.ndarray):
                data = np.array(data, dtype=float)
            
            # Calculate multiple fractal dimensions
            fractal_dim = self._box_counting_dimension(data)
            correlation_dim = self._correlation_dimension(data)
            box_counting_dim = self._improved_box_counting(data)
            dfa_alpha = self._detrended_fluctuation_analysis(data)
            complexity = self._complexity_measure(data)

            return FractalAnalysisResult(
                fractal_dimension=fractal_dim,
                correlation_dimension=correlation_dim,
                box_counting_dimension=box_counting_dim,
                detrended_fluctuation_alpha=dfa_alpha,
                complexity_measure=complexity,
            )

        except Exception as e:
            logger.error(f"Fractal analysis failed: {e}")
            return self._fallback_fractal_analysis(data)

    def _box_counting_dimension(self, data: np.ndarray) -> float:
        """Calculate box-counting fractal dimension"""
        # Ensure data is numpy array
        if not isinstance(data, np.ndarray):
            data = np.array(data, dtype=float)
            
        # Convert to 2D trajectory for box counting
        trajectory = np.column_stack((np.arange(len(data)), data))

        # Different box sizes - Fix comparison issue
        x_range = float(np.ptp(trajectory[:, 0]))
        y_range = float(np.ptp(trajectory[:, 1]))
        max_range = max(x_range, y_range)
        box_sizes = np.logspace(-2, 0, 20) * max_range
        box_counts = []

        for box_size in box_sizes:
            # Count boxes needed to cover the trajectory
            x_bins = int(np.ceil(np.ptp(trajectory[:, 0]) / box_size))
            y_bins = int(np.ceil(np.ptp(trajectory[:, 1]) / box_size))

            # Create grid
            x_min, y_min = trajectory.min(axis=0)

            # Count occupied boxes
            occupied_boxes = set()
            for x, y in trajectory:
                box_x = int((x - x_min) / box_size)
                box_y = int((y - y_min) / box_size)
                occupied_boxes.add((box_x, box_y))

            box_counts.append(len(occupied_boxes))

        # Linear regression on log-log plot
        log_sizes = np.log(box_sizes)
        log_counts = np.log(box_counts)

        # Filter out invalid values
        valid_idx = np.isfinite(log_sizes) & np.isfinite(log_counts)
        if np.sum(valid_idx) < 3:
            return 1.5  # Default fractal dimension

        slope, _ = np.polyfit(log_sizes[valid_idx], log_counts[valid_idx], 1)
        return -slope

    def _correlation_dimension(self, data: np.ndarray) -> float:
        """Calculate correlation dimension"""
        # Embed the time series in higher dimensions
        embedding_dim = min(5, len(data) // 10)
        embedded = self._embed_time_series(data, embedding_dim)

        # Calculate correlation sum for different radii
        radii = np.logspace(-2, 0, 15) * np.std(data)
        correlation_sums = []

        n_points = len(embedded)
        for radius in radii:
            count = 0
            for i in range(n_points):
                for j in range(i + 1, n_points):
                    if np.linalg.norm(embedded[i] - embedded[j]) < radius:
                        count += 1

            correlation_sums.append(count / (n_points * (n_points - 1) / 2))

        # Linear regression on log-log plot
        log_radii = np.log(radii)
        log_sums = np.log(np.array(correlation_sums) + 1e-10)  # Avoid log(0)

        valid_idx = (
            np.isfinite(log_radii) & np.isfinite(log_sums) & (np.array(correlation_sums) > 0)
        )
        if np.sum(valid_idx) < 3:
            return 1.0  # Default correlation dimension

        slope, _ = np.polyfit(log_radii[valid_idx], log_sums[valid_idx], 1)
        return max(0.1, slope)  # Ensure positive dimension

    def _improved_box_counting(self, data: np.ndarray) -> float:
        """Improved box counting with better scaling"""
        # Normalize data
        normalized_data = (data - np.min(data)) / (np.max(data) - np.min(data))

        # Create 2D representation
        points = np.column_stack((np.linspace(0, 1, len(data)), normalized_data))

        # Different grid resolutions
        resolutions = [2**i for i in range(3, 8)]
        box_counts = []

        for resolution in resolutions:
            grid_size = 1.0 / resolution
            occupied_boxes = set()

            for x, y in points:
                box_x = int(x / grid_size)
                box_y = int(y / grid_size)
                occupied_boxes.add((box_x, box_y))

            box_counts.append(len(occupied_boxes))

        # Calculate dimension from scaling
        log_resolutions = np.log(resolutions)
        log_counts = np.log(box_counts)

        slope, _ = np.polyfit(log_resolutions, log_counts, 1)
        return abs(slope)

    def _detrended_fluctuation_analysis(self, data: np.ndarray) -> float:
        """Detrended Fluctuation Analysis (DFA)"""
        if len(data) < 20:
            return 0.5  # Default for insufficient data
            
        # Convert to cumulative sum
        cumsum = np.cumsum(data - np.mean(data))

        # Different window sizes with validation
        max_window = max(4, len(data) // 4)
        if max_window < 4:
            return 0.5
            
        window_sizes = np.logspace(1, np.log10(max_window), 10).astype(int)
        window_sizes = np.unique(window_sizes)  # Remove duplicates
        window_sizes = window_sizes[window_sizes >= 4]  # Minimum window size
        
        if len(window_sizes) < 3:
            return 0.5
            
        fluctuations = []

        for window_size in window_sizes:
            if window_size > len(cumsum):
                continue
                
            # Divide into non-overlapping windows
            n_windows = len(cumsum) // int(window_size)
            if n_windows < 1:
                continue
                
            windows = cumsum[: n_windows * int(window_size)].reshape(n_windows, int(window_size))

            # Detrend each window
            window_fluctuations = []
            for window in windows:
                # Linear detrending
                x = np.arange(len(window))
                coeffs = np.polyfit(x, window, 1)
                trend = np.polyval(coeffs, x)
                detrended = window - trend
                window_fluctuations.append(np.sqrt(np.mean(detrended**2)))

            if window_fluctuations:
                fluctuations.append(np.mean(window_fluctuations))

        if len(fluctuations) < 3:
            return 0.5

        # Calculate scaling exponent
        log_sizes = np.log(window_sizes[:len(fluctuations)])
        log_fluctuations = np.log(fluctuations)

        valid_idx = np.isfinite(log_sizes) & np.isfinite(log_fluctuations)
        if np.sum(valid_idx) < 3:
            return 0.5  # Default DFA exponent

        alpha, _ = np.polyfit(log_sizes[valid_idx], log_fluctuations[valid_idx], 1)
        return alpha

    def _complexity_measure(self, data: np.ndarray) -> float:
        """Calculate complexity measure based on entropy and variance"""
        # Normalize data
        normalized = (data - np.mean(data)) / (np.std(data) + 1e-10)

        # Calculate approximate entropy
        m = 2  # pattern length
        r = 0.2 * np.std(normalized)  # tolerance

        def _maxdist(xi, xj, m):
            try:
                distances = [abs(float(ua) - float(va)) for ua, va in zip(xi[0:m], xj[0:m])]
                return max(distances) if distances else 0.0
            except (TypeError, ValueError):
                return 0.0

        def _phi(m):
            patterns = np.array(
                [normalized[i : i + m] for i in range(len(normalized) - m + 1)]
            )
            C = np.zeros(len(normalized) - m + 1)

            for i in range(len(normalized) - m + 1):
                template_i = patterns[i]
                for j in range(len(normalized) - m + 1):
                    if _maxdist(template_i, patterns[j], m) <= r:
                        C[i] += 1.0

            C = C / float(len(normalized) - m + 1.0)
            phi = np.mean(np.log(C + 1e-10))
            return phi

        complexity = _phi(m) - _phi(m + 1)
        return max(0, complexity)

    def _embed_time_series(
        self, data: np.ndarray, embedding_dim: int, delay: int = 1
    ) -> np.ndarray:
        """Embed time series in higher dimensional space"""
        n_points = len(data) - (embedding_dim - 1) * delay
        embedded = np.zeros((n_points, embedding_dim))

        for i in range(embedding_dim):
            embedded[:, i] = data[i * delay : i * delay + n_points]

        return embedded

    def _fallback_fractal_analysis(self, data: np.ndarray) -> FractalAnalysisResult:
        """Fallback fractal analysis"""
        # Simple measures
        variance_ratio = np.var(data) / (np.mean(data) + 1e-10)

        return FractalAnalysisResult(
            fractal_dimension=1.5,
            correlation_dimension=1.0,
            box_counting_dimension=1.2,
            detrended_fluctuation_alpha=0.5,
            complexity_measure=variance_ratio,
        )


class ChaosProcessor(MathematicalProcessor):
    """
    🌀 CHAOS THEORY PROCESSOR
    Implements chaos theory analysis for nonlinear dynamics detection
    """

    def __init__(self):
        self.available = SCIPY_AVAILABLE

        if not self.available:
            logger.warning("Chaos processor limited - SciPy not available")

    def process(self, data: np.ndarray) -> ChaosAnalysisResult:
        """
        Perform chaos theory analysis

        Args:
            data: Input time series data

        Returns:
            ChaosAnalysisResult with chaos measures
        """
        try:
            # Ensure data is numpy array
            if not isinstance(data, np.ndarray):
                data = np.array(data, dtype=float)
            
            # Calculate chaos theory measures
            lyapunov = self._largest_lyapunov_exponent(data)
            correlation_dim = self._correlation_dimension_chaos(data)
            embedding_dim = self._optimal_embedding_dimension(data)
            entropy_measures = self._entropy_measures(data)
            attractiveness = self._attractiveness_score(data)
            predictability = self._predictability_horizon(data, lyapunov)

            return ChaosAnalysisResult(
                lyapunov_exponent=lyapunov,
                correlation_dimension=correlation_dim,
                embedding_dimension=embedding_dim,
                entropy_measures=entropy_measures,
                attractiveness_score=attractiveness,
                predictability_horizon=predictability,
            )

        except Exception as e:
            logger.error(f"Chaos analysis failed: {e}")
            return self._fallback_chaos_analysis(data)

    def _largest_lyapunov_exponent(self, data: np.ndarray) -> float:
        """Calculate largest Lyapunov exponent"""
        # Embed the time series
        embedding_dim = min(5, len(data) // 20)
        embedded = self._embed_time_series(data, embedding_dim)

        # Find nearest neighbors and track divergence
        divergences = []
        min_separation = float(np.std(data) * 0.01)

        for i in range(len(embedded) - 10):
            # Find nearest neighbor
            distances = [
                float(np.linalg.norm(embedded[i] - embedded[j]))
                for j in range(len(embedded))
                if abs(i - j) > 10
            ]

            if not distances:
                continue

            nearest_idx = np.argmin(distances)
            if nearest_idx >= len(embedded) - 10:
                continue

            initial_distance = float(distances[nearest_idx])
            if initial_distance < min_separation:
                continue

            # Track divergence over time
            local_divergences = []
            for k in range(1, min(10, len(embedded) - max(i, nearest_idx))):
                if i + k < len(embedded) and nearest_idx + k < len(embedded):
                    future_distance = np.linalg.norm(
                        embedded[i + k] - embedded[nearest_idx + k]
                    )
                    if future_distance > 0 and initial_distance > 0:
                        divergence = np.log(future_distance / initial_distance) / k
                        local_divergences.append(divergence)

            if local_divergences:
                divergences.extend(local_divergences)

        return np.mean(divergences) if divergences else 0.0

    def _correlation_dimension_chaos(self, data: np.ndarray) -> float:
        """Calculate correlation dimension for chaos analysis"""
        # Similar to fractal correlation dimension but optimized for chaos
        embedding_dim = min(3, len(data) // 15)
        embedded = self._embed_time_series(data, embedding_dim)

        # Calculate correlation sum
        data_std = np.std(data)
        radii = np.logspace(-2, 0, 10) * data_std
        correlation_sums = []

        n_points = min(len(embedded), 200)  # Limit for performance
        embedded_sample = embedded[:n_points]

        for radius in radii:
            count = 0
            for i in range(n_points):
                for j in range(i + 1, n_points):
                    if np.linalg.norm(embedded_sample[i] - embedded_sample[j]) < radius:
                        count += 1

            correlation_sums.append(count / (n_points * (n_points - 1) / 2))

        # Find scaling region
        log_radii = np.log(radii)
        log_sums = np.log(np.array(correlation_sums) + 1e-12)

        valid_idx = (
            np.isfinite(log_radii) & np.isfinite(log_sums) & (np.array(correlation_sums) > 1e-10)
        )
        if np.sum(valid_idx) >= 3:
            slope, _ = np.polyfit(log_radii[valid_idx], log_sums[valid_idx], 1)
            return max(0.1, slope)

        return 1.0

    def _optimal_embedding_dimension(self, data: np.ndarray) -> int:
        """Determine optimal embedding dimension using false nearest neighbors"""
        max_dim = min(10, len(data) // 20)

        for m in range(1, max_dim + 1):
            embedded_m = self._embed_time_series(data, m)
            embedded_m1 = self._embed_time_series(data, m + 1)

            if len(embedded_m) < 10 or len(embedded_m1) < 10:
                return m

            # Calculate false nearest neighbors
            false_neighbors = 0
            total_neighbors = 0

            for i in range(min(50, len(embedded_m))):  # Sample for performance
                # Find nearest neighbor in m-dimensional space
                distances_m = [
                    np.linalg.norm(embedded_m[i] - embedded_m[j])
                    for j in range(len(embedded_m))
                    if j != i
                ]

                if not distances_m:
                    continue

                nearest_idx = np.argmin(distances_m)
                nearest_distance_m = distances_m[nearest_idx]

                # Check in (m+1)-dimensional space
                if nearest_idx < len(embedded_m1) and i < len(embedded_m1):
                    distance_m1 = np.linalg.norm(
                        embedded_m1[i] - embedded_m1[nearest_idx]
                    )

                    # Check if it's a false neighbor
                    if nearest_distance_m > 0:
                        ratio = (
                            abs(distance_m1 - nearest_distance_m) / nearest_distance_m
                        )
                        if ratio > 2.0:  # Threshold for false neighbor
                            false_neighbors += 1

                    total_neighbors += 1

            # If false neighbor percentage is low, we found optimal dimension
            if total_neighbors > 0:
                false_ratio = false_neighbors / total_neighbors
                if false_ratio < 0.1:  # Less than 10% false neighbors
                    return m

        return max_dim

    def _entropy_measures(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate various entropy measures"""
        measures = {}

        # Shannon entropy
        hist, _ = np.histogram(data, bins=min(50, len(data) // 5), density=True)
        hist = hist[hist > 0]  # Remove zero bins
        measures["shannon"] = -np.sum(hist * np.log2(hist)) if len(hist) > 0 else 0.0

        # Sample entropy
        measures["sample"] = self._sample_entropy(data)

        # Permutation entropy
        measures["permutation"] = self._permutation_entropy(data)

        return measures

    def _sample_entropy(
        self, data: np.ndarray, m: int = 2, r: Optional[float] = None
    ) -> float:
        """Calculate sample entropy"""
        if r is None:
            r = 0.2 * np.std(data)

        def _maxdist(xi, xj, m):
            try:
                distances = [abs(float(ua) - float(va)) for ua, va in zip(xi[0:m], xj[0:m])]
                return max(distances) if distances else 0.0
            except (TypeError, ValueError):
                return 0.0

        def _phi(m):
            patterns = np.array([data[i : i + m] for i in range(len(data) - m + 1)])
            C = 0

            for i in range(len(data) - m + 1):
                template_i = patterns[i]
                for j in range(len(data) - m + 1):
                    if i != j and _maxdist(template_i, patterns[j], m) <= r:
                        C += 1

            return C / float((len(data) - m + 1) * (len(data) - m))

        phi_m = _phi(m)
        phi_m1 = _phi(m + 1)

        if phi_m == 0 or phi_m1 == 0:
            return 0.0

        return -np.log(phi_m1 / phi_m)

    def _permutation_entropy(self, data: np.ndarray, order: int = 3) -> float:
        """Calculate permutation entropy"""
        # Create ordinal patterns
        patterns = []
        for i in range(len(data) - order + 1):
            pattern = data[i : i + order]
            # Get permutation pattern
            sorted_indices = np.argsort(pattern)
            ordinal_pattern = tuple(np.argsort(sorted_indices))
            patterns.append(ordinal_pattern)

        # Count pattern frequencies
        from collections import Counter

        pattern_counts = Counter(patterns)

        # Calculate entropy
        total_patterns = len(patterns)
        entropy = 0.0
        for count in pattern_counts.values():
            prob = count / total_patterns
            entropy -= prob * np.log2(prob)

        # Normalize by maximum possible entropy
        max_entropy = np.log2(math.factorial(order))
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _attractiveness_score(self, data: np.ndarray) -> float:
        """Calculate attractiveness score of the attractor"""
        # Measure how concentrated the trajectory is
        embedding_dim = min(3, len(data) // 10)
        embedded = self._embed_time_series(data, embedding_dim)

        # Calculate center of mass
        center = np.mean(embedded, axis=0)

        # Calculate distances from center
        distances = [np.linalg.norm(point - center) for point in embedded]

        # Attractiveness inversely related to spread
        spread = np.std(distances)
        mean_distance = np.mean(distances)

        if mean_distance > 0:
            attractiveness = 1.0 / (1.0 + spread / mean_distance)
        else:
            attractiveness = 1.0

        return attractiveness

    def _predictability_horizon(self, data: np.ndarray, lyapunov: float) -> int:
        """Estimate predictability horizon based on Lyapunov exponent"""
        if lyapunov <= 0:
            return len(data)  # Very predictable

        # Time to lose one bit of information
        sampling_rate = 1.0  # Assume unit sampling rate
        horizon = np.log(2) / (lyapunov * sampling_rate)

        # Convert to time steps and bound reasonably
        horizon_steps = int(horizon)
        return max(1, min(horizon_steps, len(data) // 2))

    def _embed_time_series(
        self, data: np.ndarray, embedding_dim: int, delay: int = 1
    ) -> np.ndarray:
        """Embed time series in higher dimensional space"""
        n_points = len(data) - (embedding_dim - 1) * delay
        if n_points <= 0:
            return np.array([])

        embedded = np.zeros((n_points, embedding_dim))
        for i in range(embedding_dim):
            embedded[:, i] = data[i * delay : i * delay + n_points]

        return embedded

    def _fallback_chaos_analysis(self, data: np.ndarray) -> ChaosAnalysisResult:
        """Fallback chaos analysis"""
        return ChaosAnalysisResult(
            lyapunov_exponent=0.0,
            correlation_dimension=1.0,
            embedding_dimension=2,
            entropy_measures={"shannon": 1.0, "sample": 0.5, "permutation": 0.5},
            attractiveness_score=0.5,
            predictability_horizon=len(data) // 4,
        )


class AdvancedMathProcessor:
    """
    🧮 ADVANCED MATHEMATICAL PROCESSOR
    Orchestrates all mathematical analysis components
    """

    def __init__(self):
        """Initialize all mathematical processors"""
        self.wavelet_processor = WaveletProcessor()
        self.fractal_processor = FractalProcessor()
        self.chaos_processor = ChaosProcessor()

        logger.info("Advanced Mathematical Processor initialized")

    def analyze_lottery_sequence(self, lottery_numbers: List[int]) -> Dict[str, Any]:
        """
        Comprehensive mathematical analysis of lottery number sequence

        Args:
            lottery_numbers: List of lottery numbers

        Returns:
            Comprehensive analysis results
        """
        # Convert to numpy array
        data = np.array(lottery_numbers, dtype=float)

        if len(data) < 10:
            logger.warning("Insufficient data for comprehensive analysis")
            return self._minimal_analysis(data)

        logger.info(f"Analyzing sequence of {len(data)} lottery numbers")

        results = {
            "data_info": {
                "length": len(data),
                "mean": np.mean(data),
                "std": np.std(data),
                "min": np.min(data),
                "max": np.max(data),
                "range": np.ptp(data),
            }
        }

        # Wavelet analysis
        try:
            wavelet_result = self.wavelet_processor.process(data)
            results["wavelet_analysis"] = {
                "scales": wavelet_result.scales,
                "frequencies": wavelet_result.frequencies,
                "energy_distribution": wavelet_result.energy_distribution,
                "dominant_scales": wavelet_result.dominant_scales,
            }
        except Exception as e:
            logger.error(f"Wavelet analysis failed: {e}")
            results["wavelet_analysis"] = {"error": str(e)}

        # Fractal analysis
        try:
            fractal_result = self.fractal_processor.process(data)
            results["fractal_analysis"] = {
                "fractal_dimension": fractal_result.fractal_dimension,
                "correlation_dimension": fractal_result.correlation_dimension,
                "box_counting_dimension": fractal_result.box_counting_dimension,
                "dfa_alpha": fractal_result.detrended_fluctuation_alpha,
                "complexity_measure": fractal_result.complexity_measure,
            }
        except Exception as e:
            logger.error(f"Fractal analysis failed: {e}")
            results["fractal_analysis"] = {"error": str(e)}

        # Chaos analysis
        try:
            chaos_result = self.chaos_processor.process(data)
            results["chaos_analysis"] = {
                "lyapunov_exponent": chaos_result.lyapunov_exponent,
                "correlation_dimension": chaos_result.correlation_dimension,
                "embedding_dimension": chaos_result.embedding_dimension,
                "entropy_measures": chaos_result.entropy_measures,
                "attractiveness_score": chaos_result.attractiveness_score,
                "predictability_horizon": chaos_result.predictability_horizon,
            }
        except Exception as e:
            logger.error(f"Chaos analysis failed: {e}")
            results["chaos_analysis"] = {"error": str(e)}

        # Summary insights
        results["insights"] = self._generate_insights(results)

        return results

    def _minimal_analysis(self, data: np.ndarray) -> Dict[str, Any]:
        """Minimal analysis for insufficient data"""
        return {
            "data_info": {
                "length": len(data),
                "mean": np.mean(data) if len(data) > 0 else 0,
                "std": np.std(data) if len(data) > 1 else 0,
                "warning": "Insufficient data for comprehensive analysis",
            },
            "insights": {"reliability": "low", "recommendation": "collect_more_data"},
        }

    def _generate_insights(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from analysis results"""
        insights = {
            "complexity_level": "unknown",
            "predictability": "unknown",
            "pattern_strength": "unknown",
            "recommendations": [],
        }

        # Analyze complexity
        if "fractal_analysis" in results and "error" not in results["fractal_analysis"]:
            fractal_dim = results["fractal_analysis"].get("fractal_dimension", 1.5)
            if fractal_dim > 1.7:
                insights["complexity_level"] = "high"
            elif fractal_dim > 1.3:
                insights["complexity_level"] = "medium"
            else:
                insights["complexity_level"] = "low"

        # Analyze predictability
        if "chaos_analysis" in results and "error" not in results["chaos_analysis"]:
            lyapunov = results["chaos_analysis"].get("lyapunov_exponent", 0)
            horizon = results["chaos_analysis"].get("predictability_horizon", 0)

            if lyapunov > 0.1:
                insights["predictability"] = "chaotic"
                insights["recommendations"].append("use_ensemble_methods")
            elif horizon > 10:
                insights["predictability"] = "short_term"
                insights["recommendations"].append("focus_on_recent_patterns")
            else:
                insights["predictability"] = "highly_predictable"
                insights["recommendations"].append("use_simple_models")

        # Analyze pattern strength
        if "wavelet_analysis" in results and "error" not in results["wavelet_analysis"]:
            energy_dist = results["wavelet_analysis"].get("energy_distribution", {})
            dominant_energy = max(energy_dist.values()) if energy_dist else 0

            if dominant_energy > 0.6:
                insights["pattern_strength"] = "strong"
                insights["recommendations"].append("exploit_dominant_patterns")
            elif dominant_energy > 0.3:
                insights["pattern_strength"] = "moderate"
                insights["recommendations"].append("combine_multiple_scales")
            else:
                insights["pattern_strength"] = "weak"
                insights["recommendations"].append("use_adaptive_methods")

        return insights


# Factory function for easy instantiation
def create_math_processor() -> AdvancedMathProcessor:
    """Create and return an AdvancedMathProcessor instance"""
    return AdvancedMathProcessor()


# Example usage and testing
if __name__ == "__main__":
    # Test with sample lottery data
    sample_data = [
        12,
        25,
        34,
        8,
        41,
        17,
        29,
        3,
        36,
        22,
        15,
        38,
        7,
        43,
        19,
        31,
        4,
        26,
        39,
        14,
    ]

    processor = create_math_processor()
    results = processor.analyze_lottery_sequence(sample_data)

    print("🧮 Advanced Mathematical Analysis Results:")
    print(f"Data length: {results['data_info']['length']}")
    print(f"Complexity level: {results['insights']['complexity_level']}")
    print(f"Predictability: {results['insights']['predictability']}")
    print(f"Pattern strength: {results['insights']['pattern_strength']}")
    print(f"Recommendations: {', '.join(results['insights']['recommendations'])}")
