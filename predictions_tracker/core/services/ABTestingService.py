import logging
import hashlib
from datetime import date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from django.db import models

logger = logging.getLogger(__name__)


class ABTestingService:
    """Service for A/B testing management và execution"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def create_ab_test(
        self,
        test_name: str,
        target_method_code: str,
        test_parameters: dict,
        baseline_parameters: dict,
        traffic_percentage: float = 50.0,
        test_duration_days: int = 30,
        success_criteria: dict = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Tạo A/B test mới
        
        Args:
            test_name: Tên test
            target_method_code: Code của method cần test
            test_parameters: Parameters được test
            baseline_parameters: Parameters baseline
            traffic_percentage: Phần trăm traffic cho variant
            test_duration_days: Thời gian test (ngày)
            success_criteria: Tiêu chí thành công
            created_by: Người tạo test
            
        Returns:
            dict: {
                "success": bool,
                "test_variant": {
                    "test_id": int,
                    "baseline_id": int,
                    "test_name": str,
                    "start_date": str,
                    "end_date": str,
                    "traffic_split": dict
                },
                "message": str
            }
        """
        try:
            # Import models trong method để tránh circular import
            from predictions_tracker.models import PredictionMethod, ABTestVariant
            
            self.logger.info(f"🧪 Creating A/B test: {test_name}")
            
            # Validate target method
            try:
                target_method = PredictionMethod.objects.get(code=target_method_code)
            except PredictionMethod.DoesNotExist:
                return {
                    "success": False,
                    "message": f"Method not found: {target_method_code}",
                    "test_variant": {}
                }
            
            # Validate success criteria
            if success_criteria is None:
                success_criteria = {
                    "min_accuracy": 0.05,  # 5% minimum
                    "min_improvement_percent": 10.0,  # 10% improvement
                    "max_p_value": 0.05  # 95% confidence
                }
            
            # Calculate test period
            start_date = date.today()
            end_date = start_date + timedelta(days=test_duration_days)
            
            # Create test variant
            test_variant = ABTestVariant.objects.create(
                test_name=test_name,
                variant_name="test_variant",
                target_method=target_method,
                test_parameters=test_parameters,
                baseline_parameters=baseline_parameters,
                start_date=start_date,
                end_date=end_date,
                traffic_percentage=traffic_percentage,
                status='active',
                created_by=created_by,
                success_criteria=success_criteria
            )
            
            # Create baseline variant
            baseline_variant = ABTestVariant.objects.create(
                test_name=test_name,
                variant_name="baseline",
                target_method=target_method,
                test_parameters=baseline_parameters,
                baseline_parameters=baseline_parameters,
                start_date=start_date,
                end_date=end_date,
                traffic_percentage=100.0 - traffic_percentage,
                status='active',
                created_by=created_by,
                success_criteria=success_criteria
            )
            
            self.logger.info(f"✅ A/B test created: {test_name}")
            
            return {
                "success": True,
                "test_variant": {
                    "test_id": test_variant.id,
                    "baseline_id": baseline_variant.id,
                    "test_name": test_name,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "traffic_split": {
                        "test": traffic_percentage,
                        "baseline": 100.0 - traffic_percentage
                    }
                },
                "message": "A/B test created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ A/B test creation failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to create A/B test: {str(e)}",
                "test_variant": {}
            }
    
    def execute_ab_test(
        self,
        test_date: date,
        method_code: str,
        predicted_numbers: list,
        actual_numbers: list
    ) -> Dict[str, Any]:
        """
        Thực thi A/B test cho ngày cụ thể
        
        Args:
            test_date: Ngày test
            method_code: Code của method
            predicted_numbers: Số dự đoán
            actual_numbers: Số thực tế
            
        Returns:
            dict: {
                "success": bool,
                "variant_used": str,
                "test_result": {
                    "variant_name": str,
                    "test_name": str,
                    "hit_count": int,
                    "total_predicted": int,
                    "accuracy_rate": float,
                    "hit_numbers": list,
                    "parameters_used": dict,
                    "confidence_interval": dict,
                    "is_successful": bool,
                    "success_details": dict
                },
                "message": str
            }
        """
        try:
            from predictions_tracker.models import PredictionMethod, ABTestVariant, ABTestResult
            
            self.logger.info(f"🔬 Executing A/B test for {method_code} on {test_date}")
            
            # Get target method
            try:
                target_method = PredictionMethod.objects.get(code=method_code)
            except PredictionMethod.DoesNotExist:
                return {
                    "success": False,
                    "message": f"Method not found: {method_code}",
                    "variant_used": "",
                    "test_result": {}
                }
            
            # Find active A/B test for this method
            active_variants = ABTestVariant.objects.filter(
                target_method=target_method,
                status='active',
                start_date__lte=test_date,
                end_date__gte=test_date
            )
            
            if not active_variants.exists():
                return {
                    "success": False,
                    "message": "No active A/B test found for this method",
                    "variant_used": "",
                    "test_result": {}
                }
            
            # Determine which variant to use (consistent hashing)
            request_id = f"{test_date.isoformat()}_{method_code}"
            selected_variant = self._select_variant_by_traffic(active_variants, request_id)
            
            if not selected_variant:
                return {
                    "success": False,
                    "message": "Failed to select A/B test variant",
                    "variant_used": "",
                    "test_result": {}
                }
            
            # Create test result
            session_id = f"{test_date.isoformat()}_{method_code}_{selected_variant.variant_name}"
            
            test_result = ABTestResult.objects.create(
                variant=selected_variant,
                test_date=test_date,
                session_id=session_id,
                predicted_numbers=predicted_numbers,
                actual_numbers=actual_numbers
            )
            
            # Get performance data
            performance_data = {
                "variant_name": selected_variant.variant_name,
                "test_name": selected_variant.test_name,
                "hit_count": test_result.hit_count,
                "total_predicted": test_result.total_predicted,
                "accuracy_rate": test_result.accuracy_rate,
                "hit_numbers": test_result.hit_numbers,
                "parameters_used": selected_variant.test_parameters,
                "confidence_interval": {
                    "lower": test_result.confidence_interval_lower,
                    "upper": test_result.confidence_interval_upper
                },
                "is_successful": test_result.is_successful,
                "success_details": test_result.success_details
            }
            
            self.logger.info(f"✅ A/B test executed: {selected_variant.variant_name} - Accuracy: {test_result.accuracy_rate:.2%}")
            
            return {
                "success": True,
                "variant_used": selected_variant.variant_name,
                "test_result": performance_data,
                "message": "A/B test executed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ A/B test execution failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"A/B test execution failed: {str(e)}",
                "variant_used": "",
                "test_result": {}
            }
    
    def _select_variant_by_traffic(self, variants, request_id: str):
        """
        Select variant based on traffic allocation using consistent hashing
        
        Args:
            variants: QuerySet of ABTestVariant
            request_id: Unique identifier for request
            
        Returns:
            ABTestVariant or None
        """
        try:
            # Sort variants by traffic percentage for consistent selection
            sorted_variants = list(variants.order_by('traffic_percentage'))
            
            # Use consistent hashing to determine variant
            for variant in sorted_variants:
                if variant.should_serve_traffic(request_id):
                    return variant
            
            # Fallback to first variant
            return sorted_variants[0] if sorted_variants else None
            
        except Exception as e:
            self.logger.error(f"Variant selection error: {str(e)}")
            return None
    
    def get_ab_test_results(
        self,
        test_name: str = None,
        method_code: str = None,
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, Any]:
        """
        Lấy kết quả A/B test
        
        Args:
            test_name: Tên test (optional)
            method_code: Code method (optional)
            start_date: Ngày bắt đầu (optional)
            end_date: Ngày kết thúc (optional)
            
        Returns:
            dict: {
                "success": bool,
                "test_results": list,
                "summary": {
                    "total_tests": int,
                    "avg_accuracy": float,
                    "success_rate": float,
                    "successful_tests": int,
                    "by_variant": dict
                },
                "message": str
            }
        """
        try:
            from predictions_tracker.models import PredictionMethod, ABTestVariant, ABTestResult
            
            self.logger.info("📊 Getting A/B test results")
            
            # Build query filters
            filters = Q()
            
            if test_name:
                filters &= Q(variant__test_name=test_name)
            
            if method_code:
                try:
                    target_method = PredictionMethod.objects.get(code=method_code)
                    filters &= Q(variant__target_method=target_method)
                except PredictionMethod.DoesNotExist:
                    return {
                        "success": False,
                        "message": f"Method not found: {method_code}",
                        "test_results": [],
                        "summary": {}
                    }
            
            if start_date:
                filters &= Q(test_date__gte=start_date)
            
            if end_date:
                filters &= Q(test_date__lte=end_date)
            
            # Get test results
            test_results = ABTestResult.objects.filter(filters).select_related(
                'variant', 'variant__target_method'
            ).order_by('-test_date', 'variant__test_name')
            
            # Format results
            formatted_results = []
            for result in test_results:
                formatted_results.append({
                    "test_name": result.variant.test_name,
                    "variant_name": result.variant.variant_name,
                    "method_name": result.variant.target_method.name,
                    "test_date": result.test_date.isoformat(),
                    "accuracy_rate": result.accuracy_rate,
                    "hit_count": result.hit_count,
                    "total_predicted": result.total_predicted,
                    "is_successful": result.is_successful,
                    "parameters": result.variant.test_parameters,
                    "confidence_interval": {
                        "lower": result.confidence_interval_lower,
                        "upper": result.confidence_interval_upper
                    }
                })
            
            # Calculate summary statistics
            summary = self._calculate_test_summary(test_results)
            
            return {
                "success": True,
                "test_results": formatted_results,
                "summary": summary,
                "message": f"Found {len(formatted_results)} test results"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get A/B test results: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to get test results: {str(e)}",
                "test_results": [],
                "summary": {}
            }
    
    def _calculate_test_summary(self, test_results) -> Dict[str, Any]:
        """
        Calculate summary statistics for test results
        
        Args:
            test_results: QuerySet of ABTestResult
            
        Returns:
            dict: {
                "total_tests": int,
                "avg_accuracy": float,
                "success_rate": float,
                "successful_tests": int,
                "by_variant": dict
            }
        """
        try:
            if not test_results:
                return {
                    "total_tests": 0,
                    "avg_accuracy": 0.0,
                    "success_rate": 0.0,
                    "successful_tests": 0,
                    "by_variant": {}
                }
            
            # Overall statistics
            total_tests = test_results.count()
            avg_accuracy = test_results.aggregate(avg_acc=Avg('accuracy_rate'))['avg_acc'] or 0
            successful_tests = test_results.filter(is_successful=True).count()
            success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            
            # By variant statistics
            by_variant = {}
            variant_stats = test_results.values('variant__variant_name').annotate(
                count=Count('id'),
                avg_accuracy=Avg('accuracy_rate'),
                success_count=Count('id', filter=Q(is_successful=True))
            )
            
            for stat in variant_stats:
                variant_name = stat['variant__variant_name']
                variant_success_rate = (stat['success_count'] / stat['count']) * 100 if stat['count'] > 0 else 0
                
                by_variant[variant_name] = {
                    "total_tests": stat['count'],
                    "avg_accuracy": round(stat['avg_accuracy'], 4),
                    "success_rate": round(variant_success_rate, 2),
                    "successful_tests": stat['success_count']
                }
            
            return {
                "total_tests": total_tests,
                "avg_accuracy": round(avg_accuracy, 4),
                "success_rate": round(success_rate, 2),
                "successful_tests": successful_tests,
                "by_variant": by_variant
            }
            
        except Exception as e:
            self.logger.error(f"Summary calculation error: {str(e)}")
            return {
                "total_tests": 0,
                "avg_accuracy": 0.0,
                "success_rate": 0.0,
                "successful_tests": 0,
                "by_variant": {}
            }
    
    def compare_variants(
        self,
        test_name: str,
        baseline_variant: str = "baseline",
        test_variant: str = "test_variant"
    ) -> Dict[str, Any]:
        """
        So sánh performance giữa các variants
        
        Args:
            test_name: Tên test
            baseline_variant: Tên baseline variant
            test_variant: Tên test variant
            
        Returns:
            dict: {
                "success": bool,
                "comparison": {
                    "baseline": dict,
                    "test_variant": dict,
                    "improvement": dict
                },
                "statistical_significance": dict,
                "recommendation": str,
                "message": str
            }
        """
        try:
            from predictions_tracker.models import ABTestResult
            
            self.logger.info(f"📊 Comparing variants for test: {test_name}")
            
            # Get baseline results
            baseline_results = ABTestResult.objects.filter(
                variant__test_name=test_name,
                variant__variant_name=baseline_variant
            )
            
            # Get test variant results
            test_results = ABTestResult.objects.filter(
                variant__test_name=test_name,
                variant__variant_name=test_variant
            )
            
            if not baseline_results.exists() or not test_results.exists():
                return {
                    "success": False,
                    "message": "Insufficient data for comparison",
                    "comparison": {},
                    "statistical_significance": {},
                    "recommendation": "Need more data"
                }
            
            # Calculate metrics for each variant
            baseline_stats = self._calculate_variant_stats(baseline_results)
            test_stats = self._calculate_variant_stats(test_results)
            
            # Calculate improvement
            accuracy_improvement = (
                (test_stats['avg_accuracy'] - baseline_stats['avg_accuracy']) / 
                baseline_stats['avg_accuracy'] * 100
            ) if baseline_stats['avg_accuracy'] > 0 else 0
            
            # Statistical significance test
            significance_test = self._calculate_statistical_significance(
                baseline_results, test_results
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                accuracy_improvement, significance_test, test_stats, baseline_stats
            )
            
            comparison_result = {
                "baseline": baseline_stats,
                "test_variant": test_stats,
                "improvement": {
                    "accuracy_improvement_percent": round(accuracy_improvement, 2),
                    "absolute_improvement": round(
                        test_stats['avg_accuracy'] - baseline_stats['avg_accuracy'], 4
                    )
                }
            }
            
            return {
                "success": True,
                "comparison": comparison_result,
                "statistical_significance": significance_test,
                "recommendation": recommendation,
                "message": "Variant comparison completed"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Variant comparison failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Comparison failed: {str(e)}",
                "comparison": {},
                "statistical_significance": {},
                "recommendation": "Error in analysis"
            }
    
    def _calculate_variant_stats(self, results) -> Dict[str, Any]:
        """
        Calculate statistics for variant results
        
        Args:
            results: QuerySet of ABTestResult
            
        Returns:
            dict: {
                "total_tests": int,
                "avg_accuracy": float,
                "overall_accuracy": float,
                "success_rate": float,
                "total_hits": int,
                "total_predictions": int
            }
        """
        stats = results.aggregate(
            count=Count('id'),
            avg_accuracy=Avg('accuracy_rate'),
            success_count=Count('id', filter=Q(is_successful=True)),
            total_hits=Sum('hit_count'),
            total_predictions=Sum('total_predicted')
        )
        
        success_rate = (stats['success_count'] / stats['count']) * 100 if stats['count'] > 0 else 0
        overall_accuracy = (stats['total_hits'] / stats['total_predictions']) if stats['total_predictions'] > 0 else 0
        
        return {
            "total_tests": stats['count'],
            "avg_accuracy": round(stats['avg_accuracy'] or 0, 4),
            "overall_accuracy": round(overall_accuracy, 4),
            "success_rate": round(success_rate, 2),
            "total_hits": stats['total_hits'] or 0,
            "total_predictions": stats['total_predictions'] or 0
        }
    
    def _calculate_statistical_significance(self, baseline_results, test_results) -> Dict[str, Any]:
        """
        Calculate statistical significance between variants
        
        Args:
            baseline_results: QuerySet of baseline ABTestResult
            test_results: QuerySet of test ABTestResult
            
        Returns:
            dict: Statistical significance metrics
        """
        try:
            # Get aggregated data
            baseline_stats = baseline_results.aggregate(
                total_hits=Sum('hit_count'),
                total_predictions=Sum('total_predicted')
            )
            
            test_stats = test_results.aggregate(
                total_hits=Sum('hit_count'),
                total_predictions=Sum('total_predicted')
            )
            
            # Try to use scipy for proper statistical test
            try:
                from scipy import stats
                
                # Two-proportion z-test
                count1 = test_stats['total_hits'] or 0
                nobs1 = test_stats['total_predictions'] or 1
                count2 = baseline_stats['total_hits'] or 0
                nobs2 = baseline_stats['total_predictions'] or 1
                
                if nobs1 > 0 and nobs2 > 0:
                    z_stat, p_value = stats.proportions_ztest([count1, count2], [nobs1, nobs2])
                    
                    return {
                        "z_statistic": round(z_stat, 4),
                        "p_value": round(p_value, 6),
                        "is_significant": p_value < 0.05,
                        "confidence_level": "95%",
                        "test_type": "two_proportion_z_test"
                    }
                    
            except ImportError:
                self.logger.warning("scipy not available, using simplified significance test")
            
            # Simplified significance test
            baseline_rate = (baseline_stats['total_hits'] or 0) / (baseline_stats['total_predictions'] or 1)
            test_rate = (test_stats['total_hits'] or 0) / (test_stats['total_predictions'] or 1)
            
            # Simple difference threshold
            difference = abs(test_rate - baseline_rate)
            is_significant = difference > 0.02  # 2% difference threshold
            
            return {
                "difference": round(difference, 4),
                "is_significant": is_significant,
                "test_type": "simplified_difference_test",
                "threshold": 0.02
            }
            
        except Exception as e:
            self.logger.error(f"Statistical significance calculation error: {str(e)}")
            return {
                "error": str(e),
                "is_significant": False,
                "test_type": "error"
            }
    
    def _generate_recommendation(
        self, 
        improvement: float, 
        significance: Dict[str, Any], 
        test_stats: Dict[str, Any], 
        baseline_stats: Dict[str, Any]
    ) -> str:
        """
        Generate recommendation based on test results
        
        Args:
            improvement: Improvement percentage
            significance: Statistical significance data
            test_stats: Test variant statistics
            baseline_stats: Baseline variant statistics
            
        Returns:
            str: Recommendation message
        """
        try:
            # Check statistical significance
            is_significant = significance.get('is_significant', False)
            
            # Check practical significance (improvement)
            meaningful_improvement = improvement > 10.0  # 10% improvement threshold
            
            # Check sample size adequacy
            adequate_sample = test_stats['total_tests'] >= 30 and baseline_stats['total_tests'] >= 30
            
            if is_significant and meaningful_improvement and adequate_sample:
                return "DEPLOY: Test variant shows significant and meaningful improvement"
            elif is_significant and meaningful_improvement:
                return "CONTINUE: Promising results, but need more data for confidence"
            elif is_significant and not meaningful_improvement:
                return "NEUTRAL: Statistically significant but practically insignificant improvement"
            elif meaningful_improvement and not is_significant:
                return "CONTINUE: Good improvement but not statistically significant yet"
            elif improvement < -5.0:  # 5% degradation
                return "STOP: Test variant shows degradation in performance"
            else:
                return "CONTINUE: Inconclusive results, continue testing"
                
        except Exception:
            return "ERROR: Unable to generate recommendation"
    
    def conclude_ab_test(self, test_name: str, conclusion: str = "auto") -> Dict[str, Any]:
        """
        Kết luận và đóng A/B test
        
        Args:
            test_name: Tên test
            conclusion: "auto", "deploy_test", "keep_baseline", "continue"
            
        Returns:
            dict: {
                "success": bool,
                "conclusion": str,
                "final_results": dict,
                "message": str
            }
        """
        try:
            from predictions_tracker.models import ABTestVariant
            
            self.logger.info(f"🏁 Concluding A/B test: {test_name}")
            
            # Get test variants
            variants = ABTestVariant.objects.filter(test_name=test_name, status='active')
            
            if not variants.exists():
                return {
                    "success": False,
                    "message": f"No active test found: {test_name}",
                    "conclusion": "",
                    "final_results": {}
                }
            
            # Get comparison results if auto conclusion
            if conclusion == "auto":
                comparison = self.compare_variants(test_name)
                if comparison["success"]:
                    recommendation = comparison["recommendation"]
                    if "DEPLOY" in recommendation:
                        conclusion = "deploy_test"
                    elif "STOP" in recommendation:
                        conclusion = "keep_baseline"
                    else:
                        conclusion = "continue"
                else:
                    conclusion = "continue"
            
            # Update variant status based on conclusion
            if conclusion in ["deploy_test", "keep_baseline"]:
                variants.update(status='completed')
                
                final_status = {
                    "conclusion": conclusion,
                    "completed_at": timezone.now().isoformat(),
                    "variants_count": variants.count(),
                    "test_duration": (variants.first().end_date - variants.first().start_date).days
                }
                
                # Get final comparison
                final_comparison = self.compare_variants(test_name)
                
                return {
                    "success": True,
                    "conclusion": conclusion,
                    "final_results": {
                        "status": final_status,
                        "comparison": final_comparison.get("comparison", {}),
                        "recommendation": final_comparison.get("recommendation", "")
                    },
                    "message": f"A/B test concluded with decision: {conclusion}"
                }
            else:
                return {
                    "success": True,
                    "conclusion": "continue",
                    "final_results": {"status": "ongoing"},
                    "message": "A/B test will continue running"
                }
                
        except Exception as e:
            self.logger.error(f"❌ A/B test conclusion failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to conclude test: {str(e)}",
                "conclusion": "",
                "final_results": {}
            }


# Service instance
ab_testing_service = ABTestingService()