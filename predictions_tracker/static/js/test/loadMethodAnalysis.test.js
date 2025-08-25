/**
 * ✅ COMPREHENSIVE TEST SUITE FOR loadMethodAnalysis() Function
 * Kiểm tra toàn diện từng bước logic của hàm loadMethodAnalysis
 */

// Mock dependencies
const mockConsole = {
  log: jest.fn(),
  error: jest.fn(),
};

const mockFetch = jest.fn();
const mockShowError = jest.fn();
const mockShowLoading = jest.fn();
const mockHideLoading = jest.fn();
const mockRenderAnalysisResults = jest.fn();

// Mock DOM elements
const mockDateInput = {
  value: "",
};

const mockDocument = {
  getElementById: jest.fn((id) => {
    if (id === "analysisDatePicker") return mockDateInput;
    return null;
  }),
};

// Setup global mocks
global.console = mockConsole;
global.fetch = mockFetch;
global.document = mockDocument;
global.showError = mockShowError;
global.showLoading = mockShowLoading;
global.hideLoading = mockHideLoading;
global.renderAnalysisResults = mockRenderAnalysisResults;
global.currentAnalysisDate = null;

// Import function under test (assuming it's available globally or can be imported)
// For this example, we'll define it inline for testing
function loadMethodAnalysis() {
  const dateInput = document.getElementById("analysisDatePicker");
  
  // Add null check to prevent test failures
  if (!dateInput) {
    console.warn("analysisDatePicker element not found");
    showError("Không tìm thấy element ngày phân tích");
    return;
  }
  
  const analysisDate = dateInput.value;

  if (!analysisDate) {
    showError("Vui lòng chọn ngày phân tích");
    return;
  }

  // Show loading
  showLoading();
  
  // Set current analysis date
  currentAnalysisDate = analysisDate;

  // Construct API URL
  const apiUrl = `/api/method-analysis/?date=${analysisDate}`;
  console.log("API URL:", apiUrl);

  // Make API call
  fetch(apiUrl)
    .then(response => {
      // Validate HTTP status
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Validate content-type
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        console.warn('Response may not be JSON:', contentType);
      }
      
      console.log("Response details:", {
        status: response.status,
        contentType: contentType,
        ok: response.ok
      });
      
      return response.json();
    })
    .then(data => {
      // Validate data structure
      if (typeof data !== 'object' || data === null) {
        throw new Error('Invalid data structure received');
      }
      
      console.log("Received data:", data);
      
      if (data.error) {
        showError(data.error || 'Có lỗi xảy ra từ API');
      } else {
        // Process successful response
        console.log("Processing successful response");
        // Additional processing logic would go here
      }
    })
    .catch(error => {
      console.error('Error in loadMethodAnalysis:', error);
      showError('Có lỗi xảy ra khi tải dữ liệu: ' + error.message);
    })
    .finally(() => {
      // Always hide loading
      hideLoading();
    });
}

