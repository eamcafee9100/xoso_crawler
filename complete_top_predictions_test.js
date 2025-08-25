// Complete Test Script for Top Predictions Feature
console.log('🎯 Testing Top Predictions Feature - Complete Analysis');

// Step 1: Check if grid exists and has data
function checkGridData() {
    console.log('\n1. 📊 Checking Grid Data...');
    
    const gridCells = document.querySelectorAll('.grid-cell');
    console.log('Found grid cells:', gridCells.length);
    
    if (gridCells.length === 0) {
        console.error('❌ No grid cells found! Make sure you are on the frequency analysis page.');
        return false;
    }
    
    let cellsWithData = 0;
    let cellsWithProbability = 0;
    let sampleData = [];
    
    gridCells.forEach((cell, index) => {
        const number = cell.dataset.number;
        const title = cell.title || '';
        
        if (number && title) {
            cellsWithData++;
            
            // Extract probability from title
            const probMatch = title.match(/(\d+\.?\d*)%\s*xác\s*suất/i);
            if (probMatch) {
                cellsWithProbability++;
                const probability = parseFloat(probMatch[1]);
                
                if (sampleData.length < 5) {
                    sampleData.push({
                        number: number,
                        probability: probability,
                        title: title.substring(0, 100) + '...'
                    });
                }
            }
        }
    });
    
    console.log('✅ Cells with data:', cellsWithData);
    console.log('✅ Cells with probability:', cellsWithProbability);
    console.log('📋 Sample data:', sampleData);
    
    return cellsWithProbability > 0;
}

// Step 2: Test createTopPredictionsSection function
function testTopPredictionsFunction() {
    console.log('\n2. 🔧 Testing createTopPredictionsSection function...');
    
    // Check if function exists in global scope or window
    if (typeof createTopPredictionsSection === 'function') {
        console.log('✅ Function found in global scope');
    } else if (typeof window.createTopPredictionsSection === 'function') {
        console.log('✅ Function found in window scope');
        window.createTopPredictionsSection = window.createTopPredictionsSection;
    } else {
        console.error('❌ createTopPredictionsSection function not found!');
        return false;
    }
    
    try {
        const html = createTopPredictionsSection();
        console.log('✅ Function executed successfully');
        console.log('📄 Generated HTML length:', html.length);
        console.log('📄 HTML preview:', html.substring(0, 200) + '...');
        return true;
    } catch (error) {
        console.error('❌ Error executing function:', error);
        return false;
    }
}

// Step 3: Test modal integration
function testModalIntegration() {
    console.log('\n3. 🖼️ Testing Modal Integration...');
    
    // Check if comprehensive analysis modal exists
    const modal = document.querySelector('#comprehensiveAnalysisModal');
    if (!modal) {
        console.error('❌ Comprehensive analysis modal not found!');
        return false;
    }
    
    console.log('✅ Comprehensive analysis modal found');
    
    // Try to open modal for testing (pick first number)
    const firstCell = document.querySelector('.grid-cell[data-number]');
    if (!firstCell) {
        console.error('❌ No clickable grid cell found');
        return false;
    }
    
    const testNumber = firstCell.dataset.number;
    console.log('🧪 Testing with number:', testNumber);
    
    // Simulate click
    if (typeof window.analyzeNumber === 'function') {
        console.log('✅ analyzeNumber function found');
        
        try {
            window.analyzeNumber(testNumber);
            console.log('✅ Modal should be opening...');
            
            // Wait a bit then check modal content
            setTimeout(() => {
                const modalBody = modal.querySelector('.modal-body');
                if (modalBody) {
                    const topPredictionsSection = modalBody.querySelector('[class*="Top"], [class*="top"], .card-header:contains("Top")');
                    if (topPredictionsSection) {
                        console.log('✅ Top predictions section found in modal!');
                    } else {
                        console.log('⚠️ Top predictions section not found in modal content');
                        console.log('Modal content preview:', modalBody.innerHTML.substring(0, 300) + '...');
                    }
                }
            }, 1000);
            
            return true;
        } catch (error) {
            console.error('❌ Error calling analyzeNumber:', error);
            return false;
        }
    } else {
        console.error('❌ analyzeNumber function not found!');
        return false;
    }
}

