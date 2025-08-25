/**
 * 🔍 SIMPLE API RESPONSE CHECKER
 * Kiểm tra cấu trúc dữ liệu trả về từ API method-analysis-v2
 */

console.log("🚀 API RESPONSE STRUCTURE CHECKER");
console.log("=".repeat(60));

// Mock successful response structure based on your code
const mockSuccessfulResponse = {
  success: true,
  analysis_date: "2025-01-15",
  hybrid_analysis: {
    short_term_insights: {
      trend_strength: 0.75,
      volatility: 0.3,
      momentum: 0.6,
    },
    long_term_stability: {
      consistency_score: 0.8,
      reliability_index: 0.7,
    },
    forward_validation: {
      confidence_score: 0.85,
      validation_period: 30,
    },
  },
  intelligent_selections: {
    optimal_numbers: [12, 34, 56, 78, 90],
    method_contributions: [
      { method_name: "Method A", contribution: 0.3, confidence: 0.8 },
      { method_name: "Method B", contribution: 0.25, confidence: 0.75 },
    ],
    selection_strategy: {
      approach: "hybrid",
      weight_distribution: "balanced",
      risk_tolerance: "medium",
    },
  },
  optimal_methods: {
    day_1: [
      {
        method_name: "Method A1",
        hybrid_score: 85.5,
        expected_hit_rate: 0.75,
        confidence: 0.8,
        predicted_numbers: [12, 34],
      },
    ],
    day_2: [
      {
        method_name: "Method B1",
        hybrid_score: 78.9,
        expected_hit_rate: 0.68,
        confidence: 0.7,
        predicted_numbers: [23, 45],
      },
    ],
    day_3: [
      {
        method_name: "Method C1",
        hybrid_score: 76.2,
        expected_hit_rate: 0.65,
        confidence: 0.68,
        predicted_numbers: [67, 89],
      },
    ],
    summary: {
      total_qualified_methods: 3,
      target_hit_rate: 0.7,
      avg_expected_hit_rate: 0.7,
    },
  },
  performance_prediction: {
    expected_hit_rate: 0.72,
    confidence_level: "high",
    overall_confidence_score: 0.78,
    risk_assessment: {
      level: "very_low",
      score: 0.15,
      description: "Low risk based on historical data",
    },
    performance_breakdown: {
      confidence_factors: {
        data_quality: 0.9,
        method_consistency: 0.85,
        historical_accuracy: 0.8,
      },
      risk_factors: [
        "Market volatility",
        "Limited historical data for some methods",
      ],
    },
  },
};

console.log("📋 1. MAIN RESPONSE STRUCTURE");
console.log("-".repeat(40));
console.log("✅ success:", mockSuccessfulResponse.success);
console.log("📅 analysis_date:", mockSuccessfulResponse.analysis_date);
console.log("📊 Main sections:");
Object.keys(mockSuccessfulResponse).forEach((key) => {
  if (key !== "success" && key !== "analysis_date") {
    console.log(
      `   - ${key}: ${mockSuccessfulResponse[key] ? "Present" : "Missing"}`
    );
  }
});

console.log("\n📊 2. HYBRID ANALYSIS DETAILS");
console.log("-".repeat(40));
if (mockSuccessfulResponse.hybrid_analysis) {
  console.log("Keys:", Object.keys(mockSuccessfulResponse.hybrid_analysis));
  console.log(
    "Structure valid:",
    typeof mockSuccessfulResponse.hybrid_analysis === "object"
  );
} else {
  console.log("❌ Missing hybrid_analysis");
}

console.log("\n🎯 3. INTELLIGENT SELECTIONS DETAILS");
console.log("-".repeat(40));
if (mockSuccessfulResponse.intelligent_selections) {
  const is = mockSuccessfulResponse.intelligent_selections;
  console.log("Keys:", Object.keys(is));
  console.log(
    "optimal_numbers count:",
    is.optimal_numbers ? is.optimal_numbers.length : 0
  );
  console.log("optimal_numbers:", is.optimal_numbers);
  console.log(
    "method_contributions count:",
    is.method_contributions ? is.method_contributions.length : 0
  );
  console.log("selection_strategy present:", !!is.selection_strategy);
} else {
  console.log("❌ Missing intelligent_selections");
}

