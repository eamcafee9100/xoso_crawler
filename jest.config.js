module.exports = {
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/predictions_tracker/static/js/test/setup.js'],
    testMatch: ['**/test/**/*.test.js'],
    collectCoverage: true,
    coverageDirectory: 'coverage',
    coverageReporters: ['text', 'lcov', 'html'],
    coverageThreshold: {
        global: {
            branches: 70,
            functions: 70,
            lines: 70,
            statements: 70
        }
    },
    transform: {
        '^.+\.js$': 'babel-jest'
    },
    testPathIgnorePatterns: ['/node_modules/', '/static/admin/'],
    verbose: true,
    clearMocks: true,
    restoreMocks: true,
    testTimeout: 10000
};