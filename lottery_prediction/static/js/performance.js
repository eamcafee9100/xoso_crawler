// Performance Dashboard JavaScript
let performanceTrendChart = null;
let modelComparisonChart = null;
let currentPeriod = 30;
let refreshInterval = null;

$(document).ready(function () {
  // Initialize dashboard
  initializeDashboard();

  // Set up event handlers
  setupEventHandlers();

  // Start auto-refresh
  startAutoRefresh();

  console.log("Performance dashboard initialized");
});

function initializeDashboard() {
  // Load initial data
  loadPerformanceData();

  // Initialize charts
  initializeCharts();
}

function setupEventHandlers() {
  // Refresh button
  $("#refreshBtn").on("click", function () {
    $(this).prop("disabled", true);
    $(this).find("i").addClass("fa-spin");

    loadPerformanceData().finally(() => {
      $(this).prop("disabled", false);
      $(this).find("i").removeClass("fa-spin");
    });
  });

  // Period selection
  $(".dropdown-menu a").on("click", function (e) {
    e.preventDefault();
    const days = parseInt($(this).data("days"));
    const text = $(this).text();

    currentPeriod = days;
    $("#selectedPeriod").text(text);

    loadPerformanceData();
  });

  // Model details modal
  $(document).on("click", ".view-details-btn", function () {
    const modelName = $(this).data("model");
    showModelDetails(modelName);
  });

  // Retrain model button
  $("#retrainModelBtn").on("click", function () {
    const modelName = $(this).data("model");
    initiateRetrain(modelName);
  });
}

function loadPerformanceData() {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: "/lottery-prediction/api/model-performance/",
      method: "GET",
      data: {
        days: currentPeriod,
        metric_type: "detailed",
      },
      success: function (response) {
        console.log("Performance data loaded:", response);

        // Update KPI cards
        updateKPICards(response.summary);

        // Update performance table
        updatePerformanceTable(response.performance_data);

        // Update charts
        updateCharts(response.performance_data);

        // Check for alerts
        checkPerformanceAlerts(response.performance_data);

        resolve(response);
      },
      error: function (xhr, status, error) {
        console.error("Failed to load performance data:", error);
        showError(
          "Failed to load performance data: " +
            (xhr.responseJSON?.error || error)
        );
        reject(error);
      },
    });
  });
}

function updateKPICards(summary) {
  // Overall Hit Rate
  const hitRate = (summary.overall_hit_rate * 100).toFixed(1) + "%";
  $("#overallHitRate").text(hitRate);
  $("#hitRateChange").text(
    `${summary.total_successful_days}/${summary.total_prediction_days} days`
  );

  // Active Models
  $("#activeModels").text(summary.total_models);
  $("#modelsChange").text("Active");

  // Successful Days
  $("#successfulDays").text(summary.total_successful_days);
  $("#successChange").text("Recent period");

  // Models at Risk (calculate based on performance)
  // This would need additional logic based on your risk criteria
  $("#modelsAtRisk").text("--");
  $("#riskChange").text("Monitoring");
}

function updatePerformanceTable(performanceData) {
  const tableBody = $("#performanceTable tbody");
  tableBody.empty();

  performanceData.forEach(function (perf) {
    const hitRate = (perf.hit_rate * 100).toFixed(1) + "%";
    const fatigueStatus = perf.fatigue_threshold_reached
      ? '<span class="badge bg-warning">Fatigued</span>'
      : '<span class="badge bg-success">Active</span>';

    const lastUpdate = perf.fatigue_reached_on
      ? new Date(perf.fatigue_reached_on).toLocaleDateString()
      : "Recently";

    const row = `
            <tr>
                <td><strong>${perf.model_name}</strong></td>
                <td>${hitRate}</td>
                <td>${perf.total_hit_days}</td>
                <td>${perf.total_days}</td>
                <td>${fatigueStatus}</td>
                <td>${lastUpdate}</td>
                <td>
                    <button class="btn btn-sm btn-info view-details-btn" data-model="${perf.model_name}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-warning retrain-btn" data-model="${perf.model_name}">
                        <i class="fas fa-redo"></i>
                    </button>
                </td>
            </tr>
        `;
    tableBody.append(row);
  });
}

