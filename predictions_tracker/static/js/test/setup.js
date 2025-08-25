/**
 * ✅ TEST SETUP FILE - Global test configuration and utilities
 * Thiết lập môi trường test toàn cục cho loadMethodAnalysis tests
 */

// Global test utilities
global.waitForPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

// Mock console để tránh spam trong tests
global.console = {
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
  debug: jest.fn(),
};

// Mock window object cho browser APIs
Object.defineProperty(window, "location", {
  value: {
    href: "http://localhost:8000",
    pathname: "/pre-lokhung/monthly-report/",
    search: "?year=2025&month=7",
  },
  writable: true,
});

// Mock fetch globally
global.fetch = jest.fn();

// Custom matchers
expect.extend({
  toHaveBeenCalledBefore(received, expectedCall) {
    const receivedCallOrder = received.mock.invocationCallOrder[0];
    const expectedCallOrder = expectedCall.mock.invocationCallOrder[0];

    const pass = receivedCallOrder < expectedCallOrder;

    if (pass) {
      return {
        message: () =>
          `Expected ${received.getMockName()} not to have been called before ${expectedCall.getMockName()}`,
        pass: true,
      };
    } else {
      return {
        message: () =>
          `Expected ${received.getMockName()} to have been called before ${expectedCall.getMockName()}`,
        pass: false,
      };
    }
  },
});

// Global test data factories
global.createMockResponse = (options = {}) => {
  const defaultOptions = {
    ok: true,
    status: 200,
    statusText: "OK",
    headers: new Map([["content-type", "application/json"]]),
    url: "http://test-url.com",
    json: () => Promise.resolve({ success: true }),
  };

  return {
    ...defaultOptions,
    ...options,
    headers: {
      get: jest.fn((key) => {
        if (options.headers && options.headers.get) {
          return options.headers.get(key);
        }
        return defaultOptions.headers.get(key.toLowerCase());
      }),
    },
  };
};

global.createMockAnalysisData = (overrides = {}) => {
  return {
    success: true,
    analysis_date: "2025-07-31",
    hybrid_analysis: {
      short_term_insights: {
        trend_direction: "up",
        recent_performance: 75.5,
        stability_score: 85.2,
      },
      long_term_stability: {
        consistency_rating: "high",
        reliability_score: 80.1,
        historical_accuracy: 72.3,
      },
      forward_validation: {
        confidence_level: "high",
        risk_assessment: "low",
        expected_performance: 78.9,
      },
    },
    intelligent_selections: {
      optimal_numbers: ["12", "34", "56", "78", "90"],
      method_contributions: [
        { method_id: 1, method_name: "Test Method 1", contribution: 0.4 },
        { method_id: 2, method_name: "Test Method 2", contribution: 0.3 },
        { method_id: 3, method_name: "Test Method 3", contribution: 0.3 },
      ],
      selection_strategy: {
        approach: "hybrid",
        confidence: 0.85,
        risk_level: "low",
      },
    },
    optimal_methods: {
      day_1: [
        {
          method_id: 1,
          method_name: "Test Method 1",
          hybrid_score: 85.5,
          risk_level: "low",
          predicted_numbers: ["12", "34"],
        },
      ],
      day_2: [
        {
          method_id: 2,
          method_name: "Test Method 2",
          hybrid_score: 80.2,
          risk_level: "medium",
          predicted_numbers: ["56", "78"],
        },
      ],
      day_3: [
        {
          method_id: 3,
          method_name: "Test Method 3",
          hybrid_score: 75.8,
          risk_level: "low",
          predicted_numbers: ["90", "12"],
        },
      ],
      summary: {
        total_methods: 3,
        avg_hybrid_score: 80.5,
        recommended_day: 1,
      },
    },
    performance_prediction: {
      expected_hit_rate: 25.5,
      confidence_level: "high",
      overall_confidence_score: 0.82,
      risk_assessment: {
        level: "low",
        factors: ["stable_performance", "consistent_methods"],
      },
      performance_breakdown: {
        confidence_factors: {
          data_quality: 0.9,
          method_stability: 0.85,
          historical_accuracy: 0.75,
        },
        risk_factors: ["market_volatility", "data_freshness"],
      },
    },
    metadata: {
      analysis_timestamp: "2025-07-31T10:30:00Z",
      total_methods_analyzed: 50,
      qualified_methods: 15,
      data_range: "2025-06-01 to 2025-07-30",
    },
    ...overrides,
  };
};

// Error test data factory
global.createMockError = (type = "network") => {
  const errors = {
    network: new Error("Failed to fetch"),
    http404: new Error("HTTP 404: Not Found"),
    http500: new Error("HTTP 500: Internal Server Error"),
    syntax: new SyntaxError("Unexpected token < in JSON at position 0"),
    generic: new Error("Some unexpected error"),
  };

  return errors[type] || errors.generic;
};

// DOM utilities
global.createMockElement = (tagName, attributes = {}) => {
  const element = {
    tagName: tagName.toUpperCase(),
    value: "",
    textContent: "",
    innerHTML: "",
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(),
      toggle: jest.fn(),
    },
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    setAttribute: jest.fn(),
    getAttribute: jest.fn(),
    ...attributes,
  };

  return element;
};

// Async test utilities
global.flushPromises = () => new Promise((resolve) => setImmediate(resolve));

// Test timing utilities
global.advanceTimersByTime = (ms) => {
  jest.advanceTimersByTime(ms);
};

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Cleanup function
global.cleanupAfterTest = () => {
  jest.clearAllMocks();
  jest.clearAllTimers();

  // Reset global variables
  if (typeof global.currentAnalysisDate !== "undefined") {
    global.currentAnalysisDate = null;
  }

  if (typeof global.lowRiskMethodsData !== "undefined") {
    global.lowRiskMethodsData = [];
  }
};

// Setup and teardown
beforeEach(() => {
  // Reset all mocks before each test
  jest.clearAllMocks();

  // Reset timers
  jest.useFakeTimers();
});

afterEach(() => {
  // Cleanup after each test
  global.cleanupAfterTest();

  // Restore timers
  jest.useRealTimers();
});

// Global error handler for unhandled promise rejections
process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
});

console.log("✅ Test setup completed successfully");
