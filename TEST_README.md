# 🧪 Test Suite cho Hàm loadMethodAnalysis()

## 📋 Tổng quan

Test suite này được thiết kế để kiểm tra toàn diện hàm `loadMethodAnalysis()` trong JavaScript theo từng bước logic một cách kỹ lưỡng.

## 🎯 Phạm vi Test

### Phase 1: Input Validation (📋)
- ✅ Kiểm tra khi input date trống
- ✅ Kiểm tra khi input date null/undefined
- ✅ Kiểm tra khi input có whitespace
- ✅ Kiểm tra khi DOM element không tồn tại
- ✅ Kiểm tra khi có valid date

### Phase 2: API Call Setup (🌐)
- ✅ Kiểm tra URL construction đúng format
- ✅ Kiểm tra parameters được append chính xác
- ✅ Kiểm tra loading state được hiển thị
- ✅ Kiểm tra currentAnalysisDate được set
- ✅ Kiểm tra debug logging

### Phase 3: Response Validation (📡)
- ✅ Kiểm tra HTTP status code validation
- ✅ Kiểm tra Content-Type header validation
- ✅ Kiểm tra response logging cho debugging
- ✅ Kiểm tra các trường hợp edge case headers

### Phase 4: Data Processing (📊)
- ✅ Kiểm tra data structure validation
- ✅ Kiểm tra success response handling
- ✅ Kiểm tra error response handling
- ✅ Kiểm tra invalid/null data handling
- ✅ Kiểm tra renderAnalysisResults được gọi đúng

### Phase 5: Error Handling (❌)
- ✅ Kiểm tra network errors
- ✅ Kiểm tra JSON parsing errors
- ✅ Kiểm tra HTTP error codes (404, 500)
- ✅ Kiểm tra generic errors
- ✅ Kiểm tra error logging
- ✅ Kiểm tra loading state cleanup

### Phase 6: Integration & Flow (🔄)
- ✅ Kiểm tra complete happy path
- ✅ Kiểm tra complete error path
- ✅ Kiểm tra multiple rapid calls
- ✅ Kiểm tra state consistency

### Phase 7: Edge Cases & Boundary (🎯)
- ✅ Kiểm tra very long date strings
- ✅ Kiểm tra special characters
- ✅ Kiểm tra DOM changes during execution
- ✅ Kiểm tra unexpected response properties
- ✅ Kiểm tra extremely large response data

### Phase 8: Mock Validation (🔧)
- ✅ Kiểm tra all mocks được setup đúng
- ✅ Kiểm tra mock functions called correctly
- ✅ Kiểm tra mock reset between tests

## 🚀 Cách chạy Tests

### Option 1: Node.js với Jest (Recommended)

```bash
# 1. Cài đặt dependencies
npm install

# 2. Chạy tất cả tests
npm test

# 3. Chạy tests với coverage
npm run test:coverage

# 4. Chạy tests trong watch mode
npm run test:watch

# 5. Chạy chỉ tests cho loadMethodAnalysis
npm run test:loadMethodAnalysis

# 6. Chạy tests với verbose output
npm run test:verbose
```

### Option 2: Browser Test Runner

```bash
# Mở file HTML test runner trong browser
open predictions_tracker/static/js/test/test-runner.html
```

Hoặc serve qua HTTP server:
```bash
# Python 3
python -m http.server 8000

# Sau đó truy cập: http://localhost:8000/predictions_tracker/static/js/test/test-runner.html
```

## 📊 Cấu trúc Files

```
predictions_tracker/
├── static/js/test/
│   ├── loadMethodAnalysis.test.js    # Main test file
│   ├── setup.js                      # Test setup utilities
│   └── test-runner.html             # Browser test runner
├── jest.config.js                   # Jest configuration
└── package.json                     # NPM dependencies & scripts
```

## 🔧 Test Configuration

### Jest Configuration (jest.config.js)
```javascript
{
  testEnvironment: 'jsdom',
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
}
```

### Coverage Reports
- Text: Console output
- HTML: `coverage/lcov-report/index.html`
- LCOV: `coverage/lcov.info`

## 🎯 Test Examples

### Input Validation Test
```javascript
test('1.1 - Should show error when date input is empty', () => {
    // Arrange
    mockDateInput.value = '';
    
    // Act
    loadMethodAnalysis();
    
    // Assert
    expect(mockShowError).toHaveBeenCalledWith('Vui lòng chọn ngày phân tích');
    expect(mockShowLoading).not.toHaveBeenCalled();
    expect(mockFetch).not.toHaveBeenCalled();
});
```

