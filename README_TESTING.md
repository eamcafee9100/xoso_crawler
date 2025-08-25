# 🤖 Automated JavaScript Testing Suite

**Hệ thống test tự động toàn diện cho loadMethodAnalysis() function**

## 📋 Tổng Quan

Dự án này cung cấp một bộ test tự động hoàn chỉnh cho hàm JavaScript `loadMethodAnalysis()` với các tính năng:

- ✅ **Jest Testing Framework** - Test runner chuyên nghiệp
- 🌐 **Browser Test Runner** - Test trực tiếp trên browser
- 📊 **Coverage Report** - Báo cáo độ phủ code chi tiết
- 🤖 **Automated Scripts** - Script tự động chạy và sửa lỗi
- 🔧 **Auto-Fix Capabilities** - Tự động sửa các lỗi phổ biến

## 📁 Cấu Trúc File

```
├── jest.config.js                           # Cấu hình Jest
├── package.json                             # Dependencies và scripts
├── babel.config.js                          # Cấu hình Babel
├── auto-test.js                             # Script test tự động (full)
├── simple-test.js                           # Script test đơn giản
├── open-tests.js                            # Script mở browser tests
├── run-test.bat                             # Windows batch script
├── run-test.ps1                             # PowerShell script
└── predictions_tracker/static/js/test/
    ├── setup.js                             # Cấu hình test environment
    ├── loadMethodAnalysis.test.js           # Test chính (1150+ dòng)
    └── test-runner.html                     # Browser test runner
```

## 🚀 Cách Sử Dụng

### 1. Quick Start (Khuyến nghị)

```bash
# Chạy test đơn giản
node simple-test.js

# Mở browser tests
node open-tests.js
```

### 2. Script Tự Động Đầy Đủ

```bash
# Auto mode (không cần tương tác)
node auto-test.js --auto

# Interactive mode (từng bước)
node auto-test.js

# Chỉ xem help
node auto-test.js --help
```

### 3. Windows Scripts

```cmd
:: Command prompt
run-test.bat

:: PowerShell
.\run-test.ps1

:: PowerShell với tham số
.\run-test.ps1 -Auto
```

### 4. NPM Commands

```bash
# Chạy tất cả tests
npm test

# Chạy với coverage
npm run test:coverage

# Chạy test cụ thể
npm run test:loadMethodAnalysis

# Watch mode (tự động chạy lại khi file thay đổi)
npm run test:watch

# Debug mode
npm run test:debug
```

## 📊 Test Coverage

Hệ thống test bao gồm **8 phases** với **45+ test cases**:

### Phase 1: Input Validation ✅
- Empty input handling
- Null/undefined checks
- Whitespace validation
- Valid input processing
- Element not found scenarios

### Phase 2: API Call Setup ✅
- URL construction
- Logging validation
- Loading state management
- Date setting verification

### Phase 3: Response Validation ✅
- HTTP status codes
- Content-type headers
- Response structure validation
- Error response handling

### Phase 4: Data Processing ✅
- Data structure validation
- Success response handling
- Error message processing
- Non-object data handling

### Phase 5: Error Handling ✅
- Network failures
- JSON parsing errors
- HTTP error codes (404, 500)
- Generic error scenarios
- Loading state cleanup

### Phase 6: Integration Tests ✅
- Complete happy path flow
- Complete error path flow
- Multiple rapid calls
- State consistency

### Phase 7: Edge Cases ✅
- Very long date strings
- Special characters
- DOM element changes
- Unexpected response properties
- Large response data

### Phase 8: Mock Validation ✅
- Mock function verification
- Call count validation
- Reset functionality

## 🌐 Browser Test Runner

File `test-runner.html` cung cấp:

- 🎨 **Bootstrap UI** - Giao diện đẹp và responsive
- ▶️ **Interactive Controls** - Chạy test từng phase hoặc tất cả
- 📊 **Real-time Results** - Kết quả test hiển thị ngay lập tức
- 📄 **Export Results** - Xuất kết quả ra file JSON/HTML
- 🔍 **Detailed Logging** - Log chi tiết từng bước thực hiện

### Cách sử dụng Browser Test:

1. Chạy `node open-tests.js` hoặc
2. Mở trực tiếp: `predictions_tracker/static/js/test/test-runner.html`
3. Click "Run All Tests" hoặc chọn phase cụ thể
4. Xem kết quả real-time

## 🔧 Auto-Fix Features

Script `auto-test.js` có khả năng tự động sửa các lỗi:

- 📦 **Dependencies** - Tự động cài đặt packages thiếu
- ⚙️ **Configuration** - Sửa Jest và Babel config
- 🌐 **JSDOM Setup** - Cấu hình DOM environment
- 🎭 **Mock Issues** - Sửa các vấn đề về mocking
- 📝 **Syntax Errors** - Sửa lỗi cú pháp cơ bản

## 📈 Coverage Reports

Sau khi chạy test, mở coverage report:

```bash
# Tự động mở coverage report
node open-tests.js

# Or manually open
open coverage/lcov-report/index.html
```

Coverage report bao gồm:
- **Line Coverage** - Tỷ lệ dòng code được test
- **Branch Coverage** - Tỷ lệ nhánh logic được test  
- **Function Coverage** - Tỷ lệ functions được test
- **Statement Coverage** - Tỷ lệ statements được test

## 🎯 Testing Targets

### Coverage Thresholds:
- **Lines**: 70%
- **Functions**: 70%
- **Branches**: 70% 
- **Statements**: 70%

### Test Environment:
- **Node.js**: 14+ 
- **Jest**: 29.6.0
- **JSDOM**: DOM simulation
- **Babel**: ES6+ transpilation

## 🐛 Troubleshooting

### Common Issues:

1. **"Module not found"**
   ```bash
   npm install
   ```

2. **"Jest configuration conflict"**
   - Chỉ sử dụng `jest.config.js`, xóa jest config trong `package.json`

3. **"DOM element not found"**
   - Kiểm tra setup.js đã tạo mock elements chưa

4. **"Tests timeout"**
   - Tăng timeout trong jest.config.js: `testTimeout: 10000`

### Debug Commands:

```bash
# Debug với Node inspector
npm run test:debug

# Chạy với verbose output
npm run test:verbose

# Clear Jest cache
npx jest --clearCache

# Run with specific pattern
npx jest --testNamePattern="Phase 1"
```

## 📚 Advanced Usage

### Custom Test Scenarios:

1. **Thêm test cases mới** trong `loadMethodAnalysis.test.js`
2. **Modify mock behaviors** trong setup.js
3. **Adjust coverage thresholds** trong jest.config.js
4. **Add new test phases** theo pattern có sẵn

### Integration với CI/CD:

```yaml
# GitHub Actions example
- name: Run Tests
  run: |
    npm install
    npm test
    npm run test:coverage
```

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch
3. Thêm tests cho code mới
4. Ensure coverage >= 70%
5. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

---

## 🎉 Kết Luận

Hệ thống test này cung cấp:

- ✅ **Comprehensive Testing** - Test toàn diện mọi khía cạnh
- 🤖 **Automation** - Tự động hóa hoàn toàn
- 🔧 **Self-Healing** - Tự sửa lỗi phổ biến
- 📊 **Detailed Reports** - Báo cáo chi tiết
- 🌐 **Multiple Interfaces** - CLI và Browser
- 🚀 **Easy Setup** - Cài đặt đơn giản

**Happy Testing! 🎯**
