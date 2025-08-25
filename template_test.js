// Quick test to see if functions exist after template fix
console.log("=== Quick Template Test ===");

// Check if functions exist
console.log("window.showNumberAnalysis:", typeof window.showNumberAnalysis);
console.log("window.generateHeatmap:", typeof window.generateHeatmap);

// Check for JavaScript errors
const originalError = console.error;
let errorCount = 0;
console.error = function(...args) {
    errorCount++;
    console.log(`❌ JS Error ${errorCount}:`, ...args);
    originalError.apply(console, args);
};

// Check page source for script tag
const scripts = document.querySelectorAll('script');
console.log(`📄 Found ${scripts.length} script tags`);

// Look for our script content
let foundOurScript = false;
scripts.forEach((script, index) => {
    if (script.innerHTML.includes('window.showNumberAnalysis')) {
        console.log(`✅ Found our script in script tag ${index}`);
        foundOurScript = true;
        
        // Check for syntax errors in our script
        try {
            const functionText = script.innerHTML;
            console.log("🔍 Script length:", functionText.length, "characters");
            
            // Look for common syntax issues
            if (functionText.includes('undefined')) {
                console.log("⚠️ Warning: 'undefined' found in script");
            }
            if (functionText.includes('    });')) {
                console.log("⚠️ Warning: Suspicious closing brackets found");
            }
        } catch (e) {
            console.log("❌ Error analyzing script:", e);
        }
    }
});

if (!foundOurScript) {
    console.log("❌ Our script not found in page");
}

// Test manual function definition
try {
    console.log("🧪 Trying to define function manually...");
    eval(`
        window.testShowNumber = function(number) {
            console.log("Test function called with:", number);
            alert("Test function works for number: " + number);
        };
    `);
    console.log("✅ Manual function definition works");
    
    // Test it
    console.log("🎯 Testing manual function...");
    window.testShowNumber('99');
    
} catch (e) {
    console.log("❌ Manual function definition failed:", e);
}

console.log("=== Test Complete ===");
