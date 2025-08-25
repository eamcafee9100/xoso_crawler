// Function to create Top Predictions display section
function createTopPredictionsSection() {
    console.log('Creating Top Predictions Section...');
    
    // Extract prediction data from grid cells
    const gridCells = document.querySelectorAll('.grid-cell');
    const predictionData = [];
    
    gridCells.forEach(cell => {
        const number = cell.dataset.number;
        const title = cell.title || '';
        
        if (number && title) {
            // Extract probability from title (format: "Số X: Y.Y% xác suất...")
            const probMatch = title.match(/(\d+\.?\d*)%\s*xác\s*suất/i);
            if (probMatch) {
                const probability = parseFloat(probMatch[1]);
                predictionData.push({
                    number: number,
                    probability: probability,
                    fullTitle: title
                });
            }
        }
    });
    
    // Sort by probability (highest first)
    predictionData.sort((a, b) => b.probability - a.probability);
    
    console.log('Extracted prediction data:', predictionData);
    
    // Create Top 10 predictions HTML
    let html = '<div class="card">';
    html += '<div class="card-header bg-success text-white py-2">';
    html += '<h6 class="mb-0">🎯 Top 10 Số có Xác suất Dự đoán Cao nhất</h6>';
    html += '</div>';
    html += '<div class="card-body">';
    
    if (predictionData.length === 0) {
        html += '<p class="text-muted">Chưa có dữ liệu xác suất dự đoán</p>';
    } else {
        html += '<div class="table-responsive">';
        html += '<table class="table table-sm table-striped">';
        html += '<thead><tr><th style="width: 60px">Hạng</th><th style="width: 60px">Số</th><th>Xác suất</th><th>Tiến trình</th></tr></thead>';
        html += '<tbody>';
        
        const top10 = predictionData.slice(0, 10);
        const maxProbability = top10.length > 0 ? top10[0].probability : 100;
        
        top10.forEach((item, index) => {
            const rank = index + 1;
            const progressWidth = (item.probability / maxProbability * 100).toFixed(1);
            
            let rankColor = '';
            if (rank === 1) rankColor = 'text-warning'; // Gold
            else if (rank === 2) rankColor = 'text-secondary'; // Silver  
            else if (rank === 3) rankColor = 'text-warning'; // Bronze
            
            let probabilityColor = '';
            if (item.probability >= 80) probabilityColor = 'bg-danger';
            else if (item.probability >= 60) probabilityColor = 'bg-warning';
            else if (item.probability >= 40) probabilityColor = 'bg-info';
            else probabilityColor = 'bg-secondary';
            
            html += '<tr>';
            html += '<td><strong class="' + rankColor + '">#' + rank + '</strong></td>';
            html += '<td><span class="badge bg-primary clickable-number" data-number="' + item.number + '" style="cursor: pointer;">' + item.number + '</span></td>';
            html += '<td><strong class="text-success">' + item.probability.toFixed(1) + '%</strong></td>';
            html += '<td>';
            html += '<div class="progress" style="height: 20px;">';
            html += '<div class="progress-bar ' + probabilityColor + '" style="width: ' + progressWidth + '%">';
            html += item.probability.toFixed(1) + '%';
            html += '</div>';
            html += '</div>';
            html += '</td>';
            html += '</tr>';
        });
        
        html += '</tbody></table>';
        html += '</div>';
        
        // Add summary statistics
        if (predictionData.length > 0) {
            const avgProbability = predictionData.reduce((sum, item) => sum + item.probability, 0) / predictionData.length;
            const highProbCount = predictionData.filter(item => item.probability >= 50).length;
            
            html += '<div class="mt-3 p-2 bg-light rounded">';
            html += '<small class="text-muted">';
            html += '📊 <strong>Thống kê:</strong> ';
            html += 'Xác suất trung bình: ' + avgProbability.toFixed(1) + '% | ';
            html += 'Số có xác suất ≥50%: ' + highProbCount + '/' + predictionData.length;
            html += '</small>';
            html += '</div>';
        }
    }
    
    html += '</div>';
    html += '</div>';
    
    return html;
}

// Function to add top predictions to existing modal
function addTopPredictionsToModal() {
    console.log('Adding Top Predictions to modal...');
    
    // Find the modal body in the comprehensive analysis modal
    const modal = document.querySelector('#comprehensiveAnalysisModal');
    if (!modal) {
        console.error('Comprehensive analysis modal not found');
        return;
    }
    
    const modalBody = modal.querySelector('.modal-body');
    if (!modalBody) {
        console.error('Modal body not found');
        return;
    }
    
    // Check if top predictions section already exists
    const existingSection = modalBody.querySelector('.top-predictions-section');
    if (existingSection) {
        console.log('Top predictions section already exists, updating...');
        existingSection.innerHTML = createTopPredictionsSection();
        return;
    }
    
    // Create new section
    const topPredictionsHtml = '<div class="top-predictions-section mb-4">' + createTopPredictionsSection() + '</div>';
    
    // Insert at the beginning of modal content
    const firstChild = modalBody.firstElementChild;
    if (firstChild) {
        firstChild.insertAdjacentHTML('afterend', topPredictionsHtml);
    } else {
        modalBody.innerHTML = topPredictionsHtml + modalBody.innerHTML;
    }
    
    // Add event listeners for clickable numbers in top predictions
    const clickableNumbers = modalBody.querySelectorAll('.clickable-number');
    clickableNumbers.forEach(numberElement => {
        numberElement.addEventListener('click', function() {
            const number = this.dataset.number;
            if (number && window.analyzeNumber) {
                console.log('Analyzing number from top predictions:', number);
                window.analyzeNumber(number);
            }
        });
    });
    
    console.log('Top predictions section added successfully');
}

// Test function
function testTopPredictions() {
    console.log('Testing Top Predictions functionality...');
    
    // Create the HTML
    const html = createTopPredictionsSection();
    console.log('Generated HTML:', html);
    
    // Try to add to modal if it exists
    addTopPredictionsToModal();
}

// Auto-execute test
console.log('🎯 Top Predictions script loaded. Use testTopPredictions() to test or addTopPredictionsToModal() to add to existing modal.');
testTopPredictions();
