#!/usr/bin/env python3
"""
🎯 Demo KepLechAnalyzer với Dữ Liệu Thực từ KetQuaXoSo
Test hiệu quả phương pháp Kép Lệch với dữ liệu thực tế

Mục tiêu:
1. Lấy dữ liệu thực từ database KetQuaXoSo
2. Phân tích giải đặc biệt và giải 7
3. Đưa ra dự đoán Kép Lệch
4. So sánh với kết quả thực tế
5. Tính toán tỷ lệ chính xác
"""

import json
import logging
import os
import sys
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")

try:
    django.setup()
    print("✅ Django setup completed")
except Exception as e:
    print(f"⚠️ Django setup failed: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_real_ketqua_data(days_back: int = 30) -> Dict[str, Any]:
    """Lấy dữ liệu thực từ KetQuaXoSo"""
    try:
        from results.models import KetQuaXoSo

        from_date = datetime.now().date() - timedelta(days=days_back)

        # Lấy dữ liệu từ database, sắp xếp theo ngày
        records = KetQuaXoSo.objects.filter(ngay__gte=from_date).order_by("ngay")

        data = {
            "records": [],
            "giai_dac_biet": {},
            "giai_7": {},
            "total_count": records.count(),
            "date_range": f"{from_date} to {datetime.now().date()}",
        }

        for record in records:
            # Chuẩn bị dữ liệu record
            record_data = {
                "ngay": record.ngay,
                "thu": record.thu,
                "giai_db": record.giai_db,
                "giai_7": record.giai_7,
                "giai_7_1": record.giai_7_1,
                "giai_7_2": record.giai_7_2,
                "giai_7_3": record.giai_7_3,
                "giai_7_4": record.giai_7_4,
            }

            data["records"].append(record_data)

            # Dữ liệu cho phân tích
            data["giai_dac_biet"][record.thu] = record.giai_db

            # Extract giải 7 numbers
            giai_7_numbers = []
            if record.giai_7:
                # Parse giải 7 full string
                for num_str in str(record.giai_7).replace(",", " ").split():
                    if num_str.isdigit() and len(num_str) >= 2:
                        giai_7_numbers.append(num_str[-2:].zfill(2))

            # Thêm từ các trường riêng lẻ
            for field in [
                record.giai_7_1,
                record.giai_7_2,
                record.giai_7_3,
                record.giai_7_4,
            ]:
                if field and str(field).isdigit():
                    giai_7_numbers.append(str(field)[-2:].zfill(2))

            data["giai_7"][record.thu] = {
                "full": record.giai_7,
                "all_7_numbers": list(set(giai_7_numbers)),  # Remove duplicates
                "date": record.ngay,
            }

        return data

    except Exception as e:
        logger.error(f"❌ Error loading real data: {e}")
        return {"error": str(e)}


def analyze_kep_lech_patterns(data: Dict[str, Any]) -> Dict[str, Any]:
    """Phân tích các pattern Kép Lệch từ dữ liệu thực"""

    # Dữ liệu Kép Lệch chuẩn
    KEP_DUONG = [
        "00",
        "02",
        "04",
        "06",
        "08",
        "10",
        "12",
        "14",
        "16",
        "18",
        "20",
        "22",
        "24",
        "26",
        "28",
        "30",
        "32",
        "34",
        "36",
        "38",
        "40",
        "42",
        "44",
        "46",
        "48",
        "50",
        "52",
        "54",
        "56",
        "58",
        "60",
        "62",
        "64",
        "66",
        "68",
        "70",
        "72",
        "74",
        "76",
        "78",
        "80",
        "82",
        "84",
        "86",
        "88",
        "90",
        "92",
        "94",
        "96",
        "98",
    ]

    KEP_AM = [
        "01",
        "03",
        "05",
        "07",
        "09",
        "11",
        "13",
        "15",
        "17",
        "19",
        "21",
        "23",
        "25",
        "27",
        "29",
        "31",
        "33",
        "35",
        "37",
        "39",
        "41",
        "43",
        "45",
        "47",
        "49",
        "51",
        "53",
        "55",
        "57",
        "59",
        "61",
        "63",
        "65",
        "67",
        "69",
        "71",
        "73",
        "75",
        "77",
        "79",
        "81",
        "83",
        "85",
        "87",
        "89",
        "91",
        "93",
        "95",
        "97",
        "99",
    ]

    SAT_KEP = [
        "12",
        "21",
        "23",
        "32",
        "34",
        "43",
        "45",
        "54",
        "56",
        "65",
        "67",
        "76",
        "78",
        "87",
        "89",
        "98",
        "90",
        "09",
    ]

    analysis = {
        "total_records": len(data.get("records", [])),
        "kep_analysis": {
            "giai_dac_biet": {
                "KEP_DUONG": [],
                "KEP_AM": [],
                "SAT_KEP": [],
                "OTHER": [],
            },
            "giai_7": {"KEP_DUONG": [], "KEP_AM": [], "SAT_KEP": [], "OTHER": []},
        },
        "frequency_stats": {
            "giai_dac_biet": {"KEP_DUONG": 0, "KEP_AM": 0, "SAT_KEP": 0, "OTHER": 0},
            "giai_7": {"KEP_DUONG": 0, "KEP_AM": 0, "SAT_KEP": 0, "OTHER": 0},
        },
        "detailed_records": [],
    }

    for record in data.get("records", []):
        record_analysis = {
            "ngay": str(record["ngay"]),
            "thu": record["thu"],
            "giai_db": record["giai_db"],
            "giai_db_2so_cuoi": (
                record["giai_db"][-2:] if len(record["giai_db"]) >= 2 else ""
            ),
            "giai_7_numbers": data["giai_7"]
            .get(record["thu"], {})
            .get("all_7_numbers", []),
            "kep_patterns": {"giai_db": None, "giai_7": []},
        }

        # Phân tích giải đặc biệt
        if record_analysis["giai_db_2so_cuoi"]:
            so_cuoi = record_analysis["giai_db_2so_cuoi"]

            if so_cuoi in KEP_DUONG:
                record_analysis["kep_patterns"]["giai_db"] = "KEP_DUONG"
                analysis["kep_analysis"]["giai_dac_biet"]["KEP_DUONG"].append(so_cuoi)
                analysis["frequency_stats"]["giai_dac_biet"]["KEP_DUONG"] += 1
            elif so_cuoi in KEP_AM:
                record_analysis["kep_patterns"]["giai_db"] = "KEP_AM"
                analysis["kep_analysis"]["giai_dac_biet"]["KEP_AM"].append(so_cuoi)
                analysis["frequency_stats"]["giai_dac_biet"]["KEP_AM"] += 1
            elif so_cuoi in SAT_KEP:
                record_analysis["kep_patterns"]["giai_db"] = "SAT_KEP"
                analysis["kep_analysis"]["giai_dac_biet"]["SAT_KEP"].append(so_cuoi)
                analysis["frequency_stats"]["giai_dac_biet"]["SAT_KEP"] += 1
            else:
                record_analysis["kep_patterns"]["giai_db"] = "OTHER"
                analysis["kep_analysis"]["giai_dac_biet"]["OTHER"].append(so_cuoi)
                analysis["frequency_stats"]["giai_dac_biet"]["OTHER"] += 1

        # Phân tích giải 7
        for number in record_analysis["giai_7_numbers"]:
            kep_type = None
            if number in KEP_DUONG:
                kep_type = "KEP_DUONG"
            elif number in KEP_AM:
                kep_type = "KEP_AM"
            elif number in SAT_KEP:
                kep_type = "SAT_KEP"
            else:
                kep_type = "OTHER"

            record_analysis["kep_patterns"]["giai_7"].append(
                {"number": number, "type": kep_type}
            )

            analysis["kep_analysis"]["giai_7"][kep_type].append(number)
            analysis["frequency_stats"]["giai_7"][kep_type] += 1

        analysis["detailed_records"].append(record_analysis)

    return analysis


def generate_predictions_from_history(
    analysis: Dict[str, Any], prediction_date: date
) -> Dict[str, Any]:
    """Tạo dự đoán dựa trên lịch sử phân tích"""

    # Dữ liệu Kép Lệch
    KEP_DUONG = [
        "00",
        "02",
        "04",
        "06",
        "08",
        "10",
        "12",
        "14",
        "16",
        "18",
        "20",
        "22",
        "24",
        "26",
        "28",
        "30",
        "32",
        "34",
        "36",
        "38",
        "40",
        "42",
        "44",
        "46",
        "48",
        "50",
        "52",
        "54",
        "56",
        "58",
        "60",
        "62",
        "64",
        "66",
        "68",
        "70",
        "72",
        "74",
        "76",
        "78",
        "80",
        "82",
        "84",
        "86",
        "88",
        "90",
        "92",
        "94",
        "96",
        "98",
    ]

    KEP_AM = [
        "01",
        "03",
        "05",
        "07",
        "09",
        "11",
        "13",
        "15",
        "17",
        "19",
        "21",
        "23",
        "25",
        "27",
        "29",
        "31",
        "33",
        "35",
        "37",
        "39",
        "41",
        "43",
        "45",
        "47",
        "49",
        "51",
        "53",
        "55",
        "57",
        "59",
        "61",
        "63",
        "65",
        "67",
        "69",
        "71",
        "73",
        "75",
        "77",
        "79",
        "81",
        "83",
        "85",
        "87",
        "89",
        "91",
        "93",
        "95",
        "97",
        "99",
    ]

    SAT_KEP = [
        "12",
        "21",
        "23",
        "32",
        "34",
        "43",
        "45",
        "54",
        "56",
        "65",
        "67",
        "76",
        "78",
        "87",
        "89",
        "98",
        "90",
        "09",
    ]

    # Tính tần suất xuất hiện
    freq_stats = analysis.get("frequency_stats", {})
    total_db = sum(freq_stats.get("giai_dac_biet", {}).values())
    total_g7 = sum(freq_stats.get("giai_7", {}).values())

    if total_db == 0:
        return {"error": "Không có dữ liệu để phân tích"}

    # Tính tỷ lệ từng loại kép
    db_ratios = {}
    g7_ratios = {}

    for kep_type in ["KEP_DUONG", "KEP_AM", "SAT_KEP"]:
        db_ratios[kep_type] = (
            freq_stats.get("giai_dac_biet", {}).get(kep_type, 0) / total_db
            if total_db > 0
            else 0
        )
        g7_ratios[kep_type] = (
            freq_stats.get("giai_7", {}).get(kep_type, 0) / total_g7
            if total_g7 > 0
            else 0
        )

    # Tạo dự đoán dựa trên pattern
    predictions = []

    # Method 1: Frequency-based prediction (từ giải đặc biệt)
    if db_ratios["KEP_DUONG"] < 0.3:  # Kép dương ít xuất hiện
        predictions.extend(
            [
                {
                    "number": "00",
                    "source": "KEP_DUONG",
                    "confidence": 0.8,
                    "reason": "Kép dương thiếu",
                },
                {
                    "number": "02",
                    "source": "KEP_DUONG",
                    "confidence": 0.7,
                    "reason": "Kép dương thiếu",
                },
                {
                    "number": "04",
                    "source": "KEP_DUONG",
                    "confidence": 0.6,
                    "reason": "Kép dương thiếu",
                },
            ]
        )

    if db_ratios["KEP_AM"] < 0.3:  # Kép âm ít xuất hiện
        predictions.extend(
            [
                {
                    "number": "01",
                    "source": "KEP_AM",
                    "confidence": 0.8,
                    "reason": "Kép âm thiếu",
                },
                {
                    "number": "03",
                    "source": "KEP_AM",
                    "confidence": 0.7,
                    "reason": "Kép âm thiếu",
                },
                {
                    "number": "05",
                    "source": "KEP_AM",
                    "confidence": 0.6,
                    "reason": "Kép âm thiếu",
                },
            ]
        )

    if db_ratios["SAT_KEP"] < 0.3:  # Sát kép ít xuất hiện
        predictions.extend(
            [
                {
                    "number": "12",
                    "source": "SAT_KEP",
                    "confidence": 0.9,
                    "reason": "Sát kép thiếu",
                },
                {
                    "number": "21",
                    "source": "SAT_KEP",
                    "confidence": 0.8,
                    "reason": "Sát kép thiếu",
                },
                {
                    "number": "23",
                    "source": "SAT_KEP",
                    "confidence": 0.7,
                    "reason": "Sát kép thiếu",
                },
            ]
        )

    # Method 2: Counter-trend prediction
    max_ratio_type = max(db_ratios, key=db_ratios.get)
    if db_ratios[max_ratio_type] > 0.5:  # Một loại xuất hiện quá nhiều
        counter_types = [t for t in db_ratios.keys() if t != max_ratio_type]
        for counter_type in counter_types:
            if counter_type == "KEP_DUONG":
                predictions.append(
                    {
                        "number": "06",
                        "source": counter_type,
                        "confidence": 0.6,
                        "reason": f"Counter {max_ratio_type}",
                    }
                )
            elif counter_type == "KEP_AM":
                predictions.append(
                    {
                        "number": "07",
                        "source": counter_type,
                        "confidence": 0.6,
                        "reason": f"Counter {max_ratio_type}",
                    }
                )
            elif counter_type == "SAT_KEP":
                predictions.append(
                    {
                        "number": "32",
                        "source": counter_type,
                        "confidence": 0.6,
                        "reason": f"Counter {max_ratio_type}",
                    }
                )

    # Method 3: Giải 7 influence
    max_g7_type = max(g7_ratios, key=g7_ratios.get) if g7_ratios else None
    if max_g7_type and g7_ratios[max_g7_type] > 0.4:
        # Giải 7 có ảnh hưởng đến giải đặc biệt
        if max_g7_type == "KEP_DUONG":
            predictions.append(
                {
                    "number": "08",
                    "source": "G7_INFLUENCE",
                    "confidence": 0.5,
                    "reason": "Giải 7 ảnh hưởng kép dương",
                }
            )
        elif max_g7_type == "KEP_AM":
            predictions.append(
                {
                    "number": "09",
                    "source": "G7_INFLUENCE",
                    "confidence": 0.5,
                    "reason": "Giải 7 ảnh hưởng kép âm",
                }
            )
        elif max_g7_type == "SAT_KEP":
            predictions.append(
                {
                    "number": "34",
                    "source": "G7_INFLUENCE",
                    "confidence": 0.5,
                    "reason": "Giải 7 ảnh hưởng sát kép",
                }
            )

    # Default predictions nếu không có pattern rõ ràng
    if not predictions:
        predictions = [
            {
                "number": "12",
                "source": "DEFAULT",
                "confidence": 0.4,
                "reason": "Sát kép phổ biến",
            },
            {
                "number": "00",
                "source": "DEFAULT",
                "confidence": 0.4,
                "reason": "Kép dương phổ biến",
            },
            {
                "number": "01",
                "source": "DEFAULT",
                "confidence": 0.4,
                "reason": "Kép âm phổ biến",
            },
        ]

    # Sắp xếp theo confidence
    predictions.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "prediction_date": str(prediction_date),
        "predictions": predictions[:10],  # Top 10 predictions
        "analysis_summary": {
            "total_records": analysis["total_records"],
            "db_ratios": db_ratios,
            "g7_ratios": g7_ratios,
            "dominant_db_type": max_ratio_type,
            "dominant_g7_type": max_g7_type,
        },
        "method_used": ["frequency_based", "counter_trend", "g7_influence"],
    }


