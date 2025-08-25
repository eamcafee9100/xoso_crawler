import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import Counter
from django.db.models import QuerySet

logger = logging.getLogger(__name__)

class DataQualityAssessment:
    """
    Service để đánh giá chất lượng dữ liệu lịch sử
    
    Returns:
        Dict với cấu trúc: {
            "completeness": float,  # Tỷ lệ hoàn thiện (0-1)
            "consistency": float,   # Tỷ lệ nhất quán (0-1) 
            "freshness": float,     # Độ mới của dữ liệu (0-1)
            "total_records": int,   # Tổng số records
            "complete_records": int, # Số records đầy đủ
            "date_gaps": List[str], # Danh sách ngày thiếu
            "quality_score": float, # Điểm tổng thể (0-1)
            "recommendations": List[str] # Khuyến nghị cải thiện
        }
    """
    
    def __init__(self):
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.8,
            'fair': 0.6,
            'poor': 0.4
        }
    
    def assess_data_quality(self, historical_data: List[Any]) -> Dict:
        """
        Đánh giá toàn diện chất lượng dữ liệu
        
        Args:
            historical_data: List KetQuaXoSo objects
            
        Returns:
            Dict với đầy đủ metrics chất lượng dữ liệu
        """
        try:
            if not historical_data:
                return self._get_empty_quality_report()
            
            # 1. Đánh giá tính hoàn thiện
            completeness_metrics = self._assess_completeness(historical_data)
            
            # 2. Đánh giá tính nhất quán
            consistency_metrics = self._assess_consistency(historical_data)
            
            # 3. Đánh giá độ mới
            freshness_metrics = self._assess_freshness(historical_data)
            
            # 4. Phát hiện gap trong dữ liệu
            gap_analysis = self._detect_date_gaps(historical_data)
            
            # 5. Đánh giá pattern integrity
            pattern_integrity = self._assess_pattern_integrity(historical_data)
            
            # 6. Tính điểm tổng thể
            overall_score = self._calculate_overall_score(
                completeness_metrics, consistency_metrics, 
                freshness_metrics, pattern_integrity
            )
            
            # 7. Tạo khuyến nghị
            recommendations = self._generate_recommendations(
                completeness_metrics, consistency_metrics, 
                freshness_metrics, gap_analysis, pattern_integrity
            )
            
            quality_report = {
                'completeness': completeness_metrics['score'],
                'consistency': consistency_metrics['score'],
                'freshness': freshness_metrics['score'],
                'pattern_integrity': pattern_integrity['score'],
                'total_records': len(historical_data),
                'complete_records': completeness_metrics['complete_count'],
                'date_gaps': gap_analysis['gaps'],
                'gap_count': len(gap_analysis['gaps']),
                'quality_score': overall_score,
                'quality_level': self._get_quality_level(overall_score),
                'recommendations': recommendations,
                'detailed_metrics': {
                    'completeness_details': completeness_metrics,
                    'consistency_details': consistency_metrics,
                    'freshness_details': freshness_metrics,
                    'gap_analysis': gap_analysis,
                    'pattern_integrity': pattern_integrity
                }
            }
            
            logger.info(f"Data quality assessed: {overall_score:.2%} ({self._get_quality_level(overall_score)})")
            return quality_report
            
        except Exception as e:
            logger.error(f"Error assessing data quality: {e}")
            return self._get_error_quality_report(str(e))
    
    def _assess_completeness(self, data: List[Any]) -> Dict:
        """Đánh giá tính hoàn thiện của dữ liệu"""
        try:
            total_records = len(data)
            complete_records = 0
            field_completeness = {}
            
            # Các field bắt buộc
            required_fields = ['giai_db', 'giai_1', 'giai_7', 'ngay']
            
            for record in data:
                record_complete = True
                for field in required_fields:
                    field_value = getattr(record, field, None)
                    
                    # Track field completeness
                    if field not in field_completeness:
                        field_completeness[field] = 0
                    
                    if field_value and str(field_value).strip():
                        field_completeness[field] += 1
                    else:
                        record_complete = False
                
                if record_complete:
                    complete_records += 1
            
            # Calculate field completion rates
            field_rates = {
                field: count / total_records 
                for field, count in field_completeness.items()
            }
            
            overall_completeness = complete_records / total_records if total_records > 0 else 0
            
            return {
                'score': overall_completeness,
                'complete_count': complete_records,
                'total_count': total_records,
                'field_completion_rates': field_rates,
                'missing_count': total_records - complete_records
            }
            
        except Exception as e:
            logger.error(f"Completeness assessment error: {e}")
            return {'score': 0.0, 'complete_count': 0, 'total_count': len(data)}
    
    def _assess_consistency(self, data: List[Any]) -> Dict:
        """Đánh giá tính nhất quán của dữ liệu"""
        try:
            consistency_issues = []
            total_checks = 0
            passed_checks = 0
            
            for i, record in enumerate(data):
                total_checks += 1
                
                # Check 1: Ngày hợp lệ
                if hasattr(record, 'ngay') and record.ngay:
                    if record.ngay <= datetime.now().date():
                        passed_checks += 1
                    else:
                        consistency_issues.append(f"Record {i}: Future date {record.ngay}")
                
                # Check 2: Format số giải đặc biệt
                if hasattr(record, 'giai_db') and record.giai_db:
                    if self._is_valid_number_format(record.giai_db):
                        passed_checks += 1
                    else:
                        consistency_issues.append(f"Record {i}: Invalid giai_db format")
                
                # Check 3: Kiểm tra các giải khác
                prize_fields = ['giai_1', 'giai_2', 'giai_3', 'giai_4', 'giai_5', 'giai_6', 'giai_7']
                for field in prize_fields:
                    if hasattr(record, field):
                        field_value = getattr(record, field)
                        if field_value and self._is_valid_prize_format(field_value):
                            passed_checks += 1
                        total_checks += 1
            
            consistency_score = passed_checks / total_checks if total_checks > 0 else 0
            
            return {
                'score': consistency_score,
                'passed_checks': passed_checks,
                'total_checks': total_checks,
                'issues': consistency_issues[:10],  # Limit to 10 issues
                'issue_count': len(consistency_issues)
            }
            
        except Exception as e:
            logger.error(f"Consistency assessment error: {e}")
            return {'score': 0.0, 'passed_checks': 0, 'total_checks': 1}
    
    def _assess_freshness(self, data: List[Any]) -> Dict:
        """Đánh giá độ mới của dữ liệu"""
        try:
            if not data:
                return {'score': 0.0, 'latest_date': None, 'days_old': float('inf')}
            
            # Tìm ngày mới nhất
            latest_date = max(record.ngay for record in data if hasattr(record, 'ngay') and record.ngay)
            days_old = (datetime.now().date() - latest_date).days
            
            # Tính điểm freshness (giảm theo thời gian)
            if days_old <= 1:
                freshness_score = 1.0
            elif days_old <= 7:
                freshness_score = 0.9
            elif days_old <= 30:
                freshness_score = 0.7
            elif days_old <= 90:
                freshness_score = 0.5
            else:
                freshness_score = 0.2
            
            return {
                'score': freshness_score,
                'latest_date': latest_date.isoformat(),
                'days_old': days_old,
                'freshness_level': self._get_freshness_level(days_old)
            }
            
        except Exception as e:
            logger.error(f"Freshness assessment error: {e}")
            return {'score': 0.0, 'latest_date': None, 'days_old': float('inf')}
    
    def _detect_date_gaps(self, data: List[Any]) -> Dict:
        """Phát hiện khoảng trống trong dữ liệu"""
        try:
            if len(data) < 2:
                return {'gaps': [], 'consecutive_days': 0, 'coverage_ratio': 0}
            
            # Lấy tất cả ngày có dữ liệu
            dates = sorted([record.ngay for record in data if hasattr(record, 'ngay') and record.ngay])
            
            if not dates:
                return {'gaps': [], 'consecutive_days': 0, 'coverage_ratio': 0}
            
            # Tìm gap
            gaps = []
            consecutive_days = 1
            max_consecutive = 1
            current_consecutive = 1
            
            for i in range(1, len(dates)):
                expected_date = dates[i-1] + timedelta(days=1)
                
                if dates[i] == expected_date:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    # Found gap
                    gap_days = (dates[i] - dates[i-1]).days - 1
                    if gap_days > 0:
                        gaps.append({
                            'start': dates[i-1].isoformat(),
                            'end': dates[i].isoformat(),
                            'missing_days': gap_days
                        })
                    current_consecutive = 1
            
            # Tính coverage ratio
            total_span = (dates[-1] - dates[0]).days + 1
            coverage_ratio = len(dates) / total_span if total_span > 0 else 0
            
            return {
                'gaps': gaps,
                'consecutive_days': max_consecutive,
                'coverage_ratio': coverage_ratio,
                'total_gaps': len(gaps),
                'missing_days_total': sum(gap['missing_days'] for gap in gaps)
            }
            
        except Exception as e:
            logger.error(f"Gap detection error: {e}")
            return {'gaps': [], 'consecutive_days': 0, 'coverage_ratio': 0}
    
    def _assess_pattern_integrity(self, data: List[Any]) -> Dict:
        """Đánh giá tính toàn vẹn của pattern số"""
        try:
            pattern_issues = []
            total_numbers = []
            
            for record in data:
                try:
                    numbers = record.get_all_2digit_numbers()
                    total_numbers.extend(numbers)
                    
                    # Check reasonable number count per day
                    if len(numbers) < 15 or len(numbers) > 50:
                        pattern_issues.append(f"Unusual number count: {len(numbers)} on {record.ngay}")
                        
                except Exception as e:
                    pattern_issues.append(f"Error extracting numbers from {record.ngay}: {e}")
            
            # Analyze number distribution
            number_freq = Counter(total_numbers)
            
            # Check for unrealistic frequencies
            avg_freq = len(total_numbers) / 100 if total_numbers else 0  # Average per number 00-99
            
            for number, freq in number_freq.items():
                if freq > avg_freq * 3:  # More than 3x average
                    pattern_issues.append(f"Number {number} appears unusually often: {freq} times")
            
            # Pattern integrity score
            if len(pattern_issues) == 0:
                integrity_score = 1.0
            elif len(pattern_issues) <= 3:
                integrity_score = 0.8
            elif len(pattern_issues) <= 10:
                integrity_score = 0.6
            else:
                integrity_score = 0.3
            
            return {
                'score': integrity_score,
                'issues': pattern_issues[:10],
                'total_issues': len(pattern_issues),
                'total_numbers_extracted': len(total_numbers),
                'unique_numbers': len(set(total_numbers)),
                'number_distribution_variance': self._calculate_distribution_variance(number_freq)
            }
            
        except Exception as e:
            logger.error(f"Pattern integrity assessment error: {e}")
            return {'score': 0.0, 'issues': [str(e)], 'total_issues': 1}
    
    def _calculate_overall_score(self, completeness: Dict, consistency: Dict, 
                               freshness: Dict, pattern_integrity: Dict) -> float:
        """Tính điểm chất lượng tổng thể"""
        try:
            # Weighted average
            weights = {
                'completeness': 0.3,
                'consistency': 0.3,
                'freshness': 0.2,
                'pattern_integrity': 0.2
            }
            
            overall_score = (
                completeness['score'] * weights['completeness'] +
                consistency['score'] * weights['consistency'] +
                freshness['score'] * weights['freshness'] +
                pattern_integrity['score'] * weights['pattern_integrity']
            )
            
            return round(overall_score, 3)
            
        except Exception as e:
            logger.error(f"Overall score calculation error: {e}")
            return 0.0
    
    def _generate_recommendations(self, completeness: Dict, consistency: Dict, 
                                freshness: Dict, gap_analysis: Dict, 
                                pattern_integrity: Dict) -> List[str]:
        """Tạo khuyến nghị cải thiện chất lượng dữ liệu"""
        recommendations = []
        
        try:
            # Completeness recommendations
            if completeness['score'] < 0.8:
                recommendations.append(f"Cải thiện tính hoàn thiện: {completeness['missing_count']} records thiếu dữ liệu")
            
            # Consistency recommendations  
            if consistency['score'] < 0.8:
                recommendations.append(f"Kiểm tra tính nhất quán: {consistency['issue_count']} vấn đề phát hiện")
            
            # Freshness recommendations
            if freshness['score'] < 0.7:
                recommendations.append(f"Cập nhật dữ liệu mới: dữ liệu cũ {freshness.get('days_old', 0)} ngày")
            
            # Gap recommendations
            if gap_analysis['total_gaps'] > 0:
                recommendations.append(f"Bổ sung dữ liệu thiếu: {gap_analysis['total_gaps']} khoảng trống")
            
            # Pattern recommendations
            if pattern_integrity['score'] < 0.8:
                recommendations.append(f"Kiểm tra pattern số: {pattern_integrity['total_issues']} vấn đề")
            
            if not recommendations:
                recommendations.append("Chất lượng dữ liệu tốt, không cần cải thiện")
                
        except Exception as e:
            logger.error(f"Recommendations generation error: {e}")
            recommendations.append("Lỗi tạo khuyến nghị")
        
        return recommendations
    
    # Helper methods
    def _is_valid_number_format(self, value: str) -> bool:
        """Kiểm tra format số hợp lệ"""
        if not value:
            return False
        return value.isdigit() and 3 <= len(value) <= 6
    
    def _is_valid_prize_format(self, value: str) -> bool:
        """Kiểm tra format giải thưởng hợp lệ"""
        if not value:
            return True  # Optional fields
        # Allow various formats: "12345", "12345-67890", etc.
        return bool(value.strip()) and len(value.strip()) > 0
    
    def _get_freshness_level(self, days_old: int) -> str:
        """Get freshness level description"""
        if days_old <= 1:
            return 'very_fresh'
        elif days_old <= 7:
            return 'fresh'
        elif days_old <= 30:
            return 'acceptable'
        elif days_old <= 90:
            return 'old'
        else:
            return 'very_old'
    
    def _get_quality_level(self, score: float) -> str:
        """Get quality level description"""
        if score >= self.quality_thresholds['excellent']:
            return 'excellent'
        elif score >= self.quality_thresholds['good']:
            return 'good'
        elif score >= self.quality_thresholds['fair']:
            return 'fair'
        else:
            return 'poor'
    
    def _calculate_distribution_variance(self, number_freq: Counter) -> float:
        """Calculate variance in number distribution"""
        try:
            if not number_freq:
                return 0.0
            
            frequencies = list(number_freq.values())
            mean_freq = sum(frequencies) / len(frequencies)
            variance = sum((f - mean_freq) ** 2 for f in frequencies) / len(frequencies)
            return round(variance, 2)
            
        except Exception:
            return 0.0
    
    def _get_empty_quality_report(self) -> Dict:
        """Get empty quality report"""
        return {
            'completeness': 0.0,
            'consistency': 0.0,
            'freshness': 0.0,
            'pattern_integrity': 0.0,
            'total_records': 0,
            'complete_records': 0,
            'date_gaps': [],
            'gap_count': 0,
            'quality_score': 0.0,
            'quality_level': 'poor',
            'recommendations': ['Không có dữ liệu để đánh giá'],
            'detailed_metrics': {}
        }
    
    def _get_error_quality_report(self, error_msg: str) -> Dict:
        """Get error quality report"""
        return {
            'completeness': 0.0,
            'consistency': 0.0,
            'freshness': 0.0,
            'pattern_integrity': 0.0,
            'total_records': 0,
            'complete_records': 0,
            'date_gaps': [],
            'gap_count': 0,
            'quality_score': 0.0,
            'quality_level': 'error',
            'recommendations': [f'Lỗi đánh giá chất lượng: {error_msg}'],
            'detailed_metrics': {'error': error_msg}
        }