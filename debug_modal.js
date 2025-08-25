// Debug modal functionality
console.log("=== Modal Debug Test ===");

// 1. Check if Bootstrap modal is available
if (typeof bootstrap !== 'undefined') {
    console.log("✅ Bootstrap available");
} else {
    console.log("❌ Bootstrap NOT available");
}

// 2. Check for modal element
const modal = document.getElementById('numberAnalysisModal');
if (modal) {
    console.log("✅ Modal element found");
    console.log("Modal classes:", modal.className);
} else {
    console.log("❌ Modal element NOT found");
}

// 3. Test modal manually
if (modal && typeof bootstrap !== 'undefined') {
    console.log("Testing modal manually...");
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    console.log("✅ Modal shown manually");
} else {
    console.log("❌ Cannot test modal");
}

// 4. Check click event listeners
const buttons = document.querySelectorAll('.number-analysis-btn');
console.log("Checking event listeners...");

// Add a temporary click listener to see if clicks are working
if (buttons.length > 0) {
    const testButton = buttons[0];
    testButton.addEventListener('click', function(e) {
        console.log("🔥 CLICK DETECTED on button:", e.target.dataset.number);
        console.log("Button text:", e.target.textContent);
        
        // Try to trigger the analysis manually
        if (typeof fetchNumberAnalysis === 'function') {
            console.log("✅ fetchNumberAnalysis function exists");
            fetchNumberAnalysis(e.target.dataset.number);
        } else {
            console.log("❌ fetchNumberAnalysis function NOT found");
        }
    });
    
    console.log("✅ Test listener added. Click any number button now!");
}
