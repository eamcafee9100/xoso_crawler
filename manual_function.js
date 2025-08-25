// Force define the function in global scope
console.log("=== Defining Function Manually ===");

// Define the function manually
window.showNumberAnalysis = function(number) {
    console.log("🚀 showNumberAnalysis called with number:", number);
    
    const modal = document.getElementById('numberAnalysisModal');
    const modalNumber = document.getElementById('modal-number');
    const modalContent = document.getElementById('modal-analysis-content');
    
    if (!modal) {
        console.error("❌ Modal not found!");
        return;
    }
    
    if (!modalNumber) {
        console.error("❌ Modal number element not found!");
        return;
    }
    
    if (!modalContent) {
        console.error("❌ Modal content element not found!");
        return;
    }
    
    console.log("✅ All modal elements found");
    
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
    
    console.log("✅ Modal should be visible now");
    
    // Fetch analysis data
    console.log("🌐 Fetching data from API...");
    fetch(`/results/number-analysis/?number=${number}`)
        .then(response => {
            console.log("📡 API Response status:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("📊 API Data received:", data);
            if (data.success) {
                modalContent.innerHTML = `
                    <div class="alert alert-success">
                        <h5>Phân tích cho số ${number}</h5>
                        <p>Dữ liệu đã được tải thành công!</p>
                        <pre>${JSON.stringify(data.analysis, null, 2)}</pre>
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
            console.error('❌ API Error:', error);
            modalContent.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    Lỗi kết nối: Không thể tải dữ liệu phân tích
                </div>
            `;
        });
};

console.log("✅ Function defined. Testing...");
console.log("Function exists:", typeof window.showNumberAnalysis === 'function');

// Test the function
console.log("🧪 Testing function with number 00...");
window.showNumberAnalysis('00');