// Step 4: Create demo top predictions display
function createDemoDisplay() {
    console.log('\n4. 🎨 Creating Demo Display...');
    
    // Create a demo container
    const demoContainer = document.createElement('div');
    demoContainer.id = 'demo-top-predictions';
    demoContainer.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        width: 400px;
        background: white;
        border: 2px solid #007bff;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        z-index: 9999;
        max-height: 500px;
        overflow-y: auto;
    `;
    
    // Remove existing demo if present
    const existingDemo = document.getElementById('demo-top-predictions');
    if (existingDemo) {
        existingDemo.remove();
    }
    
    // Create content
    let demoHtml = '<h5 style="margin: 0 0 15px 0; color: #007bff;">🎯 Demo Top Predictions</h5>';
    
    try {
        if (typeof createTopPredictionsSection === 'function') {
            demoHtml += createTopPredictionsSection();
        } else {
            demoHtml += '<p style="color: red;">Function not available</p>';
        }
    } catch (error) {
        demoHtml += '<p style="color: red;">Error: ' + error.message + '</p>';
    }
    
    demoHtml += '<button onclick="document.getElementById(\'demo-top-predictions\').remove()" style="margin-top: 10px; padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">Close Demo</button>';
    
    demoContainer.innerHTML = demoHtml;
    document.body.appendChild(demoContainer);
    
    console.log('✅ Demo display created (top-right corner)');
}

// Step 5: Extract and show actual prediction data
function showPredictionData() {
    console.log('\n5. 📊 Extracting Actual Prediction Data...');
    
    const gridCells = document.querySelectorAll('.grid-cell');
    const predictionData = [];
    
    gridCells.forEach(cell => {
        const number = cell.dataset.number;
        const title = cell.title || '';
        
        if (number && title) {
            const probMatch = title.match(/(\d+\.?\d*)%\s*xác\s*suất/i);
            if (probMatch) {
                const probability = parseFloat(probMatch[1]);
                predictionData.push({
                    number: number,
                    probability: probability
                });
            }
        }
    });
    
    // Sort by probability
    predictionData.sort((a, b) => b.probability - a.probability);
    
    console.log('📊 Total numbers with predictions:', predictionData.length);
    console.log('🏆 Top 10 Predictions:');
    console.table(predictionData.slice(0, 10));
    
    if (predictionData.length > 0) {
        const avgProb = predictionData.reduce((sum, item) => sum + item.probability, 0) / predictionData.length;
        const highProbCount = predictionData.filter(item => item.probability >= 50).length;
        
        console.log('📈 Average Probability:', avgProb.toFixed(2) + '%');
        console.log('🔥 High Probability (≥50%) Count:', highProbCount);
    }
    
    return predictionData;
}

// Main test runner
function runCompleteTest() {
    console.log('🚀 Starting Complete Top Predictions Test...');
    
    const results = {
        gridData: checkGridData(),
        functionTest: testTopPredictionsFunction(),
        modalTest: testModalIntegration(),
    };
    
    const predictionData = showPredictionData();
    createDemoDisplay();
    
    console.log('\n📋 Test Results Summary:');
    console.table(results);
    
    const allPassed = Object.values(results).every(result => result === true);
    if (allPassed) {
        console.log('🎉 All tests passed! Top Predictions feature should be working.');
    } else {
        console.log('⚠️ Some tests failed. Check the details above.');
    }
    
    console.log('\n💡 Next steps:');
    console.log('1. If demo display shows correctly → Feature is working');
    console.log('2. Try clicking a number in the grid to open analysis modal');
    console.log('3. Look for "Top 10 Số có Xác suất Dự đoán Cao nhất" section in modal');
}

// Auto-run the complete test
runCompleteTest();
