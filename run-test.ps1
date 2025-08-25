# 🤖 POWERSHELL WRAPPER for Auto Test Script

param(
    [switch]$Auto,
    [switch]$Help,
    [switch]$StepByStep,
    [switch]$TestOnly,
    [switch]$FixOnly
)

# Colors for PowerShell
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Cyan = "Cyan"
    Magenta = "Magenta"
    White = "White"
}

function Write-ColorText {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Colors[$Color]
}

function Show-Header {
    Write-ColorText "==========================================" "Cyan"
    Write-ColorText "🤖 AUTO TEST RUNNER - POWERSHELL LAUNCHER" "Cyan"
    Write-ColorText "==========================================" "Cyan"
    Write-Host ""
}

function Test-Prerequisites {
    Write-ColorText "🔍 Checking prerequisites..." "Yellow"
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-ColorText "✅ Node.js detected: $nodeVersion" "Green"
        } else {
            throw "Node.js not found"
        }
    } catch {
        Write-ColorText "❌ Node.js not found! Please install Node.js first." "Red"
        Write-ColorText "Download from: https://nodejs.org" "Yellow"
        exit 1
    }
    
    # Check NPM
    try {
        $npmVersion = npm --version 2>$null
        if ($npmVersion) {
            Write-ColorText "✅ NPM detected: $npmVersion" "Green"
        }
    } catch {
        Write-ColorText "⚠️  NPM not found, but continuing..." "Yellow"
    }
    
    # Check auto-test.js
    if (Test-Path "auto-test.js") {
        Write-ColorText "✅ Auto test script found" "Green"
    } else {
        Write-ColorText "❌ auto-test.js not found in current directory" "Red"
        exit 1
    }
    
    Write-Host ""
}

function Show-Menu {
    Write-ColorText "🚀 Choose execution mode:" "Cyan"
    Write-Host ""
    Write-ColorText "1. 🤖 Auto Mode (recommended)" "White"
    Write-ColorText "   - Automatically detect and fix issues" "Gray"
    Write-Host ""
    Write-ColorText "2. 👣 Step by Step Mode" "White"
    Write-ColorText "   - Interactive execution with confirmations" "Gray"
    Write-Host ""
    Write-ColorText "3. 🧪 Test Only Mode" "White"
    Write-ColorText "   - Run tests without fixing issues" "Gray"
    Write-Host ""
    Write-ColorText "4. 🔧 Fix Only Mode" "White"
    Write-ColorText "   - Only fix issues without running tests" "Gray"
    Write-Host ""
    Write-ColorText "5. ❓ Help" "White"
    Write-ColorText "   - Show detailed help information" "Gray"
    Write-Host ""
}

function Get-UserChoice {
    do {
        $choice = Read-Host "Enter your choice (1-5)"
        if ($choice -match '^[1-5]$') {
            return [int]$choice
        } else {
            Write-ColorText "❌ Invalid choice. Please enter 1-5." "Red"
        }
    } while ($true)
}

function Start-AutoTest {
    param([string]$Mode = "")
    
    Write-ColorText "🚀 Starting automated test runner..." "Cyan"
    Write-Host ""
    
    try {
        switch ($Mode) {
            "auto" { 
                node auto-test.js --auto 
            }
            "help" { 
                node auto-test.js --help 
            }
            default { 
                node auto-test.js 
            }
        }
        
        Write-Host ""
        Write-ColorText "🏁 Auto test runner completed" "Cyan"
        
    } catch {
        Write-ColorText "❌ Error running auto test script: $_" "Red"
        exit 1
    }
}

function Show-PostExecution {
    Write-Host ""
    Write-ColorText "📋 Post-execution summary:" "Cyan"
    Write-ColorText "✅ Check the output above for results" "Green"
    Write-ColorText "📁 Coverage report: coverage/lcov-report/index.html" "Yellow"
    Write-ColorText "🌐 Browser tests: predictions_tracker/static/js/test/test-runner.html" "Yellow"
    Write-Host ""
    
    # Ask if user wants to open coverage report
    $openCoverage = Read-Host "Open coverage report in browser? (y/n)"
    if ($openCoverage -eq "y" -or $openCoverage -eq "Y") {
        if (Test-Path "coverage/lcov-report/index.html") {
            Start-Process "coverage/lcov-report/index.html"
        } else {
            Write-ColorText "⚠️  Coverage report not found" "Yellow"
        }
    }
    
    # Ask if user wants to open browser tests
    $openBrowser = Read-Host "Open browser tests? (y/n)"
    if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
        if (Test-Path "predictions_tracker/static/js/test/test-runner.html") {
            Start-Process "predictions_tracker/static/js/test/test-runner.html"
        } else {
            Write-ColorText "⚠️  Browser test runner not found" "Yellow"
        }
    }
}

# Main execution
try {
    Show-Header
    Test-Prerequisites
    
    # Handle command line parameters
    if ($Help) {
        Start-AutoTest -Mode "help"
        exit 0
    }
    
    if ($Auto) {
        Start-AutoTest -Mode "auto"
        Show-PostExecution
        exit 0
    }
    
    # Interactive mode
    Show-Menu
    $choice = Get-UserChoice
    
    switch ($choice) {
        1 { 
            Start-AutoTest -Mode "auto"
            Show-PostExecution
        }
        2 { 
            Write-ColorText "👣 Starting step-by-step mode..." "Yellow"
            Start-AutoTest
            Show-PostExecution
        }
        3 { 
            Write-ColorText "🧪 Starting test-only mode..." "Yellow"
            # Could add specific test-only logic here
            Start-AutoTest
            Show-PostExecution
        }
        4 { 
            Write-ColorText "🔧 Starting fix-only mode..." "Yellow"
            # Could add specific fix-only logic here
            Start-AutoTest
            Show-PostExecution
        }
        5 { 
            Start-AutoTest -Mode "help"
        }
    }
    
} catch {
    Write-ColorText "💥 Fatal error: $_" "Red"
    exit 1
}

# Keep window open in interactive mode
if (-not ($Auto -or $Help)) {
    Write-Host ""
    Write-ColorText "Press any key to exit..." "Gray"
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