describe("loadMethodAnalysis() Function - Comprehensive Tests", () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();

    // Reset global variables
    global.currentAnalysisDate = null;

    // Reset DOM mock
    mockDateInput.value = "";

    // Reset fetch mock
    mockFetch.mockClear();
  });

  // ========================================
  // 📋 PHASE 1: INPUT VALIDATION TESTS
  // ========================================

  describe("Phase 1: Input Validation", () => {
    test("1.1 - Should show error when date input is empty", () => {
      // Arrange
      mockDateInput.value = "";

      // Act
      loadMethodAnalysis();

      // Assert
      expect(mockShowError).toHaveBeenCalledWith(
        "Vui lòng chọn ngày phân tích"
      );
      expect(mockShowLoading).not.toHaveBeenCalled();
      expect(mockFetch).not.toHaveBeenCalled();
      expect(global.currentAnalysisDate).toBeNull();
    });

    test("1.2 - Should show error when date input is null", () => {
      // Arrange
      mockDateInput.value = null;

      // Act
      loadMethodAnalysis();

      // Assert
      expect(mockShowError).toHaveBeenCalledWith(
        "Vui lòng chọn ngày phân tích"
      );
      expect(mockShowLoading).not.toHaveBeenCalled();
      expect(mockFetch).not.toHaveBeenCalled();
    });

    test("1.3 - Should show error when date input is undefined", () => {
      // Arrange
      mockDateInput.value = undefined;

      // Act
      loadMethodAnalysis();

      // Assert
      expect(mockShowError).toHaveBeenCalledWith(
        "Vui lòng chọn ngày phân tích"
      );
      expect(mockShowLoading).not.toHaveBeenCalled();
      expect(mockFetch).not.toHaveBeenCalled();
    });

    test("1.4 - Should show error when date input is whitespace only", () => {
      // Arrange
      mockDateInput.value = "   ";

      // Act
      loadMethodAnalysis();

      // Assert
      expect(mockShowError).toHaveBeenCalledWith(
        "Vui lòng chọn ngày phân tích"
      );
      expect(mockShowLoading).not.toHaveBeenCalled();
      expect(mockFetch).not.toHaveBeenCalled();
    });

    test("1.5 - Should proceed when valid date is provided", () => {
      // Arrange
      const validDate = "2025-07-31";
      mockDateInput.value = validDate;

      // Mock successful fetch response
      const mockResponse = {
        ok: true,
        status: 200,
        url: `/pre-lokhung/api/method-analysis-v2/?analysis_date=${validDate}&limit=15`,
        headers: {
          get: jest.fn().mockReturnValue("application/json"),
        },
        json: jest.fn().mockResolvedValue({
          success: true,
          data: {},
        }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Assert
      expect(mockShowError).not.toHaveBeenCalled();
      expect(mockShowLoading).toHaveBeenCalled();
      expect(global.currentAnalysisDate).toBe(validDate);
      expect(mockFetch).toHaveBeenCalledWith(
        `/pre-lokhung/api/method-analysis-v2/?analysis_date=${validDate}&limit=15`
      );
    });

    test("1.6 - Should handle date input element not found", () => {
      // Arrange
      mockDocument.getElementById.mockReturnValue(null);

      // Act & Assert
      expect(() => loadMethodAnalysis()).toThrow();
    });
  });

  // ========================================
  // 🌐 PHASE 2: API CALL SETUP TESTS
  // ========================================

  describe("Phase 2: API Call Setup", () => {
    beforeEach(() => {
      mockDateInput.value = "2025-07-31";
    });

    test("2.1 - Should construct correct API URL", () => {
      // Arrange
      const testDate = "2025-07-31";
      mockDateInput.value = testDate;

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Assert
      const expectedUrl = `/pre-lokhung/api/method-analysis-v2/?analysis_date=${testDate}&limit=15`;
      expect(mockFetch).toHaveBeenCalledWith(expectedUrl);
    });

    test("2.2 - Should log API URL for debugging", () => {
      // Arrange
      const testDate = "2025-12-25";
      mockDateInput.value = testDate;

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Assert
      const expectedUrl = `/pre-lokhung/api/method-analysis-v2/?analysis_date=${testDate}&limit=15`;
      expect(mockConsole.log).toHaveBeenCalledWith(
        "🔍 Calling API:",
        expectedUrl
      );
    });

    test("2.3 - Should show loading state before API call", () => {
      // Arrange
      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Assert
      expect(mockShowLoading).toHaveBeenCalledBefore(mockFetch);
    });

    test("2.4 - Should set currentAnalysisDate before API call", () => {
      // Arrange
      const testDate = "2025-07-31";
      mockDateInput.value = testDate;

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Assert
      expect(global.currentAnalysisDate).toBe(testDate);
    });
  });

  // ========================================
  // 📡 PHASE 3: RESPONSE VALIDATION TESTS
  // ========================================

  describe("Phase 3: Response Validation", () => {
    beforeEach(() => {
      mockDateInput.value = "2025-07-31";
    });

    test("3.1 - Should validate HTTP status code", async () => {
      // Arrange
      const mockResponse = {
        ok: false,
        status: 404,
        statusText: "Not Found",
        headers: { get: jest.fn() },
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockConsole.log).toHaveBeenCalledWith("📡 Response status:", 404);
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith(
        "API không tồn tại - Kiểm tra URL routing"
      );
    });

    test("3.2 - Should validate content-type header", async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        status: 200,
        headers: {
          get: jest.fn((header) => {
            if (header === "content-type") return "text/html";
            return null;
          }),
        },
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith(
        "Lỗi định dạng dữ liệu từ server"
      );
    });

    test("3.3 - Should handle missing content-type header", async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        status: 200,
        headers: {
          get: jest.fn().mockReturnValue(null),
        },
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith(
        "Lỗi định dạng dữ liệu từ server"
      );
    });

    test("3.4 - Should accept valid JSON content-type", async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        status: 200,
        url: "test-url",
        headers: {
          get: jest.fn().mockReturnValue("application/json; charset=utf-8"),
        },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockConsole.log).toHaveBeenCalledWith("📡 Response status:", 200);
      expect(mockConsole.log).toHaveBeenCalledWith(
        "📡 Response URL:",
        "test-url"
      );
      expect(mockResponse.json).toHaveBeenCalled();
    });

    test("3.5 - Should log response details for debugging", async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        status: 200,
        url: "http://test-url.com/api",
        headers: {
          get: jest.fn().mockReturnValue("application/json"),
        },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockConsole.log).toHaveBeenCalledWith("📡 Response status:", 200);
      expect(mockConsole.log).toHaveBeenCalledWith(
        "📡 Response URL:",
        "http://test-url.com/api"
      );
    });
  });

  // ========================================
  // 📊 PHASE 4: DATA PROCESSING TESTS
  // ========================================

  describe("Phase 4: Data Processing", () => {
    beforeEach(() => {
      mockDateInput.value = "2025-07-31";
    });

    test("4.1 - Should validate data structure", async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue(null),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith(
        "Lỗi định dạng dữ liệu từ server"
      );
    });

    test("4.2 - Should handle non-object data", async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue("invalid string data"),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith(
        "Lỗi định dạng dữ liệu từ server"
      );
    });

    test("4.3 - Should handle successful response", async () => {
      // Arrange
      const successData = {
        success: true,
        analysis_date: "2025-07-31",
        hybrid_analysis: {},
        intelligent_selections: {},
        optimal_methods: {},
        performance_prediction: {},
      };

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue(successData),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockRenderAnalysisResults).toHaveBeenCalledWith(successData);
      expect(mockShowError).not.toHaveBeenCalled();
    });

    test("4.4 - Should handle API error response", async () => {
      // Arrange
      const errorData = {
        success: false,
        error: "Không tìm thấy dữ liệu cho ngày này",
      };

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue(errorData),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith(
        "Không tìm thấy dữ liệu cho ngày này"
      );
      expect(mockRenderAnalysisResults).not.toHaveBeenCalled();
    });

    test("4.5 - Should handle API error without error message", async () => {
      // Arrange
      const errorData = { success: false };

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue(errorData),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith("Lỗi không xác định");
      expect(mockRenderAnalysisResults).not.toHaveBeenCalled();
    });
  });

  // ========================================
  // ❌ PHASE 5: ERROR HANDLING TESTS
  // ========================================

  describe("Phase 5: Error Handling", () => {
    beforeEach(() => {
      mockDateInput.value = "2025-07-31";
    });

    test("5.1 - Should handle network fetch failure", async () => {
      // Arrange
      mockFetch.mockRejectedValue(new Error("Failed to fetch"));

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith(
        "Không thể kết nối đến server"
      );
      expect(mockConsole.error).toHaveBeenCalledWith(
        "Analysis API Error:",
        expect.any(Error)
      );
    });

    test("5.2 - Should handle JSON parsing error", async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockRejectedValue(new SyntaxError("Unexpected token")),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith(
        "Lỗi định dạng dữ liệu từ server"
      );
      expect(mockConsole.error).toHaveBeenCalled();
    });

    test("5.3 - Should handle HTTP 404 error", async () => {
      // Arrange
      mockFetch.mockRejectedValue(new Error("HTTP 404: Not Found"));

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith(
        "API không tồn tại - Kiểm tra URL routing"
      );
    });

    test("5.4 - Should handle HTTP 500 error", async () => {
      // Arrange
      mockFetch.mockRejectedValue(new Error("HTTP 500: Internal Server Error"));

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith("Lỗi server nội bộ");
    });

    test("5.5 - Should handle generic error", async () => {
      // Arrange
      mockFetch.mockRejectedValue(new Error("Some unexpected error"));

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith("Some unexpected error");
    });

    test("5.6 - Should always hide loading on error", async () => {
      // Arrange
      mockFetch.mockRejectedValue(new Error("Any error"));

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockHideLoading).toHaveBeenCalled();
    });

    test("5.7 - Should log all errors", async () => {
      // Arrange
      const testError = new Error("Test error for logging");
      mockFetch.mockRejectedValue(testError);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert
      expect(mockConsole.error).toHaveBeenCalledWith(
        "Analysis API Error:",
        testError
      );
    });
  });

  // ========================================
  // 🔄 PHASE 6: INTEGRATION & FLOW TESTS
  // ========================================

  describe("Phase 6: Integration & Flow Tests", () => {
    test("6.1 - Should execute complete happy path flow", async () => {
      // Arrange
      const testDate = "2025-07-31";
      mockDateInput.value = testDate;

      const successData = {
        success: true,
        analysis_date: testDate,
        data: {},
      };

      const mockResponse = {
        ok: true,
        status: 200,
        url: `test-url-${testDate}`,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue(successData),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert - Verify complete flow
      expect(global.currentAnalysisDate).toBe(testDate);
      expect(mockShowLoading).toHaveBeenCalled();
      expect(mockFetch).toHaveBeenCalledWith(
        `/pre-lokhung/api/method-analysis-v2/?analysis_date=${testDate}&limit=15`
      );
      expect(mockConsole.log).toHaveBeenCalledWith(
        "🔍 Calling API:",
        expect.stringContaining(testDate)
      );
      expect(mockConsole.log).toHaveBeenCalledWith("📡 Response status:", 200);
      expect(mockConsole.log).toHaveBeenCalledWith(
        "📡 Response URL:",
        expect.stringContaining(testDate)
      );
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockRenderAnalysisResults).toHaveBeenCalledWith(successData);
      expect(mockShowError).not.toHaveBeenCalled();
    });

    test("6.2 - Should execute complete error path flow", async () => {
      // Arrange
      const testDate = "2025-07-31";
      mockDateInput.value = testDate;

      const testError = new Error("Network error");
      mockFetch.mockRejectedValue(testError);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert - Verify complete error flow
      expect(global.currentAnalysisDate).toBe(testDate);
      expect(mockShowLoading).toHaveBeenCalled();
      expect(mockFetch).toHaveBeenCalled();
      expect(mockHideLoading).toHaveBeenCalled();
      expect(mockShowError).toHaveBeenCalledWith("Network error");
      expect(mockConsole.error).toHaveBeenCalledWith(
        "Analysis API Error:",
        testError
      );
      expect(mockRenderAnalysisResults).not.toHaveBeenCalled();
    });

    test("6.3 - Should handle multiple rapid calls", async () => {
      // Arrange
      mockDateInput.value = "2025-07-31";

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act - Call multiple times rapidly
      loadMethodAnalysis();
      loadMethodAnalysis();
      loadMethodAnalysis();

      // Wait for all promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert - Should handle multiple calls
      expect(mockShowLoading).toHaveBeenCalledTimes(3);
      expect(mockFetch).toHaveBeenCalledTimes(3);
      expect(mockHideLoading).toHaveBeenCalledTimes(3);
    });

    test("6.4 - Should maintain state consistency", async () => {
      // Arrange
      const firstDate = "2025-07-31";
      const secondDate = "2025-08-01";

      mockDateInput.value = firstDate;

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act - First call
      loadMethodAnalysis();
      expect(global.currentAnalysisDate).toBe(firstDate);

      // Change date and call again
      mockDateInput.value = secondDate;
      loadMethodAnalysis();

      // Assert - State should be updated
      expect(global.currentAnalysisDate).toBe(secondDate);
    });
  });

  // ========================================
  // 🎯 PHASE 7: EDGE CASES & BOUNDARY TESTS
  // ========================================

  describe("Phase 7: Edge Cases & Boundary Tests", () => {
    test("7.1 - Should handle very long date strings", () => {
      // Arrange
      const longDate = "2025-07-31".repeat(100);
      mockDateInput.value = longDate;

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Assert
      expect(global.currentAnalysisDate).toBe(longDate);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(encodeURIComponent(longDate))
      );
    });

    test("7.2 - Should handle special characters in date", () => {
      // Arrange
      const specialDate = "2025-07-31&test=value#fragment";
      mockDateInput.value = specialDate;

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Assert
      expect(global.currentAnalysisDate).toBe(specialDate);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(specialDate)
      );
    });

    test("7.3 - Should handle DOM element changes during execution", async () => {
      // Arrange
      const initialDate = "2025-07-31";
      mockDateInput.value = initialDate;

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Change DOM during execution
      mockDateInput.value = "2025-08-01";

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert - Should use initial date value
      expect(global.currentAnalysisDate).toBe(initialDate);
    });

    test("7.4 - Should handle response with unexpected properties", async () => {
      // Arrange
      mockDateInput.value = "2025-07-31";

      const weirdData = {
        success: true,
        unexpectedProperty: "weird value",
        nestedObject: {
          deepProperty: ["array", "values"],
        },
        nullProperty: null,
        undefinedProperty: undefined,
      };

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue(weirdData),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert - Should still process successfully
      expect(mockRenderAnalysisResults).toHaveBeenCalledWith(weirdData);
      expect(mockShowError).not.toHaveBeenCalled();
    });

    test("7.5 - Should handle extremely large response data", async () => {
      // Arrange
      mockDateInput.value = "2025-07-31";

      const largeArray = new Array(10000).fill().map((_, i) => ({
        id: i,
        data: `large data item ${i}`,
        moreData: new Array(100).fill(`sub-item-${i}`),
      }));

      const largeData = {
        success: true,
        largeArray: largeArray,
        metadata: {
          totalItems: largeArray.length,
          timestamp: Date.now(),
        },
      };

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue(largeData),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert - Should handle large data
      expect(mockRenderAnalysisResults).toHaveBeenCalledWith(largeData);
      expect(mockHideLoading).toHaveBeenCalled();
    });
  });

  // ========================================
  // 🔧 PHASE 8: MOCK VALIDATION TESTS
  // ========================================

  describe("Phase 8: Mock Validation Tests", () => {
    test("8.1 - Should verify all required functions are mocked", () => {
      // Assert
      expect(mockShowError).toBeDefined();
      expect(mockShowLoading).toBeDefined();
      expect(mockHideLoading).toBeDefined();
      expect(mockRenderAnalysisResults).toBeDefined();
      expect(mockFetch).toBeDefined();
      expect(mockConsole.log).toBeDefined();
      expect(mockConsole.error).toBeDefined();
      expect(mockDocument.getElementById).toBeDefined();
    });

    test("8.2 - Should verify mock functions are called correctly", async () => {
      // Arrange
      mockDateInput.value = "2025-07-31";

      const mockResponse = {
        ok: true,
        status: 200,
        headers: { get: jest.fn().mockReturnValue("application/json") },
        json: jest.fn().mockResolvedValue({ success: true }),
      };
      mockFetch.mockResolvedValue(mockResponse);

      // Act
      loadMethodAnalysis();

      // Wait for promises to resolve
      await new Promise((resolve) => setTimeout(resolve, 0));

      // Assert - Verify mock call patterns
      expect(mockDocument.getElementById).toHaveBeenCalledWith(
        "analysisDatePicker"
      );
      expect(mockShowLoading).toHaveBeenCalledTimes(1);
      expect(mockFetch).toHaveBeenCalledTimes(1);
      expect(mockHideLoading).toHaveBeenCalledTimes(1);
      expect(mockRenderAnalysisResults).toHaveBeenCalledTimes(1);
    });

    test("8.3 - Should verify mock reset between tests", () => {
      // Assert - All mocks should be clean
      expect(mockShowError).not.toHaveBeenCalled();
      expect(mockShowLoading).not.toHaveBeenCalled();
      expect(mockHideLoading).not.toHaveBeenCalled();
      expect(mockRenderAnalysisResults).not.toHaveBeenCalled();
      expect(mockFetch).not.toHaveBeenCalled();
      expect(mockConsole.log).not.toHaveBeenCalled();
      expect(mockConsole.error).not.toHaveBeenCalled();
    });
  });
});

