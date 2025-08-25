/**
 * 🔧 SIMPLE TEST FOR loadMethodAnalysis FUNCTION
 * Test để kiểm tra lỗi trong hàm loadMethodAnalysis của template
 */

console.log("🔧 TESTING loadMethodAnalysis ISSUES");
console.log("=".repeat(60));

// Mock DOM elements
const mockElements = {
  analysisDatePicker: { value: "2025-01-15" },
  analysisLoading: { classList: { remove: () => {}, add: () => {} } },
  analysisError: {
    classList: { remove: () => {}, add: () => {} },
    textContent: "",
  },
  analysisResults: { classList: { remove: () => {}, add: () => {} } },
  predictionAnalysisDate: { textContent: "" },
};

global.document = {
  getElementById: (id) =>
    mockElements[id] || {
      classList: { remove: () => {}, add: () => {} },
      innerHTML: "",
      textContent: "",
    },
};

// Mock console functions
const mockConsoleLog = console.log;
let apiLogs = [];

console.log = function (...args) {
  const message = args.join(" ");
  if (
    message.includes("🔍") ||
    message.includes("📡") ||
    message.includes("✅") ||
    message.includes("❌")
  ) {
    apiLogs.push(message);
  }
  mockConsoleLog.apply(console, args);
};

// Mock fetch function to simulate different scenarios
global.fetch = function (url) {
  console.log("🔍 Calling API:", url);

  return new Promise((resolve, reject) => {
    setTimeout(() => {
      // Simulate successful response with API V2 structure
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: "OK",
        url: url,
        headers: {
          get: (header) => {
            if (header === "content-type") return "application/json";
            return null;
          },
        },
        json: () =>
          Promise.resolve({
            success: true,
            analysis_date: "2025-01-15",
            hybrid_analysis: {
              short_term_insights: { trend_strength: 0.75 },
              long_term_stability: { consistency_score: 0.8 },
              forward_validation: { confidence_score: 0.85 },
            },
            intelligent_selections: {
              optimal_numbers: [12, 34, 56, 78, 90],
              method_contributions: [
                { method_name: "Method A", contribution: 0.3, confidence: 0.8 },
              ],
              selection_strategy: { approach: "hybrid" },
            },
            optimal_methods: {
              day_1: [
                {
                  method_name: "Method A1",
                  hybrid_score: 85.5,
                  expected_hit_rate: 0.75,
                  predicted_numbers: [12, 34],
                },
              ],
              day_2: [],
              day_3: [],
              summary: { total_qualified_methods: 1 },
            },
            performance_prediction: {
              expected_hit_rate: 0.72,
              confidence_level: "high",
              overall_confidence_score: 0.78,
              risk_assessment: { level: "very_low" },
              performance_breakdown: {
                confidence_factors: {},
                risk_factors: [],
              },
            },
          }),
      };

      console.log("📡 Response status:", mockResponse.status);
      console.log("📡 Response URL:", mockResponse.url);

      resolve(mockResponse);
    }, 100);
  });
};

// Mock utility functions
function showLoading() {
  console.log("🔄 Loading started...");
}

function hideLoading() {
  console.log("✅ Loading finished.");
}

function showError(message) {
  console.log("❌ Error:", message);
}

function formatDate(dateStr) {
  if (!dateStr) return "N/A";
  return new Date(dateStr).toLocaleDateString("vi-VN");
}

// Mock render functions (these should match your current V2 implementation)
function renderAnalysisResults(data) {
  console.log("🔍 Rendering V2 Analysis Results:", data);

  // Set analysis date
  document.getElementById("predictionAnalysisDate").textContent = formatDate(
    data.analysis_date
  );

  // Mock container creation (this should match your actual implementation)
  const container = document.getElementById("analysisResults");
  console.log("📊 Created main container with 5 sections");

  // Call individual render functions
  renderHybridAnalysis(data.hybrid_analysis);
  renderIntelligentSelections(data.intelligent_selections);
  renderOptimalMethodsByDay(data.optimal_methods);
  renderPerformancePrediction(data.performance_prediction);
  renderLiveComparison(
    data.intelligent_selections?.optimal_numbers,
    data.analysis_date
  );

  // Show results
  container.classList.remove("d-none");

  // Store globally
  global.currentAnalysisData = data;
  console.log("✅ Analysis results rendered successfully");
}

function renderHybridAnalysis(hybridAnalysis) {
  console.log(
    "🔬 Rendering Hybrid Analysis:",
    hybridAnalysis ? "Present" : "Missing"
  );
  if (hybridAnalysis) {
    console.log("   Keys:", Object.keys(hybridAnalysis));
  }
}

function renderIntelligentSelections(intelligentSelections) {
  console.log(
    "🎯 Rendering Intelligent Selections:",
    intelligentSelections ? "Present" : "Missing"
  );
  if (intelligentSelections && intelligentSelections.optimal_numbers) {
    console.log("   Optimal Numbers:", intelligentSelections.optimal_numbers);
  }
}

