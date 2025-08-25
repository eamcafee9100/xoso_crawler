// Test prediction probabilities in comprehensive analysis
console.log("=== Testing Prediction Probabilities ===");

// Check if comprehensive analysis data exists
if (typeof window.comprehensiveAnalysisData !== 'undefined') {
    console.log("✅ Global comprehensive data found");
    console.log("Data keys:", Object.keys(window.comprehensiveAnalysisData));
} else {
    console.log("❌ No global comprehensive data");
}

// Check DOM for comprehensive analysis data
const comprehensiveSection = document.getElementById('comprehensive');
if (comprehensiveSection) {
    console.log("✅ Comprehensive section found");
    
    // Look for probability data in grid cells
    const cells = comprehensiveSection.querySelectorAll('.frequency-cell[data-number]');
    console.log("📊 Found", cells.length, "cells with data-number");
    
    if (cells.length > 0) {
        console.log("🔍 Sample cell data:");
        const sampleCell = cells[0];
        console.log("- Number:", sampleCell.dataset.number);
        console.log("- Title:", sampleCell.title);
        console.log("- Classes:", sampleCell.className);
        
        // Extract probability from title if available
        const titleMatch = sampleCell.title.match(/Xác suất (\d+\.?\d*)%/);
        if (titleMatch) {
            console.log("- Probability found:", titleMatch[1] + "%");
        }
    }
    
    // Try to extract all probabilities
    const probabilities = [];
    cells.forEach(cell => {
        const number = cell.dataset.number;
        const titleMatch = cell.title.match(/Xác suất (\d+\.?\d*)%/);
        if (titleMatch) {
            probabilities.push({
                number: number,
                probability: parseFloat(titleMatch[1]),
                ganDays: parseInt(cell.title.match(/Gan (\d+) ngày/)?.[1] || 0)
            });
        }
    });
    
    if (probabilities.length > 0) {
        console.log("📈 Found", probabilities.length, "numbers with probabilities");
        
        // Sort by probability descending
        probabilities.sort((a, b) => b.probability - a.probability);
        
        console.log("🏆 Top 10 highest probabilities:");
        probabilities.slice(0, 10).forEach((item, index) => {
            console.log(`${index + 1}. Số ${item.number}: ${item.probability}% (gan ${item.ganDays} ngày)`);
        });
        
        // Store in global variable for use
        window.extractedProbabilities = probabilities;
        console.log("✅ Probabilities stored in window.extractedProbabilities");
    } else {
        console.log("❌ No probabilities found in cell titles");
    }
} else {
    console.log("❌ Comprehensive section not found");
}

console.log("=== Test Complete ===");
