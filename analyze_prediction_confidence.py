#!/usr/bin/env python3
"""
🔍 PHÂN TÍCH CONFIDENCE THRESHOLD - PREDICTION INSIGHTS
Công cụ phân tích tại sao các dự đoán không đạt mức tin cậy
"""

import json
import os
import sys
from datetime import datetime

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def analyze_prediction_confidence():
    """
    Phân tích chi tiết về confidence thresholds và score calculation
    """
    print("=" * 80)
    print("🔍 PHÂN TÍCH CONFIDENCE THRESHOLD - PREDICTION INSIGHTS")
    print("=" * 80)

    print("\n📊 CÔNG THỨC TÍNH ĐIỂM (Score Calculation):")
    print(
        "   total_score = (frequency_score * 0.3 + momentum_score * 0.4 + significance_score * 0.3) * 100"
    )
    print("\n📈 CHI TIẾT CÁC THÀNH PHẦN:")

    print("\n1️⃣ FREQUENCY SCORE:")
    print("   • Công thức: min(1.0, frequency / 100.0)")
    print("   • Ý nghĩa: Tần suất xuất hiện tương đối")
    print("   • Trọng số: 30%")

    print("\n2️⃣ MOMENTUM SCORE:")
    print("   • trend = 'up'    → score = 0.8")
    print("   • trend = 'stable'→ score = 0.5")
    print("   • trend = 'down'  → score = 0.2")
    print("   • Trọng số: 40% (cao nhất)")

    print("\n3️⃣ SIGNIFICANCE SCORE:")
    print("   • Công thức: min(1.0, percentage / 15.0)")
    print("   • Ý nghĩa: Phần trăm xuất hiện, chuẩn hóa với 15% là cao")
    print("   • Trọng số: 30%")

    print("\n🎯 CONFIDENCE THRESHOLDS:")
    print("   • HIGH Probability  : score ≥ 70 điểm")
    print("   • MEDIUM Probability: score ≥ 50 điểm")
    print("   • FALLBACK Threshold: score ≥ 30 điểm")

    print("\n📊 VÍ DỤ TÍNH ĐIỂM:")
    examples = [
        {"digit": "7", "frequency": 25, "percentage": 12.5, "trend": "up"},
        {"digit": "3", "frequency": 15, "percentage": 8.3, "trend": "stable"},
        {"digit": "1", "frequency": 8, "percentage": 5.2, "trend": "down"},
    ]

    for example in examples:
        freq_score = min(1.0, example["frequency"] / 100.0)
        momentum_score = (
            0.8
            if example["trend"] == "up"
            else 0.5 if example["trend"] == "stable" else 0.2
        )
        sig_score = min(1.0, example["percentage"] / 15.0)
        total_score = (freq_score * 0.3 + momentum_score * 0.4 + sig_score * 0.3) * 100

        confidence_level = (
            "HIGH" if total_score >= 70 else "MEDIUM" if total_score >= 50 else "LOW"
        )

        print(f"\n   Digit {example['digit']}:")
        print(f"     • Frequency: {example['frequency']} → Score: {freq_score:.2f}")
        print(f"     • Trend: {example['trend']} → Score: {momentum_score:.2f}")
        print(
            f"     • Percentage: {example['percentage']:.1f}% → Score: {sig_score:.2f}"
        )
        print(f"     • TOTAL: {total_score:.2f} → {confidence_level}")

    print("\n⚠️ CÁC VẤN ĐỀ THƯỜNG GẶP:")
    print("   1. Dữ liệu quá đồng đều → percentage thấp → significance_score thấp")
    print("   2. Hầu hết trend = 'stable' → momentum_score = 0.5 → điểm trung bình")
    print("   3. Frequency thấp → frequency_score thấp")
    print("   4. Thiếu dữ liệu → fallback về giá trị mặc định")

    print("\n💡 GIẢI PHÁP ĐIỀU CHỈNH:")
    print("   • Giảm threshold xuống phù hợp với chất lượng dữ liệu")
    print("   • Điều chỉnh trọng số dựa trên độ tin cậy của từng thành phần")
    print("   • Sử dụng adaptive threshold dựa trên max_score")
    print("   • Tăng cường xử lý dữ liệu thiếu")

    print("\n🔧 ADAPTIVE THRESHOLD LOGIC:")
    print("   if max_score < 50:")
    print("       high_threshold = max_score * 0.8")
    print("       medium_threshold = max_score * 0.6")
    print("   else:")
    print("       high_threshold = 45")
    print("       medium_threshold = 30")

    print("\n✅ KẾT LUẬN:")
    print("   Hệ thống đã được cải thiện với:")
    print("   • Logging chi tiết để tracking score calculation")
    print("   • Adaptive threshold dựa trên chất lượng dữ liệu")
    print("   • Data quality diagnosis")
    print("   • Fallback predictions khi không đủ confidence")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    analyze_prediction_confidence()
