// Check for the actual function name
console.log("=== Function Check ===");

// Check what functions are available
if (typeof showNumberAnalysis === 'function') {
    console.log("✅ showNumberAnalysis function exists");
} else {
    console.log("❌ showNumberAnalysis function NOT found");
}

if (typeof fetchNumberAnalysis === 'function') {
    console.log("✅ fetchNumberAnalysis function exists");
} else {
    console.log("❌ fetchNumberAnalysis function NOT found");
}

// Let's manually test the showNumberAnalysis function
console.log("Testing showNumberAnalysis with number 00...");
if (typeof showNumberAnalysis === 'function') {
    showNumberAnalysis('00');
} else {
    console.log("Cannot test - function not found");
}

// Also check if clicks are actually being registered
const buttons = document.querySelectorAll('.number-analysis-btn');
if (buttons.length > 0) {
    console.log("Adding direct click test...");
    buttons[0].addEventListener('click', function(e) {
        console.log("🔥 DIRECT CLICK DETECTED!");
        console.log("Data number:", e.target.dataset.number);
        console.log("Calling showNumberAnalysis...");
        if (typeof showNumberAnalysis === 'function') {
            showNumberAnalysis(e.target.dataset.number);
        }
    });
    console.log("✅ Direct click listener added. Click button again!");
}
