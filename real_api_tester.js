/**
 * 🔍 REAL API TESTER FOR METHOD ANALYSIS V2
 * Test thực tế API endpoint với fetch request
 */

// Tạo một function để test API thực tế
async function testRealAPI() {
  console.log("🚀 TESTING REAL API ENDPOINT");
  console.log("=".repeat(60));

  // Cấu hình test
  const baseUrl = "http://localhost:8000"; // Thay đổi port nếu cần
  const testDate = "2025-01-15";
  const apiUrl = `${baseUrl}/pre-lokhung/api/method-analysis-v2/?analysis_date=${testDate}&limit=15`;

  console.log(`📅 Test date: ${testDate}`);
  console.log(`🔗 API URL: ${apiUrl}`);
  console.log("-".repeat(60));

  try {
    console.log("📡 Making API request...");

    const response = await fetch(apiUrl, {
      method: "GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    });

    console.log(
      `📊 Response Status: ${response.status} ${response.statusText}`
    );
    console.log(`📊 Response URL: ${response.url}`);

    // Check content type
    const contentType = response.headers.get("content-type");
    console.log(`📊 Content-Type: ${contentType}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    if (!contentType || !contentType.includes("application/json")) {
      console.log("⚠️ Warning: Response is not JSON format");
      const textResponse = await response.text();
      console.log("📄 Response body (first 500 chars):");
      console.log(textResponse.substring(0, 500));
      return;
    }

    const data = await response.json();

    console.log("\n✅ API Response received successfully!");
    console.log("=".repeat(60));

    // Analyze response structure
    analyzeAPIResponse(data);
  } catch (error) {
    console.log("\n❌ API REQUEST FAILED");
    console.log("=".repeat(60));
    console.log("Error type:", error.name);
    console.log("Error message:", error.message);

    if (error.message.includes("fetch")) {
      console.log("\n🔧 TROUBLESHOOTING SUGGESTIONS:");
      console.log("1. Check if Django server is running");
      console.log("2. Verify the correct port (usually 8000)");
      console.log("3. Check if the URL pattern is correct in Django urls.py");
      console.log("4. Ensure CORS is configured if testing from browser");
    } else if (error.message.includes("404")) {
      console.log("\n🔧 404 ERROR SUGGESTIONS:");
      console.log("1. Check Django URL patterns in urls.py");
      console.log("2. Verify the API endpoint exists");
      console.log("3. Check if the app is properly registered");
    } else if (error.message.includes("500")) {
      console.log("\n🔧 500 ERROR SUGGESTIONS:");
      console.log("1. Check Django server logs for detailed error");
      console.log("2. Verify database connection");
      console.log("3. Check if required data exists for the test date");
    }
  }
}

function analyzeAPIResponse(data) {
  console.log("🔍 ANALYZING API RESPONSE STRUCTURE");
  console.log("-".repeat(60));

  // 1. Basic structure check
  console.log("📋 1. BASIC STRUCTURE:");
  console.log(`   success: ${data.success} (${typeof data.success})`);
  console.log(
    `   analysis_date: ${data.analysis_date} (${typeof data.analysis_date})`
  );

  // 2. Main sections check
  console.log("\n📊 2. MAIN SECTIONS:");
  const expectedSections = [
    "hybrid_analysis",
    "intelligent_selections",
    "optimal_methods",
    "performance_prediction",
  ];
  expectedSections.forEach((section) => {
    const exists = data.hasOwnProperty(section);
    const type = exists ? typeof data[section] : "missing";
    console.log(`   ${section}: ${exists ? "✅" : "❌"} (${type})`);
  });

  // 3. Detailed analysis of each section
  if (data.success) {
    console.log("\n✅ SUCCESS RESPONSE - Analyzing details...");

    // Hybrid Analysis
    if (data.hybrid_analysis) {
      console.log("\n🔬 HYBRID ANALYSIS:");
      console.log("   Keys:", Object.keys(data.hybrid_analysis));
      console.log(
        "   Structure:",
        JSON.stringify(data.hybrid_analysis, null, 2).substring(0, 300) + "..."
      );
    }

    // Intelligent Selections
    if (data.intelligent_selections) {
      console.log("\n🎯 INTELLIGENT SELECTIONS:");
      const is = data.intelligent_selections;
      console.log("   Keys:", Object.keys(is));
      if (is.optimal_numbers) {
        console.log(`   optimal_numbers: ${is.optimal_numbers.length} items`);
        console.log(`   numbers: [${is.optimal_numbers.join(", ")}]`);
      }
      if (is.method_contributions) {
        console.log(
          `   method_contributions: ${is.method_contributions.length} items`
        );
      }
    }

    // Optimal Methods
    if (data.optimal_methods) {
      console.log("\n📈 OPTIMAL METHODS BY DAY:");
      const om = data.optimal_methods;
      console.log("   Keys:", Object.keys(om));
      ["day_1", "day_2", "day_3"].forEach((day) => {
        if (om[day]) {
          console.log(`   ${day}: ${om[day].length} methods`);
          if (om[day].length > 0) {
            const method = om[day][0];
            console.log(
              `     Sample: ${method.method_name} (score: ${method.hybrid_score})`
            );
          }
        }
      });
      if (om.summary) {
        console.log("   Summary:", om.summary);
      }
    }

    // Performance Prediction
    if (data.performance_prediction) {
      console.log("\n🎲 PERFORMANCE PREDICTION:");
      const pp = data.performance_prediction;
      console.log("   Keys:", Object.keys(pp));
      console.log(`   expected_hit_rate: ${pp.expected_hit_rate}`);
      console.log(`   confidence_level: ${pp.confidence_level}`);
      console.log(
        `   overall_confidence_score: ${pp.overall_confidence_score}`
      );
    }
  } else {
    console.log("\n❌ ERROR RESPONSE:");
    console.log("   Error message:", data.error || "No error message provided");
  }

  // 4. Data type validation
  console.log("\n🔍 DATA TYPE VALIDATION:");
  console.log(`   success is boolean: ${typeof data.success === "boolean"}`);
  console.log(
    `   analysis_date is string: ${typeof data.analysis_date === "string"}`
  );

  if (data.intelligent_selections?.optimal_numbers) {
    console.log(
      `   optimal_numbers is array: ${Array.isArray(
        data.intelligent_selections.optimal_numbers
      )}`
    );
    console.log(
      `   optimal_numbers contains numbers: ${data.intelligent_selections.optimal_numbers.every(
        (n) => typeof n === "number"
      )}`
    );
  }

  // 5. Frontend compatibility check
  console.log("\n✅ FRONTEND COMPATIBILITY:");
  const compatibilityChecks = [
    { check: "data.success exists", result: data.hasOwnProperty("success") },
    { check: "data.success is true", result: data.success === true },
    {
      check: "data.analysis_date exists",
      result: data.hasOwnProperty("analysis_date"),
    },
    { check: "hybrid_analysis section exists", result: !!data.hybrid_analysis },
    {
      check: "intelligent_selections exists",
      result: !!data.intelligent_selections,
    },
    {
      check: "optimal_numbers array exists",
      result: Array.isArray(data.intelligent_selections?.optimal_numbers),
    },
    { check: "optimal_methods exists", result: !!data.optimal_methods },
    {
      check: "day_1 methods exist",
      result: Array.isArray(data.optimal_methods?.day_1),
    },
    {
      check: "performance_prediction exists",
      result: !!data.performance_prediction,
    },
  ];

  compatibilityChecks.forEach(({ check, result }) => {
    console.log(`   ${check}: ${result ? "✅" : "❌"}`);
  });

  console.log("\n" + "=".repeat(60));
  console.log("📊 ANALYSIS COMPLETE");

  if (data.success) {
    console.log(
      "✅ API response structure looks good for frontend integration!"
    );
  } else {
    console.log("❌ API returned error - check server logs for details");
  }
}

// Alternative test function for different dates
async function testMultipleDates() {
  console.log("\n🗓️ TESTING MULTIPLE DATES");
  console.log("=".repeat(60));

  const testDates = ["2025-01-15", "2025-01-14", "2025-01-13"];

  for (const date of testDates) {
    console.log(`\n📅 Testing date: ${date}`);
    console.log("-".repeat(30));

    try {
      const apiUrl = `http://localhost:8000/pre-lokhung/api/method-analysis-v2/?analysis_date=${date}&limit=15`;
      const response = await fetch(apiUrl);

      console.log(`Status: ${response.status}`);

      if (response.ok) {
        const data = await response.json();
        console.log(`Success: ${data.success}`);
        if (data.success) {
          console.log(
            `Optimal numbers count: ${
              data.intelligent_selections?.optimal_numbers?.length || 0
            }`
          );
          console.log(
            `Methods count: Day1=${
              data.optimal_methods?.day_1?.length || 0
            }, Day2=${data.optimal_methods?.day_2?.length || 0}, Day3=${
              data.optimal_methods?.day_3?.length || 0
            }`
          );
        } else {
          console.log(`Error: ${data.error}`);
        }
      } else {
        console.log(`HTTP Error: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.log(`Request failed: ${error.message}`);
    }

    // Delay between requests
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
}

// Check if running in Node.js environment
if (typeof require !== "undefined" && typeof module !== "undefined") {
  // Node.js environment - need to install node-fetch
  console.log("⚠️ Running in Node.js environment");
  console.log("📦 You need to install node-fetch: npm install node-fetch");
  console.log("💡 Or run this script in a browser console instead");

  // Try to use node-fetch if available
  try {
    const fetch = require("node-fetch");
    global.fetch = fetch;

    // Run the test
    testRealAPI()
      .then(() => {
        console.log("\n🔄 Testing multiple dates...");
        return testMultipleDates();
      })
      .catch((error) => {
        console.error("Test failed:", error);
      });
  } catch (error) {
    console.log(
      "❌ node-fetch not available. Please install it or run in browser."
    );
    console.log("\n🌐 TO RUN IN BROWSER:");
    console.log("1. Open browser developer tools (F12)");
    console.log("2. Go to Console tab");
    console.log("3. Paste this script and run it");
    console.log("4. Make sure your Django server is running");
  }
} else {
  // Browser environment
  console.log("🌐 Running in browser environment - starting test...");
  testRealAPI().then(() => {
    return testMultipleDates();
  });
}
