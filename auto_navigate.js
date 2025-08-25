// Auto-Navigate to Frequency Analysis Page
console.log('🚀 Auto-navigating to Frequency Analysis page...');

// Try different possible URLs
const possibleUrls = [
    '/results/number-frequency-stats/',
    '/results/frequency-analysis/',
    '/results/stats/',
    '/number-frequency-stats/',
    '/frequency-analysis/'
];

// Check current URL
console.log('📍 Current URL:', window.location.href);

// Function to try navigation
function tryNavigate() {
    // First, try to find navigation links
    const navLinks = document.querySelectorAll('a');
    let foundLink = null;
    
    for (let link of navLinks) {
        const href = link.href || '';
        const text = link.textContent.toLowerCase();
        
        if (href.includes('frequency') || href.includes('stats') || 
            text.includes('frequency') || text.includes('stats')) {
            console.log('🔗 Found navigation link:', link.textContent, '→', href);
            foundLink = link;
            break;
        }
    }
    
    if (foundLink) {
        console.log('✅ Clicking navigation link...');
        foundLink.click();
        return true;
    }
    
    // If no link found, try direct URL navigation
    for (let url of possibleUrls) {
        const fullUrl = window.location.origin + url;
        console.log('🎯 Trying:', fullUrl);
        
        try {
            window.location.href = fullUrl;
            return true;
        } catch (error) {
            console.log('❌ Failed:', error.message);
        }
    }
    
    return false;
}

// Check if we're already on the right page
const hasGrid = document.querySelectorAll('.grid-cell').length > 0;
const hasFrequencyModal = document.querySelector('#numberAnalysisModal') || document.querySelector('#comprehensiveAnalysisModal');

if (hasGrid && hasFrequencyModal) {
    console.log('✅ Already on frequency analysis page!');
    console.log('🎯 Ready to test. Run complete_top_predictions_test.js');
} else {
    console.log('❌ Not on frequency analysis page. Attempting navigation...');
    
    if (!tryNavigate()) {
        console.log('⚠️  Auto-navigation failed. Please manually navigate to:');
        console.log('🔗 Menu: Results → Number Frequency Stats');
        console.log('🔗 Or URL: /results/number-frequency-stats/');
    } else {
        console.log('✅ Navigation attempted. Page should be loading...');
        console.log('⏳ Wait for page load, then run complete_top_predictions_test.js');
    }
}

// Alternative: Show manual navigation instructions
console.log('\n📝 Manual Navigation Instructions:');
console.log('1. Look for "Results" in navigation menu');
console.log('2. Click "Number Frequency Stats" or similar');
console.log('3. Wait for page with 10x10 grid to load');
console.log('4. Run complete_top_predictions_test.js again');

// Show available navigation options on current page
console.log('\n🧭 Available links on current page:');
const allLinks = document.querySelectorAll('a');
const relevantLinks = [];

allLinks.forEach((link, index) => {
    const href = link.href || '';
    const text = link.textContent.trim();
    
    if (text && (
        text.toLowerCase().includes('result') ||
        text.toLowerCase().includes('stat') ||
        text.toLowerCase().includes('frequency') ||
        text.toLowerCase().includes('analysis') ||
        href.includes('result') ||
        href.includes('stat') ||
        href.includes('frequency')
    )) {
        relevantLinks.push({
            text: text,
            href: href
        });
    }
});

if (relevantLinks.length > 0) {
    console.table(relevantLinks);
} else {
    console.log('❌ No relevant navigation links found');
}
