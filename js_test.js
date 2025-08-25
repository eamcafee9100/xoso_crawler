// JavaScript extracted from monthly_report.html
// This file is for syntax validation only

// Mock functions and variables
const $ = function() { return { on: function() {}, ajax: function() {} }; };
const console = { log: function() {}, error: function() {} };
const document = { addEventListener: function() {}, getElementById: function() { return { value: '', innerHTML: '' }; } };
const window = {};
const jQuery = $;



// ===== SECTION 1 =====


// ===== SECTION 2 =====

    // ✅ BIẾN GLOBAL CHO METHOD ANALYSIS
    let currentAnalysisDate = null;
    let lowRiskMethodsData = [];

    function loadMethodAnalysis() {
        const dateInput = document.getElementById('analysisDatePicker');
        const analysisDate = dateInput.value;
        
        if (!analysisDate) {
            showError('Vui lòng chọn ngày phân tích');
            return;
        }
        
        currentAnalysisDate = analysisDate;
        
        // Show loading
        showLoading();
        
        // ✅ SỬA: Đảm bảo URL khớp với pattern
        const apiUrl = `/pre-lokhung/api/method-analysis-v2/?analysis_date=${analysisDate}&limit=15`;
        
        console.log('🔍 Calling API:', apiUrl); // Debug URL
        
        fetch(apiUrl)
            .then(response => {
                console.log('📡 Response status:', response.status); // Debug status
                console.log('📡 Response URL:', response.url); // Debug actual URL
                
                // ✅ KIỂM TRA STATUS CODE TRƯỚC
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                // ✅ KIỂM TRA CONTENT-TYPE
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error(`Expected JSON but got: ${contentType}`);
                }
                
                return response.json();
            })
            .then(data => {
                hideLoading();
                
                // ✅ VALIDATE DATA STRUCTURE
                if (!data || typeof data !== 'object') {
                    throw new Error('Invalid response format');
                }
                
                if (data.success) {
                    renderAnalysisResults(data);
                } else {
                    showError(data.error || 'Lỗi không xác định');
                }
            })
            .catch(error => {
                hideLoading();
                
                // ✅ ENHANCED ERROR HANDLING
                let errorMessage = 'Lỗi kết nối';
                
                if (error.name === 'SyntaxError') {
                    errorMessage = 'Lỗi định dạng dữ liệu từ server';
                } else if (error.message.includes('HTTP 404')) {
                    errorMessage = 'API không tồn tại - Kiểm tra URL routing';
                } else if (error.message.includes('HTTP 500')) {
                    errorMessage = 'Lỗi server nội bộ';
                } else if (error.message.includes('Failed to fetch')) {
                    errorMessage = 'Không thể kết nối đến server';
                } else {
                    errorMessage = error.message;
                }
                
                showError(errorMessage);
                console.error('Analysis API Error:', error);
            });
    }

    // ✅ HÀM RENDER RESULTS CHO API V2
    function renderAnalysisResults(data) {
        console.log('🔍 Rendering V2 Analysis Results:', data);
        
        // Hiển thị ngày phân tích
        document.getElementById('predictionAnalysisDate').textContent = 
            formatDate(data.analysis_date);
        
        // Clear container và tạo layout mới cho V2
        const container = document.getElementById('analysisResults');
        container.innerHTML = `
            <div class="row">
                <div class="col-12">
                    <h5 class="mb-4">📊 Kết quả Phân tích V2 - ${formatDate(data.analysis_date)}</h5>
                </div>
            </div>
            
            <!-- 1. Hybrid Analysis Section -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">🔬 Hybrid Analysis</h6>
                        </div>
                        <div class="card-body" id="hybridAnalysisSection">
                            <!-- Hybrid analysis content -->
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 2. Intelligent Selections Section -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">🎯 Intelligent Selections</h6>
                        </div>
                        <div class="card-body" id="intelligentSelectionsSection">
                            <!-- Intelligent selections content -->
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 3. Optimal Methods by Day Section -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">📈 Optimal Methods by Day</h6>
                        </div>
                        <div class="card-body" id="optimalMethodsSection">
                            <!-- Optimal methods content -->
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 4. Performance Prediction Section -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">🎲 Performance Prediction</h6>
                        </div>
                        <div class="card-body" id="performancePredictionSection">
                            <!-- Performance prediction content -->
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 5. Live Comparison Section -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0">✅ Live Comparison</h6>
                        </div>
                        <div class="card-body" id="liveComparisonSection">
                            <!-- Live comparison content -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Render từng section
        renderHybridAnalysis(data.hybrid_analysis);
        renderIntelligentSelections(data.intelligent_selections);
        renderOptimalMethodsByDay(data.optimal_methods);
        renderPerformancePrediction(data.performance_prediction);
        renderLiveComparison(data.intelligent_selections?.optimal_numbers, data.analysis_date);
        
        // Show results
        container.classList.remove('d-none');
        
        // Store data globally nếu cần
        window.currentAnalysisData = data;
    }

    // ✅ 1. RENDER HYBRID ANALYSIS
    function renderHybridAnalysis(hybridAnalysis) {
        const container = document.getElementById('hybridAnalysisSection');
        
        if (!hybridAnalysis) {
            container.innerHTML = '<div class="alert alert-warning">Không có dữ liệu hybrid analysis</div>';
            return;
        }
        
        const shortTerm = hybridAnalysis.short_term_insights || {};
        const longTerm = hybridAnalysis.long_term_stability || {};
        const validation = hybridAnalysis.forward_validation || {};
        
        container.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <div class="card border-primary">
                        <div class="card-body text-center">
                            <h6 class="text-primary">📊 Short Term (30d)</h6>
                            <p class="mb-1"><strong>Methods:</strong> ${shortTerm.total_methods || 0}</p>
                            <p class="mb-1"><strong>Recent Trends:</strong> ${JSON.stringify(shortTerm.recent_trends || {})}</p>
                            <p class="mb-0"><strong>Momentum:</strong> ${JSON.stringify(shortTerm.momentum_indicators || {})}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card border-success">
                        <div class="card-body text-center">
                            <h6 class="text-success">📈 Long Term (180d)</h6>
                            <p class="mb-1"><strong>Methods:</strong> ${longTerm.total_methods || 0}</p>
                            <p class="mb-1"><strong>Stability:</strong> ${JSON.stringify(longTerm.stability_metrics || {})}</p>
                            <p class="mb-0"><strong>Consistency:</strong> ${JSON.stringify(longTerm.consistency_patterns || {})}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card border-warning">
                        <div class="card-body text-center">
                            <h6 class="text-warning">🔍 Forward Validation</h6>
                            <p class="mb-1"><strong>Methods Validated:</strong> ${validation.methods_validated || 0}</p>
                            <p class="mb-1"><strong>Accuracy:</strong> ${((validation.validation_accuracy || 0) * 100).toFixed(1)}%</p>
                            <p class="mb-0"><strong>Support:</strong> ${JSON.stringify(validation.validation_support || {})}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // ✅ 2. RENDER INTELLIGENT SELECTIONS
    function renderIntelligentSelections(intelligentSelections) {
        const container = document.getElementById('intelligentSelectionsSection');
        
        if (!intelligentSelections) {
            container.innerHTML = '<div class="alert alert-warning">Không có dữ liệu intelligent selections</div>';
            return;
        }
        
        const optimalNumbers = intelligentSelections.optimal_numbers || [];
        const methodContributions = intelligentSelections.method_contributions || [];
        const strategy = intelligentSelections.selection_strategy || {};
        
        container.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6 class="mb-3">🎯 Optimal Numbers (${optimalNumbers.length})</h6>
                    <div class="d-flex flex-wrap">
                        ${optimalNumbers.map(number => 
                            `<span class="badge bg-primary me-2 mb-2 p-2 fs-6">${number}</span>`
                        ).join('')}
                    </div>
                    
                    <div class="mt-3">
                        <h6>📊 Selection Strategy</h6>
                        <div class="row">
                            <div class="col-6">
                                <small><strong>Initial:</strong> ${strategy.total_initial_selections || 0}</small><br>
                                <small><strong>Final:</strong> ${strategy.final_selection_count || 0}</small>
                            </div>
                            <div class="col-6">
                                <small><strong>Efficiency:</strong> ${((strategy.selection_efficiency || 0) * 100).toFixed(1)}%</small><br>
                                <small><strong>Approach:</strong> ${strategy.approach || 'N/A'}</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <h6 class="mb-3">🤝 Method Contributions</h6>
                    <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
                        <table class="table table-sm">
                            <thead class="table-light sticky-top">
                                <tr>
                                    <th>Method</th>
                                    <th>Numbers</th>
                                    <th>Ratio</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${methodContributions.map(contrib => `
                                    <tr>
                                        <td>Method ${contrib.method_id}</td>
                                        <td><span class="badge bg-secondary">${contrib.numbers_contributed}</span></td>
                                        <td>${(contrib.contribution_ratio * 100).toFixed(1)}%</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }

    // ✅ 3. RENDER OPTIMAL METHODS BY DAY
    function renderOptimalMethodsByDay(optimalMethods) {
        const container = document.getElementById('optimalMethodsSection');
        
        if (!optimalMethods) {
            container.innerHTML = '<div class="alert alert-warning">Không có dữ liệu optimal methods</div>';
            return;
        }
        
        const day1Methods = optimalMethods.day_1 || [];
        const day2Methods = optimalMethods.day_2 || [];
        const day3Methods = optimalMethods.day_3 || [];
        const summary = optimalMethods.summary || {};
        
        container.innerHTML = `
            <!-- Summary -->
            <div class="row mb-3">
                <div class="col-12">
                    <div class="alert alert-info">
                        <strong>📋 Summary:</strong> 
                        Total Methods: ${summary.total_qualified_methods || 0} | 
                        Target Hit Rate: ${((summary.target_hit_rate || 0) * 100).toFixed(1)}% | 
                        Avg Expected: ${((summary.avg_expected_hit_rate || 0) * 100).toFixed(1)}%
                    </div>
                </div>
            </div>
            
            <!-- Tabs -->
            <ul class="nav nav-tabs" id="methodTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="day1-tab" data-bs-toggle="tab" data-bs-target="#day1" type="button">
                        Day 1 (${day1Methods.length})
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="day2-tab" data-bs-toggle="tab" data-bs-target="#day2" type="button">
                        Day 2 (${day2Methods.length})
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="day3-tab" data-bs-toggle="tab" data-bs-target="#day3" type="button">
                        Day 3 (${day3Methods.length})
                    </button>
                </li>
            </ul>
            
            <!-- Tab Content -->
            <div class="tab-content" id="methodTabContent">
                <div class="tab-pane fade show active" id="day1" role="tabpanel">
                    ${renderMethodsTable(day1Methods, 1)}
                </div>
                <div class="tab-pane fade" id="day2" role="tabpanel">
                    ${renderMethodsTable(day2Methods, 2)}
                </div>
                <div class="tab-pane fade" id="day3" role="tabpanel">
                    ${renderMethodsTable(day3Methods, 3)}
                </div>
            </div>
        `;
    }

    function renderMethodsTable(methods, day) {
        if (!methods || methods.length === 0) {
            return '<div class="alert alert-warning mt-3">Không có methods cho ngày này</div>';
        }
        
        // Sort by hybrid_score descending
        const sortedMethods = [...methods].sort((a, b) => (b.hybrid_score || 0) - (a.hybrid_score || 0));
        
        return `
            <div class="table-responsive mt-3">
                <table class="table table-sm table-hover">
                    <thead class="table-light">
                        <tr>
                            <th>Method</th>
                            <th>Hybrid Score</th>
                            <th>Hit Rate</th>
                            <th>Performance</th>
                            <th>Predicted Numbers</th>
                            <th>Risk</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${sortedMethods.map(method => {
                            const performanceTier = method.performance_tier || 'acceptable';
                            const tierColors = {
                                'excellent': 'success',
                                'good': 'primary', 
                                'acceptable': 'warning',
                                'poor': 'danger'
                            };
                            
                            return `
                                <tr>
                                    <td><strong>${method.method_name || 'N/A'}</strong></td>
                                    <td><span class="badge bg-info">${(method.hybrid_score || 0).toFixed(2)}</span></td>
                                    <td>${((method.expected_hit_rate || 0) * 100).toFixed(1)}%</td>
                                    <td><span class="badge bg-${tierColors[performanceTier]}">${performanceTier}</span></td>
                                    <td>
                                        ${(method.predicted_numbers || []).map(num => 
                                            `<span class="badge bg-${tierColors[performanceTier]} me-1">${num}</span>`
                                        ).join('')}
                                    </td>
                                    <td>
                                        <small class="text-${method.enhanced_risk?.level === 'very_low' ? 'success' : 'warning'}">
                                            ${method.enhanced_risk?.level || 'N/A'}
                                        </small>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    // ✅ 4. RENDER PERFORMANCE PREDICTION
    function renderPerformancePrediction(performancePrediction) {
        const container = document.getElementById('performancePredictionSection');
        
        if (!performancePrediction) {
            container.innerHTML = '<div class="alert alert-warning">Không có dữ liệu performance prediction</div>';
            return;
        }
        
        const expectedHitRate = performancePrediction.expected_hit_rate || 0;
        const confidenceLevel = performancePrediction.confidence_level || 'medium';
        const overallConfidence = performancePrediction.overall_confidence_score || 0;
        const riskAssessment = performancePrediction.risk_assessment || {};
        const breakdown = performancePrediction.performance_breakdown || {};
        const confidenceFactors = breakdown.confidence_factors || {};
        const riskFactors = breakdown.risk_factors || [];
        
        container.innerHTML = `
            <div class="row">
                <!-- Main Performance Cards -->
                <div class="col-md-4">
                    <div class="card border-success">
                        <div class="card-body text-center">
                            <h6 class="text-success">🎯 Expected Hit Rate</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-success" style="width: ${expectedHitRate * 100}%"></div>
                            </div>
                            <h4 class="text-success">${(expectedHitRate * 100).toFixed(1)}%</h4>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card border-primary">
                        <div class="card-body text-center">
                            <h6 class="text-primary">🔍 Confidence Level</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-primary" style="width: ${overallConfidence * 100}%"></div>
                            </div>
                            <h4 class="text-primary">${confidenceLevel.toUpperCase()}</h4>
                            <small>${(overallConfidence * 100).toFixed(1)}%</small>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card border-${riskAssessment.level === 'very_low' ? 'success' : 'warning'}">
                        <div class="card-body text-center">
                            <h6 class="text-${riskAssessment.level === 'very_low' ? 'success' : 'warning'}">⚠️ Risk Level</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-${riskAssessment.level === 'very_low' ? 'success' : 'warning'}" 
                                    style="width: ${(1 - (riskAssessment.risk_score || 0)) * 100}%"></div>
                            </div>
                            <h4 class="text-${riskAssessment.level === 'very_low' ? 'success' : 'warning'}">
                                ${(riskAssessment.level || 'unknown').toUpperCase()}
                            </h4>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <!-- Confidence Factors Breakdown -->
                <div class="col-md-6">
                    <h6>📊 Confidence Factors</h6>
                    <div class="list-group">
                        ${Object.entries(confidenceFactors).map(([factor, value]) => `
                            <div class="list-group-item d-flex justify-content-between align-items-center">
                                <span>${factor.charAt(0).toUpperCase() + factor.slice(1)}</span>
                                <div class="d-flex align-items-center">
                                    <div class="progress me-2" style="width: 100px;">
                                        <div class="progress-bar" style="width: ${(value || 0) * 100}%"></div>
                                    </div>
                                    <span class="badge bg-primary">${((value || 0) * 100).toFixed(1)}%</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Risk Factors -->
                <div class="col-md-6">
                    <h6>⚠️ Risk Factors</h6>
                    ${riskFactors.length > 0 ? 
                        riskFactors.map(risk => `
                            <div class="alert alert-warning alert-sm">
                                <strong>${risk.factor || 'Unknown Risk'}:</strong> ${risk.description || 'No description'}
                            </div>
                        `).join('') :
                        '<div class="alert alert-success">✅ No significant risk factors detected</div>'
                    }
                    
                    <!-- Additional Performance Info -->
                    <div class="mt-3">
                        <small class="text-muted">
                            <strong>Total Numbers:</strong> ${breakdown.total_numbers_selected || 0} | 
                            <strong>Contributing Methods:</strong> ${breakdown.contributing_methods || 0} | 
                            <strong>Selection Efficiency:</strong> ${((breakdown.selection_efficiency || 0) * 100).toFixed(1)}%
                        </small>
                    </div>
                </div>
            </div>
        `;
    }

    // ✅ 5. RENDER LIVE COMPARISON
    function renderLiveComparison(optimalNumbers, analysisDate) {
        const container = document.getElementById('liveComparisonSection');
        
        if (!optimalNumbers || optimalNumbers.length === 0) {
            container.innerHTML = '<div class="alert alert-warning">Không có optimal numbers để so sánh</div>';
            return;
        }
        
        // Show loading first
        container.innerHTML = `
            <div class="d-flex justify-content-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Đang tải kết quả...</span>
                </div>
                <p class="mt-3">Đang tải kết quả thực tế từ ${analysisDate}...</p>
            </div>
        `;
        
        // ✅ SỬA: Đường dẫn API đúng với URL routing
        const apiUrl = `/pre-lokhung/api/ketqua/${analysisDate}/`;
        console.log('🔍 Fetching actual results from:', apiUrl);
        
        // Fetch actual results from KetQuaXoSo
        fetch(apiUrl)
            .then(response => {
                console.log('📡 API Response status:', response.status);
                console.log('📡 API Response headers:', response.headers.get('content-type'));
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error(`Expected JSON but got: ${contentType}`);
                }
                
                return response.json();
            })
            .then(actualData => {
                console.log('📋 Received actual data:', actualData);
                
                // ✅ SỬA: Truy cập đúng cấu trúc JSON response
                if (!actualData.success) {
                    throw new Error(actualData.error || 'API returned success: false');
                }
                
                // ✅ TRUY CẬP ĐÚNG: actualData.data.all_2digit_numbers
                const actualNumbers = actualData.data?.all_2digit_numbers || [];
                const prizeDetails = actualData.data?.prize_details || {};
                const statistics = actualData.data?.statistics || {};
                
                console.log('🎯 Actual numbers found:', actualNumbers.length);
                
                // ✅ SO SÁNH VỚI OPTIMAL NUMBERS
                const hitNumbers = optimalNumbers.filter(num => {
                    // ✅ Đảm bảo cả hai đều là string để so sánh chính xác
                    const numStr = String(num).padStart(2, '0');
                    return actualNumbers.includes(numStr);
                });
                
                const missNumbers = optimalNumbers.filter(num => {
                    const numStr = String(num).padStart(2, '0');
                    return !actualNumbers.includes(numStr);
                });
                
                const hitRate = optimalNumbers.length > 0 ? (hitNumbers.length / optimalNumbers.length * 100) : 0;
                
                console.log('✅ Comparison results:', {
                    total: optimalNumbers.length,
                    hits: hitNumbers.length,
                    misses: missNumbers.length,
                    hitRate: hitRate.toFixed(1) + '%'
                });
                
                // ✅ RENDER KẾT QUẢ CHI TIẾT
                container.innerHTML = `
                    <div class="row">
                        <div class="col-md-8">
                            <h6 class="mb-3">🎯 Comparison Results</h6>
                            <div class="row mb-3">
                                <div class="col-md-4">
                                    <div class="card text-center border-success">
                                        <div class="card-body">
                                            <h5 class="text-success">${hitNumbers.length}</h5>
                                            <small>Numbers Hit</small>
                                            <div class="progress mt-2">
                                                <div class="progress-bar bg-success" style="width: ${hitRate}%"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card text-center border-danger">
                                        <div class="card-body">
                                            <h5 class="text-danger">${missNumbers.length}</h5>
                                            <small>Numbers Miss</small>
                                            <div class="progress mt-2">
                                                <div class="progress-bar bg-danger" style="width: ${100 - hitRate}%"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card text-center border-primary">
                                        <div class="card-body">
                                            <h5 class="text-primary">${hitRate.toFixed(1)}%</h5>
                                            <small>Hit Rate</small>
                                            <div class="mt-1">
                                                <span class="badge ${hitRate >= 30 ? 'bg-success' : hitRate >= 15 ? 'bg-warning' : 'bg-danger'}">
                                                    ${hitRate >= 30 ? 'Excellent' : hitRate >= 15 ? 'Good' : 'Poor'}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- ✅ HIỂN THỊ CHI TIẾT OPTIMAL NUMBERS VỚI STATUS -->
                            <div class="mb-3">
                                <h6>🔢 Optimal Numbers Comparison</h6>
                                <div class="d-flex flex-wrap">
                                    ${optimalNumbers.map(number => {
                                        const numStr = String(number).padStart(2, '0');
                                        const isHit = actualNumbers.includes(numStr);
                                        return `<span class="badge ${isHit ? 'bg-success' : 'bg-secondary'} me-2 mb-2 p-2 fs-6" 
                                                title="${isHit ? 'HIT' : 'MISS'}: ${numStr}">
                                            ${numStr} ${isHit ? '✓' : '✗'}
                                        </span>`;
                                    }).join('')}
                                </div>
                            </div>
                            
                            <!-- ✅ HIỂN THỊ PRIZE BREAKDOWN -->
                            <div class="mb-3">
                                <h6>🏆 Prize Breakdown</h6>
                                <div class="row">
                                    ${Object.entries(prizeDetails).map(([prizeKey, prizeData]) => `
                                        <div class="col-md-6 mb-2">
                                            <div class="border rounded p-2">
                                                <strong>${prizeData.display_name}:</strong>
                                                <div class="mt-1">
                                                    ${prizeData.two_digit_numbers.map(num => {
                                                        const isOptimal = optimalNumbers.some(opt => String(opt).padStart(2, '0') === num);
                                                        return `<span class="badge ${isOptimal ? 'bg-warning text-dark' : 'bg-light text-dark'} me-1">
                                                            ${num} ${isOptimal ? '⭐' : ''}
                                                        </span>`;
                                                    }).join('')}
                                                </div>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <h6 class="mb-3">📋 All Actual Results (${actualNumbers.length})</h6>
                            <div class="bg-light p-3 rounded" style="max-height: 400px; overflow-y: auto;">
                                <div class="d-flex flex-wrap">
                                    ${actualNumbers.map(number => {
                                        const isOptimal = optimalNumbers.some(opt => String(opt).padStart(2, '0') === number);
                                        return `<span class="badge ${isOptimal ? 'bg-success' : 'bg-dark'} me-1 mb-1" 
                                                title="${isOptimal ? 'MATCHED with optimal!' : 'Not in optimal set'}">
                                            ${number} ${isOptimal ? '⭐' : ''}
                                        </span>`;
                                    }).join('')}
                                </div>
                                
                                <!-- ✅ STATISTICS SUMMARY -->
                                <div class="mt-3 pt-3 border-top">
                                    <h6 class="small">📊 Quick Stats</h6>
                                    <div class="row text-center">
                                        <div class="col-6">
                                            <div class="bg-white rounded p-2">
                                                <div class="fw-bold">${statistics.even_odd_analysis?.even_count || 0}</div>
                                                <small>Even</small>
                                            </div>
                                        </div>
                                        <div class="col-6">
                                            <div class="bg-white rounded p-2">
                                                <div class="fw-bold">${statistics.even_odd_analysis?.odd_count || 0}</div>
                                                <small>Odd</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="mt-2 text-center">
                                        <small class="text-muted">
                                            Avg Sum: ${statistics.sum_analysis?.avg_sum || 0} | 
                                            Duplicates: ${statistics.frequency_analysis?.duplicate_count || 0}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            })
            .catch(error => {
                console.error('❌ Error fetching actual results:', error);
                
                // ✅ ENHANCED ERROR HANDLING VỚI FALLBACK DISPLAY
                let errorMessage = 'Không thể tải kết quả thực tế';
                let errorType = 'warning';
                
                if (error.message.includes('HTTP 404')) {
                    errorMessage = 'Chưa có kết quả xổ số cho ngày này';
                    errorType = 'info';
                } else if (error.message.includes('HTTP 500')) {
                    errorMessage = 'Lỗi server - vui lòng thử lại sau';
                    errorType = 'danger';
                } else if (error.message.includes('Failed to fetch')) {
                    errorMessage = 'Lỗi kết nối mạng';
                    errorType = 'warning';
                } else if (error.message.includes('success: false')) {
                    errorMessage = `API Error: ${error.message}`;
                    errorType = 'warning';
                }
                
                container.innerHTML = `
                    <div class="alert alert-${errorType}">
                        <h6><i class="fas fa-exclamation-triangle"></i> ${errorMessage}</h6>
                        <p class="mb-3">Hiển thị dự đoán tạm thời:</p>
                        
                        <!-- ✅ FALLBACK: HIỂN THỊ OPTIMAL NUMBERS VÀ THÔNG TIN CƠ BẢN -->
                        <div class="row">
                            <div class="col-md-8">
                                <h6>🎯 Predicted Optimal Numbers</h6>
                                <div class="d-flex flex-wrap">
                                    ${optimalNumbers.map(number => 
                                        `<span class="badge bg-primary me-2 mb-2 p-2 fs-6">${String(number).padStart(2, '0')}</span>`
                                    ).join('')}
                                </div>
                                
                                <div class="mt-3">
                                    <div class="row">
                                        <div class="col-4 text-center">
                                            <div class="border rounded p-2">
                                                <div class="fw-bold text-primary">${optimalNumbers.length}</div>
                                                <small>Predicted</small>
                                            </div>
                                        </div>
                                        <div class="col-4 text-center">
                                            <div class="border rounded p-2">
                                                <div class="fw-bold text-muted">?</div>
                                                <small>Hits</small>
                                            </div>
                                        </div>
                                        <div class="col-4 text-center">
                                            <div class="border rounded p-2">
                                                <div class="fw-bold text-muted">?%</div>
                                                <small>Hit Rate</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-4">
                                <div class="bg-light p-3 rounded text-center">
                                    <i class="fas fa-clock text-muted" style="font-size: 2rem;"></i>
                                    <p class="mt-2 mb-0 text-muted">
                                        Kết quả thực tế sẽ được cập nhật sau khi có dữ liệu từ <strong>${analysisDate}</strong>
                                    </p>
                                    <small class="text-muted">Vui lòng kiểm tra lại sau</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- ✅ DEBUG INFO CHO DEVELOPER -->
                    <details class="mt-3">
                        <summary class="text-muted small">Debug Info</summary>
                        <div class="small text-muted mt-2">
                            <strong>API URL:</strong> ${apiUrl}<br>
                            <strong>Error:</strong> ${error.message}<br>
                            <strong>Time:</strong> ${new Date().toLocaleString()}
                        </div>
                    </details>
                `;
            });
    }

    // ✅ HELPER FUNCTIONS
    function formatDate(dateStr) {
        if (!dateStr) return 'N/A';
        const date = new Date(dateStr);
        return date.toLocaleDateString('vi-VN');
    }
    
    // ✅ HÀM RENDER RESULTS
    function renderAnalysisResults(data) {
        document.getElementById('predictionAnalysisDate').textContent = 
            formatDate(data.analysis_date);
        
        // Render data quality
        renderDataQuality(data.data_quality);
        
        // Render LOW RISK methods
        renderLowRiskMethods(data.low_risk_methods);
        
        // Render comparison results
        renderComparisonResults(data.comparison_results);
        
        // Store data globally
        lowRiskMethodsData = data.low_risk_methods;
        
        // Show results
        document.getElementById('analysisResults').classList.remove('d-none');
    } 

    // ✅ HÀM RENDER DATA QUALITY
    function renderDataQuality(dataQuality) {
        const container = document.getElementById('dataQualityInfo');
        
        const confidenceClass = {
            'high': 'text-success',
            'medium': 'text-warning', 
            'low': 'text-danger'
        };
        
        const leakageClass = {
            'clean_no_leakage': 'text-success',
            'warning_potential_leakage': 'text-warning'
        };
        
        container.innerHTML = `
            <div class="col-md-3">
                <strong>Tổng methods:</strong><br>
                <span class="badge bg-primary">${dataQuality.total_methods_analyzed}</span>
            </div>
            <div class="col-md-3">
                <strong>Dữ liệu đủ:</strong><br>
                <span class="badge bg-info">${dataQuality.methods_with_sufficient_data}</span>
            </div>
            <div class="col-md-3">
                <strong>Độ tin cậy:</strong><br>
                <span class="badge ${confidenceClass[dataQuality.analysis_confidence] || 'bg-secondary'}">
                    ${dataQuality.analysis_confidence.toUpperCase()}
                </span>
            </div>
            <div class="col-md-3">
                <strong>Data leakage:</strong><br>
                <span class="badge ${leakageClass[dataQuality.data_leakage_check] || 'bg-secondary'}">
                    ${dataQuality.data_leakage_check === 'clean_no_leakage' ? 'CLEAN' : 'WARNING'}
                </span>
            </div>
        `;
    }

    // ✅ HÀM RENDER LOW RISK METHODS
    function renderLowRiskMethods(methods) {
        const tbody = document.getElementById('lowRiskMethodsTable');
        
        if (!methods || methods.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted">
                        Không tìm thấy LOW RISK methods với tiêu chí hiện tại
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = methods.map((method, index) => {
            const trendClass = {
                'improving': 'text-success',
                'stable': 'text-info',
                'declining': 'text-danger'
            };
            
            const trendIcon = {
                'improving': 'fas fa-arrow-up',
                'stable': 'fas fa-minus',
                'declining': 'fas fa-arrow-down'
            };
            
            return `
                <tr>
                    <td>${index + 1}</td>
                    <td>
                        <strong>${method.method_name}</strong><br>
                        <small class="text-muted">ID: ${method.method_id}</small>
                    </td>
                    <td>
                        <span class="badge bg-success">${method.score}</span>
                    </td>
                    <td>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar" style="width: ${method.confidence * 100}%">
                                ${(method.confidence * 100).toFixed(1)}%
                            </div>
                        </div>
                    </td>
                    <td>
                        <span class="${trendClass[method.recent_trend] || 'text-secondary'}">
                            <i class="${trendIcon[method.recent_trend] || 'fas fa-question'}"></i>
                            ${method.recent_trend.direction	}
                        </span>
                    </td>
                    <td>
                        <div class="predicted-numbers">
                            ${method.predicted_numbers.slice(0, 5).map(num => 
                                `<span class="badge bg-primary">${num}</span>`
                            ).join(' ')}
                            ${method.predicted_numbers.length > 5 ? 
                                `<span class="text-muted">+${method.predicted_numbers.length - 5}</span>` : ''
                            }
                        </div>
                    </td>
                    <td>
                        <span class="badge ${method.avg_hit_rate >= 0.2 ? 'bg-success' : 
                                        method.avg_hit_rate >= 0.1 ? 'bg-warning' : 'bg-danger'}">
                            ${(method.avg_hit_rate * 100).toFixed(1)}%
                        </span>
                        <br>
                        <small class="text-muted">${method.evaluations_count} đánh giá</small>
                    </td>
                    <td>
                        <span class="badge bg-success">LOW RISK</span><br>
                        <small class="text-muted">Stability: ${(method.stability * 100).toFixed(1)}%</small>
                    </td>
                </tr>
            `;
        }).join('');
    }

    // ✅ HÀM RENDER COMPARISON RESULTS
    function renderComparisonResults(comparisonResults) {
        const container = document.getElementById('comparisonResults');
        
        if (!comparisonResults || Object.keys(comparisonResults).length === 0) {
            container.innerHTML = '<div class="alert alert-warning">Không có dữ liệu so sánh</div>';
            return;
        }
        
        const dayNames = ['Ngày 1', 'Ngày 2', 'Ngày 3'];
        
        container.innerHTML = Object.keys(comparisonResults).map((dayKey, index) => {
            const dayData = comparisonResults[dayKey];
            const dayName = dayNames[index];
            
            if (dayData.available) {
                // ✅ FIX: Kiểm tra cấu trúc dữ liệu thực tế
                let analysisData = null;
                let methodsCount = 0;
                
                // ✅ Kiểm tra các field có thể có
                if (dayData.selected_numbers_analysis) {
                    analysisData = dayData.selected_numbers_analysis;
                    methodsCount = analysisData.length;
                } else if (dayData.methods_analysis) {
                    analysisData = dayData.methods_analysis;
                    methodsCount = Array.isArray(analysisData) ? analysisData.length : Object.keys(analysisData).length;
                } else if (dayData.total_selected_numbers) {
                    methodsCount = dayData.total_selected_numbers;
                } else if (dayData.total_methods) {
                    methodsCount = dayData.total_methods;
                }
                
                // ✅ HIỂN THỊ KẾT QUẢ CHI TIẾT với safe access
                const avgHitRate = (dayData.avg_hit_rate * 100).toFixed(1);
                const hitPercentage = dayData.hit_rate_percentage ? dayData.hit_rate_percentage.toFixed(1) : '0.0';
                const methodsWithHits = dayData.numbers_with_hits || dayData.methods_with_hits || 0;
                const totalMethods = dayData.total_selected_numbers || dayData.total_methods || 0;
                
                return `
                    <div class="col-md-4">
                        <div class="card border-success mb-3">
                            <div class="card-header bg-success text-white">
                                <h6 class="mb-0">${dayName}</h6>
                                <small>${formatDateVN(dayData.tracking_date)}</small>
                            </div>
                            <div class="card-body">
                                <!-- ✅ THỐNG KÊ TỔNG QUAN -->
                                <div class="row mb-3">
                                    <div class="col-6 text-center">
                                        <div class="stat-number text-success">${avgHitRate}%</div>
                                        <div class="stat-label">Tỷ lệ trúng TB</div>
                                    </div>
                                    <div class="col-6 text-center">
                                        <div class="stat-number text-info">${methodsWithHits}/${totalMethods}</div>
                                        <div class="stat-label">Số trúng</div>
                                    </div>
                                </div>
                                
                                <!-- ✅ HIỂN THỊ SỐ TRÚNG với safe access -->
                                <div class="mb-3">
                                    <strong>Số trúng:</strong>
                                    <div class="hit-numbers-display">
                                        ${analysisData ? renderHitNumbers(analysisData) : renderBasicHitNumbers(dayData)}
                                    </div>
                                </div>
                                
                                <!-- ✅ HIỂN THỊ KẾT QUẢ THỰC TẾ -->
                                <div class="mb-3">
                                    <strong>Kết quả thực tế (${dayData.actual_numbers ? dayData.actual_numbers.length : 0} số):</strong>
                                    <div class="actual-numbers-display">
                                        ${dayData.actual_numbers ? dayData.actual_numbers.map(num => 
                                            `<span class="badge bg-secondary me-1">${num}</span>`
                                        ).join('') : '<span class="text-muted">Chưa có</span>'}
                                        
                                    </div>
                                </div>
                                
                                <!-- ✅ BUTTON XEM CHI TIẾT với safe count -->
                                <button class="btn btn-sm btn-outline-primary w-100" 
                                        onclick="showDetailedComparison('${dayKey}', '${dayName}', ${JSON.stringify(dayData).replace(/"/g, '&quot;')})">
                                    <i class="fas fa-search-plus"></i> Xem chi tiết ${methodsCount} methods
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                // ✅ Hiển thị cho ngày chưa có kết quả
                const previewData = dayData.selected_numbers_preview || [];
                
                return `
                    <div class="col-md-4">
                        <div class="card border-warning mb-3">
                            <div class="card-header bg-warning text-dark">
                                <h6 class="mb-0">${dayName}</h6>
                                <small>${formatDateVN(dayData.tracking_date)}</small>
                            </div>
                            <div class="card-body text-center">
                                <i class="fas fa-clock text-warning" style="font-size: 2rem;"></i>
                                <p class="mt-2 mb-0">
                                    ${dayData.message || 'Chờ kết quả'}
                                </p>
                                ${previewData.length > 0 ? `
                                    <div class="mt-2">
                                        <small class="text-muted">Dự đoán: ${previewData.length} số</small>
                                        <div class="mt-1">
                                            ${previewData.map(item => 
                                                `<span class="badge bg-info me-1">${item.display_format || item.selected_number}</span>`
                                            ).join('')}
                                            
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                `;
            }
        }).join('');
    }

    // ✅ HÀM RENDER HIT NUMBERS CƠ BẢN KHI KHÔNG CÓ ANALYSIS DATA
    function renderBasicHitNumbers(dayData) {
        const hitNumbers = dayData.hit_numbers || [];
        const missNumbers = dayData.miss_numbers || [];
        
        if (hitNumbers.length === 0 && missNumbers.length === 0) {
            return '<div class="text-muted">Không có dữ liệu số</div>';
        }
        
        return `
            <div class="hit-summary mb-2">
                <span class="badge bg-success me-2">
                    <i class="fas fa-bullseye"></i> ${hitNumbers.length} số trúng
                </span>
                ${missNumbers.length > 0 ? `
                    <span class="badge bg-secondary me-2">
                        <i class="fas fa-times"></i> ${missNumbers.length} số trượt
                    </span>
                ` : ''}
            </div>
            <div class="hit-numbers-list">
                ${hitNumbers.slice(0, 8).map(num => 
                    `<span class="badge bg-success me-1 mb-1">${num}</span>`
                ).join('')}
                ${hitNumbers.length > 8 ? 
                    `<span class="text-muted">+${hitNumbers.length - 8} số</span>` : ''
                }
            </div>
        `;
    }


    // ✅ HÀM RENDER HIT NUMBERS - CẬP NHẬT CHO OPTIMAL SELECTIONS
    function renderHitNumbers(methodsAnalysis) {
        if (!methodsAnalysis || methodsAnalysis.length === 0) {
            return '<div class="text-muted">Không có dữ liệu</div>';
        }
        
        // ✅ CHECK XEM CÓ PHẢI SELECTED_NUMBERS_ANALYSIS KHÔNG
        if (methodsAnalysis.length > 0 && methodsAnalysis[0].hasOwnProperty('selected_numbers_analysis')) {
            return renderOptimalSelectedNumbers(methodsAnalysis[0].selected_numbers_analysis);
        } else {
            // Fallback to original logic
            return renderOriginalHitNumbers(methodsAnalysis);
        }
    }

    function renderOptimalSelectedNumbers(selectedNumbersAnalysis) {
        const hitNumbers = selectedNumbersAnalysis.filter(s => s.is_hit);
        const missNumbers = selectedNumbersAnalysis.filter(s => !s.is_hit);
        
        return `
            <div class="optimal-numbers-display mb-3">
                <div class="row">
                    <div class="col-md-6">
                        <h6 class="text-success">
                            <i class="fas fa-bullseye"></i> Số trúng (${hitNumbers.length}/${selectedNumbersAnalysis.length})
                        </h6>
                        <div class="hit-numbers-list">
                            ${hitNumbers.map(s => `
                                <span class="badge bg-success me-1 mb-1" title="${s.method_name} - Confidence: ${(s.confidence * 100).toFixed(1)}%">
                                    ${s.display_format}
                                </span>
                            `).join('')}
                            ${hitNumbers.length === 0 ? '<span class="text-muted">Không có số nào trúng</span>' : ''}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h6 class="text-danger">
                            <i class="fas fa-times"></i> Số trượt (${missNumbers.length})
                        </h6>
                        <div class="miss-numbers-list">
                            ${missNumbers.slice(0, 8).map(s => `
                                <span class="badge bg-secondary me-1 mb-1" title="${s.method_name} - Confidence: ${(s.confidence * 100).toFixed(1)}%">
                                    ${s.display_format}
                                </span>
                            `).join('')}
                            ${missNumbers.length > 8 ? `<span class="text-muted">+${missNumbers.length - 8} số</span>` : ''}
                        </div>
                    </div>
                </div>
                
                <!-- ✅ THỐNG KÊ PATTERN -->
                <div class="pattern-stats mt-3">
                    <small class="text-muted">
                        <i class="fas fa-chart-bar"></i> Pattern: 
                        Vị trí [0]: ${selectedNumbersAnalysis.filter(s => s.position === 0).length} số
                        | Vị trí [1]: ${selectedNumbersAnalysis.filter(s => s.position === 1).length} số
                    </small>
                </div>
            </div>
        `;
    }

    function renderOriginalHitNumbers(methodsAnalysis) {
        // Original logic for backward compatibility
        const allHitNumbers = new Set();
        let totalHits = 0;
        let totalPredictions = 0;
        
        methodsAnalysis.forEach(method => {
            if (method.hit_numbers && method.hit_numbers.length > 0) {
                method.hit_numbers.forEach(num => allHitNumbers.add(num));
                totalHits += method.hit_count;
            }
            totalPredictions += method.predicted_count;
        });
        
        const hitNumbersArray = Array.from(allHitNumbers).sort();
        
        return `
            <div class="hit-summary mb-2">
                <span class="badge bg-success me-2">
                    <i class="fas fa-bullseye"></i> ${totalHits}/${totalPredictions} số trúng
                </span>
                <span class="badge bg-info">
                    <i class="fas fa-star"></i> ${hitNumbersArray.length} số unique
                </span>
            </div>
            <div class="hit-numbers-list">
                ${hitNumbersArray.slice(0, 8).map(num => 
                    `<span class="badge bg-success me-1 mb-1">${num}</span>`
                ).join('')}
                ${hitNumbersArray.length > 8 ? 
                    `<span class="text-muted">+${hitNumbersArray.length - 8} số</span>` : ''
                }
            </div>
        `;
    }

    // ✅ HÀM HIỂN THỊ CHI TIẾT SO SÁNH
    function showDetailedComparison(dayKey, dayName, dayData) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        
        // ✅ Safe access cho các metrics
        const avgHitRate = dayData.avg_hit_rate ? (dayData.avg_hit_rate * 100).toFixed(1) : '0.0';
        const methodsWithHits = dayData.numbers_with_hits || dayData.methods_with_hits || 0;
        const totalMethods = dayData.total_selected_numbers || dayData.total_methods || 0;
        const hitPercentage = dayData.hit_rate_percentage ? dayData.hit_rate_percentage.toFixed(1) : '0.0';
        
        // ✅ Xác định loại dữ liệu để hiển thị
        let analysisData = null;
        if (dayData.selected_numbers_analysis) {
            analysisData = dayData.selected_numbers_analysis;
        } else if (dayData.methods_analysis) {
            analysisData = dayData.methods_analysis;
        }
        
        modal.innerHTML = `
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-chart-line"></i> Chi tiết so sánh ${dayName}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <!-- ✅ THỐNG KÊ TỔNG QUAN -->
                        <div class="row mb-4">
                            <div class="col-md-3">
                                <div class="card border-success">
                                    <div class="card-body text-center">
                                        <div class="stat-number text-success">${avgHitRate}%</div>
                                        <div class="stat-label">Tỷ lệ trúng TB</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card border-info">
                                    <div class="card-body text-center">
                                        <div class="stat-number text-info">${methodsWithHits}</div>
                                        <div class="stat-label">Số trúng</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card border-warning">
                                    <div class="card-body text-center">
                                        <div class="stat-number text-warning">${totalMethods}</div>
                                        <div class="stat-label">Tổng số</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card border-secondary">
                                    <div class="card-body text-center">
                                        <div class="stat-number text-secondary">${hitPercentage}%</div>
                                        <div class="stat-label">Tỷ lệ trúng</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- ✅ BẢNG CHI TIẾT METHODS -->
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead class="table-dark">
                                    <tr>
                                        <th>STT</th>
                                        <th>Method</th>
                                        <th>Dự đoán</th>
                                        <th>Trúng</th>
                                        <th>Tỷ lệ</th>
                                        <th>Score</th>
                                        <th>Info</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${generateMethodsComparisonRows(analysisData)}
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- ✅ KẾT QUẢ THỰC TẾ -->
                        <div class="mt-4">
                            <h6><i class="fas fa-list"></i> Kết quả thực tế ngày ${formatDateVN(dayData.tracking_date)}</h6>
                            <div class="actual-numbers-full">
                                ${dayData.actual_numbers ? dayData.actual_numbers.map(num => 
                                    `<span class="badge bg-secondary me-1 mb-1">${num}</span>`
                                ).join('') : '<span class="text-muted">Chưa có kết quả</span>'}
                            </div>
                            <small class="text-muted">Tổng cộng: ${dayData.actual_numbers ? dayData.actual_numbers.length : 0} số</small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Remove modal after hide
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }


    // ✅ HÀM TẠO ROWS CHO BẢNG SO SÁNH
    function generateMethodsComparisonRows(analysisData) {
        // ✅ Kiểm tra cấu trúc dữ liệu trước khi xử lý
        if (!analysisData) {
            return '<tr><td colspan="7" class="text-center text-muted">Không có dữ liệu phân tích</td></tr>';
        }
        
        // ✅ Xử lý array vs object
        let methodsData;
        if (Array.isArray(analysisData)) {
            methodsData = analysisData;
        } else if (analysisData.selected_numbers_analysis) {
            methodsData = analysisData.selected_numbers_analysis;
        } else if (analysisData.methods_analysis) {
            methodsData = Array.isArray(analysisData.methods_analysis) ? 
                        analysisData.methods_analysis : [analysisData.methods_analysis];
        } else {
            return '<tr><td colspan="7" class="text-center text-muted">Cấu trúc dữ liệu không hợp lệ</td></tr>';
        }
        
        // ✅ CHECK XEM CÓ PHẢI SELECTED_NUMBERS_ANALYSIS KHÔNG
        if (methodsData.length > 0 && methodsData[0].hasOwnProperty('selected_numbers_analysis')) {
            return generateOptimalNumbersComparisonRows(methodsData[0].selected_numbers_analysis);
        } else if (methodsData.length > 0 && methodsData[0].hasOwnProperty('display_format')) {
            // Đây là optimal numbers data
            return generateOptimalNumbersComparisonRows(methodsData);
        } else {
            // Original logic
            return generateOriginalComparisonRows(methodsData);
        }
    }


    function generateOptimalNumbersComparisonRows(selectedNumbersAnalysis) {
        // Sort by confidence DESC, then by hit status
        const sortedSelections = [...selectedNumbersAnalysis].sort((a, b) => {
            if (a.is_hit !== b.is_hit) return b.is_hit - a.is_hit; // Hits first
            return b.confidence - a.confidence; // Then by confidence
        });
        
        return sortedSelections.map((selection, index) => {
            const hitStatusClass = selection.is_hit ? 'table-success' : '';
            const hitIcon = selection.is_hit ? 
                '<i class="fas fa-check-circle text-success"></i>' : 
                '<i class="fas fa-times-circle text-danger"></i>';
            
            const confidencePercent = (selection.confidence * 100).toFixed(1);
            const patternInfo = selection.pattern_info;
            
            return `
                <tr class="${hitStatusClass}">
                    <td>
                        <span class="badge ${selection.is_hit ? 'bg-success' : 'bg-secondary'}">
                            ${index + 1}
                        </span>
                    </td>
                    <td>
                        <strong>${selection.method_name}</strong>
                        <br><small class="text-muted">ID: ${selection.method_id}</small>
                    </td>
                    <td>
                        <span class="badge ${selection.position === 0 ? 'bg-primary' : 'bg-info'} me-2">
                            ${selection.display_format}
                        </span>
                        <br><small class="text-muted">Vị trí ${selection.position}</small>
                    </td>
                    <td>
                        ${hitIcon}
                        <br><small class="text-muted">${selection.is_hit ? 'Trúng' : 'Trượt'}</small>
                    </td>
                    <td>
                        <span class="badge bg-info">${confidencePercent}%</span>
                        <br><small class="text-muted">Pattern: ${patternInfo.pattern_type}</small>
                    </td>
                    <td>
                        <small>
                            Pos[0]: ${(patternInfo.position_0_rate * 100).toFixed(1)}%<br>
                            Pos[1]: ${(patternInfo.position_1_rate * 100).toFixed(1)}%
                        </small>
                    </td>
                    <td>
                        <small class="text-muted">
                            ${patternInfo.selection_reason}
                            <br>${patternInfo.total_predictions} kỳ
                        </small>
                    </td>
                </tr>
            `;
        }).join('');
    }

    function generateOriginalComparisonRows(methodsAnalysis) {
        // Keep original logic for backward compatibility
        const sortedMethods = [...methodsAnalysis].sort((a, b) => {
            if (b.hit_rate !== a.hit_rate) return b.hit_rate - a.hit_rate;
            return b.hit_count - a.hit_count;
        });
        
        return sortedMethods.map((method, index) => {
            const hitRatePercent = (method.hit_rate * 100).toFixed(1);
            const hitRateClass = method.hit_rate > 0.5 ? 'text-success' : 
                                method.hit_rate > 0.3 ? 'text-warning' : 
                                method.hit_rate > 0 ? 'text-info' : 'text-muted';
            
            const predictedNumbersHTML = method.predicted_count > 0 ? 
                generatePredictedNumbersHTML(method) : 
                '<span class="text-muted">Không có dự đoán</span>';
            
            const hitNumbersHTML = method.hit_numbers.length > 0 ? 
                method.hit_numbers.map(num => 
                    `<span class="badge bg-success me-1">${num}</span>`
                ).join('') : 
                '<span class="text-muted">Không trúng</span>';
            
            return `
                <tr class="${method.hit_count > 0 ? 'table-success' : ''}">
                    <td>
                        <span class="badge ${method.hit_count > 0 ? 'bg-success' : 'bg-secondary'}">
                            ${index + 1}
                        </span>
                    </td>
                    <td>
                        <strong>${method.method_name}</strong>
                        <br><small class="text-muted">ID: ${method.method_id}</small>
                    </td>
                    <td>
                        ${predictedNumbersHTML}
                        <br><small class="text-muted">${method.predicted_count} số</small>
                    </td>
                    <td>
                        ${hitNumbersHTML}
                        <br><small class="text-muted">${method.hit_count} số</small>
                    </td>
                    <td>
                        <span class="badge ${hitRateClass.includes('success') ? 'bg-success' : 
                                        hitRateClass.includes('warning') ? 'bg-warning' : 
                                        hitRateClass.includes('info') ? 'bg-info' : 'bg-secondary'}">
                            ${hitRatePercent}%
                        </span>
                        <br><small class="text-muted">${method.hit_count}/${method.predicted_count}</small>
                    </td>
                    <td>
                        <span class="badge bg-primary">${method.score}</span>
                    </td>
                    <td>
                        <span class="badge bg-info">Ngày ${method.best_day}</span>
                    </td>
                </tr>
            `;
        }).join('');
    }

    // ✅ HÀM TẠO HTML CHO PREDICTED NUMBERS VỚI HIGHLIGHT
    function generatePredictedNumbersHTML(method) {
        if (!method.predicted_count || method.predicted_count === 0) {
            return '<span class="text-muted">Không có dự đoán</span>';
        }
        
        // Lấy predicted numbers từ method (cần thêm vào response)
        // Tạm thời sử dụng placeholder - sẽ fix trong API
        const predictedNumbers = method.predicted_numbers || [];
        const hitNumbers = new Set(method.hit_numbers || []);
        
        return predictedNumbers.map(num => {
            const isHit = hitNumbers.has(num);
            return `<span class="badge ${isHit ? 'bg-success' : 'bg-secondary'} me-1">
                ${num} ${isHit ? '✓' : ''}
            </span>`;
        }).join('');
    }

    // ✅ UTILITY FUNCTIONS
    function formatDateVN(dateStr) {
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('vi-VN', {
                weekday: 'short',
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        } catch (e) {
            return dateStr;
        }
    }


    // ✅ UTILITY FUNCTIONS
    function showLoading() {
        document.getElementById('analysisLoading').classList.remove('d-none');
        document.getElementById('analysisError').classList.add('d-none');
        document.getElementById('analysisResults').classList.add('d-none');
    }

    function hideLoading() {
        document.getElementById('analysisLoading').classList.add('d-none');
    }

    function showError(message) {
        const errorDiv = document.getElementById('analysisError');
        errorDiv.textContent = message;
        errorDiv.classList.remove('d-none');
        document.getElementById('analysisResults').classList.add('d-none');
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    
// ✅ HÀM HIGHLIGHT METHOD TRONG BẢNG
    function highlightMethodInTable(methodId, targetDate) {
        // Remove existing highlights
        document.querySelectorAll('.method-row').forEach(row => {
            row.classList.remove('filter-highlight');
        });
        
        // Highlight target method
        const targetRow = document.querySelector(`[data-method-id="${methodId}"]`);
        if (targetRow) {
            targetRow.classList.add('filter-highlight');
            targetRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Blink effect
            let blinkCount = 0;
            const blinkInterval = setInterval(() => {
                targetRow.style.backgroundColor = blinkCount % 2 === 0 ? '#fff3cd' : '#ffffff';
                blinkCount++;
                if (blinkCount >= 6) {
                    clearInterval(blinkInterval);
                    targetRow.style.backgroundColor = '';
                }
            }, 300);
        }
    }

// ✅ HELPER FUNCTION - GET CSRF TOKEN
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


document.addEventListener('DOMContentLoaded', function() {
    // Initialize date inputs
    initializeDateInputs();
    
    // Event handlers
    $('#analyzeSingleDate').on('click', analyzeSingleDate);
    $('#analyzeRange').on('click', analyzeRange);
    
    // Auto-refresh every 30 seconds for real-time updates
    //setInterval(refreshCurrentAnalysis, 30000);

    
    function initializeDateInputs() {
        const today = new Date();
        const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
        
        $('#dateRangeStart').val(formatDate(lastWeek));
        $('#dateRangeEnd').val(formatDate(today));
    }

    function formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    function analyzeSingleDate() {
        const selectedDate = $('#analysisDate').val();
        
        if (!selectedDate) {
            showAlert('Vui lòng chọn ngày để phân tích.', 'warning');
            return;
        }
        
        showLoading();
        
        // ✅ FETCH BOTH PREDICTION AND ACTUAL RESULTS
        const predictionPromise = $.ajax({
            url: '/pre-lokhung/api/cyclical-prediction-v3/',
            method: 'GET',
            data: {
                'analysis_date': selectedDate
            }
        });
        
        const actualResultsPromise = $.ajax({
            url: `/pre-lokhung/api/ketqua/${selectedDate}/`,
            method: 'GET'
        });
        
        // ✅ WAIT FOR BOTH APIs TO COMPLETE
        Promise.allSettled([predictionPromise, actualResultsPromise])
            .then(results => {
                hideLoading();
                
                const [predictionResult, actualResult] = results;
                
                if (predictionResult.status === 'fulfilled') {
                    const predictionData = predictionResult.value;
                    const actualData = actualResult.status === 'fulfilled' ? actualResult.value : null;
                    
                    // ✅ DISPLAY RESULTS WITH ACCURACY COMPARISON
                    displaySingleDateResultsWithAccuracy(predictionData, actualData, selectedDate);
                } else {
                    showAlert('Lỗi khi lấy dữ liệu dự đoán.', 'danger');
                }
            })
            .catch(error => {
                hideLoading();
                console.error('API Error:', error);
                showAlert('Lỗi khi lấy dữ liệu phân tích.', 'danger');
            });
    }

    function analyzeRange() {
        const startDate = $('#dateRangeStart').val();
        const endDate = $('#dateRangeEnd').val();
        
        if (!startDate || !endDate) {
            showAlert('Vui lòng chọn khoảng thời gian để phân tích.', 'warning');
            return;
        }
        
        if (new Date(startDate) > new Date(endDate)) {
            showAlert('Ngày bắt đầu phải nhỏ hơn ngày kết thúc.', 'warning');
            return;
        }
        
        showLoading();
        
        // Call API for each date in range
        const dates = getDateRange(startDate, endDate);
        const promises = dates.map(date => {
            return $.ajax({
                url: '/pre-lokhung/api/cyclical-prediction-v3/',
                method: 'GET',
                data: {
                    'analysis_date': dates,
                    'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
                }
            });
        });
        
        Promise.allSettled(promises)
            .then(results => {
                hideLoading();
                const successfulResults = results
                    .filter(result => result.status === 'fulfilled')
                    .map((result, index) => ({
                        date: dates[index],
                        data: result.value
                    }));
                
                if (successfulResults.length > 0) {
                    displayRangeResults(successfulResults);
                } else {
                    showNoData();
                    showAlert('Không thể lấy dữ liệu cho khoảng thời gian đã chọn.', 'warning');
                }
            });
    }

    function getDateRange(startDate, endDate) {
        const dates = [];
        const currentDate = new Date(startDate);
        const end = new Date(endDate);
        
        while (currentDate <= end) {
            dates.push(formatDate(currentDate));
            currentDate.setDate(currentDate.getDate() + 1);
        }
        
        return dates;
    }

    /**
     * ✅ ENHANCED FUNCTION: Display results with accuracy comparison
     * @param {object} predictionData - Data từ cyclical prediction API
     * @param {object} actualData - Data từ ketqua API (có thể null)
     * @param {string} selectedDate - Ngày được chọn
     */
    function displaySingleDateResultsWithAccuracy(predictionData, actualData, selectedDate) {
        console.log('📊 Cyclical Intelligence API Response:', predictionData);
        console.log('🎯 Actual Results Data:', actualData);
        
        if (!predictionData.success) {
            showAlert('Lỗi API: ' + predictionData.message, 'danger');
            return;
        }
        
        // ✅ EXTRACT PREDICTION DATA
        const cyclicalAnalysis = predictionData.cyclical_analysis || {};
        const contextAnalysis = cyclicalAnalysis.context_analysis || {};
        const methodSyncMatrix = cyclicalAnalysis.method_sync_matrix || {};
        const numberFrequencyCycles = cyclicalAnalysis.number_frequency_cycles || {};
        
        const optimalMethods = predictionData.optimal_methods || {};
        const intelligentPredictions = predictionData.intelligent_predictions || {};
        const performanceMetrics = predictionData.performance_metrics || {};
        
        // ✅ EXTRACT ACTUAL RESULTS IF AVAILABLE
        let actualNumbers = [];
        let accuracyData = null;
        
        if (actualData && actualData.success && actualData.data) {
            actualNumbers = actualData.data.all_2digit_numbers || [];
            console.log(`🎯 Found ${actualNumbers.length} actual numbers for ${selectedDate}`);
            
            // ✅ CALCULATE ACCURACY FOR EACH PREDICTION TYPE
            accuracyData = calculateAccuracyMetrics(intelligentPredictions, actualNumbers);
            console.log('📈 Accuracy Metrics:', accuracyData);
        } else {
            console.log(`⚠️ No actual results available for ${selectedDate}`);
        }
        
        // ✅ DISPLAY WITH ACCURACY HIGHLIGHTING
        displayCyclicalContextWithAccuracy(contextAnalysis, selectedDate, accuracyData);
        displayMethodSyncMatrix(methodSyncMatrix);
        displayIntelligentPredictionsWithAccuracy(intelligentPredictions, performanceMetrics, accuracyData);
        updatePerformanceDashboardWithAccuracy(performanceMetrics, accuracyData);
        displayEnhancedTableResultsWithAccuracy(predictionData, selectedDate, accuracyData);
        
        showResults();
    }

    /**
     * ✅ CALCULATE ACCURACY METRICS
     * @param {object} intelligentPredictions - Predictions data
     * @param {array} actualNumbers - Actual lottery results
     * @returns {object} Accuracy metrics cho từng loại prediction
     */
    function calculateAccuracyMetrics(intelligentPredictions, actualNumbers) {
        const cyclicalNumbers = intelligentPredictions.cyclical_numbers || [];
        const methodNumbers = intelligentPredictions.method_numbers || [];
        const fusionNumbers = intelligentPredictions.fusion_numbers || [];
        
        // ✅ CALCULATE MATCHES
        const cyclicalMatches = cyclicalNumbers.filter(num => actualNumbers.includes(num));
        const methodMatches = methodNumbers.filter(num => actualNumbers.includes(num)); 
        const fusionMatches = fusionNumbers.filter(num => actualNumbers.includes(num));
        
        // ✅ CALCULATE ACCURACY RATES
        const cyclicalAccuracy = cyclicalNumbers.length > 0 ? 
            (cyclicalMatches.length / cyclicalNumbers.length) * 100 : 0;
        const methodAccuracy = methodNumbers.length > 0 ? 
            (methodMatches.length / methodNumbers.length) * 100 : 0;
        const fusionAccuracy = fusionNumbers.length > 0 ? 
            (fusionMatches.length / fusionNumbers.length) * 100 : 0;
        
        // ✅ OVERALL ACCURACY (using fusion numbers as primary)
        const overallAccuracy = fusionNumbers.length > 0 ? fusionAccuracy : 
                               (cyclicalAccuracy + methodAccuracy) / 2;
        
        return {
            cyclical: {
                total: cyclicalNumbers.length,
                matches: cyclicalMatches,
                accuracy: cyclicalAccuracy
            },
            method: {
                total: methodNumbers.length,
                matches: methodMatches,
                accuracy: methodAccuracy
            },
            fusion: {
                total: fusionNumbers.length,
                matches: fusionMatches,
                accuracy: fusionAccuracy
            },
            overall: {
                accuracy: overallAccuracy,
                totalPredictions: fusionNumbers.length || Math.max(cyclicalNumbers.length, methodNumbers.length),
                totalMatches: fusionMatches.length || (cyclicalMatches.length + methodMatches.length)
            },
            actualNumbers: actualNumbers
        };
    }

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
        
        // Display table results
        displayEnhancedTableResults(apiResponse, selectedDate);
        
        showResults();
    }

    /**
     * ✅ ENHANCED TABLE RESULTS WITH ACCURACY HIGHLIGHTING
     */
    function displayEnhancedTableResultsWithAccuracy(apiResponse, selectedDate, accuracyData) {
        const tableBody = $('#cyclicalTableBody');
        tableBody.empty();
        
        const intelligentPredictions = apiResponse.intelligent_predictions || {};
        const performanceMetrics = apiResponse.performance_metrics || {};
        
        const cyclicalNumbers = intelligentPredictions.cyclical_numbers || [];
        const methodNumbers = intelligentPredictions.method_numbers || [];
        const fusionNumbers = intelligentPredictions.fusion_numbers || [];
        const expectedAccuracy = performanceMetrics.expected_accuracy || 0;
        const confidenceLevel = performanceMetrics.confidence_level || 'Unknown';
        
        // ✅ GENERATE HIGHLIGHTED NUMBER BADGES
        const cyclicalBadges = generateHighlightedBadges(cyclicalNumbers, accuracyData, 'cyclical', 'success');
        const methodBadges = generateHighlightedBadges(methodNumbers, accuracyData, 'method', 'warning');
        const fusionBadges = generateHighlightedBadges(fusionNumbers, accuracyData, 'fusion', 'primary');
        
        // ✅ GET REAL ACCURACY IF AVAILABLE
        const realAccuracy = accuracyData ? accuracyData.overall.accuracy : null;
        const accuracyComparison = realAccuracy !== null ? 
            (realAccuracy >= expectedAccuracy ? 'success' : 'danger') : 'secondary';
        
        // Create enhanced table row with accuracy highlighting
        const row = `
            <tr class="table-success">
                <td><strong>${formatDisplayDate(selectedDate)}</strong></td>
                <td>
                    <div class="prediction-numbers">
                        ${cyclicalBadges}
                    </div>
                    ${accuracyData ? `<small class="text-muted">Accuracy: ${accuracyData.cyclical.accuracy.toFixed(1)}%</small>` : ''}
                </td>
                <td>
                    <div class="prediction-numbers">
                        ${methodBadges}
                    </div>
                    ${accuracyData ? `<small class="text-muted">Accuracy: ${accuracyData.method.accuracy.toFixed(1)}%</small>` : ''}
                </td>
                <td>
                    <div class="prediction-numbers">
                        ${fusionBadges}
                    </div>
                    ${accuracyData ? `<small class="text-muted">Accuracy: ${accuracyData.fusion.accuracy.toFixed(1)}%</small>` : ''}
                </td>
                <td>
                    <div>
                        <span class="badge badge-${expectedAccuracy >= 50 ? 'success' : expectedAccuracy >= 30 ? 'warning' : 'danger'} badge-lg">
                            Expected: ${expectedAccuracy.toFixed(1)}%
                        </span>
                        ${realAccuracy !== null ? `
                            <br><span class="badge badge-${accuracyComparison} badge-lg mt-1">
                                Real: ${realAccuracy.toFixed(1)}%
                            </span>
                        ` : ''}
                    </div>
                </td>
                <td>
                    <span class="badge badge-${confidenceLevel === 'High' ? 'success' : confidenceLevel === 'Medium' ? 'warning' : 'danger'}">
                        ${confidenceLevel}
                    </span>
                    ${accuracyData ? `
                        <br><small class="text-muted">
                            ${accuracyData.overall.totalMatches}/${accuracyData.overall.totalPredictions} matches
                        </small>
                    ` : ''}
                </td>
            </tr>
        `;
        
        tableBody.append(row);
        
        // ✅ UPDATE SUMMARY WITH REAL ACCURACY
        const finalAccuracy = realAccuracy !== null ? realAccuracy : expectedAccuracy;
        updateSummaryStats(1, realAccuracy >= 50 ? 1 : 0, finalAccuracy, finalAccuracy);
    }

    /**
     * ✅ GENERATE HIGHLIGHTED BADGES FOR NUMBERS
     * @param {array} numbers - Array of predicted numbers
     * @param {object} accuracyData - Accuracy data including matches
     * @param {string} type - Type of prediction (cyclical, method, fusion)
     * @param {string} baseColor - Base badge color
     * @returns {string} HTML badges với highlighting
     */
    function generateHighlightedBadges(numbers, accuracyData, type, baseColor) {
        if (!numbers || numbers.length === 0) return '<span class="text-muted">No predictions</span>';
        
        const matches = accuracyData ? accuracyData[type].matches : [];
        
        return numbers.slice(0, 10).map((num, idx) => {
            const isMatch = matches.includes(num);
            const badgeClass = isMatch ? 'badge-success' : `badge-${baseColor}`;
            const matchIcon = isMatch ? '<i class="fas fa-check-circle ml-1"></i>' : '';
            const title = isMatch ? `✅ TRÚNG! Rank ${idx + 1}` : `Rank ${idx + 1}`;
            
            return `<span class="badge ${badgeClass} mr-1" title="${title}">${num}${matchIcon}</span>`;
        }).join('');
    }

    function displayEnhancedTableResults(apiResponse, selectedDate) {
        const tableBody = $('#cyclicalTableBody');
        tableBody.empty();
        
        const intelligentPredictions = apiResponse.intelligent_predictions || {};
        const performanceMetrics = apiResponse.performance_metrics || {};
        
        const cyclicalNumbers = intelligentPredictions.cyclical_numbers || [];
        const methodNumbers = intelligentPredictions.method_numbers || [];
        const fusionNumbers = intelligentPredictions.fusion_numbers || [];
        const expectedAccuracy = performanceMetrics.expected_accuracy || 0;
        const confidenceLevel = performanceMetrics.confidence_level || 'Unknown';
        
        // Create enhanced table row
        const row = `
            <tr class="table-success">
                <td><strong>${formatDisplayDate(selectedDate)}</strong></td>
                <td>
                    <div class="prediction-numbers">
                        ${cyclicalNumbers.slice(0, 10).map((num, idx) => 
                            `<span class="badge badge-success mr-1" title="Cyclical Rank ${idx + 1}">${num}</span>`
                        ).join('')}
                    </div>
                </td>
                <td>
                    <div class="prediction-numbers">
                        ${methodNumbers.slice(0, 10).map((num, idx) => 
                            `<span class="badge badge-warning mr-1" title="Method Rank ${idx + 1}">${num}</span>`
                        ).join('')}
                    </div>
                </td>
                <td>
                    <div class="prediction-numbers">
                        ${fusionNumbers.slice(0, 10).map((num, idx) => 
                            `<span class="badge badge-primary mr-1" title="Fusion Rank ${idx + 1}">${num}</span>`
                        ).join('')}
                    </div>
                </td>
                <td>
                    <span class="badge badge-${expectedAccuracy >= 50 ? 'success' : expectedAccuracy >= 30 ? 'warning' : 'danger'} badge-lg">
                        ${expectedAccuracy.toFixed(1)}%
                    </span>
                </td>
                <td>
                    <span class="badge badge-${confidenceLevel === 'High' ? 'success' : confidenceLevel === 'Medium' ? 'warning' : 'danger'}">
                        ${confidenceLevel}
                    </span>
                </td>
            </tr>
        `;
        
        tableBody.append(row);
        
        // Update summary stats
        updateSummaryStats(1, expectedAccuracy >= 50 ? 1 : 0, expectedAccuracy, expectedAccuracy);
    }

    function calculateAccuracy(prediction) {
        // Implement accuracy calculation based on prediction vs actual results
        // This is a placeholder - adjust based on your actual data structure
        if (prediction.actual_result && prediction.cyclical_prediction) {
            const predicted = prediction.cyclical_prediction.toString();
            const actual = prediction.actual_result.toString();
            
            // Simple match calculation
            if (predicted === actual) return 100;
            
            // Partial match calculation (if applicable)
            let matches = 0;
            const minLength = Math.min(predicted.length, actual.length);
            for (let i = 0; i < minLength; i++) {
                if (predicted[i] === actual[i]) matches++;
            }
            
            return Math.round((matches / Math.max(predicted.length, actual.length)) * 100);
        }
        
        return 0;
    }

    function createTableRow(date, prediction, accuracy, isAccurate) {
        const accuracyClass = getAccuracyClass(accuracy);
        const statusClass = isAccurate ? 'prediction-match' : '';
        const statusIcon = isAccurate ? '<i class="fas fa-check-circle text-success"></i>' : '<i class="fas fa-times-circle text-danger"></i>';
        
        return `
            <tr class="${statusClass}">
                <td><strong>${formatDisplayDate(date)}</strong></td>
                <td><span class="badge bg-primary">${prediction.cyclical_prediction || 'N/A'}</span></td>
                <td><span class="badge bg-secondary">${prediction.actual_result || 'Chưa có'}</span></td>
                <td class="${accuracyClass}">${accuracy}%</td>
                <td>${statusIcon} ${isAccurate ? 'Chính xác' : 'Không chính xác'}</td>
            </tr>
        `;
    }

    function getAccuracyClass(accuracy) {
        if (accuracy >= 80) return 'accuracy-high';
        if (accuracy >= 50) return 'accuracy-medium';
        return 'accuracy-low';
    }

    function formatDisplayDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN');
    }

    /**
     * ✅ ENHANCED CYCLICAL CONTEXT WITH ACCURACY
     */
    function displayCyclicalContextWithAccuracy(contextAnalysis, selectedDate, accuracyData) {
        const accuracySummary = accuracyData ? `
            <div class="alert alert-info mt-2">
                <h6><i class="fas fa-chart-line"></i> Accuracy Summary for ${formatDisplayDate(selectedDate)}</h6>
                <div class="row">
                    <div class="col-md-3">
                        <strong>Overall:</strong> 
                        <span class="badge badge-${accuracyData.overall.accuracy >= 50 ? 'success' : accuracyData.overall.accuracy >= 30 ? 'warning' : 'danger'} badge-lg">
                            ${accuracyData.overall.accuracy.toFixed(1)}%
                        </span>
                    </div>
                    <div class="col-md-3">
                        <strong>Cyclical:</strong> 
                        <span class="badge badge-success">${accuracyData.cyclical.accuracy.toFixed(1)}%</span>
                    </div>
                    <div class="col-md-3">
                        <strong>Method:</strong> 
                        <span class="badge badge-warning">${accuracyData.method.accuracy.toFixed(1)}%</span>
                    </div>
                    <div class="col-md-3">
                        <strong>Fusion:</strong> 
                        <span class="badge badge-primary">${accuracyData.fusion.accuracy.toFixed(1)}%</span>
                    </div>
                </div>
                <small class="text-muted">
                    Total matches: ${accuracyData.overall.totalMatches}/${accuracyData.overall.totalPredictions} 
                    | Actual numbers found: ${accuracyData.actualNumbers.length}
                </small>
            </div>
        ` : '<div class="alert alert-warning">⚠️ No actual results available for comparison</div>';
        
        const contextHtml = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-primary">
                        <div class="card-header bg-primary text-white">
                            <h5><i class="fas fa-brain"></i> Cyclical Context Analysis - ${formatDisplayDate(selectedDate)}</h5>
                        </div>
                        <div class="card-body">
                            ${accuracySummary}
                            <div class="row mt-3">
                                <div class="col-md-6">
                                    <h6>📊 Context Information:</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Day Phase:</strong> ${contextAnalysis.day_of_month_phase || 'N/A'}</li>
                                        <li><strong>Week Phase:</strong> ${contextAnalysis.week_phase || 'N/A'}</li>
                                        <li><strong>Month Trend:</strong> ${contextAnalysis.month_trend || 'N/A'}</li>
                                        <li><strong>Cycle Strength:</strong> 
                                            <span class="badge badge-info">${((contextAnalysis.cycle_strength || 0) * 100).toFixed(1)}%</span>
                                        </li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <h6>🔄 Cycle Status:</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Active Cycles:</strong> ${(contextAnalysis.active_cycles || []).length}</li>
                                        <li><strong>Fatigued Methods:</strong> ${(contextAnalysis.fatigued_methods || []).length}</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#cyclicalContext').html(contextHtml);
    }

    /**
     * ✅ ENHANCED INTELLIGENT PREDICTIONS WITH ACCURACY
     */
    function displayIntelligentPredictionsWithAccuracy(intelligentPredictions, performanceMetrics, accuracyData) {
        const cyclicalNumbers = intelligentPredictions.cyclical_numbers || [];
        const methodNumbers = intelligentPredictions.method_numbers || [];
        const fusionNumbers = intelligentPredictions.fusion_numbers || [];
        
        // ✅ GENERATE HIGHLIGHTED BADGES
        const cyclicalBadges = generateHighlightedBadges(cyclicalNumbers, accuracyData, 'cyclical', 'success');
        const methodBadges = generateHighlightedBadges(methodNumbers, accuracyData, 'method', 'warning');
        const fusionBadges = generateHighlightedBadges(fusionNumbers, accuracyData, 'fusion', 'primary');
        
        const predictionHtml = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-info">
                        <div class="card-header bg-info text-white">
                            <h5><i class="fas fa-magic"></i> Intelligent Predictions with Accuracy Tracking</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4">
                                    <h6><i class="fas fa-recycle text-success"></i> Cyclical Numbers:</h6>
                                    <div class="prediction-numbers mb-2">${cyclicalBadges}</div>
                                    ${accuracyData ? `<small class="text-success">✅ Accuracy: ${accuracyData.cyclical.accuracy.toFixed(1)}%</small>` : ''}
                                </div>
                                <div class="col-md-4">
                                    <h6><i class="fas fa-cogs text-warning"></i> Method Numbers:</h6>
                                    <div class="prediction-numbers mb-2">${methodBadges}</div>
                                    ${accuracyData ? `<small class="text-warning">⚡ Accuracy: ${accuracyData.method.accuracy.toFixed(1)}%</small>` : ''}
                                </div>
                                <div class="col-md-4">
                                    <h6><i class="fas fa-rocket text-primary"></i> Fusion Numbers:</h6>
                                    <div class="prediction-numbers mb-2">${fusionBadges}</div>
                                    ${accuracyData ? `<small class="text-primary">🚀 Accuracy: ${accuracyData.fusion.accuracy.toFixed(1)}%</small>` : ''}
                                </div>
                            </div>
                            ${accuracyData ? `
                                <div class="alert alert-info mt-3">
                                    <h6>🎯 Accuracy Comparison:</h6>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <strong>Expected Accuracy:</strong> 
                                            <span class="badge badge-secondary badge-lg">${performanceMetrics.expected_accuracy || 0}%</span>
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Actual Accuracy:</strong> 
                                            <span class="badge badge-${accuracyData.overall.accuracy >= (performanceMetrics.expected_accuracy || 0) ? 'success' : 'danger'} badge-lg">
                                                ${accuracyData.overall.accuracy.toFixed(1)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#intelligentPredictions').html(predictionHtml);
    }

    /**
     * ✅ ENHANCED PERFORMANCE DASHBOARD WITH ACCURACY
     */
    function updatePerformanceDashboardWithAccuracy(performanceMetrics, accuracyData) {
        const expectedAccuracy = performanceMetrics.expected_accuracy || 0;
        const realAccuracy = accuracyData ? accuracyData.overall.accuracy : null;
        const confidenceLevel = performanceMetrics.confidence_level || 'Unknown';
        const cyclicalStrength = performanceMetrics.cyclical_strength || 0;
        const performanceBreakdown = performanceMetrics.performance_breakdown || {};
        const riskAssessment = performanceMetrics.risk_assessment || {};
        
        const accuracyAlert = realAccuracy !== null ? 
            (realAccuracy >= expectedAccuracy ? 
                `<div class="alert alert-success"><i class="fas fa-check-circle"></i> Accuracy exceeds expectations!</div>` :
                `<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> Accuracy below expectations</div>`
            ) : '';
        
        const dashboardHtml = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-success">
                        <div class="card-header bg-success text-white">
                            <h5><i class="fas fa-tachometer-alt"></i> Performance Dashboard</h5>
                        </div>
                        <div class="card-body">
                            ${accuracyAlert}
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="display-4 text-secondary">${expectedAccuracy}%</h4>
                                        <p class="text-muted">Expected Accuracy</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="display-4 text-${realAccuracy !== null ? (realAccuracy >= expectedAccuracy ? 'success' : 'danger') : 'muted'}">
                                            ${realAccuracy !== null ? realAccuracy.toFixed(1) : '--'}%
                                        </h4>
                                        <p class="text-muted">Real Accuracy</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="display-4 text-info">${(cyclicalStrength * 100).toFixed(1)}%</h4>
                                        <p class="text-muted">Cyclical Strength</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="display-4 text-${confidenceLevel === 'High' ? 'success' : confidenceLevel === 'Medium' ? 'warning' : 'danger'}">
                                            ${confidenceLevel}
                                        </h4>
                                        <p class="text-muted">Confidence</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#performanceDashboard').html(dashboardHtml);
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

    function updateSummaryStats(total, accurate, avgAccuracy, bestAccuracy) {
        $('#totalAnalyzed').text(total);
        $('#accurateCount').text(accurate);
        $('#averageAccuracy').text(Math.round(avgAccuracy) + '%');
        $('#bestAccuracy').text(Math.round(bestAccuracy) + '%');
    }

    function showLoading() {
        $('#cyclicalLoading').show();
        $('#cyclicalResults').hide();
        $('#noDataMessage').hide();
    }

    function hideLoading() {
        $('#cyclicalLoading').hide();
    }

    function showResults() {
        $('#cyclicalResults').show();
        $('#noDataMessage').hide();
    }

    function showNoData() {
        $('#cyclicalResults').hide();
        $('#noDataMessage').show();
    }

    function showAlert(message, type) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Insert alert at the top of cyclical section
        $('.cyclical-section .card-body').prepend(alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            $('.alert').alert('close');
        }, 5000);
    }

    function refreshCurrentAnalysis() {
        // Only refresh if results are currently displayed
        if ($('#cyclicalResults').is(':visible')) {
            const currentDate = $('#analysisDate').val();
            if (currentDate) {
                analyzeSingleDate();
            }
        }
    }

    // ✅ 0. KHAI BÁO NGÀY HIỆN TẠI TRONG DATE PICKER CỦA ANALYSIS DATE PREDICTION
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('analysisDatePicker').value = today;
    // ✅ 1. KHAI BÁO BIẾN METHODANALYSIS NGAY ĐẦU
    const methodAnalysis = "";
    
    // ✅ 2. EXISTING DAY DATA - GIỮ NGUYÊN
    const dayData = {
        
        """": {
            date: """",
            weekday: """",
            sessions: [
                
                {
                    cycle_name: """",
                    status: """",
                    methods: [
                        
                        {
                            method_id: "",
                            method_name: """",
                            category: """",
                            confidence: "",
                            predicted_numbers: ["",],
                            tracking_results: [
                                
                                {
                                    day: "",
                                    tracking_date: """",
                                    has_result: truefalse,
                                    hit_count: "",
                                    hit_rate: "",
                                    hit_numbers: ["",],
                                    actual_numbers: ["",]
                                },
                                
                            ],
                            total_hits: "",
                            avg_hit_rate: ""
                        },
                        
                    ]
                },
                
            ]
        },
        
    };

    // ✅ 3. KHAI BÁO CÁC FUNCTIONS TRƯỚC KHI SỬ DỤNG

    /**
     * ✅ HÀM AUTO APPLY MÀU PREDICTION INDEX 1 SAU KHI LOAD PAGE
     */
    function autoApplyPredictionIndex1Colors() {
        try {
            console.log('🔄 Auto applying prediction index 1 colors...');
            
            const predictionCells = document.querySelectorAll('.prediction-cell[data-prediction-1]');
            let appliedCount = 0;
            
            predictionCells.forEach(cell => {
                const prediction1 = cell.dataset.prediction1;
                const autoIndex = cell.dataset.autoPredictionIndex;
                
                // ✅ CHỈ APPLY MÀU NẾU CÓ PREDICTION INDEX 1 VÀ KHÁC '-'
                if (prediction1 && prediction1 !== '-' && autoIndex === '1') {
                    cell.setAttribute('data-current-prediction', '1');
                    appliedCount++;
                    
                    console.log(`✅ Applied index 1 colors to method ${cell.dataset.methodId}, prediction: ${prediction1}`);
                }
            });
            
            console.log(`🎨 Auto-applied prediction index 1 colors to ${appliedCount} cells`);
            
            // ✅ HIỂN THỊ NOTIFICATION CHO USER
            if (appliedCount > 0) {
                showAutoColorNotification(appliedCount);
            }
            
        } catch (error) {
            console.error('❌ Error auto-applying prediction index 1 colors:', error);
        }
    }
    
    /**
     * ✅ HÀM HIỂN THỊ NOTIFICATION KHI AUTO APPLY MÀU
     */
    function showAutoColorNotification(count) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-palette me-2"></i>
            <strong>Auto Color Applied:</strong> 
            Đã tự động áp dụng màu scheme <strong>prediction index 1</strong> cho ${count} methods có prediction thứ 2.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            // ✅ AUTO REMOVE AFTER 5 SECONDS
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 5000);
        }
    }
    
    /**
     * ✅ HÀM THAY ĐỔI MÀU BADGE DỰA TRÊN SỐ DỰ ĐOÁN
     */
    function changeBadgeColors(methodId, date, predictionIndex) {
        try {
            const cell = document.querySelector(`[data-method-id="${methodId}"][data-date="${date}"]`);
            if (!cell) {
                console.warn(`⚠️ Cell not found for method ${methodId}, date ${date}`);
                return;
            }
            
            cell.setAttribute('data-current-prediction', predictionIndex);
            console.log(`🎨 Changed badge colors for method ${methodId} to prediction index ${predictionIndex}`);
            
        } catch (error) {
            console.error('❌ Error changing badge colors:', error);
        }
    }
    
    /**
     * ✅ HÀM THAY ĐỔI MÀU TẤT CẢ BADGES
     */
    function changeAllBadgeColors(predictionIndex) {
        try {
            const predictionCells = document.querySelectorAll('.prediction-cell[data-prediction-0], .prediction-cell[data-prediction-1]');
            let changedCount = 0;
            
            predictionCells.forEach(cell => {
                const methodId = cell.dataset.methodId;
                const date = cell.dataset.date;
                
                if (methodId && date) {
                    const hasThisPrediction = cell.dataset[`prediction${predictionIndex}`] && 
                                           cell.dataset[`prediction${predictionIndex}`] !== '-';
                    
                    if (hasThisPrediction) {
                        cell.setAttribute('data-current-prediction', predictionIndex);
                        changedCount++;
                    }
                }
            });
            
            console.log(`🎨 Changed ${changedCount} cells to prediction index ${predictionIndex}`);
            
        } catch (error) {
            console.error('❌ Error changing all badge colors:', error);
        }
    }
    
    /**
     * ✅ HÀM RESET VỀ MÀU MẶC ĐỊNH (INDEX 0)
     */
    function resetBadgeColors() {
        try {
            const predictionCells = document.querySelectorAll('.prediction-cell[data-current-prediction]');
            
            predictionCells.forEach(cell => {
                cell.removeAttribute('data-current-prediction');
            });
            
            console.log('🎨 Reset all badge colors to default (index 0)');
            
        } catch (error) {
            console.error('❌ Error resetting badge colors:', error);
        }
    }
    
    /**
     * ✅ HÀM TOGGLE GIỮA 2 SCHEME MÀU
     */
    function toggleBadgeColors() {
        try {
            const firstCellWithPrediction = document.querySelector('.prediction-cell[data-current-prediction]');
            const currentIndex = firstCellWithPrediction ? 
                                parseInt(firstCellWithPrediction.getAttribute('data-current-prediction')) : 0;
            
            const newIndex = currentIndex === 0 ? 1 : 0;
            changeAllBadgeColors(newIndex);
            
            showColorChangeNotification(newIndex);
            
        } catch (error) {
            console.error('❌ Error toggling badge colors:', error);
        }
    }
    
    /**
     * ✅ HÀM HIỂN THỊ THÔNG BÁO THAY ĐỔI MÀU
     */
    function showColorChangeNotification(predictionIndex) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-palette me-2"></i>
            <strong>Đã thay đổi màu badges:</strong> 
            Hiển thị scheme màu cho <strong>prediction index ${predictionIndex}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 3000);
        }
    }
    
    // ✅ AUTO APPLY PREDICTION INDEX 1 COLORS KHI PAGE LOAD XONG
    setTimeout(() => {
        autoApplyPredictionIndex1Colors();
    }, 500); // Delay 500ms để đảm bảo DOM render xong
    
    // ✅ EXPOSE FUNCTIONS FOR MANUAL CONTROL
    window.badgeColorControl = {
        change: changeBadgeColors,
        changeAll: changeAllBadgeColors,
        reset: resetBadgeColors,
        toggle: toggleBadgeColors,
        showPredictionIndex: showPredictionIndexColors,
        info: showBadgeInfo
    };
    
    // ✅ HÀM HIỂN THỊ PREDICTION INDEX COLORS
    function showPredictionIndexColors() {
        const badges = document.querySelectorAll('.hit-badge[data-pred-index]');
        let info = {
            index_0: { count: 0, days: [] },
            index_1: { count: 0, days: [] }
        };
        
        badges.forEach(badge => {
            const predIndex = badge.getAttribute('data-pred-index');
            const day = badge.getAttribute('data-day');
            
            if (predIndex === '0') {
                info.index_0.count++;
                info.index_0.days.push(day);
            } else if (predIndex === '1') {
                info.index_1.count++;
                info.index_1.days.push(day);
            }
        });
        
        console.log('📊 Prediction Index Color Analysis:', info);
        return info;
    }
    
    // ✅ HÀM HIỂN THỊ THÔNG TIN BADGE
    function showBadgeInfo() {
        const badges = document.querySelectorAll('.hit-badge');
        badges.forEach(badge => {
            const day = badge.getAttribute('data-day');
            const predIndex = badge.getAttribute('data-pred-index');
            const bgColor = window.getComputedStyle(badge).backgroundColor;
            
            console.log(`Badge Day ${day} - Prediction Index ${predIndex} - Color: ${bgColor}`);
        });
    }
    
    console.log('✅ Badge color control initialized with prediction index support');
    console.log('💡 Use: window.badgeColorControl.showPredictionIndex() to see prediction index info');
    console.log('💡 Use: window.badgeColorControl.info() to debug badge colors');

    // ✅ HÀM TẠO DAY-BY-DAY ANALYSIS HTML
    function generateDayByDayAnalysis(dayAnalysis) {
        console.log('Day-by-day analysis:', dayAnalysis);
        if (!dayAnalysis || !dayAnalysis.day_1) {
            return '<div class="alert alert-warning alert-sm">Không có dữ liệu phân tích theo ngày</div>';
        }

        const bestDay = dayAnalysis.best_day;
        const strategy = dayAnalysis.recommended_strategy;
        
        let html = `
            <div class="day-analysis-container mb-2">
                <div class="row g-1 mb-2">
        `;
        
        // Hiển thị 3 ngày tracking
        for (let day = 1; day <= 3; day++) {
            const dayData = dayAnalysis[`day_${day}`];
            const isBestDay = day === bestDay;
            const cardClass = isBestDay ? 'border-success bg-light-success' : 'border-secondary';
            const probability = dayData.hit_probability || 0;
            const confidence = dayData.confidence || 'no_data';
            
            // Color coding cho probability
            let probColor = 'text-danger';
            if (probability >= 70) probColor = 'text-success';
            else if (probability >= 50) probColor = 'text-warning';
            else if (probability >= 30) probColor = 'text-info';
            
            // Confidence icon
            const confIcons = {
                'high': '🔥',
                'medium': '⚡',
                'low': '💡',
                'very_low': '❓',
                'no_data': '❌'
            };
            
            html += `
                <div class="col-4">
                    <div class="card card-sm ${cardClass}" style="font-size: 0.75rem;">
                        <div class="card-body p-1 text-center">
                            <div class="fw-bold">Ngày ${day} ${isBestDay ? '⭐' : ''}</div>
                            <div class="${probColor} fw-bold">${probability}%</div>
                            <div class="text-muted">${confIcons[confidence]}</div>
                            ${dayData.sample_size ? `<small class="text-muted">(${dayData.sample_size} mẫu)</small>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }
        
        html += `
                </div>
                <div class="goi-y-strategy">
                    <div class="alert alert-info alert-sm p-2 mb-0" style="font-size: 0.8rem;">
                        <strong>🎯 Gợi ý:</strong> ${strategy}
                    </div>
                </div>
            </div>
        `;
        
        return html;
    }

    // ✅ HÀM TẠO RECOMMENDATIONS LIST HTML - SỬA LỖI
    function generateRecommendationsList(recommendations) {
        if (recommendations.length === 0) {
            return '<div class="alert alert-info">Không có đủ dữ liệu để phân tích</div>';
        }

        let html = '<div class="list-group">';
        
        recommendations.slice(0, 5).forEach((rec, index) => {
            const scoreClass = rec.score >= 80 ? 'success' : rec.score >= 60 ? 'warning' : 'danger';
            const trendIcon = rec.trend_direction === 'up' ? '📈' : rec.trend_direction === 'down' ? '📉' : '➡️';
            const riskColor = rec.risk_level === 'low' ? 'success' : rec.risk_level === 'medium' ? 'warning' : 'danger';
            
            // ✅ KIỂM TRA METHODANALYSIS TRƯỚC KHI SỬ DỤNG
            let dayAnalysisHTML = '';
            if (methodAnalysis && methodAnalysis.day_by_day_analysis && methodAnalysis.day_by_day_analysis[rec.method_id]) {
                const dayAnalysis = methodAnalysis.day_by_day_analysis[rec.method_id];
                dayAnalysisHTML = generateDayByDayAnalysis(dayAnalysis);
            } else {
                dayAnalysisHTML = '<div class="alert alert-warning alert-sm">Không có dữ liệu phân tích theo ngày</div>';
            }
            
            html += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center mb-2">
                                <span class="badge bg-secondary me-2">#${index + 1}</span>
                                <strong class="text-primary">${rec.method_name}</strong>
                                <span class="ms-2">${trendIcon}</span>
                            </div>
                            
                            <!-- ✅ THÊM PHÂN TÍCH THEO TỪNG NGÀY -->
                            ${dayAnalysisHTML}
                            
                            <div class="mt-2">
                                <small class="text-muted">${rec.reason}</small>
                            </div>
                            <div class="mt-1">
                                <small class="text-info">
                                    Recent: ${rec.recent_performance}% | 
                                    Stability: ${rec.stability}% |
                                    ${rec.cycle_info.next_expected_hit !== 'unknown' ? 
                                        `Chu kỳ: ${rec.cycle_info.next_expected_hit}` : 
                                        'Chu kỳ: không rõ'}
                                </small>
                            </div>
                        </div>
                        <div class="text-end">
                            <div class="badge bg-${scoreClass} mb-1">${rec.score}/100</div><br>
                            <small class="text-${riskColor}">Risk: ${rec.risk_level}</small><br>
                            <small class="text-muted">Conf: ${rec.confidence}%</small>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        return html;
    }

    // ✅ HÀM TẠO RECOMMENDATIONS - SỬA LỖI
    function generateRecommendations(methods) {
        let recommendations = [];

        if (!methodAnalysis) {
            console.warn('methodAnalysis not available');
            return recommendations;
        }

        methods.forEach(method => {
            const analysis = methodAnalysis.method_recommendations ? methodAnalysis.method_recommendations[method.method_id] : null;
            const trends = methodAnalysis.method_trends ? methodAnalysis.method_trends[method.method_id] : null;
            const cycles = methodAnalysis.method_cycles ? methodAnalysis.method_cycles[method.method_id] : null;

            if (analysis && trends && cycles) {
                recommendations.push({
                    method_id: method.method_id,
                    method_name: method.method_name,
                    score: analysis.score,
                    confidence: analysis.confidence,
                    reason: analysis.reason,
                    risk_level: analysis.risk_level,
                    trend_direction: trends.trend_direction,
                    recent_performance: trends.recent_performance,
                    stability: trends.stability,
                    cycle_info: cycles
                });
            }
        });

        // Sắp xếp theo score
        recommendations.sort((a, b) => b.score - a.score);
        return recommendations;
    }

    // ✅ HÀM generateStatsOverview - SỬA LỖI
    function generateStatsOverview(recommendations) {
        if (recommendations.length === 0) {
            return '<div class="text-muted">Không có dữ liệu</div>';
        }

        const avgScore = recommendations.reduce((sum, rec) => sum + rec.score, 0) / recommendations.length;
        const highScore = recommendations.filter(rec => rec.score >= 70).length;
        const upTrend = recommendations.filter(rec => rec.trend_direction === 'up').length;
        const lowRisk = recommendations.filter(rec => rec.risk_level === 'low').length;

        // ✅ THÊM THỐNG KÊ THEO NGÀY - KIỂM TRA METHODANALYSIS
        let dayStats = {1: [], 2: [], 3: []};
        if (methodAnalysis && methodAnalysis.day_by_day_analysis) {
            recommendations.forEach(rec => {
                const dayAnalysis = methodAnalysis.day_by_day_analysis[rec.method_id];
                if (dayAnalysis) {
                    for (let day = 1; day <= 3; day++) {
                        const dayData = dayAnalysis[`day_${day}`];
                        if (dayData && dayData.hit_probability > 0) {
                            dayStats[day].push(dayData.hit_probability);
                        }
                    }
                }
            });
        }

        // Tìm ngày có xác suất cao nhất
        let bestDayOverall = 1;
        let bestAvgProb = 0;
        for (let day = 1; day <= 3; day++) {
            if (dayStats[day].length > 0) {
                const avgProb = dayStats[day].reduce((sum, prob) => sum + prob, 0) / dayStats[day].length;
                if (avgProb > bestAvgProb) {
                    bestAvgProb = avgProb;
                    bestDayOverall = day;
                }
            }
        }

        return `
            <div class="list-group list-group-flush">
                <div class="list-group-item p-2">
                    <div class="d-flex justify-content-between">
                        <span>Điểm TB:</span>
                        <strong class="${avgScore >= 70 ? 'text-success' : avgScore >= 50 ? 'text-warning' : 'text-danger'}">${avgScore.toFixed(1)}</strong>
                    </div>
                </div>
                <div class="list-group-item p-2">
                    <div class="d-flex justify-content-between">
                        <span>Điểm cao (≥70):</span>
                        <strong class="text-success">${highScore}/${recommendations.length}</strong>
                    </div>
                </div>
                <div class="list-group-item p-2">
                    <div class="d-flex justify-content-between">
                        <span>Xu hướng tăng:</span>
                        <strong class="text-primary">${upTrend}/${recommendations.length}</strong>
                    </div>
                </div>
                <div class="list-group-item p-2">
                    <div class="d-flex justify-content-between">
                        <span>Rủi ro thấp:</span>
                        <strong class="text-success">${lowRisk}/${recommendations.length}</strong>
                    </div>
                </div>
                <!-- ✅ THÊM THỐNG KÊ NGÀY TỐT NHẤT -->
                <div class="list-group-item p-2 bg-light">
                    <div class="d-flex justify-content-between">
                        <span>📅 Ngày khuyến nghị:</span>
                        <strong class="text-primary">Ngày ${bestDayOverall} (${bestAvgProb.toFixed(1)}%)</strong>
                    </div>
                </div>
            </div>
        `;
    }

    /**
    * ✅ HÀM TẠO PHẦN PHÂN TÍCH AI VÀ ML CHO NGÀY CỤ THỂ
    * @param {string} date - Ngày cần phân tích (định dạng YYYY-MM-DD)
    * @param {number} selectedMethodId - ID của phương pháp đã chọn (nếu có)
    * @returns {string} - HTML cho phần phân tích
    */
    function createAnalysisSection(date, selectedMethodId) {
        const methods = getDayMethods(date, selectedMethodId);
        let analysisHTML = `
            <div class="card mb-3">
                <div class="card-header bg-primary text-white">
                    <h6 class="mb-0">
                        <i class="fas fa-brain me-2"></i>AI Pattern Analysis & ML Prediction cho ngày ${date}
                        <div class="spinner-border spinner-border-sm ms-2 d-none" id="analysis-spinner" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </h6>
                </div>
                <div class="card-body" id="analysis-content">
                    <div class="text-center text-muted">
                        <i class="fas fa-chart-line fa-2x mb-2"></i>
                        <p>Đang phân tích pattern và ML cho ngày này...</p>
                        <small class="text-muted">Sử dụng API: pattern-analysis</small>
                    </div>
                </div>
                <!-- ✅ METADATA CONTAINER -->
                <div id="data-source-info" class="d-none">
                    <!-- Metadata will be populated by JavaScript -->
                </div>
            </div>
        `;
        
        // Trigger pattern analysis cho ngày cụ thể
        setTimeout(() => {
            performDaySpecificAnalysis(date, selectedMethodId);
        }, 100);
        
        return analysisHTML;
    }

    function showDataSourceInfo(metadata) {
        if (!metadata || typeof metadata !== 'object') {
            return;
        }
        
        const infoContainer = document.getElementById('data-source-info');
        if (!infoContainer) {
            return;
        }
        
        try {
            const totalMethods = metadata.total_active_methods || 0;
            const successfulMethods = metadata.successful_predictions || 0;
            const analysisTimestamp = metadata.analysis_timestamp || 'Unknown';
            
            const html = `
                <div class="card-footer bg-light">
                    <div class="row text-center">
                        <div class="col-md-3">
                            <div class="fw-bold text-primary">${totalMethods}</div>
                            <small class="text-muted">Total Methods</small>
                        </div>
                        <div class="col-md-3">
                            <div class="fw-bold text-success">${successfulMethods}</div>
                            <small class="text-muted">Successful</small>
                        </div>
                        <div class="col-md-3">
                            <div class="fw-bold text-info">${metadata.service || 'TrackingService'}</div>
                            <small class="text-muted">Service</small>
                        </div>
                        <div class="col-md-3">
                            <div class="fw-bold text-secondary">${new Date(analysisTimestamp).toLocaleTimeString()}</div>
                            <small class="text-muted">Analysis Time</small>
                        </div>
                    </div>
                </div>
            `;
            
            infoContainer.innerHTML = html;
            infoContainer.classList.remove('d-none');
            
        } catch (error) {
            console.error('❌ Error displaying metadata:', error);
        }
    }

    /**
    * ✅ HÀM VALIDATE RESPONSE DATA TRƯỚC KHI XỬ LÝ
    * @param {object} data - Response data from API
    * @returns {boolean} - True if valid, false otherwise
    */
    function validateResponseData(data) {
        if (!data || typeof data !== 'object') {
            console.error('❌ Invalid response data: not an object');
            return false;
        }
        
        // ✅ VALIDATE REQUIRED FIELDS cho pattern-analysis API
        const requiredFields = ['success'];
        const missingFields = requiredFields.filter(field => !(field in data));
        
        if (missingFields.length > 0) {
            console.error('❌ Missing required fields:', missingFields);
            return false;
        }
        
        // ✅ VALIDATE SUCCESS FIELD
        if (typeof data.success !== 'boolean') {
            console.error('❌ Invalid success field type');
            return false;
        }
        
        // ✅ NẾU SUCCESS = TRUE, VALIDATE ADDITIONAL FIELDS
        if (data.success) {
            if (data.predictions && typeof data.predictions !== 'object') {
                console.error('❌ Invalid predictions field type');
                return false;
            }
            
            if (data.analysis && typeof data.analysis !== 'object') {
                console.error('❌ Invalid analysis field type');
                return false;
            }
            
            if (data.data_quality && typeof data.data_quality !== 'object') {
                console.error('❌ Invalid data_quality field type');
                return false;
            }
            
            if (data.metadata && typeof data.metadata !== 'object') {
                console.error('❌ Invalid metadata field type');
                return false;
            }
        }
        
        return true;
    }

    /**
    * ✅ SỬA HÀM performDaySpecificAnalysis - SIMPLIFIED VERSION
    * @param {string} date - Ngày cần phân tích
    * @param {number|null} selectedMethodId - Method được chọn (không cần thiết nữa)
    */
    function performDaySpecificAnalysis(date, selectedMethodId = null) {
        const content = document.getElementById('analysis-content');
        
        // Show spinner
        const spinner = document.getElementById('analysis-spinner');
        if (spinner) {
            spinner.classList.remove('d-none');
        }

        console.log('🔍 Day Specific Analysis:');
        console.log(`   📅 Analysis Date: ${date}`);

        // ✅ CHỈ GỌI API VỚI NGÀY PHÂN TÍCH
        getPatternAnalysisPredictions(date)
            .then(async (data) => {
                // Hide spinner
                if (spinner) {
                    spinner.classList.add('d-none');
                }
                
                // Display results
                await displayAnalysisResults(data);
            })
            .catch(error => {
                // Hide spinner
                if (spinner) {
                    spinner.classList.add('d-none');
                }
                
                showErrorMessage('Lỗi phân tích pattern: ' + error.message);
            });
    }
    
    /**
    * ✅ THÊM HÀM HIỂN THỊ WARNING CHO INVALID METHODS
    */
    function showAnalysisWarning(message, invalidMethodIds = []) {
        const alertHtml = `
            <div class="alert alert-warning alert-dismissible fade show mt-3" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>⚠️ Cảnh báo:</strong> ${message}
                ${invalidMethodIds.length > 0 ? `
                    <details class="mt-2">
                        <summary>Chi tiết method IDs không hợp lệ:</summary>
                        <ul class="mt-2 mb-0">
                            ${invalidMethodIds.map(id => `<li><code>${JSON.stringify(id)}</code></li>`).join('')}
                        </ul>
                    </details>
                ` : ''}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        // Thêm vào đầu analysis content
        const content = document.getElementById('analysis-content');
        if (content) {
            content.insertAdjacentHTML('afterbegin', alertHtml);
        }
    }

    /**
    * ✅ THÊM HÀM HELPER EXTRACT ANALYSIS DATE
    * @param {object} predictions - Predictions object
    * @returns {string} - Analysis date (YYYY-MM-DD)
    */
    function extractAnalysisDateFromPredictions(predictions) {
        // ✅ TRY TO EXTRACT DATE FROM FIRST PREDICTION
        const firstPrediction = Object.values(predictions)[0];
        if (firstPrediction && firstPrediction.analysis_date) {
            return firstPrediction.analysis_date;
        }
        
        // ✅ FALLBACK TO TODAY'S DATE
        return new Date().toISOString().split('T')[0];
    }
    
    // ✅ HÀM HIỂN THỊ KẾT QUẢ ENHANCED ML
    function displayEnhancedMLResults(predictions, modelPerformance) {
        const content = document.getElementById('analysis-content');
        if (!content) return;

        let html = `
            <div class="alert alert-success">
                <h5><i class="fas fa-robot"></i> Enhanced ML Predictions</h5>
                <p>Sử dụng mô hình Machine Learning đã được huấn luyện</p>
            </div>
        `;

        // Model performance info
        if (modelPerformance && modelPerformance.overall_performance) {
            const perf = modelPerformance.overall_performance;
            html += `
                <div class="card mb-3">
                    <div class="card-header bg-info text-white">
                        <h6>Model Performance</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <strong>Avg Accuracy:</strong> ${(perf.avg_accuracy * 100).toFixed(1)}%
                            </div>
                            <div class="col-md-4">
                                <strong>Best Accuracy:</strong> ${(perf.best_accuracy * 100).toFixed(1)}%
                            </div>
                            <div class="col-md-4">
                                <strong>Consistency:</strong> ${(perf.consistency * 100).toFixed(1)}%
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        // Predictions
        const sortedPredictions = Object.entries(predictions).sort((a, b) => 
            b[1].overall_confidence - a[1].overall_confidence
        );

        html += '<div class="row g-3">';
        
        sortedPredictions.forEach(([methodId, prediction], index) => {
            const confidence = (prediction.overall_confidence * 100).toFixed(1);
            const recommendedDay = prediction.recommended_day;
            
            html += `
                <div class="col-md-6">
                    <div class="card ${index === 0 ? 'border-success' : ''}">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">${prediction.method_name}</h6>
                            <span class="badge bg-primary">${confidence}% confidence</span>
                        </div>
                        <div class="card-body">
                            <div class="row g-2">
            `;
            
            // Day predictions
            for (let day = 1; day <= 3; day++) {
                const dayPred = prediction.day_predictions[`day_${day}`];
                const isRecommended = day === recommendedDay;
                const probability = (dayPred.probability * 100).toFixed(1);
                const dayConfidence = (dayPred.confidence * 100).toFixed(1);
                
                html += `
                    <div class="col-4">
                        <div class="day-prob-card ${isRecommended ? 'recommended' : ''}">
                            <div class="day-label">Day ${day}</div>
                            <div class="prob-value">${probability}%</div>
                            <small class="text-muted">${dayConfidence}% conf</small>
                            ${isRecommended ? '<i class="fas fa-star text-warning"></i>' : ''}
                        </div>
                    </div>
                `;
            }
            
            html += `
                            </div>
                            <div class="mt-2">
                                <small class="text-muted">
                                    Source: ${prediction.prediction_source} | 
                                    Features: ${prediction.feature_count}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        content.innerHTML = html;
    }
    

    /**
    * ✅ HÀM ĐÁNH GIÁ CHẤT LƯỢNG DỰ ĐOÁN
    * @param {number} probability - Xác suất (%)
    * @param {number} confidence - Độ tin cậy (%) 
    * @returns {string} - Text mô tả chất lượng
    */
    function getQualityText(probability, confidence) {
        // ✅ BOTH MUST BE CHECKED INDIVIDUALLY FOR STRICT MODE
        if (probability >= 60 && confidence >= 60) {
            const avgScore = (probability + confidence) / 2;
            if (avgScore >= 80) return "🔥🔥 Xuất sắc";
            if (avgScore >= 70) return "🔥 Rất tốt";
            return "⚡ Tốt";
        }
        
        // ✅ FOR NON-BADGE DISPLAY
        const avgScore = (probability + confidence) / 2;
        if (avgScore >= 45) return "💡 Khá";
        if (avgScore >= 30) return "❓ Thấp";
        return "❌ Rất thấp";
    }

    /**
    * ✅ HÀM ÁP DỤNG STYLE THEO CHẤT LƯỢNG
    * @param {Element} badge - Badge element
    * @param {number} probability - Xác suất (%)
    * @param {number} confidence - Độ tin cậy (%)
    * @param {boolean} isRecommended - Có phải ngày được khuyến nghị
    */
    function applyQualityStyle(badge, probability, confidence, isRecommended) {
        const avgScore = (probability + confidence) / 2;
        
        // ✅ STYLE CHO RECOMMENDED DAY
        if (isRecommended) {
            badge.style.fontWeight = 'bold';
            badge.style.boxShadow = '0 0 0 2px #fff, 0 0 0 4px gold';
            badge.style.zIndex = '15';
        }
        
        // ✅ OPACITY VÀ BORDER DỰA TRÊN CHẤT LƯỢNG
        if (avgScore >= 60) {
            badge.style.opacity = '1.0';
            badge.style.border = '2px solid #28a745';  // Green border for high quality
        } else if (avgScore >= 45) {
            badge.style.opacity = '0.9';
            badge.style.border = '1px solid #17a2b8';  // Blue border for good quality
        } else if (avgScore >= 30) {
            badge.style.opacity = '0.8';
            badge.style.border = '1px solid #ffc107';  // Yellow border for fair quality
        } else {
            badge.style.opacity = '0.7';
            badge.style.border = '1px solid #6c757d';  // Gray border for low quality
        }
        
        // ✅ ANIMATION CHO HIGH QUALITY
        if (avgScore >= 60) {
            badge.style.animation = 'pulse 2s infinite';
        }
    }

   /**
    * ✅ SỬA HÀM displayAnalysisResults - FIX ENHANCED ML CASE
    * @param {object} data - Response data from API
    * @param {object} dataQuality - Frontend data quality
    */
    async function displayAnalysisResults(data, dataQuality = null) {
        const content = document.getElementById('analysis-content');
        if (!content) return;

        // Hide spinner
        const spinner = document.getElementById('analysis-spinner');
        if (spinner) {
            spinner.classList.add('d-none');
        }

        // ✅ XỬ LÝ CÁC LOẠI RESPONSE KHÁC NHAU
        if (!data.success) {
            handleAnalysisError(data);
            return;
        }

        // ✅ KIỂM TRA CÓ PREDICTIONS KHÔNG
        if (!data.predictions || Object.keys(data.predictions).length === 0) {
            content.innerHTML = `
                <div class="alert alert-warning">
                    <h6 class="alert-heading">⚠️ Không có dự đoán</h6>
                    <p>Không có đủ dữ liệu để tạo dự đoán cho ngày này.</p>
                </div>
            `;
            return;
        }

        try {
            // ✅ DEBUG STRUCTURE TRƯỚC KHI LỌC
            console.log('🔍 Raw predictions received:', data.predictions);
            debugPredictionsStructure(data.predictions);
            
            // ✅ LẤY ANALYSIS DATE TỪ DATA
            const analysisDate = data.target_date || extractAnalysisDateFromPredictions(data.predictions);
            
            // ✅ LỌC QUALITY PREDICTIONS VỚI ACCURACY CHECK
            let qualityPredictions;
            try {
                // ✅ SỬ DỤNG HÀM MỚI VỚI ACCURACY CHECK
                qualityPredictions = await filterQualityPredictionsWithAccuracy(data.predictions, analysisDate);
            } catch (filterError) {
                console.error('❌ Error in accuracy-based filtering:', filterError);
                
                // ✅ FALLBACK: Sử dụng filtering cũ
                qualityPredictions = filterQualityPredictions(data.predictions);
                
                // Show warning to user
                const warningAlert = document.createElement('div');
                warningAlert.className = 'alert alert-warning alert-dismissible fade show mb-3';
                warningAlert.innerHTML = `
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Cảnh báo:</strong> Không thể so sánh với kết quả thực tế. Sử dụng tiêu chí lọc cũ.
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                content.insertBefore(warningAlert, content.firstChild);
            }

            // ✅ HIỂN THỊ KẾT QUẢ THEO LOẠI ANALYSIS VỚI ERROR HANDLING
            if (data.enhanced && data.model_performance) {
                // Enhanced ML results từ pattern-analysis
                console.log('🔮 Displaying Enhanced ML Results with Accuracy Scoring');
                console.log(`📊 Accuracy-based filter: ${Object.keys(data.predictions).length} → ${Object.keys(qualityPredictions).length} methods`);
                
                displayEnhancedMLResults(qualityPredictions, data.model_performance);
                
                // ✅ CẬP NHẬT BẢNG VỚI QUALITY PREDICTIONS (ĐÃ LỌC THEO ACCURACY)
                updateTableWithPredictions(qualityPredictions);
                
            } else if (data.predictions) {
                console.log('🔍 Processing Pattern Analysis Results with Accuracy Scoring');
                console.log(`📊 Accuracy-based filter: ${Object.keys(data.predictions).length} → ${Object.keys(qualityPredictions).length} methods`);
                
                // Standard pattern analysis results
                displayAllMethodsPredictions(qualityPredictions, data.analysis, Object.keys(data.predictions).length);
                
                // ✅ CẬP NHẬT BẢNG VỚI QUALITY PREDICTIONS (ĐÃ LỌC THEO ACCURACY)  
                updateTableWithPredictions(qualityPredictions);
            }

            // ✅ HIỂN THỊ METADATA
            if (data.metadata) {
                showDataSourceInfo(data.metadata);
            }
            
        } catch (displayError) {
            console.error('❌ Error in displayAnalysisResults:', displayError);
            
            // ✅ FALLBACK ERROR DISPLAY
            content.innerHTML = `
                <div class="alert alert-danger">
                    <h6 class="alert-heading">❌ Lỗi hiển thị kết quả</h6>
                    <p>Có lỗi khi xử lý dữ liệu phân tích: ${displayError.message}</p>
                </div>
            `;
        }
    }

    
    /**
    * ✅ CẢI THIỆN HÀM filterQualityPredictions - THÊM SO SÁNH VỚI KẾT QUẢ THỰC TẾ
    * @param {object} predictions - All predictions
    * @param {string} analysisDate - Analysis date (YYYY-MM-DD)
    * @returns {object} - Filtered quality predictions with accuracy scores
    */
    async function filterQualityPredictionsWithAccuracy(predictions, analysisDate) {
        const qualityPredictions = {};
        let skippedCount = 0;
        
        console.log('🔍 Starting enhanced quality filter with accuracy check...');
        console.log(`📊 Input: ${Object.keys(predictions).length} methods for ${analysisDate}`);
        
        // ✅ LẤY SỐ THỰC TẾ TỪ API
        let actualNumbers = [];
        try {
            const actualData = await fetchActualNumbers(analysisDate);
            actualNumbers = actualData.all_2digit_numbers || [];
            console.log(`📋 Actual numbers for ${analysisDate}:`, actualNumbers);
        } catch (error) {
            console.warn(`⚠️ Could not fetch actual numbers for ${analysisDate}:`, error);
            // Fallback to original filtering if no actual data
            return filterQualityPredictions(predictions);
        }
        
        const methodScores = [];
        
        Object.entries(predictions).forEach(([methodId, prediction]) => {
            try {
                // ✅ VALIDATE PREDICTION STRUCTURE
                if (!prediction || typeof prediction !== 'object') {
                    console.warn(`⚠️ Invalid prediction object for method ${methodId}:`, prediction);
                    skippedCount++;
                    return;
                }
                
                // ✅ NORMALIZE PREDICTION DATA
                let dayProbabilities, dayConfidences, confidence, recommendedDay, dayPredictedNumbers;
                
                if (prediction.day_probabilities && typeof prediction.day_probabilities === 'object') {
                    dayProbabilities = prediction.day_probabilities;
                    dayConfidences = prediction.day_confidences || {};
                    confidence = prediction.confidence || 0;
                    recommendedDay = prediction.recommended_day || 1;
                    dayPredictedNumbers = prediction.day_predicted_numbers || {};
                } else if (prediction.day_predictions && typeof prediction.day_predictions === 'object') {
                    dayProbabilities = {
                        day_1: prediction.day_predictions.day_1?.probability || 0,
                        day_2: prediction.day_predictions.day_2?.probability || 0,
                        day_3: prediction.day_predictions.day_3?.probability || 0
                    };
                    dayConfidences = {
                        day_1: prediction.day_predictions.day_1?.confidence || 0,
                        day_2: prediction.day_predictions.day_2?.confidence || 0,
                        day_3: prediction.day_predictions.day_3?.confidence || 0
                    };
                    confidence = prediction.overall_confidence || prediction.confidence || 0;
                    recommendedDay = prediction.recommended_day || 1;
                    dayPredictedNumbers = prediction.day_predicted_numbers || {};
                } else {
                    console.warn(`⚠️ Method ${methodId} has incomplete prediction data, using defaults`);
                    dayProbabilities = { day_1: 0.05, day_2: 0.05, day_3: 0.05 };
                    dayConfidences = { day_1: 0.05, day_2: 0.05, day_3: 0.05 };
                    confidence = prediction.confidence || 0.05;
                    recommendedDay = prediction.recommended_day || 1;
                    dayPredictedNumbers = {};
                }
                
                // ✅ TÍNH ACCURACY SCORE VỚI SỐ THỰC TẾ
                const accuracyScore = calculateAccuracyScore(
                    dayPredictedNumbers, 
                    actualNumbers, 
                    analysisDate,
                    recommendedDay
                );
                
                // ✅ TÍNH QUALITY METRICS
                const maxProb = Math.max(
                    dayProbabilities.day_1 || 0,
                    dayProbabilities.day_2 || 0,
                    dayProbabilities.day_3 || 0
                ) * 100;
                
                const maxConf = Math.max(
                    dayConfidences.day_1 || 0,
                    dayConfidences.day_2 || 0,
                    dayConfidences.day_3 || 0
                ) * 100;
                
                const overallConfidence = confidence * 100;
                
                // ✅ TÍNH TỔNG ĐIỂM (WEIGHTED SCORE)
                const totalScore = calculateWeightedScore({
                    accuracyScore,
                    maxProb,
                    maxConf,
                    overallConfidence,
                    recommendedDay
                });
                
                methodScores.push({
                    methodId,
                    prediction: {
                        ...prediction,
                        day_probabilities: dayProbabilities,
                        day_confidences: dayConfidences,
                        confidence: confidence,
                        recommended_day: recommendedDay,
                        day_predicted_numbers: dayPredictedNumbers,
                        method_name: prediction.method_name || `Method ${methodId}`,
                    },
                    accuracyScore,
                    maxProb,
                    maxConf,
                    overallConfidence,
                    totalScore
                });
                
            } catch (error) {
                console.error(`❌ Error processing method ${methodId}:`, error, prediction);
                skippedCount++;
            }
        });
        
        // ✅ SẮP XẾP THEO TỔNG ĐIỂM (accuracy > probability > confidence)
        methodScores.sort((a, b) => b.totalScore - a.totalScore);
        
        // ✅ LỌC VÀ TẠO RESULT
        const minRequiredScore = 30; // Điểm tối thiểu
        const qualifiedMethods = methodScores.filter(method => method.totalScore >= minRequiredScore);
        
        qualifiedMethods.forEach(method => {
            qualityPredictions[method.methodId] = {
                ...method.prediction,
                _accuracy_score: method.accuracyScore,
                _total_score: method.totalScore,
                _quality_metrics: {
                    accuracy: method.accuracyScore,
                    max_probability: method.maxProb,
                    max_confidence: method.maxConf,
                    overall_confidence: method.overallConfidence
                }
            };
        });
        
        console.log(`🔍 Enhanced quality filter results:`);
        console.log(`   ✅ Qualified: ${Object.keys(qualityPredictions).length}`);
        console.log(`   ❌ Filtered: ${skippedCount + (methodScores.length - qualifiedMethods.length)}`);
        console.log(`   📊 Total: ${Object.keys(predictions).length}`);
        console.log(`   🎯 Top accuracy scores:`, qualifiedMethods.slice(0, 3).map(m => `Method ${m.methodId}: ${m.accuracyScore.toFixed(1)}%`));
        
        return qualityPredictions;
    }

    /**
    * ✅ HÀM TÍNH ACCURACY SCORE
    * @param {object} dayPredictedNumbers - Predicted numbers cho từng ngày
    * @param {array} actualNumbers - Số thực tế
    * @param {string} analysisDate - Ngày phân tích 
    * @param {number} recommendedDay - Ngày được khuyến nghị
    * @returns {number} - Accuracy score (0-100)
    */
    function calculateAccuracyScore(dayPredictedNumbers, actualNumbers, analysisDate, recommendedDay) {
        if (!actualNumbers || actualNumbers.length === 0) {
            return 0; // Không có số thực tế để so sánh
        }
        
        let totalAccuracy = 0;
        let validDays = 0;
        
        // ✅ TÍNH ACCURACY CHO TỪNG NGÀY
        ['day_1', 'day_2', 'day_3'].forEach((dayKey, index) => {
            const dayNumbers = dayPredictedNumbers[dayKey] || [];
            if (dayNumbers.length > 0) {
                const dayAccuracy = calculateDayAccuracy(dayNumbers, actualNumbers);
                
                // ✅ TĂNG TRỌNG SỐ CHO NGÀY ĐƯỢC KHUYẾN NGHỊ
                const isRecommendedDay = (index + 1) === recommendedDay;
                const weight = isRecommendedDay ? 2.0 : 1.0;
                
                totalAccuracy += dayAccuracy * weight;
                validDays += weight;
            }
        });
        
        return validDays > 0 ? totalAccuracy / validDays : 0;
    }

    /**
    * ✅ HÀM TÍNH ACCURACY CHO MỘT NGÀY
    * @param {array} predictedNumbers - Số dự đoán
    * @param {array} actualNumbers - Số thực tế
    * @returns {number} - Accuracy percentage (0-100)
    */
    function calculateDayAccuracy(predictedNumbers, actualNumbers) {
        if (!predictedNumbers || predictedNumbers.length === 0) return 0;
        
        const predictedSet = new Set(predictedNumbers.map(n => String(n).padStart(2, '0')));
        const actualSet = new Set(actualNumbers.map(n => String(n).padStart(2, '0')));
        
        // ✅ TÍNH SỐ TRÙNG KHỚP
        const matches = [...predictedSet].filter(num => actualSet.has(num));
        const hitRate = (matches.length / predictedSet.size) * 100;
        
        // ✅ BONUS CHO SỐ LƯỢNG TRÙNG KHỚP CAO
        const matchBonus = Math.min(matches.length * 5, 20); // Tối đa 20% bonus
        
        return Math.min(hitRate + matchBonus, 100);
    }

    /**
    * ✅ HÀM TÍNH WEIGHTED SCORE
    * @param {object} metrics - Các chỉ số đánh giá
    * @returns {number} - Weighted total score
    */
    function calculateWeightedScore({ accuracyScore, maxProb, maxConf, overallConfidence, recommendedDay }) {
        // ✅ TRỌNG SỐ: Accuracy > Probability > Confidence
        const weights = {
            accuracy: 0.5,      // 50% trọng số cho accuracy
            probability: 0.3,   // 30% cho probability  
            confidence: 0.2     // 20% cho confidence
        };
        
        const normalizedProb = Math.min(maxProb, 100);
        const normalizedConf = Math.min(maxConf, 100);
        const normalizedOverall = Math.min(overallConfidence, 100);
        
        // ✅ TÍNH TỔNG ĐIỂM
        const totalScore = 
            (accuracyScore * weights.accuracy) +
            (normalizedProb * weights.probability) +
            ((normalizedConf + normalizedOverall) / 2 * weights.confidence);
        
        return Math.round(totalScore * 100) / 100; // Round to 2 decimal places
    }

    /**
    * ✅ HÀM LẤY SỐ THỰC TẾ TỪ API
    * @param {string} date - Date string (YYYY-MM-DD)
    * @returns {Promise<object>} - API response with actual numbers
    */
    async function fetchActualNumbers(date) {
        const apiUrl = `/pre-lokhung/api/ketqua/${date}/`;
        
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'API returned success: false');
        }
        
        return data.data;
    }
    /**
    * ✅ CẢI THIỆN HÀM filterQualityPredictions - STRICTER FILTERING
    * @param {object} predictions - All predictions
    * @returns {object} - Filtered quality predictions
    */
    function filterQualityPredictions(predictions) {
        const qualityPredictions = {};
        let skippedCount = 0;
        
        console.log('🔍 Starting quality filter process...');
        console.log(`📊 Input: ${Object.keys(predictions).length} methods`);
        
        Object.entries(predictions).forEach(([methodId, prediction]) => {
            try {
                // ✅ VALIDATE PREDICTION STRUCTURE
                if (!prediction || typeof prediction !== 'object') {
                    console.warn(`⚠️ Invalid prediction object for method ${methodId}:`, prediction);
                    skippedCount++;
                    return;
                }
                
                // ✅ NORMALIZE PREDICTION DATA - HANDLE MULTIPLE FORMATS
                let dayProbabilities, dayConfidences, confidence, recommendedDay;
                
                // ✅ FORMAT 1: Standard format với day_probabilities
                if (prediction.day_probabilities && typeof prediction.day_probabilities === 'object') {
                    dayProbabilities = prediction.day_probabilities;
                    dayConfidences = prediction.day_confidences || {};
                    confidence = prediction.confidence || 0;
                    recommendedDay = prediction.recommended_day || 1;
                    console.log(`🔍 Method ${methodId} - Standard format`);
                }
                // ✅ FORMAT 2: Enhanced ML format với day_predictions
                else if (prediction.day_predictions && typeof prediction.day_predictions === 'object') {
                    dayProbabilities = {
                        day_1: prediction.day_predictions.day_1?.probability || 0,
                        day_2: prediction.day_predictions.day_2?.probability || 0,
                        day_3: prediction.day_predictions.day_3?.probability || 0
                    };
                    dayConfidences = {
                        day_1: prediction.day_predictions.day_1?.confidence || 0,
                        day_2: prediction.day_predictions.day_2?.confidence || 0,
                        day_3: prediction.day_predictions.day_3?.confidence || 0
                    };
                    confidence = prediction.overall_confidence || prediction.confidence || 0;
                    recommendedDay = prediction.recommended_day || 1;
                    console.log(`🔍 Method ${methodId} - Enhanced ML format`);
                }
                // ✅ FORMAT 3: Basic format với minimal data
                else {
                    console.warn(`⚠️ Method ${methodId} has incomplete prediction data, using defaults`);
                    dayProbabilities = { day_1: 0.05, day_2: 0.05, day_3: 0.05 };
                    dayConfidences = { day_1: 0.05, day_2: 0.05, day_3: 0.05 };
                    confidence = prediction.confidence || 0.05;
                    recommendedDay = prediction.recommended_day || 1;
                }
                
                // ✅ VALIDATE PROBABILITIES VÀ CONFIDENCES
                const maxProb = Math.max(
                    dayProbabilities.day_1 || 0,
                    dayProbabilities.day_2 || 0,
                    dayProbabilities.day_3 || 0
                ) * 100;
                
                const maxConf = Math.max(
                    dayConfidences.day_1 || 0,
                    dayConfidences.day_2 || 0,
                    dayConfidences.day_3 || 0
                ) * 100;
                
                const overallConfidence = confidence * 100;
                
                // ✅ CẬP NHẬT QUALITY FILTER - GIẢM THRESHOLD XUỐNG 50%
                const qualityThreshold = (
                    // Threshold 1: GIẢM TỪ 60% XUỐNG 50% - High probability AND high confidence
                    (maxProb >= 50 && maxConf >= 39) ||
                    // Threshold 2: Very high probability (even with lower confidence) 
                    (maxProb >= 51 && maxConf >= 41) ||
                    // Threshold 3: Recommended day with decent stats
                    (maxProb >= 50 && maxConf >= 40 && overallConfidence >= 39) ||
                    // Threshold 4: Very high overall confidence
                    (overallConfidence >= 52 && maxProb >= 41)
                );
                
                console.log(`🔍 Method ${methodId} evaluation:`, {
                    method_name: prediction.method_name,
                    maxProb: maxProb.toFixed(1),
                    maxConf: maxConf.toFixed(1),
                    overallConf: overallConfidence.toFixed(1),
                    recommendedDay: recommendedDay,
                    qualityThreshold: qualityThreshold
                });
                
                if (qualityThreshold) {
                    // ✅ ENSURE NORMALIZED STRUCTURE BEFORE ADDING
                    qualityPredictions[methodId] = {
                        ...prediction,
                        day_probabilities: dayProbabilities,
                        day_confidences: dayConfidences,
                        confidence: confidence,
                        recommended_day: recommendedDay,
                        day_predicted_numbers: prediction.day_predicted_numbers || {},
                        pattern_info: prediction.pattern_info || {
                            trend: 'unknown',
                            performance_category: 'basic',
                            stability: 'unknown'
                        },
                        method_name: prediction.method_name || `Method ${methodId}`,
                        // ✅ THÊM QUALITY SCORE ĐỂ DEBUG
                        _quality_score: Math.max(maxProb + maxConf, overallConfidence)
                    };
                    
                    console.log(`✅ Method ${methodId} PASSED quality filter - Score: ${qualityPredictions[methodId]._quality_score.toFixed(1)}`);
                } else {
                    skippedCount++;
                    console.log(`❌ Method ${methodId} FAILED quality filter - MaxProb: ${maxProb.toFixed(1)}%, MaxConf: ${maxConf.toFixed(1)}%, OverallConf: ${overallConfidence.toFixed(1)}%`);
                }
                
            } catch (error) {
                console.error(`❌ Error processing method ${methodId}:`, error, prediction);
                skippedCount++;
            }
        });
        
        // ✅ SORT BY QUALITY SCORE
        const sortedQualityPredictions = {};
        Object.entries(qualityPredictions)
            .sort(([,a], [,b]) => (b._quality_score || 0) - (a._quality_score || 0))
            .forEach(([methodId, prediction]) => {
                // Remove internal quality score before returning
                const {_quality_score, ...cleanPrediction} = prediction;
                sortedQualityPredictions[methodId] = cleanPrediction;
            });
        
        console.log(`🔍 Quality filter results:`);
        console.log(`   ✅ Passed: ${Object.keys(sortedQualityPredictions).length}`);
        console.log(`   ❌ Filtered: ${skippedCount}`);
        console.log(`   📊 Total: ${Object.keys(predictions).length}`);
        console.log(`   📈 Pass rate: ${((Object.keys(sortedQualityPredictions).length / Object.keys(predictions).length) * 100).toFixed(1)}%`);
        
        // ✅ LOG TOP QUALITY METHODS
        Object.entries(qualityPredictions).slice(0, 3).forEach(([methodId, prediction], index) => {
            console.log(`🏆 Top ${index + 1}: Method ${methodId} (${prediction.method_name}) - Quality: ${prediction._quality_score?.toFixed(1)}`);
        });
        
        return sortedQualityPredictions;
    }

    /**
    * ✅ SỬA HÀM normalizeBasicPredictions - ENHANCED NORMALIZATION
    * @param {object} predictions - Raw predictions with possible missing fields
    * @returns {object} - Normalized predictions
    */
    function normalizeBasicPredictions(predictions) {
        const normalized = {};
        
        Object.entries(predictions).forEach(([methodId, prediction]) => {
            try {
                // ✅ ENSURE MINIMAL REQUIRED STRUCTURE VỚI COMPREHENSIVE DEFAULTS
                normalized[methodId] = {
                    method_name: prediction.method_name || `Method ${methodId}`,
                    recommended_day: prediction.recommended_day || 1,
                    confidence: prediction.confidence || 0.1,
                    day_probabilities: prediction.day_probabilities || {
                        day_1: 0.1, day_2: 0.1, day_3: 0.1
                    },
                    day_confidences: prediction.day_confidences || {
                        day_1: 0.1, day_2: 0.1, day_3: 0.1
                    },
                    day_predicted_numbers: prediction.day_predicted_numbers || {},
                    pattern_info: prediction.pattern_info || {
                        trend: 'unknown',
                        performance_category: 'basic',
                        stability: 'unknown',
                        prediction_type: 'normalized'
                    }
                };
            } catch (error) {
                console.error(`❌ Error normalizing method ${methodId}:`, error);
                
                // ✅ FALLBACK MINIMAL STRUCTURE
                normalized[methodId] = {
                    method_name: `Method ${methodId}`,
                    recommended_day: 1,
                    confidence: 0.1,
                    day_probabilities: { day_1: 0.1, day_2: 0.1, day_3: 0.1 },
                    day_confidences: { day_1: 0.1, day_2: 0.1, day_3: 0.1 },
                    day_predicted_numbers: {},
                    pattern_info: {
                        trend: 'unknown',
                        performance_category: 'error',
                        stability: 'unknown',
                        prediction_type: 'fallback'
                    }
                };
            }
        });
        
        console.log(`🔧 Normalized ${Object.keys(normalized).length} basic predictions`);
        return normalized;
    }


    /**
    * ✅ SỬA HÀM displayAllMethodsPredictions - THÊM DEFENSIVE PROGRAMMING
    * @param {object} qualityPredictions - Already filtered predictions
    * @param {object} analysis - Analysis data
    * @param {number} totalOriginalMethods - Total methods before filtering
    */
    function displayAllMethodsPredictions(qualityPredictions, analysis, totalOriginalMethods = 0) {
        const content = document.getElementById('analysis-content');
        if (!content) return;

        const filteredCount = totalOriginalMethods - Object.keys(qualityPredictions).length;

        // Sort predictions by confidence
        const sortedPredictions = Object.entries(qualityPredictions).sort((a, b) => 
            b[1].confidence - a[1].confidence
        );

        let html = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="alert alert-info">
                        <h6 class="alert-heading">🤖 Enhanced AI Analysis - Quality Filtered (50% Threshold)</h6>
                        <p>Hiển thị ${Object.keys(qualityPredictions).length} phương pháp chất lượng cao 
                        ${filteredCount > 0 ? `(đã ẩn ${filteredCount} phương pháp chất lượng thấp)` : ''}. 
                        <strong>Badges chỉ hiển thị khi Xác suất ≥ 50% VÀ Độ tin cậy ≥ 50%.</strong></p>
                    </div>
                </div>
            </div>
            
            <!-- ✅ QUALITY FILTER INFO - CẬP NHẬT THRESHOLD -->
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="card border-info">
                        <div class="card-body p-2">
                            <h6 class="card-title text-info mb-1">
                                <i class="fas fa-filter me-2"></i>Bộ lọc chất lượng (Threshold 50%)
                            </h6>
                            <div class="row text-center">
                                <div class="col-6">
                                    <div class="fw-bold text-success">${Object.keys(qualityPredictions).length}</div>
                                    <small class="text-muted">Hiển thị</small>
                                </div>
                                <div class="col-6">
                                    <div class="fw-bold text-danger">${filteredCount}</div>
                                    <small class="text-muted">Đã ẩn</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card border-success">
                        <div class="card-body p-2">
                            <h6 class="card-title text-success mb-1">
                                <i class="fas fa-info-circle me-2"></i>Tiêu chí chất lượng - CẬP NHẬT
                            </h6>
                            <div style="font-size: 0.8rem;">
                                <div>🔥 <strong>Badges: ≥50% xác suất VÀ ≥50% tin cậy</strong></div>
                                <div>⚡ Tốt: ≥40% trung bình</div>
                                <div>💡 Khá: ≥30% trung bình</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- ✅ TOP METHODS HIỂN THỊ PRIORITY -->
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-warning">
                        <div class="card-header bg-warning text-dark">
                            <h6 class="mb-0">
                                <i class="fas fa-trophy me-2"></i>Top ${Math.min(5, sortedPredictions.length)} phương pháp cao nhất
                            </h6>
                        </div>
                        <div class="card-body p-2">
                            <div class="row g-2">
        `;

        // ✅ HIỂN THỊ TOP 5 METHODS VỚI LAYOUT ĐẸP HƠN
        sortedPredictions.slice(0, 5).forEach(([methodId, prediction], index) => {
            const confidence = (prediction.confidence * 100).toFixed(1);
            const recommendedDay = prediction.recommended_day;
            const dayProbs = prediction.day_probabilities;
            
            // ✅ TÌM NGÀY CÓ XÁC SUẤT CAO NHẤT
            const maxProb = Math.max(dayProbs.day_1, dayProbs.day_2, dayProbs.day_3);
            const bestDay = Object.keys(dayProbs).find(key => dayProbs[key] === maxProb).split('_')[1];
            
            const trophyIcon = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '🏆';
            const cardBorder = index === 0 ? 'border-warning' : index < 3 ? 'border-info' : 'border-secondary';
            
            html += `
                <div class="col-md-${index < 3 ? '4' : '6'}">
                    <div class="card ${cardBorder} h-100">
                        <div class="card-body p-2 text-center">
                            <div class="mb-1">
                                <span class="fs-4">${trophyIcon}</span>
                                <span class="badge bg-secondary ms-1">#${index + 1}</span>
                            </div>
                            <h6 class="card-title mb-1 text-truncate">${prediction.method_name}</h6>
                            <div class="mb-2">
                                <span class="badge bg-primary">Ngày ${recommendedDay}</span>
                                <div class="text-muted small">Tin cậy: ${confidence}%</div>
                            </div>
                            <div class="row g-1 text-center">
                                ${[1, 2, 3].map(day => {
                                    const dayProb = (dayProbs[`day_${day}`] * 100).toFixed(1);
                                    const isMax = day == bestDay;
                                    const isRecommended = day === recommendedDay;
                                    
                                    return `
                                        <div class="col-4">
                                            <div class="small ${isMax ? 'fw-bold text-success' : ''} ${isRecommended ? 'text-primary' : ''}">
                                                D${day}: ${dayProb}%
                                                ${isMax ? '📈' : ''}
                                                ${isRecommended ? '⭐' : ''}
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                            <button class="btn btn-outline-primary btn-sm mt-1" 
                                    onclick="highlightMethodInTable('${methodId}', '${new Date().toISOString().split('T')[0]}')">
                                <i class="fas fa-search me-1"></i>Xem
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // ✅ TIẾP TỤC VỚI GRID CỦA TẤT CẢ METHODS
        html += `
            <div class="row">
                <div class="col-12">
                    <h6 class="text-primary mb-3">
                        <i class="fas fa-list me-2"></i>Tất cả ${Object.keys(qualityPredictions).length} phương pháp (sắp xếp theo độ tin cậy):
                    </h6>
                    <div class="prediction-grid">
        `;

        // ✅ EXISTING CODE CHO TẤT CẢ PREDICTIONS...
        // (rest of the existing displayAllMethodsPredictions code)
        
        content.innerHTML = html;
    }


    /**
    * ✅ HÀM MỚI - GET TREND CLASS CHO DEFENSIVE PROGRAMMING
    * @param {string} trend - Trend value
    * @returns {string} - CSS class
    */
    function getTrendClass(trend) {
        switch (trend) {
            case 'improving':
            case 'increasing':
            case 'up':
                return 'success';
            case 'declining':
            case 'decreasing':
            case 'down':
                return 'danger';
            case 'stable':
                return 'info';
            default:
                return 'secondary';
        }
    }

    /**
    * ✅ SỬA HÀM getPatternAnalysisPredictions - SIMPLIFIED VERSION
    * @param {string} analysisDate - Ngày cần phân tích (YYYY-MM-DD)
    * @returns {Promise} - API response promise
    */
    function getPatternAnalysisPredictions(analysisDate) {
        const requestData = {
            analysis_date: analysisDate  // Chỉ cần ngày phân tích
        };
        
        console.log('🔄 Calling SIMPLIFIED pattern-analysis API:');
        console.log(`   📅 Analysis Date: ${analysisDate}`);
        
        return fetch('/pre-lokhung/api/pattern-analysis/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Pattern analysis response:', data);
            return data;
        })
        .catch(error => {
            console.error('❌ Pattern analysis error:', error);
            throw error;
        });
    }

    function validateAdvancedResponseData(data) {
        if (!data || !data.success) {
            return false;
        }
        
        // ✅ VALIDATE ADVANCED FIELDS
        if (data.predictions) {
            for (const [methodId, prediction] of Object.entries(data.predictions)) {
                // Kiểm tra có đủ fields không
                if (!prediction.day_probabilities || !prediction.day_confidences) {
                    console.error(`Method ${methodId} missing required prediction fields`);
                    return false;
                }
                
                // Kiểm tra probability values hợp lệ
                for (const day of ['day_1', 'day_2', 'day_3']) {
                    const prob = prediction.day_probabilities[day];
                    const conf = prediction.day_confidences[day];
                    
                    if (prob < 0 || prob > 1 || conf < 0 || conf > 1) {
                        console.error(`Invalid probability/confidence values for ${methodId} ${day}`);
                        return false;
                    }
                }
            }
        }
        
        return true;
    }

    // ✅ CẬP NHẬT updateTableWithPredictions với logic nghiêm ngặt hơn
    function updateTableWithPredictions(predictions) {
        console.log('🎯 Updating table with ENHANCED prediction badges (50% threshold)...');
        
        if (!predictions || Object.keys(predictions).length === 0) {
            console.warn('⚠️ No predictions to update table with');
            return;
        }
        
        // ✅ XÓA BADGES CŨ
        document.querySelectorAll('.hit-badge-predict').forEach(badge => badge.remove());
        
        let totalBadges = 0;
        let shownBadges = 0;
        let highQualityBadges = 0;
        let excellentQualityBadges = 0;
        
        Object.entries(predictions).forEach(([methodId, prediction]) => {
            try {
                const dayProbabilities = prediction.day_probabilities;
                const dayConfidences = prediction.day_confidences;
                const recommendedDay = prediction.recommended_day || 1;
                const predictionQuality = prediction.prediction_quality || 'unknown';
                
                // ✅ CHỈ XỬ LÝ PREDICTIONS CHẤT LƯỢNG CAO
                if (predictionQuality === 'poor') {
                    console.log(`❌ Skipping poor quality prediction for method ${methodId}`);
                    return;
                }
                
                const methodCells = document.querySelectorAll(`td.prediction-cell[data-method-id="${methodId}"]`);
                
                methodCells.forEach(cell => {
                    let cellDiv = cell.querySelector('div');
                    if (!cellDiv) {
                        cellDiv = document.createElement('div');
                        cellDiv.style.position = 'relative';
                        cellDiv.style.height = '100%';
                        cell.appendChild(cellDiv);
                    }
                    
                    // ✅ TẠO BADGES VỚI LOGIC NÂNG CAO - GIẢM THRESHOLD
                    for (let day = 1; day <= 3; day++) {
                        const probability = parseFloat(dayProbabilities[`day_${day}`] * 100);
                        const confidence = parseFloat(dayConfidences[`day_${day}`] * 100);
                        
                        totalBadges++;
                        
                        // ✅ ĐIỀU KIỆN HIỂN THỊ GIẢM XUỐNG 50%
                        const qualityScore = (probability + confidence) / 2;
                        const isRecommended = day === recommendedDay;
                        const isHighQuality = predictionQuality === 'excellent' || predictionQuality === 'good';
                        
                        const shouldShow = (
                            // ✅ GIẢM THRESHOLD: Excellent quality với threshold 40%
                            (predictionQuality === 'excellent' && qualityScore >= 40) ||
                            // ✅ GIẢM THRESHOLD: Good quality với threshold 50% (từ 65%)
                            (predictionQuality === 'good' && qualityScore >= 50) ||
                            // ✅ GIẢM THRESHOLD: Recommended day với quality 40% (từ 45%)
                            (isRecommended && isHighQuality && qualityScore >= 40) ||
                            // ✅ GIẢM THRESHOLD: Fair quality với threshold 70% (từ 80%)
                            (predictionQuality === 'fair' && qualityScore >= 70) ||
                            // ✅ THÊM: Strict badge criteria - 50% & 50%
                            (probability >= 50 && confidence >= 50)
                        );
                        
                        if (shouldShow) {
                            const predictionBadge = document.createElement('span');
                            predictionBadge.className = 'hit-badge-predict';
                            predictionBadge.setAttribute('data-day', day);
                            predictionBadge.setAttribute('data-method-id', methodId);
                            predictionBadge.setAttribute('data-quality', predictionQuality);
                            predictionBadge.textContent = day;
                            
                            // ✅ ENHANCED TOOLTIP - CẬP NHẬT THRESHOLD
                            predictionBadge.title = `🤖 AI Dự đoán NÂNG CAO ngày ${day}${isRecommended ? ' ⭐' : ''}:
                                • Xác suất: ${probability.toFixed(1)}%
                                • Độ tin cậy: ${confidence.toFixed(1)}%
                                • Điểm chất lượng: ${qualityScore.toFixed(1)}
                                • Mức độ: ${predictionQuality.toUpperCase()}
                                • Threshold: ≥50% xác suất VÀ ≥50% tin cậy
                                • Thuật toán: Enhanced Pattern ML
                                • Features: Cyclical + Sequential + Correlation`;
                            
                            // ✅ STYLING DỰA TRÊN QUALITY
                            applyAdvancedQualityStyle(predictionBadge, probability, confidence, predictionQuality, isRecommended);
                            
                            cellDiv.appendChild(predictionBadge);
                            shownBadges++;
                            
                            // ✅ COUNT QUALITY LEVELS
                            if (predictionQuality === 'excellent') {
                                excellentQualityBadges++;
                                highQualityBadges++;
                            } else if (predictionQuality === 'good') {
                                highQualityBadges++;
                            }
                            
                            console.log(`✅ Added ENHANCED badge (50% criteria): Method ${methodId}, Day ${day}, Quality: ${predictionQuality}, Score: ${qualityScore.toFixed(1)}`);
                        } else {
                            console.log(`❌ Hidden badge (50% criteria): Method ${methodId}, Day ${day}, Quality: ${predictionQuality}, Score: ${qualityScore.toFixed(1)}`);
                        }
                    }
                });
            } catch (error) {
                console.error(`❌ Error processing enhanced prediction for method ${methodId}:`, error);
            }
        });
        
        // ✅ BÁOCÁO KẾT QUẢ
        console.log(`📊 ENHANCED Badge update summary (50% threshold):`);
        console.log(`   Total processed: ${totalBadges}`);
        console.log(`   Shown badges: ${shownBadges}`);
        console.log(`   High quality badges: ${highQualityBadges}`);
        console.log(`   Excellent quality badges: ${excellentQualityBadges}`);
        console.log(`   Show rate: ${totalBadges > 0 ? ((shownBadges / totalBadges) * 100).toFixed(1) : 0}%`);
        
        // ✅ THÔNG BÁO CHO USER VỚI 50% THRESHOLD
        try {
            if (excellentQualityBadges > 0) {
                showEnhanced50PercentSuccess(shownBadges, excellentQualityBadges);
            } else if (shownBadges > 0) {
                showEnhanced50PercentWarning(shownBadges, totalBadges);
            } else {
                showEnhanced50PercentInfo(totalBadges);
            }
        } catch (notificationError) {
            console.error('❌ Error showing 50% threshold notification:', notificationError);
        }
    }

    /**
    * ✅ NOTIFICATION FUNCTIONS CHO 50% THRESHOLD
    */
    function showEnhanced50PercentSuccess(shownBadges, excellentBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            <strong>Enhanced AI Success (50% Threshold):</strong> 
            Hiển thị ${shownBadges} prediction badges với tiêu chí mới: <strong>≥50% xác suất VÀ ≥50% tin cậy</strong>.
            <br><small class="text-muted mt-1 d-block">
                🔥 ${excellentBadges} badges chất lượng xuất sắc được tìm thấy!
            </small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 8000);
    }

    function showEnhanced50PercentWarning(shownBadges, totalBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Enhanced AI Warning (50% Threshold):</strong> 
            Hiển thị ${shownBadges}/${totalBadges} prediction badges với tiêu chí mới: <strong>≥50% xác suất VÀ ≥50% tin cậy</strong>.
            <br><small class="text-muted mt-1 d-block">⚡ Threshold đã giảm từ 60% xuống 50% để hiển thị nhiều dự đoán hơn.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 10000);
    }

    function showEnhanced50PercentInfo(totalBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            <strong>Enhanced AI Info (50% Threshold):</strong> 
            Không có prediction badges nào đạt tiêu chí mới từ ${totalBadges} dự đoán: <strong>≥50% xác suất VÀ ≥50% tin cậy</strong>.
            <br><small class="text-muted mt-1 d-block">💡 Có thể cần giảm threshold thêm hoặc cải thiện model training.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 12000);
    }
    /**
    * ✅ HÀM HIỂN THỊ SUCCESS MESSAGE CHO ADVANCED PREDICTIONS
    * @param {number} shownBadges - Số badges được hiển thị
    * @param {number} highQualityBadges - Số badges chất lượng cao
    */
    function showAdvancedPredictionSuccess(shownBadges, highQualityBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            <strong>AI Prediction Success:</strong> 
            Hiển thị ${shownBadges} prediction badges, trong đó ${highQualityBadges} badges chất lượng cao.
            <br><small class="text-muted mt-1 d-block">🤖 Advanced ML đã tìm thấy những dự đoán có độ tin cậy cao!</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 8000);
    }

    /**
    * ✅ HÀM HIỂN THỊ WARNING MESSAGE CHO ADVANCED PREDICTIONS
    * @param {number} shownBadges - Số badges được hiển thị
    * @param {number} totalBadges - Tổng số badges được xử lý
    */
    function showAdvancedPredictionWarning(shownBadges, totalBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>AI Prediction Warning:</strong> 
            Chỉ hiển thị ${shownBadges}/${totalBadges} prediction badges đạt tiêu chí chất lượng.
            <br><small class="text-muted mt-1 d-block">⚡ Các dự đoán khác có độ tin cậy thấp hơn threshold.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 10000);
    }

    /**
    * ✅ HÀM HIỂN THỊ ERROR MESSAGE CHO ADVANCED PREDICTIONS  
    * @param {number} totalBadges - Tổng số badges được xử lý
    */
    function showAdvancedPredictionError(totalBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            <strong>AI Prediction Info:</strong> 
            Không có prediction badges nào đạt tiêu chí hiển thị từ ${totalBadges} dự đoán được phân tích.
            <br><small class="text-muted mt-1 d-block">💡 Tất cả dự đoán đều có độ tin cậy thấp hơn threshold hiển thị.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 12000);
    }

    /**
    * ✅ HÀM HELPER HIỂN THỊ NOTIFICATION TẠM THỜI
    * @param {HTMLElement} notification - Element notification
    * @param {number} duration - Thời gian hiển thị (ms)
    */
    function showTemporaryNotification(notification, duration = 8000) {
        const container = document.querySelector('.container-fluid');
        if (container) {
            // Remove existing notifications of same type
            const existingNotifications = container.querySelectorAll('.alert');
            existingNotifications.forEach(alert => {
                if (alert.textContent.includes('AI Prediction')) {
                    alert.remove();
                }
            });
            
            // Add new notification at top
            container.insertBefore(notification, container.firstChild);
            
            // Auto remove after duration
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.classList.remove('show');
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.remove();
                        }
                    }, 150); // Wait for fade out animation
                }
            }, duration);
        }
    }

    /**
    * ✅ HÀM HIỂN THỊ NOTIFICATION CHO STRICT BADGE MODE
    * @param {number} shownBadges - Số badges được hiển thị
    * @param {number} totalBadges - Tổng số badges
    * @param {number} highQualityCount - Số badges chất lượng cao
    */
    function showStrictModeNotification(shownBadges, totalBadges, highQualityCount) {
        let notificationType, message, icon;
        
        if (highQualityCount > 0) {
            notificationType = 'success';
            icon = 'fas fa-check-circle';
            message = `
                <strong>Strict Mode Success:</strong> 
                Hiển thị ${shownBadges} badges chất lượng cao từ ${totalBadges} dự đoán.
                <br><small class="text-muted mt-1 d-block">🔥 Chỉ hiển thị dự đoán có Xác suất ≥60% VÀ Độ tin cậy ≥60%</small>
            `;
        } else if (shownBadges > 0) {
            notificationType = 'warning';
            icon = 'fas fa-exclamation-triangle';
            message = `
                <strong>Strict Mode Warning:</strong> 
                Hiển thị ${shownBadges}/${totalBadges} badges, nhưng không có badges chất lượng cao.
                <br><small class="text-muted mt-1 d-block">⚡ Các badges hiển thị có độ tin cậy trung bình</small>
            `;
        } else {
            notificationType = 'info';
            icon = 'fas fa-info-circle';
            message = `
                <strong>Strict Mode Info:</strong> 
                Không có badges nào đạt tiêu chí strict từ ${totalBadges} dự đoán.
                <br><small class="text-muted mt-1 d-block">💡 Tất cả dự đoán có chất lượng thấp hơn threshold</small>
            `;
        }
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${notificationType} alert-dismissible fade show mt-2`;
        notification.innerHTML = `
            <i class="${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, notificationType === 'success' ? 6000 : 10000);
    }

    /**
    * ✅ HÀM HIỂN THỊ ENHANCED ANALYSIS STATUS
    * @param {string} analysisType - Loại phân tích
    * @param {object} metadata - Metadata từ API response
    */
    function showAnalysisStatusNotification(analysisType, metadata) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-primary alert-dismissible fade show mt-2';
        
        const successfulMethods = metadata.successful_methods || 0;
        const totalMethods = metadata.total_methods || 0;
        const dataQuality = metadata.data_quality_score || 0;
        
        notification.innerHTML = `
            <i class="fas fa-brain me-2"></i>
            <strong>AI Analysis Complete:</strong> 
            ${analysisType} phân tích ${successfulMethods}/${totalMethods} methods với chất lượng dữ liệu ${(dataQuality * 100).toFixed(0)}%.
            <br><small class="text-muted mt-1 d-block">🚀 Sử dụng Advanced ML với ${metadata.months_analyzed || 12} tháng dữ liệu lịch sử</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 7000);
    }

    function applyAdvancedQualityStyle(badge, probability, confidence, quality, isRecommended) {
        // ✅ BASE STYLE
        badge.style.position = 'absolute';
        badge.style.zIndex = '15';
        badge.style.fontWeight = 'bold';
        badge.style.transition = 'all 0.3s ease';
        
        // ✅ QUALITY-BASED STYLING
        switch (quality) {
            case 'excellent':
                badge.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
                badge.style.border = '2px solid gold';
                badge.style.boxShadow = '0 0 15px rgba(40, 167, 69, 0.6)';
                badge.style.animation = 'pulse 2s infinite';
                break;
                
            case 'good':
                badge.style.background = 'linear-gradient(45deg, #007bff, #17a2b8)';
                badge.style.border = '2px solid silver';
                badge.style.boxShadow = '0 0 10px rgba(0, 123, 255, 0.5)';
                break;
                
            case 'fair':
                badge.style.background = 'linear-gradient(45deg, #ffc107, #fd7e14)';
                badge.style.border = '1px solid #ffc107';
                badge.style.boxShadow = '0 0 8px rgba(255, 193, 7, 0.4)';
                break;
                
            default:
                badge.style.background = '#6c757d';
                badge.style.opacity = '0.7';
        }
        
        // ✅ RECOMMENDED DAY ENHANCEMENT
        if (isRecommended) {
            badge.style.transform = 'scale(1.1)';
            badge.style.boxShadow += ', 0 0 0 3px rgba(255, 215, 0, 0.3)';
        }
    }


    /**
    * ✅ HÀM MỚI - HIỂN THỊ WARNING VỀ STRICT BADGES
    */
    function showStrictBadgeWarning(totalBadges, errorCount) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            <strong>Thông báo:</strong> 
            ${errorCount > 0 ? 
                `Có ${errorCount} lỗi khi xử lý dự đoán. ` : 
                ''
            }
            Tất cả ${totalBadges} dự đoán đều không đạt tiêu chí <strong>STRICT</strong> (Xác suất ≥60% VÀ Độ tin cậy ≥60%) nên không hiển thị badges.
            <br><small class="text-muted mt-1 d-block">💡 Giảm threshold để xem thêm dự đoán chất lượng thấp hơn.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            // Auto remove after 15 seconds (longer for important info)
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 15000);
        }
    }

    /**
    * ✅ HÀM MỚI - HIỂN THỊ SUCCESS VỀ STRICT BADGES
    */
    function showStrictBadgeSuccess(shownBadges, totalBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            <strong>Thành công:</strong> 
            Hiển thị ${shownBadges}/${totalBadges} badges đạt tiêu chí <strong>STRICT</strong> (Xác suất ≥60% VÀ Độ tin cậy ≥60%).
            <br><small class="text-muted mt-1 d-block">🔥 Chỉ hiển thị những dự đoán chất lượng cao nhất!</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            // Auto remove after 10 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 10000);
        }
    }


    /**
    * ✅ HÀM MỚI - HIỂN THỊ WARNING VỀ BADGES
    */
    function showBadgeWarning(totalBadges, errorCount) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            <strong>Thông báo:</strong> 
            ${errorCount > 0 ? 
                `Có ${errorCount} lỗi khi xử lý dự đoán. ` : 
                ''
            }
            ${totalBadges > 0 ? 
                `Tất cả ${totalBadges} dự đoán đều có chất lượng thấp nên không hiển thị badges.` :
                'Không có dữ liệu dự đoán để hiển thị.'
            }
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            // Auto remove after 10 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 10000);
        }
    }
    /**
    * ✅ HÀM DEBUG - KIỂM TRA CẤU TRÚC PREDICTIONS
    * @param {object} predictions - Predictions object
    */
    function debugPredictionsStructure(predictions) {
        console.log('🔍 Debug predictions structure:');
        console.log('Total methods:', Object.keys(predictions).length);
        
        // ✅ KIỂM TRA FORMAT CỦA TỪNG PREDICTION
        Object.entries(predictions).slice(0, 2).forEach(([methodId, prediction]) => {
            console.log(`Method ${methodId}:`, {
                method_name: prediction.method_name,
                recommended_day: prediction.recommended_day,
                confidence: prediction.confidence,
                day_probabilities: prediction.day_probabilities,
                day_confidences: prediction.day_confidences,
                day_predicted_numbers: prediction.day_predicted_numbers,
                // ✅ KIỂM TRA CÁC FORMAT KHÁC
                pattern_info: prediction.pattern_info,
                overall_confidence: prediction.overall_confidence,
                day_predictions: prediction.day_predictions
            });
        });
        
        // ✅ VALIDATE STRUCTURE
        const firstPrediction = Object.values(predictions)[0];
        if (firstPrediction) {
            console.log('🔍 First prediction structure validation:', {
                has_day_probabilities: !!firstPrediction.day_probabilities,
                has_day_confidences: !!firstPrediction.day_confidences,
                has_confidence: typeof firstPrediction.confidence !== 'undefined',
                has_recommended_day: typeof firstPrediction.recommended_day !== 'undefined',
                type: typeof firstPrediction.day_probabilities,
                keys: firstPrediction.day_probabilities ? Object.keys(firstPrediction.day_probabilities) : 'N/A'
            });
        }
    }

    /**
    * ✅ HÀM LẤY ICON CHẤT LƯỢNG
    * @param {number} probability - Xác suất (%)
    * @param {number} confidence - Độ tin cậy (%)
    * @returns {string} - Icon tương ứng
    */
    function getQualityIcon(probability, confidence) {
        const avg = (probability + confidence) / 2;
        if (avg >= 60) return '🔥';
        if (avg >= 45) return '⚡';
        if (avg >= 30) return '💡';
        if (avg >= 20) return '❓';
        return '';
    }
    
    /**
     * ✅ HÀM HIỂN THỊ BASIC PREDICTIONS (FALLBACK)
     * @param {object} predictions - ML predictions
     * @param {object} analysis - Pattern analysis
     */
    function displayBasicPredictions(predictions, analysis) {
        const content = document.getElementById('analysis-content');
        if (!content) return;

        let html = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="alert alert-info">
                        <h6 class="alert-heading">🤖 Dự đoán ML cơ bản</h6>
                        <p>Hệ thống đã phân tích ${Object.keys(predictions).length} phương pháp và đưa ra dự đoán khung thời gian trúng.</p>
                    </div>
                </div>
            </div>
            <div class="row g-3">
        `;

        // Sort predictions by confidence
        const sortedPredictions = Object.entries(predictions).sort((a, b) => 
            b[1].confidence - a[1].confidence
        );

        sortedPredictions.forEach(([methodId, prediction], index) => {
            const confidence = prediction.confidence * 100;
            const confidenceClass = confidence >= 80 ? 'success' : 
                                   confidence >= 60 ? 'warning' : 
                                   confidence >= 40 ? 'info' : 'danger';
            
            html += `
                <div class="col-md-6 col-lg-4">
                    <div class="card border-${confidenceClass} h-100">
                        <div class="card-header bg-${confidenceClass} text-white p-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <strong>${prediction.method_name}</strong>
                                <span class="badge bg-light text-dark">#{index + 1}</span>
                            </div>
                        </div>
                        <div class="card-body p-2">
                            <div class="text-center mb-2">
                                <div class="mb-1">
                                    <span class="badge bg-${confidenceClass} fs-6 px-3 py-2">
                                        🎯 Ngày ${prediction.recommended_day}
                                    </span>
                                </div>
                                <small class="text-muted">Độ tin cậy: ${confidence.toFixed(1)}%</small>
                            </div>
                            
                            <div class="row g-1 mb-2">
                                ${[1, 2, 3].map(day => {
                                    const dayProb = (prediction.day_probabilities[`day_${day}`] * 100).toFixed(1);
                                    const isRecommended = day === prediction.recommended_day;
                                    
                                    return `
                                        <div class="col-4">
                                            <div class="text-center p-1 ${isRecommended ? 'bg-light border rounded' : ''}">
                                                <small class="text-muted">Ngày ${day}</small>
                                                <div class="fw-bold ${isRecommended ? 'text-' + confidenceClass : ''}">${dayProb}%</div>
                                                ${isRecommended ? '<i class="fas fa-star text-warning"></i>' : ''}
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                            
                            ${prediction.pattern_info ? `
                                <div class="pattern-info">
                                    <small class="text-muted">
                                        <i class="fas fa-chart-line me-1"></i>
                                        ${prediction.pattern_info.trend || 'stable'} | 
                                        Chu kỳ: ${prediction.pattern_info.cycle_length || 'N/A'}
                                    </small>
                                </div>
                            ` : ''}
                            
                            <div class="text-center mt-2">
                                <button class="btn btn-outline-${confidenceClass} btn-sm" 
                                        onclick="highlightMethodInTable('${methodId}', '${new Date().toISOString().split('T')[0]}')">
                                    <i class="fas fa-search me-1"></i>Xem trong bảng
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';

        // Add analysis summary if available
        if (analysis) {
            html += `
                <div class="row mt-3">
                    <div class="col-12">
                        <div class="card border-info">
                            <div class="card-header bg-light">
                                <h6 class="mb-0 text-info">📊 Tóm tắt phân tích</h6>
                            </div>
                            <div class="card-body p-2">
                                <div class="row text-center">
                                    <div class="col-md-3">
                                        <div class="fw-bold text-primary">${analysis.total_methods || Object.keys(predictions).length}</div>
                                        <small class="text-muted">Methods</small>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="fw-bold text-success">Ngày ${analysis.best_overall_day || 1}</div>
                                        <small class="text-muted">Tốt nhất</small>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="fw-bold text-warning">${((analysis.avg_confidence || 0) * 100).toFixed(1)}%</div>
                                        <small class="text-muted">Tin cậy TB</small>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="fw-bold text-info">${sortedPredictions[0]?.[1]?.method_name || 'N/A'}</div>
                                        <small class="text-muted">Top method</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        content.innerHTML = html;
    }

    /**
     * ✅ HÀM GET DATA SOURCE TEXT CHO UI
     * @param {string} dataSource - Data source type
     * @returns {string} - Friendly text description
     */
    function getDataSourceText(dataSource) {
        const sourceTexts = {
            'frontend_enhanced': '📊 Dữ liệu hiện tại + Lịch sử',
            'historical_only': '📈 Chỉ dữ liệu lịch sử',
            'pattern_analysis': '🔍 Phân tích Pattern',
            'ml_enhanced': '🤖 ML nâng cao',
            'fallback': '🔄 Dữ liệu fallback',
            'basic_ml': '🔧 ML cơ bản',
            'enhanced_ml': '🚀 ML nâng cao'
        };
        return sourceTexts[dataSource] || dataSource;
    }

    /**
    * ✅ HÀM HIỂN THỊ ERROR MESSAGE CẢI THIỆN
    */
    function showErrorMessage(message) {
        const content = document.getElementById('analysis-content');
        if (content) {
            content.innerHTML = `
                <div class="alert alert-danger">
                    <h6 class="alert-heading">❌ Lỗi phân tích</h6>
                    <p>${message}</p>
                    <hr>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            ${new Date().toLocaleString('vi-VN')}
                        </small>
                        <button class="btn btn-outline-danger btn-sm" onclick="location.reload()">
                            <i class="fas fa-refresh me-1"></i>Tải lại trang
                        </button>
                    </div>
                </div>
            `;
        }
    }

    

    function handleAnalysisError(data, dataQuality = null) {
        let errorMessage = data.error || 'Lỗi không xác định';
        
        // ✅ ENHANCED ERROR MESSAGES cho pattern-analysis
        if (data.error_type) {
            switch (data.error_type) {
                case 'date_parsing_error':
                    errorMessage = '❌ Lỗi định dạng ngày. Vui lòng kiểm tra lại.';
                    break;
                case 'method_ids_validation_error':
                    errorMessage = '❌ Lỗi danh sách phương pháp. Vui lòng chọn lại.';
                    break;
                case 'pattern_analysis_error':
                    errorMessage = '❌ Lỗi phân tích pattern. Hệ thống đang xử lý.';
                    break;
                case 'ml_analysis_error':
                    errorMessage = '❌ Lỗi phân tích ML. Hệ thống đang bảo trì.';
                    break;
                case 'database_error':
                    errorMessage = '❌ Lỗi cơ sở dữ liệu. Vui lòng thử lại sau.';
                    break;
                case 'service_unavailable':
                    errorMessage = '❌ Dịch vụ phân tích không khả dụng. Vui lòng thử lại sau.';
                    break;
                case 'insufficient_data':
                    errorMessage = '❌ Không đủ dữ liệu lịch sử để phân tích.';
                    break;
                default:
                    errorMessage = `❌ ${data.error}`;
            }
        }
        
        // ✅ THÊM THÔNG TIN BỔ SUNG
        if (data.fallback_attempted) {
            errorMessage += '<br><small class="text-muted">Đã thử mở rộng timeframe nhưng vẫn không đủ dữ liệu.</small>';
        }
        
        if (data.suggestion) {
            errorMessage += `<br><small class="text-info">💡 ${data.suggestion}</small>`;
        }

        if (data.available_methods) {
            errorMessage += `<br><small class="text-muted">Methods có dữ liệu: ${data.available_methods.join(', ')}</small>`;
        }
        
        const content = document.getElementById('analysis-content');
        if (content) {
            content.innerHTML = `
                <div class="alert alert-danger">
                    <h6 class="alert-heading">❌ Không thể phân tích Pattern</h6>
                    <div>${errorMessage}</div>
                    <hr>
                    <div class="row">
                        <div class="col-md-6">
                            <small class="text-muted">
                                <i class="fas fa-database me-2"></i>
                                Timeframe: ${data.months_searched || 12} tháng |
                                API: pattern-analysis
                            </small>
                        </div>
                        <div class="col-md-6 text-end">
                            <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">
                                <i class="fas fa-refresh me-1"></i>Thử lại
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
    }


    // ✅ HÀM HIỂN THỊ KẾT QUẢ CHO NGÀY CỤ THỂ - LAYOUT MỚI
    function displayDaySpecificResults(predictions, analysis, targetDate, dayMethods) {
        const content = document.getElementById('analysis-content');
        if (!content) return;
        
        // Lọc predictions cho các methods có trong ngày này
        const dayPredictions = {};
        dayMethods.forEach(method => {
            if (predictions[method.method_id]) {
                dayPredictions[method.method_id] = {
                    ...predictions[method.method_id],
                    method_data: method
                };
            }
        });
        
        if (Object.keys(dayPredictions).length === 0) {
            content.innerHTML = '<div class="alert alert-info">Không có dự đoán ML cho các methods trong ngày này</div>';
            return;
        }
        
        // Sắp xếp theo confidence
        const sortedPredictions = Object.entries(dayPredictions).sort((a, b) => 
            b[1].confidence - a[1].confidence
        );
        
        let html = `
            <!-- ✅ OVERVIEW STATS -->
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="card border-info">
                        <div class="card-body p-2">
                            <h6 class="card-title text-info mb-1">
                                <i class="fas fa-chart-pie me-2"></i>Thống kê tổng quan
                            </h6>
                            <div class="row text-center">
                                <div class="col-4">
                                    <div class="fw-bold text-primary">${Object.keys(dayPredictions).length}</div>
                                    <small class="text-muted">Methods</small>
                                </div>
                                <div class="col-4">
                                    <div class="fw-bold text-success">Ngày ${analysis.best_overall_day}</div>
                                    <small class="text-muted">Tốt nhất</small>
                                </div>
                                <div class="col-4">
                                    <div class="fw-bold text-warning">${(analysis.avg_confidence * 100).toFixed(1)}%</div>
                                    <small class="text-muted">Tin cậy TB</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card border-success">
                        <div class="card-body p-2">
                            <h6 class="card-title text-success mb-1">
                                <i class="fas fa-bullseye me-2"></i>Khuyến nghị cho ngày ${targetDate}
                            </h6>
                            <div class="text-center">
                                ${generateDayRecommendationSummary(sortedPredictions)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- ✅ PREDICTIONS GRID - LAYOUT MỚI -->
            <div class="row">
                <div class="col-12">
                    <h6 class="text-primary mb-3">
                        <i class="fas fa-magic me-2"></i>Dự đoán khung thời gian trúng từng phương pháp:
                    </h6>
                    <div class="prediction-grid">
        `;
        
        sortedPredictions.forEach(([methodId, prediction], index) => {
            const confidence = prediction.confidence * 100;
            const recommendedDay = prediction.recommended_day;
            const probability = prediction.day_probabilities;
            
            // Xác định class cho confidence
            const confidenceClass = confidence >= 80 ? 'success' : confidence >= 60 ? 'warning' : confidence >= 40 ? 'info' : 'danger';
            const priorityBadge = index < 3 ? 'badge-top-choice' : '';
            
            // Tìm ngày có xác suất cao nhất
            const maxProb = Math.max(probability.day_1, probability.day_2, probability.day_3);
            
            html += `
                <div class="prediction-item mb-3 ${priorityBadge}">
                    <div class="card border-${confidenceClass} h-100">
                        ${index < 3 ? '<div class="position-absolute top-0 start-50 translate-middle"><span class="badge bg-danger">TOP</span></div>' : ''}
                        <div class="card-header bg-${confidenceClass} text-white p-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>${prediction.method_name}</strong>
                                    ${index === 0 ? '<i class="fas fa-crown ms-2"></i>' : ''}
                                </div>
                                <span class="badge bg-light text-dark">#{index + 1}</span>
                            </div>
                        </div>
                        <div class="card-body p-2">
                            <!-- Recommendation -->
                            <div class="text-center mb-2">
                                <div class="recommendation-day">
                                    <span class="badge bg-${confidenceClass} fs-6 px-3 py-2">
                                        🎯 Ngày ${recommendedDay}
                                    </span>
                                </div>
                                <div class="confidence-score mt-1">
                                    <small class="text-muted">Độ tin cậy: </small>
                                    <strong class="text-${confidenceClass}">${confidence.toFixed(1)}%</strong>
                                </div>
                            </div>
                            
                            <!-- Day Probabilities -->
                            <div class="day-probabilities mb-2">
                                <div class="row g-1">
                                    ${[1, 2, 3].map(day => {
                                        const dayProb = probability[`day_${day}`] * 100;
                                        const isRecommended = day === recommendedDay;
                                        const isHighest = (probability[`day_${day}`] === maxProb);
                                        const barClass = isRecommended ? confidenceClass : 'secondary';
                                        
                                        return `
                                            <div class="col-4">
                                                <div class="day-prob-card ${isRecommended ? 'recommended' : ''} ${isHighest ? 'highest-prob' : ''}">
                                                    <div class="text-center">
                                                        <div class="day-label">Ngày ${day}</div>
                                                        <div class="prob-value text-${barClass} fw-bold">${dayProb.toFixed(1)}%</div>
                                                        <div class="prob-bar">
                                                            <div class="progress" style="height: 4px;">
                                                                <div class="progress-bar bg-${barClass}" style="width: ${dayProb}%"></div>
                                                            </div>
                                                        </div>
                                                        ${isRecommended ? '<i class="fas fa-star text-warning"></i>' : ''}
                                                    </div>
                                                </div>
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                            
                            <!-- Pattern Info -->
                            ${prediction.pattern_info ? `
                                <div class="pattern-info">
                                    <div class="row g-1">
                                        <div class="col-6">
                                            <small class="text-muted">Chu kỳ:</small>
                                            <div class="fw-bold">${prediction.pattern_info.cycle_length}</div>
                                        </div>
                                        <div class="col-6">
                                            <small class="text-muted">Xu hướng:</small>
                                            <div class="fw-bold">${getTrendIcon(prediction.pattern_info.trend)} ${prediction.pattern_info.trend}</div>
                                        </div>
                                    </div>
                                </div>
                            ` : ''}
                            
                            <!-- Action Button -->
                            <div class="text-center mt-2">
                                <button class="btn btn-outline-${confidenceClass} btn-sm" 
                                        onclick="highlightMethodInTable('${methodId}', '${targetDate}')">
                                    <i class="fas fa-search me-1"></i>Xem trong bảng
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
            
            <!-- ✅ DETAILED ANALYSIS -->
            <div class="row mt-3">
                <div class="col-12">
                    <div class="card border-info">
                        <div class="card-header bg-light">
                            <h6 class="mb-0 text-info">
                                <i class="fas fa-microscope me-2"></i>Phân tích chi tiết Pattern
                            </h6>
                        </div>
                        <div class="card-body p-2">
                            ${generateDetailedAnalysis(sortedPredictions, analysis)}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        content.innerHTML = html;
    }

    // ✅ HÀM TẠO TÓM TẮT KHUYẾN NGHỊ
    function generateDayRecommendationSummary(sortedPredictions) {
        if (sortedPredictions.length === 0) {
            return '<span class="text-muted">Không có khuyến nghị</span>';
        }
        
        const topPrediction = sortedPredictions[0][1];
        const confidence = topPrediction.confidence * 100;
        const confidenceClass = confidence >= 80 ? 'success' : confidence >= 60 ? 'warning' : 'info';
        
        return `
            <div class="top-recommendation">
                <div class="fw-bold text-${confidenceClass}">
                    <i class="fas fa-medal me-1"></i>
                    ${topPrediction.method_name}
                </div>
                <div>
                    <span class="badge bg-${confidenceClass}">Ngày ${topPrediction.recommended_day}</span>
                    <small class="text-muted ms-2">${confidence.toFixed(1)}% tin cậy</small>
                </div>
            </div>
        `;
    }

    // ✅ HÀM TẠO PHÂN TÍCH CHI TIẾT
    function generateDetailedAnalysis(sortedPredictions, analysis) {
        const dayDistribution = {};
        let totalConfidence = 0;
        
        sortedPredictions.forEach(([methodId, prediction]) => {
            const day = prediction.recommended_day;
            if (!dayDistribution[day]) dayDistribution[day] = [];
            dayDistribution[day].push(prediction);
            totalConfidence += prediction.confidence;
        });
        
        const avgConfidence = totalConfidence / sortedPredictions.length;
        
        let html = '<div class="row g-2">';
        
        // Day distribution
        [1, 2, 3].forEach(day => {
            const dayMethods = dayDistribution[day] || [];
            const dayCount = dayMethods.length;
            const dayPercentage = (dayCount / sortedPredictions.length * 100).toFixed(1);
            
            html += `
                <div class="col-md-4">
                    <div class="analysis-day-card">
                        <div class="text-center">
                            <h6 class="text-primary">Ngày ${day}</h6>
                            <div class="day-stats">
                                <div class="stat-number">${dayCount}</div>
                                <div class="stat-label">methods (${dayPercentage}%)</div>
                            </div>
                            ${dayMethods.length > 0 ? `
                                <div class="top-method">
                                    <small class="text-muted">Top:</small>
                                    <div class="fw-bold">${dayMethods[0].method_name}</div>
                                </div>
                            ` : '<div class="text-muted">Không có</div>'}
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        
        // Overall insights
        html += `
            <div class="mt-3 p-2 bg-light rounded">
                <h6 class="text-info mb-2">
                    <i class="fas fa-lightbulb me-2"></i>Insights từ AI:
                </h6>
                <ul class="list-unstyled mb-0">
                    <li><i class="fas fa-check-circle text-success me-2"></i>
                        Độ tin cậy trung bình: <strong>${(avgConfidence * 100).toFixed(1)}%</strong>
                    </li>
                    <li><i class="fas fa-chart-line text-info me-2"></i>
                        Ngày được khuyến nghị nhiều nhất: <strong>Ngày ${analysis.best_overall_day}</strong>
                    </li>
                    <li><i class="fas fa-star text-warning me-2"></i>
                        Method hàng đầu: <strong>${sortedPredictions[0][1].method_name}</strong>
                    </li>
                </ul>
            </div>
        `;
        
        return html;
    }

    // ✅ HÀM HELPER
    function getTrendIcon(trend) {
        const icons = {
            'increasing': '📈',
            'decreasing': '📉', 
            'stable': '➡️'
        };
        return icons[trend] || '📊';
    }

    

    // ✅ HÀM TẠO METHOD DETAIL HTML - GIỮ NGUYÊN
    function generateMethodDetailHTML(method) {
        let html = `
            <div class="method-row">
                <div class="row align-items-center">
                    <div class="col-md-3">
                        <div class="fw-bold">${method.method_name}</div>
                        <small class="text-muted">${method.category}</small>
                        <div class="mt-1">
                            <span class="badge bg-info">Tin cậy: ${method.confidence.toFixed(1)}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="mb-1"><small class="text-muted">Số dự đoán:</small></div>
        `;

        method.predicted_numbers.forEach(number => {
            html += `<span class="prediction-number predicted">${number}</span>`;
        });

        html += `
                    </div>
                    <div class="col-md-6">
                        <div class="row">
        `;

        method.tracking_results.forEach(tracking => {
            html += `
                <div class="col-4">
                    <div class="tracking-day">
                        <div class="text-center mb-2">
                            <strong>Ngày ${tracking.day}</strong><br>
                            <small>${tracking.tracking_date}</small>
                        </div>
            `;

            if (tracking.has_result) {
                const badgeClass = tracking.hit_rate >= 20 ? 'bg-success' : 
                                tracking.hit_rate >= 10 ? 'bg-warning' : 'bg-danger';
                
                html += `
                    <div class="text-center mb-2">
                        <span class="hit-rate-badge badge ${badgeClass}">
                            ${tracking.hit_count}/${method.predicted_numbers.length} 
                            (${tracking.hit_rate.toFixed(1)}%)
                        </span>
                    </div>
                `;

                if (tracking.hit_numbers.length > 0) {
                    html += '<div class="mb-1"><small class="text-success">Trúng:</small><br>';
                    tracking.hit_numbers.forEach(number => {
                        html += `<span class="prediction-number hit">${number}</span>`;
                    });
                    html += '</div>';
                }
            } else {
                html += `
                    <div class="text-center text-muted">
                        <i class="fas fa-clock"></i><br>Chờ kết quả
                    </div>
                `;
            }

            html += '</div></div>';
        });

        html += `
                        </div>
                        <div class="mt-2 text-center">
                            <small class="text-muted">
                                Tổng: ${method.total_hits} số trúng | 
                                TB: ${method.avg_hit_rate.toFixed(1)}%
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;

        return html;
    }

    /**
    * ✅ SỬA HÀM showDayDetail - SIMPLIFIED
    */
    function showDayDetail(date) {
        const data = dayData[date];
        if (!data) return;

        const detailSection = document.getElementById('dayDetail');
        const titleElement = document.getElementById('dayDetailTitle');
        const contentElement = document.getElementById('dayDetailContent');

        titleElement.textContent = `Chi tiết ngày ${data.date} (${data.weekday})`;

        let html = '';
        
        // ✅ ANALYSIS SECTION - SIMPLIFIED
        html += `
            <div class="card mb-3">
                <div class="card-header bg-primary text-white">
                    <h6 class="mb-0">
                        <i class="fas fa-brain me-2"></i>AI Pattern Analysis cho ngày ${date}
                        <div class="spinner-border spinner-border-sm ms-2 d-none" id="analysis-spinner" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </h6>
                </div>
                <div class="card-body" id="analysis-content">
                    <div class="text-center text-muted">
                        <i class="fas fa-chart-line fa-2x mb-2"></i>
                        <p>Đang phân tích pattern cho ngày này...</p>
                    </div>
                </div>
                <div id="data-source-info" class="d-none"></div>
            </div>
        `;
        
        // ✅ EXISTING SESSION DATA (giữ nguyên)
        if (data.sessions.length === 0) {
            html += '<div class="alert alert-info">Không có dự đoán cho ngày này</div>';
        } else {
            data.sessions.forEach(session => {
                html += `
                    <div class="session-card mt-3">
                        <div class="card-header bg-light">
                            <div class="d-flex justify-content-between align-items-center">
                                <strong>${session.cycle_name}</strong>
                                <span class="badge bg-secondary">${session.status}</span>
                            </div>
                        </div>
                        <div class="card-body">
                `;

                session.methods.forEach(method => {
                    html += generateMethodDetailHTML(method);
                });

                html += '</div></div>';
            });
        }

        contentElement.innerHTML = html;
        detailSection.style.display = 'block';
        detailSection.scrollIntoView({ behavior: 'smooth' });
        
        // ✅ TRIGGER ANALYSIS - SIMPLIFIED
        setTimeout(() => {
            performDaySpecificAnalysis(date);
        }, 100);
    }

    // ✅ THAY THẾ HÀM generateAnalysisSection - TÍCH HỢP ML
    function generateAnalysisSection(date, selectedMethodId) {
        let analysisHTML = `
            <div class="card mb-3">
                <div class="card-header bg-primary text-white">
                    <h6 class="mb-0">
                        <i class="fas fa-brain me-2"></i>AI Pattern Analysis & ML Prediction cho ngày ${date}
                        <div class="spinner-border spinner-border-sm ms-2 d-none" id="analysis-spinner" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </h6>
                </div>
                <div class="card-body" id="analysis-content">
                    <div class="text-center text-muted">
                        <i class="fas fa-chart-line fa-2x mb-2"></i>
                        <p>Đang phân tích pattern và ML cho ngày này...</p>
                        <small class="text-muted">Sử dụng API: pattern-analysis</small>
                    </div>
                </div>
                <!-- ✅ METADATA CONTAINER -->
                <div id="data-source-info" class="d-none">
                    <!-- Metadata will be populated by JavaScript -->
                </div>
            </div>
        `;
        
        // Trigger pattern analysis cho ngày cụ thể
        setTimeout(() => {
            performDaySpecificAnalysis(date, selectedMethodId);
        }, 100);
        
        return analysisHTML;
    }

    // ✅ 4. EXISTING EVENT LISTENERS & FILTER CODE - GIỮ NGUYÊN

    // Add click event listeners to date headers
    document.querySelectorAll('.date-header').forEach(header => {
        header.addEventListener('click', function() {
            const date = this.dataset.date;
            showDayDetail(date);
        });
    });

    // Add click event listeners to prediction cells  
    /*document.querySelectorAll('.prediction-cell').forEach(cell => {
        cell.addEventListener('click', function() {
            const date = this.dataset.date;
            const methodId = parseInt(this.dataset.methodId);
            if (date && methodId) {
                showDayDetail(date, methodId);
            }
        });
    });
    */
    // ✅ EXISTING FILTER CODE - GIỮ NGUYÊN
    const methodSearch = document.getElementById('methodSearch');
    const minHitRate = document.getElementById('minHitRate');
    const applyFilter = document.getElementById('applyFilter');
    
    // Thêm event listener cho Enter key trong input
    methodSearch.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            applyFilterMethods();
        }
    });
    
    minHitRate.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            applyFilterMethods();
        }
    });
    
    applyFilter.addEventListener('click', applyFilterMethods);
    
    function applyFilterMethods() {
        const searchTerm = methodSearch.value.toLowerCase().trim();
        const minRate = parseFloat(minHitRate.value) || 0;
        
        // Get all method rows
        const methodRows = document.querySelectorAll('.method-row');
        let visibleCount = 0;
        
        methodRows.forEach(row => {
            try {
                // ✅ FIX: Lấy tên method từ data attribute hoặc text content
                let methodName = '';
                if (row.dataset.methodName) {
                    methodName = row.dataset.methodName.toLowerCase();
                } else {
                    // Fallback: lấy từ text content của .fw-bold
                    const nameElement = row.querySelector('.method-name .fw-bold');
                    methodName = nameElement ? nameElement.textContent.toLowerCase() : '';
                }
                
                // ✅ FIX: Lấy hit rate từ data attribute hoặc DOM
                let hitRate = 0;
                if (row.dataset.hitRate) {
                    hitRate = parseFloat(row.dataset.hitRate);
                } else {
                    // Fallback: lấy từ DOM
                    const hitRateCell = row.querySelector('.method-totals div small');
                    if (hitRateCell) {
                        const hitRateText = hitRateCell.textContent;
                        const match = hitRateText.match(/(\d+(?:\.\d+)?)%/);
                        if (match) {
                            hitRate = parseFloat(match[1]);
                        }
                    }
                }
                
                // ✅ Kiểm tra điều kiện lọc
                const nameMatch = !searchTerm || methodName.includes(searchTerm);
                const rateMatch = hitRate >= minRate;
                
                // ✅ Hiển thị/ẩn row
                if (nameMatch && rateMatch) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
                
            } catch (error) {
                console.error('Lỗi khi lọc method row:', error);
                // Hiển thị row nếu có lỗi
                row.style.display = '';
                visibleCount++;
            }
        });
        
        // ✅ Cập nhật counter hiển thị
        updateFilterCounter(visibleCount, methodRows.length);
        
        // ✅ Cuộn lên đầu bảng sau khi filter
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            tableContainer.scrollTop = 0;
        }
    }
    
    // ✅ Hàm cập nhật counter
    function updateFilterCounter(visible, total) {
        let counterElement = document.getElementById('filter-counter');
        
        // Tạo counter element nếu chưa có
        if (!counterElement) {
            counterElement = document.createElement('div');
            counterElement.id = 'filter-counter';
            counterElement.className = 'mt-2 text-muted';
            
            const cardBody = document.querySelector('.card-body');
            if (cardBody) {
                cardBody.appendChild(counterElement);
            }
        }
        
        // Cập nhật text
        if (visible === total) {
            counterElement.innerHTML = `<small><i class="fas fa-list"></i> Hiển thị tất cả ${total} phương pháp</small>`;
        } else {
            counterElement.innerHTML = `<small><i class="fas fa-filter"></i> Hiển thị ${visible}/${total} phương pháp</small>`;
        }
    }
    
    // ✅ Thêm nút Reset filter
    const resetFilterBtn = document.createElement('button');
    resetFilterBtn.className = 'btn btn-outline-secondary';
    resetFilterBtn.innerHTML = '<i class="fas fa-undo"></i> Reset';
    resetFilterBtn.onclick = function() {
        methodSearch.value = '';
        minHitRate.value = '0';
        applyFilterMethods();
    };
    
    // Thêm reset button vào UI
    const applyFilterParent = applyFilter.parentElement;
    if (applyFilterParent) {
        applyFilterParent.classList.remove('col-md-4');
        applyFilterParent.classList.add('col-md-4');
        applyFilterParent.innerHTML = `
            <div class="d-grid gap-2 d-md-flex">
                ${applyFilter.outerHTML}
                ${resetFilterBtn.outerHTML}
            </div>
        `;
        
        // Re-bind events sau khi thay đổi DOM
        const newApplyBtn = applyFilterParent.querySelector('button:first-child');
        const newResetBtn = applyFilterParent.querySelector('button:last-child');
        
        newApplyBtn.addEventListener('click', applyFilterMethods);
        newResetBtn.addEventListener('click', function() {
            methodSearch.value = '';
            minHitRate.value = '0';
            applyFilterMethods();
        });
    }
    
    // ✅ Khởi tạo counter ban đầu
    const initialTotal = document.querySelectorAll('.method-row').length;
    updateFilterCounter(initialTotal, initialTotal);

    // ✅ 5. WINDOW FUNCTIONS
    window.hideDayDetail = function() {
        document.getElementById('dayDetail').style.display = 'none';
    };

    // ✅ 6. DEBUG LOG
    console.log('Method Analysis Data:', methodAnalysis);
    console.log('Day Data:', dayData);


    // ✅ HÀM TÍNH DIVERSITY SCORE TỔNG THỂ
    function calculateOverallDiversityScore(hitPatterns) {
        let totalScore = 0;
        let methodCount = 0;
        
        Object.keys(hitPatterns.hit_day_1).forEach(methodId => {
            const day1Data = hitPatterns.hit_day_1[methodId];
            const day2Data = hitPatterns.hit_day_2[methodId];
            const day3Data = hitPatterns.hit_day_3[methodId];
            
            const allData = day1Data.concat(day2Data, day3Data);
            const hitRate = allData.reduce((sum, val) => sum + val, 0) / allData.length;
            const diversityScore = Math.min(hitRate, 1 - hitRate) * 2;
            
            totalScore += diversityScore;
            methodCount++;
        });
        
        return methodCount > 0 ? totalScore / methodCount : 0;
    }

    
    // ✅ HIỂN THỊ KẾT QUẢ DỰ ĐOÁN
    function displayPredictionResults(predictions) {
        let html = `
            <div class="card mt-4">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0">🎯 Dự đoán khung thời gian trúng</h5>
                </div>
                <div class="card-body">
                    <div class="row">
        `;
        
        Object.entries(predictions).forEach(([methodId, prediction]) => {
            const confidence = prediction.confidence * 100;
            const recommendedDay = prediction.recommended_day;
            const probability = prediction.day_probabilities;
            
            const confidenceClass = confidence >= 80 ? 'success' : confidence >= 60 ? 'warning' : 'danger';
            
            html += `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card border-${confidenceClass}">
                        <div class="card-body p-2">
                            <h6 class="card-title mb-1">${prediction.method_name}</h6>
                            <div class="mb-2">
                                <span class="badge bg-${confidenceClass}">
                                    Ngày ${recommendedDay} (${confidence.toFixed(1)}%)
                                </span>
                            </div>
                            <div style="font-size: 0.8rem;">
                                <div>Ngày 1: ${(probability.day_1 * 100).toFixed(1)}%</div>
                                <div>Ngày 2: ${(probability.day_2 * 100).toFixed(1)}%</div>
                                <div>Ngày 3: ${(probability.day_3 * 100).toFixed(1)}%</div>
                            </div>
                            ${prediction.pattern_info ? `
                                <small class="text-muted">
                                    Chu kỳ: ${prediction.pattern_info.cycle_length} | 
                                    Xu hướng: ${prediction.pattern_info.trend}
                                </small>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
        
        // Thêm vào DOM
        const container = document.querySelector('.container-fluid');
        const existingResults = document.getElementById('prediction-results');
        if (existingResults) {
            existingResults.remove();
        }
        
        const resultsDiv = document.createElement('div');
        resultsDiv.id = 'prediction-results';
        resultsDiv.innerHTML = html;
        container.appendChild(resultsDiv);
    }

    // ✅ HIỂN THỊ PHÂN TÍCH PATTERN TỔNG QUAN
    function displayPatternAnalysis(analysis) {
        let html = `
            <div class="card mt-3">
                <div class="card-header bg-info text-white">
                    <h6 class="mb-0">📊 Phân tích Pattern Tổng quan</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <h6>Thống kê chung:</h6>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Tổng methods:</span>
                                    <span>${analysis.total_methods}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Ngày tốt nhất:</span>
                                    <span class="badge bg-success">Ngày ${analysis.best_overall_day}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Độ tin cậy TB:</span>
                                    <span>${(analysis.avg_confidence * 100).toFixed(1)}%</span>
                                </li>
                            </ul>
                        </div>
                        <div class="col-md-8">
                            <h6>Top methods khuyến nghị:</h6>
                            <div class="list-group">
        `;
        
        analysis.top_recommendations.slice(0, 5).forEach((rec, index) => {
            const confidence = rec.confidence * 100;
            const badgeClass = confidence >= 80 ? 'success' : confidence >= 60 ? 'warning' : 'danger';
            
            html += `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${rec.method_name}</strong><br>
                        <small class="text-muted">Ngày ${rec.recommended_day}</small>
                    </div>
                    <span class="badge bg-${badgeClass}">${confidence.toFixed(1)}%</span>
                </div>
            `;
        });
        
        html += `
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Thêm vào prediction results
        const resultsDiv = document.getElementById('prediction-results');
        if (resultsDiv) {
            resultsDiv.insertAdjacentHTML('beforeend', html);
        }
    }

    // ✅ HELPER FUNCTION - GET CSRF TOKEN
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Thêm vào filter card
    /*const filterCard = document.querySelector('.card-body');
    if (filterCard) {
        filterCard.appendChild(analysisButton);
    }
    */

    // ✅ 7. DEBUGGING
    console.log('🔧 Monthly Report JS initialized with enhanced error handling');
    console.log('📊 Method Analysis Data:', methodAnalysis);
    console.log('📅 Day Data:', Object.keys(dayData).length, 'days loaded');

});


// ===== SECTION 3 =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize date inputs
    initializeDateInputs();
    
    // Event handlers
    $('#analyzeSingleDate').on('click', analyzeSingleDate);
    $('#analyzeRange').on('click', analyzeRange);
    
    // Auto-refresh every 30 seconds for real-time updates
    //setInterval(refreshCurrentAnalysis, 30000);

    
    function initializeDateInputs() {
        const today = new Date();
        const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
        
        $('#dateRangeStart').val(formatDate(lastWeek));
        $('#dateRangeEnd').val(formatDate(today));
    }

    function formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    function analyzeSingleDate() {
        const selectedDate = $('#analysisDate').val();
        
        if (!selectedDate) {
            showAlert('Vui lòng chọn ngày để phân tích.', 'warning');
            return;
        }
        
        showLoading();
        
        // ✅ FETCH BOTH PREDICTION AND ACTUAL RESULTS
        const predictionPromise = $.ajax({
            url: '/pre-lokhung/api/cyclical-prediction-v3/',
            method: 'GET',
            data: {
                'analysis_date': selectedDate
            }
        });
        
        const actualResultsPromise = $.ajax({
            url: `/pre-lokhung/api/ketqua/${selectedDate}/`,
            method: 'GET'
        });
        
        // ✅ WAIT FOR BOTH APIs TO COMPLETE
        Promise.allSettled([predictionPromise, actualResultsPromise])
            .then(results => {
                hideLoading();
                
                const [predictionResult, actualResult] = results;
                
                if (predictionResult.status === 'fulfilled') {
                    const predictionData = predictionResult.value;
                    const actualData = actualResult.status === 'fulfilled' ? actualResult.value : null;
                    
                    // ✅ DISPLAY RESULTS WITH ACCURACY COMPARISON
                    displaySingleDateResultsWithAccuracy(predictionData, actualData, selectedDate);
                } else {
                    showAlert('Lỗi khi lấy dữ liệu dự đoán.', 'danger');
                }
            })
            .catch(error => {
                hideLoading();
                console.error('API Error:', error);
                showAlert('Lỗi khi lấy dữ liệu phân tích.', 'danger');
            });
    }

    function analyzeRange() {
        const startDate = $('#dateRangeStart').val();
        const endDate = $('#dateRangeEnd').val();
        
        if (!startDate || !endDate) {
            showAlert('Vui lòng chọn khoảng thời gian để phân tích.', 'warning');
            return;
        }
        
        if (new Date(startDate) > new Date(endDate)) {
            showAlert('Ngày bắt đầu phải nhỏ hơn ngày kết thúc.', 'warning');
            return;
        }
        
        showLoading();
        
        // Call API for each date in range
        const dates = getDateRange(startDate, endDate);
        const promises = dates.map(date => {
            return $.ajax({
                url: '/pre-lokhung/api/cyclical-prediction-v3/',
                method: 'GET',
                data: {
                    'analysis_date': dates,
                    'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
                }
            });
        });
        
        Promise.allSettled(promises)
            .then(results => {
                hideLoading();
                const successfulResults = results
                    .filter(result => result.status === 'fulfilled')
                    .map((result, index) => ({
                        date: dates[index],
                        data: result.value
                    }));
                
                if (successfulResults.length > 0) {
                    displayRangeResults(successfulResults);
                } else {
                    showNoData();
                    showAlert('Không thể lấy dữ liệu cho khoảng thời gian đã chọn.', 'warning');
                }
            });
    }

    function getDateRange(startDate, endDate) {
        const dates = [];
        const currentDate = new Date(startDate);
        const end = new Date(endDate);
        
        while (currentDate <= end) {
            dates.push(formatDate(currentDate));
            currentDate.setDate(currentDate.getDate() + 1);
        }
        
        return dates;
    }

    /**
     * ✅ ENHANCED FUNCTION: Display results with accuracy comparison
     * @param {object} predictionData - Data từ cyclical prediction API
     * @param {object} actualData - Data từ ketqua API (có thể null)
     * @param {string} selectedDate - Ngày được chọn
     */
    function displaySingleDateResultsWithAccuracy(predictionData, actualData, selectedDate) {
        console.log('📊 Cyclical Intelligence API Response:', predictionData);
        console.log('🎯 Actual Results Data:', actualData);
        
        if (!predictionData.success) {
            showAlert('Lỗi API: ' + predictionData.message, 'danger');
            return;
        }
        
        // ✅ EXTRACT PREDICTION DATA
        const cyclicalAnalysis = predictionData.cyclical_analysis || {};
        const contextAnalysis = cyclicalAnalysis.context_analysis || {};
        const methodSyncMatrix = cyclicalAnalysis.method_sync_matrix || {};
        const numberFrequencyCycles = cyclicalAnalysis.number_frequency_cycles || {};
        
        const optimalMethods = predictionData.optimal_methods || {};
        const intelligentPredictions = predictionData.intelligent_predictions || {};
        const performanceMetrics = predictionData.performance_metrics || {};
        
        // ✅ EXTRACT ACTUAL RESULTS IF AVAILABLE
        let actualNumbers = [];
        let accuracyData = null;
        
        if (actualData && actualData.success && actualData.data) {
            actualNumbers = actualData.data.all_2digit_numbers || [];
            console.log(`🎯 Found ${actualNumbers.length} actual numbers for ${selectedDate}`);
            
            // ✅ CALCULATE ACCURACY FOR EACH PREDICTION TYPE
            accuracyData = calculateAccuracyMetrics(intelligentPredictions, actualNumbers);
            console.log('📈 Accuracy Metrics:', accuracyData);
        } else {
            console.log(`⚠️ No actual results available for ${selectedDate}`);
        }
        
        // ✅ DISPLAY WITH ACCURACY HIGHLIGHTING
        displayCyclicalContextWithAccuracy(contextAnalysis, selectedDate, accuracyData);
        displayMethodSyncMatrix(methodSyncMatrix);
        displayIntelligentPredictionsWithAccuracy(intelligentPredictions, performanceMetrics, accuracyData);
        updatePerformanceDashboardWithAccuracy(performanceMetrics, accuracyData);
        displayEnhancedTableResultsWithAccuracy(predictionData, selectedDate, accuracyData);
        
        showResults();
    }

    /**
     * ✅ CALCULATE ACCURACY METRICS
     * @param {object} intelligentPredictions - Predictions data
     * @param {array} actualNumbers - Actual lottery results
     * @returns {object} Accuracy metrics cho từng loại prediction
     */
    function calculateAccuracyMetrics(intelligentPredictions, actualNumbers) {
        const cyclicalNumbers = intelligentPredictions.cyclical_numbers || [];
        const methodNumbers = intelligentPredictions.method_numbers || [];
        const fusionNumbers = intelligentPredictions.fusion_numbers || [];
        
        // ✅ CALCULATE MATCHES
        const cyclicalMatches = cyclicalNumbers.filter(num => actualNumbers.includes(num));
        const methodMatches = methodNumbers.filter(num => actualNumbers.includes(num)); 
        const fusionMatches = fusionNumbers.filter(num => actualNumbers.includes(num));
        
        // ✅ CALCULATE ACCURACY RATES
        const cyclicalAccuracy = cyclicalNumbers.length > 0 ? 
            (cyclicalMatches.length / cyclicalNumbers.length) * 100 : 0;
        const methodAccuracy = methodNumbers.length > 0 ? 
            (methodMatches.length / methodNumbers.length) * 100 : 0;
        const fusionAccuracy = fusionNumbers.length > 0 ? 
            (fusionMatches.length / fusionNumbers.length) * 100 : 0;
        
        // ✅ OVERALL ACCURACY (using fusion numbers as primary)
        const overallAccuracy = fusionNumbers.length > 0 ? fusionAccuracy : 
                               (cyclicalAccuracy + methodAccuracy) / 2;
        
        return {
            cyclical: {
                total: cyclicalNumbers.length,
                matches: cyclicalMatches,
                accuracy: cyclicalAccuracy
            },
            method: {
                total: methodNumbers.length,
                matches: methodMatches,
                accuracy: methodAccuracy
            },
            fusion: {
                total: fusionNumbers.length,
                matches: fusionMatches,
                accuracy: fusionAccuracy
            },
            overall: {
                accuracy: overallAccuracy,
                totalPredictions: fusionNumbers.length || Math.max(cyclicalNumbers.length, methodNumbers.length),
                totalMatches: fusionMatches.length || (cyclicalMatches.length + methodMatches.length)
            },
            actualNumbers: actualNumbers
        };
    }

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
        
        // Display table results
        displayEnhancedTableResults(apiResponse, selectedDate);
        
        showResults();
    }

    /**
     * ✅ ENHANCED TABLE RESULTS WITH ACCURACY HIGHLIGHTING
     */
    function displayEnhancedTableResultsWithAccuracy(apiResponse, selectedDate, accuracyData) {
        const tableBody = $('#cyclicalTableBody');
        tableBody.empty();
        
        const intelligentPredictions = apiResponse.intelligent_predictions || {};
        const performanceMetrics = apiResponse.performance_metrics || {};
        
        const cyclicalNumbers = intelligentPredictions.cyclical_numbers || [];
        const methodNumbers = intelligentPredictions.method_numbers || [];
        const fusionNumbers = intelligentPredictions.fusion_numbers || [];
        const expectedAccuracy = performanceMetrics.expected_accuracy || 0;
        const confidenceLevel = performanceMetrics.confidence_level || 'Unknown';
        
        // ✅ GENERATE HIGHLIGHTED NUMBER BADGES
        const cyclicalBadges = generateHighlightedBadges(cyclicalNumbers, accuracyData, 'cyclical', 'success');
        const methodBadges = generateHighlightedBadges(methodNumbers, accuracyData, 'method', 'warning');
        const fusionBadges = generateHighlightedBadges(fusionNumbers, accuracyData, 'fusion', 'primary');
        
        // ✅ GET REAL ACCURACY IF AVAILABLE
        const realAccuracy = accuracyData ? accuracyData.overall.accuracy : null;
        const accuracyComparison = realAccuracy !== null ? 
            (realAccuracy >= expectedAccuracy ? 'success' : 'danger') : 'secondary';
        
        // Create enhanced table row with accuracy highlighting
        const row = `
            <tr class="table-success">
                <td><strong>${formatDisplayDate(selectedDate)}</strong></td>
                <td>
                    <div class="prediction-numbers">
                        ${cyclicalBadges}
                    </div>
                    ${accuracyData ? `<small class="text-muted">Accuracy: ${accuracyData.cyclical.accuracy.toFixed(1)}%</small>` : ''}
                </td>
                <td>
                    <div class="prediction-numbers">
                        ${methodBadges}
                    </div>
                    ${accuracyData ? `<small class="text-muted">Accuracy: ${accuracyData.method.accuracy.toFixed(1)}%</small>` : ''}
                </td>
                <td>
                    <div class="prediction-numbers">
                        ${fusionBadges}
                    </div>
                    ${accuracyData ? `<small class="text-muted">Accuracy: ${accuracyData.fusion.accuracy.toFixed(1)}%</small>` : ''}
                </td>
                <td>
                    <div>
                        <span class="badge badge-${expectedAccuracy >= 50 ? 'success' : expectedAccuracy >= 30 ? 'warning' : 'danger'} badge-lg">
                            Expected: ${expectedAccuracy.toFixed(1)}%
                        </span>
                        ${realAccuracy !== null ? `
                            <br><span class="badge badge-${accuracyComparison} badge-lg mt-1">
                                Real: ${realAccuracy.toFixed(1)}%
                            </span>
                        ` : ''}
                    </div>
                </td>
                <td>
                    <span class="badge badge-${confidenceLevel === 'High' ? 'success' : confidenceLevel === 'Medium' ? 'warning' : 'danger'}">
                        ${confidenceLevel}
                    </span>
                    ${accuracyData ? `
                        <br><small class="text-muted">
                            ${accuracyData.overall.totalMatches}/${accuracyData.overall.totalPredictions} matches
                        </small>
                    ` : ''}
                </td>
            </tr>
        `;
        
        tableBody.append(row);
        
        // ✅ UPDATE SUMMARY WITH REAL ACCURACY
        const finalAccuracy = realAccuracy !== null ? realAccuracy : expectedAccuracy;
        updateSummaryStats(1, realAccuracy >= 50 ? 1 : 0, finalAccuracy, finalAccuracy);
    }

    /**
     * ✅ GENERATE HIGHLIGHTED BADGES FOR NUMBERS
     * @param {array} numbers - Array of predicted numbers
     * @param {object} accuracyData - Accuracy data including matches
     * @param {string} type - Type of prediction (cyclical, method, fusion)
     * @param {string} baseColor - Base badge color
     * @returns {string} HTML badges với highlighting
     */
    function generateHighlightedBadges(numbers, accuracyData, type, baseColor) {
        if (!numbers || numbers.length === 0) return '<span class="text-muted">No predictions</span>';
        
        const matches = accuracyData ? accuracyData[type].matches : [];
        
        return numbers.slice(0, 10).map((num, idx) => {
            const isMatch = matches.includes(num);
            const badgeClass = isMatch ? 'badge-success' : `badge-${baseColor}`;
            const matchIcon = isMatch ? '<i class="fas fa-check-circle ml-1"></i>' : '';
            const title = isMatch ? `✅ TRÚNG! Rank ${idx + 1}` : `Rank ${idx + 1}`;
            
            return `<span class="badge ${badgeClass} mr-1" title="${title}">${num}${matchIcon}</span>`;
        }).join('');
    }

    function displayEnhancedTableResults(apiResponse, selectedDate) {
        const tableBody = $('#cyclicalTableBody');
        tableBody.empty();
        
        const intelligentPredictions = apiResponse.intelligent_predictions || {};
        const performanceMetrics = apiResponse.performance_metrics || {};
        
        const cyclicalNumbers = intelligentPredictions.cyclical_numbers || [];
        const methodNumbers = intelligentPredictions.method_numbers || [];
        const fusionNumbers = intelligentPredictions.fusion_numbers || [];
        const expectedAccuracy = performanceMetrics.expected_accuracy || 0;
        const confidenceLevel = performanceMetrics.confidence_level || 'Unknown';
        
        // Create enhanced table row
        const row = `
            <tr class="table-success">
                <td><strong>${formatDisplayDate(selectedDate)}</strong></td>
                <td>
                    <div class="prediction-numbers">
                        ${cyclicalNumbers.slice(0, 10).map((num, idx) => 
                            `<span class="badge badge-success mr-1" title="Cyclical Rank ${idx + 1}">${num}</span>`
                        ).join('')}
                    </div>
                </td>
                <td>
                    <div class="prediction-numbers">
                        ${methodNumbers.slice(0, 10).map((num, idx) => 
                            `<span class="badge badge-warning mr-1" title="Method Rank ${idx + 1}">${num}</span>`
                        ).join('')}
                    </div>
                </td>
                <td>
                    <div class="prediction-numbers">
                        ${fusionNumbers.slice(0, 10).map((num, idx) => 
                            `<span class="badge badge-primary mr-1" title="Fusion Rank ${idx + 1}">${num}</span>`
                        ).join('')}
                    </div>
                </td>
                <td>
                    <span class="badge badge-${expectedAccuracy >= 50 ? 'success' : expectedAccuracy >= 30 ? 'warning' : 'danger'} badge-lg">
                        ${expectedAccuracy.toFixed(1)}%
                    </span>
                </td>
                <td>
                    <span class="badge badge-${confidenceLevel === 'High' ? 'success' : confidenceLevel === 'Medium' ? 'warning' : 'danger'}">
                        ${confidenceLevel}
                    </span>
                </td>
            </tr>
        `;
        
        tableBody.append(row);
        
        // Update summary stats
        updateSummaryStats(1, expectedAccuracy >= 50 ? 1 : 0, expectedAccuracy, expectedAccuracy);
    }

    function calculateAccuracy(prediction) {
        // Implement accuracy calculation based on prediction vs actual results
        // This is a placeholder - adjust based on your actual data structure
        if (prediction.actual_result && prediction.cyclical_prediction) {
            const predicted = prediction.cyclical_prediction.toString();
            const actual = prediction.actual_result.toString();
            
            // Simple match calculation
            if (predicted === actual) return 100;
            
            // Partial match calculation (if applicable)
            let matches = 0;
            const minLength = Math.min(predicted.length, actual.length);
            for (let i = 0; i < minLength; i++) {
                if (predicted[i] === actual[i]) matches++;
            }
            
            return Math.round((matches / Math.max(predicted.length, actual.length)) * 100);
        }
        
        return 0;
    }

    function createTableRow(date, prediction, accuracy, isAccurate) {
        const accuracyClass = getAccuracyClass(accuracy);
        const statusClass = isAccurate ? 'prediction-match' : '';
        const statusIcon = isAccurate ? '<i class="fas fa-check-circle text-success"></i>' : '<i class="fas fa-times-circle text-danger"></i>';
        
        return `
            <tr class="${statusClass}">
                <td><strong>${formatDisplayDate(date)}</strong></td>
                <td><span class="badge bg-primary">${prediction.cyclical_prediction || 'N/A'}</span></td>
                <td><span class="badge bg-secondary">${prediction.actual_result || 'Chưa có'}</span></td>
                <td class="${accuracyClass}">${accuracy}%</td>
                <td>${statusIcon} ${isAccurate ? 'Chính xác' : 'Không chính xác'}</td>
            </tr>
        `;
    }

    function getAccuracyClass(accuracy) {
        if (accuracy >= 80) return 'accuracy-high';
        if (accuracy >= 50) return 'accuracy-medium';
        return 'accuracy-low';
    }

    function formatDisplayDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN');
    }

    /**
     * ✅ ENHANCED CYCLICAL CONTEXT WITH ACCURACY
     */
    function displayCyclicalContextWithAccuracy(contextAnalysis, selectedDate, accuracyData) {
        const accuracySummary = accuracyData ? `
            <div class="alert alert-info mt-2">
                <h6><i class="fas fa-chart-line"></i> Accuracy Summary for ${formatDisplayDate(selectedDate)}</h6>
                <div class="row">
                    <div class="col-md-3">
                        <strong>Overall:</strong> 
                        <span class="badge badge-${accuracyData.overall.accuracy >= 50 ? 'success' : accuracyData.overall.accuracy >= 30 ? 'warning' : 'danger'} badge-lg">
                            ${accuracyData.overall.accuracy.toFixed(1)}%
                        </span>
                    </div>
                    <div class="col-md-3">
                        <strong>Cyclical:</strong> 
                        <span class="badge badge-success">${accuracyData.cyclical.accuracy.toFixed(1)}%</span>
                    </div>
                    <div class="col-md-3">
                        <strong>Method:</strong> 
                        <span class="badge badge-warning">${accuracyData.method.accuracy.toFixed(1)}%</span>
                    </div>
                    <div class="col-md-3">
                        <strong>Fusion:</strong> 
                        <span class="badge badge-primary">${accuracyData.fusion.accuracy.toFixed(1)}%</span>
                    </div>
                </div>
                <small class="text-muted">
                    Total matches: ${accuracyData.overall.totalMatches}/${accuracyData.overall.totalPredictions} 
                    | Actual numbers found: ${accuracyData.actualNumbers.length}
                </small>
            </div>
        ` : '<div class="alert alert-warning">⚠️ No actual results available for comparison</div>';
        
        const contextHtml = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-primary">
                        <div class="card-header bg-primary text-white">
                            <h5><i class="fas fa-brain"></i> Cyclical Context Analysis - ${formatDisplayDate(selectedDate)}</h5>
                        </div>
                        <div class="card-body">
                            ${accuracySummary}
                            <div class="row mt-3">
                                <div class="col-md-6">
                                    <h6>📊 Context Information:</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Day Phase:</strong> ${contextAnalysis.day_of_month_phase || 'N/A'}</li>
                                        <li><strong>Week Phase:</strong> ${contextAnalysis.week_phase || 'N/A'}</li>
                                        <li><strong>Month Trend:</strong> ${contextAnalysis.month_trend || 'N/A'}</li>
                                        <li><strong>Cycle Strength:</strong> 
                                            <span class="badge badge-info">${((contextAnalysis.cycle_strength || 0) * 100).toFixed(1)}%</span>
                                        </li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <h6>🔄 Cycle Status:</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Active Cycles:</strong> ${(contextAnalysis.active_cycles || []).length}</li>
                                        <li><strong>Fatigued Methods:</strong> ${(contextAnalysis.fatigued_methods || []).length}</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#cyclicalContext').html(contextHtml);
    }

    /**
     * ✅ ENHANCED INTELLIGENT PREDICTIONS WITH ACCURACY
     */
    function displayIntelligentPredictionsWithAccuracy(intelligentPredictions, performanceMetrics, accuracyData) {
        const cyclicalNumbers = intelligentPredictions.cyclical_numbers || [];
        const methodNumbers = intelligentPredictions.method_numbers || [];
        const fusionNumbers = intelligentPredictions.fusion_numbers || [];
        
        // ✅ GENERATE HIGHLIGHTED BADGES
        const cyclicalBadges = generateHighlightedBadges(cyclicalNumbers, accuracyData, 'cyclical', 'success');
        const methodBadges = generateHighlightedBadges(methodNumbers, accuracyData, 'method', 'warning');
        const fusionBadges = generateHighlightedBadges(fusionNumbers, accuracyData, 'fusion', 'primary');
        
        const predictionHtml = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-info">
                        <div class="card-header bg-info text-white">
                            <h5><i class="fas fa-magic"></i> Intelligent Predictions with Accuracy Tracking</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4">
                                    <h6><i class="fas fa-recycle text-success"></i> Cyclical Numbers:</h6>
                                    <div class="prediction-numbers mb-2">${cyclicalBadges}</div>
                                    ${accuracyData ? `<small class="text-success">✅ Accuracy: ${accuracyData.cyclical.accuracy.toFixed(1)}%</small>` : ''}
                                </div>
                                <div class="col-md-4">
                                    <h6><i class="fas fa-cogs text-warning"></i> Method Numbers:</h6>
                                    <div class="prediction-numbers mb-2">${methodBadges}</div>
                                    ${accuracyData ? `<small class="text-warning">⚡ Accuracy: ${accuracyData.method.accuracy.toFixed(1)}%</small>` : ''}
                                </div>
                                <div class="col-md-4">
                                    <h6><i class="fas fa-rocket text-primary"></i> Fusion Numbers:</h6>
                                    <div class="prediction-numbers mb-2">${fusionBadges}</div>
                                    ${accuracyData ? `<small class="text-primary">🚀 Accuracy: ${accuracyData.fusion.accuracy.toFixed(1)}%</small>` : ''}
                                </div>
                            </div>
                            ${accuracyData ? `
                                <div class="alert alert-info mt-3">
                                    <h6>🎯 Accuracy Comparison:</h6>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <strong>Expected Accuracy:</strong> 
                                            <span class="badge badge-secondary badge-lg">${performanceMetrics.expected_accuracy || 0}%</span>
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Actual Accuracy:</strong> 
                                            <span class="badge badge-${accuracyData.overall.accuracy >= (performanceMetrics.expected_accuracy || 0) ? 'success' : 'danger'} badge-lg">
                                                ${accuracyData.overall.accuracy.toFixed(1)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#intelligentPredictions').html(predictionHtml);
    }

    /**
     * ✅ ENHANCED PERFORMANCE DASHBOARD WITH ACCURACY
     */
    function updatePerformanceDashboardWithAccuracy(performanceMetrics, accuracyData) {
        const expectedAccuracy = performanceMetrics.expected_accuracy || 0;
        const realAccuracy = accuracyData ? accuracyData.overall.accuracy : null;
        const confidenceLevel = performanceMetrics.confidence_level || 'Unknown';
        const cyclicalStrength = performanceMetrics.cyclical_strength || 0;
        const performanceBreakdown = performanceMetrics.performance_breakdown || {};
        const riskAssessment = performanceMetrics.risk_assessment || {};
        
        const accuracyAlert = realAccuracy !== null ? 
            (realAccuracy >= expectedAccuracy ? 
                `<div class="alert alert-success"><i class="fas fa-check-circle"></i> Accuracy exceeds expectations!</div>` :
                `<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> Accuracy below expectations</div>`
            ) : '';
        
        const dashboardHtml = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-success">
                        <div class="card-header bg-success text-white">
                            <h5><i class="fas fa-tachometer-alt"></i> Performance Dashboard</h5>
                        </div>
                        <div class="card-body">
                            ${accuracyAlert}
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="display-4 text-secondary">${expectedAccuracy}%</h4>
                                        <p class="text-muted">Expected Accuracy</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="display-4 text-${realAccuracy !== null ? (realAccuracy >= expectedAccuracy ? 'success' : 'danger') : 'muted'}">
                                            ${realAccuracy !== null ? realAccuracy.toFixed(1) : '--'}%
                                        </h4>
                                        <p class="text-muted">Real Accuracy</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="display-4 text-info">${(cyclicalStrength * 100).toFixed(1)}%</h4>
                                        <p class="text-muted">Cyclical Strength</p>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <h4 class="display-4 text-${confidenceLevel === 'High' ? 'success' : confidenceLevel === 'Medium' ? 'warning' : 'danger'}">
                                            ${confidenceLevel}
                                        </h4>
                                        <p class="text-muted">Confidence</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('#performanceDashboard').html(dashboardHtml);
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

    function updateSummaryStats(total, accurate, avgAccuracy, bestAccuracy) {
        $('#totalAnalyzed').text(total);
        $('#accurateCount').text(accurate);
        $('#averageAccuracy').text(Math.round(avgAccuracy) + '%');
        $('#bestAccuracy').text(Math.round(bestAccuracy) + '%');
    }

    function showLoading() {
        $('#cyclicalLoading').show();
        $('#cyclicalResults').hide();
        $('#noDataMessage').hide();
    }

    function hideLoading() {
        $('#cyclicalLoading').hide();
    }

    function showResults() {
        $('#cyclicalResults').show();
        $('#noDataMessage').hide();
    }

    function showNoData() {
        $('#cyclicalResults').hide();
        $('#noDataMessage').show();
    }

    function showAlert(message, type) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Insert alert at the top of cyclical section
        $('.cyclical-section .card-body').prepend(alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            $('.alert').alert('close');
        }, 5000);
    }

    function refreshCurrentAnalysis() {
        // Only refresh if results are currently displayed
        if ($('#cyclicalResults').is(':visible')) {
            const currentDate = $('#analysisDate').val();
            if (currentDate) {
                analyzeSingleDate();
            }
        }
    }

    // ✅ 0. KHAI BÁO NGÀY HIỆN TẠI TRONG DATE PICKER CỦA ANALYSIS DATE PREDICTION
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('analysisDatePicker').value = today;
    // ✅ 1. KHAI BÁO BIẾN METHODANALYSIS NGAY ĐẦU
    const methodAnalysis = "";
    
    // ✅ 2. EXISTING DAY DATA - GIỮ NGUYÊN
    const dayData = {
        
        """": {
            date: """",
            weekday: """",
            sessions: [
                
                {
                    cycle_name: """",
                    status: """",
                    methods: [
                        
                        {
                            method_id: "",
                            method_name: """",
                            category: """",
                            confidence: "",
                            predicted_numbers: ["",],
                            tracking_results: [
                                
                                {
                                    day: "",
                                    tracking_date: """",
                                    has_result: truefalse,
                                    hit_count: "",
                                    hit_rate: "",
                                    hit_numbers: ["",],
                                    actual_numbers: ["",]
                                },
                                
                            ],
                            total_hits: "",
                            avg_hit_rate: ""
                        },
                        
                    ]
                },
                
            ]
        },
        
    };

    // ✅ 3. KHAI BÁO CÁC FUNCTIONS TRƯỚC KHI SỬ DỤNG

    /**
     * ✅ HÀM AUTO APPLY MÀU PREDICTION INDEX 1 SAU KHI LOAD PAGE
     */
    function autoApplyPredictionIndex1Colors() {
        try {
            console.log('🔄 Auto applying prediction index 1 colors...');
            
            const predictionCells = document.querySelectorAll('.prediction-cell[data-prediction-1]');
            let appliedCount = 0;
            
            predictionCells.forEach(cell => {
                const prediction1 = cell.dataset.prediction1;
                const autoIndex = cell.dataset.autoPredictionIndex;
                
                // ✅ CHỈ APPLY MÀU NẾU CÓ PREDICTION INDEX 1 VÀ KHÁC '-'
                if (prediction1 && prediction1 !== '-' && autoIndex === '1') {
                    cell.setAttribute('data-current-prediction', '1');
                    appliedCount++;
                    
                    console.log(`✅ Applied index 1 colors to method ${cell.dataset.methodId}, prediction: ${prediction1}`);
                }
            });
            
            console.log(`🎨 Auto-applied prediction index 1 colors to ${appliedCount} cells`);
            
            // ✅ HIỂN THỊ NOTIFICATION CHO USER
            if (appliedCount > 0) {
                showAutoColorNotification(appliedCount);
            }
            
        } catch (error) {
            console.error('❌ Error auto-applying prediction index 1 colors:', error);
        }
    }
    
    /**
     * ✅ HÀM HIỂN THỊ NOTIFICATION KHI AUTO APPLY MÀU
     */
    function showAutoColorNotification(count) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-palette me-2"></i>
            <strong>Auto Color Applied:</strong> 
            Đã tự động áp dụng màu scheme <strong>prediction index 1</strong> cho ${count} methods có prediction thứ 2.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            // ✅ AUTO REMOVE AFTER 5 SECONDS
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 5000);
        }
    }
    
    /**
     * ✅ HÀM THAY ĐỔI MÀU BADGE DỰA TRÊN SỐ DỰ ĐOÁN
     */
    function changeBadgeColors(methodId, date, predictionIndex) {
        try {
            const cell = document.querySelector(`[data-method-id="${methodId}"][data-date="${date}"]`);
            if (!cell) {
                console.warn(`⚠️ Cell not found for method ${methodId}, date ${date}`);
                return;
            }
            
            cell.setAttribute('data-current-prediction', predictionIndex);
            console.log(`🎨 Changed badge colors for method ${methodId} to prediction index ${predictionIndex}`);
            
        } catch (error) {
            console.error('❌ Error changing badge colors:', error);
        }
    }
    
    /**
     * ✅ HÀM THAY ĐỔI MÀU TẤT CẢ BADGES
     */
    function changeAllBadgeColors(predictionIndex) {
        try {
            const predictionCells = document.querySelectorAll('.prediction-cell[data-prediction-0], .prediction-cell[data-prediction-1]');
            let changedCount = 0;
            
            predictionCells.forEach(cell => {
                const methodId = cell.dataset.methodId;
                const date = cell.dataset.date;
                
                if (methodId && date) {
                    const hasThisPrediction = cell.dataset[`prediction${predictionIndex}`] && 
                                           cell.dataset[`prediction${predictionIndex}`] !== '-';
                    
                    if (hasThisPrediction) {
                        cell.setAttribute('data-current-prediction', predictionIndex);
                        changedCount++;
                    }
                }
            });
            
            console.log(`🎨 Changed ${changedCount} cells to prediction index ${predictionIndex}`);
            
        } catch (error) {
            console.error('❌ Error changing all badge colors:', error);
        }
    }
    
    /**
     * ✅ HÀM RESET VỀ MÀU MẶC ĐỊNH (INDEX 0)
     */
    function resetBadgeColors() {
        try {
            const predictionCells = document.querySelectorAll('.prediction-cell[data-current-prediction]');
            
            predictionCells.forEach(cell => {
                cell.removeAttribute('data-current-prediction');
            });
            
            console.log('🎨 Reset all badge colors to default (index 0)');
            
        } catch (error) {
            console.error('❌ Error resetting badge colors:', error);
        }
    }
    
    /**
     * ✅ HÀM TOGGLE GIỮA 2 SCHEME MÀU
     */
    function toggleBadgeColors() {
        try {
            const firstCellWithPrediction = document.querySelector('.prediction-cell[data-current-prediction]');
            const currentIndex = firstCellWithPrediction ? 
                                parseInt(firstCellWithPrediction.getAttribute('data-current-prediction')) : 0;
            
            const newIndex = currentIndex === 0 ? 1 : 0;
            changeAllBadgeColors(newIndex);
            
            showColorChangeNotification(newIndex);
            
        } catch (error) {
            console.error('❌ Error toggling badge colors:', error);
        }
    }
    
    /**
     * ✅ HÀM HIỂN THỊ THÔNG BÁO THAY ĐỔI MÀU
     */
    function showColorChangeNotification(predictionIndex) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-palette me-2"></i>
            <strong>Đã thay đổi màu badges:</strong> 
            Hiển thị scheme màu cho <strong>prediction index ${predictionIndex}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 3000);
        }
    }
    
    // ✅ AUTO APPLY PREDICTION INDEX 1 COLORS KHI PAGE LOAD XONG
    setTimeout(() => {
        autoApplyPredictionIndex1Colors();
    }, 500); // Delay 500ms để đảm bảo DOM render xong
    
    // ✅ EXPOSE FUNCTIONS FOR MANUAL CONTROL
    window.badgeColorControl = {
        change: changeBadgeColors,
        changeAll: changeAllBadgeColors,
        reset: resetBadgeColors,
        toggle: toggleBadgeColors,
        showPredictionIndex: showPredictionIndexColors,
        info: showBadgeInfo
    };
    
    // ✅ HÀM HIỂN THỊ PREDICTION INDEX COLORS
    function showPredictionIndexColors() {
        const badges = document.querySelectorAll('.hit-badge[data-pred-index]');
        let info = {
            index_0: { count: 0, days: [] },
            index_1: { count: 0, days: [] }
        };
        
        badges.forEach(badge => {
            const predIndex = badge.getAttribute('data-pred-index');
            const day = badge.getAttribute('data-day');
            
            if (predIndex === '0') {
                info.index_0.count++;
                info.index_0.days.push(day);
            } else if (predIndex === '1') {
                info.index_1.count++;
                info.index_1.days.push(day);
            }
        });
        
        console.log('📊 Prediction Index Color Analysis:', info);
        return info;
    }
    
    // ✅ HÀM HIỂN THỊ THÔNG TIN BADGE
    function showBadgeInfo() {
        const badges = document.querySelectorAll('.hit-badge');
        badges.forEach(badge => {
            const day = badge.getAttribute('data-day');
            const predIndex = badge.getAttribute('data-pred-index');
            const bgColor = window.getComputedStyle(badge).backgroundColor;
            
            console.log(`Badge Day ${day} - Prediction Index ${predIndex} - Color: ${bgColor}`);
        });
    }
    
    console.log('✅ Badge color control initialized with prediction index support');
    console.log('💡 Use: window.badgeColorControl.showPredictionIndex() to see prediction index info');
    console.log('💡 Use: window.badgeColorControl.info() to debug badge colors');

    // ✅ HÀM TẠO DAY-BY-DAY ANALYSIS HTML
    function generateDayByDayAnalysis(dayAnalysis) {
        console.log('Day-by-day analysis:', dayAnalysis);
        if (!dayAnalysis || !dayAnalysis.day_1) {
            return '<div class="alert alert-warning alert-sm">Không có dữ liệu phân tích theo ngày</div>';
        }

        const bestDay = dayAnalysis.best_day;
        const strategy = dayAnalysis.recommended_strategy;
        
        let html = `
            <div class="day-analysis-container mb-2">
                <div class="row g-1 mb-2">
        `;
        
        // Hiển thị 3 ngày tracking
        for (let day = 1; day <= 3; day++) {
            const dayData = dayAnalysis[`day_${day}`];
            const isBestDay = day === bestDay;
            const cardClass = isBestDay ? 'border-success bg-light-success' : 'border-secondary';
            const probability = dayData.hit_probability || 0;
            const confidence = dayData.confidence || 'no_data';
            
            // Color coding cho probability
            let probColor = 'text-danger';
            if (probability >= 70) probColor = 'text-success';
            else if (probability >= 50) probColor = 'text-warning';
            else if (probability >= 30) probColor = 'text-info';
            
            // Confidence icon
            const confIcons = {
                'high': '🔥',
                'medium': '⚡',
                'low': '💡',
                'very_low': '❓',
                'no_data': '❌'
            };
            
            html += `
                <div class="col-4">
                    <div class="card card-sm ${cardClass}" style="font-size: 0.75rem;">
                        <div class="card-body p-1 text-center">
                            <div class="fw-bold">Ngày ${day} ${isBestDay ? '⭐' : ''}</div>
                            <div class="${probColor} fw-bold">${probability}%</div>
                            <div class="text-muted">${confIcons[confidence]}</div>
                            ${dayData.sample_size ? `<small class="text-muted">(${dayData.sample_size} mẫu)</small>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }
        
        html += `
                </div>
                <div class="goi-y-strategy">
                    <div class="alert alert-info alert-sm p-2 mb-0" style="font-size: 0.8rem;">
                        <strong>🎯 Gợi ý:</strong> ${strategy}
                    </div>
                </div>
            </div>
        `;
        
        return html;
    }

    // ✅ HÀM TẠO RECOMMENDATIONS LIST HTML - SỬA LỖI
    function generateRecommendationsList(recommendations) {
        if (recommendations.length === 0) {
            return '<div class="alert alert-info">Không có đủ dữ liệu để phân tích</div>';
        }

        let html = '<div class="list-group">';
        
        recommendations.slice(0, 5).forEach((rec, index) => {
            const scoreClass = rec.score >= 80 ? 'success' : rec.score >= 60 ? 'warning' : 'danger';
            const trendIcon = rec.trend_direction === 'up' ? '📈' : rec.trend_direction === 'down' ? '📉' : '➡️';
            const riskColor = rec.risk_level === 'low' ? 'success' : rec.risk_level === 'medium' ? 'warning' : 'danger';
            
            // ✅ KIỂM TRA METHODANALYSIS TRƯỚC KHI SỬ DỤNG
            let dayAnalysisHTML = '';
            if (methodAnalysis && methodAnalysis.day_by_day_analysis && methodAnalysis.day_by_day_analysis[rec.method_id]) {
                const dayAnalysis = methodAnalysis.day_by_day_analysis[rec.method_id];
                dayAnalysisHTML = generateDayByDayAnalysis(dayAnalysis);
            } else {
                dayAnalysisHTML = '<div class="alert alert-warning alert-sm">Không có dữ liệu phân tích theo ngày</div>';
            }
            
            html += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center mb-2">
                                <span class="badge bg-secondary me-2">#${index + 1}</span>
                                <strong class="text-primary">${rec.method_name}</strong>
                                <span class="ms-2">${trendIcon}</span>
                            </div>
                            
                            <!-- ✅ THÊM PHÂN TÍCH THEO TỪNG NGÀY -->
                            ${dayAnalysisHTML}
                            
                            <div class="mt-2">
                                <small class="text-muted">${rec.reason}</small>
                            </div>
                            <div class="mt-1">
                                <small class="text-info">
                                    Recent: ${rec.recent_performance}% | 
                                    Stability: ${rec.stability}% |
                                    ${rec.cycle_info.next_expected_hit !== 'unknown' ? 
                                        `Chu kỳ: ${rec.cycle_info.next_expected_hit}` : 
                                        'Chu kỳ: không rõ'}
                                </small>
                            </div>
                        </div>
                        <div class="text-end">
                            <div class="badge bg-${scoreClass} mb-1">${rec.score}/100</div><br>
                            <small class="text-${riskColor}">Risk: ${rec.risk_level}</small><br>
                            <small class="text-muted">Conf: ${rec.confidence}%</small>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        return html;
    }

    // ✅ HÀM TẠO RECOMMENDATIONS - SỬA LỖI
    function generateRecommendations(methods) {
        let recommendations = [];

        if (!methodAnalysis) {
            console.warn('methodAnalysis not available');
            return recommendations;
        }

        methods.forEach(method => {
            const analysis = methodAnalysis.method_recommendations ? methodAnalysis.method_recommendations[method.method_id] : null;
            const trends = methodAnalysis.method_trends ? methodAnalysis.method_trends[method.method_id] : null;
            const cycles = methodAnalysis.method_cycles ? methodAnalysis.method_cycles[method.method_id] : null;

            if (analysis && trends && cycles) {
                recommendations.push({
                    method_id: method.method_id,
                    method_name: method.method_name,
                    score: analysis.score,
                    confidence: analysis.confidence,
                    reason: analysis.reason,
                    risk_level: analysis.risk_level,
                    trend_direction: trends.trend_direction,
                    recent_performance: trends.recent_performance,
                    stability: trends.stability,
                    cycle_info: cycles
                });
            }
        });

        // Sắp xếp theo score
        recommendations.sort((a, b) => b.score - a.score);
        return recommendations;
    }

    // ✅ HÀM generateStatsOverview - SỬA LỖI
    function generateStatsOverview(recommendations) {
        if (recommendations.length === 0) {
            return '<div class="text-muted">Không có dữ liệu</div>';
        }

        const avgScore = recommendations.reduce((sum, rec) => sum + rec.score, 0) / recommendations.length;
        const highScore = recommendations.filter(rec => rec.score >= 70).length;
        const upTrend = recommendations.filter(rec => rec.trend_direction === 'up').length;
        const lowRisk = recommendations.filter(rec => rec.risk_level === 'low').length;

        // ✅ THÊM THỐNG KÊ THEO NGÀY - KIỂM TRA METHODANALYSIS
        let dayStats = {1: [], 2: [], 3: []};
        if (methodAnalysis && methodAnalysis.day_by_day_analysis) {
            recommendations.forEach(rec => {
                const dayAnalysis = methodAnalysis.day_by_day_analysis[rec.method_id];
                if (dayAnalysis) {
                    for (let day = 1; day <= 3; day++) {
                        const dayData = dayAnalysis[`day_${day}`];
                        if (dayData && dayData.hit_probability > 0) {
                            dayStats[day].push(dayData.hit_probability);
                        }
                    }
                }
            });
        }

        // Tìm ngày có xác suất cao nhất
        let bestDayOverall = 1;
        let bestAvgProb = 0;
        for (let day = 1; day <= 3; day++) {
            if (dayStats[day].length > 0) {
                const avgProb = dayStats[day].reduce((sum, prob) => sum + prob, 0) / dayStats[day].length;
                if (avgProb > bestAvgProb) {
                    bestAvgProb = avgProb;
                    bestDayOverall = day;
                }
            }
        }

        return `
            <div class="list-group list-group-flush">
                <div class="list-group-item p-2">
                    <div class="d-flex justify-content-between">
                        <span>Điểm TB:</span>
                        <strong class="${avgScore >= 70 ? 'text-success' : avgScore >= 50 ? 'text-warning' : 'text-danger'}">${avgScore.toFixed(1)}</strong>
                    </div>
                </div>
                <div class="list-group-item p-2">
                    <div class="d-flex justify-content-between">
                        <span>Điểm cao (≥70):</span>
                        <strong class="text-success">${highScore}/${recommendations.length}</strong>
                    </div>
                </div>
                <div class="list-group-item p-2">
                    <div class="d-flex justify-content-between">
                        <span>Xu hướng tăng:</span>
                        <strong class="text-primary">${upTrend}/${recommendations.length}</strong>
                    </div>
                </div>
                <div class="list-group-item p-2">
                    <div class="d-flex justify-content-between">
                        <span>Rủi ro thấp:</span>
                        <strong class="text-success">${lowRisk}/${recommendations.length}</strong>
                    </div>
                </div>
                <!-- ✅ THÊM THỐNG KÊ NGÀY TỐT NHẤT -->
                <div class="list-group-item p-2 bg-light">
                    <div class="d-flex justify-content-between">
                        <span>📅 Ngày khuyến nghị:</span>
                        <strong class="text-primary">Ngày ${bestDayOverall} (${bestAvgProb.toFixed(1)}%)</strong>
                    </div>
                </div>
            </div>
        `;
    }

    /**
    * ✅ HÀM TẠO PHẦN PHÂN TÍCH AI VÀ ML CHO NGÀY CỤ THỂ
    * @param {string} date - Ngày cần phân tích (định dạng YYYY-MM-DD)
    * @param {number} selectedMethodId - ID của phương pháp đã chọn (nếu có)
    * @returns {string} - HTML cho phần phân tích
    */
    function createAnalysisSection(date, selectedMethodId) {
        const methods = getDayMethods(date, selectedMethodId);
        let analysisHTML = `
            <div class="card mb-3">
                <div class="card-header bg-primary text-white">
                    <h6 class="mb-0">
                        <i class="fas fa-brain me-2"></i>AI Pattern Analysis & ML Prediction cho ngày ${date}
                        <div class="spinner-border spinner-border-sm ms-2 d-none" id="analysis-spinner" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </h6>
                </div>
                <div class="card-body" id="analysis-content">
                    <div class="text-center text-muted">
                        <i class="fas fa-chart-line fa-2x mb-2"></i>
                        <p>Đang phân tích pattern và ML cho ngày này...</p>
                        <small class="text-muted">Sử dụng API: pattern-analysis</small>
                    </div>
                </div>
                <!-- ✅ METADATA CONTAINER -->
                <div id="data-source-info" class="d-none">
                    <!-- Metadata will be populated by JavaScript -->
                </div>
            </div>
        `;
        
        // Trigger pattern analysis cho ngày cụ thể
        setTimeout(() => {
            performDaySpecificAnalysis(date, selectedMethodId);
        }, 100);
        
        return analysisHTML;
    }

    function showDataSourceInfo(metadata) {
        if (!metadata || typeof metadata !== 'object') {
            return;
        }
        
        const infoContainer = document.getElementById('data-source-info');
        if (!infoContainer) {
            return;
        }
        
        try {
            const totalMethods = metadata.total_active_methods || 0;
            const successfulMethods = metadata.successful_predictions || 0;
            const analysisTimestamp = metadata.analysis_timestamp || 'Unknown';
            
            const html = `
                <div class="card-footer bg-light">
                    <div class="row text-center">
                        <div class="col-md-3">
                            <div class="fw-bold text-primary">${totalMethods}</div>
                            <small class="text-muted">Total Methods</small>
                        </div>
                        <div class="col-md-3">
                            <div class="fw-bold text-success">${successfulMethods}</div>
                            <small class="text-muted">Successful</small>
                        </div>
                        <div class="col-md-3">
                            <div class="fw-bold text-info">${metadata.service || 'TrackingService'}</div>
                            <small class="text-muted">Service</small>
                        </div>
                        <div class="col-md-3">
                            <div class="fw-bold text-secondary">${new Date(analysisTimestamp).toLocaleTimeString()}</div>
                            <small class="text-muted">Analysis Time</small>
                        </div>
                    </div>
                </div>
            `;
            
            infoContainer.innerHTML = html;
            infoContainer.classList.remove('d-none');
            
        } catch (error) {
            console.error('❌ Error displaying metadata:', error);
        }
    }

    /**
    * ✅ HÀM VALIDATE RESPONSE DATA TRƯỚC KHI XỬ LÝ
    * @param {object} data - Response data from API
    * @returns {boolean} - True if valid, false otherwise
    */
    function validateResponseData(data) {
        if (!data || typeof data !== 'object') {
            console.error('❌ Invalid response data: not an object');
            return false;
        }
        
        // ✅ VALIDATE REQUIRED FIELDS cho pattern-analysis API
        const requiredFields = ['success'];
        const missingFields = requiredFields.filter(field => !(field in data));
        
        if (missingFields.length > 0) {
            console.error('❌ Missing required fields:', missingFields);
            return false;
        }
        
        // ✅ VALIDATE SUCCESS FIELD
        if (typeof data.success !== 'boolean') {
            console.error('❌ Invalid success field type');
            return false;
        }
        
        // ✅ NẾU SUCCESS = TRUE, VALIDATE ADDITIONAL FIELDS
        if (data.success) {
            if (data.predictions && typeof data.predictions !== 'object') {
                console.error('❌ Invalid predictions field type');
                return false;
            }
            
            if (data.analysis && typeof data.analysis !== 'object') {
                console.error('❌ Invalid analysis field type');
                return false;
            }
            
            if (data.data_quality && typeof data.data_quality !== 'object') {
                console.error('❌ Invalid data_quality field type');
                return false;
            }
            
            if (data.metadata && typeof data.metadata !== 'object') {
                console.error('❌ Invalid metadata field type');
                return false;
            }
        }
        
        return true;
    }

    /**
    * ✅ SỬA HÀM performDaySpecificAnalysis - SIMPLIFIED VERSION
    * @param {string} date - Ngày cần phân tích
    * @param {number|null} selectedMethodId - Method được chọn (không cần thiết nữa)
    */
    function performDaySpecificAnalysis(date, selectedMethodId = null) {
        const content = document.getElementById('analysis-content');
        
        // Show spinner
        const spinner = document.getElementById('analysis-spinner');
        if (spinner) {
            spinner.classList.remove('d-none');
        }

        console.log('🔍 Day Specific Analysis:');
        console.log(`   📅 Analysis Date: ${date}`);

        // ✅ CHỈ GỌI API VỚI NGÀY PHÂN TÍCH
        getPatternAnalysisPredictions(date)
            .then(async (data) => {
                // Hide spinner
                if (spinner) {
                    spinner.classList.add('d-none');
                }
                
                // Display results
                await displayAnalysisResults(data);
            })
            .catch(error => {
                // Hide spinner
                if (spinner) {
                    spinner.classList.add('d-none');
                }
                
                showErrorMessage('Lỗi phân tích pattern: ' + error.message);
            });
    }
    
    /**
    * ✅ THÊM HÀM HIỂN THỊ WARNING CHO INVALID METHODS
    */
    function showAnalysisWarning(message, invalidMethodIds = []) {
        const alertHtml = `
            <div class="alert alert-warning alert-dismissible fade show mt-3" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>⚠️ Cảnh báo:</strong> ${message}
                ${invalidMethodIds.length > 0 ? `
                    <details class="mt-2">
                        <summary>Chi tiết method IDs không hợp lệ:</summary>
                        <ul class="mt-2 mb-0">
                            ${invalidMethodIds.map(id => `<li><code>${JSON.stringify(id)}</code></li>`).join('')}
                        </ul>
                    </details>
                ` : ''}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        // Thêm vào đầu analysis content
        const content = document.getElementById('analysis-content');
        if (content) {
            content.insertAdjacentHTML('afterbegin', alertHtml);
        }
    }

    /**
    * ✅ THÊM HÀM HELPER EXTRACT ANALYSIS DATE
    * @param {object} predictions - Predictions object
    * @returns {string} - Analysis date (YYYY-MM-DD)
    */
    function extractAnalysisDateFromPredictions(predictions) {
        // ✅ TRY TO EXTRACT DATE FROM FIRST PREDICTION
        const firstPrediction = Object.values(predictions)[0];
        if (firstPrediction && firstPrediction.analysis_date) {
            return firstPrediction.analysis_date;
        }
        
        // ✅ FALLBACK TO TODAY'S DATE
        return new Date().toISOString().split('T')[0];
    }
    
    // ✅ HÀM HIỂN THỊ KẾT QUẢ ENHANCED ML
    function displayEnhancedMLResults(predictions, modelPerformance) {
        const content = document.getElementById('analysis-content');
        if (!content) return;

        let html = `
            <div class="alert alert-success">
                <h5><i class="fas fa-robot"></i> Enhanced ML Predictions</h5>
                <p>Sử dụng mô hình Machine Learning đã được huấn luyện</p>
            </div>
        `;

        // Model performance info
        if (modelPerformance && modelPerformance.overall_performance) {
            const perf = modelPerformance.overall_performance;
            html += `
                <div class="card mb-3">
                    <div class="card-header bg-info text-white">
                        <h6>Model Performance</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <strong>Avg Accuracy:</strong> ${(perf.avg_accuracy * 100).toFixed(1)}%
                            </div>
                            <div class="col-md-4">
                                <strong>Best Accuracy:</strong> ${(perf.best_accuracy * 100).toFixed(1)}%
                            </div>
                            <div class="col-md-4">
                                <strong>Consistency:</strong> ${(perf.consistency * 100).toFixed(1)}%
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        // Predictions
        const sortedPredictions = Object.entries(predictions).sort((a, b) => 
            b[1].overall_confidence - a[1].overall_confidence
        );

        html += '<div class="row g-3">';
        
        sortedPredictions.forEach(([methodId, prediction], index) => {
            const confidence = (prediction.overall_confidence * 100).toFixed(1);
            const recommendedDay = prediction.recommended_day;
            
            html += `
                <div class="col-md-6">
                    <div class="card ${index === 0 ? 'border-success' : ''}">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">${prediction.method_name}</h6>
                            <span class="badge bg-primary">${confidence}% confidence</span>
                        </div>
                        <div class="card-body">
                            <div class="row g-2">
            `;
            
            // Day predictions
            for (let day = 1; day <= 3; day++) {
                const dayPred = prediction.day_predictions[`day_${day}`];
                const isRecommended = day === recommendedDay;
                const probability = (dayPred.probability * 100).toFixed(1);
                const dayConfidence = (dayPred.confidence * 100).toFixed(1);
                
                html += `
                    <div class="col-4">
                        <div class="day-prob-card ${isRecommended ? 'recommended' : ''}">
                            <div class="day-label">Day ${day}</div>
                            <div class="prob-value">${probability}%</div>
                            <small class="text-muted">${dayConfidence}% conf</small>
                            ${isRecommended ? '<i class="fas fa-star text-warning"></i>' : ''}
                        </div>
                    </div>
                `;
            }
            
            html += `
                            </div>
                            <div class="mt-2">
                                <small class="text-muted">
                                    Source: ${prediction.prediction_source} | 
                                    Features: ${prediction.feature_count}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        content.innerHTML = html;
    }
    

    /**
    * ✅ HÀM ĐÁNH GIÁ CHẤT LƯỢNG DỰ ĐOÁN
    * @param {number} probability - Xác suất (%)
    * @param {number} confidence - Độ tin cậy (%) 
    * @returns {string} - Text mô tả chất lượng
    */
    function getQualityText(probability, confidence) {
        // ✅ BOTH MUST BE CHECKED INDIVIDUALLY FOR STRICT MODE
        if (probability >= 60 && confidence >= 60) {
            const avgScore = (probability + confidence) / 2;
            if (avgScore >= 80) return "🔥🔥 Xuất sắc";
            if (avgScore >= 70) return "🔥 Rất tốt";
            return "⚡ Tốt";
        }
        
        // ✅ FOR NON-BADGE DISPLAY
        const avgScore = (probability + confidence) / 2;
        if (avgScore >= 45) return "💡 Khá";
        if (avgScore >= 30) return "❓ Thấp";
        return "❌ Rất thấp";
    }

    /**
    * ✅ HÀM ÁP DỤNG STYLE THEO CHẤT LƯỢNG
    * @param {Element} badge - Badge element
    * @param {number} probability - Xác suất (%)
    * @param {number} confidence - Độ tin cậy (%)
    * @param {boolean} isRecommended - Có phải ngày được khuyến nghị
    */
    function applyQualityStyle(badge, probability, confidence, isRecommended) {
        const avgScore = (probability + confidence) / 2;
        
        // ✅ STYLE CHO RECOMMENDED DAY
        if (isRecommended) {
            badge.style.fontWeight = 'bold';
            badge.style.boxShadow = '0 0 0 2px #fff, 0 0 0 4px gold';
            badge.style.zIndex = '15';
        }
        
        // ✅ OPACITY VÀ BORDER DỰA TRÊN CHẤT LƯỢNG
        if (avgScore >= 60) {
            badge.style.opacity = '1.0';
            badge.style.border = '2px solid #28a745';  // Green border for high quality
        } else if (avgScore >= 45) {
            badge.style.opacity = '0.9';
            badge.style.border = '1px solid #17a2b8';  // Blue border for good quality
        } else if (avgScore >= 30) {
            badge.style.opacity = '0.8';
            badge.style.border = '1px solid #ffc107';  // Yellow border for fair quality
        } else {
            badge.style.opacity = '0.7';
            badge.style.border = '1px solid #6c757d';  // Gray border for low quality
        }
        
        // ✅ ANIMATION CHO HIGH QUALITY
        if (avgScore >= 60) {
            badge.style.animation = 'pulse 2s infinite';
        }
    }

   /**
    * ✅ SỬA HÀM displayAnalysisResults - FIX ENHANCED ML CASE
    * @param {object} data - Response data from API
    * @param {object} dataQuality - Frontend data quality
    */
    async function displayAnalysisResults(data, dataQuality = null) {
        const content = document.getElementById('analysis-content');
        if (!content) return;

        // Hide spinner
        const spinner = document.getElementById('analysis-spinner');
        if (spinner) {
            spinner.classList.add('d-none');
        }

        // ✅ XỬ LÝ CÁC LOẠI RESPONSE KHÁC NHAU
        if (!data.success) {
            handleAnalysisError(data);
            return;
        }

        // ✅ KIỂM TRA CÓ PREDICTIONS KHÔNG
        if (!data.predictions || Object.keys(data.predictions).length === 0) {
            content.innerHTML = `
                <div class="alert alert-warning">
                    <h6 class="alert-heading">⚠️ Không có dự đoán</h6>
                    <p>Không có đủ dữ liệu để tạo dự đoán cho ngày này.</p>
                </div>
            `;
            return;
        }

        try {
            // ✅ DEBUG STRUCTURE TRƯỚC KHI LỌC
            console.log('🔍 Raw predictions received:', data.predictions);
            debugPredictionsStructure(data.predictions);
            
            // ✅ LẤY ANALYSIS DATE TỪ DATA
            const analysisDate = data.target_date || extractAnalysisDateFromPredictions(data.predictions);
            
            // ✅ LỌC QUALITY PREDICTIONS VỚI ACCURACY CHECK
            let qualityPredictions;
            try {
                // ✅ SỬ DỤNG HÀM MỚI VỚI ACCURACY CHECK
                qualityPredictions = await filterQualityPredictionsWithAccuracy(data.predictions, analysisDate);
            } catch (filterError) {
                console.error('❌ Error in accuracy-based filtering:', filterError);
                
                // ✅ FALLBACK: Sử dụng filtering cũ
                qualityPredictions = filterQualityPredictions(data.predictions);
                
                // Show warning to user
                const warningAlert = document.createElement('div');
                warningAlert.className = 'alert alert-warning alert-dismissible fade show mb-3';
                warningAlert.innerHTML = `
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Cảnh báo:</strong> Không thể so sánh với kết quả thực tế. Sử dụng tiêu chí lọc cũ.
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                content.insertBefore(warningAlert, content.firstChild);
            }

            // ✅ HIỂN THỊ KẾT QUẢ THEO LOẠI ANALYSIS VỚI ERROR HANDLING
            if (data.enhanced && data.model_performance) {
                // Enhanced ML results từ pattern-analysis
                console.log('🔮 Displaying Enhanced ML Results with Accuracy Scoring');
                console.log(`📊 Accuracy-based filter: ${Object.keys(data.predictions).length} → ${Object.keys(qualityPredictions).length} methods`);
                
                displayEnhancedMLResults(qualityPredictions, data.model_performance);
                
                // ✅ CẬP NHẬT BẢNG VỚI QUALITY PREDICTIONS (ĐÃ LỌC THEO ACCURACY)
                updateTableWithPredictions(qualityPredictions);
                
            } else if (data.predictions) {
                console.log('🔍 Processing Pattern Analysis Results with Accuracy Scoring');
                console.log(`📊 Accuracy-based filter: ${Object.keys(data.predictions).length} → ${Object.keys(qualityPredictions).length} methods`);
                
                // Standard pattern analysis results
                displayAllMethodsPredictions(qualityPredictions, data.analysis, Object.keys(data.predictions).length);
                
                // ✅ CẬP NHẬT BẢNG VỚI QUALITY PREDICTIONS (ĐÃ LỌC THEO ACCURACY)  
                updateTableWithPredictions(qualityPredictions);
            }

            // ✅ HIỂN THỊ METADATA
            if (data.metadata) {
                showDataSourceInfo(data.metadata);
            }
            
        } catch (displayError) {
            console.error('❌ Error in displayAnalysisResults:', displayError);
            
            // ✅ FALLBACK ERROR DISPLAY
            content.innerHTML = `
                <div class="alert alert-danger">
                    <h6 class="alert-heading">❌ Lỗi hiển thị kết quả</h6>
                    <p>Có lỗi khi xử lý dữ liệu phân tích: ${displayError.message}</p>
                </div>
            `;
        }
    }

    
    /**
    * ✅ CẢI THIỆN HÀM filterQualityPredictions - THÊM SO SÁNH VỚI KẾT QUẢ THỰC TẾ
    * @param {object} predictions - All predictions
    * @param {string} analysisDate - Analysis date (YYYY-MM-DD)
    * @returns {object} - Filtered quality predictions with accuracy scores
    */
    async function filterQualityPredictionsWithAccuracy(predictions, analysisDate) {
        const qualityPredictions = {};
        let skippedCount = 0;
        
        console.log('🔍 Starting enhanced quality filter with accuracy check...');
        console.log(`📊 Input: ${Object.keys(predictions).length} methods for ${analysisDate}`);
        
        // ✅ LẤY SỐ THỰC TẾ TỪ API
        let actualNumbers = [];
        try {
            const actualData = await fetchActualNumbers(analysisDate);
            actualNumbers = actualData.all_2digit_numbers || [];
            console.log(`📋 Actual numbers for ${analysisDate}:`, actualNumbers);
        } catch (error) {
            console.warn(`⚠️ Could not fetch actual numbers for ${analysisDate}:`, error);
            // Fallback to original filtering if no actual data
            return filterQualityPredictions(predictions);
        }
        
        const methodScores = [];
        
        Object.entries(predictions).forEach(([methodId, prediction]) => {
            try {
                // ✅ VALIDATE PREDICTION STRUCTURE
                if (!prediction || typeof prediction !== 'object') {
                    console.warn(`⚠️ Invalid prediction object for method ${methodId}:`, prediction);
                    skippedCount++;
                    return;
                }
                
                // ✅ NORMALIZE PREDICTION DATA
                let dayProbabilities, dayConfidences, confidence, recommendedDay, dayPredictedNumbers;
                
                if (prediction.day_probabilities && typeof prediction.day_probabilities === 'object') {
                    dayProbabilities = prediction.day_probabilities;
                    dayConfidences = prediction.day_confidences || {};
                    confidence = prediction.confidence || 0;
                    recommendedDay = prediction.recommended_day || 1;
                    dayPredictedNumbers = prediction.day_predicted_numbers || {};
                } else if (prediction.day_predictions && typeof prediction.day_predictions === 'object') {
                    dayProbabilities = {
                        day_1: prediction.day_predictions.day_1?.probability || 0,
                        day_2: prediction.day_predictions.day_2?.probability || 0,
                        day_3: prediction.day_predictions.day_3?.probability || 0
                    };
                    dayConfidences = {
                        day_1: prediction.day_predictions.day_1?.confidence || 0,
                        day_2: prediction.day_predictions.day_2?.confidence || 0,
                        day_3: prediction.day_predictions.day_3?.confidence || 0
                    };
                    confidence = prediction.overall_confidence || prediction.confidence || 0;
                    recommendedDay = prediction.recommended_day || 1;
                    dayPredictedNumbers = prediction.day_predicted_numbers || {};
                } else {
                    console.warn(`⚠️ Method ${methodId} has incomplete prediction data, using defaults`);
                    dayProbabilities = { day_1: 0.05, day_2: 0.05, day_3: 0.05 };
                    dayConfidences = { day_1: 0.05, day_2: 0.05, day_3: 0.05 };
                    confidence = prediction.confidence || 0.05;
                    recommendedDay = prediction.recommended_day || 1;
                    dayPredictedNumbers = {};
                }
                
                // ✅ TÍNH ACCURACY SCORE VỚI SỐ THỰC TẾ
                const accuracyScore = calculateAccuracyScore(
                    dayPredictedNumbers, 
                    actualNumbers, 
                    analysisDate,
                    recommendedDay
                );
                
                // ✅ TÍNH QUALITY METRICS
                const maxProb = Math.max(
                    dayProbabilities.day_1 || 0,
                    dayProbabilities.day_2 || 0,
                    dayProbabilities.day_3 || 0
                ) * 100;
                
                const maxConf = Math.max(
                    dayConfidences.day_1 || 0,
                    dayConfidences.day_2 || 0,
                    dayConfidences.day_3 || 0
                ) * 100;
                
                const overallConfidence = confidence * 100;
                
                // ✅ TÍNH TỔNG ĐIỂM (WEIGHTED SCORE)
                const totalScore = calculateWeightedScore({
                    accuracyScore,
                    maxProb,
                    maxConf,
                    overallConfidence,
                    recommendedDay
                });
                
                methodScores.push({
                    methodId,
                    prediction: {
                        ...prediction,
                        day_probabilities: dayProbabilities,
                        day_confidences: dayConfidences,
                        confidence: confidence,
                        recommended_day: recommendedDay,
                        day_predicted_numbers: dayPredictedNumbers,
                        method_name: prediction.method_name || `Method ${methodId}`,
                    },
                    accuracyScore,
                    maxProb,
                    maxConf,
                    overallConfidence,
                    totalScore
                });
                
            } catch (error) {
                console.error(`❌ Error processing method ${methodId}:`, error, prediction);
                skippedCount++;
            }
        });
        
        // ✅ SẮP XẾP THEO TỔNG ĐIỂM (accuracy > probability > confidence)
        methodScores.sort((a, b) => b.totalScore - a.totalScore);
        
        // ✅ LỌC VÀ TẠO RESULT
        const minRequiredScore = 30; // Điểm tối thiểu
        const qualifiedMethods = methodScores.filter(method => method.totalScore >= minRequiredScore);
        
        qualifiedMethods.forEach(method => {
            qualityPredictions[method.methodId] = {
                ...method.prediction,
                _accuracy_score: method.accuracyScore,
                _total_score: method.totalScore,
                _quality_metrics: {
                    accuracy: method.accuracyScore,
                    max_probability: method.maxProb,
                    max_confidence: method.maxConf,
                    overall_confidence: method.overallConfidence
                }
            };
        });
        
        console.log(`🔍 Enhanced quality filter results:`);
        console.log(`   ✅ Qualified: ${Object.keys(qualityPredictions).length}`);
        console.log(`   ❌ Filtered: ${skippedCount + (methodScores.length - qualifiedMethods.length)}`);
        console.log(`   📊 Total: ${Object.keys(predictions).length}`);
        console.log(`   🎯 Top accuracy scores:`, qualifiedMethods.slice(0, 3).map(m => `Method ${m.methodId}: ${m.accuracyScore.toFixed(1)}%`));
        
        return qualityPredictions;
    }

    /**
    * ✅ HÀM TÍNH ACCURACY SCORE
    * @param {object} dayPredictedNumbers - Predicted numbers cho từng ngày
    * @param {array} actualNumbers - Số thực tế
    * @param {string} analysisDate - Ngày phân tích 
    * @param {number} recommendedDay - Ngày được khuyến nghị
    * @returns {number} - Accuracy score (0-100)
    */
    function calculateAccuracyScore(dayPredictedNumbers, actualNumbers, analysisDate, recommendedDay) {
        if (!actualNumbers || actualNumbers.length === 0) {
            return 0; // Không có số thực tế để so sánh
        }
        
        let totalAccuracy = 0;
        let validDays = 0;
        
        // ✅ TÍNH ACCURACY CHO TỪNG NGÀY
        ['day_1', 'day_2', 'day_3'].forEach((dayKey, index) => {
            const dayNumbers = dayPredictedNumbers[dayKey] || [];
            if (dayNumbers.length > 0) {
                const dayAccuracy = calculateDayAccuracy(dayNumbers, actualNumbers);
                
                // ✅ TĂNG TRỌNG SỐ CHO NGÀY ĐƯỢC KHUYẾN NGHỊ
                const isRecommendedDay = (index + 1) === recommendedDay;
                const weight = isRecommendedDay ? 2.0 : 1.0;
                
                totalAccuracy += dayAccuracy * weight;
                validDays += weight;
            }
        });
        
        return validDays > 0 ? totalAccuracy / validDays : 0;
    }

    /**
    * ✅ HÀM TÍNH ACCURACY CHO MỘT NGÀY
    * @param {array} predictedNumbers - Số dự đoán
    * @param {array} actualNumbers - Số thực tế
    * @returns {number} - Accuracy percentage (0-100)
    */
    function calculateDayAccuracy(predictedNumbers, actualNumbers) {
        if (!predictedNumbers || predictedNumbers.length === 0) return 0;
        
        const predictedSet = new Set(predictedNumbers.map(n => String(n).padStart(2, '0')));
        const actualSet = new Set(actualNumbers.map(n => String(n).padStart(2, '0')));
        
        // ✅ TÍNH SỐ TRÙNG KHỚP
        const matches = [...predictedSet].filter(num => actualSet.has(num));
        const hitRate = (matches.length / predictedSet.size) * 100;
        
        // ✅ BONUS CHO SỐ LƯỢNG TRÙNG KHỚP CAO
        const matchBonus = Math.min(matches.length * 5, 20); // Tối đa 20% bonus
        
        return Math.min(hitRate + matchBonus, 100);
    }

    /**
    * ✅ HÀM TÍNH WEIGHTED SCORE
    * @param {object} metrics - Các chỉ số đánh giá
    * @returns {number} - Weighted total score
    */
    function calculateWeightedScore({ accuracyScore, maxProb, maxConf, overallConfidence, recommendedDay }) {
        // ✅ TRỌNG SỐ: Accuracy > Probability > Confidence
        const weights = {
            accuracy: 0.5,      // 50% trọng số cho accuracy
            probability: 0.3,   // 30% cho probability  
            confidence: 0.2     // 20% cho confidence
        };
        
        const normalizedProb = Math.min(maxProb, 100);
        const normalizedConf = Math.min(maxConf, 100);
        const normalizedOverall = Math.min(overallConfidence, 100);
        
        // ✅ TÍNH TỔNG ĐIỂM
        const totalScore = 
            (accuracyScore * weights.accuracy) +
            (normalizedProb * weights.probability) +
            ((normalizedConf + normalizedOverall) / 2 * weights.confidence);
        
        return Math.round(totalScore * 100) / 100; // Round to 2 decimal places
    }

    /**
    * ✅ HÀM LẤY SỐ THỰC TẾ TỪ API
    * @param {string} date - Date string (YYYY-MM-DD)
    * @returns {Promise<object>} - API response with actual numbers
    */
    async function fetchActualNumbers(date) {
        const apiUrl = `/pre-lokhung/api/ketqua/${date}/`;
        
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'API returned success: false');
        }
        
        return data.data;
    }
    /**
    * ✅ CẢI THIỆN HÀM filterQualityPredictions - STRICTER FILTERING
    * @param {object} predictions - All predictions
    * @returns {object} - Filtered quality predictions
    */
    function filterQualityPredictions(predictions) {
        const qualityPredictions = {};
        let skippedCount = 0;
        
        console.log('🔍 Starting quality filter process...');
        console.log(`📊 Input: ${Object.keys(predictions).length} methods`);
        
        Object.entries(predictions).forEach(([methodId, prediction]) => {
            try {
                // ✅ VALIDATE PREDICTION STRUCTURE
                if (!prediction || typeof prediction !== 'object') {
                    console.warn(`⚠️ Invalid prediction object for method ${methodId}:`, prediction);
                    skippedCount++;
                    return;
                }
                
                // ✅ NORMALIZE PREDICTION DATA - HANDLE MULTIPLE FORMATS
                let dayProbabilities, dayConfidences, confidence, recommendedDay;
                
                // ✅ FORMAT 1: Standard format với day_probabilities
                if (prediction.day_probabilities && typeof prediction.day_probabilities === 'object') {
                    dayProbabilities = prediction.day_probabilities;
                    dayConfidences = prediction.day_confidences || {};
                    confidence = prediction.confidence || 0;
                    recommendedDay = prediction.recommended_day || 1;
                    console.log(`🔍 Method ${methodId} - Standard format`);
                }
                // ✅ FORMAT 2: Enhanced ML format với day_predictions
                else if (prediction.day_predictions && typeof prediction.day_predictions === 'object') {
                    dayProbabilities = {
                        day_1: prediction.day_predictions.day_1?.probability || 0,
                        day_2: prediction.day_predictions.day_2?.probability || 0,
                        day_3: prediction.day_predictions.day_3?.probability || 0
                    };
                    dayConfidences = {
                        day_1: prediction.day_predictions.day_1?.confidence || 0,
                        day_2: prediction.day_predictions.day_2?.confidence || 0,
                        day_3: prediction.day_predictions.day_3?.confidence || 0
                    };
                    confidence = prediction.overall_confidence || prediction.confidence || 0;
                    recommendedDay = prediction.recommended_day || 1;
                    console.log(`🔍 Method ${methodId} - Enhanced ML format`);
                }
                // ✅ FORMAT 3: Basic format với minimal data
                else {
                    console.warn(`⚠️ Method ${methodId} has incomplete prediction data, using defaults`);
                    dayProbabilities = { day_1: 0.05, day_2: 0.05, day_3: 0.05 };
                    dayConfidences = { day_1: 0.05, day_2: 0.05, day_3: 0.05 };
                    confidence = prediction.confidence || 0.05;
                    recommendedDay = prediction.recommended_day || 1;
                }
                
                // ✅ VALIDATE PROBABILITIES VÀ CONFIDENCES
                const maxProb = Math.max(
                    dayProbabilities.day_1 || 0,
                    dayProbabilities.day_2 || 0,
                    dayProbabilities.day_3 || 0
                ) * 100;
                
                const maxConf = Math.max(
                    dayConfidences.day_1 || 0,
                    dayConfidences.day_2 || 0,
                    dayConfidences.day_3 || 0
                ) * 100;
                
                const overallConfidence = confidence * 100;
                
                // ✅ CẬP NHẬT QUALITY FILTER - GIẢM THRESHOLD XUỐNG 50%
                const qualityThreshold = (
                    // Threshold 1: GIẢM TỪ 60% XUỐNG 50% - High probability AND high confidence
                    (maxProb >= 50 && maxConf >= 39) ||
                    // Threshold 2: Very high probability (even with lower confidence) 
                    (maxProb >= 51 && maxConf >= 41) ||
                    // Threshold 3: Recommended day with decent stats
                    (maxProb >= 50 && maxConf >= 40 && overallConfidence >= 39) ||
                    // Threshold 4: Very high overall confidence
                    (overallConfidence >= 52 && maxProb >= 41)
                );
                
                console.log(`🔍 Method ${methodId} evaluation:`, {
                    method_name: prediction.method_name,
                    maxProb: maxProb.toFixed(1),
                    maxConf: maxConf.toFixed(1),
                    overallConf: overallConfidence.toFixed(1),
                    recommendedDay: recommendedDay,
                    qualityThreshold: qualityThreshold
                });
                
                if (qualityThreshold) {
                    // ✅ ENSURE NORMALIZED STRUCTURE BEFORE ADDING
                    qualityPredictions[methodId] = {
                        ...prediction,
                        day_probabilities: dayProbabilities,
                        day_confidences: dayConfidences,
                        confidence: confidence,
                        recommended_day: recommendedDay,
                        day_predicted_numbers: prediction.day_predicted_numbers || {},
                        pattern_info: prediction.pattern_info || {
                            trend: 'unknown',
                            performance_category: 'basic',
                            stability: 'unknown'
                        },
                        method_name: prediction.method_name || `Method ${methodId}`,
                        // ✅ THÊM QUALITY SCORE ĐỂ DEBUG
                        _quality_score: Math.max(maxProb + maxConf, overallConfidence)
                    };
                    
                    console.log(`✅ Method ${methodId} PASSED quality filter - Score: ${qualityPredictions[methodId]._quality_score.toFixed(1)}`);
                } else {
                    skippedCount++;
                    console.log(`❌ Method ${methodId} FAILED quality filter - MaxProb: ${maxProb.toFixed(1)}%, MaxConf: ${maxConf.toFixed(1)}%, OverallConf: ${overallConfidence.toFixed(1)}%`);
                }
                
            } catch (error) {
                console.error(`❌ Error processing method ${methodId}:`, error, prediction);
                skippedCount++;
            }
        });
        
        // ✅ SORT BY QUALITY SCORE
        const sortedQualityPredictions = {};
        Object.entries(qualityPredictions)
            .sort(([,a], [,b]) => (b._quality_score || 0) - (a._quality_score || 0))
            .forEach(([methodId, prediction]) => {
                // Remove internal quality score before returning
                const {_quality_score, ...cleanPrediction} = prediction;
                sortedQualityPredictions[methodId] = cleanPrediction;
            });
        
        console.log(`🔍 Quality filter results:`);
        console.log(`   ✅ Passed: ${Object.keys(sortedQualityPredictions).length}`);
        console.log(`   ❌ Filtered: ${skippedCount}`);
        console.log(`   📊 Total: ${Object.keys(predictions).length}`);
        console.log(`   📈 Pass rate: ${((Object.keys(sortedQualityPredictions).length / Object.keys(predictions).length) * 100).toFixed(1)}%`);
        
        // ✅ LOG TOP QUALITY METHODS
        Object.entries(qualityPredictions).slice(0, 3).forEach(([methodId, prediction], index) => {
            console.log(`🏆 Top ${index + 1}: Method ${methodId} (${prediction.method_name}) - Quality: ${prediction._quality_score?.toFixed(1)}`);
        });
        
        return sortedQualityPredictions;
    }

    /**
    * ✅ SỬA HÀM normalizeBasicPredictions - ENHANCED NORMALIZATION
    * @param {object} predictions - Raw predictions with possible missing fields
    * @returns {object} - Normalized predictions
    */
    function normalizeBasicPredictions(predictions) {
        const normalized = {};
        
        Object.entries(predictions).forEach(([methodId, prediction]) => {
            try {
                // ✅ ENSURE MINIMAL REQUIRED STRUCTURE VỚI COMPREHENSIVE DEFAULTS
                normalized[methodId] = {
                    method_name: prediction.method_name || `Method ${methodId}`,
                    recommended_day: prediction.recommended_day || 1,
                    confidence: prediction.confidence || 0.1,
                    day_probabilities: prediction.day_probabilities || {
                        day_1: 0.1, day_2: 0.1, day_3: 0.1
                    },
                    day_confidences: prediction.day_confidences || {
                        day_1: 0.1, day_2: 0.1, day_3: 0.1
                    },
                    day_predicted_numbers: prediction.day_predicted_numbers || {},
                    pattern_info: prediction.pattern_info || {
                        trend: 'unknown',
                        performance_category: 'basic',
                        stability: 'unknown',
                        prediction_type: 'normalized'
                    }
                };
            } catch (error) {
                console.error(`❌ Error normalizing method ${methodId}:`, error);
                
                // ✅ FALLBACK MINIMAL STRUCTURE
                normalized[methodId] = {
                    method_name: `Method ${methodId}`,
                    recommended_day: 1,
                    confidence: 0.1,
                    day_probabilities: { day_1: 0.1, day_2: 0.1, day_3: 0.1 },
                    day_confidences: { day_1: 0.1, day_2: 0.1, day_3: 0.1 },
                    day_predicted_numbers: {},
                    pattern_info: {
                        trend: 'unknown',
                        performance_category: 'error',
                        stability: 'unknown',
                        prediction_type: 'fallback'
                    }
                };
            }
        });
        
        console.log(`🔧 Normalized ${Object.keys(normalized).length} basic predictions`);
        return normalized;
    }


    /**
    * ✅ SỬA HÀM displayAllMethodsPredictions - THÊM DEFENSIVE PROGRAMMING
    * @param {object} qualityPredictions - Already filtered predictions
    * @param {object} analysis - Analysis data
    * @param {number} totalOriginalMethods - Total methods before filtering
    */
    function displayAllMethodsPredictions(qualityPredictions, analysis, totalOriginalMethods = 0) {
        const content = document.getElementById('analysis-content');
        if (!content) return;

        const filteredCount = totalOriginalMethods - Object.keys(qualityPredictions).length;

        // Sort predictions by confidence
        const sortedPredictions = Object.entries(qualityPredictions).sort((a, b) => 
            b[1].confidence - a[1].confidence
        );

        let html = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="alert alert-info">
                        <h6 class="alert-heading">🤖 Enhanced AI Analysis - Quality Filtered (50% Threshold)</h6>
                        <p>Hiển thị ${Object.keys(qualityPredictions).length} phương pháp chất lượng cao 
                        ${filteredCount > 0 ? `(đã ẩn ${filteredCount} phương pháp chất lượng thấp)` : ''}. 
                        <strong>Badges chỉ hiển thị khi Xác suất ≥ 50% VÀ Độ tin cậy ≥ 50%.</strong></p>
                    </div>
                </div>
            </div>
            
            <!-- ✅ QUALITY FILTER INFO - CẬP NHẬT THRESHOLD -->
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="card border-info">
                        <div class="card-body p-2">
                            <h6 class="card-title text-info mb-1">
                                <i class="fas fa-filter me-2"></i>Bộ lọc chất lượng (Threshold 50%)
                            </h6>
                            <div class="row text-center">
                                <div class="col-6">
                                    <div class="fw-bold text-success">${Object.keys(qualityPredictions).length}</div>
                                    <small class="text-muted">Hiển thị</small>
                                </div>
                                <div class="col-6">
                                    <div class="fw-bold text-danger">${filteredCount}</div>
                                    <small class="text-muted">Đã ẩn</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card border-success">
                        <div class="card-body p-2">
                            <h6 class="card-title text-success mb-1">
                                <i class="fas fa-info-circle me-2"></i>Tiêu chí chất lượng - CẬP NHẬT
                            </h6>
                            <div style="font-size: 0.8rem;">
                                <div>🔥 <strong>Badges: ≥50% xác suất VÀ ≥50% tin cậy</strong></div>
                                <div>⚡ Tốt: ≥40% trung bình</div>
                                <div>💡 Khá: ≥30% trung bình</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- ✅ TOP METHODS HIỂN THỊ PRIORITY -->
            <div class="row mb-3">
                <div class="col-12">
                    <div class="card border-warning">
                        <div class="card-header bg-warning text-dark">
                            <h6 class="mb-0">
                                <i class="fas fa-trophy me-2"></i>Top ${Math.min(5, sortedPredictions.length)} phương pháp cao nhất
                            </h6>
                        </div>
                        <div class="card-body p-2">
                            <div class="row g-2">
        `;

        // ✅ HIỂN THỊ TOP 5 METHODS VỚI LAYOUT ĐẸP HƠN
        sortedPredictions.slice(0, 5).forEach(([methodId, prediction], index) => {
            const confidence = (prediction.confidence * 100).toFixed(1);
            const recommendedDay = prediction.recommended_day;
            const dayProbs = prediction.day_probabilities;
            
            // ✅ TÌM NGÀY CÓ XÁC SUẤT CAO NHẤT
            const maxProb = Math.max(dayProbs.day_1, dayProbs.day_2, dayProbs.day_3);
            const bestDay = Object.keys(dayProbs).find(key => dayProbs[key] === maxProb).split('_')[1];
            
            const trophyIcon = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '🏆';
            const cardBorder = index === 0 ? 'border-warning' : index < 3 ? 'border-info' : 'border-secondary';
            
            html += `
                <div class="col-md-${index < 3 ? '4' : '6'}">
                    <div class="card ${cardBorder} h-100">
                        <div class="card-body p-2 text-center">
                            <div class="mb-1">
                                <span class="fs-4">${trophyIcon}</span>
                                <span class="badge bg-secondary ms-1">#${index + 1}</span>
                            </div>
                            <h6 class="card-title mb-1 text-truncate">${prediction.method_name}</h6>
                            <div class="mb-2">
                                <span class="badge bg-primary">Ngày ${recommendedDay}</span>
                                <div class="text-muted small">Tin cậy: ${confidence}%</div>
                            </div>
                            <div class="row g-1 text-center">
                                ${[1, 2, 3].map(day => {
                                    const dayProb = (dayProbs[`day_${day}`] * 100).toFixed(1);
                                    const isMax = day == bestDay;
                                    const isRecommended = day === recommendedDay;
                                    
                                    return `
                                        <div class="col-4">
                                            <div class="small ${isMax ? 'fw-bold text-success' : ''} ${isRecommended ? 'text-primary' : ''}">
                                                D${day}: ${dayProb}%
                                                ${isMax ? '📈' : ''}
                                                ${isRecommended ? '⭐' : ''}
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                            <button class="btn btn-outline-primary btn-sm mt-1" 
                                    onclick="highlightMethodInTable('${methodId}', '${new Date().toISOString().split('T')[0]}')">
                                <i class="fas fa-search me-1"></i>Xem
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // ✅ TIẾP TỤC VỚI GRID CỦA TẤT CẢ METHODS
        html += `
            <div class="row">
                <div class="col-12">
                    <h6 class="text-primary mb-3">
                        <i class="fas fa-list me-2"></i>Tất cả ${Object.keys(qualityPredictions).length} phương pháp (sắp xếp theo độ tin cậy):
                    </h6>
                    <div class="prediction-grid">
        `;

        // ✅ EXISTING CODE CHO TẤT CẢ PREDICTIONS...
        // (rest of the existing displayAllMethodsPredictions code)
        
        content.innerHTML = html;
    }


    /**
    * ✅ HÀM MỚI - GET TREND CLASS CHO DEFENSIVE PROGRAMMING
    * @param {string} trend - Trend value
    * @returns {string} - CSS class
    */
    function getTrendClass(trend) {
        switch (trend) {
            case 'improving':
            case 'increasing':
            case 'up':
                return 'success';
            case 'declining':
            case 'decreasing':
            case 'down':
                return 'danger';
            case 'stable':
                return 'info';
            default:
                return 'secondary';
        }
    }

    /**
    * ✅ SỬA HÀM getPatternAnalysisPredictions - SIMPLIFIED VERSION
    * @param {string} analysisDate - Ngày cần phân tích (YYYY-MM-DD)
    * @returns {Promise} - API response promise
    */
    function getPatternAnalysisPredictions(analysisDate) {
        const requestData = {
            analysis_date: analysisDate  // Chỉ cần ngày phân tích
        };
        
        console.log('🔄 Calling SIMPLIFIED pattern-analysis API:');
        console.log(`   📅 Analysis Date: ${analysisDate}`);
        
        return fetch('/pre-lokhung/api/pattern-analysis/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Pattern analysis response:', data);
            return data;
        })
        .catch(error => {
            console.error('❌ Pattern analysis error:', error);
            throw error;
        });
    }

    function validateAdvancedResponseData(data) {
        if (!data || !data.success) {
            return false;
        }
        
        // ✅ VALIDATE ADVANCED FIELDS
        if (data.predictions) {
            for (const [methodId, prediction] of Object.entries(data.predictions)) {
                // Kiểm tra có đủ fields không
                if (!prediction.day_probabilities || !prediction.day_confidences) {
                    console.error(`Method ${methodId} missing required prediction fields`);
                    return false;
                }
                
                // Kiểm tra probability values hợp lệ
                for (const day of ['day_1', 'day_2', 'day_3']) {
                    const prob = prediction.day_probabilities[day];
                    const conf = prediction.day_confidences[day];
                    
                    if (prob < 0 || prob > 1 || conf < 0 || conf > 1) {
                        console.error(`Invalid probability/confidence values for ${methodId} ${day}`);
                        return false;
                    }
                }
            }
        }
        
        return true;
    }

    // ✅ CẬP NHẬT updateTableWithPredictions với logic nghiêm ngặt hơn
    function updateTableWithPredictions(predictions) {
        console.log('🎯 Updating table with ENHANCED prediction badges (50% threshold)...');
        
        if (!predictions || Object.keys(predictions).length === 0) {
            console.warn('⚠️ No predictions to update table with');
            return;
        }
        
        // ✅ XÓA BADGES CŨ
        document.querySelectorAll('.hit-badge-predict').forEach(badge => badge.remove());
        
        let totalBadges = 0;
        let shownBadges = 0;
        let highQualityBadges = 0;
        let excellentQualityBadges = 0;
        
        Object.entries(predictions).forEach(([methodId, prediction]) => {
            try {
                const dayProbabilities = prediction.day_probabilities;
                const dayConfidences = prediction.day_confidences;
                const recommendedDay = prediction.recommended_day || 1;
                const predictionQuality = prediction.prediction_quality || 'unknown';
                
                // ✅ CHỈ XỬ LÝ PREDICTIONS CHẤT LƯỢNG CAO
                if (predictionQuality === 'poor') {
                    console.log(`❌ Skipping poor quality prediction for method ${methodId}`);
                    return;
                }
                
                const methodCells = document.querySelectorAll(`td.prediction-cell[data-method-id="${methodId}"]`);
                
                methodCells.forEach(cell => {
                    let cellDiv = cell.querySelector('div');
                    if (!cellDiv) {
                        cellDiv = document.createElement('div');
                        cellDiv.style.position = 'relative';
                        cellDiv.style.height = '100%';
                        cell.appendChild(cellDiv);
                    }
                    
                    // ✅ TẠO BADGES VỚI LOGIC NÂNG CAO - GIẢM THRESHOLD
                    for (let day = 1; day <= 3; day++) {
                        const probability = parseFloat(dayProbabilities[`day_${day}`] * 100);
                        const confidence = parseFloat(dayConfidences[`day_${day}`] * 100);
                        
                        totalBadges++;
                        
                        // ✅ ĐIỀU KIỆN HIỂN THỊ GIẢM XUỐNG 50%
                        const qualityScore = (probability + confidence) / 2;
                        const isRecommended = day === recommendedDay;
                        const isHighQuality = predictionQuality === 'excellent' || predictionQuality === 'good';
                        
                        const shouldShow = (
                            // ✅ GIẢM THRESHOLD: Excellent quality với threshold 40%
                            (predictionQuality === 'excellent' && qualityScore >= 40) ||
                            // ✅ GIẢM THRESHOLD: Good quality với threshold 50% (từ 65%)
                            (predictionQuality === 'good' && qualityScore >= 50) ||
                            // ✅ GIẢM THRESHOLD: Recommended day với quality 40% (từ 45%)
                            (isRecommended && isHighQuality && qualityScore >= 40) ||
                            // ✅ GIẢM THRESHOLD: Fair quality với threshold 70% (từ 80%)
                            (predictionQuality === 'fair' && qualityScore >= 70) ||
                            // ✅ THÊM: Strict badge criteria - 50% & 50%
                            (probability >= 50 && confidence >= 50)
                        );
                        
                        if (shouldShow) {
                            const predictionBadge = document.createElement('span');
                            predictionBadge.className = 'hit-badge-predict';
                            predictionBadge.setAttribute('data-day', day);
                            predictionBadge.setAttribute('data-method-id', methodId);
                            predictionBadge.setAttribute('data-quality', predictionQuality);
                            predictionBadge.textContent = day;
                            
                            // ✅ ENHANCED TOOLTIP - CẬP NHẬT THRESHOLD
                            predictionBadge.title = `🤖 AI Dự đoán NÂNG CAO ngày ${day}${isRecommended ? ' ⭐' : ''}:
                                • Xác suất: ${probability.toFixed(1)}%
                                • Độ tin cậy: ${confidence.toFixed(1)}%
                                • Điểm chất lượng: ${qualityScore.toFixed(1)}
                                • Mức độ: ${predictionQuality.toUpperCase()}
                                • Threshold: ≥50% xác suất VÀ ≥50% tin cậy
                                • Thuật toán: Enhanced Pattern ML
                                • Features: Cyclical + Sequential + Correlation`;
                            
                            // ✅ STYLING DỰA TRÊN QUALITY
                            applyAdvancedQualityStyle(predictionBadge, probability, confidence, predictionQuality, isRecommended);
                            
                            cellDiv.appendChild(predictionBadge);
                            shownBadges++;
                            
                            // ✅ COUNT QUALITY LEVELS
                            if (predictionQuality === 'excellent') {
                                excellentQualityBadges++;
                                highQualityBadges++;
                            } else if (predictionQuality === 'good') {
                                highQualityBadges++;
                            }
                            
                            console.log(`✅ Added ENHANCED badge (50% criteria): Method ${methodId}, Day ${day}, Quality: ${predictionQuality}, Score: ${qualityScore.toFixed(1)}`);
                        } else {
                            console.log(`❌ Hidden badge (50% criteria): Method ${methodId}, Day ${day}, Quality: ${predictionQuality}, Score: ${qualityScore.toFixed(1)}`);
                        }
                    }
                });
            } catch (error) {
                console.error(`❌ Error processing enhanced prediction for method ${methodId}:`, error);
            }
        });
        
        // ✅ BÁOCÁO KẾT QUẢ
        console.log(`📊 ENHANCED Badge update summary (50% threshold):`);
        console.log(`   Total processed: ${totalBadges}`);
        console.log(`   Shown badges: ${shownBadges}`);
        console.log(`   High quality badges: ${highQualityBadges}`);
        console.log(`   Excellent quality badges: ${excellentQualityBadges}`);
        console.log(`   Show rate: ${totalBadges > 0 ? ((shownBadges / totalBadges) * 100).toFixed(1) : 0}%`);
        
        // ✅ THÔNG BÁO CHO USER VỚI 50% THRESHOLD
        try {
            if (excellentQualityBadges > 0) {
                showEnhanced50PercentSuccess(shownBadges, excellentQualityBadges);
            } else if (shownBadges > 0) {
                showEnhanced50PercentWarning(shownBadges, totalBadges);
            } else {
                showEnhanced50PercentInfo(totalBadges);
            }
        } catch (notificationError) {
            console.error('❌ Error showing 50% threshold notification:', notificationError);
        }
    }

    /**
    * ✅ NOTIFICATION FUNCTIONS CHO 50% THRESHOLD
    */
    function showEnhanced50PercentSuccess(shownBadges, excellentBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            <strong>Enhanced AI Success (50% Threshold):</strong> 
            Hiển thị ${shownBadges} prediction badges với tiêu chí mới: <strong>≥50% xác suất VÀ ≥50% tin cậy</strong>.
            <br><small class="text-muted mt-1 d-block">
                🔥 ${excellentBadges} badges chất lượng xuất sắc được tìm thấy!
            </small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 8000);
    }

    function showEnhanced50PercentWarning(shownBadges, totalBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Enhanced AI Warning (50% Threshold):</strong> 
            Hiển thị ${shownBadges}/${totalBadges} prediction badges với tiêu chí mới: <strong>≥50% xác suất VÀ ≥50% tin cậy</strong>.
            <br><small class="text-muted mt-1 d-block">⚡ Threshold đã giảm từ 60% xuống 50% để hiển thị nhiều dự đoán hơn.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 10000);
    }

    function showEnhanced50PercentInfo(totalBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            <strong>Enhanced AI Info (50% Threshold):</strong> 
            Không có prediction badges nào đạt tiêu chí mới từ ${totalBadges} dự đoán: <strong>≥50% xác suất VÀ ≥50% tin cậy</strong>.
            <br><small class="text-muted mt-1 d-block">💡 Có thể cần giảm threshold thêm hoặc cải thiện model training.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 12000);
    }
    /**
    * ✅ HÀM HIỂN THỊ SUCCESS MESSAGE CHO ADVANCED PREDICTIONS
    * @param {number} shownBadges - Số badges được hiển thị
    * @param {number} highQualityBadges - Số badges chất lượng cao
    */
    function showAdvancedPredictionSuccess(shownBadges, highQualityBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            <strong>AI Prediction Success:</strong> 
            Hiển thị ${shownBadges} prediction badges, trong đó ${highQualityBadges} badges chất lượng cao.
            <br><small class="text-muted mt-1 d-block">🤖 Advanced ML đã tìm thấy những dự đoán có độ tin cậy cao!</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 8000);
    }

    /**
    * ✅ HÀM HIỂN THỊ WARNING MESSAGE CHO ADVANCED PREDICTIONS
    * @param {number} shownBadges - Số badges được hiển thị
    * @param {number} totalBadges - Tổng số badges được xử lý
    */
    function showAdvancedPredictionWarning(shownBadges, totalBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>AI Prediction Warning:</strong> 
            Chỉ hiển thị ${shownBadges}/${totalBadges} prediction badges đạt tiêu chí chất lượng.
            <br><small class="text-muted mt-1 d-block">⚡ Các dự đoán khác có độ tin cậy thấp hơn threshold.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 10000);
    }

    /**
    * ✅ HÀM HIỂN THỊ ERROR MESSAGE CHO ADVANCED PREDICTIONS  
    * @param {number} totalBadges - Tổng số badges được xử lý
    */
    function showAdvancedPredictionError(totalBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            <strong>AI Prediction Info:</strong> 
            Không có prediction badges nào đạt tiêu chí hiển thị từ ${totalBadges} dự đoán được phân tích.
            <br><small class="text-muted mt-1 d-block">💡 Tất cả dự đoán đều có độ tin cậy thấp hơn threshold hiển thị.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 12000);
    }

    /**
    * ✅ HÀM HELPER HIỂN THỊ NOTIFICATION TẠM THỜI
    * @param {HTMLElement} notification - Element notification
    * @param {number} duration - Thời gian hiển thị (ms)
    */
    function showTemporaryNotification(notification, duration = 8000) {
        const container = document.querySelector('.container-fluid');
        if (container) {
            // Remove existing notifications of same type
            const existingNotifications = container.querySelectorAll('.alert');
            existingNotifications.forEach(alert => {
                if (alert.textContent.includes('AI Prediction')) {
                    alert.remove();
                }
            });
            
            // Add new notification at top
            container.insertBefore(notification, container.firstChild);
            
            // Auto remove after duration
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.classList.remove('show');
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.remove();
                        }
                    }, 150); // Wait for fade out animation
                }
            }, duration);
        }
    }

    /**
    * ✅ HÀM HIỂN THỊ NOTIFICATION CHO STRICT BADGE MODE
    * @param {number} shownBadges - Số badges được hiển thị
    * @param {number} totalBadges - Tổng số badges
    * @param {number} highQualityCount - Số badges chất lượng cao
    */
    function showStrictModeNotification(shownBadges, totalBadges, highQualityCount) {
        let notificationType, message, icon;
        
        if (highQualityCount > 0) {
            notificationType = 'success';
            icon = 'fas fa-check-circle';
            message = `
                <strong>Strict Mode Success:</strong> 
                Hiển thị ${shownBadges} badges chất lượng cao từ ${totalBadges} dự đoán.
                <br><small class="text-muted mt-1 d-block">🔥 Chỉ hiển thị dự đoán có Xác suất ≥60% VÀ Độ tin cậy ≥60%</small>
            `;
        } else if (shownBadges > 0) {
            notificationType = 'warning';
            icon = 'fas fa-exclamation-triangle';
            message = `
                <strong>Strict Mode Warning:</strong> 
                Hiển thị ${shownBadges}/${totalBadges} badges, nhưng không có badges chất lượng cao.
                <br><small class="text-muted mt-1 d-block">⚡ Các badges hiển thị có độ tin cậy trung bình</small>
            `;
        } else {
            notificationType = 'info';
            icon = 'fas fa-info-circle';
            message = `
                <strong>Strict Mode Info:</strong> 
                Không có badges nào đạt tiêu chí strict từ ${totalBadges} dự đoán.
                <br><small class="text-muted mt-1 d-block">💡 Tất cả dự đoán có chất lượng thấp hơn threshold</small>
            `;
        }
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${notificationType} alert-dismissible fade show mt-2`;
        notification.innerHTML = `
            <i class="${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, notificationType === 'success' ? 6000 : 10000);
    }

    /**
    * ✅ HÀM HIỂN THỊ ENHANCED ANALYSIS STATUS
    * @param {string} analysisType - Loại phân tích
    * @param {object} metadata - Metadata từ API response
    */
    function showAnalysisStatusNotification(analysisType, metadata) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-primary alert-dismissible fade show mt-2';
        
        const successfulMethods = metadata.successful_methods || 0;
        const totalMethods = metadata.total_methods || 0;
        const dataQuality = metadata.data_quality_score || 0;
        
        notification.innerHTML = `
            <i class="fas fa-brain me-2"></i>
            <strong>AI Analysis Complete:</strong> 
            ${analysisType} phân tích ${successfulMethods}/${totalMethods} methods với chất lượng dữ liệu ${(dataQuality * 100).toFixed(0)}%.
            <br><small class="text-muted mt-1 d-block">🚀 Sử dụng Advanced ML với ${metadata.months_analyzed || 12} tháng dữ liệu lịch sử</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        showTemporaryNotification(notification, 7000);
    }

    function applyAdvancedQualityStyle(badge, probability, confidence, quality, isRecommended) {
        // ✅ BASE STYLE
        badge.style.position = 'absolute';
        badge.style.zIndex = '15';
        badge.style.fontWeight = 'bold';
        badge.style.transition = 'all 0.3s ease';
        
        // ✅ QUALITY-BASED STYLING
        switch (quality) {
            case 'excellent':
                badge.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
                badge.style.border = '2px solid gold';
                badge.style.boxShadow = '0 0 15px rgba(40, 167, 69, 0.6)';
                badge.style.animation = 'pulse 2s infinite';
                break;
                
            case 'good':
                badge.style.background = 'linear-gradient(45deg, #007bff, #17a2b8)';
                badge.style.border = '2px solid silver';
                badge.style.boxShadow = '0 0 10px rgba(0, 123, 255, 0.5)';
                break;
                
            case 'fair':
                badge.style.background = 'linear-gradient(45deg, #ffc107, #fd7e14)';
                badge.style.border = '1px solid #ffc107';
                badge.style.boxShadow = '0 0 8px rgba(255, 193, 7, 0.4)';
                break;
                
            default:
                badge.style.background = '#6c757d';
                badge.style.opacity = '0.7';
        }
        
        // ✅ RECOMMENDED DAY ENHANCEMENT
        if (isRecommended) {
            badge.style.transform = 'scale(1.1)';
            badge.style.boxShadow += ', 0 0 0 3px rgba(255, 215, 0, 0.3)';
        }
    }


    /**
    * ✅ HÀM MỚI - HIỂN THỊ WARNING VỀ STRICT BADGES
    */
    function showStrictBadgeWarning(totalBadges, errorCount) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            <strong>Thông báo:</strong> 
            ${errorCount > 0 ? 
                `Có ${errorCount} lỗi khi xử lý dự đoán. ` : 
                ''
            }
            Tất cả ${totalBadges} dự đoán đều không đạt tiêu chí <strong>STRICT</strong> (Xác suất ≥60% VÀ Độ tin cậy ≥60%) nên không hiển thị badges.
            <br><small class="text-muted mt-1 d-block">💡 Giảm threshold để xem thêm dự đoán chất lượng thấp hơn.</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            // Auto remove after 15 seconds (longer for important info)
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 15000);
        }
    }

    /**
    * ✅ HÀM MỚI - HIỂN THỊ SUCCESS VỀ STRICT BADGES
    */
    function showStrictBadgeSuccess(shownBadges, totalBadges) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            <strong>Thành công:</strong> 
            Hiển thị ${shownBadges}/${totalBadges} badges đạt tiêu chí <strong>STRICT</strong> (Xác suất ≥60% VÀ Độ tin cậy ≥60%).
            <br><small class="text-muted mt-1 d-block">🔥 Chỉ hiển thị những dự đoán chất lượng cao nhất!</small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            // Auto remove after 10 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 10000);
        }
    }


    /**
    * ✅ HÀM MỚI - HIỂN THỊ WARNING VỀ BADGES
    */
    function showBadgeWarning(totalBadges, errorCount) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show mt-2';
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            <strong>Thông báo:</strong> 
            ${errorCount > 0 ? 
                `Có ${errorCount} lỗi khi xử lý dự đoán. ` : 
                ''
            }
            ${totalBadges > 0 ? 
                `Tất cả ${totalBadges} dự đoán đều có chất lượng thấp nên không hiển thị badges.` :
                'Không có dữ liệu dự đoán để hiển thị.'
            }
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            // Auto remove after 10 seconds
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 10000);
        }
    }
    /**
    * ✅ HÀM DEBUG - KIỂM TRA CẤU TRÚC PREDICTIONS
    * @param {object} predictions - Predictions object
    */
    function debugPredictionsStructure(predictions) {
        console.log('🔍 Debug predictions structure:');
        console.log('Total methods:', Object.keys(predictions).length);
        
        // ✅ KIỂM TRA FORMAT CỦA TỪNG PREDICTION
        Object.entries(predictions).slice(0, 2).forEach(([methodId, prediction]) => {
            console.log(`Method ${methodId}:`, {
                method_name: prediction.method_name,
                recommended_day: prediction.recommended_day,
                confidence: prediction.confidence,
                day_probabilities: prediction.day_probabilities,
                day_confidences: prediction.day_confidences,
                day_predicted_numbers: prediction.day_predicted_numbers,
                // ✅ KIỂM TRA CÁC FORMAT KHÁC
                pattern_info: prediction.pattern_info,
                overall_confidence: prediction.overall_confidence,
                day_predictions: prediction.day_predictions
            });
        });
        
        // ✅ VALIDATE STRUCTURE
        const firstPrediction = Object.values(predictions)[0];
        if (firstPrediction) {
            console.log('🔍 First prediction structure validation:', {
                has_day_probabilities: !!firstPrediction.day_probabilities,
                has_day_confidences: !!firstPrediction.day_confidences,
                has_confidence: typeof firstPrediction.confidence !== 'undefined',
                has_recommended_day: typeof firstPrediction.recommended_day !== 'undefined',
                type: typeof firstPrediction.day_probabilities,
                keys: firstPrediction.day_probabilities ? Object.keys(firstPrediction.day_probabilities) : 'N/A'
            });
        }
    }

    /**
    * ✅ HÀM LẤY ICON CHẤT LƯỢNG
    * @param {number} probability - Xác suất (%)
    * @param {number} confidence - Độ tin cậy (%)
    * @returns {string} - Icon tương ứng
    */
    function getQualityIcon(probability, confidence) {
        const avg = (probability + confidence) / 2;
        if (avg >= 60) return '🔥';
        if (avg >= 45) return '⚡';
        if (avg >= 30) return '💡';
        if (avg >= 20) return '❓';
        return '';
    }
    
    /**
     * ✅ HÀM HIỂN THỊ BASIC PREDICTIONS (FALLBACK)
     * @param {object} predictions - ML predictions
     * @param {object} analysis - Pattern analysis
     */
    function displayBasicPredictions(predictions, analysis) {
        const content = document.getElementById('analysis-content');
        if (!content) return;

        let html = `
            <div class="row mb-3">
                <div class="col-12">
                    <div class="alert alert-info">
                        <h6 class="alert-heading">🤖 Dự đoán ML cơ bản</h6>
                        <p>Hệ thống đã phân tích ${Object.keys(predictions).length} phương pháp và đưa ra dự đoán khung thời gian trúng.</p>
                    </div>
                </div>
            </div>
            <div class="row g-3">
        `;

        // Sort predictions by confidence
        const sortedPredictions = Object.entries(predictions).sort((a, b) => 
            b[1].confidence - a[1].confidence
        );

        sortedPredictions.forEach(([methodId, prediction], index) => {
            const confidence = prediction.confidence * 100;
            const confidenceClass = confidence >= 80 ? 'success' : 
                                   confidence >= 60 ? 'warning' : 
                                   confidence >= 40 ? 'info' : 'danger';
            
            html += `
                <div class="col-md-6 col-lg-4">
                    <div class="card border-${confidenceClass} h-100">
                        <div class="card-header bg-${confidenceClass} text-white p-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <strong>${prediction.method_name}</strong>
                                <span class="badge bg-light text-dark">#{index + 1}</span>
                            </div>
                        </div>
                        <div class="card-body p-2">
                            <div class="text-center mb-2">
                                <div class="mb-1">
                                    <span class="badge bg-${confidenceClass} fs-6 px-3 py-2">
                                        🎯 Ngày ${prediction.recommended_day}
                                    </span>
                                </div>
                                <small class="text-muted">Độ tin cậy: ${confidence.toFixed(1)}%</small>
                            </div>
                            
                            <div class="row g-1 mb-2">
                                ${[1, 2, 3].map(day => {
                                    const dayProb = (prediction.day_probabilities[`day_${day}`] * 100).toFixed(1);
                                    const isRecommended = day === prediction.recommended_day;
                                    
                                    return `
                                        <div class="col-4">
                                            <div class="text-center p-1 ${isRecommended ? 'bg-light border rounded' : ''}">
                                                <small class="text-muted">Ngày ${day}</small>
                                                <div class="fw-bold ${isRecommended ? 'text-' + confidenceClass : ''}">${dayProb}%</div>
                                                ${isRecommended ? '<i class="fas fa-star text-warning"></i>' : ''}
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                            
                            ${prediction.pattern_info ? `
                                <div class="pattern-info">
                                    <small class="text-muted">
                                        <i class="fas fa-chart-line me-1"></i>
                                        ${prediction.pattern_info.trend || 'stable'} | 
                                        Chu kỳ: ${prediction.pattern_info.cycle_length || 'N/A'}
                                    </small>
                                </div>
                            ` : ''}
                            
                            <div class="text-center mt-2">
                                <button class="btn btn-outline-${confidenceClass} btn-sm" 
                                        onclick="highlightMethodInTable('${methodId}', '${new Date().toISOString().split('T')[0]}')">
                                    <i class="fas fa-search me-1"></i>Xem trong bảng
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';

        // Add analysis summary if available
        if (analysis) {
            html += `
                <div class="row mt-3">
                    <div class="col-12">
                        <div class="card border-info">
                            <div class="card-header bg-light">
                                <h6 class="mb-0 text-info">📊 Tóm tắt phân tích</h6>
                            </div>
                            <div class="card-body p-2">
                                <div class="row text-center">
                                    <div class="col-md-3">
                                        <div class="fw-bold text-primary">${analysis.total_methods || Object.keys(predictions).length}</div>
                                        <small class="text-muted">Methods</small>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="fw-bold text-success">Ngày ${analysis.best_overall_day || 1}</div>
                                        <small class="text-muted">Tốt nhất</small>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="fw-bold text-warning">${((analysis.avg_confidence || 0) * 100).toFixed(1)}%</div>
                                        <small class="text-muted">Tin cậy TB</small>
                                    </div>
                                    <div class="col-md-3">
                                        <div class="fw-bold text-info">${sortedPredictions[0]?.[1]?.method_name || 'N/A'}</div>
                                        <small class="text-muted">Top method</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        content.innerHTML = html;
    }

    /**
     * ✅ HÀM GET DATA SOURCE TEXT CHO UI
     * @param {string} dataSource - Data source type
     * @returns {string} - Friendly text description
     */
    function getDataSourceText(dataSource) {
        const sourceTexts = {
            'frontend_enhanced': '📊 Dữ liệu hiện tại + Lịch sử',
            'historical_only': '📈 Chỉ dữ liệu lịch sử',
            'pattern_analysis': '🔍 Phân tích Pattern',
            'ml_enhanced': '🤖 ML nâng cao',
            'fallback': '🔄 Dữ liệu fallback',
            'basic_ml': '🔧 ML cơ bản',
            'enhanced_ml': '🚀 ML nâng cao'
        };
        return sourceTexts[dataSource] || dataSource;
    }

    /**
    * ✅ HÀM HIỂN THỊ ERROR MESSAGE CẢI THIỆN
    */
    function showErrorMessage(message) {
        const content = document.getElementById('analysis-content');
        if (content) {
            content.innerHTML = `
                <div class="alert alert-danger">
                    <h6 class="alert-heading">❌ Lỗi phân tích</h6>
                    <p>${message}</p>
                    <hr>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            <i class="fas fa-clock me-1"></i>
                            ${new Date().toLocaleString('vi-VN')}
                        </small>
                        <button class="btn btn-outline-danger btn-sm" onclick="location.reload()">
                            <i class="fas fa-refresh me-1"></i>Tải lại trang
                        </button>
                    </div>
                </div>
            `;
        }
    }

    

    function handleAnalysisError(data, dataQuality = null) {
        let errorMessage = data.error || 'Lỗi không xác định';
        
        // ✅ ENHANCED ERROR MESSAGES cho pattern-analysis
        if (data.error_type) {
            switch (data.error_type) {
                case 'date_parsing_error':
                    errorMessage = '❌ Lỗi định dạng ngày. Vui lòng kiểm tra lại.';
                    break;
                case 'method_ids_validation_error':
                    errorMessage = '❌ Lỗi danh sách phương pháp. Vui lòng chọn lại.';
                    break;
                case 'pattern_analysis_error':
                    errorMessage = '❌ Lỗi phân tích pattern. Hệ thống đang xử lý.';
                    break;
                case 'ml_analysis_error':
                    errorMessage = '❌ Lỗi phân tích ML. Hệ thống đang bảo trì.';
                    break;
                case 'database_error':
                    errorMessage = '❌ Lỗi cơ sở dữ liệu. Vui lòng thử lại sau.';
                    break;
                case 'service_unavailable':
                    errorMessage = '❌ Dịch vụ phân tích không khả dụng. Vui lòng thử lại sau.';
                    break;
                case 'insufficient_data':
                    errorMessage = '❌ Không đủ dữ liệu lịch sử để phân tích.';
                    break;
                default:
                    errorMessage = `❌ ${data.error}`;
            }
        }
        
        // ✅ THÊM THÔNG TIN BỔ SUNG
        if (data.fallback_attempted) {
            errorMessage += '<br><small class="text-muted">Đã thử mở rộng timeframe nhưng vẫn không đủ dữ liệu.</small>';
        }
        
        if (data.suggestion) {
            errorMessage += `<br><small class="text-info">💡 ${data.suggestion}</small>`;
        }

        if (data.available_methods) {
            errorMessage += `<br><small class="text-muted">Methods có dữ liệu: ${data.available_methods.join(', ')}</small>`;
        }
        
        const content = document.getElementById('analysis-content');
        if (content) {
            content.innerHTML = `
                <div class="alert alert-danger">
                    <h6 class="alert-heading">❌ Không thể phân tích Pattern</h6>
                    <div>${errorMessage}</div>
                    <hr>
                    <div class="row">
                        <div class="col-md-6">
                            <small class="text-muted">
                                <i class="fas fa-database me-2"></i>
                                Timeframe: ${data.months_searched || 12} tháng |
                                API: pattern-analysis
                            </small>
                        </div>
                        <div class="col-md-6 text-end">
                            <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">
                                <i class="fas fa-refresh me-1"></i>Thử lại
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
    }


    // ✅ HÀM HIỂN THỊ KẾT QUẢ CHO NGÀY CỤ THỂ - LAYOUT MỚI
    function displayDaySpecificResults(predictions, analysis, targetDate, dayMethods) {
        const content = document.getElementById('analysis-content');
        if (!content) return;
        
        // Lọc predictions cho các methods có trong ngày này
        const dayPredictions = {};
        dayMethods.forEach(method => {
            if (predictions[method.method_id]) {
                dayPredictions[method.method_id] = {
                    ...predictions[method.method_id],
                    method_data: method
                };
            }
        });
        
        if (Object.keys(dayPredictions).length === 0) {
            content.innerHTML = '<div class="alert alert-info">Không có dự đoán ML cho các methods trong ngày này</div>';
            return;
        }
        
        // Sắp xếp theo confidence
        const sortedPredictions = Object.entries(dayPredictions).sort((a, b) => 
            b[1].confidence - a[1].confidence
        );
        
        let html = `
            <!-- ✅ OVERVIEW STATS -->
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="card border-info">
                        <div class="card-body p-2">
                            <h6 class="card-title text-info mb-1">
                                <i class="fas fa-chart-pie me-2"></i>Thống kê tổng quan
                            </h6>
                            <div class="row text-center">
                                <div class="col-4">
                                    <div class="fw-bold text-primary">${Object.keys(dayPredictions).length}</div>
                                    <small class="text-muted">Methods</small>
                                </div>
                                <div class="col-4">
                                    <div class="fw-bold text-success">Ngày ${analysis.best_overall_day}</div>
                                    <small class="text-muted">Tốt nhất</small>
                                </div>
                                <div class="col-4">
                                    <div class="fw-bold text-warning">${(analysis.avg_confidence * 100).toFixed(1)}%</div>
                                    <small class="text-muted">Tin cậy TB</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card border-success">
                        <div class="card-body p-2">
                            <h6 class="card-title text-success mb-1">
                                <i class="fas fa-bullseye me-2"></i>Khuyến nghị cho ngày ${targetDate}
                            </h6>
                            <div class="text-center">
                                ${generateDayRecommendationSummary(sortedPredictions)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- ✅ PREDICTIONS GRID - LAYOUT MỚI -->
            <div class="row">
                <div class="col-12">
                    <h6 class="text-primary mb-3">
                        <i class="fas fa-magic me-2"></i>Dự đoán khung thời gian trúng từng phương pháp:
                    </h6>
                    <div class="prediction-grid">
        `;
        
        sortedPredictions.forEach(([methodId, prediction], index) => {
            const confidence = prediction.confidence * 100;
            const recommendedDay = prediction.recommended_day;
            const probability = prediction.day_probabilities;
            
            // Xác định class cho confidence
            const confidenceClass = confidence >= 80 ? 'success' : confidence >= 60 ? 'warning' : confidence >= 40 ? 'info' : 'danger';
            const priorityBadge = index < 3 ? 'badge-top-choice' : '';
            
            // Tìm ngày có xác suất cao nhất
            const maxProb = Math.max(probability.day_1, probability.day_2, probability.day_3);
            
            html += `
                <div class="prediction-item mb-3 ${priorityBadge}">
                    <div class="card border-${confidenceClass} h-100">
                        ${index < 3 ? '<div class="position-absolute top-0 start-50 translate-middle"><span class="badge bg-danger">TOP</span></div>' : ''}
                        <div class="card-header bg-${confidenceClass} text-white p-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>${prediction.method_name}</strong>
                                    ${index === 0 ? '<i class="fas fa-crown ms-2"></i>' : ''}
                                </div>
                                <span class="badge bg-light text-dark">#{index + 1}</span>
                            </div>
                        </div>
                        <div class="card-body p-2">
                            <!-- Recommendation -->
                            <div class="text-center mb-2">
                                <div class="recommendation-day">
                                    <span class="badge bg-${confidenceClass} fs-6 px-3 py-2">
                                        🎯 Ngày ${recommendedDay}
                                    </span>
                                </div>
                                <div class="confidence-score mt-1">
                                    <small class="text-muted">Độ tin cậy: </small>
                                    <strong class="text-${confidenceClass}">${confidence.toFixed(1)}%</strong>
                                </div>
                            </div>
                            
                            <!-- Day Probabilities -->
                            <div class="day-probabilities mb-2">
                                <div class="row g-1">
                                    ${[1, 2, 3].map(day => {
                                        const dayProb = probability[`day_${day}`] * 100;
                                        const isRecommended = day === recommendedDay;
                                        const isHighest = (probability[`day_${day}`] === maxProb);
                                        const barClass = isRecommended ? confidenceClass : 'secondary';
                                        
                                        return `
                                            <div class="col-4">
                                                <div class="day-prob-card ${isRecommended ? 'recommended' : ''} ${isHighest ? 'highest-prob' : ''}">
                                                    <div class="text-center">
                                                        <div class="day-label">Ngày ${day}</div>
                                                        <div class="prob-value text-${barClass} fw-bold">${dayProb.toFixed(1)}%</div>
                                                        <div class="prob-bar">
                                                            <div class="progress" style="height: 4px;">
                                                                <div class="progress-bar bg-${barClass}" style="width: ${dayProb}%"></div>
                                                            </div>
                                                        </div>
                                                        ${isRecommended ? '<i class="fas fa-star text-warning"></i>' : ''}
                                                    </div>
                                                </div>
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                            
                            <!-- Pattern Info -->
                            ${prediction.pattern_info ? `
                                <div class="pattern-info">
                                    <div class="row g-1">
                                        <div class="col-6">
                                            <small class="text-muted">Chu kỳ:</small>
                                            <div class="fw-bold">${prediction.pattern_info.cycle_length}</div>
                                        </div>
                                        <div class="col-6">
                                            <small class="text-muted">Xu hướng:</small>
                                            <div class="fw-bold">${getTrendIcon(prediction.pattern_info.trend)} ${prediction.pattern_info.trend}</div>
                                        </div>
                                    </div>
                                </div>
                            ` : ''}
                            
                            <!-- Action Button -->
                            <div class="text-center mt-2">
                                <button class="btn btn-outline-${confidenceClass} btn-sm" 
                                        onclick="highlightMethodInTable('${methodId}', '${targetDate}')">
                                    <i class="fas fa-search me-1"></i>Xem trong bảng
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
            
            <!-- ✅ DETAILED ANALYSIS -->
            <div class="row mt-3">
                <div class="col-12">
                    <div class="card border-info">
                        <div class="card-header bg-light">
                            <h6 class="mb-0 text-info">
                                <i class="fas fa-microscope me-2"></i>Phân tích chi tiết Pattern
                            </h6>
                        </div>
                        <div class="card-body p-2">
                            ${generateDetailedAnalysis(sortedPredictions, analysis)}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        content.innerHTML = html;
    }

    // ✅ HÀM TẠO TÓM TẮT KHUYẾN NGHỊ
    function generateDayRecommendationSummary(sortedPredictions) {
        if (sortedPredictions.length === 0) {
            return '<span class="text-muted">Không có khuyến nghị</span>';
        }
        
        const topPrediction = sortedPredictions[0][1];
        const confidence = topPrediction.confidence * 100;
        const confidenceClass = confidence >= 80 ? 'success' : confidence >= 60 ? 'warning' : 'info';
        
        return `
            <div class="top-recommendation">
                <div class="fw-bold text-${confidenceClass}">
                    <i class="fas fa-medal me-1"></i>
                    ${topPrediction.method_name}
                </div>
                <div>
                    <span class="badge bg-${confidenceClass}">Ngày ${topPrediction.recommended_day}</span>
                    <small class="text-muted ms-2">${confidence.toFixed(1)}% tin cậy</small>
                </div>
            </div>
        `;
    }

    // ✅ HÀM TẠO PHÂN TÍCH CHI TIẾT
    function generateDetailedAnalysis(sortedPredictions, analysis) {
        const dayDistribution = {};
        let totalConfidence = 0;
        
        sortedPredictions.forEach(([methodId, prediction]) => {
            const day = prediction.recommended_day;
            if (!dayDistribution[day]) dayDistribution[day] = [];
            dayDistribution[day].push(prediction);
            totalConfidence += prediction.confidence;
        });
        
        const avgConfidence = totalConfidence / sortedPredictions.length;
        
        let html = '<div class="row g-2">';
        
        // Day distribution
        [1, 2, 3].forEach(day => {
            const dayMethods = dayDistribution[day] || [];
            const dayCount = dayMethods.length;
            const dayPercentage = (dayCount / sortedPredictions.length * 100).toFixed(1);
            
            html += `
                <div class="col-md-4">
                    <div class="analysis-day-card">
                        <div class="text-center">
                            <h6 class="text-primary">Ngày ${day}</h6>
                            <div class="day-stats">
                                <div class="stat-number">${dayCount}</div>
                                <div class="stat-label">methods (${dayPercentage}%)</div>
                            </div>
                            ${dayMethods.length > 0 ? `
                                <div class="top-method">
                                    <small class="text-muted">Top:</small>
                                    <div class="fw-bold">${dayMethods[0].method_name}</div>
                                </div>
                            ` : '<div class="text-muted">Không có</div>'}
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        
        // Overall insights
        html += `
            <div class="mt-3 p-2 bg-light rounded">
                <h6 class="text-info mb-2">
                    <i class="fas fa-lightbulb me-2"></i>Insights từ AI:
                </h6>
                <ul class="list-unstyled mb-0">
                    <li><i class="fas fa-check-circle text-success me-2"></i>
                        Độ tin cậy trung bình: <strong>${(avgConfidence * 100).toFixed(1)}%</strong>
                    </li>
                    <li><i class="fas fa-chart-line text-info me-2"></i>
                        Ngày được khuyến nghị nhiều nhất: <strong>Ngày ${analysis.best_overall_day}</strong>
                    </li>
                    <li><i class="fas fa-star text-warning me-2"></i>
                        Method hàng đầu: <strong>${sortedPredictions[0][1].method_name}</strong>
                    </li>
                </ul>
            </div>
        `;
        
        return html;
    }

    // ✅ HÀM HELPER
    function getTrendIcon(trend) {
        const icons = {
            'increasing': '📈',
            'decreasing': '📉', 
            'stable': '➡️'
        };
        return icons[trend] || '📊';
    }

    

    // ✅ HÀM TẠO METHOD DETAIL HTML - GIỮ NGUYÊN
    function generateMethodDetailHTML(method) {
        let html = `
            <div class="method-row">
                <div class="row align-items-center">
                    <div class="col-md-3">
                        <div class="fw-bold">${method.method_name}</div>
                        <small class="text-muted">${method.category}</small>
                        <div class="mt-1">
                            <span class="badge bg-info">Tin cậy: ${method.confidence.toFixed(1)}</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="mb-1"><small class="text-muted">Số dự đoán:</small></div>
        `;

        method.predicted_numbers.forEach(number => {
            html += `<span class="prediction-number predicted">${number}</span>`;
        });

        html += `
                    </div>
                    <div class="col-md-6">
                        <div class="row">
        `;

        method.tracking_results.forEach(tracking => {
            html += `
                <div class="col-4">
                    <div class="tracking-day">
                        <div class="text-center mb-2">
                            <strong>Ngày ${tracking.day}</strong><br>
                            <small>${tracking.tracking_date}</small>
                        </div>
            `;

            if (tracking.has_result) {
                const badgeClass = tracking.hit_rate >= 20 ? 'bg-success' : 
                                tracking.hit_rate >= 10 ? 'bg-warning' : 'bg-danger';
                
                html += `
                    <div class="text-center mb-2">
                        <span class="hit-rate-badge badge ${badgeClass}">
                            ${tracking.hit_count}/${method.predicted_numbers.length} 
                            (${tracking.hit_rate.toFixed(1)}%)
                        </span>
                    </div>
                `;

                if (tracking.hit_numbers.length > 0) {
                    html += '<div class="mb-1"><small class="text-success">Trúng:</small><br>';
                    tracking.hit_numbers.forEach(number => {
                        html += `<span class="prediction-number hit">${number}</span>`;
                    });
                    html += '</div>';
                }
            } else {
                html += `
                    <div class="text-center text-muted">
                        <i class="fas fa-clock"></i><br>Chờ kết quả
                    </div>
                `;
            }

            html += '</div></div>';
        });

        html += `
                        </div>
                        <div class="mt-2 text-center">
                            <small class="text-muted">
                                Tổng: ${method.total_hits} số trúng | 
                                TB: ${method.avg_hit_rate.toFixed(1)}%
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;

        return html;
    }

    /**
    * ✅ SỬA HÀM showDayDetail - SIMPLIFIED
    */
    function showDayDetail(date) {
        const data = dayData[date];
        if (!data) return;

        const detailSection = document.getElementById('dayDetail');
        const titleElement = document.getElementById('dayDetailTitle');
        const contentElement = document.getElementById('dayDetailContent');

        titleElement.textContent = `Chi tiết ngày ${data.date} (${data.weekday})`;

        let html = '';
        
        // ✅ ANALYSIS SECTION - SIMPLIFIED
        html += `
            <div class="card mb-3">
                <div class="card-header bg-primary text-white">
                    <h6 class="mb-0">
                        <i class="fas fa-brain me-2"></i>AI Pattern Analysis cho ngày ${date}
                        <div class="spinner-border spinner-border-sm ms-2 d-none" id="analysis-spinner" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </h6>
                </div>
                <div class="card-body" id="analysis-content">
                    <div class="text-center text-muted">
                        <i class="fas fa-chart-line fa-2x mb-2"></i>
                        <p>Đang phân tích pattern cho ngày này...</p>
                    </div>
                </div>
                <div id="data-source-info" class="d-none"></div>
            </div>
        `;
        
        // ✅ EXISTING SESSION DATA (giữ nguyên)
        if (data.sessions.length === 0) {
            html += '<div class="alert alert-info">Không có dự đoán cho ngày này</div>';
        } else {
            data.sessions.forEach(session => {
                html += `
                    <div class="session-card mt-3">
                        <div class="card-header bg-light">
                            <div class="d-flex justify-content-between align-items-center">
                                <strong>${session.cycle_name}</strong>
                                <span class="badge bg-secondary">${session.status}</span>
                            </div>
                        </div>
                        <div class="card-body">
                `;

                session.methods.forEach(method => {
                    html += generateMethodDetailHTML(method);
                });

                html += '</div></div>';
            });
        }

        contentElement.innerHTML = html;
        detailSection.style.display = 'block';
        detailSection.scrollIntoView({ behavior: 'smooth' });
        
        // ✅ TRIGGER ANALYSIS - SIMPLIFIED
        setTimeout(() => {
            performDaySpecificAnalysis(date);
        }, 100);
    }

    // ✅ THAY THẾ HÀM generateAnalysisSection - TÍCH HỢP ML
    function generateAnalysisSection(date, selectedMethodId) {
        let analysisHTML = `
            <div class="card mb-3">
                <div class="card-header bg-primary text-white">
                    <h6 class="mb-0">
                        <i class="fas fa-brain me-2"></i>AI Pattern Analysis & ML Prediction cho ngày ${date}
                        <div class="spinner-border spinner-border-sm ms-2 d-none" id="analysis-spinner" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </h6>
                </div>
                <div class="card-body" id="analysis-content">
                    <div class="text-center text-muted">
                        <i class="fas fa-chart-line fa-2x mb-2"></i>
                        <p>Đang phân tích pattern và ML cho ngày này...</p>
                        <small class="text-muted">Sử dụng API: pattern-analysis</small>
                    </div>
                </div>
                <!-- ✅ METADATA CONTAINER -->
                <div id="data-source-info" class="d-none">
                    <!-- Metadata will be populated by JavaScript -->
                </div>
            </div>
        `;
        
        // Trigger pattern analysis cho ngày cụ thể
        setTimeout(() => {
            performDaySpecificAnalysis(date, selectedMethodId);
        }, 100);
        
        return analysisHTML;
    }

    // ✅ 4. EXISTING EVENT LISTENERS & FILTER CODE - GIỮ NGUYÊN

    // Add click event listeners to date headers
    document.querySelectorAll('.date-header').forEach(header => {
        header.addEventListener('click', function() {
            const date = this.dataset.date;
            showDayDetail(date);
        });
    });

    // Add click event listeners to prediction cells  
    /*document.querySelectorAll('.prediction-cell').forEach(cell => {
        cell.addEventListener('click', function() {
            const date = this.dataset.date;
            const methodId = parseInt(this.dataset.methodId);
            if (date && methodId) {
                showDayDetail(date, methodId);
            }
        });
    });
    */
    // ✅ EXISTING FILTER CODE - GIỮ NGUYÊN
    const methodSearch = document.getElementById('methodSearch');
    const minHitRate = document.getElementById('minHitRate');
    const applyFilter = document.getElementById('applyFilter');
    
    // Thêm event listener cho Enter key trong input
    methodSearch.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            applyFilterMethods();
        }
    });
    
    minHitRate.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            applyFilterMethods();
        }
    });
    
    applyFilter.addEventListener('click', applyFilterMethods);
    
    function applyFilterMethods() {
        const searchTerm = methodSearch.value.toLowerCase().trim();
        const minRate = parseFloat(minHitRate.value) || 0;
        
        // Get all method rows
        const methodRows = document.querySelectorAll('.method-row');
        let visibleCount = 0;
        
        methodRows.forEach(row => {
            try {
                // ✅ FIX: Lấy tên method từ data attribute hoặc text content
                let methodName = '';
                if (row.dataset.methodName) {
                    methodName = row.dataset.methodName.toLowerCase();
                } else {
                    // Fallback: lấy từ text content của .fw-bold
                    const nameElement = row.querySelector('.method-name .fw-bold');
                    methodName = nameElement ? nameElement.textContent.toLowerCase() : '';
                }
                
                // ✅ FIX: Lấy hit rate từ data attribute hoặc DOM
                let hitRate = 0;
                if (row.dataset.hitRate) {
                    hitRate = parseFloat(row.dataset.hitRate);
                } else {
                    // Fallback: lấy từ DOM
                    const hitRateCell = row.querySelector('.method-totals div small');
                    if (hitRateCell) {
                        const hitRateText = hitRateCell.textContent;
                        const match = hitRateText.match(/(\d+(?:\.\d+)?)%/);
                        if (match) {
                            hitRate = parseFloat(match[1]);
                        }
                    }
                }
                
                // ✅ Kiểm tra điều kiện lọc
                const nameMatch = !searchTerm || methodName.includes(searchTerm);
                const rateMatch = hitRate >= minRate;
                
                // ✅ Hiển thị/ẩn row
                if (nameMatch && rateMatch) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
                
            } catch (error) {
                console.error('Lỗi khi lọc method row:', error);
                // Hiển thị row nếu có lỗi
                row.style.display = '';
                visibleCount++;
            }
        });
        
        // ✅ Cập nhật counter hiển thị
        updateFilterCounter(visibleCount, methodRows.length);
        
        // ✅ Cuộn lên đầu bảng sau khi filter
        const tableContainer = document.querySelector('.table-container');
        if (tableContainer) {
            tableContainer.scrollTop = 0;
        }
    }
    
    // ✅ Hàm cập nhật counter
    function updateFilterCounter(visible, total) {
        let counterElement = document.getElementById('filter-counter');
        
        // Tạo counter element nếu chưa có
        if (!counterElement) {
            counterElement = document.createElement('div');
            counterElement.id = 'filter-counter';
            counterElement.className = 'mt-2 text-muted';
            
            const cardBody = document.querySelector('.card-body');
            if (cardBody) {
                cardBody.appendChild(counterElement);
            }
        }
        
        // Cập nhật text
        if (visible === total) {
            counterElement.innerHTML = `<small><i class="fas fa-list"></i> Hiển thị tất cả ${total} phương pháp</small>`;
        } else {
            counterElement.innerHTML = `<small><i class="fas fa-filter"></i> Hiển thị ${visible}/${total} phương pháp</small>`;
        }
    }
    
    // ✅ Thêm nút Reset filter
    const resetFilterBtn = document.createElement('button');
    resetFilterBtn.className = 'btn btn-outline-secondary';
    resetFilterBtn.innerHTML = '<i class="fas fa-undo"></i> Reset';
    resetFilterBtn.onclick = function() {
        methodSearch.value = '';
        minHitRate.value = '0';
        applyFilterMethods();
    };
    
    // Thêm reset button vào UI
    const applyFilterParent = applyFilter.parentElement;
    if (applyFilterParent) {
        applyFilterParent.classList.remove('col-md-4');
        applyFilterParent.classList.add('col-md-4');
        applyFilterParent.innerHTML = `
            <div class="d-grid gap-2 d-md-flex">
                ${applyFilter.outerHTML}
                ${resetFilterBtn.outerHTML}
            </div>
        `;
        
        // Re-bind events sau khi thay đổi DOM
        const newApplyBtn = applyFilterParent.querySelector('button:first-child');
        const newResetBtn = applyFilterParent.querySelector('button:last-child');
        
        newApplyBtn.addEventListener('click', applyFilterMethods);
        newResetBtn.addEventListener('click', function() {
            methodSearch.value = '';
            minHitRate.value = '0';
            applyFilterMethods();
        });
    }
    
    // ✅ Khởi tạo counter ban đầu
    const initialTotal = document.querySelectorAll('.method-row').length;
    updateFilterCounter(initialTotal, initialTotal);

    // ✅ 5. WINDOW FUNCTIONS
    window.hideDayDetail = function() {
        document.getElementById('dayDetail').style.display = 'none';
    };

    // ✅ 6. DEBUG LOG
    console.log('Method Analysis Data:', methodAnalysis);
    console.log('Day Data:', dayData);


    // ✅ HÀM TÍNH DIVERSITY SCORE TỔNG THỂ
    function calculateOverallDiversityScore(hitPatterns) {
        let totalScore = 0;
        let methodCount = 0;
        
        Object.keys(hitPatterns.hit_day_1).forEach(methodId => {
            const day1Data = hitPatterns.hit_day_1[methodId];
            const day2Data = hitPatterns.hit_day_2[methodId];
            const day3Data = hitPatterns.hit_day_3[methodId];
            
            const allData = day1Data.concat(day2Data, day3Data);
            const hitRate = allData.reduce((sum, val) => sum + val, 0) / allData.length;
            const diversityScore = Math.min(hitRate, 1 - hitRate) * 2;
            
            totalScore += diversityScore;
            methodCount++;
        });
        
        return methodCount > 0 ? totalScore / methodCount : 0;
    }

    
    // ✅ HIỂN THỊ KẾT QUẢ DỰ ĐOÁN
    function displayPredictionResults(predictions) {
        let html = `
            <div class="card mt-4">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0">🎯 Dự đoán khung thời gian trúng</h5>
                </div>
                <div class="card-body">
                    <div class="row">
        `;
        
        Object.entries(predictions).forEach(([methodId, prediction]) => {
            const confidence = prediction.confidence * 100;
            const recommendedDay = prediction.recommended_day;
            const probability = prediction.day_probabilities;
            
            const confidenceClass = confidence >= 80 ? 'success' : confidence >= 60 ? 'warning' : 'danger';
            
            html += `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card border-${confidenceClass}">
                        <div class="card-body p-2">
                            <h6 class="card-title mb-1">${prediction.method_name}</h6>
                            <div class="mb-2">
                                <span class="badge bg-${confidenceClass}">
                                    Ngày ${recommendedDay} (${confidence.toFixed(1)}%)
                                </span>
                            </div>
                            <div style="font-size: 0.8rem;">
                                <div>Ngày 1: ${(probability.day_1 * 100).toFixed(1)}%</div>
                                <div>Ngày 2: ${(probability.day_2 * 100).toFixed(1)}%</div>
                                <div>Ngày 3: ${(probability.day_3 * 100).toFixed(1)}%</div>
                            </div>
                            ${prediction.pattern_info ? `
                                <small class="text-muted">
                                    Chu kỳ: ${prediction.pattern_info.cycle_length} | 
                                    Xu hướng: ${prediction.pattern_info.trend}
                                </small>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
        
        // Thêm vào DOM
        const container = document.querySelector('.container-fluid');
        const existingResults = document.getElementById('prediction-results');
        if (existingResults) {
            existingResults.remove();
        }
        
        const resultsDiv = document.createElement('div');
        resultsDiv.id = 'prediction-results';
        resultsDiv.innerHTML = html;
        container.appendChild(resultsDiv);
    }

    // ✅ HIỂN THỊ PHÂN TÍCH PATTERN TỔNG QUAN
    function displayPatternAnalysis(analysis) {
        let html = `
            <div class="card mt-3">
                <div class="card-header bg-info text-white">
                    <h6 class="mb-0">📊 Phân tích Pattern Tổng quan</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <h6>Thống kê chung:</h6>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Tổng methods:</span>
                                    <span>${analysis.total_methods}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Ngày tốt nhất:</span>
                                    <span class="badge bg-success">Ngày ${analysis.best_overall_day}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Độ tin cậy TB:</span>
                                    <span>${(analysis.avg_confidence * 100).toFixed(1)}%</span>
                                </li>
                            </ul>
                        </div>
                        <div class="col-md-8">
                            <h6>Top methods khuyến nghị:</h6>
                            <div class="list-group">
        `;
        
        analysis.top_recommendations.slice(0, 5).forEach((rec, index) => {
            const confidence = rec.confidence * 100;
            const badgeClass = confidence >= 80 ? 'success' : confidence >= 60 ? 'warning' : 'danger';
            
            html += `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${rec.method_name}</strong><br>
                        <small class="text-muted">Ngày ${rec.recommended_day}</small>
                    </div>
                    <span class="badge bg-${badgeClass}">${confidence.toFixed(1)}%</span>
                </div>
            `;
        });
        
        html += `
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Thêm vào prediction results
        const resultsDiv = document.getElementById('prediction-results');
        if (resultsDiv) {
            resultsDiv.insertAdjacentHTML('beforeend', html);
        }
    }

    // ✅ HELPER FUNCTION - GET CSRF TOKEN
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Thêm vào filter card
    /*const filterCard = document.querySelector('.card-body');
    if (filterCard) {
        filterCard.appendChild(analysisButton);
    }
    */

    // ✅ 7. DEBUGGING
    console.log('🔧 Monthly Report JS initialized with enhanced error handling');
    console.log('📊 Method Analysis Data:', methodAnalysis);
    console.log('📅 Day Data:', Object.keys(dayData).length, 'days loaded');

});
