// Frequency Analysis JavaScript Functions
// This file handles number analysis and heatmap generation

// Global functions for number analysis
window.showNumberAnalysis = function(number) {
    console.log("showNumberAnalysis called with:", number);
    
    const modal = document.getElementById('numberAnalysisModal');
    const modalNumber = document.getElementById('modal-number');
    const modalContent = document.getElementById('modal-analysis-content');
    
    if (!modal || !modalNumber || !modalContent) {
        console.error("Modal elements not found");
        return;
    }
    
    modalNumber.textContent = number;
    modalContent.innerHTML = `
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Đang tải...</span>
            </div>
            <p class="mt-2">Đang phân tích số ${number}...</p>
        </div>
    `;
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Fetch analysis data
    fetch(`/results/number-analysis/?number=${number}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                modalContent.innerHTML = `
                    <div class="alert alert-success">
                        <h5>✅ Phân tích chi tiết cho số ${number}</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <h6>📊 Thống kê cơ bản:</h6>
                                <ul>
                                    <li>Xuất hiện 30 ngày: <strong>${data.analysis.basic_stats.appearances_30d} lần</strong></li>
                                    <li>Tổng xuất hiện: <strong>${data.analysis.basic_stats.total_appearances} lần</strong></li>
                                    <li>Lần cuối: <strong>${data.analysis.basic_stats.last_appearance}</strong></li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>⚡ Phân tích "Gan":</h6>
                                <ul>
                                    <li>Gan hiện tại: <strong class="text-danger">${data.analysis.gan_analysis.current_gan_days} ngày</strong></li>
                                    <li>Gan tối đa: <strong>${data.analysis.gan_analysis.max_gan_days} ngày</strong></li>
                                    <li>Gan trung bình: <strong>${data.analysis.gan_analysis.avg_gan_days} ngày</strong></li>
                                </ul>
                            </div>
                        </div>
                        <div class="mt-3">
                            <h6>🎯 Xác suất dự đoán:</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar bg-success" style="width: ${data.analysis.prediction_probabilities.combined}%">
                                    ${data.analysis.prediction_probabilities.combined.toFixed(2)}%
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                modalContent.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i>
                        Lỗi: ${data.error || 'Không thể tải dữ liệu phân tích'}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            modalContent.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    Lỗi kết nối: Không thể tải dữ liệu phân tích
                </div>
            `;
        });
};

window.generateHeatmap = function() {
    console.log("generateHeatmap called");
    
    const container = document.getElementById('heatmap-container');
    if (!container) {
        console.error("Heatmap container not found");
        return;
    }
    
    container.innerHTML = `
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Đang tải...</span>
            </div>
            <p class="mt-2">Đang tạo heatmap...</p>
        </div>
    `;
    
    fetch('/results/frequency-heatmap/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                container.innerHTML = `
                    <div class="alert alert-success">
                        <h5>🔥 Heatmap đã được tạo thành công!</h5>
                        <p>Dữ liệu heatmap đã được tải.</p>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i>
                        Lỗi: ${data.error || 'Không thể tạo heatmap'}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    Lỗi kết nối: Không thể tạo heatmap
                </div>
            `;
        });
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("Frequency analysis JS loaded");
    
    // Bind number analysis buttons
    const buttons = document.querySelectorAll('.number-analysis-btn');
    console.log(`Binding ${buttons.length} analysis buttons`);
    
    buttons.forEach((btn, index) => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const number = this.dataset.number;
            console.log(`Button ${index} clicked: ${number}`);
            window.showNumberAnalysis(number);
        });
    });
    
    // Bind heatmap button
    const heatmapBtn = document.getElementById('generate-heatmap');
    if (heatmapBtn) {
        heatmapBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Heatmap button clicked');
            window.generateHeatmap();
        });
        console.log("Heatmap button bound");
    }
});