function initializeCharts() {
  // Performance Trend Chart
  const trendCtx = document.getElementById("performanceTrendChart");
  if (trendCtx) {
    performanceTrendChart = new Chart(trendCtx, {
      type: "line",
      data: {
        labels: [],
        datasets: [],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: "Hit Rate Trends Over Time",
          },
          legend: {
            display: true,
            position: "top",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 1,
            ticks: {
              callback: function (value) {
                return (value * 100).toFixed(0) + "%";
              },
            },
            title: {
              display: true,
              text: "Hit Rate",
            },
          },
          x: {
            title: {
              display: true,
              text: "Period",
            },
          },
        },
      },
    });
  }

  // Model Comparison Chart
  const comparisonCtx = document.getElementById("modelComparisonChart");
  if (comparisonCtx) {
    modelComparisonChart = new Chart(comparisonCtx, {
      type: "doughnut",
      data: {
        labels: [],
        datasets: [
          {
            data: [],
            backgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4BC0C0",
              "#9966FF",
              "#FF9F40",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: "Model Performance Comparison",
          },
          legend: {
            display: true,
            position: "bottom",
          },
        },
      },
    });
  }
}

function updateCharts(performanceData) {
  if (!performanceData || performanceData.length === 0) return;

  // Update trend chart
  if (performanceTrendChart) {
    const labels = performanceData.map(
      (p) => `${p.year}-${p.month.toString().padStart(2, "0")}`
    );
    const hitRates = performanceData.map((p) => p.hit_rate);

    // Group by model
    const modelData = {};
    performanceData.forEach((p) => {
      if (!modelData[p.model_name]) {
        modelData[p.model_name] = {
          labels: [],
          data: [],
        };
      }
      modelData[p.model_name].labels.push(
        `${p.year}-${p.month.toString().padStart(2, "0")}`
      );
      modelData[p.model_name].data.push(p.hit_rate);
    });

    // Create datasets
    const colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"];
    const datasets = Object.keys(modelData).map((modelName, index) => ({
      label: modelName,
      data: modelData[modelName].data,
      borderColor: colors[index % colors.length],
      backgroundColor: colors[index % colors.length] + "20",
      tension: 0.1,
    }));

    performanceTrendChart.data.labels = [...new Set(labels)].sort();
    performanceTrendChart.data.datasets = datasets;
    performanceTrendChart.update();
  }

  // Update comparison chart
  if (modelComparisonChart) {
    const modelNames = [...new Set(performanceData.map((p) => p.model_name))];
    const avgHitRates = modelNames.map((name) => {
      const modelPerfs = performanceData.filter((p) => p.model_name === name);
      return (
        modelPerfs.reduce((sum, p) => sum + p.hit_rate, 0) / modelPerfs.length
      );
    });

    modelComparisonChart.data.labels = modelNames;
    modelComparisonChart.data.datasets[0].data = avgHitRates;
    modelComparisonChart.update();
  }
}

function checkPerformanceAlerts(performanceData) {
  const alerts = [];

  performanceData.forEach((perf) => {
    // Low performance alert
    if (perf.hit_rate < 0.25) {
      alerts.push({
        type: "danger",
        title: "Low Performance Alert",
        message: `Model ${perf.model_name} has hit rate of ${(
          perf.hit_rate * 100
        ).toFixed(1)}% (below 25%)`,
      });
    }

    // Fatigue alert
    if (perf.fatigue_threshold_reached) {
      alerts.push({
        type: "warning",
        title: "Model Fatigue Alert",
        message: `Model ${perf.model_name} has reached fatigue threshold and may need retraining`,
      });
    }

    // Good performance
    if (perf.hit_rate > 0.4) {
      alerts.push({
        type: "success",
        title: "Good Performance",
        message: `Model ${perf.model_name} is performing well with ${(
          perf.hit_rate * 100
        ).toFixed(1)}% hit rate`,
      });
    }
  });

  displayAlerts(alerts);
}

