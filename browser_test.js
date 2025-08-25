// Test script for browser console
// Copy và paste vào Browser Console (F12) để test

console.log("=== Testing Frequency Analysis Grid ===");

// 1. Check if we're on the comprehensive tab
const comprehensiveTab = document.getElementById('comprehensive');
if (comprehensiveTab) {
    console.log("✅ Comprehensive tab found");
    
    // Check if tab is active
    const isActive = comprehensiveTab.classList.contains('active') || comprehensiveTab.classList.contains('show');
    console.log("Tab active:", isActive);
} else {
    console.log("❌ Comprehensive tab NOT found");
}

// 2. Check for frequency grid
const frequencyGrid = document.querySelector('.frequency-grid');
if (frequencyGrid) {
    console.log("✅ Frequency grid found");
    console.log("Grid children count:", frequencyGrid.children.length);
} else {
    console.log("❌ Frequency grid NOT found");
}

// 3. Check for analysis buttons
const analysisButtons = document.querySelectorAll('.number-analysis-btn');
console.log("Number analysis buttons found:", analysisButtons.length);

// 4. Check first few buttons
if (analysisButtons.length > 0) {
    console.log("✅ Analysis buttons exist");
    console.log("First button data-number:", analysisButtons[0].dataset.number);
    console.log("First button text:", analysisButtons[0].textContent.trim());
    
    // Test click on first button
    console.log("Testing click on first button...");
    analysisButtons[0].click();
} else {
    console.log("❌ No analysis buttons found");
}

// 5. Check for comprehensive analysis data in page
const pageContent = document.documentElement.innerHTML;
const hasComprehensiveData = pageContent.includes('comprehensive_analysis');
console.log("Page has comprehensive_analysis data:", hasComprehensiveData);

// 6. Check for debug info
const debugInfo = document.querySelector('small.text-muted');
if (debugInfo && debugInfo.textContent.includes('Số phần tử phân tích')) {
    console.log("✅ Debug info found:", debugInfo.textContent);
} else {
    console.log("❌ Debug info NOT found");
}

// 7. Test heatmap button
const heatmapBtn = document.getElementById('generate-heatmap');
if (heatmapBtn) {
    console.log("✅ Heatmap button found");
    console.log("Testing heatmap button click...");
    heatmapBtn.click();
} else {
    console.log("❌ Heatmap button NOT found");
}

console.log("=== Test Complete ===");
