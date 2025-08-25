// Simple Grid Probability Display Test
console.log('🎯 Testing Simple Grid Probability Display...');

// Function to check grid cells with probability display
function checkGridProbabilities() {
    console.log('\n📊 Checking Grid Cells with Probability Display...');
    
    const gridCells = document.querySelectorAll('.frequency-cell');
    console.log('Found grid cells:', gridCells.length);
    
    if (gridCells.length === 0) {
        console.error('❌ No grid cells found! Make sure you are on comprehensive analysis tab.');
        return false;
    }
    
    let cellsWithProbability = 0;
    let cellsWithData = 0;
    let sampleData = [];
    
    gridCells.forEach((cell, index) => {
        const number = cell.dataset.number;
        const smallElements = cell.querySelectorAll('small');
        
        if (number && smallElements.length >= 2) {
            cellsWithData++;
            
            // Check if second small element contains percentage
            const probabilityElement = smallElements[1];
            if (probabilityElement && probabilityElement.textContent.includes('%')) {
                cellsWithProbability++;
                
                if (sampleData.length < 10) {
                    sampleData.push({
                        number: number,
                        ganDays: smallElements[0] ? smallElements[0].textContent : 'N/A',
                        probability: probabilityElement.textContent,
                        cellClass: cell.className
                    });
                }
            }
        }
    });
    
    console.log('✅ Cells with data:', cellsWithData);
    console.log('✅ Cells with probability display:', cellsWithProbability);
    console.log('📋 Sample data:');
    console.table(sampleData);
    
    return cellsWithProbability > 0;
}

// Function to highlight high probability cells
function highlightHighProbabilityCells() {
    console.log('\n🎯 Highlighting High Probability Cells...');
    
    const gridCells = document.querySelectorAll('.frequency-cell');
    const probabilityData = [];
    
    gridCells.forEach(cell => {
        const number = cell.dataset.number;
        const smallElements = cell.querySelectorAll('small');
        
        if (number && smallElements.length >= 2) {
            const probabilityText = smallElements[1].textContent;
            const probabilityMatch = probabilityText.match(/(\d+\.?\d*)%/);
            
            if (probabilityMatch) {
                const probability = parseFloat(probabilityMatch[1]);
                probabilityData.push({
                    number: number,
                    probability: probability,
                    element: cell
                });
            }
        }
    });
    
    // Sort by probability
    probabilityData.sort((a, b) => b.probability - a.probability);
    
    // Highlight top 10
    const top10 = probabilityData.slice(0, 10);
    
    console.log('🏆 Top 10 Highest Probability Numbers:');
    console.table(top10.map(item => ({
        number: item.number,
        probability: item.probability + '%'
    })));
    
    // Add visual highlight to top 3
    top10.slice(0, 3).forEach((item, index) => {
        const rankColors = ['gold', 'silver', '#cd7f32']; // Gold, Silver, Bronze
        item.element.style.boxShadow = `0 0 10px ${rankColors[index]}`;
        item.element.style.borderColor = rankColors[index];
        item.element.style.borderWidth = '3px';
    });
    
    console.log('✨ Top 3 cells highlighted with colored borders');
    
    return top10;
}

// Function to create probability summary
function createProbabilitySummary() {
    console.log('\n📈 Creating Probability Summary...');
    
    const gridCells = document.querySelectorAll('.frequency-cell');
    const probabilities = [];
    
    gridCells.forEach(cell => {
        const smallElements = cell.querySelectorAll('small');
        if (smallElements.length >= 2) {
            const probabilityText = smallElements[1].textContent;
            const probabilityMatch = probabilityText.match(/(\d+\.?\d*)%/);
            
            if (probabilityMatch) {
                probabilities.push(parseFloat(probabilityMatch[1]));
            }
        }
    });
    
    if (probabilities.length > 0) {
        const avgProbability = probabilities.reduce((sum, p) => sum + p, 0) / probabilities.length;
        const maxProbability = Math.max(...probabilities);
        const minProbability = Math.min(...probabilities);
        const highProbCount = probabilities.filter(p => p >= 50).length;
        const mediumProbCount = probabilities.filter(p => p >= 25 && p < 50).length;
        const lowProbCount = probabilities.filter(p => p < 25).length;
        
        console.log('📊 Probability Statistics:');
        console.log('- Total numbers with probabilities:', probabilities.length);
        console.log('- Average probability:', avgProbability.toFixed(2) + '%');
        console.log('- Highest probability:', maxProbability + '%');
        console.log('- Lowest probability:', minProbability + '%');
        console.log('- High probability (≥50%):', highProbCount);
        console.log('- Medium probability (25-49%):', mediumProbCount);
        console.log('- Low probability (<25%):', lowProbCount);
        
        return {
            total: probabilities.length,
            avg: avgProbability,
            max: maxProbability,
            min: minProbability,
            high: highProbCount,
            medium: mediumProbCount,
            low: lowProbCount
        };
    }
    
    return null;
}

// Function to check if on comprehensive tab
function checkComprehensiveTab() {
    const comprehensiveTab = document.querySelector('#comprehensive-tab');
    const comprehensivePane = document.querySelector('#comprehensive');
    
    if (!comprehensiveTab || !comprehensivePane) {
        console.error('❌ Comprehensive tab not found!');
        return false;
    }
    
    const isActive = comprehensivePane.classList.contains('show', 'active');
    
    if (!isActive) {
        console.log('⚠️ Not on comprehensive tab. Switching...');
        comprehensiveTab.click();
        
        setTimeout(() => {
            console.log('✅ Switched to comprehensive tab');
            runGridTest();
        }, 1000);
        
        return false;
    }
    
    console.log('✅ Already on comprehensive tab');
    return true;
}

// Main test function
function runGridTest() {
    console.log('🚀 Starting Simple Grid Probability Test...');
    
    const onCorrectTab = checkComprehensiveTab();
    if (!onCorrectTab) return;
    
    const hasGridData = checkGridProbabilities();
    const topProbabilities = highlightHighProbabilityCells();
    const summary = createProbabilitySummary();
    
    if (hasGridData) {
        console.log('\n🎉 SUCCESS! Probability display is working correctly.');
        console.log('✅ Probabilities are visible on grid cells');
        console.log('✅ Top probability cells highlighted');
        console.log('✅ Statistics calculated');
    } else {
        console.log('\n❌ FAILED! Probability display not working.');
        console.log('💡 Make sure you are on comprehensive analysis tab');
        console.log('💡 Check if comprehensive_analysis data is loaded');
    }
    
    console.log('\n💡 Usage:');
    console.log('- Look at grid cells: Number + Gan days + Probability%');
    console.log('- Top 3 highest probability numbers have colored borders');
    console.log('- Check console for detailed statistics');
}

// Auto-run test
runGridTest();