def evaluate_predictions(
    predictions: Dict[str, Any], actual_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Đánh giá hiệu quả của dự đoán"""

    if not actual_results:
        return {"error": "Không có kết quả thực tế để đánh giá"}

    evaluation = {
        "total_predictions": len(predictions.get("predictions", [])),
        "total_actual_results": len(actual_results),
        "hits": [],
        "misses": [],
        "accuracy_stats": {
            "hit_count": 0,
            "miss_count": 0,
            "hit_rate": 0.0,
            "confidence_weighted_score": 0.0,
        },
        "detailed_comparison": [],
    }

    predicted_numbers = [p["number"] for p in predictions.get("predictions", [])]

    for actual in actual_results:
        actual_2so_cuoi = actual["giai_db"][-2:] if len(actual["giai_db"]) >= 2 else ""

        comparison = {
            "date": str(actual["ngay"]),
            "actual_giai_db": actual["giai_db"],
            "actual_2so_cuoi": actual_2so_cuoi,
            "predicted": actual_2so_cuoi in predicted_numbers,
            "matching_prediction": None,
        }

        if comparison["predicted"]:
            # Tìm prediction match
            for pred in predictions.get("predictions", []):
                if pred["number"] == actual_2so_cuoi:
                    comparison["matching_prediction"] = pred
                    evaluation["hits"].append(comparison)
                    evaluation["accuracy_stats"]["hit_count"] += 1
                    break
        else:
            evaluation["misses"].append(comparison)
            evaluation["accuracy_stats"]["miss_count"] += 1

        evaluation["detailed_comparison"].append(comparison)

    # Tính toán accuracy
    total_tests = len(actual_results)
    if total_tests > 0:
        evaluation["accuracy_stats"]["hit_rate"] = (
            evaluation["accuracy_stats"]["hit_count"] / total_tests
        )

        # Confidence weighted score
        total_confidence = 0
        hit_confidence = 0
        for pred in predictions.get("predictions", []):
            total_confidence += pred["confidence"]
            for hit in evaluation["hits"]:
                if hit.get("matching_prediction", {}).get("number") == pred["number"]:
                    hit_confidence += pred["confidence"]

        if total_confidence > 0:
            evaluation["accuracy_stats"]["confidence_weighted_score"] = (
                hit_confidence / total_confidence
            )

    return evaluation


def main():
    """Demo chính"""
    print("=" * 80)
    print("🎯 DEMO: KepLechAnalyzer với Dữ Liệu Thực từ KetQuaXoSo")
    print("=" * 80)

    try:
        # Bước 1: Lấy dữ liệu thực
        print("📊 BƯỚC 1: Lấy dữ liệu thực từ database")
        print("-" * 50)

        data = get_real_ketqua_data(days_back=60)  # Lấy 60 ngày

        if "error" in data:
            print(f"❌ Lỗi: {data['error']}")
            return

        print(f"✅ Đã lấy {data['total_count']} bản ghi")
        print(f"✅ Phạm vi: {data['date_range']}")
        print()

        # Bước 2: Phân tích pattern
        print("🔍 BƯỚC 2: Phân tích các pattern Kép Lệch")
        print("-" * 50)

        analysis = analyze_kep_lech_patterns(data)

        print(f"📈 Tổng số bản ghi phân tích: {analysis['total_records']}")
        print()
        print("📊 Thống kê Giải Đặc Biệt:")
        for kep_type, count in analysis["frequency_stats"]["giai_dac_biet"].items():
            percentage = (
                (count / analysis["total_records"] * 100)
                if analysis["total_records"] > 0
                else 0
            )
            print(f"   • {kep_type}: {count} lần ({percentage:.1f}%)")

        print()
        print("📊 Thống kê Giải 7:")
        total_g7 = sum(analysis["frequency_stats"]["giai_7"].values())
        for kep_type, count in analysis["frequency_stats"]["giai_7"].items():
            percentage = (count / total_g7 * 100) if total_g7 > 0 else 0
            print(f"   • {kep_type}: {count} lần ({percentage:.1f}%)")
        print()

        # Bước 3: Hiển thị chi tiết một số ngày
        print("📋 BƯỚC 3: Chi tiết một số ngày gần đây")
        print("-" * 50)

        recent_records = analysis["detailed_records"][-10:]  # 10 ngày gần nhất
        for record in recent_records:
            print(f"📅 {record['ngay']} ({record['thu']}):")
            print(
                f"   • Giải ĐB: {record['giai_db']} → 2 số cuối: {record['giai_db_2so_cuoi']} ({record['kep_patterns']['giai_db']})"
            )
            if record["giai_7_numbers"]:
                g7_patterns = [
                    f"{p['number']}({p['type']})"
                    for p in record["kep_patterns"]["giai_7"]
                ]
                print(
                    f"   • Giải 7: {record['giai_7_numbers']} → Patterns: {g7_patterns}"
                )
            print()

        # Bước 4: Tạo dự đoán
        print("🎯 BƯỚC 4: Tạo dự đoán cho ngày tiếp theo")
        print("-" * 50)

        # Sử dụng 80% dữ liệu để training, 20% để test
        split_point = int(len(data["records"]) * 0.8)
        training_data = data["records"][:split_point]
        test_data = data["records"][split_point:]

        # Tạo analysis từ training data
        training_data_formatted = {
            "records": training_data,
            "giai_7": {
                rec["thu"]: data["giai_7"].get(rec["thu"], {}) for rec in training_data
            },
        }
        training_analysis = analyze_kep_lech_patterns(training_data_formatted)

        if test_data:
            prediction_date = test_data[0]["ngay"]
            predictions = generate_predictions_from_history(
                training_analysis, prediction_date
            )

            print(f"🔮 Dự đoán cho ngày {prediction_date}:")
            for i, pred in enumerate(predictions["predictions"][:5], 1):
                print(
                    f"   {i}. Số {pred['number']} ({pred['source']}) - Confidence: {pred['confidence']:.1%}"
                )
                print(f"      Lý do: {pred['reason']}")
            print()

            # Bước 5: Đánh giá hiệu quả
            print("📊 BƯỚC 5: Đánh giá hiệu quả dự đoán")
            print("-" * 50)

            evaluation = evaluate_predictions(predictions, test_data)

            print(f"🎯 Tổng số dự đoán: {evaluation['total_predictions']}")
            print(f"🎯 Số ngày test: {evaluation['total_actual_results']}")
            print(f"🎯 Số lần trúng: {evaluation['accuracy_stats']['hit_count']}")
            print(f"🎯 Tỷ lệ chính xác: {evaluation['accuracy_stats']['hit_rate']:.1%}")
            print(
                f"🎯 Điểm confidence trọng số: {evaluation['accuracy_stats']['confidence_weighted_score']:.1%}"
            )
            print()

            # Chi tiết kết quả trúng
            if evaluation["hits"]:
                print("✅ Các lần dự đoán TRÚNG:")
                for hit in evaluation["hits"]:
                    pred = hit["matching_prediction"]
                    print(
                        f"   • {hit['date']}: Dự đoán {pred['number']} → Thực tế {hit['actual_giai_db']} ✓"
                    )
                    print(
                        f"     Confidence: {pred['confidence']:.1%}, Lý do: {pred['reason']}"
                    )
                print()

            # Chi tiết kết quả sai
            if evaluation["misses"]:
                print("❌ Các lần dự đoán SAI:")
                for miss in evaluation["misses"][:5]:  # Chỉ hiển thị 5 lần đầu
                    print(
                        f"   • {miss['date']}: Thực tế {miss['actual_giai_db']} (số cuối: {miss['actual_2so_cuoi']}) - Không có trong dự đoán"
                    )
                if len(evaluation["misses"]) > 5:
                    print(f"   ... và {len(evaluation['misses']) - 5} lần khác")
                print()

            # Bước 6: Lưu kết quả
            print("💾 BƯỚC 6: Lưu kết quả demo")
            print("-" * 50)

            demo_results = {
                "timestamp": datetime.now().isoformat(),
                "data_info": {
                    "total_records": data["total_count"],
                    "date_range": data["date_range"],
                    "training_records": len(training_data),
                    "test_records": len(test_data),
                },
                "analysis": analysis,
                "predictions": predictions,
                "evaluation": evaluation,
                "summary": {
                    "hit_rate": evaluation["accuracy_stats"]["hit_rate"],
                    "confidence_score": evaluation["accuracy_stats"][
                        "confidence_weighted_score"
                    ],
                    "method_effectiveness": (
                        "HIGH"
                        if evaluation["accuracy_stats"]["hit_rate"] > 0.3
                        else (
                            "MEDIUM"
                            if evaluation["accuracy_stats"]["hit_rate"] > 0.2
                            else "LOW"
                        )
                    ),
                },
            }

            output_file = f"kep_lech_real_data_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(demo_results, f, ensure_ascii=False, indent=2, default=str)

            print(f"✅ Kết quả đã được lưu: {output_file}")

        else:
            print("⚠️ Không có dữ liệu test để đánh giá")

        print()

        # Tóm tắt cuối cùng
        print("=" * 80)
        print("📋 TÓM TẮT DEMO")
        print("=" * 80)

        if test_data and "evaluation" in locals():
            hit_rate = evaluation["accuracy_stats"]["hit_rate"]
            confidence_score = evaluation["accuracy_stats"]["confidence_weighted_score"]

            if hit_rate > 0.3:
                effectiveness = "🔥 CAO - Phương pháp hiệu quả"
            elif hit_rate > 0.2:
                effectiveness = "⚡ TRUNG BÌNH - Có tiềm năng"
            else:
                effectiveness = "⚠️ THẤP - Cần cải thiện"

            print(f"✅ Đã phân tích {data['total_count']} bản ghi thực từ KetQuaXoSo")
            print(f"✅ Tỷ lệ dự đoán chính xác: {hit_rate:.1%}")
            print(f"✅ Điểm confidence trọng số: {confidence_score:.1%}")
            print(f"✅ Hiệu quả phương pháp: {effectiveness}")

            # Khuyến nghị
            print()
            print("💡 KHUYẾN NGHỊ:")
            if hit_rate > 0.25:
                print("   • Phương pháp Kép Lệch có tiềm năng trong dự đoán")
                print("   • Nên kết hợp với các phương pháp khác để tăng độ chính xác")
                print("   • Theo dõi performance trong thời gian dài hơn")
            else:
                print("   • Cần cải thiện thuật toán dự đoán")
                print(
                    "   • Xem xét thêm các yếu tố khác (ngày trong tuần, xu hướng...)"
                )
                print("   • Không nên dựa hoàn toàn vào phương pháp này")
        else:
            print("⚠️ Không đủ dữ liệu để đánh giá hiệu quả")
            print(f"✅ Đã phân tích {data['total_count']} bản ghi thực từ KetQuaXoSo")
            print("✅ Dữ liệu pattern đã được thu thập thành công")

        print("=" * 80)

    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
