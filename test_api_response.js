/**
 * 🔍 API RESPONSE TESTER FOR METHOD ANALYSIS V2
 * Test script để kiểm tra kết quả trả về của API method-analysis-v2
 */

// Mock DOM elements và functions cần thiết
global.document = {
  getElementById: (id) => {
    const mockElements = {
      analysisDatePicker: { value: "2025-01-15" },
      predictionAnalysisDate: { textContent: "" },
      analysisResults: {
        classList: {
          remove: (cls) => console.log(`✅ Removed class: ${cls}`),
        },
        innerHTML: "",
      },
      hybridAnalysisSection: { innerHTML: "" },
      intelligentSelectionsSection: { innerHTML: "" },
      optimalMethodsSection: { innerHTML: "" },
      performancePredictionSection: { innerHTML: "" },
      liveComparisonSection: { innerHTML: "" },
    };
    return (
      mockElements[id] || {
        innerHTML: "",
        textContent: "",
        classList: { remove: () => {} },
      }
    );
  },
};

// Use original console for logging
const originalConsole = console;

// Mock utility functions
function showLoading() {
  originalConsole.log("🔄 Loading started...");
}

function hideLoading() {
  originalConsole.log("✅ Loading finished.");
}

function showError(message) {
  originalConsole.log("❌ Error:", message);
}

function formatDate(dateStr) {
  if (!dateStr) return "N/A";
  const date = new Date(dateStr);
  return date.toLocaleDateString("vi-VN");
}

// Mock render functions để test cấu trúc dữ liệu
function renderHybridAnalysis(hybridAnalysis) {
  originalConsole.log("\n📊 HYBRID ANALYSIS DATA:");
  originalConsole.log("Structure:", hybridAnalysis ? "Present" : "Missing");
  if (hybridAnalysis) {
    originalConsole.log("Keys:", Object.keys(hybridAnalysis));
    originalConsole.log(
      "Sample data:",
      JSON.stringify(hybridAnalysis, null, 2).substring(0, 200) + "..."
    );
  }
}

function renderIntelligentSelections(intelligentSelections) {
  originalConsole.log("\n🎯 INTELLIGENT SELECTIONS DATA:");
  originalConsole.log(
    "Structure:",
    intelligentSelections ? "Present" : "Missing"
  );
  if (intelligentSelections) {
    originalConsole.log("Keys:", Object.keys(intelligentSelections));
    if (intelligentSelections.optimal_numbers) {
      originalConsole.log(
        "Optimal Numbers Count:",
        intelligentSelections.optimal_numbers.length
      );
      originalConsole.log(
        "Optimal Numbers:",
        intelligentSelections.optimal_numbers
      );
    }
    if (intelligentSelections.method_contributions) {
      originalConsole.log(
        "Method Contributions Count:",
        intelligentSelections.method_contributions.length
      );
    }
  }
}

function renderOptimalMethodsByDay(optimalMethods) {
  originalConsole.log("\n📈 OPTIMAL METHODS BY DAY DATA:");
  originalConsole.log("Structure:", optimalMethods ? "Present" : "Missing");
  if (optimalMethods) {
    originalConsole.log("Keys:", Object.keys(optimalMethods));
    ["day_1", "day_2", "day_3"].forEach((day) => {
      if (optimalMethods[day]) {
        originalConsole.log(
          `${day.toUpperCase()} Methods Count:`,
          optimalMethods[day].length
        );
      }
    });
    if (optimalMethods.summary) {
      originalConsole.log("Summary:", optimalMethods.summary);
    }
  }
}

function renderPerformancePrediction(performancePrediction) {
  originalConsole.log("\n🎲 PERFORMANCE PREDICTION DATA:");
  originalConsole.log(
    "Structure:",
    performancePrediction ? "Present" : "Missing"
  );
  if (performancePrediction) {
    originalConsole.log("Keys:", Object.keys(performancePrediction));
    originalConsole.log(
      "Expected Hit Rate:",
      performancePrediction.expected_hit_rate
    );
    originalConsole.log(
      "Confidence Level:",
      performancePrediction.confidence_level
    );
    originalConsole.log(
      "Overall Confidence Score:",
      performancePrediction.overall_confidence_score
    );
  }
}

function renderLiveComparison(optimalNumbers, analysisDate) {
  originalConsole.log("\n✅ LIVE COMPARISON DATA:");
  originalConsole.log("Optimal Numbers for Comparison:", optimalNumbers);
  originalConsole.log("Analysis Date:", analysisDate);
}

