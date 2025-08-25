// Test to see full analysis data structure
console.log("=== Testing Full Analysis Data ===");

// Test with a specific number to see full data structure
window.testFullAnalysis = function(number) {
    console.log("Testing full analysis for number:", number);
    
    fetch(`/results/number-analysis/?number=${number}`)
        .then(response => response.json())
        .then(data => {
            console.log("📊 Full API Response:", data);
            
            if (data.success && data.analysis) {
                const analysis = data.analysis;
                
                console.log("🔍 Analysis sections available:");
                console.log("- Basic stats:", !!analysis.basic_stats);
                console.log("- Gan analysis:", !!analysis.gan_analysis);
                console.log("- Cycle analysis:", !!analysis.cycle_analysis);
                console.log("- Weekday patterns:", !!analysis.weekday_patterns);
                console.log("- Companion numbers:", !!analysis.companion_numbers, "count:", analysis.companion_numbers?.length || 0);
                console.log("- Consecutive analysis:", !!analysis.consecutive_analysis);
                console.log("- Predecessor analysis:", !!analysis.predecessor_analysis, "count:", analysis.predecessor_analysis?.length || 0);
                console.log("- Prediction probabilities:", !!analysis.prediction_probabilities);
                
                // Show companion numbers detail
                if (analysis.companion_numbers && analysis.companion_numbers.length > 0) {
                    console.log("🤝 Top companion numbers:");
                    analysis.companion_numbers.slice(0, 5).forEach(comp => {
                        console.log(`   ${comp.number}: ${comp.co_occurrences} times (${comp.percentage}%)`);
                    });
                }
                
                // Show predecessor analysis detail
                if (analysis.predecessor_analysis && analysis.predecessor_analysis.length > 0) {
                    console.log("⏮️ Top predecessor numbers:");
                    analysis.predecessor_analysis.slice(0, 5).forEach(pred => {
                        console.log(`   ${pred.number}: ${pred.occurrences} times (${pred.percentage}%)`);
                    });
                }
                
                // Show weekday patterns
                if (analysis.weekday_patterns) {
                    console.log("📅 Weekday patterns:");
                    Object.entries(analysis.weekday_patterns).forEach(([day, stats]) => {
                        console.log(`   ${day}: ${stats.count} times (${stats.percentage}%)`);
                    });
                }
            }
        })
        .catch(error => {
            console.error("❌ Error fetching analysis:", error);
        });
};

// Test with number 00
console.log("🧪 Testing with number 00...");
window.testFullAnalysis('00');
