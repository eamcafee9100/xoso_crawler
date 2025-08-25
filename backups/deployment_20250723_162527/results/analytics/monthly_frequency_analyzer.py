class MonthlyFrequencyAnalyzer:
    """Phân tích tần suất xuất hiện theo từng giai đoạn trong tháng"""
    
    def __init__(self):
        self.db_cache = {}
    
    def analyze_monthly_frequency(self, year, month):
        """
        Phân tích tần suất xuất hiện của các số trong tháng
        
        Args:
            year: Năm cần phân tích
            month: Tháng cần phân tích
            
        Returns:
            Dict chứa thông tin phân tích tần suất
        """
        from calendar import monthrange
        import datetime
        
        # Xác định số ngày trong tháng
        days_in_month = monthrange(year, month)[1]
        
        # Chia tháng thành 3 giai đoạn
        early_days = range(1, min(11, days_in_month + 1))
        mid_days = range(11, min(21, days_in_month + 1))
        late_days = range(21, days_in_month + 1)
        
        # Lấy dữ liệu tần suất cho từng giai đoạn
        early_freq = self._get_frequency_for_period(year, month, early_days)
        mid_freq = self._get_frequency_for_period(year, month, mid_days)
        late_freq = self._get_frequency_for_period(year, month, late_days)
        
        # Phân tích tỉ lệ xuất hiện của từng số qua các giai đoạn
        number_trends = {}
        for num in range(100):
            num_str = f"{num:02d}"
            
            early_count = early_freq.get(num_str, 0)
            mid_count = mid_freq.get(num_str, 0)
            late_count = late_freq.get(num_str, 0)
            
            # Tính tỉ lệ xuất hiện trong mỗi giai đoạn
            early_rate = early_count / len(early_days) if early_days else 0
            mid_rate = mid_count / len(mid_days) if mid_days else 0
            late_rate = late_count / len(late_days) if late_days else 0
            
            # Xác định xu hướng (tăng, giảm, không đổi)
            trend = "stable"
            if early_rate < mid_rate < late_rate:
                trend = "increasing"
            elif early_rate > mid_rate > late_rate:
                trend = "decreasing"
            elif early_rate < mid_rate and mid_rate > late_rate:
                trend = "peak_middle"
            elif early_rate > mid_rate and mid_rate < late_rate:
                trend = "valley_middle"
            
            number_trends[num_str] = {
                'early_count': early_count,
                'mid_count': mid_count,
                'late_count': late_count,
                'early_rate': early_rate,
                'mid_rate': mid_rate,
                'late_rate': late_rate,
                'trend': trend,
                'total_count': early_count + mid_count + late_count
            }
        
        # Tính tổng số và số xuất hiện cho mỗi giai đoạn
        total_numbers = {
            'early': sum(early_freq.values()),
            'mid': sum(mid_freq.values()),
            'late': sum(late_freq.values())
        }
        
        # Tìm top 10 số xuất hiện nhiều nhất cho mỗi giai đoạn
        top_early = sorted(early_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        top_mid = sorted(mid_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        top_late = sorted(late_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'year': year,
            'month': month,
            'period_analysis': {
                'early': {
                    'days': list(early_days),
                    'total_numbers': total_numbers['early'],
                    'top_numbers': top_early
                },
                'mid': {
                    'days': list(mid_days),
                    'total_numbers': total_numbers['mid'],
                    'top_numbers': top_mid
                },
                'late': {
                    'days': list(late_days),
                    'total_numbers': total_numbers['late'],
                    'top_numbers': top_late
                }
            },
            'number_trends': number_trends,
            'recommended_numbers': {
                'early': [num for num, _ in top_early],
                'mid': [num for num, _ in top_mid],
                'late': [num for num, _ in top_late],
                'increasing_trend': [num for num, data in number_trends.items() 
                                    if data['trend'] == 'increasing' and data['total_count'] > 0],
                'decreasing_trend': [num for num, data in number_trends.items() 
                                    if data['trend'] == 'decreasing' and data['total_count'] > 0]
            }
        }
    
    def _get_frequency_for_period(self, year, month, days):
        """Lấy tần suất xuất hiện của các số trong một giai đoạn cụ thể"""
        from results.models import KetQuaXoSo
        import datetime
        
        frequency = {}
        
        for day in days:
            try:
                date = datetime.date(year, month, day)
                
                # Lấy kết quả xổ số của ngày này
                result = self._get_result_for_date(date)
                
                if result and hasattr(result, 'get_all_2digit_numbers'):
                    numbers = result.get_all_2digit_numbers()
                    
                    # Cập nhật tần suất
                    for num in numbers:
                        frequency[num] = frequency.get(num, 0) + 1
            except Exception as e:
                logger.error(f"Error getting data for {year}-{month}-{day}: {e}")
        
        return frequency
    
    def _get_result_for_date(self, date):
        """Lấy kết quả xổ số cho một ngày cụ thể"""
        from results.models import KetQuaXoSo
        
        # Sử dụng cache để giảm truy vấn DB
        if date in self.db_cache:
            return self.db_cache[date]
        
        try:
            result = KetQuaXoSo.objects.get(ngay=date)
            self.db_cache[date] = result
            return result
        except KetQuaXoSo.DoesNotExist:
            return None