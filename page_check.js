// Simple Page Check Script
console.log('🔍 Checking Current Page for Frequency Analysis Features...');

// Check page URL
console.log('📍 Current URL:', window.location.href);
console.log('📍 Current Page Title:', document.title);

// Check for frequency analysis indicators
const indicators = {
    'Grid Cells (.grid-cell)': document.querySelectorAll('.grid-cell').length,
    'Frequency Stats Table': document.querySelectorAll('table').length,
    'Number Analysis Modal': document.querySelector('#numberAnalysisModal') ? 'Found' : 'Not Found',
    'Comprehensive Analysis Modal': document.querySelector('#comprehensiveAnalysisModal') ? 'Found' : 'Not Found',
    'Generate Heatmap Button': document.querySelector('button:contains("Heatmap"), [onclick*="heatmap"]') ? 'Found' : 'Not Found',
    'analyzeNumber Function': typeof window.analyzeNumber === 'function' ? 'Available' : 'Not Available',
    'showFrequencyHeatmap Function': typeof window.showFrequencyHeatmap === 'function' ? 'Available' : 'Not Available'
};

console.log('\n📊 Page Analysis Results:');
console.table(indicators);

// Check if we're on the right page
const hasGrid = document.querySelectorAll('.grid-cell').length > 0;
const hasFrequencyFeatures = document.querySelector('#numberAnalysisModal') || document.querySelector('#comprehensiveAnalysisModal');

if (hasGrid && hasFrequencyFeatures) {
    console.log('✅ Perfect! You are on the correct Frequency Analysis page.');
    console.log('🎯 Ready to test Top Predictions feature.');
} else if (hasFrequencyFeatures && !hasGrid) {
    console.log('⚠️  You are on a frequency page but grid not found.');
    console.log('💡 Try scrolling down or waiting for page to load completely.');
} else {
    console.log('❌ You are NOT on the Frequency Analysis page.');
    console.log('📍 Please navigate to: /results/number-frequency-stats/');
    console.log('🔗 Or click: Results → Number Frequency Stats in menu');
}

// Additional page content check
console.log('\n🔍 Page Content Analysis:');
console.log('- Page contains "frequency":', document.body.innerHTML.toLowerCase().includes('frequency'));
console.log('- Page contains "analysis":', document.body.innerHTML.toLowerCase().includes('analysis'));
console.log('- Page contains grid-related class:', document.body.innerHTML.includes('grid'));
console.log('- Page has Django CSRF token:', document.querySelector('[name="csrfmiddlewaretoken"]') ? 'Yes' : 'No');

// Show available navigation options
console.log('\n🧭 Available Navigation:');
const navLinks = document.querySelectorAll('a[href*="frequency"], a[href*="stats"], a[href*="results"]');
if (navLinks.length > 0) {
    console.log('Found relevant links:');
    navLinks.forEach((link, index) => {
        console.log(`${index + 1}. ${link.textContent.trim()} → ${link.href}`);
    });
} else {
    console.log('No frequency/stats links found in navigation');
}

// Check for development server
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('\n🚀 Development server detected. Make sure Django is running.');
} else {
    console.log('\n🌐 Production server detected.');
}

console.log('\n📝 Next Steps:');
console.log('1. Navigate to the correct page if needed');
console.log('2. Wait for page to fully load');
console.log('3. Run complete_top_predictions_test.js again');
console.log('4. Look for 10x10 grid with numbers 00-99');
