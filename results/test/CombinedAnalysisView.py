class CombinedAnalysisView(TemplateView):
    template_name = 'results/combined_analysis.html'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prediction_service = PredictionService()
    
    def _get_selected_date(self):
        """Get selected date from request or return today's date"""
        try:
            date_str = self.request.GET.get('selected_date')
            if date_str:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            return datetime.now().date()
        except Exception as e:
            logging.error(f"Error parsing date: {str(e)}")
            return datetime.now().date()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Khởi tạo trạng thái xử lý
        context['processing_stages'] = {
            'initialization': {'status': 'pending', 'message': 'Initializing analysis...'},
            'data_retrieval': {'status': 'pending', 'message': 'Retrieving historical data...'},
            'historical_analysis': {'status': 'pending', 'message': 'Analyzing historical data...'},
            'shap_analysis': {'status': 'pending', 'message': 'Performing SHAP analysis...'},
            'predictions': {'status': 'pending', 'message': 'Generating predictions...'},
            'pattern_analysis': {'status': 'pending', 'message': 'Analyzing patterns...'},
            'optimization': {'status': 'pending', 'message': 'Optimizing predictions...'},
            'combination': {'status': 'pending', 'message': 'Combining results...'}
        }
        
        try:
            # Đánh dấu khởi tạo hoàn thành
            context['processing_stages']['initialization'] = {'status': 'complete', 'message': 'Initialization complete'}
            
            # Lấy ngày được chọn và tính ngày mục tiêu
            selected_date = self._get_selected_date()
            target_date = selected_date + timedelta(days=1)
            history_days = int(self.request.GET.get('days', 90))
            
            # Tạo cache key
            cache_key = f"combined_analysis_{selected_date}_{history_days}"
            cached_data = cache.get(cache_key)
            
            # Sử dụng dữ liệu cache nếu có
            if cached_data:
                logger.info(f"Using cached data for {selected_date}")
                context.update(cached_data)
                
                # Đánh dấu tất cả các giai đoạn là hoàn thành khi sử dụng cache
                for stage in context['processing_stages']:
                    context['processing_stages'][stage] = {'status': 'complete', 'message': f'{stage} complete (cached)'}
                
                return context
            
            # Đánh dấu giai đoạn truy xuất dữ liệu đang tiến hành
            context['processing_stages']['data_retrieval'] = {'status': 'in_progress', 'message': 'Retrieving data...'}
            
            # Khởi tạo predictor
            predictor = BachThuLoPredictor(
                target_date=target_date,
                history_days=history_days,
                selected_date=selected_date
            )
            
            # Lấy dữ liệu lịch sử
            historical_data = self._get_historical_data_before_date(selected_date)
            
            # Đánh dấu giai đoạn truy xuất dữ liệu hoàn thành
            context['processing_stages']['data_retrieval'] = {'status': 'complete', 'message': 'Data retrieved successfully'}
            
            # Phân tích lịch sử
            context['processing_stages']['historical_analysis'] = {'status': 'in_progress', 'message': 'Analyzing historical data...'}
            historical_accuracy = self._analyze_historical_accuracy(historical_data)
            context['historical_accuracy'] = historical_accuracy
            context['processing_stages']['historical_analysis'] = {'status': 'complete', 'message': 'Historical analysis complete'}
            
            # Phân tích SHAP
            context['processing_stages']['shap_analysis'] = {'status': 'in_progress', 'message': 'Calculating SHAP values...'}
            
            # Thử lấy SHAP prediction từ predictor trước
            shap_prediction = None
            if hasattr(predictor, 'get_shap_prediction'):
                try:
                    logger.info("Calling predictor.get_shap_prediction()")
                    shap_prediction = predictor.get_shap_prediction()
                    
                    if shap_prediction:
                        logger.info(f"Predictor returned SHAP prediction with {len(shap_prediction.get('predicted_numbers', []))} numbers")
                        context['shap_prediction'] = shap_prediction
                        # Nếu có shap_values trong shap_prediction, trích xuất thông tin SHAP
                        if 'shap_values' in shap_prediction and 'base_value' in shap_prediction:
                            shap_analysis = {
                                'shap_values': shap_prediction['shap_values'],
                                'feature_names': shap_prediction.get('feature_names', ['Feature 1', 'Feature 2', 'Feature 3']),
                                'base_value': shap_prediction['base_value'],
                                'feature_importance': {
                                    'values': {}  # Sẽ được tính sau
                                }
                            }
                            
                            # Thử tính feature importance nếu có đủ dữ liệu
                            if isinstance(shap_prediction['shap_values'], list) and len(shap_prediction['shap_values']) > 0:
                                import numpy as np
                                shap_values = np.array(shap_prediction['shap_values'])
                                for i, name in enumerate(shap_analysis['feature_names']):
                                    if i < shap_values.shape[1]:
                                        shap_analysis['feature_importance']['values'][name] = float(np.abs(shap_values[:, i]).mean())
                                
                                # Thêm mô tả
                                top_features = sorted(
                                    shap_analysis['feature_importance']['values'].items(),
                                    key=lambda x: abs(x[1]),
                                    reverse=True
                                )[:5]
                                
                                shap_analysis['feature_importance']['description'] = self._get_feature_importance_description(top_features)
                            
                            context['shap_analysis'] = shap_analysis
                            context['processing_stages']['shap_analysis'] = {'status': 'complete', 'message': 'SHAP analysis from predictor complete'}
                        else:
                            logger.warning("shap_prediction doesn't contain shap_values or base_value")
                    else:
                        logger.warning("predictor.get_shap_prediction() returned None or empty")
                except Exception as e:
                    logger.error(f"Error getting SHAP prediction from predictor: {e}", exc_info=True)
            
            # Nếu không có SHAP prediction từ predictor, tạo bằng phương thức của view
            if not shap_prediction or 'shap_analysis' not in context:
                try:
                    shap_analysis = self._calculate_shap_analysis(predictor, selected_date)
                    if shap_analysis:
                        context['shap_analysis'] = shap_analysis
                        
                        # Tạo shap_prediction nếu chưa có
                        if not shap_prediction:
                            # Dự đoán số từ SHAP model
                            shap_numbers = self._predict_from_shap_model(self.model, selected_date) if hasattr(self, 'model') else []
                            
                            # Nếu không có kết quả, lấy từ predict_frequency
                            if not shap_numbers and hasattr(predictor, 'predict_frequency'):
                                shap_numbers = predictor.predict_frequency()[:5]
                            
                            if shap_numbers:
                                context['shap_prediction'] = {
                                    'predicted_numbers': shap_numbers,
                                    'confidence_scores': {num: 0.7 for num in shap_numbers},
                                    'shap_values': shap_analysis.get('shap_values', []),
                                    'base_value': shap_analysis.get('base_value', 0),
                                    'feature_names': shap_analysis.get('feature_names', [])
                                }
                        
                        context['processing_stages']['shap_analysis'] = {'status': 'complete', 'message': 'SHAP analysis complete'}
                    else:
                        context['processing_stages']['shap_analysis'] = {'status': 'warning', 'message': 'SHAP analysis failed'}
                except Exception as e:
                    logger.error(f"Error in SHAP analysis: {e}", exc_info=True)
                    context['processing_stages']['shap_analysis'] = {'status': 'failed', 'message': f'SHAP analysis failed: {str(e)}'}
            
            # Bắt đầu tạo dự đoán
            context['processing_stages']['predictions'] = {'status': 'in_progress', 'message': 'Generating predictions...'}
            
            # Lấy dự đoán từ predictor
            predictions = predictor.predict()
            context['best_predictions'] = predictions
            
            if not predictions:
                logger.warning("predictor.predict() returned empty or None")
                # Thử gọi trực tiếp vào các phương thức dự đoán cụ thể của predictor
                try:
                    direct_predictions = {}
                    # Kiểm tra tất cả các phương pháp dự đoán
                    prediction_methods = [
                        'predict_frequency', 'predict_recent', 'predict_shadow', 
                        'predict_region', 'predict_cycle'
                    ]
                    method_names = {
                        'predict_frequency': 'tan_so_cao',
                        'predict_recent': 'lap_lai_gan_nhat',
                        'predict_shadow': 'bong_so',
                        'predict_region': 'khu_vuc',
                        'predict_cycle': 'chu_ky'
                    }
                    
                    for method in prediction_methods:
                        if hasattr(predictor, method):
                            try:
                                result = getattr(predictor, method)()
                                if result:
                                    method_key = method_names.get(method, method)
                                    direct_predictions[method_key] = result
                                    logger.info(f"Method {method} returned {len(result)} predictions")
                            except Exception as method_error:
                                logger.error(f"Error calling {method}: {method_error}", exc_info=True)
                    
                    logger.info(f"Direct method calls returned: {direct_predictions}")
                    if direct_predictions:
                        # Tính trọng số nếu có thể
                        weights = {}
                        if hasattr(predictor, 'calculate_method_weights'):
                            try:
                                weights = predictor.calculate_method_weights()
                            except Exception as weight_error:
                                logger.error(f"Error calculating weights: {weight_error}")
                                weights = {key: 0.6 for key in direct_predictions.keys()}
                        else:
                            weights = {key: 0.6 for key in direct_predictions.keys()}
                        
                        # Tính kết quả kết hợp nếu có thể
                        combined_results = []
                        if hasattr(predictor, 'calculate_combined_numbers'):
                            try:
                                combined_results = predictor.calculate_combined_numbers(direct_predictions, weights)
                            except Exception as combine_error:
                                logger.error(f"Error combining results: {combine_error}")
                        
                        predictions = {
                            'predictions': direct_predictions,
                            'method_weights': weights,
                            'recommended_numbers': combined_results
                        }
                except Exception as inner_e:
                    logger.error(f"Error calling direct prediction methods: {inner_e}", exc_info=True)
            
            context['best_predictions'] = predictions
            
            # Đánh dấu giai đoạn dự đoán hoàn thành
            context['processing_stages']['predictions'] = {'status': 'complete', 'message': 'Predictions generated successfully'}
            
            # Phân tích mẫu số
            context['processing_stages']['pattern_analysis'] = {'status': 'in_progress', 'message': 'Analyzing patterns...'}
            pattern_analysis = self._analyze_prediction_patterns(predictions, historical_data)
            context['pattern_analysis'] = pattern_analysis
            context['processing_stages']['pattern_analysis'] = {'status': 'complete', 'message': 'Pattern analysis complete'}
            
            # Tối ưu hóa dự đoán
            context['processing_stages']['optimization'] = {'status': 'in_progress', 'message': 'Optimizing predictions...'}
            
            # Format method predictions
            method_predictions = []
            methods_data = {
                'lap_lai_gan_nhat': ('Lặp lại gần nhất', 0.80),
                'tan_so_cao': ('Tần suất cao', 0.54),
                'bong_so': ('Bóng số', 0.85),
                'khu_vuc': ('Khu vực', 0.75),
                'khu_vuc_nang_cao': ('Khu vực nâng cao', 0.90),
                'chu_ky': ('Chu kỳ', 0.85)
            }
            
            # Cập nhật trọng số dựa trên phân tích lịch sử
            if historical_accuracy and 'methods' in historical_accuracy:
                for method_key in methods_data.keys():
                    if method_key in historical_accuracy['methods']:
                        hit_rate = historical_accuracy['methods'][method_key]['hit_rate']
                        if hit_rate > 0:
                            # Cập nhật độ tin cậy dựa trên hiệu suất lịch sử
                            methods_data[method_key] = (methods_data[method_key][0], min(0.95, hit_rate / 100))

            # Ghi log cho mục đích debug
            logger.info(f"Predictions keys: {list(predictions.get('predictions', {}).keys())}")
            logger.info(f"Methods data keys: {list(methods_data.keys())}")

            # Định dạng dự đoán cho mỗi phương pháp
            for method, prediction in predictions.get('predictions', {}).items():
                if method in methods_data and prediction:  # Thêm kiểm tra prediction không rỗng
                    name, confidence = methods_data[method]
                    numbers = prediction[0] if isinstance(prediction, tuple) else prediction
                    
                    # Kiểm tra numbers có dữ liệu hợp lệ không
                    if not numbers:
                        logger.warning(f"Method {method} returned empty numbers, skipping")
                        continue
                        
                    # Đảm bảo numbers là list chuỗi 2 chữ số
                    processed_numbers = []
                    for num in numbers:
                        try:
                            # Chuyển đổi sang chuỗi 2 chữ số
                            num_str = str(num).zfill(2)
                            processed_numbers.append(num_str)
                        except Exception as e:
                            logger.warning(f"Error processing number {num}: {e}")
                            
                    if not processed_numbers:
                        logger.warning(f"No valid numbers for method {method}, skipping")
                        continue
                        
                    # Tính điểm tin cậy cho từng số
                    confidence_scores = {}
                    for num in processed_numbers:
                        # Điểm cơ bản từ trọng số phương pháp
                        base_confidence = confidence
                        # Tăng điểm nếu số nằm trong hot numbers
                        if pattern_analysis and pattern_analysis.get('hot_numbers'):
                            for hot_num, _ in pattern_analysis['hot_numbers']:
                                if num == hot_num:
                                    base_confidence = min(0.95, base_confidence * 1.2)  # Tăng 20%
                                    break
                        # Tăng điểm nếu số nằm trong trending numbers
                        if pattern_analysis and pattern_analysis.get('trending_numbers'):
                            for item in pattern_analysis['trending_numbers']:
                                trend_num = item[0]  # Vì đã chuẩn hóa nên luôn là (number, score)
                                if num == trend_num or (trend_num and "-" in trend_num and (num in trend_num.split("-"))):
                                    base_confidence = min(0.95, base_confidence * 1.15)  # Tăng 15%
                                    break
                        confidence_scores[num] = base_confidence
                    
                    method_predictions.append({
                        'method': {'name': name, 'description': f'Phương pháp {name.lower()}'},
                        'numbers': processed_numbers,
                        'confidence_scores': confidence_scores,
                        'confidence': confidence,
                        'weight': predictions.get('method_weights', {}).get(method, 0.0)
                    })

            # Kiểm tra nếu không có method_predictions nào được tạo
            if not method_predictions:
                logger.warning("No valid method predictions were created, using fallback")
                fallback_predictions = self._create_fallback_predictions()
                method_predictions.extend(fallback_predictions)

            context['enhanced_methods'] = method_predictions

            
            # Tạo dự đoán tối ưu từ phân tích lịch sử
            optimized_predictions = self._generate_optimized_ensemble(historical_accuracy, predictions)
            context['optimized_predictions'] = optimized_predictions
            context['processing_stages']['optimization'] = {'status': 'complete', 'message': 'Optimization complete'}
            
            # Bắt đầu kết hợp kết quả
            context['processing_stages']['combination'] = {'status': 'in_progress', 'message': 'Combining results...'}
            
            # Kết hợp dự đoán từ SHAP và các phương pháp
            try:
                # Ghi log chi tiết các tham số đầu vào để debug
                logger.info(f"combine_predictions inputs: shap_prediction exists: {context.get('shap_prediction') is not None}, method_predictions count: {len(method_predictions)}")
                
                # Kiểm tra method_predictions trước khi gọi
                if not method_predictions:
                    logger.warning("method_predictions is empty, creating fallback data")
                    # Tạo dữ liệu dự phòng cho method_predictions nếu rỗng
                    fallback_predictions = self._create_fallback_predictions()
                    method_predictions.extend(fallback_predictions)
                    context['enhanced_methods'] = method_predictions
                
                combined_numbers = self.prediction_service.combine_predictions(
                    context.get('shap_prediction'), method_predictions
                )
                
                if not combined_numbers:
                    logger.warning("combine_predictions returned empty result, using fallback logic")
                    # Sử dụng logic dự phòng nâng cao
                    combined_numbers = self._create_fallback_combined_numbers(method_predictions, pattern_analysis)
                
                # Ghi log kết quả
                logger.info(f"Combined numbers created: {len(combined_numbers)} items")
                
            except Exception as e:
                logger.error(f"Error combining predictions: {e}", exc_info=True)
                # Tạo combined_numbers dự phòng mạnh mẽ hơn
                combined_numbers = self._create_fallback_combined_numbers(method_predictions, pattern_analysis)
                logger.info(f"Created fallback combined numbers: {len(combined_numbers)} items")

            context['combined_numbers'] = combined_numbers
            
            # Phân tích mẫu số và xu hướng
            all_predictions = []
            for method in method_predictions:
                all_predictions.extend(method.get('numbers', []))
            
            # Phân tích đầu số và đuôi số
            digit_analysis = self._analyze_digit_distribution(all_predictions)
            context['digit_analysis'] = digit_analysis
            
            # Tạo dự đoán tối ưu dựa trên tất cả phân tích
            optimal_numbers = self._generate_optimal_predictions(combined_numbers, pattern_analysis, all_predictions)
            context['optimal_numbers'] = optimal_numbers
            
            # Phân phối số dự đoán
            context['number_distribution'] = self.prediction_service.get_number_distribution(method_predictions)
            
            # Gợi ý cặp số
            context['pair_suggestions'] = self.prediction_service.generate_combined_suggestions(
                context.get('shap_prediction'), method_predictions
            )
            
            # Đề xuất phương pháp tốt nhất
            context['method_recommendation'] = self.prediction_service.get_recommended_method()
            
            # Thêm thông tin vào combined_numbers
            if combined_numbers and isinstance(combined_numbers, (list, tuple)) and len(combined_numbers) > 0:
                enhanced_combined = []
                
                # Log chi tiết để debug
                logger.info(f"Creating enhanced_combined_numbers from {len(combined_numbers)} combined numbers")
                
                for item in combined_numbers:
                    # Đảm bảo item có định dạng đúng (num, score)
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        num, score = item
                    elif isinstance(item, dict) and 'number' in item and 'score' in item:
                        num, score = item['number'], item['score']
                    else:
                        logger.warning(f"Skipping invalid combined number item: {item}")
                        continue
                        
                    # Đảm bảo num là chuỗi 2 chữ số
                    try:
                        num = str(num).zfill(2)
                    except Exception as e:
                        logger.warning(f"Error processing number {num}: {e}")
                        continue
                        
                    # Thêm thông tin về loại mẫu số
                    number_type = []
                    if pattern_analysis and pattern_analysis.get('repetition_patterns'):
                        if pattern_analysis['repetition_patterns'].get('doubles') and num in pattern_analysis['repetition_patterns']['doubles']:
                            number_type.append('double')
                        elif pattern_analysis['repetition_patterns'].get('mirrors') and num in pattern_analysis['repetition_patterns']['mirrors']:
                            number_type.append('mirror')
                        elif pattern_analysis['repetition_patterns'].get('consecutive') and num in pattern_analysis['repetition_patterns']['consecutive']:
                            number_type.append('consecutive')
                            
                    # Thêm thông tin về xu hướng
                    trend_info = None
                    if pattern_analysis and pattern_analysis.get('trending_numbers'):
                        for item in pattern_analysis['trending_numbers']:
                            trend_num = item[0]  # Vì đã chuẩn hóa nên luôn là (number, score)
                            if num == trend_num or (trend_num and "-" in trend_num and (num in trend_num.split("-"))):
                                base_confidence = min(0.95, base_confidence * 1.15)  # Tăng 15%
                                break
                                
                    # Thêm thông tin về hot/cold
                    is_hot = False
                    is_cold = False
                    hot_count = 0
                    cold_count = 0
                    if pattern_analysis and pattern_analysis.get('hot_numbers'):
                        for hot_num, count in pattern_analysis['hot_numbers']:
                            if num == hot_num:
                                is_hot = True
                                hot_count = count
                                break
                    if pattern_analysis and pattern_analysis.get('cold_numbers'):
                        for cold_num, count in pattern_analysis['cold_numbers']:
                            if num == cold_num:
                                is_cold = True
                                cold_count = count
                                break
                                
                    # Tạo đối tượng số cải tiến
                    enhanced_num = {
                        'number': num,
                        'score': score,
                        'types': number_type,
                        'is_hot': is_hot,
                        'is_cold': is_cold,
                        'hot_count': hot_count,
                        'cold_count': cold_count,
                        'trend': trend_info
                    }
                    enhanced_combined.append(enhanced_num)
                    
                # Cập nhật context
                context['enhanced_combined_numbers'] = enhanced_combined
                logger.info(f"Created {len(enhanced_combined)} enhanced combined numbers")
            else:
                logger.warning("combined_numbers is empty or invalid, creating fallback enhanced_combined_numbers")
                # Tạo enhanced_combined_numbers dự phòng
                fallback_enhanced = []
                
                # Sử dụng optimal_numbers nếu có
                if context.get('optimal_numbers'):
                    for num in context['optimal_numbers']:
                        fallback_enhanced.append({
                            'number': num,
                            'score': 0.5,
                            'types': [],
                            'is_hot': False,
                            'is_cold': False,
                            'hot_count': 0,
                            'cold_count': 0,
                            'trend': None
                        })
                # Nếu không, tạo một số số cơ bản
                else:
                    for i in range(10, 100, 10):
                        num = f"{i:02d}"
                        fallback_enhanced.append({
                            'number': num,
                            'score': 0.5,
                            'types': [],
                            'is_hot': False,
                            'is_cold': False,
                            'hot_count': 0,
                            'cold_count': 0,
                            'trend': None
                        })
                        
                context['enhanced_combined_numbers'] = fallback_enhanced
                logger.info(f"Created {len(fallback_enhanced)} fallback enhanced combined numbers")
            
            # Lấy số thực tế nếu có
            actual_result = KetQuaXoSo.objects.filter(ngay=target_date).first()
            if actual_result:
                actual_numbers = actual_result.get_all_2digit_numbers()
                context['actual_numbers'] = actual_numbers
                
                # Tính độ chính xác của các dự đoán
                # 1. Độ chính xác combined_numbers
                combined_predicted = [num for num, _ in combined_numbers]
                combined_metrics = self.prediction_service.calculate_performance_metrics(
                    combined_predicted, actual_numbers
                )
                
                # 2. Độ chính xác optimized_predictions
                optimized_predicted = [num for num, _ in optimized_predictions]
                optimized_metrics = self.prediction_service.calculate_performance_metrics(
                    optimized_predicted, actual_numbers
                )
                
                # 3. Độ chính xác optimal_numbers
                optimal_metrics = self.prediction_service.calculate_performance_metrics(
                    optimal_numbers, actual_numbers
                )
                
                # 4. Độ chính xác của mỗi phương pháp
                method_accuracies = {}
                for method in method_predictions:
                    method_name = method['method']['name']
                    method_numbers = method['numbers']
                    method_metrics = self.prediction_service.calculate_performance_metrics(
                        method_numbers, actual_numbers
                    )
                    method_accuracies[method_name] = method_metrics
                
                # 5. Độ chính xác SHAP
                shap_accuracy = None
                if 'shap_prediction' in context and hasattr(context['shap_prediction'], 'predicted_numbers'):
                    shap_metrics = self.prediction_service.calculate_performance_metrics(
                        context['shap_prediction'].predicted_numbers, actual_numbers
                    )
                    shap_accuracy = shap_metrics
                
                # Tổng hợp độ chính xác
                context['performance_stats'] = {
                    'combined': combined_metrics,
                    'optimized': optimized_metrics,
                    'optimal': optimal_metrics,
                    'methods': method_accuracies,
                    'shap': shap_accuracy
                }
            
            context['processing_stages']['combination'] = {'status': 'complete', 'message': 'Results combined successfully'}
            
            # Thêm thông tin về ngày vào context
            context.update({
                'selected_date': selected_date,
                'target_date': target_date,
                'history_days': history_days,
                'today': timezone.now().date()
            })
            
            # Cache kết quả cho các request tương lai
            cacheable_data = {
                'shap_analysis': context.get('shap_analysis'),
                'best_predictions': context.get('best_predictions'),
                'enhanced_methods': context.get('enhanced_methods'),
                'shap_prediction': context.get('shap_prediction'),
                'combined_numbers': context.get('combined_numbers'),
                'enhanced_combined_numbers': context.get('enhanced_combined_numbers'),
                'number_distribution': context.get('number_distribution'),
                'pair_suggestions': context.get('pair_suggestions'),
                'method_recommendation': context.get('method_recommendation'),
                'pattern_analysis': context.get('pattern_analysis'),
                'digit_analysis': context.get('digit_analysis'),
                'optimized_predictions': context.get('optimized_predictions'),
                'optimal_numbers': context.get('optimal_numbers'),
                'historical_accuracy': context.get('historical_accuracy'),
                'selected_date': selected_date,
                'target_date': target_date,
                'history_days': history_days
            }
            
            # Cache trong 1 giờ
            cache.set(cache_key, cacheable_data, 60*60)
            # Kiểm tra dữ liệu cache
            cached_data = cache.get(cache_key)
            
        except Exception as e:
            logger.error(f"Error in get_context_data: {str(e)}", exc_info=True)
            messages.error(self.request, f"Đã xảy ra lỗi: {str(e)}")
            
            # Đánh dấu giai đoạn hiện tại là thất bại
            for stage, info in context['processing_stages'].items():
                if info['status'] == 'in_progress' or info['status'] == 'pending':
                    context['processing_stages'][stage] = {'status': 'failed', 'message': f'Failed: {str(e)}'}
                    break
            
            # Sử dụng context mặc định
            context.update(self._get_default_context())
        
        return context

    def _analyze_digit_distribution(self, numbers):
        """
        Phân tích phân phối chữ số đầu và chữ số cuối
        Args:
            numbers: Danh sách các số dự đoán
        Returns:
            Dict chứa phân tích phân phối chữ số
        """
        try:
            # Khởi tạo kết quả
            digit_distribution = {
                'first_digits': {str(i): 0 for i in range(10)},  # Phân phối chữ số đầu
                'last_digits': {str(i): 0 for i in range(10)},   # Phân phối chữ số cuối
                'total_numbers': len(numbers),
                'unique_numbers': len(set(numbers)),
                'common_patterns': {
                    'doubles': [],       # Số kép (00, 11, ...)
                    'mirrors': [],       # Số gương (19, 28, ...)
                    'consecutive': [],   # Số liên tiếp (12, 23, ...)
                }
            }
            
            # Đếm tần suất của từng chữ số đầu và cuối
            for num in numbers:
                # Chuẩn hóa thành chuỗi có 2 chữ số
                num_str = str(num).zfill(2)
                
                # Lấy chữ số đầu và cuối
                first_digit = num_str[0]
                last_digit = num_str[1]
                
                # Tăng số đếm
                digit_distribution['first_digits'][first_digit] += 1
                digit_distribution['last_digits'][last_digit] += 1
                
                # Phát hiện các mẫu đặc biệt
                if first_digit == last_digit:  # Số kép
                    digit_distribution['common_patterns']['doubles'].append(num_str)
                
                if int(first_digit) + int(last_digit) == 9:  # Số gương
                    digit_distribution['common_patterns']['mirrors'].append(num_str)
                    
                if abs(int(first_digit) - int(last_digit)) == 1:  # Số liên tiếp
                    digit_distribution['common_patterns']['consecutive'].append(num_str)
            
            # Tìm chữ số đầu và cuối phổ biến nhất
            digit_distribution['most_common_first_digit'] = max(
                digit_distribution['first_digits'].items(), 
                key=lambda x: x[1]
            )[0] if digit_distribution['first_digits'] else None
            
            digit_distribution['most_common_last_digit'] = max(
                digit_distribution['last_digits'].items(), 
                key=lambda x: x[1]
            )[0] if digit_distribution['last_digits'] else None
            
            # Sắp xếp chữ số đầu và cuối theo tần suất giảm dần
            digit_distribution['sorted_first_digits'] = sorted(
                digit_distribution['first_digits'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            digit_distribution['sorted_last_digits'] = sorted(
                digit_distribution['last_digits'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return digit_distribution
        except Exception as e:
            logger.error(f"Error in _analyze_digit_distribution: {str(e)}", exc_info=True)
            return {
                'first_digits': {},
                'last_digits': {},
                'total_numbers': 0,
                'error': str(e)
            }
    def _generate_optimal_predictions(self, combined_numbers, pattern_analysis, all_predictions):
        """
        Tạo dự đoán tối ưu dựa trên phân tích
        Args:
            combined_numbers: Danh sách các cặp (số, điểm)
            pattern_analysis: Kết quả phân tích mẫu số và xu hướng
            all_predictions: Danh sách tất cả số dự đoán
        Returns:
            List các số dự đoán tối ưu
        """
        try:
            # Log chi tiết để debug
            logger.info(f"Generating optimal predictions with {len(combined_numbers)} combined numbers, " 
                    f"{len(all_predictions)} total predictions")
            
            # Tạo dict để lưu điểm số
            scores = {}
            
            # Thêm điểm từ combined_numbers
            if combined_numbers:
                for item in combined_numbers:
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        num, score = item
                    elif isinstance(item, dict) and 'number' in item and 'score' in item:
                        num, score = item['number'], item['score']
                    else:
                        continue
                    
                    try:
                        num_str = str(num).zfill(2)
                        scores[num_str] = score
                    except Exception as e:
                        logger.warning(f"Error processing combined number {num}: {e}")
                        continue
            
            # Thêm tất cả các số từ all_predictions với điểm cơ bản
            for num in all_predictions:
                try:
                    num_str = str(num).zfill(2)
                    if num_str not in scores:
                        scores[num_str] = 0.3  # Điểm cơ bản cho các số chưa có trong combined_numbers
                except Exception as e:
                    logger.warning(f"Error processing prediction {num}: {e}")
                    continue
            
            # Thêm điểm cho các số nóng
            if pattern_analysis and pattern_analysis.get('hot_numbers'):
                for hot_num, count in pattern_analysis['hot_numbers']:
                    try:
                        hot_num_str = str(hot_num).zfill(2)
                        if hot_num_str in scores:
                            scores[hot_num_str] += count * 0.03  # Điểm bổ sung dựa trên mức độ "nóng"
                        else:
                            scores[hot_num_str] = count * 0.03 + 0.3  # Điểm cơ bản + điểm "nóng"
                    except Exception as e:
                        logger.warning(f"Error processing hot number {hot_num}: {e}")
                        continue
            
            # Thêm điểm cho số có xu hướng
            if pattern_analysis and pattern_analysis.get('trending_numbers'):
                for item in pattern_analysis['trending_numbers']:
                    trend_num = item[0]  # Vì đã chuẩn hóa nên luôn là (number, score)
                    if num == trend_num or (trend_num and "-" in trend_num and (num in trend_num.split("-"))):
                        base_confidence = min(0.95, base_confidence * 1.15)  # Tăng 15%
                        break
            
            # Thêm điểm cho mẫu số đặc biệt
            if pattern_analysis and pattern_analysis.get('repetition_patterns'):
                repetition_patterns = pattern_analysis.get('repetition_patterns', {})
                
                # Tạo một danh sách tất cả các số đặc biệt
                special_numbers = []
                for pattern_type in ['doubles', 'mirrors', 'consecutive']:
                    if repetition_patterns.get(pattern_type):
                        special_numbers.extend(repetition_patterns[pattern_type])
                
                # Thêm điểm cho các số đặc biệt
                for num in special_numbers:
                    try:
                        num_str = str(num).zfill(2)
                        if num_str in scores:
                            scores[num_str] += 0.05  # Thêm điểm cho số đặc biệt
                        else:
                            scores[num_str] = 0.35  # Điểm cơ bản + điểm đặc biệt
                    except Exception as e:
                        logger.warning(f"Error processing special number {num}: {e}")
                        continue
            
            # Cân đối đầu số và đuôi số
            if pattern_analysis and pattern_analysis.get('digit_patterns'):
                digit_patterns = pattern_analysis.get('digit_patterns', {})
                
                if digit_patterns.get('first_digits'):
                    top_first_digits = [d for d, _ in digit_patterns['first_digits'][:3]]
                    for num_str in list(scores.keys()):
                        if len(num_str) >= 2 and num_str[0] in top_first_digits:
                            scores[num_str] += 0.04  # Thêm điểm cho số có đầu số phổ biến
                
                if digit_patterns.get('last_digits'):
                    top_last_digits = [d for d, _ in digit_patterns['last_digits'][:3]]
                    for num_str in list(scores.keys()):
                        if len(num_str) >= 2 and num_str[1] in top_last_digits:
                            scores[num_str] += 0.04  # Thêm điểm cho số có đuôi số phổ biến
            
            # Sắp xếp và lấy top 15 số
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            # Đảm bảo đa dạng
            optimal_numbers = []
            first_digits_used = set()
            for num_str, _ in sorted_scores:
                if len(optimal_numbers) >= 15:
                    break
                    
                # Giới hạn số lượng số có cùng chữ số đầu tiên
                if len(num_str) >= 2:
                    first_digit = num_str[0]
                    if first_digit in first_digits_used and len(first_digits_used) >= 4:
                        if sum(1 for n in optimal_numbers if n[0] == first_digit) >= 3:
                            continue
                    first_digits_used.add(first_digit)
                    
                optimal_numbers.append(num_str)
            
            logger.info(f"Generated {len(optimal_numbers)} optimal predictions")
            return optimal_numbers
            
        except Exception as e:
            logger.error(f"Error generating optimal predictions: {e}", exc_info=True)
            # Fallback to combined_numbers or basic predictions
            fallback_numbers = []
            
            # Thử lấy từ combined_numbers
            if combined_numbers:
                try:
                    for item in combined_numbers[:15]:
                        if isinstance(item, (list, tuple)) and len(item) >= 1:
                            fallback_numbers.append(str(item[0]).zfill(2))
                        elif isinstance(item, dict) and 'number' in item:
                            fallback_numbers.append(str(item['number']).zfill(2))
                except Exception:
                    pass
                    
            # Nếu vẫn không có, tạo một số cơ bản
            if not fallback_numbers:
                fallback_numbers = [f"{i:02d}" for i in range(10, 100, 6)][:15]
                
            logger.info(f"Generated {len(fallback_numbers)} fallback optimal predictions")
            return fallback_numbers
    
    def _create_default_historical_accuracy(self):
        """Tạo dữ liệu độ chính xác lịch sử mặc định khi có lỗi"""
        default_methods = {
            'tan_so_cao': {'hit_rate': 45.0, 'day_hit_rate': 60.0, 'total_hits': 45, 'total_predictions': 100, 'hit_days': 6, 'used_days': 10},
            'lap_lai_gan_nhat': {'hit_rate': 50.0, 'day_hit_rate': 70.0, 'total_hits': 50, 'total_predictions': 100, 'hit_days': 7, 'used_days': 10},
            'bong_so': {'hit_rate': 40.0, 'day_hit_rate': 50.0, 'total_hits': 40, 'total_predictions': 100, 'hit_days': 5, 'used_days': 10},
            'khu_vuc': {'hit_rate': 35.0, 'day_hit_rate': 40.0, 'total_hits': 35, 'total_predictions': 100, 'hit_days': 4, 'used_days': 10},
            'chu_ky': {'hit_rate': 30.0, 'day_hit_rate': 30.0, 'total_hits': 30, 'total_predictions': 100, 'hit_days': 3, 'used_days': 10}
        }
        
        return {
            'methods': default_methods,
            'overall': {
                'hit_rate': 40.0,
                'total_hits': 200,
                'total_predictions': 500
            },
            'trend': [],
            'best_method': {
                'name': 'lap_lai_gan_nhat',
                'stats': default_methods['lap_lai_gan_nhat']
            },
            'worst_method': {
                'name': 'chu_ky',
                'stats': default_methods['chu_ky']
            },
            'meta': {
                'is_default': True,
                'reason': 'Error in historical analysis',
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
    
            
    def _predict_from_shap_model(self, model, selected_date):
        """
        Dự đoán số từ mô hình SHAP
        
        Args:
            model: Mô hình đã huấn luyện
            selected_date: Ngày được chọn
            
        Returns:
            List các số dự đoán
        """
        try:
            import numpy as np
            
            # Tạo đặc trưng cho ngày dự đoán
            target_date = selected_date + timedelta(days=1)
            
            features = [
                target_date.day / 31.0,  # Ngày trong tháng (chuẩn hóa)
                target_date.month / 12.0,  # Tháng (chuẩn hóa)
                target_date.weekday() / 6.0,  # Thứ trong tuần (chuẩn hóa)
            ]
            
            # Tạo biến thể của đặc trưng để tăng đa dạng
            variants = [
                features,
                [features[0] * 0.95, features[1], features[2]],
                [features[0] * 1.05, features[1], features[2]],
                [features[0], features[1] * 0.95, features[2]],
                [features[0], features[1] * 1.05, features[2]],
                [features[0], features[1], features[2] * 0.95],
                [features[0], features[1], features[2] * 1.05]
            ]
            
            # Dự đoán
            X_predict = np.array(variants)
            predictions = model.predict(X_predict)
            
            # Chuyển thành số 2 chữ số (00-99)
            predicted_numbers = []
            for pred in predictions:
                num = int(round(pred)) % 100
                predicted_numbers.append(f"{num:02d}")
                
            # Loại bỏ trùng lặp
            unique_predictions = list(set(predicted_numbers))
            
            return unique_predictions
            
        except Exception as e:
            logger.error(f"Error predicting from SHAP model: {e}", exc_info=True)
            return []
    
    # Cập nhật phương thức _analyze_historical_accuracy
    def _analyze_historical_accuracy(self, historical_data, days=30):
        """
        Phân tích độ chính xác lịch sử của các phương pháp dự đoán
        Args:
            historical_data: QuerySet dữ liệu lịch sử
            days: Số ngày để phân tích
        Returns:
            Dict chứa thông tin về độ chính xác lịch sử
        """
        try:
            # Log thông tin đầu vào
            history_count = len(historical_data) if historical_data else 0
            logger.info(f"Phân tích độ chính xác lịch sử với {history_count} bản ghi cho {days} ngày")
            
            # Sử dụng PerformanceEvaluator
            target_date = self._get_selected_date()
            evaluator = PerformanceEvaluator(target_date=target_date, historical_days=days)
            
            # Kiểm tra xem có dữ liệu hiệu suất được lưu trữ hay không
            performance_results = evaluator.evaluate_method_performance(date_range=days)
            
            if performance_results:
                # Chuyển đổi kết quả từ PerformanceEvaluator sang định dạng của _analyze_historical_accuracy
                accuracy_data = {
                    'methods': {},
                    'overall': {
                        'hit_rate': 0,
                        'total_hits': 0,
                        'total_predictions': 0
                    },
                    'trend': [],
                    'best_method': None,
                    'worst_method': None
                }
                
                # Tổng hợp số liệu tổng thể
                total_hits = 0
                total_predictions = 0
                
                # Lấy dữ liệu cho từng phương pháp
                for method_key, stats in performance_results.items():
                    accuracy_data['methods'][method_key] = {
                        'hit_rate': stats.get('accuracy', 0),
                        'day_hit_rate': stats.get('trend', {}).get('second_half_avg', 0) * 100,  # Chuyển sang phần trăm
                        'total_hits': stats.get('total_hit', 0),
                        'total_predictions': stats.get('total_predicted', 0),
                        'hit_days': stats.get('hit_days', 0),
                        'used_days': stats.get('total_days', 0),
                        'is_tired': stats.get('is_tired', False),
                        'days_since_last_hit': stats.get('days_since_last_hit', 0)
                    }
                    
                    total_hits += stats.get('total_hit', 0)
                    total_predictions += stats.get('total_predicted', 0)
                
                # Cập nhật thống kê tổng thể
                if total_predictions > 0:
                    accuracy_data['overall']['hit_rate'] = (total_hits / total_predictions) * 100
                accuracy_data['overall']['total_hits'] = total_hits
                accuracy_data['overall']['total_predictions'] = total_predictions
                
                # Tìm phương pháp tốt nhất và tệ nhất
                if accuracy_data['methods']:
                    methods_with_min_days = {k: v for k, v in accuracy_data['methods'].items() if v['used_days'] >= 3}
                    
                    if methods_with_min_days:
                        best_method = max(methods_with_min_days.items(), key=lambda x: x[1]['hit_rate'])
                        worst_method = min(methods_with_min_days.items(), key=lambda x: x[1]['hit_rate'])
                        
                        accuracy_data['best_method'] = {
                            'name': best_method[0],
                            'stats': best_method[1]
                        }
                        
                        accuracy_data['worst_method'] = {
                            'name': worst_method[0],
                            'stats': worst_method[1]
                        }
                
                # Thêm meta-information
                accuracy_data['meta'] = {
                    'days_analyzed': days,
                    'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'performance_evaluator'
                }
                
                return accuracy_data
                
            # Nếu không có dữ liệu từ PerformanceEvaluator, sử dụng phương pháp hiện tại
            if not historical_data or len(historical_data) < 2:
                logger.warning("Không đủ dữ liệu lịch sử cho phân tích độ chính xác")
                return self._create_default_historical_accuracy()
            
            # Phần còn lại của mã hiện tại không thay đổi
            # ...

        except Exception as e:
            logger.error(f"Lỗi khi phân tích độ chính xác lịch sử: {e}", exc_info=True)
            return self._create_default_historical_accuracy()

    # Cập nhật phương thức _generate_optimized_ensemble
    def _generate_optimized_ensemble(self, historical_accuracy, predictions):
        """
        Tạo dự đoán kết hợp tối ưu dựa trên độ chính xác lịch sử
        Args:
            historical_accuracy: Kết quả phân tích độ chính xác lịch sử
            predictions: Dict chứa dự đoán từ các phương pháp
        Returns:
            List các cặp (số, điểm) tối ưu
        """
        try:
            from collections import defaultdict
            
            # Kiểm tra dữ liệu đầu vào
            if not historical_accuracy or not predictions or 'predictions' not in predictions:
                return []
                
            # Lấy trọng số từ PerformanceEvaluator
            target_date = self._get_selected_date()
            evaluator = PerformanceEvaluator(target_date=target_date)
            optimal_weights = evaluator.get_current_method_weights()
            
            method_weights = {}
            
            # Sử dụng trọng số tối ưu từ evaluator nếu có
            if optimal_weights:
                for method_key in predictions['predictions'].keys():
                    if method_key in optimal_weights:
                        method_weights[method_key] = optimal_weights[method_key]
                        logger.info(f"Sử dụng trọng số tối ưu cho {method_key}: {optimal_weights[method_key]}")
            
            # Nếu không có trọng số từ evaluator, tính từ historical_accuracy
            if not method_weights and 'methods' in historical_accuracy:
                for method_key, stats in historical_accuracy['methods'].items():
                    # Kết hợp tỷ lệ trúng và tỷ lệ ngày trúng để tính trọng số
                    hit_rate_weight = stats['hit_rate'] / 100  # Chuyển về tỷ lệ 0-1
                    day_hit_rate_weight = stats['day_hit_rate'] / 100  # Chuyển về tỷ lệ 0-1
                    
                    # Công thức trọng số: 70% tỷ lệ trúng + 30% tỷ lệ ngày trúng
                    method_weights[method_key] = (0.7 * hit_rate_weight) + (0.3 * day_hit_rate_weight)
                    
                    # Điều chỉnh cho phương pháp mệt mỏi
                    if stats.get('is_tired', False):
                        method_weights[method_key] *= 0.7  # Giảm 30% nếu mệt mỏi
            
            # Nếu vẫn không có trọng số, sử dụng từ predictor
            if not method_weights and 'method_weights' in predictions:
                method_weights = predictions['method_weights']
                
            # Tính điểm cho mỗi số
            number_scores = defaultdict(float)
            
            for method_key, numbers in predictions['predictions'].items():
                # Lấy trọng số của phương pháp
                weight = method_weights.get(method_key, 0.5)  # Mặc định là 0.5 nếu không có trọng số
                
                # Tăng trọng số cho phương pháp tốt nhất
                if historical_accuracy.get('best_method') and historical_accuracy['best_method']['name'] == method_key:
                    weight *= 1.3  # Tăng thêm 30%
                    
                # Giảm trọng số cho phương pháp tệ nhất
                if historical_accuracy.get('worst_method') and historical_accuracy['worst_method']['name'] == method_key:
                    weight *= 0.7  # Giảm 30%
                    
                # Bổ sung điểm cho từng số
                if isinstance(numbers, (list, tuple)):
                    num_list = numbers if isinstance(numbers, list) else numbers[0]
                    for num in num_list:
                        number_scores[num] += weight
                        
            # Sắp xếp theo điểm giảm dần
            sorted_numbers = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Log các số top và điểm của chúng
            logger.info(f"Đã tạo {len(sorted_numbers)} số tối ưu với điểm")
            for num, score in sorted_numbers[:10]:
                logger.info(f"  {num}: {score:.2f}")
                
            return sorted_numbers
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo ensemble tối ưu: {e}", exc_info=True)
            return []

    # Cập nhật phương thức _analyze_prediction_patterns để sử dụng phân tích mẫu từ NumberFrequencyStats
    def _analyze_prediction_patterns(self, predictions, historical_data):
        """
        Phân tích các mẫu số (patterns) trong dự đoán
        Args:
            predictions: Dict chứa kết quả dự đoán
            historical_data: QuerySet dữ liệu lịch sử
        Returns:
            Dict chứa kết quả phân tích
        """
        try:
            # Sử dụng PerformanceEvaluator để phân tích mẫu từ NumberFrequencyStats
            target_date = self._get_selected_date()
            evaluator = PerformanceEvaluator(target_date=target_date)
            pattern_analysis = evaluator.analyze_number_patterns(days=30)
            
            if pattern_analysis and 'hot_numbers' in pattern_analysis:
                logger.info(f"Sử dụng phân tích mẫu từ NumberFrequencyStats")
                
                # Thêm thống kê về tất cả các số dự đoán
                all_predictions = []
                
                # Kiểm tra cấu trúc của predictions
                if isinstance(predictions, dict) and 'predictions' in predictions:
                    pred_dict = predictions.get('predictions', {})
                    for method_data in pred_dict.values():
                        if isinstance(method_data, (list, tuple)):
                            numbers = method_data if isinstance(method_data, list) else method_data[0]
                            all_predictions.extend(numbers)
                elif isinstance(predictions, list):
                    # Nếu predictions là danh sách các phương pháp
                    for method_data in predictions:
                        if isinstance(method_data, dict) and 'numbers' in method_data:
                            all_predictions.extend(method_data['numbers'])
                
                # Chuẩn hóa và đếm tần suất
                standardized_predictions = []
                for num in all_predictions:
                    try:
                        num_str = str(num).zfill(2)
                        standardized_predictions.append(num_str)
                    except Exception as e:
                        logger.warning(f"Lỗi chuẩn hóa số {num}: {e}")
                
                # Đếm tần suất
                prediction_frequency = {}
                for num in standardized_predictions:
                    prediction_frequency[num] = prediction_frequency.get(num, 0) + 1
                
                sorted_predictions = sorted(prediction_frequency.items(), key=lambda x: x[1], reverse=True)
                
                # Kết hợp thông tin từ phân tích mẫu và dự đoán
                result = {
                    'hot_numbers': pattern_analysis.get('hot_numbers', []),
                    'cold_numbers': pattern_analysis.get('cold_numbers', []),
                    'trending_numbers': pattern_analysis.get('related_pairs', [])[:10],  # Sử dụng cặp số liên quan làm số trending
                    'digit_patterns': {
                        'first_digits': pattern_analysis.get('first_digit_patterns', []),
                        'last_digits': pattern_analysis.get('last_digit_patterns', [])
                    },
                    'repetition_patterns': {
                        'doubles': [],
                        'mirrors': [],
                        'consecutive': []
                    },
                    'weekday_popular': pattern_analysis.get('weekday_popular', {}),
                    'phase_popular': pattern_analysis.get('phase_popular', {}),
                    'prediction_frequency': sorted_predictions,
                    'statistics': {
                        'total_unique_numbers': len(set(standardized_predictions)),
                        'prediction_days': 30,
                        'analysis_source': 'NumberFrequencyStats'
                    }
                }
                
                # Tìm mẫu lặp lại (Kép, Lộn, Liên tiếp)
                for num in set(standardized_predictions):
                    if len(num) == 2:
                        if num[0] == num[1]:  # Kép
                            result['repetition_patterns']['doubles'].append(num)
                        elif int(num[0]) + int(num[1]) == 9:  # Gương
                            result['repetition_patterns']['mirrors'].append(num)
                        elif abs(int(num[0]) - int(num[1])) == 1:  # Liên tiếp
                            result['repetition_patterns']['consecutive'].append(num)
                
                return result
            
            # Nếu không có dữ liệu từ NumberFrequencyStats, sử dụng phương thức hiện tại
            # ...
            
        except Exception as e:
            logger.error(f"Lỗi khi phân tích mẫu dự đoán: {e}", exc_info=True)
            # Trả về một dictionary trống trong trường hợp lỗi
            return {
                'digit_patterns': {},
                'repetition_patterns': {},
                'trending_numbers': [],
                'cold_numbers': [],
                'hot_numbers': [],
                'error': str(e)
            }
    # Add these new helper methods to CombinedAnalysisView
    def _store_performance_metrics(self, prediction_date, method_key, predictions, actual_numbers, hit_count, total_count):
        """Store performance metrics in database"""
        try:
            # Calculate hit rate
            hit_rate = (hit_count / total_count) * 100 if total_count > 0 else 0
            
            # Calculate days since last hit
            days_since_last_hit = self._calculate_days_since_last_hit(method_key, prediction_date)
            
            # Store in database
            PredictionPerformanceMetrics.objects.update_or_create(
                target_date=prediction_date,
                method_name=method_key,
                method_version="1.0",  # Default version
                defaults={
                    'analysis_date': datetime.now().date(),
                    'total_predictions': total_count,
                    'correct_predictions': hit_count,
                    'hit_rate': hit_rate,
                    'predicted_numbers': json.dumps(predictions),
                    'actual_numbers': json.dumps(actual_numbers),
                    'days_since_last_hit': days_since_last_hit,
                    'is_tired': days_since_last_hit >= 19  # 19-21 days threshold
                }
            )
        except Exception as e:
            logger.error(f"Error storing performance metrics: {e}", exc_info=True)

    def _calculate_days_since_last_hit(self, method_name, target_date):
        """Calculate days since the method last had a hit"""
        try:
            # Get the most recent hit before target_date
            last_hit = PredictionPerformanceMetrics.objects.filter(
                method_name=method_name,
                target_date__lt=target_date,
                correct_predictions__gt=0
            ).order_by('-target_date').first()
            
            if last_hit:
                return (target_date - last_hit.target_date).days
                
            # If no previous hit found, check historical data manually
            historical_data = self._get_historical_data_before_date(target_date)
            
            if not historical_data or len(historical_data) < 7:
                return 0
                
            # Initialize predictor for checking
            predictor = BachThuLoPredictor(
                target_date=target_date,
                history_days=min(90, len(historical_data)),
                selected_date=target_date - timedelta(days=1)
            )
            
            # Check the last 30 days
            days_to_check = min(30, len(historical_data))
            
            for i in range(days_to_check):
                check_date = target_date - timedelta(days=i+1)
                
                # Get actual numbers for this date
                result = next((r for r in historical_data if r.ngay == check_date), None)
                
                if not result or not hasattr(result, 'get_all_2digit_numbers'):
                    continue
                    
                actual_numbers = result.get_all_2digit_numbers()
                
                if not actual_numbers:
                    continue
                    
                # Check if the method had hits on this date
                if hasattr(predictor, method_name.replace('_', '_predict_')):
                    method_func = getattr(predictor, method_name.replace('_', '_predict_'))
                    predictions = method_func(check_date)
                    
                    if predictions:
                        standardized_predictions = [str(num).zfill(2) for num in predictions]
                        hits = [num for num in standardized_predictions if num in actual_numbers]
                        
                        if hits:
                            return i + 1
            
            # If no hit found in the checked period
            return days_to_check
            
        except Exception as e:
            logger.error(f"Error calculating days since last hit: {e}", exc_info=True)
            return 0

    def _get_cached_performance_metrics(self, target_date, days):
        """Get cached performance metrics from database"""
        try:
            # Check if we have a complete analysis for this date and days range
            cached_analysis = PredictionPerformanceMetrics.objects.filter(
                analysis_date=datetime.now().date(),
                target_date__lt=target_date,
                target_date__gte=target_date - timedelta(days=days)
            ).count()
            
            # If we have enough data points (at least 80% of days analyzed)
            if cached_analysis >= days * 0.8:
                # Build the analysis result from database
                accuracy_data = {
                    'methods': {},
                    'overall': {
                        'hit_rate': 0,
                        'total_hits': 0,
                        'total_predictions': 0
                    },
                    'trend': [],
                    'best_method': None,
                    'worst_method': None
                }
                
                # Get unique method names
                method_names = PredictionPerformanceMetrics.objects.filter(
                    target_date__lt=target_date,
                    target_date__gte=target_date - timedelta(days=days)
                ).values_list('method_name', flat=True).distinct()
                
                # Get stats for each method
                for method_name in method_names:
                    metrics = PredictionPerformanceMetrics.objects.filter(
                        method_name=method_name,
                        target_date__lt=target_date,
                        target_date__gte=target_date - timedelta(days=days)
                    )
                    
                    total_predictions = sum(m.total_predictions for m in metrics)
                    correct_predictions = sum(m.correct_predictions for m in metrics)
                    hit_days = metrics.filter(correct_predictions__gt=0).count()
                    used_days = metrics.count()
                    
                    hit_rate = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
                    day_hit_rate = (hit_days / used_days) * 100 if used_days > 0 else 0
                    
                    # Get days since last hit
                    days_since_last_hit = self._calculate_days_since_last_hit(method_name, target_date)
                    
                    accuracy_data['methods'][method_name] = {
                        'hit_rate': hit_rate,
                        'day_hit_rate': day_hit_rate,
                        'total_hits': correct_predictions,
                        'total_predictions': total_predictions,
                        'hit_days': hit_days,
                        'used_days': used_days,
                        'days_since_last_hit': days_since_last_hit,
                        'is_tired': days_since_last_hit >= 19
                    }
                    
                    # Update overall stats
                    accuracy_data['overall']['total_hits'] += correct_predictions
                    accuracy_data['overall']['total_predictions'] += total_predictions
                    
                    # Build trend data
                    for metric in metrics.order_by('target_date'):
                        trend_entry = next((t for t in accuracy_data['trend'] 
                                            if t['date'] == metric.target_date.strftime('%Y-%m-%d')), None)
                        
                        if not trend_entry:
                            trend_entry = {
                                'date': metric.target_date.strftime('%Y-%m-%d'),
                                'hits': {},
                                'predictions': {}
                            }
                            accuracy_data['trend'].append(trend_entry)
                            
                        trend_entry['hits'][method_name] = metric.correct_predictions
                        trend_entry['predictions'][method_name] = metric.total_predictions
                
                # Calculate overall hit rate
                if accuracy_data['overall']['total_predictions'] > 0:
                    accuracy_data['overall']['hit_rate'] = (
                        accuracy_data['overall']['total_hits'] / 
                        accuracy_data['overall']['total_predictions']
                    ) * 100
                    
                # Find best and worst methods
                if accuracy_data['methods']:
                    methods_with_min_days = {k: v for k, v in accuracy_data['methods'].items() if v['used_days'] >= 3}
                    
                    if methods_with_min_days:
                        best_method = max(methods_with_min_days.items(), key=lambda x: x[1]['hit_rate'])
                        worst_method = min(methods_with_min_days.items(), key=lambda x: x[1]['hit_rate'])
                        
                        accuracy_data['best_method'] = {
                            'name': best_method[0],
                            'stats': best_method[1]
                        }
                        
                        accuracy_data['worst_method'] = {
                            'name': worst_method[0],
                            'stats': worst_method[1]
                        }
                        
                # Add meta-information
                accuracy_data['meta'] = {
                    'days_analyzed': len(accuracy_data['trend']),
                    'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'database'
                }
                
                return accuracy_data
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached performance metrics: {e}", exc_info=True)
            return None

    def _cache_performance_analysis(self, target_date, accuracy_data, days):
        """Cache performance analysis in the database"""
        try:
            # No need to cache if we're using cached data
            if accuracy_data.get('meta', {}).get('source') == 'database':
                return
                
            # Store method weights based on analysis
            effective_date = target_date + timedelta(days=1)  # Effective tomorrow
            
            for method_key, stats in accuracy_data.get('methods', {}).items():
                if stats.get('used_days', 0) < 3:
                    continue
                    
                # Calculate weight based on hit rate and other factors
                hit_rate = stats.get('hit_rate', 0)
                day_hit_rate = stats.get('day_hit_rate', 0)
                is_tired = stats.get('is_tired', False)
                
                # Formula: 70% hit rate + 30% day hit rate
                base_weight = (0.7 * hit_rate/100) + (0.3 * day_hit_rate/100)
                
                # Apply tiredness penalty
                if is_tired:
                    base_weight *= 0.7  # Reduce by 30% if tired
                    
                # Ensure weight is in reasonable range
                final_weight = max(0.1, min(0.95, base_weight))
                
                # Store in database
                MethodWeightsHistory.objects.create(
                    effective_date=effective_date,
                    method_name=method_key,
                    weight=final_weight,
                    calculation_basis='historical',
                    days_analyzed=days
                )
                
        except Exception as e:
            logger.error(f"Error caching performance analysis: {e}", exc_info=True)

    
    def _calculate_shap_analysis(self, predictor, target_date):
        """
        Perform SHAP analysis with proper error handling
        
        Args:
            predictor: BachThuLoPredictor instance
            target_date: Date to analyze
            
        Returns:
            Dict with SHAP analysis results or empty dict on failure
        """
        try:
            # Check if shap module is available
            try:
                import shap
            except ImportError:
                logger.warning("SHAP library not available")
                return {}
            
            # Get historical data
            historical_data = self._get_historical_data_before_date(target_date)
            if not historical_data or len(historical_data) < 10:
                logger.warning(f"Insufficient historical data for SHAP analysis: {len(historical_data)} records")
                return {}
            
            # Prepare features for analysis
            X, y = self._prepare_ml_data(historical_data)
            if X is None or y is None or len(X) == 0:
                logger.warning("Failed to prepare ML data for SHAP analysis")
                return {}
            
            # Check if we have a model
            if not hasattr(self, 'model') or self.model is None:
                self.model = self._train_model(X, y)
            
            if self.model is None:
                logger.warning("No model available for SHAP analysis")
                return {}
            
            # Calculate SHAP values
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X)
            
            # Define feature names
            feature_names = [
                'number',
                'days_since_last',
                'hot_cold_index',
                'weekday_freq',
                'month_freq',
                'position_freq',
                'pair_freq',
                'sequence_freq'
            ]
            
            # Calculate global feature importance
            feature_importance = {
                name: float(np.abs(shap_values[:, i]).mean())
                for i, name in enumerate(feature_names)
                if i < len(feature_names) and i < shap_values.shape[1]
            }
            
            # Get top contributing features
            top_features = sorted(
                feature_importance.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:5]
            
            # Calculate SHAP interaction values for top pairs if supported
            try:
                interaction_values = explainer.shap_interaction_values(X)
                
                # Get top feature interactions
                interactions = []
                for i, feat1 in enumerate(feature_names):
                    if i >= interaction_values.shape[1]:
                        continue
                    for j in range(i+1, min(len(feature_names), interaction_values.shape[2])):
                        feat2 = feature_names[j]
                        try:
                            interaction_strength = float(np.abs(interaction_values[:, i, j]).mean())
                            interactions.append((feat1, feat2, interaction_strength))
                        except IndexError:
                            continue
                
                # Sort interactions by strength
                top_interactions = sorted(
                    interactions,
                    key=lambda x: x[2],
                    reverse=True
                )[:5]
            except Exception as e:
                logger.warning(f"Failed to calculate SHAP interactions: {e}")
                top_interactions = []
            
            return {
                'feature_importance': {
                    'values': dict(top_features),
                    'description': self._get_feature_importance_description(top_features)
                },
                'interactions': {
                    'values': top_interactions,
                    'description': self._get_interaction_description(top_interactions)
                },
                'shap_values': shap_values.tolist() if hasattr(shap_values, 'tolist') else shap_values,
                'feature_names': feature_names,
                'base_value': float(explainer.expected_value) if hasattr(explainer, 'expected_value') else 0,
                'target_date': target_date,
                'model_version': getattr(self, 'model_version', '1.0')
            }
            
        except Exception as e:
            logger.error(f"Error in SHAP analysis: {e}", exc_info=True)
            return {}
    
    def _get_historical_data_before_date(self, target_date):
        """
        Get historical data up to but not including target date
        
        Args:
            target_date: Date to get data before
            
        Returns:
            QuerySet of KetQuaXoSo objects
        """
        try:
            history_days = int(self.request.GET.get('days', 90))
            end_date = target_date - timedelta(days=1)
            start_date = end_date - timedelta(days=history_days)
            
            return KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by('-ngay')
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []
    
    def _prepare_ml_data(self, historical_data):
        """
        Prepare features and labels for ML model
        
        Args:
            historical_data: QuerySet of historical lottery results
            
        Returns:
            Tuple of (features, labels) or (None, None) on failure
        """
        try:
            from sklearn.preprocessing import StandardScaler
            
            # Extract features from historical data
            X = []
            y = []
            
            for result in historical_data:
                # Basic features (this is a simplified example)
                features = [
                    result.ngay.day / 31,  # Day of month normalized
                    result.ngay.month / 12,  # Month normalized
                    result.ngay.weekday() / 6,  # Day of week normalized
                ]
                
                # Add more features as needed
                X.append(features)
                
                # Use last 2 digits of special prize as label
                if hasattr(result, 'giai_db') and result.giai_db:
                    label = int(result.giai_db[-2:]) if len(result.giai_db) >= 2 else 0
                    y.append(label)
                else:
                    # Skip this record if no label
                    X.pop()
            
            if not X or not y:
                return None, None
            
            # Convert to numpy arrays
            X = np.array(X)
            y = np.array(y)
            
            # Normalize features
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing ML data: {e}", exc_info=True)
            return None, None
    
    def _train_model(self, X, y):
        """
        Train a machine learning model
        
        Args:
            X: Feature matrix
            y: Labels
            
        Returns:
            Trained model or None on failure
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            
            # Create and train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            return model
            
        except Exception as e:
            logger.error(f"Error training model: {e}", exc_info=True)
            return None
    
    def _get_feature_importance_description(self, top_features):
        """
        Generate human-readable description of feature importance
        
        Args:
            top_features: List of (feature_name, importance) tuples
            
        Returns:
            String description
        """
        descriptions = []
        for feature, importance in top_features:
            descriptions.append(
                f"{feature} có mức ảnh hưởng {importance:.2f}% "
                f"đến kết quả dự đoán"
            )
        return "\n".join(descriptions)
    
    def _get_interaction_description(self, interactions):
        """
        Generate human-readable description of feature interactions
        
        Args:
            interactions: List of (feature1, feature2, strength) tuples
            
        Returns:
            String description
        """
        descriptions = []
        for feat1, feat2, strength in interactions:
            descriptions.append(
                f"Tương tác giữa {feat1} và {feat2} "
                f"có độ mạnh {strength:.2f}%"
            )
        return "\n".join(descriptions)
    
    def _get_default_context(self):
        """
        Return default context when error occurs
        
        Returns:
            Dict with default context values
        """
        today = timezone.now().date()
        return {
            'selected_date': today,
            'target_date': today + timedelta(days=1),
            'predictions': [],
            'shap_analysis': {},
            'enhanced_methods': [],
            'combined_numbers': [],
            'number_distribution': {},
            'pair_suggestions': [],
            'method_recommendation': None,
            'performance_stats': None,
            'error': "Lỗi tạo dự đoán",
            'today': today
        }
