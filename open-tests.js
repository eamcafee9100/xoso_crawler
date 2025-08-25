#!/usr/bin/env node

/**
 * 🌐 BROWSER TEST LAUNCHER
 * Script để mở browser test và báo cáo coverage
 */

const { execSync, spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const COLORS = {
  RED: "\x1b[31m",
  GREEN: "\x1b[32m",
  YELLOW: "\x1b[33m",
  BLUE: "\x1b[34m",
  CYAN: "\x1b[36m",
  WHITE: "\x1b[37m",
  RESET: "\x1b[0m",
  BOLD: "\x1b[1m",
};

function log(message, color = "WHITE") {
  console.log(`${COLORS[color]}${message}${COLORS.RESET}`);
}

function openInBrowser(filePath) {
  const fullPath = path.resolve(filePath);
  const fileUrl = `file://${fullPath.replace(/\\/g, "/")}`;

  try {
    // Try different commands based on OS
    if (process.platform === "win32") {
      execSync(`start "" "${fileUrl}"`, { shell: true });
    } else if (process.platform === "darwin") {
      execSync(`open "${fileUrl}"`);
    } else {
      execSync(`xdg-open "${fileUrl}"`);
    }
    return true;
  } catch (error) {
    log(`⚠️  Could not open browser automatically: ${error.message}`, "YELLOW");
    log(`📋 Please manually open: ${fileUrl}`, "CYAN");
    return false;
  }
}

async function main() {
  log(`${COLORS.BOLD}${COLORS.CYAN}🌐 BROWSER TEST LAUNCHER${COLORS.RESET}`);
  log(`${COLORS.CYAN}${"=".repeat(50)}${COLORS.RESET}\n`);

  // Check and open browser test runner
  const testRunnerPath = "predictions_tracker/static/js/test/test-runner.html";
  if (fs.existsSync(testRunnerPath)) {
    log("🌐 Opening browser test runner...", "YELLOW");
    if (openInBrowser(testRunnerPath)) {
      log("✅ Browser test runner opened successfully!", "GREEN");
    }
  } else {
    log("❌ Browser test runner not found!", "RED");
  }

  // Check and open coverage report
  const coveragePath = "coverage/lcov-report/index.html";
  if (fs.existsSync(coveragePath)) {
    log("\n📊 Opening coverage report...", "YELLOW");
    if (openInBrowser(coveragePath)) {
      log("✅ Coverage report opened successfully!", "GREEN");
    }
  } else {
    log("\n⚠️  Coverage report not found. Generating...", "YELLOW");
    try {
      execSync("npx jest --coverage --silent", { stdio: "pipe", shell: true });
      if (fs.existsSync(coveragePath)) {
        log("📊 Opening generated coverage report...", "YELLOW");
        openInBrowser(coveragePath);
        log("✅ Coverage report generated and opened!", "GREEN");
      }
    } catch (error) {
      log("❌ Could not generate coverage report", "RED");
    }
  }

  // Summary
  log(`\n${COLORS.BOLD}📋 SUMMARY${COLORS.RESET}`, "CYAN");
  log("✅ Browser test launcher completed", "GREEN");
  log("\n🔗 Available links:", "CYAN");

  if (fs.existsSync(testRunnerPath)) {
    const testUrl = path.resolve(testRunnerPath).replace(/\\/g, "/");
    log(`  🌐 Browser Test Runner: file://${testUrl}`, "WHITE");
  }

  if (fs.existsSync(coveragePath)) {
    const coverageUrl = path.resolve(coveragePath).replace(/\\/g, "/");
    log(`  📊 Coverage Report: file://${coverageUrl}`, "WHITE");
  }

  log("\n🚀 Next actions:", "CYAN");
  log("  1. Check browser test results", "WHITE");
  log("  2. Review coverage metrics", "WHITE");
  log("  3. Run additional tests if needed: npm test", "WHITE");

  log(`\n${COLORS.BOLD}${COLORS.GREEN}🎉 ALL DONE!${COLORS.RESET}`);
}

// Run the script
if (require.main === module) {
  main().catch((error) => {
    log(`💥 Error: ${error.message}`, "RED");
    process.exit(1);
  });
}
