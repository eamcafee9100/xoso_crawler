// Enhanced modal content with full analysis data
function createFullAnalysisModal(data, number) {
    const analysis = data.analysis;
    
    // Helper function to create companion numbers section
    function createCompanionSection() {
        if (!analysis.companion_numbers || analysis.companion_numbers.length === 0) {
            return '<p class="text-muted">Chưa có dữ liệu số cùng xuất hiện</p>';
        }
        
        let html = '<div class="table-responsive"><table class="table table-sm table-striped">';
        html += '<thead><tr><th>Số</th><th>Xuất hiện cùng</th><th>Tỷ lệ</th></tr></thead><tbody>';
        
        analysis.companion_numbers.slice(0, 10).forEach(comp => {
            html += '<tr>';
            html += '<td><span class="badge bg-primary">' + comp.number + '</span></td>';
            html += '<td>' + comp.co_occurrences + ' lần</td>';
            html += '<td>' + comp.percentage.toFixed(1) + '%</td>';
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
        return html;
    }
    
    // Helper function to create predecessor section
    function createPredecessorSection() {
        if (!analysis.predecessor_analysis || analysis.predecessor_analysis.length === 0) {
            return '<p class="text-muted">Chưa có dữ liệu số tiền nhiệm</p>';
        }
        
        let html = '<div class="table-responsive"><table class="table table-sm table-striped">';
        html += '<thead><tr><th>Số</th><th>Xuất hiện trước</th><th>Tỷ lệ</th></tr></thead><tbody>';
        
        analysis.predecessor_analysis.slice(0, 10).forEach(pred => {
            html += '<tr>';
            html += '<td><span class="badge bg-warning">' + pred.number + '</span></td>';
            html += '<td>' + pred.occurrences + ' lần</td>';
            html += '<td>' + pred.percentage.toFixed(1) + '%</td>';
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
        return html;
    }
    
    // Helper function to create weekday patterns
    function createWeekdaySection() {
        if (!analysis.weekday_patterns || Object.keys(analysis.weekday_patterns).length === 0) {
            return '<p class="text-muted">Chưa có dữ liệu theo ngày trong tuần</p>';
        }
        
        let html = '<div class="row">';
        
        Object.entries(analysis.weekday_patterns).forEach(([day, stats]) => {
            const percentage = stats.percentage || 0;
            html += '<div class="col-6 col-md-4 mb-2">';
            html += '<div class="text-center">';
            html += '<div class="fw-bold">' + day.substring(0, 3) + '</div>';
            html += '<div class="small">' + stats.count + ' lần</div>';
            html += '<div class="progress" style="height: 4px;">';
            html += '<div class="progress-bar" style="width: ' + percentage + '%"></div>';
            html += '</div>';
            html += '<div class="small text-muted">' + percentage.toFixed(1) + '%</div>';
            html += '</div>';
            html += '</div>';
        });
        
        html += '</div>';
        return html;
    }
    
    // Helper function to create cycle analysis
    function createCycleSection() {
        if (!analysis.cycle_analysis) {
            return '<p class="text-muted">Chưa có dữ liệu chu kỳ</p>';
        }
        
        const cycle = analysis.cycle_analysis;
        let html = '<div class="row">';
        html += '<div class="col-6"><strong>Trung bình:</strong> ' + (cycle.avg_cycle || 0).toFixed(1) + ' ngày</div>';
        html += '<div class="col-6"><strong>Trung vị:</strong> ' + (cycle.median_cycle || 0) + ' ngày</div>';
        html += '<div class="col-6"><strong>Tối thiểu:</strong> ' + (cycle.min_cycle || 0) + ' ngày</div>';
        html += '<div class="col-6"><strong>Tối đa:</strong> ' + (cycle.max_cycle || 0) + ' ngày</div>';
        html += '</div>';
        
        if (cycle.cycle_distribution && Object.keys(cycle.cycle_distribution).length > 0) {
            html += '<div class="mt-2"><small class="text-muted">Phân bố chu kỳ:</small><br>';
            Object.entries(cycle.cycle_distribution).slice(0, 5).forEach(([days, count]) => {
                html += '<span class="badge bg-light text-dark me-1">' + days + ' ngày: ' + count + ' lần</span>';
            });
            html += '</div>';
        }
        
        return html;
    }
    
    // Main modal content
    return '<div class="container-fluid">' +
        '<div class="row mb-3">' +
            '<div class="col-12">' +
                '<h5 class="text-center mb-3">📊 Phân tích toàn diện cho số <span class="badge bg-primary fs-6">' + number + '</span></h5>' +
            '</div>' +
        '</div>' +
        
        // Basic stats and prediction
        '<div class="row mb-4">' +
            '<div class="col-md-6">' +
                '<div class="card">' +
                    '<div class="card-header bg-info text-white py-2">' +
                        '<h6 class="mb-0">📈 Thống kê cơ bản</h6>' +
                    '</div>' +
                    '<div class="card-body">' +
                        '<ul class="list-unstyled mb-0">' +
                            '<li>📅 Xuất hiện 30 ngày: <strong>' + analysis.basic_stats.appearances_30d + ' lần</strong></li>' +
                            '<li>📊 Tổng xuất hiện: <strong>' + analysis.basic_stats.total_appearances + ' lần</strong></li>' +
                            '<li>🕒 Lần cuối: <strong>' + (analysis.basic_stats.last_appearance || 'Chưa có') + '</strong></li>' +
                        '</ul>' +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<div class="col-md-6">' +
                '<div class="card">' +
                    '<div class="card-header bg-warning text-dark py-2">' +
                        '<h6 class="mb-0">⚡ Phân tích "Gan"</h6>' +
                    '</div>' +
                    '<div class="card-body">' +
                        '<ul class="list-unstyled mb-0">' +
                            '<li>🔥 Gan hiện tại: <strong class="text-danger">' + analysis.gan_analysis.current_gan_days + ' ngày</strong></li>' +
                            '<li>📏 Gan tối đa: <strong>' + analysis.gan_analysis.max_gan_days + ' ngày</strong></li>' +
                            '<li>📊 Gan trung bình: <strong>' + (analysis.gan_analysis.avg_gan_days || 0).toFixed(1) + ' ngày</strong></li>' +
                        '</ul>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
        
        // Prediction probability
        '<div class="row mb-4">' +
            '<div class="col-12">' +
                '<div class="card">' +
                    '<div class="card-header bg-success text-white py-2">' +
                        '<h6 class="mb-0">🎯 Xác suất dự đoán</h6>' +
                    '</div>' +
                    '<div class="card-body">' +
                        '<div class="progress mb-2" style="height: 25px;">' +
                            '<div class="progress-bar bg-success" style="width: ' + analysis.prediction_probabilities.combined + '%">' +
                                '<span class="fw-bold">' + analysis.prediction_probabilities.combined.toFixed(1) + '%</span>' +
                            '</div>' +
                        '</div>' +
                        '<small class="text-muted">Dựa trên chu kỳ và gan tối đa</small>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
        
        // Companion numbers and predecessors
        '<div class="row mb-4">' +
            '<div class="col-md-6">' +
                '<div class="card">' +
                    '<div class="card-header bg-primary text-white py-2">' +
                        '<h6 class="mb-0">🤝 Số cùng xuất hiện</h6>' +
                    '</div>' +
                    '<div class="card-body">' +
                        createCompanionSection() +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<div class="col-md-6">' +
                '<div class="card">' +
                    '<div class="card-header bg-secondary text-white py-2">' +
                        '<h6 class="mb-0">⏮️ Số thường xuất hiện trước</h6>' +
                    '</div>' +
                    '<div class="card-body">' +
                        createPredecessorSection() +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
        
        // Weekday patterns and cycle analysis
        '<div class="row mb-4">' +
            '<div class="col-md-6">' +
                '<div class="card">' +
                    '<div class="card-header bg-info text-white py-2">' +
                        '<h6 class="mb-0">📅 Theo ngày trong tuần</h6>' +
                    '</div>' +
                    '<div class="card-body">' +
                        createWeekdaySection() +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<div class="col-md-6">' +
                '<div class="card">' +
                    '<div class="card-header bg-dark text-white py-2">' +
                        '<h6 class="mb-0">🔄 Chu kỳ xuất hiện</h6>' +
                    '</div>' +
                    '<div class="card-body">' +
                        createCycleSection() +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
    '</div>';
}

// Copy this function to console to test enhanced modal
