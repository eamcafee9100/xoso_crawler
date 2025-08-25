// Direct Navigation to Base Frequency Stats Page
console.log('🎯 Navigating to base frequency stats page...');

// Current URL analysis
console.log('📍 Current URL:', window.location.href);
console.log('📍 Current params:', window.location.search);

// Remove analysis_mode parameter and navigate to base page
const baseUrl = 'http://127.0.0.1:8000/number-frequency-stats/';
console.log('🚀 Navigating to:', baseUrl);

// Method 1: Direct navigation
try {
    window.location.href = baseUrl;
    console.log('✅ Navigation initiated...');
} catch (error) {
    console.error('❌ Navigation failed:', error);
}

// Alternative method if direct navigation doesn't work
setTimeout(() => {
    if (window.location.href === baseUrl) {
        console.log('✅ Successfully navigated to base page');
        console.log('⏳ Waiting for page load...');
        
        // Wait a bit more then check for grid
        setTimeout(() => {
            const gridCells = document.querySelectorAll('.grid-cell');
            console.log('📊 Grid cells found:', gridCells.length);
            
            if (gridCells.length > 0) {
                console.log('🎉 Grid loaded successfully!');
                console.log('🎯 Ready to test Top Predictions feature');
            } else {
                console.log('⚠️ Grid not found. Trying page refresh...');
                window.location.reload();
            }
        }, 2000);
    }
}, 1000);

console.log('\n💡 If navigation doesn\'t work automatically:');
console.log('1. Manually go to: http://127.0.0.1:8000/number-frequency-stats/');
console.log('2. Remove the ?analysis_mode=comprehensive parameter');
console.log('3. Look for the 10x10 grid');
console.log('4. Run complete_top_predictions_test.js');

// Also try clicking the "n Quản lý dữ liệu" link which looks like the right one
const managementLink = Array.from(document.querySelectorAll('a')).find(link => 
    link.textContent.includes('Quản lý dữ liệu') && 
    link.href.includes('/number-frequency-stats/')
);

if (managementLink) {
    console.log('\n🔗 Alternative: Clicking "Quản lý dữ liệu" link...');
    setTimeout(() => {
        managementLink.click();
        console.log('✅ Link clicked, waiting for page load...');
    }, 3000);
}
