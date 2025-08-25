#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔗 DATA INTEGRATION SERVICE
Connects Ultimate Prediction System with real NumberFrequencyStats data
"""

import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from django.db.models import Count, Q
from django.utils import timezone

# Import real models
from results.models import KetQuaXoSo, NumberFrequencyStats

logger = logging.getLogger(__name__)


class RealDataIntegrationService:
    """
    Service để kết nối Ultimate Prediction System với dữ liệu thực tế
    """

    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    def get_real_lottery_numbers(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 1000,
    ) -> List[int]:
        """
        Lấy dữ liệu số thực tế từ NumberFrequencyStats

        Args:
            start_date: Ngày bắt đầu (default: 30 ngày trước)
            end_date: Ngày kết thúc (default: hôm nay)
            limit: Giới hạn số lượng records

        Returns:
            List[int]: Danh sách các số đã xuất hiện
        """
        try:
            # Default date range: last 30 days
            if not end_date:
                end_date = timezone.now().date()
            if not start_date:
                start_date = end_date - timedelta(days=30)

            logger.info(f"Fetching real lottery data from {start_date} to {end_date}")

            # Query NumberFrequencyStats for real data
            frequency_stats = NumberFrequencyStats.objects.filter(
                date__range=[start_date, end_date]
            ).order_by("-date")[:limit]

            # Extract numbers
            real_numbers = []
            for stat in frequency_stats:
                try:
                    number = int(stat.number)
                    real_numbers.append(number)
                except (ValueError, TypeError):
                    continue

            logger.info(f"Retrieved {len(real_numbers)} real lottery numbers")
            return real_numbers

        except Exception as e:
            logger.error(f"Failed to get real lottery numbers: {e}")
            # Fallback to sample data
            return self._get_fallback_data()

    def get_historical_patterns(self, days_back: int = 90) -> Dict[str, Any]:
        """
        Phân tích patterns từ dữ liệu lịch sử thực tế

        Args:
            days_back: Số ngày lùi lại để phân tích

        Returns:
            Dict chứa patterns phân tích
        """
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days_back)

            # Get frequency distribution
            frequency_data = (
                NumberFrequencyStats.objects.filter(date__range=[start_date, end_date])
                .values("number")
                .annotate(
                    total_count=Count("id"),
                    special_count=Count("id", filter=Q(appeared_in_special=True)),
                    first_count=Count("id", filter=Q(appeared_in_first=True)),
                )
                .order_by("-total_count")
            )

            # Analyze patterns
            hot_numbers = []
            cold_numbers = []
            special_favorites = []

            for item in frequency_data[:20]:  # Top 20
                number = item["number"]
                total = item["total_count"]
                special = item["special_count"]

                if total >= 3:  # Hot threshold
                    hot_numbers.append(
                        {
                            "number": number,
                            "frequency": total,
                            "special_rate": special / total if total > 0 else 0,
                        }
                    )

                if special >= 2:  # Special prize favorites
                    special_favorites.append(
                        {"number": number, "special_appearances": special}
                    )

            # Find cold numbers (rarely appearing)
            all_possible = set(f"{i:02d}" for i in range(100))
            appearing_numbers = set(item["number"] for item in frequency_data)
            cold_candidates = all_possible - appearing_numbers

            cold_numbers = [
                {"number": num, "frequency": 0} for num in list(cold_candidates)[:10]
            ]

            return {
                "analysis_period": f"{start_date} to {end_date}",
                "total_records": len(frequency_data),
                "hot_numbers": hot_numbers[:10],
                "cold_numbers": cold_numbers,
                "special_favorites": special_favorites[:5],
                "data_quality": "real_database",
                "patterns_detected": len(hot_numbers) + len(cold_numbers),
            }

        except Exception as e:
            logger.error(f"Failed to analyze historical patterns: {e}")
            return self._get_fallback_patterns()

    def get_recent_results(self, limit: int = 7) -> List[Dict[str, Any]]:
        """
        Lấy kết quả xổ số gần đây từ KetQuaXoSo

        Args:
            limit: Số ngày gần đây

        Returns:
            List các kết quả xổ số
        """
        try:
            recent_results = KetQuaXoSo.objects.filter(ngay__isnull=False).order_by(
                "-ngay"
            )[:limit]

            results = []
            for result in recent_results:
                # Extract all prize numbers
                prize_numbers = []

                # Special prize
                if result.giai_db:
                    prize_numbers.extend(
                        self._extract_numbers_from_prize(result.giai_db)
                    )

                # First prize
                if result.giai_1:
                    prize_numbers.extend(
                        self._extract_numbers_from_prize(result.giai_1)
                    )

                # Other prizes - sample a few
                for field_name in ["giai_2_1", "giai_3_1", "giai_4_1"]:
                    prize_value = getattr(result, field_name, None)
                    if prize_value:
                        prize_numbers.extend(
                            self._extract_numbers_from_prize(prize_value)
                        )

                results.append(
                    {
                        "date": result.ngay.isoformat() if result.ngay else None,
                        "special_prize": result.giai_db,
                        "extracted_numbers": prize_numbers[
                            :10
                        ],  # Limit to prevent overflow
                        "total_numbers": len(prize_numbers),
                    }
                )

            logger.info(f"Retrieved {len(results)} recent lottery results")
            return results

        except Exception as e:
            logger.error(f"Failed to get recent results: {e}")
            return []

    def _extract_numbers_from_prize(self, prize_value: str) -> List[int]:
        """Extract 2-digit numbers from prize string"""
        if not prize_value or len(prize_value) < 2:
            return []

        numbers = []
        # Extract last 2 digits
        try:
            last_two = prize_value[-2:]
            numbers.append(int(last_two))
        except (ValueError, TypeError):
            pass

        # If 4+ digits, also extract first 2
        if len(prize_value) >= 4:
            try:
                first_two = prize_value[:2]
                numbers.append(int(first_two))
            except (ValueError, TypeError):
                pass

        return numbers

    def _get_fallback_data(self) -> List[int]:
        """Fallback sample data when real data unavailable"""
        return [
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
            11,
            39,
        ]

    def _get_fallback_patterns(self) -> Dict[str, Any]:
        """Fallback patterns when real analysis fails"""
        return {
            "analysis_period": "fallback",
            "hot_numbers": [{"number": "12", "frequency": 5}],
            "cold_numbers": [{"number": "99", "frequency": 0}],
            "data_quality": "fallback_mode",
        }

    def get_enhanced_lottery_input(
        self, 
        include_patterns: bool = True, 
        include_recent: bool = True,
        prediction_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Tạo input data tổng hợp cho Ultimate Prediction System

        Args:
            include_patterns: Có bao gồm pattern analysis không
            include_recent: Có bao gồm recent results không  
            prediction_date: Ngày cụ thể để filter dữ liệu

        Returns:
            Dict chứa lottery numbers và metadata thực tế
        """
        try:
            # Get real lottery numbers với date filtering
            if prediction_date:
                # Lấy dữ liệu từ prediction_date trở về trước 30 ngày
                start_date = prediction_date - timedelta(days=30)
                end_date = prediction_date
                real_numbers = self.get_real_lottery_numbers(start_date, end_date)
                data_source = f"real_database_filtered_{prediction_date}"
                logger.info(f"📅 Date-specific data for {prediction_date}: {len(real_numbers)} numbers")
            else:
                # Default behavior - last 30 days
                real_numbers = self.get_real_lottery_numbers()
                data_source = "real_database"

            result = {
                "lottery_numbers": real_numbers,
                "data_source": data_source,
                "total_numbers": len(real_numbers),
                "data_quality_score": 0.9 if len(real_numbers) > 50 else 0.7,
                "analysis_date": prediction_date.isoformat() if prediction_date else None,
            }

            # Include historical patterns if requested
            if include_patterns:
                patterns = self.get_historical_patterns()
                result["historical_patterns"] = patterns

            # Include recent results if requested
            if include_recent:
                recent = self.get_recent_results()
                result["recent_results"] = recent

            logger.info(
                f"Enhanced input prepared with {len(real_numbers)} real numbers"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to create enhanced input: {e}")
            return {
                "lottery_numbers": self._get_fallback_data(),
                "data_source": "fallback",
                "data_quality_score": 0.3,
            }