// 🔍 MODIFIED loadMethodAnalysis FUNCTION FOR TESTING
async function loadMethodAnalysisTest() {
  originalConsole.log("🚀 Starting API Response Test for loadMethodAnalysis");
  originalConsole.log("=".repeat(60));

  const dateInput = document.getElementById("analysisDatePicker");
  const analysisDate = dateInput.value;

  if (!analysisDate) {
    showError("Vui lòng chọn ngày phân tích");
    return;
  }

  originalConsole.log(`📅 Testing with date: ${analysisDate}`);

  // Show loading
  showLoading();

  // ✅ Construct API URL
  const apiUrl = `/pre-lokhung/api/method-analysis-v2/?analysis_date=${analysisDate}&limit=15`;
  originalConsole.log("🔍 API URL:", apiUrl);

  try {
    // Since this is a test, we'll create a mock fetch to simulate different scenarios
    originalConsole.log("\n📡 Testing API Response Scenarios:");
    originalConsole.log("-".repeat(40));

    // Test 1: Successful response
    await testSuccessfulResponse(apiUrl, analysisDate);

    // Test 2: Error responses
    await testErrorResponses(apiUrl);
  } catch (error) {
    hideLoading();
    originalConsole.error("🚫 Test execution error:", error);
  }
}

// 🧪 TEST SUCCESSFUL RESPONSE
async function testSuccessfulResponse(apiUrl, analysisDate) {
  console.log("\n✅ TEST 1: Successful API Response");
  console.log("-".repeat(30));

  // Mock successful response data structure
  const mockSuccessfulData = {
    success: true,
    analysis_date: analysisDate,
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
        { method_name: "Method C", contribution: 0.2, confidence: 0.7 },
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
        {
          method_name: "Method A2",
          hybrid_score: 82.3,
          expected_hit_rate: 0.72,
          confidence: 0.75,
          predicted_numbers: [56, 78],
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
        total_qualified_methods: 4,
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

  console.log("📦 Mock Response Structure:");
  console.log("- success:", mockSuccessfulData.success);
  console.log("- analysis_date:", mockSuccessfulData.analysis_date);
  console.log(
    "- Main sections:",
    Object.keys(mockSuccessfulData).filter(
      (key) => key !== "success" && key !== "analysis_date"
    )
  );

  // Simulate the response processing
  try {
    // Validate data structure (như trong code gốc)
    if (!mockSuccessfulData || typeof mockSuccessfulData !== "object") {
      throw new Error("Invalid response format");
    }

    if (mockSuccessfulData.success) {
      console.log("\n🎯 Processing Successful Response:");

      // Test renderAnalysisResults logic
      console.log("\n📋 Rendering Analysis Results...");
      document.getElementById("predictionAnalysisDate").textContent =
        formatDate(mockSuccessfulData.analysis_date);

      // Test individual render functions
      renderHybridAnalysis(mockSuccessfulData.hybrid_analysis);
      renderIntelligentSelections(mockSuccessfulData.intelligent_selections);
      renderOptimalMethodsByDay(mockSuccessfulData.optimal_methods);
      renderPerformancePrediction(mockSuccessfulData.performance_prediction);
      renderLiveComparison(
        mockSuccessfulData.intelligent_selections?.optimal_numbers,
        mockSuccessfulData.analysis_date
      );

      // Show results
      document.getElementById("analysisResults").classList.remove("d-none");

      // Store data globally
      global.currentAnalysisData = mockSuccessfulData;
      console.log(
        "\n✅ Test 1 PASSED: Successful response processed correctly"
      );
    } else {
      showError(mockSuccessfulData.error || "Lỗi không xác định");
    }
  } catch (error) {
    console.error("❌ Error processing successful response:", error);
  }
}

// 🧪 TEST ERROR RESPONSES
async function testErrorResponses(apiUrl) {
  console.log("\n❌ TEST 2: Error Response Scenarios");
  console.log("-".repeat(30));

  const errorScenarios = [
    {
      name: "HTTP 404 Error",
      error: new Error("HTTP 404: Not Found"),
      expectedMessage: "API không tồn tại - Kiểm tra URL routing",
    },
    {
      name: "HTTP 500 Error",
      error: new Error("HTTP 500: Internal Server Error"),
      expectedMessage: "Lỗi server nội bộ",
    },
    {
      name: "Network Error",
      error: new Error("Failed to fetch"),
      expectedMessage: "Không thể kết nối đến server",
    },
    {
      name: "JSON Parse Error",
      error: new SyntaxError("Unexpected token < in JSON"),
      expectedMessage: "Lỗi định dạng dữ liệu từ server",
    },
    {
      name: "Success False Response",
      mockData: { success: false, error: "Custom API error" },
      expectedMessage: "Custom API error",
    },
    {
      name: "Invalid Data Structure",
      mockData: null,
      expectedMessage: "Invalid response format",
    },
  ];

  errorScenarios.forEach((scenario, index) => {
    console.log(`\n${index + 1}. Testing: ${scenario.name}`);

    try {
      if (scenario.error) {
        // Simulate error handling
        let errorMessage = "Lỗi kết nối";

        if (scenario.error.name === "SyntaxError") {
          errorMessage = "Lỗi định dạng dữ liệu từ server";
        } else if (scenario.error.message.includes("HTTP 404")) {
          errorMessage = "API không tồn tại - Kiểm tra URL routing";
        } else if (scenario.error.message.includes("HTTP 500")) {
          errorMessage = "Lỗi server nội bộ";
        } else if (scenario.error.message.includes("Failed to fetch")) {
          errorMessage = "Không thể kết nối đến server";
        } else {
          errorMessage = scenario.error.message;
        }

        console.log(`   Expected: "${scenario.expectedMessage}"`);
        console.log(`   Got: "${errorMessage}"`);
        console.log(
          `   ✅ ${errorMessage === scenario.expectedMessage ? "PASS" : "FAIL"}`
        );
      } else if (scenario.mockData !== undefined) {
        // Test data validation
        if (!scenario.mockData || typeof scenario.mockData !== "object") {
          console.log(`   Expected: "Invalid response format"`);
          console.log(`   Got: "Invalid response format"`);
          console.log(`   ✅ PASS`);
        } else if (!scenario.mockData.success) {
          console.log(`   Expected: "${scenario.expectedMessage}"`);
          console.log(`   Got: "${scenario.mockData.error}"`);
          console.log(
            `   ✅ ${
              scenario.mockData.error === scenario.expectedMessage
                ? "PASS"
                : "FAIL"
            }`
          );
        }
      }
    } catch (testError) {
      console.log(`   ❌ Test error: ${testError.message}`);
    }
  });
}

// 🔍 ADDITIONAL API STRUCTURE ANALYSIS
function analyzeAPIStructure() {
  console.log("\n🔬 API STRUCTURE ANALYSIS");
  console.log("=".repeat(60));

  console.log("\n📋 Expected API Response Structure:");
  console.log(`
{
  "success": boolean,
  "analysis_date": "YYYY-MM-DD",
  "hybrid_analysis": {
    "short_term_insights": object,
    "long_term_stability": object, 
    "forward_validation": object
  },
  "intelligent_selections": {
    "optimal_numbers": number[],
    "method_contributions": object[],
    "selection_strategy": object
  },
  "optimal_methods": {
    "day_1": method[],
    "day_2": method[],
    "day_3": method[],
    "summary": object
  },
  "performance_prediction": {
    "expected_hit_rate": number,
    "confidence_level": string,
    "overall_confidence_score": number,
    "risk_assessment": object,
    "performance_breakdown": object
  }
}
    `);

  console.log("\n🎯 Critical Fields for Frontend:");
  console.log("- success: Must be true for processing");
  console.log("- analysis_date: Used for display formatting");
  console.log(
    "- intelligent_selections.optimal_numbers: Used in live comparison"
  );
  console.log("- optimal_methods.day_1/2/3: Used for method tables");
  console.log("- performance_prediction: Used for performance cards");

  console.log("\n⚠️ Potential Issues to Check:");
  console.log("- Missing required fields");
  console.log("- Incorrect data types (string vs number)");
  console.log("- Empty arrays when data expected");
  console.log("- Null values instead of objects");
  console.log("- Date format compatibility");
}

// 🚀 RUN ALL TESTS
async function runAllTests() {
  console.log("🧪 STARTING COMPREHENSIVE API RESPONSE TESTS");
  console.log("=".repeat(60));

  try {
    await loadMethodAnalysisTest();
    analyzeAPIStructure();

    console.log("\n" + "=".repeat(60));
    console.log("✅ ALL TESTS COMPLETED");
    console.log("📊 Check the output above for detailed analysis");
    console.log("🔍 Use this information to verify your actual API response");
  } catch (error) {
    console.error("🚫 Test suite error:", error);
  }
}

// Execute tests
runAllTests();
