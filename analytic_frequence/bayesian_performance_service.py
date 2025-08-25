"""
🎯 Bayesian Performance Prediction Service (Phase 2)
==================================================

Advanced Bayesian inference for performance prediction without heavy ML dependencies.
Implements Bayesian updating, uncertainty quantification, and predictive modeling.

Features:
- Bayesian performance prediction
- Uncertainty quantification
- Prior belief updating
- Credible intervals
- Model comparison using Bayes factors
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
import json
import logging
import math

logger = logging.getLogger(__name__)

class PriorType(Enum):
    """Prior distribution types"""
    NORMAL = "normal"
    BETA = "beta"
    GAMMA = "gamma"
    UNIFORM = "uniform"
    JEFFREYS = "jeffreys"

class InferenceMethod(Enum):
    """Bayesian inference methods"""
    CONJUGATE = "conjugate"
    MCMC_LITE = "mcmc_lite"
    VARIATIONAL = "variational"
    EMPIRICAL_BAYES = "empirical_bayes"

@dataclass(frozen=True)
class BayesianPrior:
    """Bayesian prior distribution"""
    distribution_type: PriorType
    parameters: Dict[str, float]
    belief_strength: float  # How confident we are in the prior
    source: str  # Where the prior comes from

@dataclass(frozen=True)
class BayesianPosterior:
    """Bayesian posterior distribution"""
    distribution_type: PriorType
    parameters: Dict[str, float]
    credible_interval: Tuple[float, float]
    posterior_mean: float
    posterior_variance: float
    evidence: float  # Marginal likelihood

@dataclass(frozen=True)
class UncertaintyQuantification:
    """Comprehensive uncertainty quantification"""
    epistemic_uncertainty: float  # Model uncertainty
    aleatoric_uncertainty: float  # Data uncertainty
    total_uncertainty: float
    confidence_level: float
    prediction_interval: Tuple[float, float]
    reliability_score: float

@dataclass(frozen=True)
class BayesianPrediction:
    """Bayesian prediction with uncertainty"""
    predicted_value: float
    prediction_variance: float
    credible_interval: Tuple[float, float]
    uncertainty_quantification: UncertaintyQuantification
    posterior_distribution: BayesianPosterior
    model_evidence: float
    timestamp: datetime = field(default_factory=datetime.now)

class BayesianPerformanceService:
    """
    🎯 Bayesian Performance Prediction Service
    
    Provides Bayesian inference for performance prediction with comprehensive
    uncertainty quantification using lightweight statistical methods.
    """
    
    def __init__(self):
        """Initialize Bayesian service"""
        self.priors = {}
        self.posteriors = {}
        self.observations = {}
        self.model_evidence_history = []
        
        # Configuration
        self.config = {
            'default_confidence_level': 0.95,
            'mcmc_samples': 1000,
            'burn_in': 200,
            'convergence_tolerance': 0.01,
            'evidence_threshold': -10.0  # Log evidence threshold
        }
        
        logger.info("✅ Bayesian Performance Service initialized")
    
    def define_prior(self, metric_name: str, prior_type: PriorType, 
                    parameters: Dict[str, float], belief_strength: float = 1.0,
                    source: str = "expert_knowledge") -> BayesianPrior:
        """
        🎯 Define Prior Distribution
        
        Sets up prior beliefs about performance metrics
        """
        try:
            # Validate parameters based on distribution type
            self._validate_prior_parameters(prior_type, parameters)
            
            prior = BayesianPrior(
                distribution_type=prior_type,
                parameters=parameters,
                belief_strength=belief_strength,
                source=source
            )
            
            self.priors[metric_name] = prior
            
            logger.info(f"✅ Defined {prior_type.value} prior for {metric_name}")
            logger.info(f"   Parameters: {parameters}")
            logger.info(f"   Belief strength: {belief_strength}")
            
            return prior
            
        except Exception as e:
            logger.error(f"❌ Error defining prior for {metric_name}: {e}")
            raise
    
    def update_posterior(self, metric_name: str, observations: List[float],
                        inference_method: InferenceMethod = InferenceMethod.CONJUGATE) -> BayesianPosterior:
        """
        🔄 Update Posterior Distribution
        
        Updates beliefs based on new observations using Bayesian inference
        """
        try:
            if metric_name not in self.priors:
                raise ValueError(f"No prior defined for {metric_name}")
            
            prior = self.priors[metric_name]
            
            # Store observations
            if metric_name not in self.observations:
                self.observations[metric_name] = []
            self.observations[metric_name].extend(observations)
            
            # Perform Bayesian update
            if inference_method == InferenceMethod.CONJUGATE:
                posterior = self._conjugate_update(prior, observations)
            elif inference_method == InferenceMethod.MCMC_LITE:
                posterior = self._mcmc_lite_update(prior, observations)
            elif inference_method == InferenceMethod.EMPIRICAL_BAYES:
                posterior = self._empirical_bayes_update(prior, observations)
            else:
                posterior = self._conjugate_update(prior, observations)  # Default
            
            self.posteriors[metric_name] = posterior
            
            logger.info(f"✅ Updated posterior for {metric_name}")
            logger.info(f"   Posterior mean: {posterior.posterior_mean:.4f}")
            logger.info(f"   95% CI: [{posterior.credible_interval[0]:.4f}, {posterior.credible_interval[1]:.4f}]")
            logger.info(f"   Evidence: {posterior.evidence:.2f}")
            
            return posterior
            
        except Exception as e:
            logger.error(f"❌ Error updating posterior for {metric_name}: {e}")
            raise
    
    def predict_performance(self, metric_name: str, horizon: int = 1,
                          include_uncertainty: bool = True) -> BayesianPrediction:
        """
        🔮 Predict Future Performance
        
        Makes Bayesian predictions with comprehensive uncertainty quantification
        """
        try:
            if metric_name not in self.posteriors:
                raise ValueError(f"No posterior available for {metric_name}")
            
            posterior = self.posteriors[metric_name]
            
            # Make prediction from posterior
            predicted_value = posterior.posterior_mean
            prediction_variance = posterior.posterior_variance * (1 + 1/len(self.observations.get(metric_name, [1])))
            
            # Calculate credible interval
            credible_interval = self._calculate_credible_interval(
                predicted_value, prediction_variance, self.config['default_confidence_level']
            )
            
            # Quantify uncertainty
            if include_uncertainty:
                uncertainty = self._quantify_uncertainty(metric_name, prediction_variance)
            else:
                uncertainty = UncertaintyQuantification(
                    epistemic_uncertainty=0.0,
                    aleatoric_uncertainty=0.0,
                    total_uncertainty=math.sqrt(prediction_variance),
                    confidence_level=self.config['default_confidence_level'],
                    prediction_interval=credible_interval,
                    reliability_score=0.5
                )
            
            # Calculate model evidence
            model_evidence = posterior.evidence
            
            prediction = BayesianPrediction(
                predicted_value=predicted_value,
                prediction_variance=prediction_variance,
                credible_interval=credible_interval,
                uncertainty_quantification=uncertainty,
                posterior_distribution=posterior,
                model_evidence=model_evidence
            )
            
            logger.info(f"✅ Generated Bayesian prediction for {metric_name}")
            logger.info(f"   Predicted value: {predicted_value:.4f}")
            logger.info(f"   Total uncertainty: {uncertainty.total_uncertainty:.4f}")
            logger.info(f"   Reliability: {uncertainty.reliability_score:.3f}")
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error predicting performance for {metric_name}: {e}")
            raise
    
    def compare_models(self, model_names: List[str], 
                      observations_dict: Dict[str, List[float]]) -> Dict[str, float]:
        """
        ⚖️ Bayesian Model Comparison
        
        Compares different models using Bayes factors
        """
        try:
            logger.info(f"⚖️ Comparing {len(model_names)} models using Bayes factors...")
            
            model_evidences = {}
            
            for model_name in model_names:
                if model_name in observations_dict:
                    observations = observations_dict[model_name]
                    
                    # Define default prior if not exists
                    if model_name not in self.priors:
                        self.define_prior(
                            model_name, 
                            PriorType.NORMAL, 
                            {'mean': 0.5, 'variance': 0.1},
                            belief_strength=0.5,
                            source='default'
                        )
                    
                    # Update posterior
                    posterior = self.update_posterior(model_name, observations)
                    model_evidences[model_name] = posterior.evidence
            
            # Calculate Bayes factors (relative to first model)
            if len(model_evidences) > 1:
                reference_model = model_names[0]
                reference_evidence = model_evidences[reference_model]
                
                bayes_factors = {}
                for model_name, evidence in model_evidences.items():
                    bayes_factor = evidence - reference_evidence  # Log Bayes factor
                    bayes_factors[model_name] = math.exp(bayes_factor)  # Convert to ratio
                
                # Log results
                best_model = max(bayes_factors.items(), key=lambda x: x[1])
                logger.info(f"✅ Model comparison completed")
                logger.info(f"   Best model: {best_model[0]} (BF: {best_model[1]:.2f})")
                
                return bayes_factors
            else:
                return {model_names[0]: 1.0} if model_names else {}
            
        except Exception as e:
            logger.error(f"❌ Error in model comparison: {e}")
            return {}
    
    def assess_prediction_reliability(self, metric_name: str) -> Dict[str, float]:
        """
        🔍 Assess Prediction Reliability
        
        Analyzes the reliability of Bayesian predictions
        """
        try:
            if metric_name not in self.posteriors:
                raise ValueError(f"No posterior available for {metric_name}")
            
            posterior = self.posteriors[metric_name]
            observations = self.observations.get(metric_name, [])
            
            # Calculate various reliability metrics
            reliability_metrics = {}
            
            # 1. Posterior uncertainty
            posterior_uncertainty = posterior.posterior_variance
            reliability_metrics['posterior_uncertainty'] = posterior_uncertainty
            
            # 2. Data sufficiency (based on sample size)
            n_obs = len(observations)
            data_sufficiency = min(1.0, n_obs / 30.0)  # Assume 30 is "sufficient"
            reliability_metrics['data_sufficiency'] = data_sufficiency
            
            # 3. Prior-data conflict
            if n_obs > 0:
                data_mean = np.mean(observations)
                prior_mean = self.priors[metric_name].parameters.get('mean', 0.5)
                conflict = abs(data_mean - prior_mean)
                prior_data_agreement = math.exp(-conflict)
                reliability_metrics['prior_data_agreement'] = prior_data_agreement
            else:
                reliability_metrics['prior_data_agreement'] = 1.0
            
            # 4. Model evidence strength
            evidence_strength = max(0.0, min(1.0, (posterior.evidence + 10) / 10))  # Normalize
            reliability_metrics['evidence_strength'] = evidence_strength
            
            # 5. Overall reliability score
            weights = [0.3, 0.3, 0.2, 0.2]  # Weights for each metric
            values = [
                1.0 - min(1.0, posterior_uncertainty),
                data_sufficiency,
                reliability_metrics['prior_data_agreement'],
                evidence_strength
            ]
            
            overall_reliability = sum(w * v for w, v in zip(weights, values))
            reliability_metrics['overall_reliability'] = overall_reliability
            
            logger.info(f"✅ Reliability assessment for {metric_name}")
            logger.info(f"   Overall reliability: {overall_reliability:.3f}")
            
            return reliability_metrics
            
        except Exception as e:
            logger.error(f"❌ Error assessing reliability for {metric_name}: {e}")
            return {}
    
    def generate_ensemble_prediction(self, metric_names: List[str],
                                   weights: Optional[List[float]] = None) -> BayesianPrediction:
        """
        🎯 Generate Ensemble Bayesian Prediction
        
        Combines multiple Bayesian predictions into an ensemble
        """
        try:
            logger.info(f"🎯 Generating ensemble prediction from {len(metric_names)} models...")
            
            if not metric_names:
                raise ValueError("No metrics provided for ensemble")
            
            # Get individual predictions
            individual_predictions = []
            for metric_name in metric_names:
                if metric_name in self.posteriors:
                    pred = self.predict_performance(metric_name)
                    individual_predictions.append(pred)
            
            if not individual_predictions:
                raise ValueError("No valid predictions available for ensemble")
            
            # Set weights
            if weights is None:
                weights = [1.0 / len(individual_predictions)] * len(individual_predictions)
            elif len(weights) != len(individual_predictions):
                raise ValueError("Number of weights must match number of predictions")
            
            # Normalize weights
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            
            # Combine predictions
            ensemble_mean = sum(w * pred.predicted_value for w, pred in zip(weights, individual_predictions))
            
            # Combine variances (assuming independence)
            ensemble_variance = sum(w**2 * pred.prediction_variance for w, pred in zip(weights, individual_predictions))
            
            # Calculate ensemble credible interval
            ensemble_ci = self._calculate_credible_interval(
                ensemble_mean, ensemble_variance, self.config['default_confidence_level']
            )
            
            # Combine uncertainties
            epistemic = np.mean([pred.uncertainty_quantification.epistemic_uncertainty for pred in individual_predictions])
            aleatoric = np.mean([pred.uncertainty_quantification.aleatoric_uncertainty for pred in individual_predictions])
            total_uncertainty = math.sqrt(epistemic**2 + aleatoric**2)
            reliability = np.mean([pred.uncertainty_quantification.reliability_score for pred in individual_predictions])
            
            ensemble_uncertainty = UncertaintyQuantification(
                epistemic_uncertainty=epistemic,
                aleatoric_uncertainty=aleatoric,
                total_uncertainty=total_uncertainty,
                confidence_level=self.config['default_confidence_level'],
                prediction_interval=ensemble_ci,
                reliability_score=reliability
            )
            
            # Create ensemble posterior (simplified)
            ensemble_posterior = BayesianPosterior(
                distribution_type=PriorType.NORMAL,
                parameters={'mean': ensemble_mean, 'variance': ensemble_variance},
                credible_interval=ensemble_ci,
                posterior_mean=ensemble_mean,
                posterior_variance=ensemble_variance,
                evidence=np.mean([pred.model_evidence for pred in individual_predictions])
            )
            
            ensemble_prediction = BayesianPrediction(
                predicted_value=ensemble_mean,
                prediction_variance=ensemble_variance,
                credible_interval=ensemble_ci,
                uncertainty_quantification=ensemble_uncertainty,
                posterior_distribution=ensemble_posterior,
                model_evidence=ensemble_posterior.evidence
            )
            
            logger.info(f"✅ Ensemble prediction generated")
            logger.info(f"   Ensemble mean: {ensemble_mean:.4f}")
            logger.info(f"   Total uncertainty: {total_uncertainty:.4f}")
            logger.info(f"   Reliability: {reliability:.3f}")
            
            return ensemble_prediction
            
        except Exception as e:
            logger.error(f"❌ Error generating ensemble prediction: {e}")
            raise
    
    # =================== PRIVATE METHODS ===================
    
    def _validate_prior_parameters(self, prior_type: PriorType, parameters: Dict[str, float]):
        """Validate prior parameters for distribution type"""
        if prior_type == PriorType.NORMAL:
            if 'mean' not in parameters or 'variance' not in parameters:
                raise ValueError("Normal prior requires 'mean' and 'variance' parameters")
            if parameters['variance'] <= 0:
                raise ValueError("Variance must be positive")
                
        elif prior_type == PriorType.BETA:
            if 'alpha' not in parameters or 'beta' not in parameters:
                raise ValueError("Beta prior requires 'alpha' and 'beta' parameters")
            if parameters['alpha'] <= 0 or parameters['beta'] <= 0:
                raise ValueError("Beta parameters must be positive")
                
        elif prior_type == PriorType.GAMMA:
            if 'shape' not in parameters or 'rate' not in parameters:
                raise ValueError("Gamma prior requires 'shape' and 'rate' parameters")
            if parameters['shape'] <= 0 or parameters['rate'] <= 0:
                raise ValueError("Gamma parameters must be positive")
    
    def _conjugate_update(self, prior: BayesianPrior, observations: List[float]) -> BayesianPosterior:
        """Perform conjugate Bayesian update"""
        try:
            obs_array = np.array(observations)
            n = len(observations)
            
            if prior.distribution_type == PriorType.NORMAL:
                # Normal-Normal conjugate update
                prior_mean = prior.parameters['mean']
                prior_var = prior.parameters['variance']
                
                # Assume known likelihood variance (simplified)
                likelihood_var = np.var(obs_array) if n > 1 else 0.1
                
                # Posterior parameters
                posterior_precision = 1/prior_var + n/likelihood_var
                posterior_var = 1/posterior_precision
                posterior_mean = (prior_mean/prior_var + np.sum(obs_array)/likelihood_var) * posterior_var
                
                # Credible interval
                ci = self._calculate_credible_interval(posterior_mean, posterior_var, 0.95)
                
                # Calculate evidence (marginal likelihood)
                evidence = self._calculate_evidence_normal(prior, obs_array, likelihood_var)
                
                return BayesianPosterior(
                    distribution_type=PriorType.NORMAL,
                    parameters={'mean': posterior_mean, 'variance': posterior_var},
                    credible_interval=ci,
                    posterior_mean=posterior_mean,
                    posterior_variance=posterior_var,
                    evidence=evidence
                )
                
            elif prior.distribution_type == PriorType.BETA:
                # Beta-Binomial conjugate update (for rates/proportions)
                alpha_prior = prior.parameters['alpha']
                beta_prior = prior.parameters['beta']
                
                # Assume observations are successes/failures
                successes = np.sum(obs_array)
                failures = n - successes
                
                # Posterior parameters
                alpha_post = alpha_prior + successes
                beta_post = beta_prior + failures
                
                posterior_mean = alpha_post / (alpha_post + beta_post)
                posterior_var = (alpha_post * beta_post) / ((alpha_post + beta_post)**2 * (alpha_post + beta_post + 1))
                
                # Credible interval for Beta distribution (approximation)
                beta_mean = alpha_post / (alpha_post + beta_post)
                beta_var = (alpha_post * beta_post) / ((alpha_post + beta_post)**2 * (alpha_post + beta_post + 1))
                beta_std = math.sqrt(beta_var)
                
                # Normal approximation for credible interval
                z_score = 1.96  # 95% confidence
                ci = (
                    max(0, beta_mean - z_score * beta_std),
                    min(1, beta_mean + z_score * beta_std)
                )
                
                evidence = self._calculate_evidence_beta(prior, successes, failures)
                
                return BayesianPosterior(
                    distribution_type=PriorType.BETA,
                    parameters={'alpha': alpha_post, 'beta': beta_post},
                    credible_interval=ci,
                    posterior_mean=posterior_mean,
                    posterior_variance=posterior_var,
                    evidence=evidence
                )
            
            else:
                # Default to normal approximation
                return self._normal_approximation_update(prior, observations)
                
        except Exception as e:
            logger.error(f"❌ Error in conjugate update: {e}")
            return self._normal_approximation_update(prior, observations)
    
    def _mcmc_lite_update(self, prior: BayesianPrior, observations: List[float]) -> BayesianPosterior:
        """Lightweight MCMC update (simplified Metropolis-Hastings)"""
        try:
            obs_array = np.array(observations)
            n_samples = self.config['mcmc_samples']
            burn_in = self.config['burn_in']
            
            # Initialize
            if prior.distribution_type == PriorType.NORMAL:
                current_param = prior.parameters['mean']
                prior_var = prior.parameters['variance']
                
                samples = []
                
                for i in range(n_samples + burn_in):
                    # Propose new parameter
                    proposal = current_param + np.random.normal(0, 0.1)
                    
                    # Calculate log probabilities
                    current_log_prob = self._log_posterior_normal(current_param, prior, obs_array)
                    proposal_log_prob = self._log_posterior_normal(proposal, prior, obs_array)
                    
                    # Accept/reject
                    if np.log(np.random.random()) < (proposal_log_prob - current_log_prob):
                        current_param = proposal
                    
                    # Store sample after burn-in
                    if i >= burn_in:
                        samples.append(current_param)
                
                # Calculate posterior statistics
                posterior_mean = np.mean(samples)
                posterior_var = np.var(samples)
                
                # Credible interval from samples
                ci = (np.percentile(samples, 2.5), np.percentile(samples, 97.5))
                
                evidence = self._calculate_evidence_normal(prior, obs_array, 0.1)
                
                return BayesianPosterior(
                    distribution_type=PriorType.NORMAL,
                    parameters={'mean': posterior_mean, 'variance': posterior_var},
                    credible_interval=ci,
                    posterior_mean=posterior_mean,
                    posterior_variance=posterior_var,
                    evidence=evidence
                )
            
            else:
                # Fallback to conjugate update
                return self._conjugate_update(prior, observations)
                
        except Exception as e:
            logger.error(f"❌ Error in MCMC update: {e}")
            return self._conjugate_update(prior, observations)
    
    def _empirical_bayes_update(self, prior: BayesianPrior, observations: List[float]) -> BayesianPosterior:
        """Empirical Bayes update (estimate hyperparameters from data)"""
        try:
            obs_array = np.array(observations)
            
            # Estimate hyperparameters from data
            data_mean = np.mean(obs_array)
            data_var = np.var(obs_array) if len(obs_array) > 1 else 0.1
            
            # Use data to inform posterior
            # This is a simplified empirical Bayes approach
            posterior_mean = data_mean
            posterior_var = data_var / len(obs_array)  # Posterior uncertainty decreases with sample size
            
            ci = self._calculate_credible_interval(posterior_mean, posterior_var, 0.95)
            evidence = self._calculate_evidence_normal(prior, obs_array, data_var)
            
            return BayesianPosterior(
                distribution_type=PriorType.NORMAL,
                parameters={'mean': posterior_mean, 'variance': posterior_var},
                credible_interval=ci,
                posterior_mean=posterior_mean,
                posterior_variance=posterior_var,
                evidence=evidence
            )
            
        except Exception as e:
            logger.error(f"❌ Error in empirical Bayes update: {e}")
            return self._normal_approximation_update(prior, observations)
    
    def _normal_approximation_update(self, prior: BayesianPrior, observations: List[float]) -> BayesianPosterior:
        """Normal approximation fallback"""
        obs_array = np.array(observations)
        
        # Simple normal approximation
        if len(obs_array) > 0:
            posterior_mean = np.mean(obs_array)
            posterior_var = np.var(obs_array) / len(obs_array) if len(obs_array) > 1 else 0.1
        else:
            posterior_mean = prior.parameters.get('mean', 0.5)
            posterior_var = prior.parameters.get('variance', 0.1)
        
        ci = self._calculate_credible_interval(posterior_mean, posterior_var, 0.95)
        evidence = -5.0  # Default evidence
        
        return BayesianPosterior(
            distribution_type=PriorType.NORMAL,
            parameters={'mean': posterior_mean, 'variance': posterior_var},
            credible_interval=ci,
            posterior_mean=posterior_mean,
            posterior_variance=posterior_var,
            evidence=evidence
        )
    
    def _calculate_credible_interval(self, mean: float, variance: float, confidence: float) -> Tuple[float, float]:
        """Calculate credible interval for normal distribution"""
        try:
            std = math.sqrt(variance)
            # Use standard normal quantiles (approximation)
            if confidence == 0.95:
                z_score = 1.96
            elif confidence == 0.99:
                z_score = 2.576
            elif confidence == 0.90:
                z_score = 1.645
            else:
                z_score = 1.96  # Default to 95%
            
            lower = mean - z_score * std
            upper = mean + z_score * std
            
            return (lower, upper)
            
        except Exception:
            return (mean - 0.1, mean + 0.1)
    
    def _quantify_uncertainty(self, metric_name: str, prediction_variance: float) -> UncertaintyQuantification:
        """Quantify different types of uncertainty"""
        try:
            observations = self.observations.get(metric_name, [])
            n_obs = len(observations)
            
            # Epistemic uncertainty (model uncertainty)
            # Decreases with more data
            epistemic = prediction_variance / (1 + n_obs/10)
            
            # Aleatoric uncertainty (data uncertainty)
            # Inherent noise in the data
            if n_obs > 1:
                data_variance = np.var(observations)
                aleatoric = data_variance * 0.5  # Assume 50% is irreducible
            else:
                aleatoric = prediction_variance * 0.3
            
            # Total uncertainty
            total_uncertainty = math.sqrt(epistemic + aleatoric)
            
            # Prediction interval (wider than credible interval)
            prediction_std = math.sqrt(prediction_variance + aleatoric)
            z_score = 1.96  # 95% confidence
            
            # Get posterior mean
            posterior = self.posteriors.get(metric_name)
            mean = posterior.posterior_mean if posterior else 0.5
            
            prediction_interval = (
                mean - z_score * prediction_std,
                mean + z_score * prediction_std
            )
            
            # Reliability score
            reliability = max(0.0, 1.0 - total_uncertainty)
            
            return UncertaintyQuantification(
                epistemic_uncertainty=epistemic,
                aleatoric_uncertainty=aleatoric,
                total_uncertainty=total_uncertainty,
                confidence_level=0.95,
                prediction_interval=prediction_interval,
                reliability_score=reliability
            )
            
        except Exception as e:
            logger.error(f"❌ Error quantifying uncertainty: {e}")
            return UncertaintyQuantification(
                epistemic_uncertainty=prediction_variance * 0.7,
                aleatoric_uncertainty=prediction_variance * 0.3,
                total_uncertainty=math.sqrt(prediction_variance),
                confidence_level=0.95,
                prediction_interval=(0.0, 1.0),
                reliability_score=0.5
            )
    
    def _calculate_evidence_normal(self, prior: BayesianPrior, observations: np.ndarray, likelihood_var: float) -> float:
        """Calculate marginal likelihood for normal model"""
        try:
            # Simplified evidence calculation
            n = len(observations)
            if n == 0:
                return 0.0
            
            # Log marginal likelihood approximation
            log_evidence = -n/2 * np.log(2 * np.pi * likelihood_var)
            log_evidence -= np.sum((observations - np.mean(observations))**2) / (2 * likelihood_var)
            
            return log_evidence
            
        except Exception:
            return -5.0  # Default evidence
    
    def _calculate_evidence_beta(self, prior: BayesianPrior, successes: float, failures: float) -> float:
        """Calculate marginal likelihood for beta-binomial model"""
        try:
            alpha_prior = prior.parameters['alpha']
            beta_prior = prior.parameters['beta']
            
            # Log marginal likelihood for beta-binomial
            from math import lgamma
            
            log_evidence = (lgamma(successes + alpha_prior) + lgamma(failures + beta_prior) + 
                           lgamma(alpha_prior + beta_prior) - lgamma(successes + failures + alpha_prior + beta_prior) -
                           lgamma(alpha_prior) - lgamma(beta_prior))
            
            return log_evidence
            
        except Exception:
            return -5.0  # Default evidence
    
    def _log_posterior_normal(self, param: float, prior: BayesianPrior, observations: np.ndarray) -> float:
        """Calculate log posterior for normal model"""
        try:
            # Log prior
            prior_mean = prior.parameters['mean']
            prior_var = prior.parameters['variance']
            log_prior = -0.5 * (param - prior_mean)**2 / prior_var
            
            # Log likelihood (assume variance = 0.1)
            likelihood_var = 0.1
            log_likelihood = np.sum(-0.5 * (observations - param)**2 / likelihood_var)
            
            return log_prior + log_likelihood
            
        except Exception:
            return -float('inf')

# =================== DEMONSTRATION FUNCTIONS ===================

def demo_bayesian_performance_service():
    """Demonstrate Bayesian Performance Service"""
    print("🎯 BAYESIAN PERFORMANCE PREDICTION SERVICE - DEMONSTRATION")
    print("=" * 70)
    
    # Initialize service
    bayesian_service = BayesianPerformanceService()
    
    # Define priors for different metrics
    print("\n📊 DEFINING BAYESIAN PRIORS:")
    
    # Accuracy prior
    accuracy_prior = bayesian_service.define_prior(
        'accuracy', 
        PriorType.BETA,
        {'alpha': 8, 'beta': 2},  # Prior belief: high accuracy
        belief_strength=0.8,
        source='historical_data'
    )
    print(f"   ✅ Accuracy prior: Beta(8, 2) - believing in high accuracy")
    
    # Sharpe ratio prior
    sharpe_prior = bayesian_service.define_prior(
        'sharpe_ratio',
        PriorType.NORMAL,
        {'mean': 1.0, 'variance': 0.5},  # Moderate Sharpe ratio expected
        belief_strength=0.6,
        source='market_knowledge'
    )
    print(f"   ✅ Sharpe ratio prior: Normal(1.0, 0.5)")
    
    # Generate sample observations
    print("\n📈 GENERATING SAMPLE OBSERVATIONS:")
    np.random.seed(42)
    
    # Accuracy observations (simulated as success rate)
    accuracy_obs = np.random.beta(8, 3, 20)  # Slightly different from prior
    print(f"   Accuracy observations: {len(accuracy_obs)} samples, mean: {np.mean(accuracy_obs):.3f}")
    
    # Sharpe ratio observations
    sharpe_obs = np.random.normal(1.2, 0.3, 15)  # Slightly better than prior
    print(f"   Sharpe observations: {len(sharpe_obs)} samples, mean: {np.mean(sharpe_obs):.3f}")
    
    # Update posteriors
    print("\n🔄 UPDATING POSTERIOR DISTRIBUTIONS:")
    
    accuracy_posterior = bayesian_service.update_posterior('accuracy', accuracy_obs.tolist())
    print(f"   ✅ Accuracy posterior updated")
    
    sharpe_posterior = bayesian_service.update_posterior('sharpe_ratio', sharpe_obs.tolist())
    print(f"   ✅ Sharpe ratio posterior updated")
    
    # Make predictions
    print("\n🔮 BAYESIAN PREDICTIONS:")
    
    accuracy_prediction = bayesian_service.predict_performance('accuracy')
    print(f"\n   Accuracy Prediction:")
    print(f"     Predicted value: {accuracy_prediction.predicted_value:.4f}")
    print(f"     95% Credible interval: [{accuracy_prediction.credible_interval[0]:.4f}, {accuracy_prediction.credible_interval[1]:.4f}]")
    print(f"     Total uncertainty: {accuracy_prediction.uncertainty_quantification.total_uncertainty:.4f}")
    print(f"     Reliability score: {accuracy_prediction.uncertainty_quantification.reliability_score:.3f}")
    
    sharpe_prediction = bayesian_service.predict_performance('sharpe_ratio')
    print(f"\n   Sharpe Ratio Prediction:")
    print(f"     Predicted value: {sharpe_prediction.predicted_value:.4f}")
    print(f"     95% Credible interval: [{sharpe_prediction.credible_interval[0]:.4f}, {sharpe_prediction.credible_interval[1]:.4f}]")
    print(f"     Total uncertainty: {sharpe_prediction.uncertainty_quantification.total_uncertainty:.4f}")
    print(f"     Reliability score: {sharpe_prediction.uncertainty_quantification.reliability_score:.3f}")
    
    # Model comparison
    print("\n⚖️ BAYESIAN MODEL COMPARISON:")
    
    # Create alternative model observations
    alt_accuracy_obs = np.random.beta(6, 4, 18)  # Different model
    
    model_data = {
        'model_a_accuracy': accuracy_obs.tolist(),
        'model_b_accuracy': alt_accuracy_obs.tolist()
    }
    
    bayes_factors = bayesian_service.compare_models(['model_a_accuracy', 'model_b_accuracy'], model_data)
    for model, bf in bayes_factors.items():
        print(f"   {model}: Bayes Factor = {bf:.3f}")
    
    # Reliability assessment
    print("\n🔍 PREDICTION RELIABILITY ASSESSMENT:")
    
    accuracy_reliability = bayesian_service.assess_prediction_reliability('accuracy')
    print(f"   Accuracy reliability metrics:")
    for metric, value in accuracy_reliability.items():
        print(f"     {metric}: {value:.3f}")
    
    # Ensemble prediction
    print("\n🎯 ENSEMBLE BAYESIAN PREDICTION:")
    
    ensemble_pred = bayesian_service.generate_ensemble_prediction(
        ['accuracy', 'sharpe_ratio'],
        weights=[0.6, 0.4]  # Weight accuracy more
    )
    
    print(f"   Ensemble prediction: {ensemble_pred.predicted_value:.4f}")
    print(f"   Total uncertainty: {ensemble_pred.uncertainty_quantification.total_uncertainty:.4f}")
    print(f"   Reliability: {ensemble_pred.uncertainty_quantification.reliability_score:.3f}")
    print(f"   Model evidence: {ensemble_pred.model_evidence:.2f}")
    
    print(f"\n✅ Bayesian Performance Prediction Service demonstration completed!")
    
    return bayesian_service

if __name__ == "__main__":
    service = demo_bayesian_performance_service()