console.log("\n📈 4. OPTIMAL METHODS BY DAY DETAILS");
console.log("-".repeat(40));
if (mockSuccessfulResponse.optimal_methods) {
  const om = mockSuccessfulResponse.optimal_methods;
  console.log("Keys:", Object.keys(om));
  ["day_1", "day_2", "day_3"].forEach((day) => {
    if (om[day]) {
      console.log(`${day} methods count:`, om[day].length);
      if (om[day].length > 0) {
        console.log(`${day} sample method:`, {
          method_name: om[day][0].method_name,
          hybrid_score: om[day][0].hybrid_score,
          expected_hit_rate: om[day][0].expected_hit_rate,
        });
      }
    }
  });
  console.log("Summary present:", !!om.summary);
  if (om.summary) {
    console.log("Summary data:", om.summary);
  }
} else {
  console.log("❌ Missing optimal_methods");
}

console.log("\n🎲 5. PERFORMANCE PREDICTION DETAILS");
console.log("-".repeat(40));
if (mockSuccessfulResponse.performance_prediction) {
  const pp = mockSuccessfulResponse.performance_prediction;
  console.log("Keys:", Object.keys(pp));
  console.log("expected_hit_rate:", pp.expected_hit_rate);
  console.log("confidence_level:", pp.confidence_level);
  console.log("overall_confidence_score:", pp.overall_confidence_score);
  console.log("risk_assessment present:", !!pp.risk_assessment);
  console.log("performance_breakdown present:", !!pp.performance_breakdown);

  if (pp.risk_assessment) {
    console.log("Risk level:", pp.risk_assessment.level);
    console.log("Risk score:", pp.risk_assessment.score);
  }
} else {
  console.log("❌ Missing performance_prediction");
}

console.log("\n🔍 6. DATA TYPE VALIDATION");
console.log("-".repeat(40));
console.log(
  "success is boolean:",
  typeof mockSuccessfulResponse.success === "boolean"
);
console.log(
  "analysis_date is string:",
  typeof mockSuccessfulResponse.analysis_date === "string"
);
console.log(
  "optimal_numbers is array:",
  Array.isArray(mockSuccessfulResponse.intelligent_selections?.optimal_numbers)
);
console.log(
  "method_contributions is array:",
  Array.isArray(
    mockSuccessfulResponse.intelligent_selections?.method_contributions
  )
);
console.log(
  "day_1 methods is array:",
  Array.isArray(mockSuccessfulResponse.optimal_methods?.day_1)
);
console.log(
  "expected_hit_rate is number:",
  typeof mockSuccessfulResponse.performance_prediction?.expected_hit_rate ===
    "number"
);

console.log("\n⚠️ 7. POTENTIAL ISSUES TO CHECK IN REAL API");
console.log("-".repeat(40));
console.log("1. Check if success field exists and is boolean");
console.log("2. Verify analysis_date format is YYYY-MM-DD");
console.log("3. Ensure optimal_numbers array has valid number format");
console.log(
  "4. Confirm method arrays (day_1, day_2, day_3) exist and have correct structure"
);
console.log(
  "5. Validate that numeric fields (scores, rates) are actual numbers, not strings"
);
console.log("6. Check for null/undefined values in nested objects");
console.log("7. Verify array lengths > 0 when data is expected");

console.log("\n📝 8. EXPECTED API URL FORMAT");
console.log("-".repeat(40));
console.log(
  "URL: /pre-lokhung/api/method-analysis-v2/?analysis_date=YYYY-MM-DD&limit=15"
);
console.log(
  "Example: /pre-lokhung/api/method-analysis-v2/?analysis_date=2025-01-15&limit=15"
);

console.log("\n✅ 9. FRONTEND COMPATIBILITY CHECK");
console.log("-".repeat(40));
console.log("loadMethodAnalysis function expects:");
console.log("- data.success === true for processing");
console.log("- data.analysis_date for date display");
console.log("- data.hybrid_analysis for hybrid section");
console.log(
  "- data.intelligent_selections.optimal_numbers for live comparison"
);
console.log("- data.optimal_methods with day_1/2/3 arrays for method tables");
console.log("- data.performance_prediction for performance cards");

console.log("\n" + "=".repeat(60));
console.log("✅ ANALYSIS COMPLETE");
console.log("📊 Use this structure to validate your actual API response");
console.log("🔍 Compare real API data with expected structure above");
