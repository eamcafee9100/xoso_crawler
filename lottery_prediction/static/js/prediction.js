// Prediction form handler with proper error handling and chart management

let probabilityChart = null;
let currentRequest = null;

$(document).ready(function() {
    // Initialize form handler
    $('#predictionForm').on('submit', handleFormSubmission);
    
    // Initialize context change handler
    $('#predictionContext').on('change', handleContextChange);
    
    // Set default date based on context
    updateDefaultDate();
    
    console.log('Prediction form initialized');
});

function handleFormSubmission(e) {
    e.preventDefault();
    
    // Cancel any existing request
    if (currentRequest) {
        currentRequest.abort();
    }
    
    // Get form data
    const formData = getFormData();
    
    // Validate form data
    if (!validateFormData(formData)) {
        return;
    }
    
    // Show loading state
    showLoading();
    
    // Make API request
    currentRequest = $.ajax({
        url: '/lottery-prediction/api/predict/',
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        },
        data: JSON.stringify(formData),
        success: function(response) {
            console.log('API Success:', response);
            handleSuccess(response);
        },
        error: function(xhr, status, error) {
            console.error('API Error:', xhr.responseJSON || error);
            handleError(xhr.responseJSON || {error: error});
        },
        complete: function() {
            hideLoading();
            currentRequest = null;
        }
    });
}

function getFormData() {
    return {
        prediction_date: $('#predictionDate').val(),
        model_type: $('#modelType').val(),
        top_k: parseInt($('#topK').val()),
        prediction_context: $('#predictionContext').val()
    };
}

function validateFormData(data) {
    // Basic client-side validation
    if (!data.prediction_date) {
        showError('Please select a prediction date');
        return false;
    }
    
    if (data.top_k < 1 || data.top_k > 50) {
        showError('Top K must be between 1 and 50');
        return false;
    }
    
    // Context-specific validation
    const currentDate = new Date().toISOString().split('T')[0];
    if (data.prediction_context === 'prediction' && data.prediction_date <= currentDate) {
        showError('Please select a future date for real predictions');
        return false;
    }
    
    return true;
}

function handleSuccess(response) {
    console.log('Processing successful response:', response);
    
    // Show results section
    $('#resultsSection').removeClass('d-none');
    
    // Render prediction results
    renderResults(response);
    
    // Render model info
    renderModelInfo(response.model_info);
    
    // Render data quality info
    renderDataQuality(response.data_quality);
    
    // Show success message
    showSuccess('Predictions generated successfully!');
    
    // Scroll to results
    $('#resultsSection')[0].scrollIntoView({ behavior: 'smooth' });
}

function renderResults(response) {
    const predictions = response.top_k_predictions || [];
    const tableBody = $('#predictionTable tbody');
    
    // Clear existing results
    tableBody.empty();
    
    // Add table header if not exists
    const tableHead = $('#predictionTable thead');
    if (tableHead.children().length === 0) {
        tableHead.html(`
            <tr>
                <th>Rank</th>
                <th>Number</th>
                <th>Probability</th>
                <th>Confidence</th>
            </tr>
        `);
    }
    
    // Populate table with predictions
    predictions.forEach(function(pred, index) {
        const probability = (pred.probability * 100).toFixed(2);
        const confidenceClass = getConfidenceClass(pred.probability);
        
        const row = `
            <tr>
                <td><span class="badge bg-primary">${pred.rank}</span></td>
                <td><strong>${pred.number}</strong></td>
                <td>${probability}%</td>
                <td><span class="badge ${confidenceClass}">${getConfidenceLabel(pred.probability)}</span></td>
            </tr>
        `;
        tableBody.append(row);
    });
    
    // Render probability chart
    renderChart(predictions);
}

function renderChart(predictions) {
    const ctx = document.getElementById('probabilityChart');
    if (!ctx) {
        console.warn('Chart canvas not found');
        return;
    }
    
    // Destroy existing chart if it exists
    if (probabilityChart && typeof probabilityChart.destroy === 'function') {
        probabilityChart.destroy();
    }
    
    // Prepare chart data
    const labels = predictions.map(p => p.number);
    const data = predictions.map(p => (p.probability * 100).toFixed(2));
    
    // Create new chart
    try {
        probabilityChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Probability (%)',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Prediction Probabilities'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Probability (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Numbers'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating chart:', error);
    }
}

