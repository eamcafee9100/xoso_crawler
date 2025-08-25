class PredictionService:
    """Service class for prediction-related operations"""
    
    def combine_predictions(self, shap_prediction, method_predictions):
        """
        Kết hợp dự đoán từ SHAP và các phương pháp khác nhau
        
        Args:
            shap_prediction: Dự đoán từ mô hình SHAP
            method_predictions: Danh sách dự đoán từ các phương pháp khác
        
        Returns:
            List các cặp (số, điểm) đã kết hợp
        """
        try:
            # Log thông tin đầu vào
            has_shap = shap_prediction is not None
            method_count = len(method_predictions) if method_predictions else 0
            logger.info(f"Combining predictions: has_shap={has_shap}, method_count={method_count}")
            
            # Dict để tổng hợp điểm số
            combined_scores = {}
            
            # Thêm điểm từ dự đoán SHAP
            if shap_prediction and isinstance(shap_prediction, dict):
                if 'predicted_numbers' in shap_prediction and shap_prediction['predicted_numbers']:
                    shap_numbers = shap_prediction['predicted_numbers']
                    confidence_scores = shap_prediction.get('confidence_scores', {})
                    
                    for num in shap_numbers:
                        try:
                            num_str = str(num).zfill(2)
                            # Điểm cơ bản cho SHAP là cao hơn
                            base_score = 0.75
                            # Dùng điểm tin cậy từ SHAP nếu có
                            if num in confidence_scores:
                                base_score = confidence_scores[num]
                            # Thêm vào combined_scores với trọng số cao hơn vì đến từ mô hình ML
                            combined_scores[num_str] = combined_scores.get(num_str, 0) + (base_score * 1.5)
                        except Exception as e:
                            logger.warning(f"Error processing SHAP number {num}: {e}")
                            continue
            
            # Thêm điểm từ các phương pháp dự đoán
            if method_predictions and isinstance(method_predictions, list):
                # Tính tổng trọng số
                total_weight = sum(method.get('weight', 0.5) for method in method_predictions)
                # Nếu tổng trọng số = 0, sử dụng trọng số đồng đều
                if total_weight == 0:
                    total_weight = len(method_predictions) * 0.5
                    
                for method in method_predictions:
                    if 'numbers' not in method or not method['numbers']:
                        continue
                        
                    # Lấy thông tin phương pháp
                    method_weight = method.get('weight', 0.5)
                    method_confidence = method.get('confidence', 0.6)
                    confidence_scores = method.get('confidence_scores', {})
                    
                    # Chuẩn hóa trọng số
                    normalized_weight = method_weight / total_weight if total_weight > 0 else 1.0 / len(method_predictions)
                    
                    for num in method['numbers']:
                        try:
                            num_str = str(num).zfill(2)
                            
                            # Tính điểm dựa trên độ tin cậy và trọng số phương pháp
                            num_confidence = confidence_scores.get(num, method_confidence)
                            score = num_confidence * normalized_weight
                            
                            # Thêm vào combined_scores
                            combined_scores[num_str] = combined_scores.get(num_str, 0) + score
                        except Exception as e:
                            logger.warning(f"Error processing method number {num}: {e}")
                            continue
            
            # Kiểm tra nếu combined_scores rỗng
            if not combined_scores:
                logger.warning("No valid scores were combined")
                # Tạo dữ liệu dự phòng
                for i in range(10, 100, 10):
                    num_str = f"{i:02d}"
                    combined_scores[num_str] = 0.5
            
            # Sắp xếp theo điểm giảm dần
            sorted_scores = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Lấy top 20 số có điểm cao nhất
            result = sorted_scores[:20]
            
            logger.info(f"Combined {len(result)} numbers with scores")
            return result
            
        except Exception as e:
            logger.error(f"Error combining predictions: {e}", exc_info=True)
            # Trả về dữ liệu dự phòng trong trường hợp lỗi
            fallback_result = [(f"{i:02d}", 0.5) for i in range(10, 100, 10)][:10]
            logger.info(f"Returning {len(fallback_result)} fallback combined numbers")
            return fallback_result

    def calculate_accuracy(self, prediction):
        """
        Calculate accuracy of a prediction
        
        Args:
            prediction: Prediction object with actual_result
            
        Returns:
            Accuracy as a float or None if not calculable
        """
        if not prediction or not hasattr(prediction, 'actual_result'):
            return None
            
        try:
            actual_numbers = set(prediction.actual_result.get_all_2digit_numbers())
            predicted_numbers = set(str(num).zfill(2) for num in prediction.predicted_numbers)
            correct = len(actual_numbers & predicted_numbers)
            return correct / len(predicted_numbers) if predicted_numbers else 0
        except Exception as e:
            logger.error(f"Error calculating accuracy: {e}")
            return None
    
    def calculate_method_accuracy(self, enhanced_pred):
        """
        Calculate accuracy for a specific method
        
        Args:
            enhanced_pred: Enhanced prediction object
            
        Returns:
            Accuracy as a float or None if not calculable
        """
        try:
            if not enhanced_pred or not hasattr(enhanced_pred, 'date'):
                return None
                
            actual_result = KetQuaXoSo.objects.get(ngay=enhanced_pred.date)
            actual_numbers = set(actual_result.get_all_2digit_numbers())
            predicted_numbers = set(enhanced_pred.numbers)
            correct = len(actual_numbers & predicted_numbers)
            return correct / len(predicted_numbers) if predicted_numbers else 0
        except (KetQuaXoSo.DoesNotExist, AttributeError) as e:
            logger.error(f"Error calculating method accuracy: {e}")
            return None
    
    def generate_combined_suggestions(self, shap_pred, enhanced_preds):
        """
        Generate high-potential number pairs
        
        Args:
            shap_pred: SHAP prediction object
            enhanced_preds: List of enhanced prediction objects
            
        Returns:
            List of pair suggestions with scores
        """
        pair_scores = defaultdict(float)
        all_numbers = set()
        
        # Add points from SHAP
        if shap_pred and hasattr(shap_pred, 'predicted_numbers'):
            shap_numbers = [str(num).zfill(2) for num in shap_pred.predicted_numbers]
            all_numbers.update(shap_numbers)
            for a, b in combinations(shap_numbers, 2):
                pair_scores[(a, b)] += 0.3
        
        # Add points from other methods
        for pred in enhanced_preds:
            if hasattr(pred, 'numbers') and hasattr(pred, 'confidence_scores'):
                for num in pred.numbers:
                    all_numbers.add(num)
                for a, b in combinations(pred.numbers, 2):
                    pair_scores[(a, b)] += pred.confidence_scores.get(a, 0.1) * pred.confidence_scores.get(b, 0.1)
        
        # Sort and select top pairs
        sorted_pairs = sorted(pair_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [
            {'numbers': pair, 'strength': score}
            for pair, score in sorted_pairs
        ]
    
    def get_recommended_method(self):
        """
        Analyze and recommend the best prediction method
        
        Returns:
            Dict with best method and comparison data, or None
        """
        try:
            methods = PredictionMethod.objects.annotate(
                avg_accuracy=Avg(
                    'enhancedprediction__accuracy',
                    filter=Q(enhancedprediction__accuracy__isnull=False)
                )
            ).exclude(avg_accuracy__isnull=True).order_by('-avg_accuracy')
            
            if methods.exists():
                return {
                    'best_method': methods.first(),
                    'comparison_data': [
                        {'name': m.name, 'accuracy': m.avg_accuracy}
                        for m in methods
                    ]
                }
        except Exception as e:
            logger.error(f"Error getting recommended method: {e}")
            
        return None
    
    def get_number_distribution(self, predictions_list):
        """
        Get distribution of numbers across all predictions
        
        Args:
            predictions_list: List of prediction objects
            
        Returns:
            Dict mapping numbers to occurrence count
        """
        distribution = defaultdict(int)
        
        for pred in predictions_list:
            if hasattr(pred, 'numbers'):
                for num in pred.numbers:
                    distribution[num] += 1
        
        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
    
    def calculate_performance_metrics(self, predictions, actual_numbers):
        """
        Calculate comprehensive performance metrics
        
        Args:
            predictions: List of predicted numbers
            actual_numbers: List of actual numbers
            
        Returns:
            Dict with various performance metrics
        """
        if not predictions or not actual_numbers:
            return {
                'accuracy': 0,
                'precision': 0,
                'recall': 0,
                'f1_score': 0,
                'hit_count': 0,
                'total_predicted': len(predictions) if predictions else 0,
                'total_actual': len(actual_numbers) if actual_numbers else 0
            }
            
        pred_set = set(predictions)
        actual_set = set(actual_numbers)
        correct = len(pred_set.intersection(actual_set))
        
        precision = correct / len(pred_set) if pred_set else 0
        recall = correct / len(actual_set) if actual_set else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'accuracy': precision * 100,  # Traditional accuracy
            'precision': precision * 100,
            'recall': recall * 100,
            'f1_score': f1_score * 100,
            'hit_count': correct,
            'total_predicted': len(pred_set),
            'total_actual': len(actual_set)
        }
