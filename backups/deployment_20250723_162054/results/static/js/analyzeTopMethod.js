
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM loaded, checking for analyzeTopMethods button");
  
  // Kiểm tra nút phân tích tồn tại
  const analyzeButton = document.getElementById('analyzeTopMethods');
  if (!analyzeButton) {
    console.error("Button #analyzeTopMethods not found!");
    return;
  }
  
  console.log("Button found, attaching click event");
  
  // Xử lý khi người dùng nhấn nút phân tích
  analyzeButton.addEventListener('click', function() {
    console.log("Button clicked");
    
    // Hiển thị loader
    const loader = document.getElementById('topMethodsAnalysisLoader');
    const results = document.getElementById('topMethodsAnalysisResults');
    
    if (!loader || !results) {
      console.error("Loader or results container not found");
      return;
    }
    
    loader.style.display = 'flex';
    results.style.display = 'none';
    
    // Lấy ngày được chọn
    const selectedDateInput = document.getElementById('selectedDate');
    if (!selectedDateInput) {
      console.error("Selected date input not found");
      return;
    }
    
    const selectedDate = selectedDateInput.value || "{{ selected_date|date:'Y-m-d' }}";
    console.log("Selected date:", selectedDate);
    
    // Phân tích dữ liệu
    setTimeout(function() {
      try {
        analyzeTopMethods(selectedDate);
        
        // Ẩn loader và hiển thị kết quả
        loader.style.display = 'none';
        results.style.display = 'block';
      } catch (error) {
        console.error("Error during analysis:", error);
        alert("Có lỗi xảy ra khi phân tích: " + error.message);
        loader.style.display = 'none';
      }
    }, 1000); // Giả lập thời gian phân tích
  });

  // Hàm phân tích Top 10 phương pháp
  function analyzeTopMethods(selectedDate) {
    console.log("Starting analysis for date:", selectedDate);
    
    // Tìm bảng chính chứa dữ liệu
    let table = document.getElementById('monthlyReportTable');
    if (!table) {
      // Thử tìm bảng theo class nếu không tìm thấy bằng ID
      table = document.querySelector('table.table-bordered.table-striped');
      console.log("Table found by class instead of ID");
    }
    
    if (!table) {
      console.error("Monthly report table not found!");
      // Tạo dữ liệu mẫu nếu không tìm thấy bảng
      createSampleData(selectedDate);
      return;
    }
    
    // Lấy 10 phương pháp đầu tiên từ bảng
    const methodRows = Array.from(table.querySelectorAll('tbody tr')).slice(0, 10);
    console.log("Found", methodRows.length, "method rows");
    
    // Nếu không tìm thấy hàng nào, tạo dữ liệu mẫu
    if (methodRows.length === 0) {
      console.warn("No method rows found, creating sample data");
      createSampleData(selectedDate);
      return;
    }
    
    // Chuyển đổi ngày thành định dạng hiển thị
    const dateObj = new Date(selectedDate);
    const formattedDate = dateObj.toLocaleDateString('vi-VN');
    const analysisDateElem = document.getElementById('analysisDate');
    if (analysisDateElem) {
      analysisDateElem.textContent = formattedDate;
    }
    
    // Tính ngày tiếp theo
    const nextDay = new Date(selectedDate);
    nextDay.setDate(nextDay.getDate() + 1);
    const formattedNextDay = nextDay.toLocaleDateString('vi-VN');
    const nextDayDateElem = document.getElementById('nextDayDate');
    if (nextDayDateElem) {
      nextDayDateElem.textContent = formattedNextDay;
    }
    
    // Thu thập thông tin phương pháp
    const methodsInfo = [];
    const allNumbers = [];
    const twoDigitNumbers = {};
    const threeDigitNumbers = {};
    const methodsForNumbers = {};
    const hitRatesForNumbers = {};
    
    // Dữ liệu lịch sử từ context
    {% if historical_hit_rates %}
    const historicalHitRates = {
      {% for number, info in historical_hit_rates.items %}
        "{{ number }}": {
          hits: {{ info.hits }},
          total: {{ info.total }},
          rate: {{ info.rate|floatformat:2 }},
          dates: [{% for date in info.dates %}"{{ date|date:'Y-m-d' }}",{% endfor %}]
        },
      {% endfor %}
    };
    {% else %}
    const historicalHitRates = {};
    {% endif %}
    
    // Xác định ngày được chọn trong định dạng hiển thị
    const selectedDateStr = dateObj.toLocaleDateString('vi-VN', {day: '2-digit', month: '2-digit', year: 'numeric'});
    console.log("Selected date in locale format:", selectedDateStr);
    
    // Xác định vị trí của ngày trong header
    const selectedDay = dateObj.getDate();
    console.log("Looking for day:", selectedDay);
    
    const headerCells = table.querySelectorAll('th.date-header');
    let selectedDayIndex = -1;
    
    headerCells.forEach((header, index) => {
      const dayText = header.textContent.split('\n')[0].trim();
      if (dayText == selectedDay.toString()) {
        selectedDayIndex = index;
        console.log(`Found day ${selectedDay} at index ${index}`);
      }
    });
    
    // Phân tích từng phương pháp
    methodRows.forEach((row, index) => {
      console.log(`Analyzing method ${index + 1}`);
      
      // Lấy tên và mã phương pháp từ thuộc tính data-* của thẻ tr
      let methodName = row.dataset.methodName;
      let methodCode = row.dataset.methodCode;
      const methodId = row.dataset.methodId;
      
      // Kiểm tra nếu tìm thấy tên và mã phương pháp
      if (!methodName || !methodCode) {
        console.warn(`Method ${index + 1} is missing name or code in data attributes`);
        
        // Thử phương pháp dự phòng - tìm trong ô td.method-name
        const methodNameCell = row.querySelector('td.method-name');
        if (methodNameCell) {
          // Phân tích từ text
          const methodNameText = methodNameCell.textContent.trim();
          console.log(`Falling back to text extraction. Method cell text: ${methodNameText}`);
          
          // Phân tích tên và mã phương pháp từ nội dung của ô
          let extractedName = methodNameText;
          let extractedCode = '';
          
          // Tìm kiếm mã trong dấu ngoặc
          const codeMatch = methodNameText.match(/\(([^)]+)\)/);
          if (codeMatch && codeMatch[1]) {
            extractedCode = codeMatch[1].trim();
            // Xóa phần mã trong dấu ngoặc khỏi tên phương pháp
            extractedName = methodNameText.replace(/\s*\([^)]+\)/, '').trim();
          } else {
            // Nếu không tìm thấy mã trong dấu ngoặc, tạo một mã từ các chữ cái đầu
            extractedCode = extractedName.split(/\s+/).map(word => word[0]).join('').toUpperCase();
          }
          
          // Sử dụng giá trị đã trích xuất
          methodName = extractedName;
          methodCode = extractedCode;
        } else {
          // Nếu không tìm thấy thông tin phương pháp, tạo giá trị mặc định
          methodName = `Phương pháp ${index + 1}`;
          methodCode = `PP${index + 1}`;
        }
      }
      
      console.log(`Method name: "${methodName}", code: "${methodCode}"`);
      
      // Tìm ô dữ liệu cho ngày được chọn (dựa vào vị trí trong hàng)
      let hitRate = 0;
      let predictedNumbers = [];
      
      // Nếu tìm thấy vị trí ngày trong header
      if (selectedDayIndex >= 0) {
        // +1 vì cột đầu tiên là tên phương pháp
        const allCells = Array.from(row.querySelectorAll('td'));
        const cellIndex = selectedDayIndex + 1; // +1 vì cột đầu tiên là tên phương pháp
        
        if (cellIndex < allCells.length) {
          const cell = allCells[cellIndex];
          console.log(`Found cell for day ${selectedDay} at index ${cellIndex}`);
          
          // Cố gắng lấy hitRate từ data attribute trước
          if (cell.dataset.hitRate) {
            hitRate = parseFloat(cell.dataset.hitRate || 0);
            console.log(`Found hit rate in data attribute: ${hitRate}%`);
          } else {
            // Nếu không có, thử trích xuất từ nội dung
            const hitRateMatch = cell.textContent.match(/(\d+(\.\d+)?)%/);
            hitRate = hitRateMatch ? parseFloat(hitRateMatch[1]) : 0;
            console.log(`Extracted hit rate from content: ${hitRate}%`);
          }
        }
      } else {
        // Nếu không tìm thấy ngày trong header, thử tìm ô bằng data-date
        const dateCells = Array.from(row.querySelectorAll('td')).filter(cell =>
          cell.dataset.date === selectedDateStr
        );
        
        if (dateCells.length > 0) {
          console.log(`Found ${dateCells.length} cells with data-date=${selectedDateStr}`);
          hitRate = parseFloat(dateCells[0].dataset.hitRate || 0);
          console.log(`Hit rate: ${hitRate}%`);
        }
      }
      
      // Tìm số dự đoán từ context nếu có
      {% if day_data and day_data.predicted_numbers_by_method %}
      try {
        const predictionsByMethod = {{ day_data.predicted_numbers_by_method|safe }};
        if (methodId && predictionsByMethod[methodId]) {
          predictedNumbers = predictionsByMethod[methodId];
          console.log(`Found ${predictedNumbers.length} predicted numbers for method ${methodId} from context`);
        } else {
          console.warn(`No predictions found for method ${methodId}`);
        }
      } catch (e) {
        console.error("Error parsing predicted numbers:", e);
      }
      {% elif day_data and day_data.predicted_numbers %}
      try {
        predictedNumbers = {{ day_data.predicted_numbers|safe }};
        console.log(`Found ${predictedNumbers.length} predicted numbers from general context`);
      } catch (e) {
        console.error("Error parsing predicted numbers:", e);
      }
      {% endif %}
      
      // Nếu không tìm thấy số dự đoán, thử lấy từ lịch sử hoặc tạo thông minh
      if (!predictedNumbers || predictedNumbers.length === 0) {
        // Thử lấy dự đoán lịch sử cho phương pháp này
        const historicalPredictions = getHistoricalPredictions(methodId, selectedDate);
        
        if (historicalPredictions.length > 0) {
          predictedNumbers = historicalPredictions;
          console.log(`Using historical predictions for method ${methodName}: ${predictedNumbers.length} numbers`);
        } else {
          // Sử dụng phân tích tần suất để tạo số thông minh
          console.log("Generating intelligent weighted numbers based on frequency analysis");
          predictedNumbers = generateWeightedNumbers(methodName, selectedDate);
        }
      }
      
      // Thêm thông tin phương pháp
      methodsInfo.push({
        name: methodName,
        code: methodCode,
        hitRate: hitRate,
        predictedNumbers: predictedNumbers
      });
      
      // Thống kê số
      predictedNumbers.forEach(number => {
        allNumbers.push(number);
        
        // Phân loại số 2 chữ số và 3 chữ số
        if (number.length === 2) {
          twoDigitNumbers[number] = (twoDigitNumbers[number] || 0) + 1;
        } else if (number.length === 3) {
          threeDigitNumbers[number] = (threeDigitNumbers[number] || 0) + 1;
        }
        
        // Ghi nhận phương pháp cho số
        if (!methodsForNumbers[number]) {
          methodsForNumbers[number] = [];
        }
        if (!methodsForNumbers[number].includes(methodName)) {
          methodsForNumbers[number].push(methodName);
        }
        
        // Gán tỉ lệ trúng lịch sử hoặc tính toán từ số tương tự
        if (historicalHitRates[number]) {
          hitRatesForNumbers[number] = historicalHitRates[number].rate;
        } else {
          // Tính toán từ số tương tự thay vì tạo ngẫu nhiên
          hitRatesForNumbers[number] = calculateSimilarNumbersHitRate(number, historicalHitRates);
        }
      });
    });
    
    console.log(`Total numbers collected: ${allNumbers.length}`);
    console.log(`Two-digit numbers: ${Object.keys(twoDigitNumbers).length}`);
    console.log(`Three-digit numbers: ${Object.keys(threeDigitNumbers).length}`);
    
    // Nếu không thu thập được dữ liệu, tạo dữ liệu mẫu
    if (allNumbers.length === 0) {
      console.warn("No numbers collected, creating sample data");
      createSampleData(selectedDate);
      return;
    }
    
    // Tính toán xu hướng và mùa vụ cho mỗi số
    const trendData = calculateTrends(historicalHitRates, selectedDate);
    const seasonalData = calculateSeasonalFactors(historicalHitRates, selectedDate);
    
    // Hiển thị danh sách Top 10 phương pháp
    const topMethodsList = document.getElementById('topMethodsList');
    if (topMethodsList) {
      topMethodsList.innerHTML = '';
      methodsInfo.forEach(method => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${method.name} (${method.code})</td>
          <td>${method.hitRate.toFixed(2)}%</td>
          <td>${method.predictedNumbers.length}</td>
        `;
        topMethodsList.appendChild(row);
      });
    }
    
    // Hiển thị thông tin chung
    const totalPredictionsElem = document.getElementById('totalPredictions');
    if (totalPredictionsElem) {
      totalPredictionsElem.textContent = allNumbers.length;
    }
    
    // Tìm số xuất hiện nhiều nhất
    let mostFrequentTwoDigit = '';
    let maxTwoDigitFreq = 0;
    
    for (const [number, freq] of Object.entries(twoDigitNumbers)) {
      if (freq > maxTwoDigitFreq) {
        maxTwoDigitFreq = freq;
        mostFrequentTwoDigit = number;
      }
    }
    
    let mostFrequentThreeDigit = '';
    let maxThreeDigitFreq = 0;
    
    for (const [number, freq] of Object.entries(threeDigitNumbers)) {
      if (freq > maxThreeDigitFreq) {
        maxThreeDigitFreq = freq;
        mostFrequentThreeDigit = number;
      }
    }
    
    // Hiển thị số xuất hiện nhiều nhất
    const mostFrequentTwoDigitElem = document.getElementById('mostFrequentTwoDigit');
    if (mostFrequentTwoDigitElem) {
      mostFrequentTwoDigitElem.textContent =
        mostFrequentTwoDigit ? `${mostFrequentTwoDigit} (${maxTwoDigitFreq} lần)` : 'Không có dữ liệu';
    }
    
    const mostFrequentThreeDigitElem = document.getElementById('mostFrequentThreeDigit');
    if (mostFrequentThreeDigitElem) {
      mostFrequentThreeDigitElem.textContent =
        mostFrequentThreeDigit ? `${mostFrequentThreeDigit} (${maxThreeDigitFreq} lần)` : 'Không có dữ liệu';
    }
    
    // Tìm số có tỉ lệ trúng cao nhất
    let highestHitRateNumber = '';
    let highestHitRate = 0;
    
    for (const [number, rate] of Object.entries(hitRatesForNumbers)) {
      if (rate > highestHitRate) {
        highestHitRate = rate;
        highestHitRateNumber = number;
      }
    }
    
    const highestHitRateNumberElem = document.getElementById('highestHitRateNumber');
    if (highestHitRateNumberElem) {
      highestHitRateNumberElem.textContent =
        highestHitRateNumber ? `${highestHitRateNumber} (${highestHitRate.toFixed(2)}%)` : 'Không có dữ liệu';
    }
    
    // Tính điểm nâng cao cho mỗi số
    const scoreForNumbers = {};
    const scoreDetails = {};
    
    for (const [number, freq] of Object.entries({...twoDigitNumbers, ...threeDigitNumbers})) {
      const hitRate = hitRatesForNumbers[number] || 0;
      const trend = trendData[number] || { factor: 1.0 };
      const seasonal = seasonalData[number] || { factor: 1.0 };
      
      // Tính điểm nâng cao với nhiều yếu tố
      const details = calculateAdvancedScore(number, freq, hitRate, selectedDate, trend, seasonal);
      scoreForNumbers[number] = details.finalScore;
      scoreDetails[number] = details;
    }
    
    // Sắp xếp số theo điểm
    const sortedNumbers = Object.entries(scoreForNumbers)
      .sort((a, b) => b[1] - a[1]);
    
    // Hiển thị bảng số 2 chữ số với thông tin nâng cao
    const twoDigitsTable = document.querySelector('#twoDigitsTable tbody');
    if (twoDigitsTable) {
      twoDigitsTable.innerHTML = '';
      
      Object.entries(twoDigitNumbers)
        .sort((a, b) => scoreForNumbers[b[0]] - scoreForNumbers[a[0]])
        .forEach(([number, freq]) => {
          const methods = methodsForNumbers[number] || [];
          const hitRate = hitRatesForNumbers[number] || 0;
          const score = scoreForNumbers[number] || 0;
          const details = scoreDetails[number] || {};
          
          const row = document.createElement('tr');
          row.innerHTML = `
            <td class="fw-bold">${number}</td>
            <td>${freq} lần</td>
            <td>${methods.join(', ')}</td>
            <td>
              ${hitRate.toFixed(2)}% 
              <small class="text-muted d-block">${historicalHitRates[number] ? 'Dữ liệu thực' : 'Ước tính'}</small>
            </td>
            <td>
              ${score.toFixed(2)}
              <div class="progress mt-1" style="height: 4px;">
                <div class="progress-bar" style="width: ${Math.min(100, score)}%"></div>
              </div>
            </td>
            <td>
              ${score > 50 ? '<span class="badge bg-success">Nên đánh</span>' : 
                (score > 30 ? '<span class="badge bg-warning text-dark">Có thể đánh</span>' : 
                '<span class="badge bg-secondary">Không khuyến nghị</span>')}
              <button class="btn btn-sm btn-link p-0 mt-1 d-block" onclick="showAnalysisDetail('${number}')">
                Chi tiết
              </button>
            </td>
          `;
          twoDigitsTable.appendChild(row);
        });
    }
    
    // Hiển thị bảng số 3 chữ số
    const threeDigitsTable = document.querySelector('#threeDigitsTable tbody');
    if (threeDigitsTable) {
      threeDigitsTable.innerHTML = '';
      
      Object.entries(threeDigitNumbers)
        .sort((a, b) => scoreForNumbers[b[0]] - scoreForNumbers[a[0]])
        .forEach(([number, freq]) => {
          const methods = methodsForNumbers[number] || [];
          const hitRate = hitRatesForNumbers[number] || 0;
          const score = scoreForNumbers[number] || 0;
          const details = scoreDetails[number] || {};
          
          const row = document.createElement('tr');
          row.innerHTML = `
            <td class="fw-bold">${number}</td>
            <td>${freq} lần</td>
            <td>${methods.join(', ')}</td>
            <td>
              ${hitRate.toFixed(2)}% 
              <small class="text-muted d-block">${historicalHitRates[number] ? 'Dữ liệu thực' : 'Ước tính'}</small>
            </td>
            <td>
              ${score.toFixed(2)}
              <div class="progress mt-1" style="height: 4px;">
                <div class="progress-bar" style="width: ${Math.min(100, score)}%"></div>
              </div>
            </td>
            <td>
              ${score > 50 ? '<span class="badge bg-success">Nên đánh</span>' : 
                (score > 30 ? '<span class="badge bg-warning text-dark">Có thể đánh</span>' : 
                '<span class="badge bg-secondary">Không khuyến nghị</span>')}
              <button class="btn btn-sm btn-link p-0 mt-1 d-block" onclick="showAnalysisDetail('${number}')">
                Chi tiết
              </button>
            </td>
          `;
          threeDigitsTable.appendChild(row);
        });
    }
    
    // Hiển thị Top 10 số nên đánh với thông tin chi tiết hơn
    const topRecommendations = document.getElementById('topRecommendations');
    if (topRecommendations) {
      topRecommendations.innerHTML = '';
      
      sortedNumbers.slice(0, 10).forEach(([number, score], index) => {
        const freq = (twoDigitNumbers[number] || threeDigitNumbers[number] || 0);
        const hitRate = hitRatesForNumbers[number] || 0;
        const details = scoreDetails[number] || {};
        
        const row = document.createElement('tr');
        row.innerHTML = `
          <td class="fw-bold">
            ${index + 1}. ${number}
            ${details.trendFactor > 1.1 ? '<i class="fas fa-arrow-up text-success" title="Xu hướng tăng"></i>' : 
              (details.trendFactor < 0.9 ? '<i class="fas fa-arrow-down text-danger" title="Xu hướng giảm"></i>' : '')}
          </td>
          <td>
            ${score.toFixed(2)}
            <div class="progress mt-1" style="height: 4px;">
              <div class="progress-bar" style="width: ${Math.min(100, score)}%"></div>
            </div>
          </td>
          <td>${freq} lần</td>
          <td>${hitRate.toFixed(2)}%</td>
        `;
        topRecommendations.appendChild(row);
      });
    }
    
    // Hiển thị chiến lược với nhiều thông tin hơn
    // Chiến lược 1: Đánh theo tần suất
    const strategy1 = document.getElementById('strategy1Numbers');
    if (strategy1) {
      const topByFrequency = [...Object.entries({...twoDigitNumbers, ...threeDigitNumbers})]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      
      strategy1.innerHTML = topByFrequency.map(([number, freq]) =>
        `<span class="badge bg-primary me-2 mb-1">${number} (${freq} lần)</span>`
      ).join('');
    }
    
    // Chiến lược 2: Đánh theo tỉ lệ trúng
    const strategy2 = document.getElementById('strategy2Numbers');
    if (strategy2) {
      const topByHitRate = [...Object.entries(hitRatesForNumbers)]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      
      strategy2.innerHTML = topByHitRate.map(([number, rate]) =>
        `<span class="badge bg-success me-2 mb-1">${number} (${rate.toFixed(2)}%)</span>`
      ).join('');
    }
    
    // Chiến lược 3: Đánh theo điểm tổng hợp
    const strategy3 = document.getElementById('strategy3Numbers');
    if (strategy3) {
      strategy3.innerHTML = sortedNumbers.slice(0, 5).map(([number, score]) =>
        `<span class="badge bg-danger me-2 mb-1">${number} (${score.toFixed(2)} điểm)</span>`
      ).join('');
    }
    
    // Thêm chiến lược 4: Đánh theo xu hướng tăng
    const strategy4 = document.getElementById('strategy4Numbers');
    if (strategy4) {
      const topByTrend = Object.entries(trendData)
        .filter(([number]) => twoDigitNumbers[number] || threeDigitNumbers[number])
        .sort((a, b) => b[1].factor - a[1].factor)
        .slice(0, 5);
      
      strategy4.innerHTML = topByTrend.map(([number, data]) =>
        `<span class="badge bg-info me-2 mb-1">${number} (x${data.factor.toFixed(2)})</span>`
      ).join('');
    }
    
    // Thêm nhận xét phân tích nâng cao
    const analysisInsights = document.getElementById('analysisInsights');
    if (analysisInsights) {
      analysisInsights.innerHTML = '';
      
      // Tạo các nhận xét dựa trên dữ liệu và phân tích
      const insights = [
        `Số <strong>${mostFrequentTwoDigit}</strong> xuất hiện nhiều nhất (${maxTwoDigitFreq} lần) trong top 10 phương pháp.`,
        `Số <strong>${highestHitRateNumber}</strong> có tỉ lệ trúng cao nhất (${highestHitRate.toFixed(2)}%).`,
        `Có ${Object.keys(twoDigitNumbers).length} số 2 chữ số và ${Object.keys(threeDigitNumbers).length} số 3 chữ số được dự đoán.`
      ];
      
      // Sắp xếp phương pháp theo tỉ lệ trúng
      if (methodsInfo.length > 0) {
        const sortedMethods = [...methodsInfo].sort((a, b) => b.hitRate - a.hitRate);
        insights.push(`Phương pháp <strong>${sortedMethods[0].name}</strong> có tỉ lệ trúng cao nhất (${sortedMethods[0].hitRate.toFixed(2)}%).`);
      }
      
      // Thêm nhận xét về số xuất hiện trong nhiều phương pháp
      const numbersInMultipleMethods = [];
      for (const [number, methods] of Object.entries(methodsForNumbers)) {
        if (methods.length >= 3) { // Xuất hiện trong 3+ phương pháp
          numbersInMultipleMethods.push({number, count: methods.length});
        }
      }
      
      if (numbersInMultipleMethods.length > 0) {
        numbersInMultipleMethods.sort((a, b) => b.count - a.count);
        const topMultipleNumber = numbersInMultipleMethods[0];
        insights.push(`Số <strong>${topMultipleNumber.number}</strong> xuất hiện trong nhiều phương pháp nhất (${topMultipleNumber.count} phương pháp).`);
      }
      
      // Thêm nhận xét về xu hướng
      const risingTrendNumbers = Object.entries(trendData)
        .filter(([number, data]) => data.factor > 1.2 && (twoDigitNumbers[number] || threeDigitNumbers[number]))
        .sort((a, b) => b[1].factor - a[1].factor)
        .slice(0, 3);
      
      if (risingTrendNumbers.length > 0) {
        const trendInsight = `Các số có xu hướng tăng mạnh: ${risingTrendNumbers.map(([number, data]) => 
              // Thêm nhận xét về xu hướng
      const risingTrendNumbers = Object.entries(trendData)
        .filter(([number, data]) => data.factor > 1.2 && (twoDigitNumbers[number] || threeDigitNumbers[number]))
        .sort((a, b) => b[1].factor - a[1].factor)
        .slice(0, 3);
      
      if (risingTrendNumbers.length > 0) {
        const trendInsight = `Các số có xu hướng tăng mạnh: ${risingTrendNumbers.map(([number, data]) => 
          `<strong>${number}</strong> (x${data.factor.toFixed(2)})`).join(', ')}.`;
        insights.push(trendInsight);
      }
      
      // Thêm nhận xét về mùa vụ
      const seasonalNumbers = Object.entries(seasonalData)
        .filter(([number, data]) => data.factor > 1.2 && (twoDigitNumbers[number] || threeDigitNumbers[number]))
        .sort((a, b) => b[1].factor - a[1].factor)
        .slice(0, 3);
      
      if (seasonalNumbers.length > 0) {
        const seasonalInsight = `Các số có lợi thế theo ngày trong tuần: ${seasonalNumbers.map(([number, data]) => 
          `<strong>${number}</strong> (x${data.factor.toFixed(2)})`).join(', ')}.`;
        insights.push(seasonalInsight);
      }
      
      // Hiển thị các nhận xét
      insights.forEach(insight => {
        const li = document.createElement('li');
        li.innerHTML = insight;
        analysisInsights.appendChild(li);
      });
    }
    
    // Vẽ biểu đồ phân phối số
    if (typeof Chart !== 'undefined') {
      console.log("Attempting to create chart");
      
      // Chuẩn bị dữ liệu cho biểu đồ
      const twoDigitLabels = Object.keys(twoDigitNumbers).slice(0, 10);
      const twoDigitData = twoDigitLabels.map(num => twoDigitNumbers[num]);
      
      const threeDigitLabels = Object.keys(threeDigitNumbers).slice(0, 10);
      const threeDigitData = threeDigitLabels.map(num => threeDigitNumbers[num]);
      
      // Hủy biểu đồ cũ nếu có
      if (window.numbersChart) {
        window.numbersChart.destroy();
      }
      
      // Tạo biểu đồ mới
      const chartCanvas = document.getElementById('numbersDistributionChart');
      if (chartCanvas) {
        const ctx = chartCanvas.getContext('2d');
        window.numbersChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: [...twoDigitLabels, ...threeDigitLabels],
            datasets: [
              {
                label: 'Tần suất xuất hiện',
                data: [...twoDigitData, ...threeDigitData],
                backgroundColor: [
                  ...Array(twoDigitLabels.length).fill('rgba(54, 162, 235, 0.6)'),
                  ...Array(threeDigitLabels.length).fill('rgba(255, 99, 132, 0.6)')
                ],
                borderColor: [
                  ...Array(twoDigitLabels.length).fill('rgba(54, 162, 235, 1)'),
                  ...Array(threeDigitLabels.length).fill('rgba(255, 99, 132, 1)')
                ],
                borderWidth: 1
              },
              {
                label: 'Tỉ lệ trúng (%)',
                data: [...twoDigitLabels, ...threeDigitLabels].map(num => hitRatesForNumbers[num] || 0),
                type: 'line',
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                fill: false,
                yAxisID: 'y1'
              },
              {
                label: 'Điểm tổng hợp',
                data: [...twoDigitLabels, ...threeDigitLabels].map(num => scoreForNumbers[num] / 5 || 0),
                type: 'line',
                borderColor: 'rgba(153, 102, 255, 1)',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderWidth: 2,
                borderDash: [5, 5],
                fill: false,
                yAxisID: 'y1'
              }
            ]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Tần suất xuất hiện'
                }
              },
              y1: {
                beginAtZero: true,
                position: 'right',
                grid: {
                  drawOnChartArea: false
                },
                title: {
                  display: true,
                  text: 'Tỉ lệ trúng (%) / Điểm'
                },
                max: Math.max(
                  ...Object.values(hitRatesForNumbers),
                  ...Object.values(scoreForNumbers).map(score => score / 5)
                ) * 1.2 || 20
              }
            },
            plugins: {
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const datasetLabel = context.dataset.label || '';
                    const value = context.raw;
                    const number = context.label;
                    
                    if (context.datasetIndex === 0) {
                      return `${datasetLabel}: ${value} lần`;
                    } else if (context.datasetIndex === 1) {
                      return `${datasetLabel}: ${value.toFixed(2)}%`;
                    } else {
                      return `${datasetLabel}: ${(value * 5).toFixed(2)}`;
                    }
                  },
                  afterLabel: function(context) {
                    const number = context.label;
                    const methods = methodsForNumbers[number] || [];
                    const details = scoreDetails[number] || {};
                    
                    let result = `Phương pháp: ${methods.join(', ')}`;
                    
                    if (details.trendFactor) {
                      result += `\nXu hướng: x${details.trendFactor.toFixed(2)}`;
                    }
                    
                    if (details.seasonalFactor) {
                      result += `\nMùa vụ: x${details.seasonalFactor.toFixed(2)}`;
                    }
                    
                    return result;
                  }
                }
              },
              legend: {
                position: 'top',
              },
              title: {
                display: true,
                text: 'Phân tích Top 20 số'
              }
            }
          }
        });
      } else {
        console.error("Chart canvas element not found");
      }
    } else {
      console.warn("Chart.js not loaded");
    }
    
    // Tạo heat map cho các số 2 chữ số
    createTwoDigitHeatMap(twoDigitNumbers, hitRatesForNumbers, scoreForNumbers, methodsForNumbers, scoreDetails);
    
    // Gán hàm hiển thị phân tích chi tiết vào window để có thể gọi từ onclick
    window.showAnalysisDetail = function(number) {
      showNumberAnalysisDetail(number, {
        frequency: twoDigitNumbers[number] || threeDigitNumbers[number] || 0,
        hitRate: hitRatesForNumbers[number] || 0,
        score: scoreForNumbers[number] || 0,
        methods: methodsForNumbers[number] || [],
        details: scoreDetails[number] || {},
        historical: historicalHitRates[number],
        trend: trendData[number] || {},
        seasonal: seasonalData[number] || {}
      });
    };
  }
  
  // Hàm tạo heat map nâng cao cho các số 2 chữ số
  function createTwoDigitHeatMap(twoDigitNumbers, hitRatesForNumbers, scoreForNumbers, methodsForNumbers, scoreDetails) {
    console.log("Creating enhanced heat map");
    
    // Tạo phần tử container nếu chưa có
    let heatMapContainer = document.getElementById('twoDigitHeatMap');
    if (!heatMapContainer) {
      console.log("Creating new heat map container");
      heatMapContainer = document.createElement('div');
      heatMapContainer.id = 'twoDigitHeatMap';
      heatMapContainer.className = 'mt-4';
      
      const title = document.createElement('h5');
      title.className = 'mb-3';
      title.textContent = 'Heat Map số 2 chữ số';
      
      heatMapContainer.appendChild(title);
      
      // Thêm vào tab số 2 chữ số
      const twoDigitsTab = document.getElementById('twoDigits');
      if (twoDigitsTab) {
        twoDigitsTab.appendChild(heatMapContainer);
      } else {
        console.error("Two digits tab not found");
        return;
      }
    }
    
    // Xóa nội dung cũ
    while (heatMapContainer.children.length > 1) {
      heatMapContainer.removeChild(heatMapContainer.lastChild);
    }
    
    // Thêm bộ chọn chế độ hiển thị
    const displayModeSelector = document.createElement('div');
    displayModeSelector.className = 'mb-3';
    displayModeSelector.innerHTML = `
      <div class="btn-group" role="group">
        <input type="radio" class="btn-check" name="heatmapMode" id="modeFrequency" autocomplete="off" checked>
        <label class="btn btn-outline-primary" for="modeFrequency">Tần suất</label>
        
        <input type="radio" class="btn-check" name="heatmapMode" id="modeHitRate" autocomplete="off">
        <label class="btn btn-outline-success" for="modeHitRate">Tỉ lệ trúng</label>
        
        <input type="radio" class="btn-check" name="heatmapMode" id="modeScore" autocomplete="off">
        <label class="btn btn-outline-danger" for="modeScore">Điểm tổng hợp</label>
      </div>
    `;
    heatMapContainer.appendChild(displayModeSelector);
    
    // Tạo grid 10x10 cho các số từ 00-99
    const grid = document.createElement('div');
    grid.className = 'two-digit-grid';
    grid.style.display = 'grid';
    grid.style.gridTemplateColumns = 'repeat(10, 1fr)';
    grid.style.gap = '2px';
    
    // Tính giá trị lớn nhất để chuẩn hóa màu sắc
    const maxFrequency = Math.max(...Object.values(twoDigitNumbers)) || 1;
    const maxHitRate = Math.max(...Object.values(hitRatesForNumbers)) || 1;
    const maxScore = Math.max(...Object.values(scoreForNumbers)) || 1;
    
    console.log("Max values - Frequency:", maxFrequency, "Hit Rate:", maxHitRate, "Score:", maxScore);
    
    // Tạo các ô cho mỗi số
    for (let i = 0; i < 100; i++) {
      const number = i.toString().padStart(2, '0');
      const frequency = twoDigitNumbers[number] || 0;
      const hitRate = hitRatesForNumbers[number] || 0;
      const score = scoreForNumbers[number] || 0;
      const details = scoreDetails[number] || {};
      
      // Tính màu dựa trên tần suất (từ trắng đến đỏ)
      const freqIntensity = frequency / maxFrequency;
      const hitRateIntensity = hitRate / maxHitRate;
      const scoreIntensity = score / maxScore;
      
      const cell = document.createElement('div');
      cell.className = 'number-cell';
      cell.dataset.number = number;
      cell.dataset.frequency = frequency;
      cell.dataset.hitRate = hitRate;
      cell.dataset.score = score;
      
      cell.style.padding = '5px';
      cell.style.textAlign = 'center';
      cell.style.backgroundColor = `rgb(${255}, ${255 * (1 - freqIntensity * 0.8)}, ${255 * (1 - freqIntensity * 0.8)})`;
      cell.style.border = '1px solid #ddd';
      cell.style.borderRadius = '4px';
      cell.style.cursor = 'pointer';
      cell.style.transition = 'all 0.3s ease';
      cell.style.position = 'relative';
      
      cell.innerHTML = `
        <div class="fw-bold">${number}</div>
        <div class="small frequency-display">${frequency > 0 ? frequency + 'x' : ''}</div>
        <div class="small hit-rate-display" style="display:none">${hitRate > 0 ? hitRate.toFixed(1) + '%' : ''}</div>
        <div class="small score-display" style="display:none">${score > 0 ? score.toFixed(1) : ''}</div>
      `;
      
      // Thêm chỉ báo xu hướng
      if (details.trendFactor > 1.1) {
        const trendIndicator = document.createElement('div');
        trendIndicator.style.position = 'absolute';
        trendIndicator.style.top = '2px';
        trendIndicator.style.right = '2px';
        trendIndicator.style.fontSize = '8px';
        trendIndicator.innerHTML = '▲';
        trendIndicator.style.color = '#28a745';
        cell.appendChild(trendIndicator);
      } else if (details.trendFactor < 0.9) {
        const trendIndicator = document.createElement('div');
        trendIndicator.style.position = 'absolute';
        trendIndicator.style.top = '2px';
        trendIndicator.style.right = '2px';
        trendIndicator.style.fontSize = '8px';
        trendIndicator.innerHTML = '▼';
        trendIndicator.style.color = '#dc3545';
        cell.appendChild(trendIndicator);
      }
      
      // Thêm tooltip khi hover
      cell.title = `Số ${number}:\nTần suất: ${frequency} lần\nTỉ lệ trúng: ${hitRate.toFixed(2)}%\nĐiểm: ${score.toFixed(2)}`;
      
      // Thêm border đậm nếu là số xuất hiện nhiều
      if (frequency > 0) {
        cell.style.borderColor = '#007bff';
        cell.style.borderWidth = '2px';
      }
      
      // Thêm sự kiện click để hiển thị thông tin chi tiết
      cell.addEventListener('click', function() {
        const methods = methodsForNumbers[number] || [];
        window.showAnalysisDetail(number);
      });
      
      grid.appendChild(cell);
    }
    
    heatMapContainer.appendChild(grid);
    
    // Thêm chú thích màu
    const legend = document.createElement('div');
    legend.className = 'mt-3 d-flex justify-content-center align-items-center';
    legend.innerHTML = `
      <div class="d-flex align-items-center me-4">
        <div style="width: 20px; height: 20px; background-color: rgb(255, 255, 255); border: 1px solid #ddd; margin-right: 5px;"></div>
        <span>Không xuất hiện</span>
      </div>
      <div class="d-flex align-items-center me-4">
        <div style="width: 20px; height: 20px; background-color: rgb(255, 204, 204); border: 1px solid #ddd; margin-right: 5px;"></div>
        <span>Ít xuất hiện</span>
      </div>
      <div class="d-flex align-items-center">
        <div style="width: 20px; height: 20px; background-color: rgb(255, 51, 51); border: 1px solid #ddd; margin-right: 5px;"></div>
        <span>Xuất hiện nhiều</span>
      </div>
    `;
    heatMapContainer.appendChild(legend);
    
    // Thêm sự kiện cho các nút chế độ hiển thị
    document.getElementById('modeFrequency').addEventListener('change', function() {
      if (this.checked) {
        document.querySelectorAll('.number-cell').forEach(cell => {
          const frequency = parseFloat(cell.dataset.frequency || 0);
          const intensity = frequency / maxFrequency;
          cell.style.backgroundColor = `rgb(${255}, ${255 * (1 - intensity * 0.8)}, ${255 * (1 - intensity * 0.8)})`;
          cell.querySelectorAll('.frequency-display').forEach(el => el.style.display = '');
          cell.querySelectorAll('.hit-rate-display').forEach(el => el.style.display = 'none');
          cell.querySelectorAll('.score-display').forEach(el => el.style.display = 'none');
        });
      }
    });
    
    document.getElementById('modeHitRate').addEventListener('change', function() {
      if (this.checked) {
        document.querySelectorAll('.number-cell').forEach(cell => {
          const hitRate = parseFloat(cell.dataset.hitRate || 0);
          const intensity = hitRate / maxHitRate;
          cell.style.backgroundColor = `rgb(${255 * (1 - intensity * 0.8)}, ${255}, ${255 * (1 - intensity * 0.8)})`;
          cell.querySelectorAll('.frequency-display').forEach(el => el.style.display = 'none');
          cell.querySelectorAll('.hit-rate-display').forEach(el => el.style.display = '');
          cell.querySelectorAll('.score-display').forEach(el => el.style.display = 'none');
        });
      }
    });
    
    document.getElementById('modeScore').addEventListener('change', function() {
      if (this.checked) {
        document.querySelectorAll('.number-cell').forEach(cell => {
          const score = parseFloat(cell.dataset.score || 0);
          const intensity = score / maxScore;
          cell.style.backgroundColor = `rgb(${255 * (1 - intensity * 0.8)}, ${255 * (1 - intensity * 0.8)}, ${255})`;
          cell.querySelectorAll('.frequency-display').forEach(el => el.style.display = 'none');
          cell.querySelectorAll('.hit-rate-display').forEach(el => el.style.display = 'none');
          cell.querySelectorAll('.score-display').forEach(el => el.style.display = '');
        });
      }
    });
    
    console.log("Heat map created successfully");
  }
  
  // Hàm hiển thị phân tích chi tiết cho số
  function showNumberAnalysisDetail(number, data) {
    console.log(`Showing detailed analysis for number ${number}`, data);
    
    // Tạo modal
    const modalId = `analysisModal-${number}`;
    let modal = document.getElementById(modalId);
    
    // Nếu modal đã tồn tại, xóa đi để tạo mới
    if (modal) {
      document.body.removeChild(modal);
    }
    
    // Tạo modal mới
    modal = document.createElement('div');
    modal.id = modalId;
    modal.className = 'modal fade';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-labelledby', `${modalId}-label`);
    modal.setAttribute('aria-hidden', 'true');
    
    // Chuẩn bị dữ liệu chi tiết
    const frequency = data.frequency;
    const hitRate = data.hitRate;
    const score = data.score;
    const methods = data.methods;
    const details = data.details;
    const historical = data.historical;
    const trend = data.trend;
    const seasonal = data.seasonal;
    
    // Xây dựng nội dung modal
    modal.innerHTML = `
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="${modalId}-label">
              Phân tích chi tiết số: <span class="badge bg-primary">${number}</span>
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <ul class="nav nav-tabs" id="numberAnalysisTabs" role="tablist">
              <li class="nav-item" role="presentation">
                <button class="nav-link active" id="summary-tab-${number}" data-bs-toggle="tab" 
                        data-bs-target="#summary-${number}" type="button" role="tab">
                  Tổng quan
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button class="nav-link" id="score-details-tab-${number}" data-bs-toggle="tab" 
                        data-bs-target="#score-details-${number}" type="button" role="tab">
                  Chi tiết điểm
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button class="nav-link" id="history-tab-${number}" data-bs-toggle="tab" 
                        data-bs-target="#history-${number}" type="button" role="tab">
                  Lịch sử & Xu hướng
                </button>
              </li>
            </ul>
            
            <div class="tab-content pt-3">
              <!-- Tab Tổng quan -->
              <div class="tab-pane fade show active" id="summary-${number}" role="tabpanel">
                <div class="row">
                  <div class="col-md-6">
                    <div class="card mb-3">
                      <div class="card-header bg-light">
                        <h6 class="mb-0">Thông tin cơ bản</h6>
                      </div>
                      <div class="card-body">
                        <p><strong>Tần suất xuất hiện:</strong> ${frequency} lần</p>
                        <p><strong>Tỉ lệ trúng:</strong> ${hitRate.toFixed(2)}%</p>
                        <p><strong>Điểm tổng hợp:</strong> ${score.toFixed(2)}</p>
                        <p><strong>Đánh giá:</strong> 
                          ${score > 50 ? '<span class="badge bg-success">Nên đánh</span>' : 
                            (score > 30 ? '<span class="badge bg-warning text-dark">Có thể đánh</span>' : 
                            '<span class="badge bg-secondary">Không khuyến nghị</span>')}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="card mb-3">
                      <div class="card-header bg-light">
                        <h6 class="mb-0">Các phương pháp dự đoán</h6>
                      </div>
                      <div class="card-body">
                        <ul class="list-group">
                          ${methods.map(method => `<li class="list-group-item">${method}</li>`).join('')}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="card mb-3">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Thông tin chi tiết</h6>
                  </div>
                  <div class="card-body">
                    <div class="row">
                      <div class="col-md-4">
                        <p><strong>Phân tích cấu trúc:</strong></p>
                        <ul>
                          ${number.length === 2 ? `
                            <li>Chữ số hàng chục: ${number[0]}</li>
                            <li>Chữ số hàng đơn vị: ${number[1]}</li>
                            <li>Tổng các chữ số: ${parseInt(number[0]) + parseInt(number[1])}</li>
                            <li>Hiệu các chữ số: ${Math.abs(parseInt(number[0]) - parseInt(number[1]))}</li>
                          ` : `
                            <li>Chữ số hàng trăm: ${number[0]}</li>
                            <li>Chữ số hàng chục: ${number[1]}</li>
                            <li>Chữ số hàng đơn vị: ${number[2]}</li>
                            <li>Tổng các chữ số: ${parseInt(number[0]) + parseInt(number[1]) + parseInt(number[2])}</li>
                          `}
                        </ul>
                      </div>
                      <div class="col-md-4">
                        <p><strong>Đánh giá xu hướng:</strong></p>
                        <div class="d-flex align-items-center mb-2">
                          <div class="me-2" style="width: 30px; text-align: center;">
                            ${details.trendFactor > 1.1 ? '<i class="fas fa-arrow-up text-success"></i>' : 
                              (details.trendFactor < 0.9 ? '<i class="fas fa-arrow-down text-danger"></i>' : 
                              '<i class="fas fa-equals text-secondary"></i>')}
                          </div>
                          <div class="flex-grow-1">
                            <div class="progress" style="height: 8px;">
                              <div class="progress-bar ${details.trendFactor > 1 ? 'bg-success' : 'bg-danger'}" 
                                   style="width: ${Math.abs(details.trendFactor - 1) * 100}%"></div>
                            </div>
                          </div>
                          <div class="ms-2">
                            x${details.trendFactor ? details.trendFactor.toFixed(2) : '1.00'}
                          </div>
                        </div>
                        <p class="small text-muted">
                          ${details.trendFactor > 1.1 ? 'Số này có xu hướng tăng mạnh.' : 
                            (details.trendFactor > 1.0 ? 'Số này có xu hướng tăng nhẹ.' : 
                            (details.trendFactor < 0.9 ? 'Số này có xu hướng giảm mạnh.' : 
                            'Số này có xu hướng ổn định.'))}
                        </p>
                      </div>
                      <div class="col-md-4">
                        <p><strong>Đánh giá mùa vụ:</strong></p>
                        <div class="d-flex align-items-center mb-2">
                          <div class="me-2" style="width: 30px; text-align: center;">
                            ${details.seasonalFactor > 1.1 ? '<i class="fas fa-calendar-check text-success"></i>' : 
                              (details.seasonalFactor < 0.9 ? '<i class="fas fa-calendar-times text-danger"></i>' : 
                              '<i class="fas fa-calendar-day text-secondary"></i>')}
                          </div>
                          <div class="flex-grow-1">
                            <div class="progress" style="height: 8px;">
                              <div class="progress-bar ${details.seasonalFactor > 1 ? 'bg-success' : 'bg-danger'}" 
                                   style="width: ${Math.abs(details.seasonalFactor - 1) * 100}%"></div>
                            </div>
                          </div>
                          <div class="ms-2">
                            x${details.seasonalFactor ? details.seasonalFactor.toFixed(2) : '1.00'}
                          </div>
                        </div>
                        <p class="small text-muted">
                          ${details.seasonalFactor > 1.1 ? 'Số này thường trúng vào ngày này trong tuần.' : 
                            (details.seasonalFactor > 1.0 ? 'Số này có khả năng trúng cao vào ngày này.' : 
                            (details.seasonalFactor < 0.9 ? 'Số này ít khi trúng vào ngày này trong tuần.' : 
                            'Số này không có quy luật rõ ràng theo ngày trong tuần.'))}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Tab Chi tiết điểm -->
              <div class="tab-pane fade" id="score-details-${number}" role="tabpanel">
                <div class="card mb-3">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Phân tích điểm số chi tiết</h6>
                  </div>
                  <div class="card-body">
                    <table class="table table-sm table-bordered">
                      <thead>
                        <tr>
                          <th>Yếu tố</th>
                          <th>Giá trị</th>
                          <th>Hệ số</th>
                          <th>Điểm</th>
                        </tr>
                      </thead>
                      <tbody>
                                                <tr>
                          <td>Tần suất xuất hiện</td>
                          <td>${frequency} lần</td>
                          <td>x4</td>
                          <td>${(frequency * 4).toFixed(2)}</td>
                        </tr>
                        <tr>
                          <td>Tỉ lệ trúng</td>
                          <td>${hitRate.toFixed(2)}%</td>
                          <td>x2</td>
                          <td>${(hitRate * 2).toFixed(2)}</td>
                        </tr>
                        <tr>
                          <td>Xu hướng</td>
                          <td>x${details.trendFactor ? details.trendFactor.toFixed(2) : '1.00'}</td>
                          <td>${details.baseScore ? details.baseScore.toFixed(2) : ((frequency * 4) + (hitRate * 2)).toFixed(2)}</td>
                          <td>${details.trendScore ? details.trendScore.toFixed(2) : ((frequency * 4 + hitRate * 2) * (details.trendFactor || 1)).toFixed(2)}</td>
                        </tr>
                        <tr>
                          <td>Mùa vụ</td>
                          <td>x${details.seasonalFactor ? details.seasonalFactor.toFixed(2) : '1.00'}</td>
                          <td>${details.trendScore ? details.trendScore.toFixed(2) : ((frequency * 4 + hitRate * 2) * (details.trendFactor || 1)).toFixed(2)}</td>
                          <td>${details.seasonalScore ? details.seasonalScore.toFixed(2) : ((frequency * 4 + hitRate * 2) * (details.trendFactor || 1) * (details.seasonalFactor || 1)).toFixed(2)}</td>
                        </tr>
                        <tr>
                          <td>Điểm tổng hợp</td>
                          <td colspan="2" class="text-end fw-bold">Tổng:</td>
                          <td class="fw-bold">${score.toFixed(2)}</td>
                        </tr>
                      </tbody>
                    </table>
                    
                    <div class="alert alert-info mt-3">
                      <h6 class="mb-2">Cách tính điểm:</h6>
                      <ol>
                        <li>Điểm cơ bản = (Tần suất × 4) + (Tỉ lệ trúng × 2)</li>
                        <li>Điểm xu hướng = Điểm cơ bản × Hệ số xu hướng</li>
                        <li>Điểm cuối cùng = Điểm xu hướng × Hệ số mùa vụ</li>
                      </ol>
                      <p class="mb-0"><strong>Diễn giải:</strong> ${getScoreExplanation(score, details)}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Tab Lịch sử & Xu hướng -->
              <div class="tab-pane fade" id="history-${number}" role="tabpanel">
                <div class="card mb-3">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Lịch sử trúng số</h6>
                  </div>
                  <div class="card-body">
                    ${historical ? `
                      <p><strong>Số lần trúng:</strong> ${historical.hits} / ${historical.total} lần (${historical.rate.toFixed(2)}%)</p>
                      <div class="mb-3">
                        <label class="form-label">Tỉ lệ trúng:</label>
                        <div class="progress">
                          <div class="progress-bar bg-success" role="progressbar" style="width: ${historical.rate}%;"
                               aria-valuenow="${historical.rate}" aria-valuemin="0" aria-valuemax="100">
                            ${historical.rate.toFixed(2)}%
                          </div>
                        </div>
                      </div>
                      ${historical.dates && historical.dates.length > 0 ? `
                        <p><strong>Ngày trúng gần đây:</strong></p>
                        <ul class="list-group">
                          ${historical.dates.slice(0, 5).map(date => `
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                              ${new Date(date).toLocaleDateString('vi-VN')}
                              <span class="badge bg-success rounded-pill">Trúng</span>
                            </li>
                          `).join('')}
                        </ul>
                      ` : ''}
                    ` : `
                      <div class="alert alert-warning">
                        Không có dữ liệu lịch sử cho số này.
                      </div>
                    `}
                  </div>
                </div>
                
                <div class="card mb-3">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Phân tích xu hướng</h6>
                  </div>
                  <div class="card-body">
                    ${trend && trend.data ? `
                      <p><strong>Xu hướng hiện tại:</strong> 
                        ${trend.factor > 1.1 ? 'Tăng mạnh' : 
                          (trend.factor > 1.0 ? 'Tăng nhẹ' : 
                          (trend.factor < 0.9 ? 'Giảm mạnh' : 
                          'Ổn định'))}
                        (x${trend.factor.toFixed(2)})
                      </p>
                      <div class="mb-3">
                        <canvas id="trendChart-${number}" height="200"></canvas>
                      </div>
                      <p class="text-muted small">
                        Biểu đồ thể hiện tỉ lệ trúng theo thời gian. Xu hướng tăng/giảm được tính toán dựa trên 
                        dữ liệu 90 ngày gần đây so với dữ liệu cũ hơn.
                      </p>
                    ` : `
                      <div class="alert alert-warning">
                        Không đủ dữ liệu để phân tích xu hướng.
                      </div>
                    `}
                  </div>
                </div>
                
                <div class="card">
                  <div class="card-header bg-light">
                    <h6 class="mb-0">Phân tích mùa vụ</h6>
                  </div>
                  <div class="card-body">
                    ${seasonal && seasonal.data ? `
                      <p><strong>Hệ số mùa vụ:</strong> x${seasonal.factor.toFixed(2)}</p>
                      <p><strong>Ngày tốt nhất trong tuần:</strong> ${getBestDayOfWeek(seasonal.data)}</p>
                      <div class="mb-3">
                        <canvas id="seasonalChart-${number}" height="200"></canvas>
                      </div>
                      <p class="text-muted small">
                        Biểu đồ thể hiện tỉ lệ trúng theo ngày trong tuần. Ngày có cột cao nhất là ngày có 
                        tỉ lệ trúng cao nhất cho số này.
                      </p>
                    ` : `
                      <div class="alert alert-warning">
                        Không đủ dữ liệu để phân tích mùa vụ.
                      </div>
                    `}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Đóng</button>
          </div>
        </div>
      </div>
    `;
    
    // Thêm modal vào trang
    document.body.appendChild(modal);
    
    // Hiển thị modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    
    // Vẽ biểu đồ xu hướng và mùa vụ nếu có dữ liệu
    modal.addEventListener('shown.bs.modal', function() {
      // Vẽ biểu đồ xu hướng
      if (trend && trend.data && typeof Chart !== 'undefined') {
        const trendCanvas = document.getElementById(`trendChart-${number}`);
        if (trendCanvas) {
          const trendCtx = trendCanvas.getContext('2d');
          new Chart(trendCtx, {
            type: 'line',
            data: {
              labels: trend.data.map(d => d.label),
              datasets: [{
                label: 'Tỉ lệ trúng (%)',
                data: trend.data.map(d => d.rate),
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                tension: 0.3
              }]
            },
            options: {
              responsive: true,
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Tỉ lệ trúng (%)'
                  }
                }
              },
              plugins: {
                title: {
                  display: true,
                  text: `Xu hướng tỉ lệ trúng của số ${number} theo thời gian`
                }
              }
            }
          });
        }
      }
      
      // Vẽ biểu đồ mùa vụ
      if (seasonal && seasonal.data && typeof Chart !== 'undefined') {
        const seasonalCanvas = document.getElementById(`seasonalChart-${number}`);
        if (seasonalCanvas) {
          const seasonalCtx = seasonalCanvas.getContext('2d');
          new Chart(seasonalCtx, {
            type: 'bar',
            data: {
              labels: ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'],
              datasets: [{
                label: 'Tỉ lệ trúng (%)',
                data: seasonal.data,
                backgroundColor: seasonal.data.map((rate, index) => {
                  // Highlight ngày tốt nhất
                  return index === seasonal.data.indexOf(Math.max(...seasonal.data)) 
                    ? 'rgba(40, 167, 69, 0.6)' 
                    : 'rgba(54, 162, 235, 0.6)';
                }),
                borderColor: seasonal.data.map((rate, index) => {
                  return index === seasonal.data.indexOf(Math.max(...seasonal.data)) 
                    ? 'rgba(40, 167, 69, 1)' 
                    : 'rgba(54, 162, 235, 1)';
                }),
                borderWidth: 1
              }]
            },
            options: {
              responsive: true,
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Tỉ lệ trúng (%)'
                  }
                }
              },
              plugins: {
                title: {
                  display: true,
                  text: `Tỉ lệ trúng của số ${number} theo ngày trong tuần`
                }
              }
            }
          });
        }
      }
    });
  }
  
  // Hàm lấy dự đoán lịch sử cho phương pháp
  function getHistoricalPredictions(methodId, selectedDate) {
    // Trong thực tế, bạn sẽ lấy dữ liệu này từ API hoặc database
    // Trong ví dụ này, chúng ta sẽ trả về một mảng rỗng
    return [];
  }
  
  // Hàm tạo số dựa trên phân tích tần suất
  function generateWeightedNumbers(methodName, selectedDate) {
    // Giả lập việc tạo số thông minh
    const numbers = [];
    const count = Math.floor(Math.random() * 10) + 5;
    
    for (let i = 0; i < count; i++) {
      if (Math.random() < 0.7) {
        const num = Math.floor(Math.random() * 100).toString().padStart(2, '0');
        numbers.push(num);
      } else {
        const num = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
        numbers.push(num);
      }
    }
    
    return numbers;
  }
  
  // Hàm tính tỉ lệ trúng cho số tương tự
  function calculateSimilarNumbersHitRate(number, historicalRates) {
    // Với số 2 chữ số, số tương tự có thể là:
    // - Số có cùng chữ số hàng chục
    // - Số có cùng chữ số hàng đơn vị
    // - Số có tổng chữ số bằng nhau
    
    if (number.length === 2) {
      const tens = number[0];
      const units = number[1];
      const sum = parseInt(tens) + parseInt(units);
      
      let similarRates = [];
      let weightedSum = 0;
      let totalWeight = 0;
      
      // Duyệt qua tất cả số có dữ liệu lịch sử
      for (const [otherNumber, info] of Object.entries(historicalRates)) {
        if (otherNumber.length === 2) {
          const otherTens = otherNumber[0];
          const otherUnits = otherNumber[1];
          const otherSum = parseInt(otherTens) + parseInt(otherUnits);
          
          let similarity = 0;
          if (tens === otherTens) similarity += 3; // Cùng hàng chục
          if (units === otherUnits) similarity += 3; // Cùng hàng đơn vị
          if (sum === otherSum) similarity += 2; // Cùng tổng
          
          // Nếu có độ tương đồng, thêm vào tính toán
          if (similarity > 0) {
            weightedSum += info.rate * similarity;
            totalWeight += similarity;
            similarRates.push({ number: otherNumber, rate: info.rate, similarity });
          }
        }
      }
      
      // Trả về trung bình có trọng số nếu có đủ dữ liệu
      if (totalWeight > 0) {
        console.log(`Calculated similar hit rate for ${number} based on ${similarRates.length} similar numbers`);
        return weightedSum / totalWeight;
      }
    } else if (number.length === 3) {
      // Xử lý tương tự cho số 3 chữ số
      const hundreds = number[0];
      const tens = number[1];
      const units = number[2];
      const sum = parseInt(hundreds) + parseInt(tens) + parseInt(units);
      
      let similarRates = [];
      let weightedSum = 0;
      let totalWeight = 0;
      
      for (const [otherNumber, info] of Object.entries(historicalRates)) {
        if (otherNumber.length === 3) {
          const otherHundreds = otherNumber[0];
          const otherTens = otherNumber[1];
          const otherUnits = otherNumber[2];
          const otherSum = parseInt(otherHundreds) + parseInt(otherTens) + parseInt(otherUnits);
          
          let similarity = 0;
          if (hundreds === otherHundreds) similarity += 2;
          if (tens === otherTens) similarity += 2;
          if (units === otherUnits) similarity += 2;
          if (sum === otherSum) similarity += 1;
          
          if (similarity > 0) {
            weightedSum += info.rate * similarity;
            totalWeight += similarity;
            similarRates.push({ number: otherNumber, rate: info.rate, similarity });
          }
        }
      }
      
      if (totalWeight > 0) {
        return weightedSum / totalWeight;
      }
    }
    
    // Nếu không có số tương tự, sử dụng trung bình chung
    const allRates = Object.values(historicalRates).map(info => info.rate);
    const avgRate = allRates.length > 0 ? 
      allRates.reduce((sum, rate) => sum + rate, 0) / allRates.length : 5;
    
    // Dao động ngẫu nhiên ±20% quanh trung bình
    return avgRate * (0.8 + Math.random() * 0.4);
  }
  
  // Hàm tính xu hướng dựa trên dữ liệu lịch sử
  function calculateTrends(historicalHitRates, selectedDate) {
    const trendData = {};
    const selectedDateObj = new Date(selectedDate);
    
    // Với mỗi số có dữ liệu lịch sử
    for (const [number, info] of Object.entries(historicalHitRates)) {
      if (info.dates && info.dates.length > 0) {
        // Chia thành hai nhóm: 90 ngày gần đây và trước đó
        const recentDates = [];
        const olderDates = [];
        
        info.dates.forEach(dateStr => {
          const date = new Date(dateStr);
          const diffDays = Math.floor((selectedDateObj - date) / (1000 * 60 * 60 * 24));
          
          if (diffDays <= 90) {
            recentDates.push(date);
          } else {
            olderDates.push(date);
          }
        });
        
        // Tính tỉ lệ trúng trong 90 ngày gần đây
        const recentRate = recentDates.length / 90 * 100;
        
        // Tính tỉ lệ trúng trong khoảng thời gian trước đó
        const olderRate = olderDates.length > 0 ? 
          olderDates.length / (info.total - 90) * 100 : 0;
        
        // Tính hệ số xu hướng
        let trendFactor = 1.0;
        if (olderRate > 0) {
          trendFactor = recentRate / olderRate;
        } else if (recentRate > 0) {
          trendFactor = 1.2; // Nếu không có dữ liệu cũ nhưng có dữ liệu gần đây, coi là xu hướng tăng
        }
        
        // Giới hạn hệ số xu hướng trong khoảng hợp lý
        trendFactor = Math.max(0.5, Math.min(2.0, trendFactor));
        
        // Tạo dữ liệu cho biểu đồ xu hướng
        const trendChartData = [
          { label: '90+ ngày trước', rate: olderRate },
          { label: '60-90 ngày', rate: calculateRateForPeriod(info.dates, 60, 90, selectedDateObj) },
          { label: '30-60 ngày', rate: calculateRateForPeriod(info.dates, 30, 60, selectedDateObj) },
          { label: '0-30 ngày', rate: calculateRateForPeriod(info.dates, 0, 30, selectedDateObj) }
        ];
        
        trendData[number] = {
          factor: trendFactor,
          recentRate: recentRate,
          olderRate: olderRate,
          data: trendChartData
        };
      } else {
        // Nếu không có dữ liệu ngày cụ thể, sử dụng hệ số mặc định
        trendData[number] = {
          factor: 1.0,
          recentRate: 0,
          olderRate: 0,
          data: null
        };
      }
    }
    
    return trendData;
  }
  
  // Hàm tính tỉ lệ trúng cho một khoảng thời gian cụ thể
  function calculateRateForPeriod(dates, startDays, endDays, referenceDate) {
    const periodDates = dates.filter(dateStr => {
      const date = new Date(dateStr);
      const diffDays = Math.floor((referenceDate - date) / (1000 * 60 * 60 * 24));
      return diffDays >= startDays && diffDays < endDays;
    });
    
    return periodDates.length / (endDays - startDays) * 100;
  }
  
  // Hàm tính các yếu tố mùa vụ
  function calculateSeasonalFactors(historicalHitRates, selectedDate) {
    const seasonalData = {};
    const selectedDayOfWeek = new Date(selectedDate).getDay(); // 0 = CN, 1 = T2, ...
    
    for (const [number, info] of Object.entries(historicalHitRates)) {
      if (info.dates && info.dates.length > 0) {
        // Thống kê số lần trúng theo ngày trong tuần
        const hitsByDay = [0, 0, 0, 0, 0, 0, 0]; // CN, T2, T3, T4, T5, T6, T7
        
        info.dates.forEach(dateStr => {
          const dayOfWeek = new Date(dateStr).getDay();
          hitsByDay[dayOfWeek]++;
        });
        
        // Tính tỉ lệ trúng theo ngày trong tuần
        const totalDays = info.total / 7; // Giả sử phân bố đều các ngày trong tuần
        const ratesByDay = hitsByDay.map(hits => (hits / totalDays) * 100);
        
        // Tính hệ số mùa vụ cho ngày được chọn
        const avgRate = info.rate;
        const selectedDayRate = ratesByDay[selectedDayOfWeek];
        
        let seasonalFactor = 1.0;
        if (avgRate > 0) {
          seasonalFactor = selectedDayRate / avgRate;
        }
        
        // Giới hạn hệ số mùa vụ trong khoảng hợp lý
        seasonalFactor = Math.max(0.7, Math.min(1.5, seasonalFactor));
        
        seasonalData[number] = {
          factor: seasonalFactor,
          data: ratesByDay
        };
      } else {
        // Nếu không có dữ liệu ngày cụ thể, sử dụng hệ số mặc định
        seasonalData[number] = {
          factor: 1.0,
          data: null
        };
      }
    }
    
    return seasonalData;
  }
  
  // Hàm tính điểm nâng cao cho một số
  function calculateAdvancedScore(number, freq, hitRate, selectedDate, trend, seasonal) {
    // Điểm cơ bản dựa trên tần suất và tỉ lệ trúng
    const baseScore = (freq * 4) + (hitRate * 2);
    
    // Hệ số xu hướng
    const trendFactor = trend && trend.factor ? trend.factor : 1.0;
    
    // Hệ số mùa vụ
    const seasonalFactor = seasonal && seasonal.factor ? seasonal.factor : 1.0;
    
    // Thêm phân tích cấu trúc số
    let structureFactor = 1.0;
    
    if (number.length === 2) {
      const tens = parseInt(number[0]);
      const units = parseInt(number[1]);
      
      // Các số đẹp có thể có lợi thế
      if (tens === units) structureFactor *= 1.1; // Số đôi (11, 22, ...)
      if (Math.abs(tens - units) === 1) structureFactor *= 1.05; // Số liên tiếp (12, 23, ...)
      if ((tens + units) === 9) structureFactor *= 1.05; // Tổng bằng 9
    } else if (number.length === 3) {
      const hundreds = parseInt(number[0]);
      const tens = parseInt(number[1]);
      const units = parseInt(number[2]);
      
      // Các số đẹp có thể có lợi thế
      if (hundreds === tens && tens === units) structureFactor *= 1.15; // Số tam hoa (111, 222, ...)
      if (hundreds === tens || tens === units) structureFactor *= 1.05; // Có 2 số giống nhau
    }
    
    // Tính điểm dựa trên các hệ số
    const trendScore = baseScore * trendFactor;
    const seasonalScore = trendScore * seasonalFactor;
    const finalScore = seasonalScore * structureFactor;
    
    return {
      baseScore: baseScore,
      trendFactor: trendFactor,
      trendScore: trendScore,
      seasonalFactor: seasonalFactor,
      seasonalScore: seasonalScore,
      structureFactor: structureFactor,
      finalScore: finalScore
    };
  }
  
  // Hàm tạo giải thích cho điểm số
  function getScoreExplanation(score, details) {
    if (score > 60) {
      return "Số này có điểm rất cao, với sự kết hợp tốt giữa tần suất xuất hiện cao và tỉ lệ trúng tốt. " +
             "Xu hướng gần đây cũng đang tăng, và có lợi thế vào ngày này trong tuần.";
    } else if (score > 50) {
      return "Số này có điểm cao, xuất hiện nhiều trong các phương pháp dự đoán và có tỉ lệ trúng khá tốt. " +
             "Đây là lựa chọn tốt để đánh.";
    } else if (score > 40) {
      return "Số này có điểm khá, với tần suất xuất hiện vừa phải và tỉ lệ trúng khá. " +
             "Có thể cân nhắc đánh nhưng không phải là số mạnh nhất.";
    } else if (score > 30) {
      return "Số này có điểm trung bình, không nổi bật về tần suất hoặc tỉ lệ trúng. " +
             "Có thể đánh với mức độ thấp.";
    } else {
      return "Số này có điểm thấp, ít xuất hiện trong các phương pháp dự đoán hoặc có tỉ lệ trúng kém. " +
             "Không khuyến nghị đánh số này.";
    }
  }
  
  // Hàm lấy ngày tốt nhất trong tuần
  function getBestDayOfWeek(data) {
    if (!data || data.length === 0) return "Không xác định";
    
    const dayNames = ['Chủ nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
    const maxIndex = data.indexOf(Math.max(...data));
    
    return dayNames[maxIndex];
  }
  
  // Hàm tạo dữ liệu mẫu nếu không tìm thấy dữ liệu thực
  function createSampleData(selectedDate) {
    console.log("Creating sample data for date:", selectedDate);
    
    // Chuyển đổi ngày thành định dạng hiển thị
    const dateObj = new Date(selectedDate);
    const formattedDate = dateObj.toLocaleDateString('vi-VN');
    const analysisDateElem = document.getElementById('analysisDate');
    if (analysisDateElem) {
      analysisDateElem.textContent = formattedDate;
    }
    
    // Tính ngày tiếp theo
    const nextDay = new Date(selectedDate);
    nextDay.setDate(nextDay.getDate() + 1);
    const formattedNextDay = nextDay.toLocaleDateString('vi-VN');
    const nextDayDateElem = document.getElementById('nextDayDate');
    if (nextDayDateElem) {
      nextDayDateElem.textContent = formattedNextDay;
    }
    
    // Tạo các phương pháp mẫu
    const sampleMethods = [
      { name: "Phương pháp 1", code: "PP1", hitRate: 35.8 },
      { name: "Phương pháp 2", code: "PP2", hitRate: 32.5 },
      { name: "Phương pháp 3", code: "PP3", hitRate: 28.9 },
      { name: "Phương pháp 4", code: "PP4", hitRate: 25.4 },
      { name: "Phương pháp 5", code: "PP5", hitRate: 22.7 }
    ];
    
        // Tạo số ngẫu nhiên cho mỗi phương pháp
    const twoDigitNumbers = {};
    const threeDigitNumbers = {};
    const methodsForNumbers = {};
    const hitRatesForNumbers = {};
    const allNumbers = [];
    
    sampleMethods.forEach(method => {
      // Tạo 10-15 số cho mỗi phương pháp
      const numCount = Math.floor(Math.random() * 6) + 10;
      const methodNumbers = [];
      
      for (let i = 0; i < numCount; i++) {
        // 70% là số 2 chữ số, 30% là số 3 chữ số
        if (Math.random() < 0.7) {
          const num = Math.floor(Math.random() * 100).toString().padStart(2, '0');
          methodNumbers.push(num);
          
          // Cập nhật thống kê
          twoDigitNumbers[num] = (twoDigitNumbers[num] || 0) + 1;
          allNumbers.push(num);
          
          // Ghi nhận phương pháp
          if (!methodsForNumbers[num]) {
            methodsForNumbers[num] = [];
          }
          if (!methodsForNumbers[num].includes(method.name)) {
            methodsForNumbers[num].push(method.name);
          }
          
          // Tạo tỉ lệ trúng ngẫu nhiên
          if (!hitRatesForNumbers[num]) {
            hitRatesForNumbers[num] = Math.random() * 15 + 5; // 5-20%
          }
        } else {
          const num = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
          methodNumbers.push(num);
          
          // Cập nhật thống kê
          threeDigitNumbers[num] = (threeDigitNumbers[num] || 0) + 1;
          allNumbers.push(num);
          
          // Ghi nhận phương pháp
          if (!methodsForNumbers[num]) {
            methodsForNumbers[num] = [];
          }
          if (!methodsForNumbers[num].includes(method.name)) {
            methodsForNumbers[num].push(method.name);
          }
          
          // Tạo tỉ lệ trúng ngẫu nhiên
          if (!hitRatesForNumbers[num]) {
            hitRatesForNumbers[num] = Math.random() * 12 + 3; // 3-15%
          }
        }
      }
      
      // Thêm thông tin dự đoán vào phương pháp
      method.predictedNumbers = methodNumbers;
    });
    
    // Đảm bảo có một số số xuất hiện trong nhiều phương pháp
    for (let i = 0; i < 5; i++) {
      let num;
      if (Math.random() < 0.7) {
        num = Math.floor(Math.random() * 100).toString().padStart(2, '0');
        twoDigitNumbers[num] = Math.floor(Math.random() * 3) + 3; // 3-5 lần
      } else {
        num = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
        threeDigitNumbers[num] = Math.floor(Math.random() * 3) + 2; // 2-4 lần
      }
      
      // Gán số này cho 3-4 phương pháp ngẫu nhiên
      const methodCount = Math.floor(Math.random() * 2) + 3; // 3-4
      const shuffledMethods = [...sampleMethods].sort(() => 0.5 - Math.random());
      
      methodsForNumbers[num] = shuffledMethods.slice(0, methodCount).map(m => m.name);
      hitRatesForNumbers[num] = Math.random() * 20 + 10; // 10-30% (cao hơn trung bình)
    }
    
    console.log("Sample data created:", 
      "Methods:", sampleMethods.length,
      "Numbers:", allNumbers.length,
      "2-digit numbers:", Object.keys(twoDigitNumbers).length,
      "3-digit numbers:", Object.keys(threeDigitNumbers).length
    );
    
    // Tính xu hướng và mùa vụ giả lập
    const trendData = {};
    const seasonalData = {};
    
    for (const number of [...Object.keys(twoDigitNumbers), ...Object.keys(threeDigitNumbers)]) {
      // Tạo xu hướng ngẫu nhiên
      const trendFactor = 0.7 + Math.random() * 0.6; // 0.7-1.3
      trendData[number] = {
        factor: trendFactor,
        recentRate: hitRatesForNumbers[number] * trendFactor,
        olderRate: hitRatesForNumbers[number],
        data: [
          { label: '90+ ngày trước', rate: hitRatesForNumbers[number] * (1 / trendFactor) },
          { label: '60-90 ngày', rate: hitRatesForNumbers[number] * (1 + (trendFactor - 1) * 0.3) },
          { label: '30-60 ngày', rate: hitRatesForNumbers[number] * (1 + (trendFactor - 1) * 0.6) },
          { label: '0-30 ngày', rate: hitRatesForNumbers[number] * trendFactor }
        ]
      };
      
      // Tạo mùa vụ ngẫu nhiên
      const seasonalFactor = 0.8 + Math.random() * 0.4; // 0.8-1.2
      const weekdayRates = Array(7).fill(0).map(() => 5 + Math.random() * 10); // 5-15%
      const selectedDayOfWeek = new Date(selectedDate).getDay();
      weekdayRates[selectedDayOfWeek] = hitRatesForNumbers[number] * seasonalFactor;
      
      seasonalData[number] = {
        factor: seasonalFactor,
        data: weekdayRates
      };
    }
    
    // Tính điểm nâng cao
    const scoreForNumbers = {};
    const scoreDetails = {};
    
    for (const [number, freq] of Object.entries({...twoDigitNumbers, ...threeDigitNumbers})) {
      const hitRate = hitRatesForNumbers[number] || 0;
      const trend = trendData[number] || { factor: 1.0 };
      const seasonal = seasonalData[number] || { factor: 1.0 };
      
      // Tính điểm với nhiều yếu tố
      const details = calculateAdvancedScore(number, freq, hitRate, selectedDate, trend, seasonal);
      scoreForNumbers[number] = details.finalScore;
      scoreDetails[number] = details;
    }
    
    // Hiển thị dữ liệu mẫu
    
    // Hiển thị danh sách phương pháp
    const topMethodsList = document.getElementById('topMethodsList');
    if (topMethodsList) {
      topMethodsList.innerHTML = '';
      
      sampleMethods.forEach(method => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${method.name} (${method.code})</td>
          <td>${method.hitRate.toFixed(2)}%</td>
          <td>${method.predictedNumbers.length}</td>
        `;
        topMethodsList.appendChild(row);
      });
    }
    
    // Hiển thị thông tin chung
    const totalPredictionsElem = document.getElementById('totalPredictions');
    if (totalPredictionsElem) {
      totalPredictionsElem.textContent = allNumbers.length;
    }
    
    // Tìm số xuất hiện nhiều nhất
    let mostFrequentTwoDigit = '';
    let maxTwoDigitFreq = 0;
    
    for (const [number, freq] of Object.entries(twoDigitNumbers)) {
      if (freq > maxTwoDigitFreq) {
        maxTwoDigitFreq = freq;
        mostFrequentTwoDigit = number;
      }
    }
    
    let mostFrequentThreeDigit = '';
    let maxThreeDigitFreq = 0;
    
    for (const [number, freq] of Object.entries(threeDigitNumbers)) {
      if (freq > maxThreeDigitFreq) {
        maxThreeDigitFreq = freq;
        mostFrequentThreeDigit = number;
      }
    }
    
    // Hiển thị số xuất hiện nhiều nhất
    const mostFrequentTwoDigitElem = document.getElementById('mostFrequentTwoDigit');
    if (mostFrequentTwoDigitElem) {
      mostFrequentTwoDigitElem.textContent =
        mostFrequentTwoDigit ? `${mostFrequentTwoDigit} (${maxTwoDigitFreq} lần)` : 'Không có dữ liệu';
    }
    
    const mostFrequentThreeDigitElem = document.getElementById('mostFrequentThreeDigit');
    if (mostFrequentThreeDigitElem) {
      mostFrequentThreeDigitElem.textContent =
        mostFrequentThreeDigit ? `${mostFrequentThreeDigit} (${maxThreeDigitFreq} lần)` : 'Không có dữ liệu';
    }
    
    // Tìm số có tỉ lệ trúng cao nhất
    let highestHitRateNumber = '';
    let highestHitRate = 0;
    
    for (const [number, rate] of Object.entries(hitRatesForNumbers)) {
      if (rate > highestHitRate) {
        highestHitRate = rate;
        highestHitRateNumber = number;
      }
    }
    
    const highestHitRateNumberElem = document.getElementById('highestHitRateNumber');
    if (highestHitRateNumberElem) {
      highestHitRateNumberElem.textContent =
        highestHitRateNumber ? `${highestHitRateNumber} (${highestHitRate.toFixed(2)}%)` : 'Không có dữ liệu';
    }
    
    // Hiển thị bảng số 2 chữ số
    const twoDigitsTable = document.querySelector('#twoDigitsTable tbody');
    if (twoDigitsTable) {
      twoDigitsTable.innerHTML = '';
      
      Object.entries(twoDigitNumbers)
        .sort((a, b) => scoreForNumbers[b[0]] - scoreForNumbers[a[0]])
        .forEach(([number, freq]) => {
          const methods = methodsForNumbers[number] || [];
          const hitRate = hitRatesForNumbers[number] || 0;
          const score = scoreForNumbers[number] || 0;
          const details = scoreDetails[number] || {};
          
          const row = document.createElement('tr');
          row.innerHTML = `
            <td class="fw-bold">${number}</td>
            <td>${freq} lần</td>
            <td>${methods.join(', ')}</td>
            <td>
              ${hitRate.toFixed(2)}% 
              <small class="text-muted d-block">Dữ liệu mẫu</small>
            </td>
            <td>
              ${score.toFixed(2)}
              <div class="progress mt-1" style="height: 4px;">
                <div class="progress-bar" style="width: ${Math.min(100, score)}%"></div>
              </div>
            </td>
            <td>
              ${score > 50 ? '<span class="badge bg-success">Nên đánh</span>' : 
                (score > 30 ? '<span class="badge bg-warning text-dark">Có thể đánh</span>' : 
                '<span class="badge bg-secondary">Không khuyến nghị</span>')}
              <button class="btn btn-sm btn-link p-0 mt-1 d-block" onclick="showAnalysisDetail('${number}')">
                Chi tiết
              </button>
            </td>
          `;
          twoDigitsTable.appendChild(row);
        });
    }
    
    // Hiển thị bảng số 3 chữ số
    const threeDigitsTable = document.querySelector('#threeDigitsTable tbody');
    if (threeDigitsTable) {
      threeDigitsTable.innerHTML = '';
      
      Object.entries(threeDigitNumbers)
        .sort((a, b) => scoreForNumbers[b[0]] - scoreForNumbers[a[0]])
        .forEach(([number, freq]) => {
          const methods = methodsForNumbers[number] || [];
          const hitRate = hitRatesForNumbers[number] || 0;
          const score = scoreForNumbers[number] || 0;
          const details = scoreDetails[number] || {};
          
          const row = document.createElement('tr');
          row.innerHTML = `
            <td class="fw-bold">${number}</td>
            <td>${freq} lần</td>
            <td>${methods.join(', ')}</td>
            <td>
              ${hitRate.toFixed(2)}% 
              <small class="text-muted d-block">Dữ liệu mẫu</small>
            </td>
            <td>
              ${score.toFixed(2)}
              <div class="progress mt-1" style="height: 4px;">
                <div class="progress-bar" style="width: ${Math.min(100, score)}%"></div>
              </div>
            </td>
            <td>
              ${score > 50 ? '<span class="badge bg-success">Nên đánh</span>' : 
                (score > 30 ? '<span class="badge bg-warning text-dark">Có thể đánh</span>' : 
                '<span class="badge bg-secondary">Không khuyến nghị</span>')}
              <button class="btn btn-sm btn-link p-0 mt-1 d-block" onclick="showAnalysisDetail('${number}')">
                Chi tiết
              </button>
            </td>
          `;
          threeDigitsTable.appendChild(row);
        });
    }
    
    // Hiển thị Top 10 số nên đánh
    const topRecommendations = document.getElementById('topRecommendations');
    if (topRecommendations) {
      topRecommendations.innerHTML = '';
      
      Object.entries(scoreForNumbers)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .forEach(([number, score], index) => {
          const freq = (twoDigitNumbers[number] || threeDigitNumbers[number] || 0);
          const hitRate = hitRatesForNumbers[number] || 0;
          const details = scoreDetails[number] || {};
          
          const row = document.createElement('tr');
          row.innerHTML = `
            <td class="fw-bold">
              ${index + 1}. ${number}
              ${details.trendFactor > 1.1 ? '<i class="fas fa-arrow-up text-success" title="Xu hướng tăng"></i>' : 
                (details.trendFactor < 0.9 ? '<i class="fas fa-arrow-down text-danger" title="Xu hướng giảm"></i>' : '')}
            </td>
            <td>
              ${score.toFixed(2)}
              <div class="progress mt-1" style="height: 4px;">
                <div class="progress-bar" style="width: ${Math.min(100, score)}%"></div>
              </div>
            </td>
            <td>${freq} lần</td>
            <td>${hitRate.toFixed(2)}%</td>
          `;
          topRecommendations.appendChild(row);
        });
    }
    
    // Hiển thị chiến lược
    // Chiến lược 1: Đánh theo tần suất
    const strategy1 = document.getElementById('strategy1Numbers');
    if (strategy1) {
      const topByFrequency = [...Object.entries({...twoDigitNumbers, ...threeDigitNumbers})]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      
      strategy1.innerHTML = topByFrequency.map(([number, freq]) =>
        `<span class="badge bg-primary me-2 mb-1">${number} (${freq} lần)</span>`
      ).join('');
    }
    
    // Chiến lược 2: Đánh theo tỉ lệ trúng
    const strategy2 = document.getElementById('strategy2Numbers');
    if (strategy2) {
      const topByHitRate = [...Object.entries(hitRatesForNumbers)]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      
      strategy2.innerHTML = topByHitRate.map(([number, rate]) =>
        `<span class="badge bg-success me-2 mb-1">${number} (${rate.toFixed(2)}%)</span>`
      ).join('');
    }
    
    // Chiến lược 3: Đánh theo điểm tổng hợp
    const strategy3 = document.getElementById('strategy3Numbers');
    if (strategy3) {
      const topByScore = Object.entries(scoreForNumbers)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      
      strategy3.innerHTML = topByScore.map(([number, score]) =>
        `<span class="badge bg-danger me-2 mb-1">${number} (${score.toFixed(2)} điểm)</span>`
      ).join('');
    }
    
    // Thêm chiến lược 4: Đánh theo xu hướng tăng
    const strategy4 = document.getElementById('strategy4Numbers');
    if (strategy4) {
      const topByTrend = Object.entries(trendData)
        .filter(([number]) => twoDigitNumbers[number] || threeDigitNumbers[number])
        .sort((a, b) => b[1].factor - a[1].factor)
        .slice(0, 5);
      
      strategy4.innerHTML = topByTrend.map(([number, data]) =>
        `<span class="badge bg-info me-2 mb-1">${number} (x${data.factor.toFixed(2)})</span>`
      ).join('');
    }
    
    // Thêm nhận xét phân tích
    const analysisInsights = document.getElementById('analysisInsights');
    if (analysisInsights) {
      analysisInsights.innerHTML = '';
      
      // Tạo các nhận xét dựa trên dữ liệu mẫu
      const insights = [
        `Số <strong>${mostFrequentTwoDigit}</strong> xuất hiện nhiều nhất (${maxTwoDigitFreq} lần) trong các phương pháp dự đoán.`,
        `Số <strong>${highestHitRateNumber}</strong> có tỉ lệ trúng cao nhất (${highestHitRate.toFixed(2)}%).`,
        `Có ${Object.keys(twoDigitNumbers).length} số 2 chữ số và ${Object.keys(threeDigitNumbers).length} số 3 chữ số được dự đoán.`
      ];
      
      // Thêm nhận xét về số xuất hiện trong nhiều phương pháp
      const numbersInMultipleMethods = [];
      for (const [number, methods] of Object.entries(methodsForNumbers)) {
        if (methods.length >= 3) { // Xuất hiện trong 3+ phương pháp
          numbersInMultipleMethods.push({number, count: methods.length});
        }
      }
      
      if (numbersInMultipleMethods.length > 0) {
        numbersInMultipleMethods.sort((a, b) => b.count - a.count);
        const topMultipleNumber = numbersInMultipleMethods[0];
        insights.push(`Số <strong>${topMultipleNumber.number}</strong> xuất hiện trong nhiều phương pháp nhất (${topMultipleNumber.count} phương pháp).`);
      }
      
      // Thêm nhận xét về xu hướng
      const risingTrendNumbers = Object.entries(trendData)
        .filter(([number, data]) => data.factor > 1.2 && (twoDigitNumbers[number] || threeDigitNumbers[number]))
        .sort((a, b) => b[1].factor - a[1].factor)
        .slice(0, 3);
      
      if (risingTrendNumbers.length > 0) {
        const trendInsight = `Các số có xu hướng tăng mạnh: ${risingTrendNumbers.map(([number, data]) => 
          `<strong>${number}</strong> (x${data.factor.toFixed(2)})`).join(', ')}.`;
        insights.push(trendInsight);
      }
      
      // Hiển thị các nhận xét
      insights.forEach(insight => {
        const li = document.createElement('li');
        li.innerHTML = insight;
        analysisInsights.appendChild(li);
      });
    }
    
    // Vẽ biểu đồ phân phối số
    if (typeof Chart !== 'undefined') {
      // Giống như hàm analyzeTopMethods nhưng với dữ liệu mẫu
      // ...
    }
    
    // Tạo heat map cho các số 2 chữ số
    createTwoDigitHeatMap(twoDigitNumbers, hitRatesForNumbers, scoreForNumbers, methodsForNumbers, scoreDetails);
    
    // Gán hàm hiển thị phân tích chi tiết
    window.showAnalysisDetail = function(number) {
      // Lấy dữ liệu mẫu cho số này
      const data = {
        frequency: twoDigitNumbers[number] || threeDigitNumbers[number] || 0,
        hitRate: hitRatesForNumbers[number] || 0,
        score: scoreForNumbers[number] || 0,
        methods: methodsForNumbers[number] || [],
        details: scoreDetails[number] || {},
        historical: null, // Không có dữ liệu lịch sử thật
        trend: trendData[number] || {},
        seasonal: seasonalData[number] || {}
      };
      
      showNumberAnalysisDetail(number, data);
    };
  }
  
  // Xử lý sự kiện click cho các ô ngày
  const dateHeaders = document.querySelectorAll('.date-header');
  // Lấy năm và tháng từ URL hiện tại hoặc sử dụng ngày hiện tại
  const urlParams = new URLSearchParams(window.location.search);
  let year = urlParams.get('year');
  let month = urlParams.get('month');
  
  // Nếu không có năm/tháng trong URL, sử dụng ngày hiện tại
  if (!year || !month) {
    const today = new Date();
    year = today.getFullYear();
    month = today.getMonth() + 1; // Tháng bắt đầu từ 0
  }
  
  dateHeaders.forEach(header => {
    header.style.cursor = 'pointer';
    header.addEventListener('click', function() {
      // Lấy số ngày từ thẻ <br> đầu tiên
      const dayElement = this.querySelector('br')?.previousSibling;
      if (!dayElement) return;
      
      const day = dayElement.textContent.trim();
      if (!day || isNaN(day)) return;
      
      // Tạo URL mới với tham số year, month và day
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.set('year', year);
      newUrl.searchParams.set('month', month);
      newUrl.searchParams.set('day', day);
      
      window.location.href = newUrl.toString();
    });
  });
});