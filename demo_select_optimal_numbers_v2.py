#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 EXAMPLE DEMONSTRATION: _select_optimal_numbers_with_intelligence_v2
Minh họa cách hoạt động của hàm chọn số thông minh
"""


def simulate_select_optimal_numbers_v2():
    """
    Mô phỏng hoạt động của hàm _select_optimal_numbers_with_intelligence_v2
    """
    print("🎯 SIMULATION: _select_optimal_numbers_with_intelligence_v2")
    print("=" * 70)

    # ✅ STAGE 0: INPUT DATA SIMULATION
    print("\n📋 STAGE 0: INPUT PREPARATION")
    print("-" * 50)

    # Giả lập optimal_methods input
    optimal_methods = {
        "day_1": [
            {
                "method_id": 101,
                "method": {"name": "BTL Miền Bắc", "id": 101},
                "predicted_numbers": ["12", "34", "56"],
                "expected_hit_rate": 0.75,
                "best_day": 1,
            },
            {
                "method_id": 102,
                "method": {"name": "Nuôi Lô Kép", "id": 102},
                "predicted_numbers": ["34", "78", "90"],
                "expected_hit_rate": 0.68,
                "best_day": 1,
            },
        ],
        "day_2": [
            {
                "method_id": 103,
                "method": {"name": "Bàm Chân 3 Càng", "id": 103},
                "predicted_numbers": ["12", "45", "67"],
                "expected_hit_rate": 0.62,
                "best_day": 2,
            }
        ],
        "day_3": [
            {
                "method_id": 104,
                "method": {"name": "Cặp Số Vàng", "id": 104},
                "predicted_numbers": ["23", "45", "89"],
                "expected_hit_rate": 0.55,
                "best_day": 3,
            }
        ],
        "summary": {"total_methods": 4},  # Sẽ bị skip
    }

    analysis_date = "2025-07-31"

    # Collect all methods
    all_methods = []
    for day_key, day_methods in optimal_methods.items():
        if day_key != "summary":
            all_methods.extend(day_methods)

    print(f"📊 Total methods collected: {len(all_methods)}")
    for i, method in enumerate(all_methods, 1):
        print(
            f"   {i}. {method['method']['name']} - Expected: {method['expected_hit_rate']:.1%}"
        )

    # ✅ STAGE 1: POSITION-AWARE SELECTION SIMULATION
    print(f"\n🔍 STAGE 1: POSITION-AWARE SELECTION")
    print("-" * 50)

    position_selections = []

    for method in all_methods:
        method_id = method["method_id"]
        method_name = method["method"]["name"]
        predicted_numbers = method["predicted_numbers"]

        print(f"\n📈 Analyzing Method {method_id}: {method_name}")
        print(f"   Predicted numbers: {predicted_numbers}")

        # Mô phỏng position analysis results
        if method_id == 101:  # BTL - thường trúng vị trí 0
            position_analysis = {
                "position_0_hits": 15,
                "position_1_hits": 3,
                "position_0_rate": 0.83,
                "position_1_rate": 0.17,
                "preferred_position": 0,
                "pattern_type": "only_0",
                "confidence": 0.85,
            }
        elif method_id == 102:  # Nuôi Lô - thường trúng vị trí 1
            position_analysis = {
                "position_0_hits": 2,
                "position_1_hits": 12,
                "position_0_rate": 0.14,
                "position_1_rate": 0.86,
                "preferred_position": 1,
                "pattern_type": "only_1",
                "confidence": 0.78,
            }
        elif method_id == 103:  # Bàm Chân - mixed pattern
            position_analysis = {
                "position_0_hits": 8,
                "position_1_hits": 7,
                "position_0_rate": 0.53,
                "position_1_rate": 0.47,
                "preferred_position": 0,
                "pattern_type": "mixed",
                "confidence": 0.55,
            }
        else:  # Cặp Số - both positions
            position_analysis = {
                "position_0_hits": 6,
                "position_1_hits": 6,
                "position_0_rate": 0.50,
                "position_1_rate": 0.50,
                "preferred_position": 0,
                "pattern_type": "both",
                "confidence": 0.50,
            }

        print(f"   Position Analysis:")
        print(f"     - Pattern Type: {position_analysis['pattern_type']}")
        print(f"     - Preferred Position: {position_analysis['preferred_position']}")
        print(f"     - Position 0 Rate: {position_analysis['position_0_rate']:.1%}")
        print(f"     - Position 1 Rate: {position_analysis['position_1_rate']:.1%}")
        print(f"     - Confidence: {position_analysis['confidence']:.1%}")

        # Smart position selection simulation
        selections = simulate_smart_position_selection(
            predicted_numbers, position_analysis, method
        )
        position_selections.extend(selections)

        print(f"   Selected numbers: {[s['number'] for s in selections]}")
        print(
            f"   Selection confidences: {[f'{s['confidence']:.2f}' for s in selections]}"
        )

    print(f"\n📊 Total position selections: {len(position_selections)}")

    # ✅ STAGE 2: DIVERSIFICATION SIMULATION
    print(f"\n🎲 STAGE 2: DIVERSIFICATION & OPTIMIZATION")
    print("-" * 50)

    # Group by number
    from collections import defaultdict

    number_groups = defaultdict(list)
    for selection in position_selections:
        number_groups[selection["number"]].append(selection)

    print(f"📊 Number groups created: {len(number_groups)}")

    diversified_selections = []

    for number, selections in number_groups.items():
        # Sort by confidence descending
        selections.sort(key=lambda x: x["confidence"], reverse=True)

        # Take best selection for this number
        best_selection = selections[0].copy()

        # Calculate diversification metrics
        method_support = len(set(s["method_info"]["method_id"] for s in selections))
        combined_confidence = sum(
            s["confidence"] for s in selections[:3]
        )  # Top 3 supporters

        diversification_score = method_support * 0.3 + combined_confidence * 0.7

        best_selection["diversification_score"] = diversification_score
        best_selection["method_support"] = method_support
        best_selection["supporting_methods"] = [
            s["method_info"]["method_id"] for s in selections
        ]

        diversified_selections.append(best_selection)

        print(f"   Number {number}:")
        print(f"     - Method Support: {method_support} methods")
        print(f"     - Combined Confidence: {combined_confidence:.2f}")
        print(f"     - Diversification Score: {diversification_score:.2f}")
        print(f"     - Supporting Methods: {best_selection['supporting_methods']}")

    # ✅ STAGE 3: FINAL OPTIMIZATION SIMULATION
    print(f"\n🏆 STAGE 3: FINAL OPTIMIZATION")
    print("-" * 50)

    # Sort by diversification score
    diversified_selections.sort(key=lambda x: x["diversification_score"], reverse=True)

    print("📊 Diversified selections ranked:")
    for i, selection in enumerate(diversified_selections, 1):
        print(
            f"   {i}. Number {selection['number']} - Score: {selection['diversification_score']:.2f}"
        )

    # Select top numbers ensuring diversity
    target_count = 15
    selected_numbers = []
    used_methods = set()

    print(f"\n🎯 Phase 1: Method Diversity Selection (target: {target_count})")

    for selection in diversified_selections:
        if len(selected_numbers) >= target_count:
            break

        number = selection["number"]
        method_id = selection["method_info"]["method_id"]

        # Avoid duplicates and prefer method diversity
        if number not in selected_numbers and (
            method_id not in used_methods or len(selected_numbers) < target_count // 2
        ):

            selected_numbers.append(number)
            used_methods.add(method_id)
            print(
                f"   ✅ Selected: {number} (Method {method_id}, Score: {selection['diversification_score']:.2f})"
            )

    # Phase 2: Fill remaining slots
    if len(selected_numbers) < target_count:
        print(
            f"\n📈 Phase 2: Fill Remaining Slots ({len(selected_numbers)}/{target_count})"
        )

        remaining_selections = [
            s for s in diversified_selections if s["number"] not in selected_numbers
        ]
        remaining_selections.sort(key=lambda x: x["confidence"], reverse=True)

        for selection in remaining_selections:
            if len(selected_numbers) >= target_count:
                break
            selected_numbers.append(selection["number"])
            print(
                f"   ✅ Added: {selection['number']} (Confidence: {selection['confidence']:.2f})"
            )

    # ✅ FINAL RESULTS
    print(f"\n🎉 FINAL RESULTS")
    print("=" * 50)

    final_numbers = sorted(selected_numbers[:target_count])

    print(f"📊 Selected Numbers ({len(final_numbers)}): {final_numbers}")
    print(f"📊 Method Coverage: {len(used_methods)} methods")
    print(f"📊 Method Distribution:")

    method_distribution = {}
    for selection in diversified_selections:
        if selection["number"] in final_numbers:
            method_id = selection["method_info"]["method_id"]
            method_name = selection["method_info"]["method_name"]
            if method_id not in method_distribution:
                method_distribution[method_id] = {"name": method_name, "numbers": []}
            method_distribution[method_id]["numbers"].append(selection["number"])

    for method_id, info in method_distribution.items():
        print(f"     Method {method_id} ({info['name']}): {info['numbers']}")

    # Simulation summary
    print(f"\n📋 SIMULATION SUMMARY")
    print("-" * 30)
    print(f"✅ Total Input Methods: {len(all_methods)}")
    print(f"✅ Position Selections: {len(position_selections)}")
    print(f"✅ Unique Numbers: {len(number_groups)}")
    print(f"✅ Final Selection: {len(final_numbers)}")
    print(f"✅ Method Diversity: {len(used_methods)}/{len(all_methods)} methods used")

    return final_numbers


def simulate_smart_position_selection(predicted_numbers, position_analysis, method):
    """
    Mô phỏng smart position selection logic
    """
    selections = []
    pattern_type = position_analysis["pattern_type"]
    confidence = position_analysis["confidence"]
    preferred_position = position_analysis["preferred_position"]
    method_weight = method["expected_hit_rate"]

    if pattern_type == "only_0" and confidence > 0.5:
        # Chọn số ở vị trí 0 với confidence cao
        if len(predicted_numbers) > 0:
            selections.append(
                {
                    "number": predicted_numbers[0],
                    "confidence": confidence * method_weight,
                    "position": 0,
                    "method_info": {
                        "method_id": method["method_id"],
                        "method_name": method["method"]["name"],
                        "expected_hit_rate": method["expected_hit_rate"],
                    },
                }
            )

    elif pattern_type == "only_1" and confidence > 0.5:
        # Chọn số ở vị trí 1 với confidence cao
        if len(predicted_numbers) > 1:
            selections.append(
                {
                    "number": predicted_numbers[1],
                    "confidence": confidence * method_weight,
                    "position": 1,
                    "method_info": {
                        "method_id": method["method_id"],
                        "method_name": method["method"]["name"],
                        "expected_hit_rate": method["expected_hit_rate"],
                    },
                }
            )

    elif pattern_type in ["both", "mixed"] and confidence > 0.3:
        # Chọn cả 2 vị trí với trọng số khác nhau
        for i, number in enumerate(predicted_numbers[:2]):
            position_confidence = confidence * (0.6 if i == preferred_position else 0.4)
            selections.append(
                {
                    "number": number,
                    "confidence": position_confidence * method_weight,
                    "position": i,
                    "method_info": {
                        "method_id": method["method_id"],
                        "method_name": method["method"]["name"],
                        "expected_hit_rate": method["expected_hit_rate"],
                    },
                }
            )
    else:
        # Fallback: chọn số đầu tiên với confidence thấp
        if len(predicted_numbers) > 0:
            selections.append(
                {
                    "number": predicted_numbers[0],
                    "confidence": 0.3 * method_weight,
                    "position": 0,
                    "method_info": {
                        "method_id": method["method_id"],
                        "method_name": method["method"]["name"],
                        "expected_hit_rate": method["expected_hit_rate"],
                    },
                }
            )

    return selections


if __name__ == "__main__":
    print("🚀 STARTING SIMULATION...")
    print("=" * 70)

    final_numbers = simulate_select_optimal_numbers_v2()

    print(f"\n🎯 SIMULATION COMPLETE!")
    print(f"Final optimal numbers: {final_numbers}")
    print("=" * 70)
