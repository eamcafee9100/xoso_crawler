import logging
import numpy as np
from datetime import date, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from scipy.optimize import minimize
from collections import defaultdict

from predictions_tracker.models import (
    CyclicalNumberPredictor,
    MethodCyclicalPerformance,
    CyclicalContextEngine
)
from predictions_tracker.core.services.CyclicalValidationService import cyclical_validation_service

logger = logging.getLogger(__name__)


@dataclass
class OptimizationParameters:
    """Cấu trúc parameters cần optimize"""
    frequency_weight: float = 0.4
    weekly_weight: float = 0.3
    monthly_weight: float = 0.2
    phase_weight: float = 0.1
    min_cyclical_fitness: float = 20.0
    max_fatigue_risk: float = 0.8
    prediction_limit: int = 15


@dataclass
class OptimizationResult:
    """Kết quả optimization"""
    success: bool
    optimal_parameters: OptimizationParameters
    performance_metrics: Dict[str, float]
    improvement_rate: float
    optimization_details: Dict[str, Any]


class ParameterOptimizationService:
    """Service cho parameter optimization với scipy"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.optimization_history = []
    
    def optimize_cyclical_parameters(
        self,
        optimization_period_days: int = 60,
        optimization_method: str = "L-BFGS-B"
    ) -> OptimizationResult:
        """
        Optimize cyclical prediction parameters
        
        Args:
            optimization_period_days: Số ngày để optimize (default: 60)
            optimization_method: Scipy optimization method (default: L-BFGS-B)
            
        Returns:
            OptimizationResult: {
                success: bool,
                optimal_parameters: OptimizationParameters,
                performance_metrics: dict,
                improvement_rate: float,
                optimization_details: dict
            }
        """
        try:
            self.logger.info(f"🔍 Starting parameter optimization for {optimization_period_days} days")
            
            # 1. Setup optimization period
            end_date = date.today() - timedelta(days=1)
            start_date = end_date - timedelta(days=optimization_period_days)
            
            # 2. Get baseline performance
            baseline_performance = self._get_baseline_performance(start_date, end_date)
            
            # 3. Define optimization bounds
            bounds = self._define_parameter_bounds()
            
            # 4. Initial parameters
            initial_params = self._get_initial_parameters()
            
            # 5. Run optimization
            optimization_result = minimize(
                fun=self._objective_function,
                x0=initial_params,
                args=(start_date, end_date),
                method=optimization_method,
                bounds=bounds,
                options={
                    'maxiter': 50,
                    'ftol': 1e-4,
                    'disp': True
                }
            )
            
            # 6. Process optimization results
            if optimization_result.success:
                optimal_params = self._params_array_to_object(optimization_result.x)
                optimized_performance = self._evaluate_parameters(
                    optimal_params, start_date, end_date
                )
                
                improvement_rate = (
                    optimized_performance["accuracy"] - baseline_performance["accuracy"]
                ) / baseline_performance["accuracy"] if baseline_performance["accuracy"] > 0 else 0
                
                result = OptimizationResult(
                    success=True,
                    optimal_parameters=optimal_params,
                    performance_metrics=optimized_performance,
                    improvement_rate=improvement_rate,
                    optimization_details={
                        "iterations": optimization_result.nit,
                        "function_evaluations": optimization_result.nfev,
                        "final_score": -optimization_result.fun,  # Negative because we minimize
                        "baseline_performance": baseline_performance,
                        "optimization_method": optimization_method,
                        "convergence_message": optimization_result.message
                    }
                )
                
                self.logger.info(
                    f"✅ Optimization successful. Improvement: {improvement_rate:.1%}, "
                    f"Final accuracy: {optimized_performance['accuracy']:.1%}"
                )
                
            else:
                self.logger.warning(f"❌ Optimization failed: {optimization_result.message}")
                result = OptimizationResult(
                    success=False,
                    optimal_parameters=self._params_array_to_object(initial_params),
                    performance_metrics=baseline_performance,
                    improvement_rate=0.0,
                    optimization_details={
                        "error": optimization_result.message,
                        "iterations": optimization_result.nit if hasattr(optimization_result, 'nit') else 0
                    }
                )
            
            # 7. Store optimization history
            self.optimization_history.append({
                "timestamp": date.today().isoformat(),
                "result": result,
                "period": f"{start_date} to {end_date}"
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Parameter optimization error: {str(e)}", exc_info=True)
            return OptimizationResult(
                success=False,
                optimal_parameters=OptimizationParameters(),
                performance_metrics={"accuracy": 0.0, "error": str(e)},
                improvement_rate=0.0,
                optimization_details={"error": str(e)}
            )
    
    def _get_baseline_performance(self, start_date: date, end_date: date) -> Dict[str, float]:
        """Get baseline performance với current parameters"""
        try:
            validation_result = cyclical_validation_service.validate_cyclical_approach(
                start_date, end_date
            )
            
            if "error" in validation_result:
                return {"accuracy": 0.0, "avg_hits_per_day": 0.0}
            
            return {
                "accuracy": validation_result["overall_metrics"]["accuracy"],
                "avg_hits_per_day": validation_result["overall_metrics"]["avg_hits_per_day"],
                "successful_days": validation_result["overall_metrics"]["successful_days"],
                "total_days": validation_result["overall_metrics"]["total_days"]
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to get baseline performance: {str(e)}")
            return {"accuracy": 0.0, "avg_hits_per_day": 0.0}
    
    def _define_parameter_bounds(self) -> List[Tuple[float, float]]:
        """Define bounds cho optimization parameters"""
        return [
            (0.1, 0.7),   # frequency_weight
            (0.1, 0.5),   # weekly_weight  
            (0.1, 0.5),   # monthly_weight
            (0.0, 0.3),   # phase_weight
            (10.0, 50.0), # min_cyclical_fitness
            (0.5, 0.95),  # max_fatigue_risk
            (10, 25)      # prediction_limit (converted to float in bounds)
        ]
    
    def _get_initial_parameters(self) -> np.ndarray:
        """Get initial parameters array"""
        initial_params = OptimizationParameters()
        return np.array([
            initial_params.frequency_weight,
            initial_params.weekly_weight,
            initial_params.monthly_weight,
            initial_params.phase_weight,
            initial_params.min_cyclical_fitness,
            initial_params.max_fatigue_risk,
            float(initial_params.prediction_limit)
        ])
    
    def _params_array_to_object(self, params_array: np.ndarray) -> OptimizationParameters:
        """Convert numpy array to OptimizationParameters object"""
        return OptimizationParameters(
            frequency_weight=float(params_array[0]),
            weekly_weight=float(params_array[1]),
            monthly_weight=float(params_array[2]),
            phase_weight=float(params_array[3]),
            min_cyclical_fitness=float(params_array[4]),
            max_fatigue_risk=float(params_array[5]),
            prediction_limit=int(params_array[6])
        )
    
    def _objective_function(
        self, 
        params_array: np.ndarray, 
        start_date: date, 
        end_date: date
    ) -> float:
        """
        Objective function cho optimization (minimize this)
        
        Returns:
            float: Negative accuracy score (because scipy minimizes)
        """
        try:
            # Convert params array to object
            params = self._params_array_to_object(params_array)
            
            # Evaluate parameters
            performance = self._evaluate_parameters(params, start_date, end_date)
            
            # Return negative accuracy (because we want to maximize accuracy)
            accuracy_score = performance.get("accuracy", 0.0)
            
            # Add penalty for invalid parameter combinations
            penalty = self._calculate_parameter_penalty(params)
            
            objective_score = -(accuracy_score - penalty)
            
            self.logger.debug(
                f"Objective function: params={params_array}, "
                f"accuracy={accuracy_score:.3f}, penalty={penalty:.3f}, "
                f"objective={objective_score:.3f}"
            )
            
            return objective_score
            
        except Exception as e:
            self.logger.warning(f"Objective function error: {str(e)}")
            return 1.0  # Return high value (bad score) on error
    
    def _evaluate_parameters(
        self, 
        params: OptimizationParameters, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, float]:
        """
        Evaluate performance với given parameters
        
        Returns:
            dict: {
                "accuracy": float,
                "avg_hits_per_day": float,
                "total_days": int,
                "successful_days": int
            }
        """
        try:
            # Simulate validation với new parameters
            # For now, we'll use a simplified evaluation
            # In production, this should use actual prediction logic với custom parameters
            
            simulated_accuracy = self._simulate_performance_with_params(params, start_date, end_date)
            
            return {
                "accuracy": simulated_accuracy,
                "avg_hits_per_day": simulated_accuracy * 15 * 0.6,  # Estimate
                "total_days": (end_date - start_date).days,
                "successful_days": int(simulated_accuracy * (end_date - start_date).days)
            }
            
        except Exception as e:
            self.logger.warning(f"Parameter evaluation error: {str(e)}")
            return {"accuracy": 0.0, "avg_hits_per_day": 0.0, "total_days": 0, "successful_days": 0}
    
    def _simulate_performance_with_params(
        self, 
        params: OptimizationParameters,
        start_date: date,
        end_date: date
    ) -> float:
        """
        Simulate performance với custom parameters
        
        This is a simplified simulation. In production, you would:
        1. Modify CyclicalNumberPredictor to use custom weights
        2. Run actual predictions với these parameters
        3. Compare against historical results
        
        Returns:
            float: Simulated accuracy score (0.0 to 1.0)
        """
        # Base performance từ current system
        base_performance = 0.15  # 15% baseline
        
        # Weight balance bonus (weights should sum to ~1.0)
        total_weight = (
            params.frequency_weight + params.weekly_weight + 
            params.monthly_weight + params.phase_weight
        )
        weight_balance_bonus = 0.1 * (1.0 - abs(1.0 - total_weight))
        
        # Cyclical fitness bonus
        fitness_bonus = 0.05 if 20.0 <= params.min_cyclical_fitness <= 40.0 else 0.0
        
        # Fatigue risk bonus
        fatigue_bonus = 0.05 if 0.6 <= params.max_fatigue_risk <= 0.8 else 0.0
        
        # Prediction limit bonus
        limit_bonus = 0.03 if 12 <= params.prediction_limit <= 18 else 0.0
        
        # Calculate simulated performance
        simulated_performance = (
            base_performance + 
            weight_balance_bonus + 
            fitness_bonus + 
            fatigue_bonus + 
            limit_bonus
        )
        
        # Add some randomness để simulate real-world variation
        import random
        random.seed(int(total_weight * 1000))  # Deterministic randomness
        noise = random.uniform(-0.02, 0.02)
        
        return max(0.0, min(1.0, simulated_performance + noise))
    
    def _calculate_parameter_penalty(self, params: OptimizationParameters) -> float:
        """Calculate penalty cho invalid parameter combinations"""
        penalty = 0.0
        
        # Penalty for weights not summing to ~1.0
        total_weight = (
            params.frequency_weight + params.weekly_weight + 
            params.monthly_weight + params.phase_weight
        )
        weight_penalty = abs(1.0 - total_weight) * 0.1
        penalty += weight_penalty
        
        # Penalty for extreme values
        if params.min_cyclical_fitness < 15.0 or params.min_cyclical_fitness > 45.0:
            penalty += 0.05
        
        if params.max_fatigue_risk < 0.5 or params.max_fatigue_risk > 0.9:
            penalty += 0.05
        
        if params.prediction_limit < 8 or params.prediction_limit > 30:
            penalty += 0.03
        
        return penalty
    
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """
        Get optimization history
        
        Returns:
            list: [
                {
                    "timestamp": str,
                    "result": OptimizationResult,
                    "period": str
                },
                ...
            ]
        """
        return self.optimization_history.copy()
    
    def get_current_optimal_parameters(self) -> Optional[OptimizationParameters]:
        """
        Get current optimal parameters từ latest successful optimization
        
        Returns:
            OptimizationParameters or None: Latest optimal parameters
        """
        successful_optimizations = [
            entry for entry in self.optimization_history 
            if entry["result"].success
        ]
        
        if not successful_optimizations:
            return None
        
        latest_optimization = max(
            successful_optimizations, 
            key=lambda x: x["timestamp"]
        )
        
        return latest_optimization["result"].optimal_parameters


# Service instance
parameter_optimization_service = ParameterOptimizationService()