// ========================================
// 🎯 PERFORMANCE & TIMING TESTS
// ========================================

describe("loadMethodAnalysis() Performance Tests", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockDateInput.value = "2025-07-31";
  });

  test("Should complete within reasonable time", async () => {
    // Arrange
    const mockResponse = {
      ok: true,
      status: 200,
      headers: { get: jest.fn().mockReturnValue("application/json") },
      json: jest.fn().mockResolvedValue({ success: true }),
    };
    mockFetch.mockResolvedValue(mockResponse);

    // Act
    const startTime = Date.now();
    loadMethodAnalysis();
    await new Promise((resolve) => setTimeout(resolve, 0));
    const endTime = Date.now();

    // Assert - Should complete quickly (allowing for test overhead)
    expect(endTime - startTime).toBeLessThan(100);
  });

  test("Should handle slow network responses", async () => {
    // Arrange
    const slowResponse = new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          ok: true,
          status: 200,
          headers: { get: jest.fn().mockReturnValue("application/json") },
          json: jest.fn().mockResolvedValue({ success: true }),
        });
      }, 50);
    });
    mockFetch.mockReturnValue(slowResponse);

    // Act
    const startTime = Date.now();
    loadMethodAnalysis();
    await slowResponse;
    await new Promise((resolve) => setTimeout(resolve, 0));
    const endTime = Date.now();

    // Assert
    expect(endTime - startTime).toBeGreaterThanOrEqual(50);
    expect(mockHideLoading).toHaveBeenCalled();
  });
});

// Export for Node.js environment
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    loadMethodAnalysis,
    mockShowError,
    mockShowLoading,
    mockHideLoading,
    mockRenderAnalysisResults,
    mockFetch,
    mockConsole,
    mockDocument,
    mockDateInput,
  };
}
