"""
🎯 INTELLIGENT PREDICTION API - API endpoints cho Revolutionary Intelligence System
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from datetime import date
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class IntelligentPredictionAPI(View):
    """
    🚀 Revolutionary Intelligence API - NO FALLBACK, REAL INTELLIGENCE ONLY
    
    Revolutionary Features:
    - META-PREDICTION: Predict which methods will perform best
    - BASELINE COMPARISON: Compare vs random for actual performance
    - CORRELATION ANALYSIS: Detect duplicate methods
    - ANOMALY DETECTION: Detect lottery deviations from randomness
    - DYNAMIC WEIGHTING: Context-aware method selection
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.intelligence = None
        self._initialize_revolutionary_intelligence()

    def _initialize_revolutionary_intelligence(self) -> bool:
        """
        Initialize Revolutionary Intelligence System
        
        Returns:
            bool: True if successful, raises exception if failed
        """
        try:
            from predictions_tracker.core.services.DataService import data_service
            from predictions_tracker.core.services.IntelligenceIntegration import IntelligenceIntegration
            
            # ✅ CREATE REVOLUTIONARY INTELLIGENCE INTEGRATION
            self.intelligence = IntelligenceIntegration(data_service)
            
            # ✅ INITIALIZE - MUST SUCCEED OR FAIL
            success = self.intelligence.initialize_intelligence_system()
            
            if not success:
                raise RuntimeError("Revolutionary Intelligence System initialization failed")
            
            logger.info("✅ Revolutionary Intelligence System initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Revolutionary Intelligence initialization failed: {str(e)}")
            raise RuntimeError(f"Revolutionary Intelligence System required but failed to initialize: {str(e)}")

    def post(self, request) -> JsonResponse:
        """
        Handle POST requests for Revolutionary Intelligence Predictions
        
        Args:
            request: HTTP request với JSON data
            
        Returns:
            JsonResponse: Revolutionary intelligence predictions với schema nhất quán
            {
                "success": bool,
                "meta_predictions": dict,
                "baseline_comparison": dict,
                "correlation_analysis": dict,
                "anomaly_detection": dict,
                "dynamic_weighting": dict,
                "performance_analysis": dict,
                "intelligent_recommendations": dict,
                "intelligent_predictions": dict,
                "metadata": dict
            }
        """
        try:
            # ✅ PARSE REQUEST DATA
            request_data = self._parse_request_data(request)
            
            # ✅ VALIDATE REVOLUTIONARY INTELLIGENCE SYSTEM
            if not self.intelligence:
                raise RuntimeError("Revolutionary Intelligence System not initialized")
            
            # ✅ EXTRACT PARAMETERS
            analysis_date = request_data['analysis_date']
            method_ids = request_data['method_ids']
            
            # ✅ VALIDATE PARAMETERS FOR REVOLUTIONARY ANALYSIS
            self._validate_revolutionary_parameters(method_ids, analysis_date)
            
            # ✅ GENERATE REVOLUTIONARY PREDICTIONS
            predictions_data = self._generate_revolutionary_predictions(
                method_ids=method_ids,
                analysis_date=analysis_date,
                **request_data.get('options', {})
            )
            
            # ✅ VALIDATE REVOLUTIONARY RESULTS
            self._validate_revolutionary_results(predictions_data)
            
            # ✅ SANITIZE DATA FOR JSON SERIALIZATION
            sanitized_predictions = self._sanitize_for_json(predictions_data)
            
            # ✅ ADD REVOLUTIONARY METADATA
            sanitized_predictions['metadata'].update({
                'api_endpoint': 'revolutionary-intelligence',
                'request_timestamp': datetime.now().isoformat(),
                'analysis_type': 'revolutionary_intelligence',
                'requested_methods': len(method_ids),
                'api_version': '2.0',
                'revolutionary_features': [
                    'META_PREDICTION',
                    'BASELINE_COMPARISON', 
                    'CORRELATION_ANALYSIS',
                    'ANOMALY_DETECTION',
                    'DYNAMIC_WEIGHTING'
                ]
            })
            
            logger.info(f"✅ Revolutionary Intelligence predictions generated for {len(method_ids)} methods")
            return JsonResponse(sanitized_predictions)
            
        except Exception as e:
            logger.error(f"❌ Revolutionary Intelligence API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Revolutionary Intelligence System error: {str(e)}',
                'error_type': 'revolutionary_intelligence_error',
                'revolutionary': True,
                'fallback_available': False
            }, status=500)

    def _sanitize_for_json(self, data: Any) -> Any:
        """
        Sanitize data for JSON serialization - convert non-serializable types
        
        Args:
            data: Data to sanitize
            
        Returns:
            Any: JSON-serializable data
        """
        if isinstance(data, dict):
            return {key: self._sanitize_for_json(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_for_json(item) for item in data]
        elif isinstance(data, tuple):
            return [self._sanitize_for_json(item) for item in data]
        elif isinstance(data, set):
            return list(data)
        elif isinstance(data, (datetime, date)):
            return data.isoformat()
        elif isinstance(data, bool):
            return data  # booleans are JSON serializable
        elif isinstance(data, (int, float, str)) or data is None:
            return data
        elif hasattr(data, '__dict__'):
            # Convert object to dict
            return self._sanitize_for_json(data.__dict__)
        else:
            # Convert to string as fallback
            return str(data)

    def _generate_revolutionary_predictions(self, method_ids: List[str], analysis_date: str, **options) -> Dict[str, Any]:
        """
        Generate Revolutionary Intelligence Predictions
        
        Args:
            method_ids: List of method IDs
            analysis_date: Analysis date (YYYY-MM-DD format)
            **options: Revolutionary analysis options
            
        Returns:
            Dict[str, Any]: Revolutionary predictions data với schema nhất quán
            {
                "success": bool,
                "meta_predictions": dict,
                "baseline_comparison": dict,
                "correlation_analysis": dict,
                "anomaly_detection": dict,
                "dynamic_weighting": dict,
                "performance_analysis": dict,
                "intelligent_recommendations": dict,
                "intelligent_predictions": dict,
                "metadata": dict
            }
        """
        try:
            # ✅ GENERATE REVOLUTIONARY PREDICTIONS
            predictions_data = self.intelligence.generate_intelligent_predictions(
                method_ids=method_ids,
                analysis_date=analysis_date,
                **options
            )
            
            # ✅ VALIDATE REVOLUTIONARY RESPONSE
            if not predictions_data or not predictions_data.get('success'):
                error_msg = predictions_data.get('error', 'Unknown error') if predictions_data else 'No response'
                raise RuntimeError(f'Revolutionary Intelligence generation failed: {error_msg}')
            
            # ✅ VALIDATE REVOLUTIONARY COMPONENTS
            required_components = [
                'meta_predictions',
                'baseline_comparison', 
                'correlation_analysis',
                'anomaly_detection',
                'dynamic_weighting',
                'performance_analysis',
                'intelligent_recommendations',
                'intelligent_predictions'
            ]
            
            missing_components = [comp for comp in required_components if comp not in predictions_data]
            if missing_components:
                raise RuntimeError(f'Revolutionary Intelligence missing components: {missing_components}')
            
            # ✅ ENSURE CONSISTENT SCHEMA
            validated_response = {
                'success': True,
                'meta_predictions': predictions_data.get('meta_predictions', {}),
                'baseline_comparison': predictions_data.get('baseline_comparison', {}),
                'correlation_analysis': predictions_data.get('correlation_analysis', {}),
                'anomaly_detection': predictions_data.get('anomaly_detection', {}),
                'dynamic_weighting': predictions_data.get('dynamic_weighting', {}),
                'performance_analysis': predictions_data.get('performance_analysis', {}),
                'intelligent_recommendations': predictions_data.get('intelligent_recommendations', {}),
                'intelligent_predictions': predictions_data.get('intelligent_predictions', {}),
                'metadata': predictions_data.get('metadata', {})
            }
            
            return validated_response
            
        except Exception as e:
            logger.error(f"❌ Revolutionary prediction generation error: {str(e)}")
            raise RuntimeError(f'Revolutionary Intelligence prediction generation failed: {str(e)}')

    def _validate_revolutionary_results(self, predictions_data: Dict[str, Any]) -> None:
        """
        Validate Revolutionary Intelligence Results
        
        Args:
            predictions_data: Predictions data to validate
            
        Raises:
            ValueError: Nếu validation fails
        """
        try:
            # ✅ VALIDATE STRUCTURE
            if not isinstance(predictions_data, dict):
                raise ValueError('Revolutionary Intelligence must return structured dict')
            
            # ✅ VALIDATE SUCCESS
            if not predictions_data.get('success'):
                raise ValueError('Revolutionary Intelligence analysis must succeed')
            
            # ✅ VALIDATE REVOLUTIONARY FEATURES
            meta_predictions = predictions_data.get('meta_predictions', {})
            if not isinstance(meta_predictions, dict):
                raise ValueError('META-PREDICTION component must be dict')
            
            baseline_comparison = predictions_data.get('baseline_comparison', {})
            if not isinstance(baseline_comparison, dict):
                raise ValueError('BASELINE COMPARISON component must be dict')
            
            correlation_analysis = predictions_data.get('correlation_analysis', {})
            if not isinstance(correlation_analysis, dict):
                raise ValueError('CORRELATION ANALYSIS component must be dict')
            
            anomaly_detection = predictions_data.get('anomaly_detection', {})
            if not isinstance(anomaly_detection, dict):
                raise ValueError('ANOMALY DETECTION component must be dict')
            
            dynamic_weighting = predictions_data.get('dynamic_weighting', {})
            if not isinstance(dynamic_weighting, dict):
                raise ValueError('DYNAMIC WEIGHTING component must be dict')
            
            # ✅ VALIDATE INTELLIGENCE SCORE
            metadata = predictions_data.get('metadata', {})
            intelligence_score = metadata.get('intelligence_score', 0)
            
            if not isinstance(intelligence_score, (int, float)):
                raise ValueError(f'Intelligence score must be numeric, got: {type(intelligence_score)}')
            
            if intelligence_score < 0.1:
                logger.warning(f'⚠️ Revolutionary Intelligence score low: {intelligence_score}')
            
            # ✅ VALIDATE PREDICTIONS
            intelligent_predictions = predictions_data.get('intelligent_predictions', {})
            if not isinstance(intelligent_predictions, dict):
                raise ValueError('Revolutionary Intelligence predictions must be dict')
            
            logger.info(f"✅ Revolutionary Intelligence validation passed. Score: {intelligence_score}")
            
        except Exception as e:
            logger.error(f"❌ Revolutionary Intelligence validation failed: {str(e)}")
            raise ValueError(f'Revolutionary Intelligence validation failed: {str(e)}')

    def _parse_request_data(self, request) -> Dict[str, Any]:
        """
        Parse and validate request data for Revolutionary Intelligence
        
        Args:
            request: HTTP request
            
        Returns:
            Dict[str, Any]: Parsed request data với schema nhất quán
            {
                "analysis_date": str,
                "method_ids": List[str],
                "options": dict
            }
        """
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            raise ValueError(f'Invalid JSON format required for Revolutionary Intelligence: {str(e)}')

        # ✅ VALIDATE REQUIRED FIELDS
        required_fields = ['analysis_date', 'method_ids']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValueError(f'Missing required fields for Revolutionary Intelligence: {missing_fields}')

        # ✅ EXTRACT AND CLEAN METHOD IDS
        method_ids = data.get('method_ids', [])
        if not method_ids or not isinstance(method_ids, list):
            raise ValueError('method_ids must be a non-empty list for Revolutionary Intelligence')

        # ✅ CLEAN METHOD IDS - BỎ QUA INVALID VALUES
        cleaned_method_ids = []
        for method_id in method_ids:
            if method_id is None:
                continue
                
            # Convert to string and clean
            method_id_str = str(method_id).strip()
            
            # Skip empty, dash, or clearly invalid values
            if not method_id_str or method_id_str in ['-', '', 'null', 'undefined']:
                continue
                
            # Validate it's a valid identifier (number or alphanumeric)
            if method_id_str.isdigit():
                cleaned_method_ids.append(method_id_str)
            elif method_id_str.replace('_', '').replace('-', '').isalnum() and len(method_id_str) <= 50:
                cleaned_method_ids.append(method_id_str)
            else:
                logger.warning(f"⚠️ Skipping invalid method_id: {method_id}")
                continue

        # ✅ VALIDATE FINAL CLEANED LIST
        if not cleaned_method_ids:
            raise ValueError('No valid method IDs found after cleaning. Please provide valid method IDs (numbers or alphanumeric strings)')

        # ✅ LIMIT TO REASONABLE SIZE
        if len(cleaned_method_ids) > 100:
            cleaned_method_ids = cleaned_method_ids[:100]
            logger.warning(f"⚠️ Limited to first 100 method IDs")

        # ✅ EXTRACT OPTIONS WITH PROPER TYPES
        options = {
            'use_meta_prediction': bool(data.get('use_meta_prediction', True)),
            'use_baseline_comparison': bool(data.get('use_baseline_comparison', True)),
            'use_correlation_analysis': bool(data.get('use_correlation_analysis', True)),
            'use_anomaly_detection': bool(data.get('use_anomaly_detection', True)),
            'use_dynamic_weighting': bool(data.get('use_dynamic_weighting', True)),
            'prediction_horizon': int(max(1, min(7, data.get('prediction_horizon', 3)))),
            'months_back': int(max(1, min(24, data.get('months_back', 12)))),
            'min_data_points': int(max(1, min(200, data.get('min_data_points', 50))))
        }

        logger.info(f"✅ Parsed {len(cleaned_method_ids)} valid method IDs")

        return {
            'analysis_date': str(data['analysis_date']),
            'method_ids': cleaned_method_ids,
            'options': options
        }  
    
    def _validate_revolutionary_parameters(self, method_ids: List[str], analysis_date: str) -> None:
        """
        Validate parameters for Revolutionary Intelligence Analysis
        
        Args:
            method_ids: List of method IDs (đã được cleaned)
            analysis_date: Analysis date string
            
        Raises:
            ValueError: Nếu parameters không hợp lệ
        """
        # ✅ VALIDATE METHOD IDS (should be already cleaned)
        if not method_ids or not isinstance(method_ids, list):
            raise ValueError('method_ids must be a non-empty list for Revolutionary Intelligence')
        
        # ✅ DOUBLE CHECK CLEANED METHOD IDS
        valid_count = 0
        for method_id in method_ids:
            if method_id and str(method_id).strip() and str(method_id).strip() not in ['-', '', 'null']:
                valid_count += 1
        
        if valid_count < 1:
            raise ValueError('At least 1 valid method ID required for Revolutionary Intelligence analysis')
        
        if valid_count > 100:
            raise ValueError('Revolutionary Intelligence supports up to 100 methods per request')

        # ✅ VALIDATE DATE FORMAT
        try:
            parsed_date = datetime.strptime(analysis_date, '%Y-%m-%d')
            
            # Check reasonable date range
            min_date = datetime.now() - timedelta(days=365*2)  # 2 years ago
            max_date = datetime.now() + timedelta(days=30)     # 30 days future
            
            if parsed_date < min_date or parsed_date > max_date:
                raise ValueError(f'analysis_date must be between {min_date.strftime("%Y-%m-%d")} and {max_date.strftime("%Y-%m-%d")}')
                
        except ValueError as e:
            if 'analysis_date must be' in str(e):
                raise e
            else:
                raise ValueError('analysis_date must be in YYYY-MM-DD format for Revolutionary Intelligence')

        logger.info(f"✅ Validated {valid_count} valid method IDs for Revolutionary Intelligence")

    def get(self, request) -> JsonResponse:
        """
        Handle GET requests for Revolutionary Intelligence Analysis
        
        Args:
            request: HTTP GET request
            
        Returns:
            JsonResponse: Revolutionary intelligence analysis results
        """
        try:
            analysis_type = request.GET.get('type', 'performance')
            method_ids = request.GET.getlist('method_ids')
            
            # ✅ CLEAN METHOD IDS FOR GET REQUEST
            cleaned_method_ids = []
            for method_id in method_ids:
                if method_id is None:
                    continue
                    
                method_id_str = str(method_id).strip()
                
                # Skip invalid values
                if not method_id_str or method_id_str in ['-', '', 'null', 'undefined']:
                    continue
                    
                if method_id_str.isdigit() or (method_id_str.replace('_', '').replace('-', '').isalnum() and len(method_id_str) <= 50):
                    cleaned_method_ids.append(method_id_str)
            
            if not cleaned_method_ids:
                raise ValueError('No valid method_ids found for Revolutionary Intelligence analysis')

            # ✅ ROUTE TO APPROPRIATE HANDLER
            if analysis_type == 'performance':
                return self._handle_performance_analysis(request, cleaned_method_ids)
            elif analysis_type == 'correlations':
                return self._handle_correlations(request, cleaned_method_ids)
            elif analysis_type == 'baseline':
                return self._handle_baseline_comparison(request, cleaned_method_ids)
            elif analysis_type == 'anomalies':
                return self._handle_anomaly_detection(request, cleaned_method_ids)
            else:
                raise ValueError(f'Unknown Revolutionary Intelligence analysis type: {analysis_type}')
                
        except Exception as e:
            logger.error(f"❌ Revolutionary Intelligence GET error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Revolutionary Intelligence analysis error: {str(e)}',
                'error_type': 'revolutionary_analysis_error'
            }, status=400)

    def _handle_performance_analysis(self, request, method_ids: List[str] = None) -> JsonResponse:
        """
        Handle Revolutionary Performance Analysis
        
        Args:
            request: HTTP request
            method_ids: Pre-cleaned method IDs (optional)
            
        Returns:
            JsonResponse: Performance analysis results với schema nhất quán
            {
                "success": bool,
                "performance_analysis": dict,
                "revolutionary": bool,
                "analysis_type": str,
                "methods_analyzed": int,
                "valid_method_ids": List[str],
                "timestamp": str
            }
        """
        try:
            # ✅ USE PROVIDED METHOD IDS OR EXTRACT FROM REQUEST
            if method_ids is None:
                method_ids = request.GET.getlist('method_ids')
                method_ids = [
                    str(mid).strip() for mid in method_ids 
                    if mid and str(mid).strip() and str(mid).strip() not in ['-', '', 'null']
                ]
            
            months_back = int(request.GET.get('months_back', 12))
            
            if not method_ids:
                raise ValueError('No valid method IDs provided for performance analysis')
            
            if not self.intelligence:
                raise RuntimeError('Revolutionary Intelligence System not initialized')
            
            # ✅ GET HISTORICAL DATA
            historical_data = self.intelligence._get_real_historical_data(
                method_ids, 
                datetime.now().strftime('%Y-%m-%d'), 
                months_back
            )
            
            if not historical_data:
                raise RuntimeError('Insufficient historical data for Revolutionary Performance Analysis')
            
            # ✅ PERFORM REVOLUTIONARY PERFORMANCE ANALYSIS
            performance_data = self.intelligence._real_performance_analysis(
                historical_data, method_ids
            )
            
            # ✅ SANITIZE RESPONSE DATA
            response_data = {
                'success': True,
                'performance_analysis': performance_data,
                'revolutionary': True,
                'analysis_type': 'performance',
                'methods_analyzed': len(method_ids),
                'valid_method_ids': method_ids,
                'timestamp': datetime.now().isoformat()
            }
            
            sanitized_response = self._sanitize_for_json(response_data)
            return JsonResponse(sanitized_response)
            
        except Exception as e:
            logger.error(f"❌ Revolutionary Performance Analysis error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Revolutionary Performance Analysis failed: {str(e)}',
                'error_type': 'performance_analysis_error'
            }, status=500)

    def options(self, request) -> JsonResponse:
        """
        Handle OPTIONS requests for CORS
        
        Args:
            request: HTTP OPTIONS request
            
        Returns:
            JsonResponse: CORS headers với schema nhất quán
            {
                "success": bool,
                "api_name": str,
                "version": str,
                "revolutionary_features": List[str],
                "supported_methods": List[str],
                "no_fallback": bool,
                "revolutionary_only": bool
            }
        """
        return JsonResponse({
            'success': True,
            'api_name': 'Revolutionary Intelligence Prediction API',
            'version': '2.0',
            'revolutionary_features': [
                'META_PREDICTION',
                'BASELINE_COMPARISON',
                'CORRELATION_ANALYSIS', 
                'ANOMALY_DETECTION',
                'DYNAMIC_WEIGHTING'
            ],
            'supported_methods': ['POST', 'GET', 'OPTIONS'],
            'no_fallback': True,
            'revolutionary_only': True
        })
        
    def _handle_correlations(self, request, method_ids: List[str] = None) -> JsonResponse:
        """
        Handle Revolutionary Correlation Analysis
        
        Args:
            request: HTTP request
            method_ids: Pre-cleaned method IDs (optional)
            
        Returns:
            JsonResponse: Correlation analysis results
        """
        try:
            # ✅ USE PROVIDED METHOD IDS OR EXTRACT FROM REQUEST
            if method_ids is None:
                method_ids = request.GET.getlist('method_ids')
                method_ids = [
                    str(mid).strip() for mid in method_ids 
                    if mid and str(mid).strip() and str(mid).strip() not in ['-', '', 'null']
                ]
            
            if not method_ids:
                raise ValueError('No valid method IDs provided for correlation analysis')
            
            if not self.intelligence:
                raise RuntimeError('Revolutionary Intelligence System not initialized')
            
            # ✅ GET HISTORICAL DATA
            historical_data = self.intelligence._get_real_historical_data(
                method_ids, 
                datetime.now().strftime('%Y-%m-%d'), 
                12
            )
            
            if not historical_data:
                raise RuntimeError('Insufficient historical data for Revolutionary Correlation Analysis')
            
            # ✅ PERFORM REVOLUTIONARY CORRELATION ANALYSIS
            correlation_data = self.intelligence._real_correlation_analysis(
                historical_data, method_ids
            )
            
            return JsonResponse({
                'success': True,
                'correlation_analysis': correlation_data,
                'revolutionary': True,
                'analysis_type': 'correlation',
                'methods_analyzed': len(method_ids),
                'valid_method_ids': method_ids,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Revolutionary Correlation Analysis error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Revolutionary Correlation Analysis failed: {str(e)}',
                'error_type': 'correlation_analysis_error'
            }, status=500)

    def _handle_baseline_comparison(self, request, method_ids: List[str] = None) -> JsonResponse:
        """
        Handle Revolutionary Baseline Comparison
        
        Args:
            request: HTTP request
            method_ids: Pre-cleaned method IDs (optional)
            
        Returns:
            JsonResponse: Baseline comparison results
        """
        try:
            # ✅ USE PROVIDED METHOD IDS OR EXTRACT FROM REQUEST
            if method_ids is None:
                method_ids = request.GET.getlist('method_ids')
                method_ids = [
                    str(mid).strip() for mid in method_ids 
                    if mid and str(mid).strip() and str(mid).strip() not in ['-', '', 'null']
                ]
            
            if not method_ids:
                raise ValueError('No valid method IDs provided for baseline comparison')
            
            if not self.intelligence:
                raise RuntimeError('Revolutionary Intelligence System not initialized')
            
            # ✅ GET HISTORICAL DATA
            historical_data = self.intelligence._get_real_historical_data(
                method_ids, 
                datetime.now().strftime('%Y-%m-%d'), 
                12
            )
            
            if not historical_data:
                raise RuntimeError('Insufficient historical data for Revolutionary Baseline Comparison')
            
            # ✅ PERFORM REVOLUTIONARY BASELINE COMPARISON
            baseline_data = self.intelligence._real_baseline_comparison(
                historical_data, method_ids
            )
            
            return JsonResponse({
                'success': True,
                'baseline_comparison': baseline_data,
                'revolutionary': True,
                'analysis_type': 'baseline',
                'methods_analyzed': len(method_ids),
                'valid_method_ids': method_ids,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Revolutionary Baseline Comparison error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Revolutionary Baseline Comparison failed: {str(e)}',
                'error_type': 'baseline_comparison_error'
            }, status=500)

    def _handle_anomaly_detection(self, request, method_ids: List[str] = None) -> JsonResponse:
        """
        Handle Revolutionary Anomaly Detection
        
        Args:
            request: HTTP request
            method_ids: Pre-cleaned method IDs (optional)
            
        Returns:
            JsonResponse: Anomaly detection results
        """
        try:
            # ✅ USE PROVIDED METHOD IDS OR EXTRACT FROM REQUEST
            if method_ids is None:
                method_ids = request.GET.getlist('method_ids')
                method_ids = [
                    str(mid).strip() for mid in method_ids 
                    if mid and str(mid).strip() and str(mid).strip() not in ['-', '', 'null']
                ]
            
            if not method_ids:
                raise ValueError('No valid method IDs provided for anomaly detection')
            
            if not self.intelligence:
                raise RuntimeError('Revolutionary Intelligence System not initialized')
            
            # ✅ GET HISTORICAL DATA
            historical_data = self.intelligence._get_real_historical_data(
                method_ids, 
                datetime.now().strftime('%Y-%m-%d'), 
                12
            )
            
            if not historical_data:
                raise RuntimeError('Insufficient historical data for Revolutionary Anomaly Detection')
            
            # ✅ PERFORM REVOLUTIONARY ANOMALY DETECTION
            anomaly_data = self.intelligence._real_anomaly_detection(
                historical_data, method_ids
            )
            
            return JsonResponse({
                'success': True,
                'anomaly_detection': anomaly_data,
                'revolutionary': True,
                'analysis_type': 'anomaly',
                'methods_analyzed': len(method_ids),
                'valid_method_ids': method_ids,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Revolutionary Anomaly Detection error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Revolutionary Anomaly Detection failed: {str(e)}',
                'error_type': 'anomaly_detection_error'
            }, status=500)
    
    
       
        