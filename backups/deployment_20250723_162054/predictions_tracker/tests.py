"""
Test comprehensive cho hàm _get_comprehensive_historical_data
Kiểm tra hiệu quả, độ chính xác và performance
"""

import time
import unittest
from collections import defaultdict
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch

import numpy as np
from django.test import TestCase
from django.utils import timezone

from predictions_tracker.models import (
    DailyTrackingSession,
    MethodPredictionResult,
    PredictionCycle,
    PredictionMethod,
    TrackingEvaluation,
)
from predictions_tracker.views import _get_comprehensive_historical_data
from results.models import KetQuaXoSo


class TestGetComprehensiveHistoricalData(TestCase):
    """
    Test suite cho _get_comprehensive_historical_data function
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_start_time = time.time()
        print(f"\n🧪 Starting comprehensive tests for _get_comprehensive_historical_data")
    
    def setUp(self):
        """Setup test data cho mỗi test case"""
        self.target_date = "2024-12-01"
        self.target_date_obj = datetime.strptime(self.target_date, "%Y-%m-%d").date()
        
        # Tạo test methods
        self.method1 = PredictionMethod.objects.create(
            code="test_method_1",
            name="Test Method 1",
            category="frequency",
            is_active=True
        )
        self.method2 = PredictionMethod.objects.create(
            code="test_method_2", 
            name="Test Method 2",
            category="pattern",
            is_active=True
        )
        self.method3 = PredictionMethod.objects.create(
            code="test_method_3",
            name="Test Method 3", 
            category="statistical",
            is_active=True
        )
        
        # Tạo test cycle
        self.test_cycle = PredictionCycle.objects.create(
            cycle_name="Test Cycle",
            start_date=self.target_date_obj - timedelta(days=180),
            end_date=self.target_date_obj + timedelta(days=30),
            tracking_days=3,
            status="active"
        )
    
    def tearDown(self):
        """Cleanup sau mỗi test"""
        # Clear all test data
        TrackingEvaluation.objects.all().delete()
        MethodPredictionResult.objects.all().delete()
        DailyTrackingSession.objects.all().delete()
        KetQuaXoSo.objects.all().delete()
        PredictionMethod.objects.all().delete()
        PredictionCycle.objects.all().delete()
    
    def test_empty_database_returns_empty_structure(self):
        """
        ✅ TEST 1: Database rỗng should return empty structure với schema đúng
        """
        print("\n📝 Test 1: Empty database behavior")
        
        result = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[self.method1.id],
            months_back=6
        )
        
        # ✅ Validate schema
        self.assertIsInstance(result, dict)
        self.assertIn("hit_day_1", result)
        self.assertIn("hit_day_2", result)
        self.assertIn("hit_day_3", result)
        
        # ✅ Validate empty content
        for day_key in ["hit_day_1", "hit_day_2", "hit_day_3"]:
            self.assertIsInstance(result[day_key], dict)
            self.assertEqual(len(result[day_key]), 0)
        
        print(f"   ✅ Empty database test passed - correct schema returned")
    
    def test_single_method_single_session_data_structure(self):
        """
        ✅ TEST 2: Một method, một session - validate structure chi tiết
        """
        print("\n📝 Test 2: Single method, single session data structure")
        
        # Tạo test data
        session = self._create_test_session(self.target_date_obj - timedelta(days=30))
        method_result = self._create_test_method_result(session, self.method1, ["12", "34", "56"])
        
        # Tạo actual results cho 3 ngày tracking
        for day in range(1, 4):
            tracking_date = session.prediction_date + timedelta(days=day)
            self._create_test_ketqua(tracking_date, ["12", "78", "90", "34"])
        
        result = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[self.method1.id],
            months_back=2
        )
        
        # ✅ Validate structure
        self.assertIn(self.method1.id, result["hit_day_1"])
        self.assertIn(self.method1.id, result["hit_day_2"]) 
        self.assertIn(self.method1.id, result["hit_day_3"])
        
        # ✅ Validate data types
        for day_key in ["hit_day_1", "hit_day_2", "hit_day_3"]:
            day_data = result[day_key][self.method1.id]
            self.assertIsInstance(day_data, list)
            self.assertEqual(len(day_data), 1)  # 1 session
            self.assertIn(day_data[0], [0, 1])  # Binary hit data
        
        print(f"   ✅ Single method test passed - {len(result['hit_day_1'])} methods processed")
    
    def test_multiple_methods_multiple_sessions_performance(self):
        """
        ✅ TEST 3: Performance test với multiple methods và sessions
        """
        print("\n📝 Test 3: Performance test with multiple methods and sessions")
        
        start_time = time.time()
        
        # Tạo nhiều sessions cho 3 tháng
        sessions_created = 0
        for days_back in range(0, 90, 7):  # Mỗi tuần 1 session
            session_date = self.target_date_obj - timedelta(days=days_back)
            session = self._create_test_session(session_date)
            
            # Tạo method results cho tất cả 3 methods
            for method in [self.method1, self.method2, self.method3]:
                predicted_numbers = [f"{i:02d}" for i in range(10, 15)]  # 5 numbers
                method_result = self._create_test_method_result(session, method, predicted_numbers)
                
                # Tạo actual results
                for day in range(1, 4):
                    tracking_date = session.prediction_date + timedelta(days=day)
                    # Random actual numbers với một số overlap
                    actual_numbers = [f"{i:02d}" for i in range(12, 18)]
                    self._create_test_ketqua(tracking_date, actual_numbers)
            
            sessions_created += 1
        
        setup_time = time.time() - start_time
        
        # ✅ PERFORMANCE TEST
        query_start = time.time()
        result = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[self.method1.id, self.method2.id, self.method3.id],
            months_back=3
        )
        query_time = time.time() - query_start
        
        # ✅ Validate performance
        self.assertLess(query_time, 2.0, f"Query took too long: {query_time:.3f}s")
        
        # ✅ Validate data completeness
        self.assertEqual(len(result["hit_day_1"]), 3)  # 3 methods
        
        for method_id in [self.method1.id, self.method2.id, self.method3.id]:
            day1_data = result["hit_day_1"][method_id]
            self.assertGreater(len(day1_data), 5, f"Method {method_id} has insufficient data")
            self.assertEqual(len(day1_data), sessions_created, "Data count mismatch")
        
        print(f"   ✅ Performance test passed:")
        print(f"      - Setup time: {setup_time:.3f}s")
        print(f"      - Query time: {query_time:.3f}s") 
        print(f"      - Sessions: {sessions_created}")
        print(f"      - Methods: {len(result['hit_day_1'])}")
        print(f"      - Avg data points per method: {np.mean([len(v) for v in result['hit_day_1'].values()]):.1f}")
    
    def test_hit_detection_accuracy(self):
        """
        ✅ TEST 4: Kiểm tra độ chính xác của hit detection logic
        """
        print("\n📝 Test 4: Hit detection accuracy")
        
        # Test case 1: Perfect hit
        session1 = self._create_test_session(self.target_date_obj - timedelta(days=10))
        method_result1 = self._create_test_method_result(session1, self.method1, ["12", "34", "56"])
        
        # Day 1: 2/3 hit, Day 2: 1/3 hit, Day 3: 0/3 hit
        day1_actual = ["12", "34", "78"]  # 2 hits
        day2_actual = ["12", "90", "91"]  # 1 hit
        day3_actual = ["78", "90", "91"]  # 0 hits
        
        for day, actual in enumerate([day1_actual, day2_actual, day3_actual], 1):
            tracking_date = session1.prediction_date + timedelta(days=day)
            self._create_test_ketqua(tracking_date, actual)
        
        result = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[self.method1.id],
            months_back=1
        )
        
        # ✅ Validate hit detection
        day1_hits = result["hit_day_1"][self.method1.id][0]
        day2_hits = result["hit_day_2"][self.method1.id][0] 
        day3_hits = result["hit_day_3"][self.method1.id][0]
        
        self.assertEqual(day1_hits, 1, "Day 1 should have hits (2/3 numbers matched)")
        self.assertEqual(day2_hits, 1, "Day 2 should have hits (1/3 numbers matched)")
        self.assertEqual(day3_hits, 0, "Day 3 should have no hits")
        
        print(f"   ✅ Hit detection accuracy verified:")
        print(f"      - Day 1: {day1_hits} (expected 1)")
        print(f"      - Day 2: {day2_hits} (expected 1)")
        print(f"      - Day 3: {day3_hits} (expected 0)")
    
    def test_method_filtering_behavior(self):
        """
        ✅ TEST 5: Kiểm tra method filtering có hoạt động đúng không
        """
        print("\n📝 Test 5: Method filtering behavior")
        
        # Tạo data cho cả 3 methods
        session = self._create_test_session(self.target_date_obj - timedelta(days=20))
        
        for method in [self.method1, self.method2, self.method3]:
            method_result = self._create_test_method_result(session, method, ["12", "34"])
            
            # Tạo actual results
            for day in range(1, 4):
                tracking_date = session.prediction_date + timedelta(days=day)
                self._create_test_ketqua(tracking_date, ["12", "56", "78"])
        
        # Test 1: Filter chỉ method1
        result1 = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[self.method1.id],
            months_back=1
        )
        
        self.assertEqual(len(result1["hit_day_1"]), 1)
        self.assertIn(self.method1.id, result1["hit_day_1"])
        self.assertNotIn(self.method2.id, result1["hit_day_1"])
        
        # Test 2: Filter method1 và method2
        result2 = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[self.method1.id, self.method2.id],
            months_back=1
        )
        
        self.assertEqual(len(result2["hit_day_1"]), 2)
        self.assertIn(self.method1.id, result2["hit_day_1"])
        self.assertIn(self.method2.id, result2["hit_day_1"])
        self.assertNotIn(self.method3.id, result2["hit_day_1"])
        
        # Test 3: No filter (method_ids=None)
        result3 = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=None,
            months_back=1
        )
        
        self.assertEqual(len(result3["hit_day_1"]), 3)
        
        print(f"   ✅ Method filtering tests passed:")
        print(f"      - Single method filter: {len(result1['hit_day_1'])} methods")
        print(f"      - Double method filter: {len(result2['hit_day_1'])} methods")  
        print(f"      - No filter: {len(result3['hit_day_1'])} methods")
    
    def test_date_range_boundary_conditions(self):
        """
        ✅ TEST 6: Kiểm tra boundary conditions cho date ranges
        """
        print("\n📝 Test 6: Date range boundary conditions")
        
        # Tạo sessions ở các thời điểm khác nhau
        sessions_data = [
            (self.target_date_obj - timedelta(days=1), "1_day_ago"),     # Trong range
            (self.target_date_obj - timedelta(days=30), "1_month_ago"),  # Trong range
            (self.target_date_obj - timedelta(days=90), "3_months_ago"), # Trong range
            (self.target_date_obj - timedelta(days=200), "7_months_ago"), # Ngoài range
        ]
        
        created_sessions = {}
        for session_date, label in sessions_data:
            session = self._create_test_session(session_date)
            method_result = self._create_test_method_result(session, self.method1, ["12", "34"])
            created_sessions[label] = session
            
            # Tạo actual results
            for day in range(1, 4):
                tracking_date = session.prediction_date + timedelta(days=day)
                self._create_test_ketqua(tracking_date, ["12", "56"])
        
        # Test với months_back=3
        result = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[self.method1.id],
            months_back=3
        )
        
        # Should include sessions from last 3 months (90 days)
        expected_sessions = 3  # 1 day, 1 month, 3 months ago
        actual_data_points = len(result["hit_day_1"][self.method1.id])
        
        self.assertEqual(actual_data_points, expected_sessions, 
                        f"Expected {expected_sessions} sessions in 3-month range, got {actual_data_points}")
        
        print(f"   ✅ Date range boundary test passed:")
        print(f"      - Target date: {self.target_date}")
        print(f"      - Months back: 3")
        print(f"      - Expected sessions: {expected_sessions}")
        print(f"      - Actual sessions: {actual_data_points}")
    
    def test_missing_actual_results_handling(self):
        """
        ✅ TEST 7: Xử lý khi thiếu actual results cho một số ngày
        """
        print("\n📝 Test 7: Missing actual results handling")
        
        session = self._create_test_session(self.target_date_obj - timedelta(days=15))
        method_result = self._create_test_method_result(session, self.method1, ["12", "34", "56"])
        
        # Chỉ tạo actual result cho day 1 và day 3, skip day 2
        day1_date = session.prediction_date + timedelta(days=1)
        day3_date = session.prediction_date + timedelta(days=3)
        
        self._create_test_ketqua(day1_date, ["12", "78"])  # Day 1 có actual result
        # Day 2 không có actual result
        self._create_test_ketqua(day3_date, ["56", "90"])  # Day 3 có actual result
        
        result = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[self.method1.id],
            months_back=1
        )
        
        # ✅ Validate behavior với missing data
        day1_hits = result["hit_day_1"][self.method1.id][0]
        day2_hits = result["hit_day_2"][self.method1.id][0]
        day3_hits = result["hit_day_3"][self.method1.id][0]
        
        self.assertEqual(day1_hits, 1, "Day 1 should have hit (12 matched)")
        self.assertEqual(day2_hits, 0, "Day 2 should be 0 (no actual result)")
        self.assertEqual(day3_hits, 1, "Day 3 should have hit (56 matched)")
        
        print(f"   ✅ Missing actual results handling verified:")
        print(f"      - Day 1 (has result): {day1_hits}")
        print(f"      - Day 2 (missing): {day2_hits}")
        print(f"      - Day 3 (has result): {day3_hits}")
    
    def test_data_quality_and_consistency(self):
        """
        ✅ TEST 8: Kiểm tra chất lượng và consistency của data
        """
        print("\n📝 Test 8: Data quality and consistency")
        
        # Tạo consistent test data cho multiple sessions
        sessions_created = 0
        expected_hits_pattern = []
        
        for weeks_back in range(8):  # 8 weeks of data
            session_date = self.target_date_obj - timedelta(weeks=weeks_back)
            session = self._create_test_session(session_date)
            
            # Pattern: Method1 hits on day 1, Method2 hits on day 2, etc.
            predicted_numbers = ["10", "20", "30"]
            method_result = self._create_test_method_result(session, self.method1, predicted_numbers)
            
            # Create predictable hit pattern
            day_hits = []
            for day in range(1, 4):
                tracking_date = session.prediction_date + timedelta(days=day)
                
                if day == 1:  # Method1 always hits on day 1
                    actual_numbers = ["10", "40", "50"]  # Hit: 10
                    expected_hit = 1
                else:  # No hits on day 2, 3
                    actual_numbers = ["40", "50", "60"]  # No hits
                    expected_hit = 0
                
                self._create_test_ketqua(tracking_date, actual_numbers)
                day_hits.append(expected_hit)
            
            expected_hits_pattern.append(day_hits)
            sessions_created += 1
        
        result = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[self.method1.id],
            months_back=2
        )
        
        # ✅ Validate data consistency
        day1_data = result["hit_day_1"][self.method1.id]
        day2_data = result["hit_day_2"][self.method1.id]
        day3_data = result["hit_day_3"][self.method1.id]
        
        # All day1 should be hits (1), day2 and day3 should be misses (0)
        self.assertTrue(all(hit == 1 for hit in day1_data), "All day1 should be hits")
        self.assertTrue(all(hit == 0 for hit in day2_data), "All day2 should be misses")
        self.assertTrue(all(hit == 0 for hit in day3_data), "All day3 should be misses")
        
        # Validate data length
        self.assertEqual(len(day1_data), sessions_created)
        self.assertEqual(len(day2_data), sessions_created)
        self.assertEqual(len(day3_data), sessions_created)
        
        print(f"   ✅ Data quality and consistency verified:")
        print(f"      - Sessions created: {sessions_created}")
        print(f"      - Day 1 hit rate: {sum(day1_data)/len(day1_data)*100:.1f}% (expected 100%)")
        print(f"      - Day 2 hit rate: {sum(day2_data)/len(day2_data)*100:.1f}% (expected 0%)")
        print(f"      - Day 3 hit rate: {sum(day3_data)/len(day3_data)*100:.1f}% (expected 0%)")
    
    def test_memory_usage_and_scalability(self):
        """
        ✅ TEST 9: Kiểm tra memory usage và scalability
        """
        print("\n📝 Test 9: Memory usage and scalability")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Tạo large dataset
        large_sessions_count = 50
        methods_count = 5
        
        # Tạo nhiều methods
        large_methods = []
        for i in range(methods_count):
            method = PredictionMethod.objects.create(
                code=f"large_test_method_{i}",
                name=f"Large Test Method {i}",
                category="frequency",
                is_active=True
            )
            large_methods.append(method)
        
        # Tạo large sessions
        start_creation = time.time()
        for i in range(large_sessions_count):
            session_date = self.target_date_obj - timedelta(days=i*2)
            session = self._create_test_session(session_date)
            
            for method in large_methods:
                predicted_numbers = [f"{j:02d}" for j in range(10)]  # 10 numbers each
                method_result = self._create_test_method_result(session, method, predicted_numbers)
                
                # Create actual results
                for day in range(1, 4):
                    tracking_date = session.prediction_date + timedelta(days=day)
                    actual_numbers = [f"{j:02d}" for j in range(5, 15)]  # Some overlap
                    self._create_test_ketqua(tracking_date, actual_numbers)
        
        creation_time = time.time() - start_creation
        
        # Test query performance on large dataset
        query_start = time.time()
        result = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[m.id for m in large_methods],
            months_back=6
        )
        query_time = time.time() - query_start
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # ✅ Validate scalability
        self.assertLess(query_time, 5.0, f"Large query took too long: {query_time:.3f}s")
        self.assertLess(memory_increase, 100, f"Memory increase too high: {memory_increase:.1f}MB")
        
        # ✅ Validate result structure
        self.assertEqual(len(result["hit_day_1"]), methods_count)
        
        total_data_points = sum(len(data) for data in result["hit_day_1"].values())
        expected_data_points = large_sessions_count * methods_count
        
        self.assertEqual(total_data_points, expected_data_points)
        
        print(f"   ✅ Scalability test passed:")
        print(f"      - Sessions created: {large_sessions_count}")
        print(f"      - Methods: {methods_count}")
        print(f"      - Creation time: {creation_time:.3f}s")
        print(f"      - Query time: {query_time:.3f}s")
        print(f"      - Memory increase: {memory_increase:.1f}MB")
        print(f"      - Total data points: {total_data_points}")
        
        # Cleanup large dataset
        for method in large_methods:
            method.delete()
    
    def test_edge_cases_and_error_handling(self):
        """
        ✅ TEST 10: Edge cases và error handling
        """
        print("\n📝 Test 10: Edge cases and error handling")
        
        # Test case 1: Invalid target_date format
        with patch('predictions_tracker.views.logger') as mock_logger:
            result1 = _get_comprehensive_historical_data(
                target_date="invalid-date",
                method_ids=[self.method1.id],
                months_back=1
            )
            
            # Should return empty structure without crashing
            self.assertIsInstance(result1, dict)
            self.assertIn("hit_day_1", result1)
        
        # Test case 2: Non-existent method_ids
        result2 = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[99999, 99998],  # Non-existent IDs
            months_back=1
        )
        
        # Should return empty structure
        self.assertEqual(len(result2["hit_day_1"]), 0)
        
        # Test case 3: Future target_date
        future_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
        result3 = _get_comprehensive_historical_data(
            target_date=future_date,
            method_ids=[self.method1.id],
            months_back=1
        )
        
        # Should handle gracefully
        self.assertIsInstance(result3, dict)
        
        # Test case 4: Zero months_back
        result4 = _get_comprehensive_historical_data(
            target_date=self.target_date,
            method_ids=[self.method1.id],
            months_back=0
        )
        
        # Should return empty or minimal data
        self.assertIsInstance(result4, dict)
        
        print(f"   ✅ Edge cases handling verified:")
        print(f"      - Invalid date format: handled gracefully")
        print(f"      - Non-existent method IDs: {len(result2['hit_day_1'])} results")
        print(f"      - Future target date: handled gracefully")
        print(f"      - Zero months_back: handled gracefully")
    
    # ✅ HELPER METHODS
    def _create_test_session(self, prediction_date):
        """Tạo test session"""
        return DailyTrackingSession.objects.create(
            cycle=self.test_cycle,
            session_id=f"test_session_{prediction_date.strftime('%Y%m%d')}",
            prediction_date=prediction_date,
            tracking_start_date=prediction_date,
            tracking_end_date=prediction_date + timedelta(days=3),
            status="completed"
        )
    
    def _create_test_method_result(self, session, method, predicted_numbers):
        """Tạo test method result"""
        return MethodPredictionResult.objects.create(
            session=session,
            method=method,
            base_prediction_numbers=predicted_numbers,
            overall_confidence=0.8
        )
    
    def _create_test_ketqua(self, ngay, numbers):
        """Tạo test KetQuaXoSo"""
        # Convert numbers to proper format
        giai_db = numbers[0] if numbers else "12345"
        giai_others = ",".join(numbers[1:]) if len(numbers) > 1 else "67890"
        
        return KetQuaXoSo.objects.create(
            thu=f"Thứ {ngay.weekday() + 2}",
            ngay=ngay,
            giai_db=giai_db,
            giai_1=giai_others,
            giai_2=giai_others,
            giai_3=giai_others,
            giai_4=giai_others,
            giai_5=giai_others,
            giai_6=giai_others,
            giai_7=giai_others
        )
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        total_time = time.time() - cls.test_start_time
        print(f"\n🏁 All tests completed in {total_time:.3f}s")


class TestHistoricalDataBenchmark(TestCase):
    """
    Benchmark riêng để test performance chi tiết
    """
    
    def test_performance_benchmark(self):
        """
        ✅ BENCHMARK: Performance test với dataset lớn
        """
        print(f"\n🏃 Performance Benchmark Test")
        
        # Setup large dataset
        method = PredictionMethod.objects.create(
            code="benchmark_method",
            name="Benchmark Method",
            category="frequency",
            is_active=True
        )
        
        cycle = PredictionCycle.objects.create(
            cycle_name="Benchmark Cycle",
            start_date=date.today() - timedelta(days=365),
            end_date=date.today() + timedelta(days=30),
            tracking_days=3,
            status="active"
        )
        
        # Create 100 sessions over 1 year
        sessions_count = 100
        benchmark_results = {}
        
        print(f"   Creating {sessions_count} sessions...")
        setup_start = time.time()
        
        for i in range(sessions_count):
            session_date = date.today() - timedelta(days=i*3)
            session = DailyTrackingSession.objects.create(
                cycle=cycle,
                session_id=f"benchmark_session_{i}",
                prediction_date=session_date,
                tracking_start_date=session_date,
                tracking_end_date=session_date + timedelta(days=3),
                status="completed"
            )
            
            method_result = MethodPredictionResult.objects.create(
                session=session,
                method=method,
                base_prediction_numbers=[f"{j:02d}" for j in range(10)],
                overall_confidence=0.7
            )
            
            # Create actual results
            for day in range(1, 4):
                tracking_date = session_date + timedelta(days=day)
                KetQuaXoSo.objects.create(
                    thu=f"Thứ {tracking_date.weekday() + 2}",
                    ngay=tracking_date,
                    giai_db=f"{(i % 90) + 10:02d}",
                    giai_1=f"{(i % 90) + 20:02d}",
                    giai_2=f"{(i % 90) + 30:02d},{(i % 90) + 40:02d}",
                    giai_3=f"{(i % 90) + 50:02d},{(i % 90) + 60:02d}",
                    giai_4=f"{(i % 90) + 70:02d}",
                    giai_5=f"{(i % 90) + 80:02d}",
                    giai_6=f"{(i % 90) + 11:02d}",
                    giai_7=f"{(i % 90) + 12:02d}"
                )
        
        setup_time = time.time() - setup_start
        
        # Benchmark different scenarios
        scenarios = [
            {"months_back": 1, "name": "1 month"},
            {"months_back": 3, "name": "3 months"},
            {"months_back": 6, "name": "6 months"},
            {"months_back": 12, "name": "12 months"},
        ]
        
        for scenario in scenarios:
            query_start = time.time()
            result = _get_comprehensive_historical_data(
                target_date=date.today().strftime("%Y-%m-%d"),
                method_ids=[method.id],
                months_back=scenario["months_back"]
            )
            query_time = time.time() - query_start
            
            data_points = len(result["hit_day_1"].get(method.id, []))
            
            benchmark_results[scenario["name"]] = {
                "query_time": query_time,
                "data_points": data_points,
                "throughput": data_points / query_time if query_time > 0 else 0
            }
            
            # Performance assertions
            self.assertLess(query_time, 3.0, f"{scenario['name']} query too slow")
            self.assertGreater(data_points, 0, f"{scenario['name']} no data returned")
        
        # Print benchmark results
        print(f"\n   📊 Benchmark Results:")
        print(f"      Setup time: {setup_time:.3f}s ({sessions_count} sessions)")
        print(f"      {'Scenario':<12} {'Time (s)':<10} {'Data Points':<12} {'Throughput':<15}")
        print(f"      {'-'*55}")
        
        for scenario_name, metrics in benchmark_results.items():
            print(f"      {scenario_name:<12} {metrics['query_time']:<10.3f} "
                  f"{metrics['data_points']:<12} {metrics['throughput']:<15.1f}")
        
        # Overall performance check
        avg_query_time = float(np.mean([m["query_time"] for m in benchmark_results.values()]))
        self.assertLess(avg_query_time, 2.0, f"Average query time too high: {avg_query_time:.3f}s")
        
        print(f"      Average query time: {avg_query_time:.3f}s")
        print(f"   ✅ Benchmark completed successfully")


if __name__ == "__main__":
    # Chạy tests
    unittest.main(verbosity=2)