### API Call Test
```javascript
test('2.1 - Should construct correct API URL', () => {
    // Arrange
    const testDate = '2025-07-31';
    mockDateInput.value = testDate;
    
    // Act
    loadMethodAnalysis();
    
    // Assert
    const expectedUrl = `/pre-lokhung/api/method-analysis-v2/?analysis_date=${testDate}&limit=15`;
    expect(mockFetch).toHaveBeenCalledWith(expectedUrl);
});
```

### Error Handling Test
```javascript
test('5.1 - Should handle network fetch failure', async () => {
    // Arrange
    mockFetch.mockRejectedValue(new Error('Failed to fetch'));
    
    // Act
    loadMethodAnalysis();
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // Assert
    expect(mockHideLoading).toHaveBeenCalled();
    expect(mockShowError).toHaveBeenCalledWith('Không thể kết nối đến server');
});
```

## 📈 Test Results Interpretation

### Coverage Metrics
- **Branches**: Tất cả if/else paths được test
- **Functions**: Tất cả functions được gọi
- **Lines**: Tất cả lines code được execute
- **Statements**: Tất cả statements được evaluate

### Test Status
- ✅ **PASS**: Test passed successfully
- ❌ **FAIL**: Test failed with error details
- ⏳ **PENDING**: Test skipped or not implemented

## 🐛 Debugging Tests

### Console Output
```bash
# Debug mode với breakpoints
npm run test:debug

# Silent mode (ít output)
npm run test:silent

# Bail on first failure
npm run test:bail
```

### Browser Debugging
1. Mở `test-runner.html` trong browser
2. Mở Developer Tools (F12)
3. Xem Console tab cho detailed logs
4. Sử dụng breakpoints trong Sources tab

## 🔍 Mock Objects

### Available Mocks
```javascript
// Function mocks
mockShowError()
mockShowLoading() 
mockHideLoading()
mockRenderAnalysisResults()
mockFetch()

// DOM mocks
mockDocument.getElementById()
mockDateInput.value

// Console mocks
mockConsole.log()
mockConsole.error()
```

### Mock Utilities
```javascript
// Reset mocks
mockFunction.mockClear()

// Set return values
mockFunction.mockReturnValue(value)
mockFunction.mockResolvedValue(promise)
mockFunction.mockRejectedValue(error)

// Check calls
expect(mockFunction).toHaveBeenCalled()
expect(mockFunction).toHaveBeenCalledWith(args)
expect(mockFunction).toHaveBeenCalledTimes(count)
```

## 📝 Adding New Tests

### Test Template
```javascript
test('X.Y - Test description', async () => {
    // Arrange
    resetMocks();
    // Setup test data
    
    // Act
    const result = await loadMethodAnalysis();
    
    // Assert
    expect(result).toBeDefined();
    expect(mockFunction).toHaveBeenCalled();
});
```

### Best Practices
1. **Arrange-Act-Assert** pattern
2. Reset mocks before each test
3. Use descriptive test names
4. Test both positive and negative cases
5. Include async/await for promise-based tests
6. Verify all side effects (function calls, state changes)

## 🎉 Test Results

Khi chạy thành công, bạn sẽ thấy:
```
✅ 45 tests passed
📊 Coverage: 95%+ on all metrics
⏱️  Duration: ~2-5 seconds
🎯 0 failing tests
```

## 🚨 Troubleshooting

### Common Issues
1. **"fetch is not defined"**: Đảm bảo đã setup jsdom environment
2. **"Mock not reset"**: Gọi `jest.clearAllMocks()` trong beforeEach
3. **"Async test timeout"**: Thêm `await` cho promises
4. **"Module not found"**: Kiểm tra import paths trong test files

### Solutions
```javascript
// Fix fetch undefined
global.fetch = jest.fn();

// Fix async issues
await new Promise(resolve => setTimeout(resolve, 0));

// Fix mock issues
beforeEach(() => {
    jest.clearAllMocks();
});
```

## 📞 Support

Nếu gặp vấn đề với test suite:
1. Check console logs cho error details
2. Verify all dependencies installed correctly
3. Ensure test environment setup properly
4. Review mock configurations

---

**Happy Testing! 🧪✨**