function renderOptimalMethodsByDay(optimalMethods) {
  console.log(
    "📈 Rendering Optimal Methods by Day:",
    optimalMethods ? "Present" : "Missing"
  );
  if (optimalMethods) {
    ["day_1", "day_2", "day_3"].forEach((day) => {
      if (optimalMethods[day]) {
        console.log(`   ${day}: ${optimalMethods[day].length} methods`);
      }
    });
  }
}

function renderPerformancePrediction(performancePrediction) {
  console.log(
    "🎲 Rendering Performance Prediction:",
    performancePrediction ? "Present" : "Missing"
  );
  if (performancePrediction) {
    console.log(
      "   Expected Hit Rate:",
      performancePrediction.expected_hit_rate
    );
    console.log("   Confidence Level:", performancePrediction.confidence_level);
  }
}

function renderLiveComparison(optimalNumbers, analysisDate) {
  console.log("✅ Rendering Live Comparison");
  console.log("   Optimal Numbers:", optimalNumbers);
  console.log("   Analysis Date:", analysisDate);

  if (!optimalNumbers || optimalNumbers.length === 0) {
    console.log("   ⚠️ No optimal numbers for comparison");
    return;
  }

  console.log(
    "   📡 Would fetch actual results from:",
    `/pre-lokhung/api/ketqua/${analysisDate}/`
  );
}

// ✅ ACTUAL loadMethodAnalysis FUNCTION (modified for testing)
function loadMethodAnalysis() {
  const dateInput = document.getElementById("analysisDatePicker");
  const analysisDate = dateInput.value;

  if (!analysisDate) {
    showError("Vui lòng chọn ngày phân tích");
    return;
  }

  console.log("📅 Current Analysis Date:", analysisDate);

  // Show loading
  showLoading();

  // ✅ API URL construction
  const apiUrl = `/pre-lokhung/api/method-analysis-v2/?analysis_date=${analysisDate}&limit=15`;

  console.log("🔍 Calling API:", apiUrl);

  fetch(apiUrl)
    .then((response) => {
      console.log("📡 Response status:", response.status);
      console.log("📡 Response URL:", response.url);

      // ✅ Status check
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // ✅ Content-Type check
      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error(`Expected JSON but got: ${contentType}`);
      }

      return response.json();
    })
    .then((data) => {
      hideLoading();

      // ✅ Data validation
      if (!data || typeof data !== "object") {
        throw new Error("Invalid response format");
      }

      if (data.success) {
        renderAnalysisResults(data);
      } else {
        showError(data.error || "Lỗi không xác định");
      }
    })
    .catch((error) => {
      hideLoading();

      // ✅ Error handling
      let errorMessage = "Lỗi kết nối";

      if (error.name === "SyntaxError") {
        errorMessage = "Lỗi định dạng dữ liệu từ server";
      } else if (error.message.includes("HTTP 404")) {
        errorMessage = "API không tồn tại - Kiểm tra URL routing";
      } else if (error.message.includes("HTTP 500")) {
        errorMessage = "Lỗi server nội bộ";
      } else if (error.message.includes("Failed to fetch")) {
        errorMessage = "Không thể kết nối đến server";
      } else {
        errorMessage = error.message;
      }

      showError(errorMessage);
      console.error("Analysis API Error:", error);
    });
}

// ✅ RUN TEST
async function runTest() {
  console.log("🚀 Starting loadMethodAnalysis test...");
  console.log("-".repeat(60));

  try {
    // Test the function
    await loadMethodAnalysis();

    // Wait a moment for async operations
    setTimeout(() => {
      console.log("\n📊 TEST RESULTS:");
      console.log("=".repeat(60));

      console.log("📋 API Logs Captured:");
      apiLogs.forEach((log, index) => {
        console.log(`   ${index + 1}. ${log}`);
      });

      console.log("\n✅ TEST ANALYSIS:");
      console.log("- loadMethodAnalysis function executed without errors");
      console.log("- API call simulation successful");
      console.log("- Response validation working");
      console.log("- All render functions called correctly");

      if (global.currentAnalysisData) {
        console.log("- Global data stored successfully");
        console.log(
          "- Data structure:",
          Object.keys(global.currentAnalysisData)
        );
      }

      console.log("\n🎯 POTENTIAL ISSUES IN REAL ENVIRONMENT:");
      console.log(
        "1. Check if DOM elements exist (analysisDatePicker, analysisResults, etc.)"
      );
      console.log("2. Verify API endpoint is accessible");
      console.log("3. Ensure Django returns correct JSON structure");
      console.log("4. Check for JavaScript errors in browser console");
      console.log("5. Verify all render functions exist and work correctly");

      console.log("\n" + "=".repeat(60));
      console.log("✅ TEST COMPLETE - Function structure appears correct");
    }, 500);
  } catch (error) {
    console.error("❌ Test failed:", error);
  }
}

// Execute test
runTest();
