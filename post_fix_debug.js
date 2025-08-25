// Quick debug after template fix
console.log("=== Post-Fix Debug ===");

// 1. Check if functions are now in global scope
console.log("window.showNumberAnalysis exists:", typeof window.showNumberAnalysis === 'function');
console.log("window.generateHeatmap exists:", typeof window.generateHeatmap === 'function');

// 2. Check button count and click handlers
const buttons = document.querySelectorAll('.number-analysis-btn');
console.log("Analysis buttons found:", buttons.length);

// 3. Check if original event listeners are working
if (buttons.length > 0) {
    console.log("First button data-number:", buttons[0].dataset.number);
    console.log("First button onclick:", buttons[0].onclick);
    
    // Force add a new click listener
    buttons[0].addEventListener('click', function(e) {
        console.log("🔥 NEW LISTENER: Click detected on", e.target.dataset.number);
        if (typeof window.showNumberAnalysis === 'function') {
            window.showNumberAnalysis(e.target.dataset.number);
        } else {
            console.error("Function still not available");
        }
    });
    
    console.log("✅ New listener added to first button");
    console.log("👆 Click the first button now to test");
}

// 4. Test function directly
if (typeof window.showNumberAnalysis === 'function') {
    console.log("🧪 Testing function directly...");
    window.showNumberAnalysis('01');
} else {
    console.log("❌ Function not available for direct test");
}

// 5. Check page source for script errors
console.log("🔍 Checking for JavaScript errors...");
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.message, 'at', e.filename, 'line', e.lineno);
});

console.log("=== Debug Complete ===");