function displayAlerts(alerts) {
  const alertContainer = $("#performanceAlerts");
  alertContainer.empty();

  if (alerts.length === 0) {
    $("#alertContainer").hide();
    return;
  }

  alerts.forEach((alert) => {
    const alertHtml = `
            <div class="alert alert-${
              alert.type
            } alert-dismissible fade show alert-box" role="alert">
                <i class="fas fa-${
                  alert.type === "danger"
                    ? "exclamation-triangle"
                    : alert.type === "warning"
                    ? "exclamation-circle"
                    : "check-circle"
                }"></i>
                <strong>${alert.title}:</strong> ${alert.message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    alertContainer.append(alertHtml);
  });

  $("#alertContainer").show();
}

function showModelDetails(modelName) {
  // Load detailed model information
  $.ajax({
    url: "/lottery-prediction/api/model-performance/",
    method: "GET",
    data: {
      model_name: modelName,
      days: currentPeriod,
      metric_type: "detailed",
    },
    success: function (response) {
      const modelData = response.performance_data[0];
      if (modelData) {
        const detailsHtml = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Basic Metrics</h6>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Hit Rate:</span>
                                    <strong>${(
                                      modelData.hit_rate * 100
                                    ).toFixed(2)}%</strong>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Total Hits:</span>
                                    <strong>${modelData.total_hit_days}</strong>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Total Days:</span>
                                    <strong>${modelData.total_days}</strong>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Period:</span>
                                    <strong>${modelData.year}-${modelData.month
          .toString()
          .padStart(2, "0")}</strong>
                                </li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6>Performance Breakdown</h6>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Early Month:</span>
                                    <strong>${(
                                      modelData.early_month_performance * 100
                                    ).toFixed(1)}%</strong>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Mid Month:</span>
                                    <strong>${(
                                      modelData.mid_month_performance * 100
                                    ).toFixed(1)}%</strong>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Late Month:</span>
                                    <strong>${(
                                      modelData.late_month_performance * 100
                                    ).toFixed(1)}%</strong>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Fatigue Status:</span>
                                    <strong class="${
                                      modelData.fatigue_threshold_reached
                                        ? "text-warning"
                                        : "text-success"
                                    }">
                                        ${
                                          modelData.fatigue_threshold_reached
                                            ? "Fatigued"
                                            : "Active"
                                        }
                                    </strong>
                                </li>
                            </ul>
                        </div>
                    </div>
                `;

        $("#modelDetailsContent").html(detailsHtml);
        $("#retrainModelBtn").data("model", modelName);
        $("#modelDetailsModal").modal("show");
      }
    },
    error: function (xhr, status, error) {
      showError("Failed to load model details: " + error);
    },
  });
}

function initiateRetrain(modelName) {
  if (
    confirm(
      `Are you sure you want to retrain the ${modelName} model? This may take several minutes.`
    )
  ) {
    // Redirect to retrain page with model parameter
    window.location.href = `/lottery-prediction/retrain/?model=${encodeURIComponent(
      modelName
    )}`;
  }
}

function startAutoRefresh() {
  // Refresh every 5 minutes
  refreshInterval = setInterval(() => {
    console.log("Auto-refreshing performance data...");
    loadPerformanceData();
  }, 5 * 60 * 1000);
}

function showError(message) {
  const errorHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-triangle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

  $(".container-fluid").prepend(errorHtml);

  // Auto-hide after 10 seconds
  setTimeout(() => {
    $(".alert-danger").fadeOut();
  }, 10000);
}

// Cleanup on page unload
$(window).on("beforeunload", function () {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
