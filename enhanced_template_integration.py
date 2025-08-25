"""
Enhanced Template Integration for Cyclical Intelligence
"""

# Template JavaScript enhancements to fully utilize API cyclical_prediction_by_date_v3

ENHANCED_TEMPLATE_JS = """
    // ✅ ENHANCED CYCLICAL INTELLIGENCE INTEGRATION
    
    function displaySingleDateResults(apiResponse, selectedDate) {
        console.log('📊 Cyclical Intelligence API Response:', apiResponse);
        
        if (!apiResponse.success) {
            showAlert('Lỗi API: ' + apiResponse.message, 'danger');
            return;
        }
        
        // Extract cyclical intelligence data
        const cyclicalAnalysis = apiResponse.cyclical_analysis || {};
        const contextAnalysis = cyclicalAnalysis.context_analysis || {};
        const methodSyncMatrix = cyclicalAnalysis.method_sync_matrix || {};
        const numberFrequencyCycles = cyclicalAnalysis.number_frequency_cycles || {};
        
        const optimalMethods = apiResponse.optimal_methods || {};
        const intelligentPredictions = apiResponse.intelligent_predictions || {};
        const performanceMetrics = apiResponse.performance_metrics || {};
        
        // Display cyclical context
        displayCyclicalContext(contextAnalysis, selectedDate);
        
        // Display method sync matrix
        displayMethodSyncMatrix(methodSyncMatrix);
        
        // Display intelligent predictions
        displayIntelligentPredictions(intelligentPredictions, performanceMetrics);
        
        // Update performance dashboard
        updatePerformanceDashboard(performanceMetrics);
        
        showResults();
    }
    
    function displayCyclicalContext(contextAnalysis, selectedDate) {
        const contextHtml = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-primary">
                        <div class="card-header bg-primary text-white">
                            <h6 class="mb-0">🧠 Cyclical Context Analysis - ${selectedDate}</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="badge badge-info badge-lg">${contextAnalysis.day_of_month_phase || 'N/A'}</div>
                                        <div class="small text-muted">Day Phase</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="badge badge-secondary badge-lg">${contextAnalysis.week_phase || 'N/A'}</div>
                                        <div class="small text-muted">Week Phase</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="badge badge-warning badge-lg">${contextAnalysis.month_trend || 'N/A'}</div>
                                        <div class="small text-muted">Month Trend</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="progress" style="height: 25px;">
                                            <div class="progress-bar" role="progressbar" 
                                                style="width: ${(contextAnalysis.cycle_strength * 100 || 0)}%">
                                                ${((contextAnalysis.cycle_strength * 100) || 0).toFixed(1)}%
                                            </div>
                                        </div>
                                        <div class="small text-muted">Cycle Strength</div>
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-2">
                                <div class="col-md-6">
                                    <small><strong>Active Cycles:</strong> ${(contextAnalysis.active_cycles || []).length}</small>
                                </div>
                                <div class="col-md-6">
                                    <small><strong>Fatigued Methods:</strong> ${(contextAnalysis.fatigued_methods || []).length}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#cyclicalContext').html(contextHtml);
    }
    
    function displayMethodSyncMatrix(methodSyncMatrix) {
        const syncRecords = methodSyncMatrix.sync_records || [];
        const summaryStats = methodSyncMatrix.summary_stats || {};
        
        let syncMatrixHtml = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-success">
                        <div class="card-header bg-success text-white">
                            <h6 class="mb-0">🔗 Method-Cycle Sync Matrix (${syncRecords.length} methods)</h6>
                        </div>
                        <div class="card-body">
                            <div class="row mb-3">
                                <div class="col-md-4">
                                    <div class="text-center">
                                        <h5 class="text-success">${summaryStats.avg_cyclical_fitness || 0}</h5>
                                        <small class="text-muted">Avg Cyclical Fitness</small>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="text-center">
                                        <h5 class="text-warning">${((summaryStats.avg_fatigue_risk || 0) * 100).toFixed(1)}%</h5>
                                        <small class="text-muted">Avg Fatigue Risk</small>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="text-center">
                                        <h5 class="text-info">${methodSyncMatrix.total_methods_analyzed || 0}</h5>
                                        <small class="text-muted">Methods Analyzed</small>
                                    </div>
                                </div>
                            </div>
                            <div class="table-responsive">
                                <table class="table table-sm table-hover">
                                    <thead class="thead-light">
                                        <tr>
                                            <th>Method</th>
                                            <th>Cyclical Fitness</th>
                                            <th>Phase Alignment</th>
                                            <th>Fatigue Risk</th>
                                            <th>Trend</th>
                                        </tr>
                                    </thead>
                                    <tbody>
        `;
        
        // Show top 10 methods by cyclical fitness
        const topMethods = syncRecords
            .sort((a, b) => b.cyclical_fitness - a.cyclical_fitness)
            .slice(0, 10);
            
        topMethods.forEach(method => {
            const fitnessClass = method.cyclical_fitness >= 50 ? 'success' : 
                                method.cyclical_fitness >= 30 ? 'warning' : 'danger';
            const fatigueClass = method.fatigue_risk <= 0.3 ? 'success' : 
                                 method.fatigue_risk <= 0.6 ? 'warning' : 'danger';
            
            syncMatrixHtml += `
                <tr>
                    <td class="small">${method.method_name}</td>
                    <td><span class="badge badge-${fitnessClass}">${method.cyclical_fitness}</span></td>
                    <td><span class="badge badge-info">${(method.phase_alignment * 100).toFixed(1)}%</span></td>
                    <td><span class="badge badge-${fatigueClass}">${(method.fatigue_risk * 100).toFixed(1)}%</span></td>
                    <td><span class="badge badge-secondary">${method.trend_analysis.direction}</span></td>
                </tr>
            `;
        });
        
        syncMatrixHtml += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#methodSyncMatrix').html(syncMatrixHtml);
    }
    
    function displayIntelligentPredictions(intelligentPredictions, performanceMetrics) {
        const cyclicalNumbers = intelligentPredictions.cyclical_numbers || [];
        const methodNumbers = intelligentPredictions.method_numbers || [];
        const fusionNumbers = intelligentPredictions.fusion_numbers || [];
        
        const predictionHtml = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-info">
                        <div class="card-header bg-info text-white">
                            <h6 class="mb-0">🤖 Intelligent Predictions</h6>
                        </div>
                        <div class="card-body">
                            <ul class="nav nav-tabs" id="predictionsTab" role="tablist">
                                <li class="nav-item">
                                    <a class="nav-link active" id="fusion-tab" data-toggle="tab" href="#fusion" role="tab">
                                        🎯 Fusion Numbers (${fusionNumbers.length})
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" id="cyclical-tab" data-toggle="tab" href="#cyclical" role="tab">
                                        🔄 Cyclical Numbers (${cyclicalNumbers.length})
                                    </a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" id="method-tab" data-toggle="tab" href="#method" role="tab">
                                        📊 Method Numbers (${methodNumbers.length})
                                    </a>
                                </li>
                            </ul>
                            <div class="tab-content mt-3" id="predictionsTabContent">
                                <div class="tab-pane fade show active" id="fusion" role="tabpanel">
                                    <div class="alert alert-info">
                                        <strong>🎯 Fusion Strategy:</strong> Method Weight: 60% | Cyclical Weight: 40%
                                    </div>
                                    <div class="prediction-numbers">
                                        ${fusionNumbers.map((num, idx) => 
                                            `<span class="badge badge-primary badge-lg mr-1 mb-1" title="Rank ${idx + 1}">${num}</span>`
                                        ).join('')}
                                    </div>
                                </div>
                                <div class="tab-pane fade" id="cyclical" role="tabpanel">
                                    <div class="prediction-numbers">
                                        ${cyclicalNumbers.map((num, idx) => 
                                            `<span class="badge badge-success badge-lg mr-1 mb-1" title="Cyclical Rank ${idx + 1}">${num}</span>`
                                        ).join('')}
                                    </div>
                                </div>
                                <div class="tab-pane fade" id="method" role="tabpanel">
                                    <div class="prediction-numbers">
                                        ${methodNumbers.map((num, idx) => 
                                            `<span class="badge badge-warning badge-lg mr-1 mb-1" title="Method Rank ${idx + 1}">${num}</span>`
                                        ).join('')}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#intelligentPredictions').html(predictionHtml);
    }
    
    function updatePerformanceDashboard(performanceMetrics) {
        const expectedAccuracy = performanceMetrics.expected_accuracy || 0;
        const confidenceLevel = performanceMetrics.confidence_level || 'Unknown';
        const cyclicalStrength = performanceMetrics.cyclical_strength || 0;
        const performanceBreakdown = performanceMetrics.performance_breakdown || {};
        const riskAssessment = performanceMetrics.risk_assessment || {};
        
        const dashboardHtml = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-warning">
                        <div class="card-header bg-warning text-dark">
                            <h6 class="mb-0">📈 Performance Dashboard</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="text-center">
                                        <div class="display-4 text-${expectedAccuracy >= 50 ? 'success' : expectedAccuracy >= 30 ? 'warning' : 'danger'}">
                                            ${expectedAccuracy.toFixed(1)}%
                                        </div>
                                        <div class="small text-muted">Expected Accuracy</div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="text-center">
                                        <div class="badge badge-${confidenceLevel === 'High' ? 'success' : confidenceLevel === 'Medium' ? 'warning' : 'danger'} badge-lg">
                                            ${confidenceLevel}
                                        </div>
                                        <div class="small text-muted">Confidence Level</div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="text-center">
                                        <div class="progress" style="height: 25px;">
                                            <div class="progress-bar bg-info" role="progressbar" 
                                                style="width: ${(cyclicalStrength * 100)}%">
                                                ${(cyclicalStrength * 100).toFixed(1)}%
                                            </div>
                                        </div>
                                        <div class="small text-muted">Cyclical Strength</div>
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-md-12">
                                    <h6>Performance Breakdown:</h6>
                                    <div class="progress" style="height: 30px;">
                                        <div class="progress-bar bg-primary" style="width: ${performanceBreakdown.base_accuracy || 0}%" 
                                             title="Base Accuracy: ${performanceBreakdown.base_accuracy || 0}%">
                                            Base: ${(performanceBreakdown.base_accuracy || 0).toFixed(1)}%
                                        </div>
                                        <div class="progress-bar bg-success" style="width: ${performanceBreakdown.method_bonus || 0}%" 
                                             title="Method Bonus: ${performanceBreakdown.method_bonus || 0}%">
                                            Method: +${(performanceBreakdown.method_bonus || 0).toFixed(1)}%
                                        </div>
                                        <div class="progress-bar bg-info" style="width: ${performanceBreakdown.fusion_bonus || 0}%" 
                                             title="Fusion Bonus: ${performanceBreakdown.fusion_bonus || 0}%">
                                            Fusion: +${(performanceBreakdown.fusion_bonus || 0).toFixed(1)}%
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-md-4">
                                    <small><strong>Fatigue Risk:</strong> 
                                        <span class="badge badge-${riskAssessment.fatigue_risk === 'Low' ? 'success' : riskAssessment.fatigue_risk === 'Medium' ? 'warning' : 'danger'}">
                                            ${riskAssessment.fatigue_risk || 'Unknown'}
                                        </span>
                                    </small>
                                </div>
                                <div class="col-md-4">
                                    <small><strong>Data Quality:</strong> 
                                        <span class="badge badge-${riskAssessment.data_quality === 'Good' ? 'success' : 'warning'}">
                                            ${riskAssessment.data_quality || 'Unknown'}
                                        </span>
                                    </small>
                                </div>
                                <div class="col-md-4">
                                    <small><strong>Prediction Stability:</strong> 
                                        <span class="badge badge-${riskAssessment.prediction_stability === 'High' ? 'success' : riskAssessment.prediction_stability === 'Medium' ? 'warning' : 'danger'}">
                                            ${riskAssessment.prediction_stability || 'Unknown'}
                                        </span>
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#performanceDashboard').html(dashboardHtml);
    }
"""