function renderModelInfo(modelInfo) {
    const modelInfoList = $('#modelInfoList');
    modelInfoList.empty();
    
    const infoItems = [
        { label: 'Model Name', value: modelInfo.model_name },
        { label: 'Model Type', value: modelInfo.model_type },
        { label: 'Confidence Score', value: (modelInfo.confidence_score * 100).toFixed(2) + '%' },
        { label: 'Training Data Size', value: modelInfo.training_data_size || 'N/A' },
        { label: 'Last Training', value: modelInfo.last_train_date || 'N/A' }
    ];
    
    infoItems.forEach(function(item) {
        const listItem = `
            <li class="list-group-item d-flex justify-content-between">
                <span>${item.label}:</span>
                <strong>${item.value}</strong>
            </li>
        `;
        modelInfoList.append(listItem);
    });
}

function renderDataQuality(dataQuality) {
    const qualityScore = (dataQuality.score * 100).toFixed(1);
    const qualityClass = dataQuality.score > 0.8 ? 'bg-success' : 
                        dataQuality.score > 0.6 ? 'bg-warning' : 'bg-danger';
    
    const dataQualityHtml = `
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Data Quality</h5>
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span>Quality Score:</span>
                    <span class="badge ${qualityClass}">${qualityScore}%</span>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span>Data Points:</span>
                    <span>${dataQuality.reference_data_points}</span>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                    <span>Data Freshness:</span>
                    <span>${dataQuality.data_freshness_days} days</span>
                </div>
            </div>
        </div>
    `;
    
    // Add to results section if container exists
    let dataQualityContainer = $('#dataQualityContainer');
    if (dataQualityContainer.length === 0) {
        $('#resultsSection .card-body').append('<div id="dataQualityContainer" class="mt-3"></div>');
        dataQualityContainer = $('#dataQualityContainer');
    }
    dataQualityContainer.html(dataQualityHtml);
}

function handleError(error) {
    console.error('Handling error:', error);
    
    let errorMessage = 'An error occurred while generating predictions.';
    
    if (error.details) {
        if (typeof error.details === 'string') {
            errorMessage = error.details;
        } else if (error.details.prediction_date) {
            errorMessage = error.details.prediction_date[0];
        } else {
            errorMessage = JSON.stringify(error.details);
        }
    } else if (error.error) {
        errorMessage = error.error;
    }
    
    showError(errorMessage);
    
    // Hide results section on error
    $('#resultsSection').addClass('d-none');
}

function handleContextChange() {
    updateDefaultDate();
}

function updateDefaultDate() {
    const context = $('#predictionContext').val();
    const dateInput = $('#predictionDate');
    
    if (context === 'prediction') {
        // Set to tomorrow for real predictions
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.val(tomorrow.toISOString().split('T')[0]);
    } else {
        // Set to a past date for historical testing
        const pastDate = new Date();
        pastDate.setDate(pastDate.getDate() - 7); // A week ago
        dateInput.val(pastDate.toISOString().split('T')[0]);
    }
}

function getConfidenceClass(probability) {
    if (probability > 0.05) return 'bg-success';
    if (probability > 0.02) return 'bg-warning';
    return 'bg-secondary';
}

function getConfidenceLabel(probability) {
    if (probability > 0.05) return 'High';
    if (probability > 0.02) return 'Medium';
    return 'Low';
}

function showLoading() {
    const button = $('#predictionForm button[type="submit"]');
    button.prop('disabled', true);
    button.html('<span class="spinner-border spinner-border-sm me-2"></span>Generating...');
}

function hideLoading() {
    const button = $('#predictionForm button[type="submit"]');
    button.prop('disabled', false);
    button.html('Generate');
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'danger');
}

function showNotification(message, type) {
    // Remove existing notifications
    $('.alert').remove();
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Add notification at the top of the container
    $('.container').prepend(alertHtml);
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            $('.alert-success').fadeOut();
        }, 5000);
    }
}

function getCsrfToken() {
    return $('input[name="csrfmiddlewaretoken"]').val();
}