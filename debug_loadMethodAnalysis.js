/**
 * 🔍 DEBUG HELPER FOR loadMethodAnalysis
 * Script để debug và kiểm tra response của API method-analysis-v2
 */

console.log("🔧 DEBUG HELPER FOR loadMethodAnalysis");
console.log("=".repeat(60));

console.log(`
📋 INSTRUCTIONS:
1. Copy the code below and paste it in your browser console
2. Make sure you're on the page with loadMethodAnalysis function
3. Run the debug functions to inspect API responses

🌐 BROWSER CONSOLE CODE:
`);

console.log(`
// ===== PASTE THIS IN BROWSER CONSOLE =====

// 1. Override console.log to capture API debug info
const originalConsoleLog = console.log;
const apiLogs = [];

console.log = function(...args) {
    // Capture API-related logs
    const message = args.join(' ');
    if (message.includes('🔍 Calling API:') || 
        message.includes('📡 Response') || 
        message.includes('📋 Received') ||
        message.includes('🎯 Actual numbers') ||
        message.includes('✅ Comparison results')) {
        apiLogs.push({ timestamp: new Date().toISOString(), message: message });
    }
    originalConsoleLog.apply(console, args);
};

// 2. Function to analyze API response structure
function debugAPIResponse() {
    console.log('🔍 Starting API Response Debug...');
    
    // Mock date input
    const dateInput = document.getElementById('analysisDatePicker');
    if (!dateInput) {
        console.log('❌ analysisDatePicker element not found');
        return;
    }
    
    // Set a test date if empty
    if (!dateInput.value) {
        dateInput.value = '2025-01-15';
        console.log('📅 Set test date: 2025-01-15');
    }
    
    console.log('📅 Using date:', dateInput.value);
    
    // Clear previous logs
    apiLogs.length = 0;
    
    // Call the actual function
    loadMethodAnalysis();
    
    // Wait a bit then analyze logs
    setTimeout(() => {
        console.log('\\n📊 API LOGS CAPTURED:');
        console.log('='.repeat(40));
        apiLogs.forEach((log, index) => {
            console.log(\`\${index + 1}. [\${log.timestamp.substr(11, 8)}] \${log.message}\`);
        });
        
        // Check global data
        if (window.currentAnalysisData) {
            console.log('\\n📦 GLOBAL DATA CAPTURED:');
            console.log('='.repeat(40));
            analyzeResponseStructure(window.currentAnalysisData);
        } else {
            console.log('\\n❌ No global data captured - check if API call succeeded');
        }
    }, 3000);
}

// 3. Function to analyze response structure
function analyzeResponseStructure(data) {
    console.log('🔍 RESPONSE STRUCTURE ANALYSIS:');
    console.log('-'.repeat(40));
    
    if (!data) {
        console.log('❌ No data to analyze');
        return;
    }
    
    console.log('✅ Data received, analyzing structure...');
    
    // Basic structure
    console.log('\\n📋 BASIC STRUCTURE:');
    console.log('- success:', data.success, typeof data.success);
    console.log('- analysis_date:', data.analysis_date, typeof data.analysis_date);
    console.log('- Keys:', Object.keys(data));
    
    // Detailed analysis
    if (data.success) {
        console.log('\\n✅ SUCCESS RESPONSE DETAILS:');
        
        // Hybrid Analysis
        if (data.hybrid_analysis) {
            console.log('\\n🔬 hybrid_analysis:');
            console.log('  Keys:', Object.keys(data.hybrid_analysis));
            console.log('  Type:', typeof data.hybrid_analysis);
        } else {
            console.log('\\n❌ hybrid_analysis: MISSING');
        }
        
        // Intelligent Selections
        if (data.intelligent_selections) {
            console.log('\\n🎯 intelligent_selections:');
            const is = data.intelligent_selections;
            console.log('  Keys:', Object.keys(is));
            if (is.optimal_numbers) {
                console.log('  optimal_numbers:', is.optimal_numbers);
                console.log('  optimal_numbers count:', is.optimal_numbers.length);
                console.log('  optimal_numbers type:', typeof is.optimal_numbers);
                console.log('  all numbers?', is.optimal_numbers.every(n => typeof n === 'number'));
            }
            if (is.method_contributions) {
                console.log('  method_contributions count:', is.method_contributions.length);
            }
        } else {
            console.log('\\n❌ intelligent_selections: MISSING');
        }
        
        // Optimal Methods
        if (data.optimal_methods) {
            console.log('\\n📈 optimal_methods:');
            const om = data.optimal_methods;
            console.log('  Keys:', Object.keys(om));
            ['day_1', 'day_2', 'day_3'].forEach(day => {
                if (om[day]) {
                    console.log(\`  \${day}: \${om[day].length} methods\`);
                    if (om[day].length > 0) {
                        console.log(\`    Sample method keys: \${Object.keys(om[day][0])}\`);
                    }
                } else {
                    console.log(\`  \${day}: MISSING\`);
                }
            });
            if (om.summary) {
                console.log('  summary:', om.summary);
            }
        } else {
            console.log('\\n❌ optimal_methods: MISSING');
        }
        
        // Performance Prediction
        if (data.performance_prediction) {
            console.log('\\n🎲 performance_prediction:');
            const pp = data.performance_prediction;
            console.log('  Keys:', Object.keys(pp));
            console.log('  expected_hit_rate:', pp.expected_hit_rate, typeof pp.expected_hit_rate);
            console.log('  confidence_level:', pp.confidence_level, typeof pp.confidence_level);
        } else {
            console.log('\\n❌ performance_prediction: MISSING');
        }
        
    } else {
        console.log('\\n❌ ERROR RESPONSE:');
        console.log('- Error:', data.error || 'No error message');
    }
    
    // Frontend compatibility check
    console.log('\\n✅ FRONTEND COMPATIBILITY CHECK:');
    const checks = [
        ['data.success === true', data.success === true],
        ['data.analysis_date exists', !!data.analysis_date],
        ['data.hybrid_analysis exists', !!data.hybrid_analysis],
        ['data.intelligent_selections exists', !!data.intelligent_selections],
        ['optimal_numbers is array', Array.isArray(data.intelligent_selections?.optimal_numbers)],
        ['optimal_methods exists', !!data.optimal_methods],
        ['day_1 methods exist', Array.isArray(data.optimal_methods?.day_1)],
        ['performance_prediction exists', !!data.performance_prediction]
    ];
    
    checks.forEach(([check, result]) => {
        console.log(\`\${result ? '✅' : '❌'} \${check}\`);
    });
}

// 4. Function to test error scenarios
function testErrorScenarios() {
    console.log('\\n🧪 TESTING ERROR SCENARIOS:');
    console.log('='.repeat(40));
    
    // Test với ngày không hợp lệ
    const dateInput = document.getElementById('analysisDatePicker');
    if (dateInput) {
        const originalValue = dateInput.value;
        
        // Test empty date
        dateInput.value = '';
        console.log('\\n1. Testing empty date...');
        setTimeout(() => loadMethodAnalysis(), 100);
        
        // Test invalid date
        setTimeout(() => {
            dateInput.value = '2025-13-45';
            console.log('\\n2. Testing invalid date...');
            loadMethodAnalysis();
        }, 1000);
        
        // Test future date
        setTimeout(() => {
            dateInput.value = '2030-01-01';
            console.log('\\n3. Testing future date...');
            loadMethodAnalysis();
        }, 2000);
        
        // Restore original value
        setTimeout(() => {
            dateInput.value = originalValue;
        }, 3000);
    }
}

// 5. Function to check DOM elements
function checkDOMElements() {
    console.log('\\n🔍 CHECKING DOM ELEMENTS:');
    console.log('='.repeat(40));
    
    const elements = [
        'analysisDatePicker',
        'predictionAnalysisDate', 
        'analysisResults',
        'hybridAnalysisSection',
        'intelligentSelectionsSection',
        'optimalMethodsSection',
        'performancePredictionSection',
        'liveComparisonSection'
    ];
    
    elements.forEach(id => {
        const element = document.getElementById(id);
        console.log(\`\${element ? '✅' : '❌'} \${id}: \${element ? 'Found' : 'NOT FOUND'}\`);
    });
}

// 6. Main debug function
function runFullDebug() {
    console.log('🚀 RUNNING FULL DEBUG SUITE');
    console.log('='.repeat(60));
    
    checkDOMElements();
    debugAPIResponse();
    
    setTimeout(() => {
        testErrorScenarios();
    }, 5000);
}

// Instructions
console.log('\\n📋 AVAILABLE DEBUG FUNCTIONS:');
console.log('- runFullDebug(): Run complete debug suite');
console.log('- debugAPIResponse(): Test API response with current date');
console.log('- checkDOMElements(): Check if required DOM elements exist');
console.log('- testErrorScenarios(): Test various error conditions');
console.log('- analyzeResponseStructure(data): Analyze specific response data');

console.log('\\n🚀 Quick start: Run runFullDebug()');

// ===== END OF BROWSER CONSOLE CODE =====
`);

console.log(`
📋 ADDITIONAL DEBUGGING TIPS:

1. 🔍 Manual API Testing:
   - Open browser Network tab (F12 > Network)
   - Call loadMethodAnalysis()
   - Check the API call in Network tab
   - Look at Response data

2. 🧪 Response Validation:
   - Check if response.ok is true
   - Verify Content-Type is application/json
   - Look for success field in response

3. ⚠️ Common Issues:
   - API endpoint returns HTML instead of JSON (404/500 error page)
   - CORS issues (if testing from different domain)  
   - Missing data for the selected date
   - Incorrect date format

4. 📊 Data Structure Issues:
   - Check if arrays are actually arrays (not null/undefined)
   - Verify numeric fields are numbers, not strings
   - Look for missing required fields

5. 🎯 Frontend Integration Issues:
   - DOM elements not found
   - Render functions not updating display
   - JavaScript errors preventing execution

🔗 NEXT STEPS:
1. Run the browser console code above
2. Check the detailed output
3. Compare actual vs expected response structure
4. Fix any issues found in the API or frontend code
`);

console.log("\n" + "=".repeat(60));
console.log("✅ DEBUG HELPER READY");
console.log("📋 Copy the browser console code above and run it on your page");