# Template HTML structure for displaying cyclical intelligence
ENHANCED_TEMPLATE_HTML = """
<!-- ✅ CYCLICAL INTELLIGENCE DASHBOARD -->
<div class="container-fluid mt-3">
    <!-- Cyclical Context Section -->
    <div id="cyclicalContext"></div>
    
    <!-- Method Sync Matrix Section -->
    <div id="methodSyncMatrix"></div>
    
    <!-- Intelligent Predictions Section -->
    <div id="intelligentPredictions"></div>
    
    <!-- Performance Dashboard Section -->
    <div id="performanceDashboard"></div>
    
    <!-- Original cyclical table (enhanced) -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">📊 Cyclical Analysis Results</h6>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped" id="cyclicalTable">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Cyclical Numbers</th>
                                    <th>Method Numbers</th>
                                    <th>Fusion Numbers</th>
                                    <th>Expected Accuracy</th>
                                    <th>Confidence</th>
                                </tr>
                            </thead>
                            <tbody id="cyclicalTableBody">
                                <!-- Results will be populated here -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Enhanced CSS -->
<style>
.badge-lg {
    font-size: 0.9rem;
    padding: 0.5rem 0.75rem;
}

.prediction-numbers .badge {
    font-size: 1rem;
    padding: 0.5rem 0.75rem;
    margin: 0.25rem;
}

.display-4 {
    font-weight: bold;
}

.progress {
    border-radius: 0.375rem;
}

.card {
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.nav-tabs .nav-link {
    border: 1px solid transparent;
    border-top-left-radius: 0.375rem;
    border-top-right-radius: 0.375rem;
}

.tab-content {
    border: 1px solid #dee2e6;
    border-top: none;
    border-radius: 0 0 0.375rem 0.375rem;
    padding: 1rem;
}
</style>
"""

print("✅ Enhanced Template Integration Code Generated!")
print("📋 Features Added:")
print("   - Cyclical Context Display")
print("   - Method Sync Matrix Visualization")
print("   - Intelligent Predictions Tabs")
print("   - Performance Dashboard")
print("   - Risk Assessment Indicators")
print("   - Progress Bars and Visual Elements")
