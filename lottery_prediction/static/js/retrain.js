// Retrain System JavaScript
let trainingTimer = null;
let trainingStartTime = null;
let progressInterval = null;
let logInterval = null;
let currentTrainingId = null;

$(document).ready(function () {
  // Initialize retrain system
  initializeRetrainSystem();

  // Set up event handlers
  setupEventHandlers();

  console.log("Retrain system initialized");
});

function initializeRetrainSystem() {
  // Check for ongoing training
  checkOngoingTraining();

  // Pre-populate form based on URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const modelName = urlParams.get("model");

  if (modelName) {
    $("#modelSelect").val(modelName);
    showAlert(
      "info",
      "Model Pre-selected",
      `${modelName} model has been pre-selected for retraining.`
    );
  }
}

function setupEventHandlers() {
  // Form submission
  $("#retrainForm").on("submit", function (e) {
    e.preventDefault();
    startTraining();
  });

  // Cancel training
  $("#cancelBtn").on("click", function () {
    cancelTraining();
  });

  // Quick action buttons
  $("#viewPerformanceBtn").on("click", function () {
    window.open("/lottery-prediction/performance/", "_blank");
  });

  $("#downloadLogsBtn").on("click", function () {
    downloadTrainingLogs();
  });

  $("#pauseTrainingBtn").on("click", function () {
    pauseTraining();
  });

  // Result actions
  $("#deployModelBtn").on("click", function () {
    deployModel();
  });

  $("#backupOldBtn").on("click", function () {
    backupOldModel();
  });

  $("#startNewBtn").on("click", function () {
    location.reload();
  });

  // Form validation
  $("#modelSelect").on("change", function () {
    const selectedModel = $(this).val();
    if (selectedModel) {
      loadModelInfo(selectedModel);
    }
  });
}

function checkOngoingTraining() {
  // Check if there's an ongoing training session
  $.ajax({
    url: "/lottery-prediction/api/retrain-status/",
    method: "GET",
    success: function (response) {
      if (response.status === "training") {
        // Resume training monitoring
        currentTrainingId = response.training_id;
        resumeTrainingMonitoring(response);
      }
    },
    error: function (xhr, status, error) {
      console.log("No ongoing training found");
    },
  });
}

function loadModelInfo(modelName) {
  // Load current model information
  $.ajax({
    url: "/lottery-prediction/api/model-info/",
    method: "GET",
    data: { model_name: modelName },
    success: function (response) {
      if (response.model_info) {
        const info = response.model_info;
        showAlert(
          "info",
          "Model Information",
          `Current accuracy: ${(info.accuracy * 100).toFixed(2)}%, 
                     Last trained: ${formatDate(info.last_trained)}, 
                     Training data: ${info.training_samples} samples`
        );
      }
    },
    error: function (xhr, status, error) {
      console.warn("Could not load model info:", error);
    },
  });
}

function startTraining() {
  // Validate form
  if (!$("#modelSelect").val()) {
    showAlert(
      "danger",
      "Validation Error",
      "Please select a model to retrain."
    );
    return;
  }

  // Prepare training data
  const formData = {
    model_name: $("#modelSelect").val(),
    retrain_type: $("#retrainType").val(),
    data_range: parseInt($("#dataRange").val()),
    validation_split: parseFloat($("#validationSplit").val()) / 100,
    test_split: parseFloat($("#testSplit").val()) / 100,
    auto_optimize: $("#autoOptimize").is(":checked"),
    save_backup: $("#saveBackup").is(":checked"),
    validate_results: $("#validateResults").is(":checked"),
  };

  // Show confirmation
  if (
    !confirm(
      `Start retraining ${formData.model_name} model with ${formData.retrain_type} approach?`
    )
  ) {
    return;
  }

  // Disable form and show progress
  $("#retrainForm :input").prop("disabled", true);
  $("#startRetrainBtn").prop("disabled", true);
  $("#cancelBtn").show();
  $("#progressContainer").show();

  // Update status
  updateTrainingStatus("training", "Training Started");
  resetProgress();

  // Start training timer
  trainingStartTime = new Date();
  startTrainingTimer();

  // Start training
  $.ajax({
    url: "/lottery-prediction/api/retrain-model/",
    method: "POST",
    data: JSON.stringify(formData),
    contentType: "application/json",
    headers: {
      "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
    },
    success: function (response) {
      console.log("Training started:", response);
      currentTrainingId = response.training_id;

      // Start monitoring
      startProgressMonitoring();

      showAlert(
        "success",
        "Training Started",
        `${formData.model_name} model retraining has begun. Training ID: ${currentTrainingId}`
      );

      // Log initial message
      addLogMessage(
        "info",
        `Training started for ${formData.model_name} model`
      );
      addLogMessage(
        "info",
        `Configuration: ${formData.retrain_type} retrain with ${formData.data_range} days of data`
      );
    },
    error: function (xhr, status, error) {
      console.error("Failed to start training:", error);

      const errorMsg = xhr.responseJSON?.error || error;
      showAlert(
        "danger",
        "Training Error",
        `Failed to start training: ${errorMsg}`
      );

      // Reset UI
      resetTrainingUI();
    },
  });
}

function startProgressMonitoring() {
  if (progressInterval) {
    clearInterval(progressInterval);
  }

  progressInterval = setInterval(() => {
    updateTrainingProgress();
  }, 2000); // Check every 2 seconds

  // Also start log monitoring
  startLogMonitoring();
}

function startLogMonitoring() {
  if (logInterval) {
    clearInterval(logInterval);
  }

  logInterval = setInterval(() => {
    fetchTrainingLogs();
  }, 3000); // Check logs every 3 seconds
}

function updateTrainingProgress() {
  if (!currentTrainingId) return;

  $.ajax({
    url: "/lottery-prediction/api/retrain-progress/",
    method: "GET",
    data: { training_id: currentTrainingId },
    success: function (response) {
      console.log("Progress update:", response);

      // Update progress bar
      const progress = Math.round(response.progress * 100);
      $("#overallProgress").text(progress + "%");
      $("#overallProgressBar").css("width", progress + "%");

      // Update current phase
      updateTrainingPhase(response.current_phase);

      // Update metrics
      if (response.metrics) {
        updateTrainingMetrics(response.metrics);
      }

      // Check if completed
      if (response.status === "completed") {
        trainingCompleted(response);
      } else if (response.status === "error") {
        trainingError(response);
      }
    },
    error: function (xhr, status, error) {
      console.warn("Failed to get progress update:", error);
    },
  });
}

function fetchTrainingLogs() {
  if (!currentTrainingId) return;

  $.ajax({
    url: "/lottery-prediction/api/retrain-logs/",
    method: "GET",
    data: { training_id: currentTrainingId },
    success: function (response) {
      if (response.logs && response.logs.length > 0) {
        response.logs.forEach((log) => {
          addLogMessage(log.level, log.message, log.timestamp);
        });
      }
    },
    error: function (xhr, status, error) {
      console.warn("Failed to fetch logs:", error);
    },
  });
}

function updateTrainingPhase(currentPhase) {
  // Reset all phases
  $(".training-phase").removeClass("active completed");
  $(".phase-icon").removeClass("active completed");

  // Mark completed phases
  const phases = ["preparation", "training", "validation", "deployment"];
  const currentIndex = phases.indexOf(currentPhase);

  phases.forEach((phase, index) => {
    const phaseElement = $(`.training-phase[data-phase="${phase}"]`);
    const iconElement = phaseElement.find(".phase-icon");

    if (index < currentIndex) {
      phaseElement.addClass("completed");
      iconElement.addClass("completed");
    } else if (index === currentIndex) {
      phaseElement.addClass("active");
      iconElement.addClass("active");
    }
  });
}

function updateTrainingMetrics(metrics) {
  if (metrics.accuracy !== undefined) {
    $("#currentAccuracy").text((metrics.accuracy * 100).toFixed(2) + "%");
  }

  if (metrics.training_loss !== undefined) {
    $("#trainingLoss").text(metrics.training_loss.toFixed(4));
  }

  if (metrics.validation_loss !== undefined) {
    $("#validationLoss").text(metrics.validation_loss.toFixed(4));
  }

  if (metrics.epoch !== undefined) {
    $("#epochCount").text(metrics.epoch);
  }
}

function addLogMessage(level, message, timestamp = null) {
  const logContainer = $("#trainingLog");
  const time = timestamp
    ? new Date(timestamp).toLocaleTimeString()
    : new Date().toLocaleTimeString();

  const levelClass =
    {
      info: "text-info",
      warning: "text-warning",
      error: "text-danger",
      success: "text-success",
    }[level] || "text-light";

  const logEntry = `<div class="log-entry"><span class="text-muted">[${time}]</span> <span class="${levelClass}">${message}</span></div>`;

  logContainer.append(logEntry);

  // Auto-scroll to bottom
  logContainer.scrollTop(logContainer.prop("scrollHeight"));

  // Keep only last 100 log entries
  const entries = logContainer.find(".log-entry");
  if (entries.length > 100) {
    entries.first().remove();
  }
}

function trainingCompleted(response) {
  console.log("Training completed:", response);

  // Stop monitoring
  stopMonitoring();

  // Update status
  updateTrainingStatus("completed", "Training Completed Successfully");

  // Update progress to 100%
  $("#overallProgress").text("100%");
  $("#overallProgressBar").css("width", "100%");

  // Mark all phases as completed
  $(".training-phase").addClass("completed");
  $(".phase-icon").addClass("completed");

  // Show results
  showTrainingResults(response.results);

  // Log completion
  addLogMessage("success", "Training completed successfully!");
  addLogMessage(
    "info",
    `Final accuracy: ${(response.results.final_accuracy * 100).toFixed(2)}%`
  );

  showAlert(
    "success",
    "Training Completed",
    `Model retraining completed successfully! Final accuracy: ${(
      response.results.final_accuracy * 100
    ).toFixed(2)}%`
  );
}

function trainingError(response) {
  console.error("Training error:", response);

  // Stop monitoring
  stopMonitoring();

  // Update status
  updateTrainingStatus("error", "Training Failed");

  // Log error
  addLogMessage("error", `Training failed: ${response.error}`);

  showAlert("danger", "Training Failed", response.error);

  // Reset UI
  setTimeout(() => {
    resetTrainingUI();
  }, 5000);
}

function showTrainingResults(results) {
  // Show results container
  $("#resultsContainer").show();

  // Performance comparison
  const comparisonHtml = `
        <div class="row">
            <div class="col-6">
                <div class="text-center">
                    <div class="h4 text-muted">Before</div>
                    <div class="h2">${(results.old_accuracy * 100).toFixed(
                      2
                    )}%</div>
                </div>
            </div>
            <div class="col-6">
                <div class="text-center">
                    <div class="h4 text-success">After</div>
                    <div class="h2 text-success">${(
                      results.final_accuracy * 100
                    ).toFixed(2)}%</div>
                </div>
            </div>
        </div>
        <div class="text-center mt-3">
            <div class="h5 ${
              results.improvement > 0 ? "text-success" : "text-warning"
            }">
                ${results.improvement > 0 ? "+" : ""}${(
    results.improvement * 100
  ).toFixed(2)}% improvement
            </div>
        </div>
    `;
  $("#performanceComparison").html(comparisonHtml);

  // Model details
  const detailsHtml = `
        <ul class="list-group list-group-flush">
            <li class="list-group-item d-flex justify-content-between">
                <span>Training Time:</span>
                <span>${formatDuration(results.training_time)}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
                <span>Training Samples:</span>
                <span>${results.training_samples.toLocaleString()}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
                <span>Validation Accuracy:</span>
                <span>${(results.validation_accuracy * 100).toFixed(2)}%</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
                <span>Test Accuracy:</span>
                <span>${(results.test_accuracy * 100).toFixed(2)}%</span>
            </li>
            <li class="list-group-item d-flex justify-content-between">
                <span>Model Size:</span>
                <span>${formatFileSize(results.model_size)}</span>
            </li>
        </ul>
    `;
  $("#modelDetails").html(detailsHtml);
}

function cancelTraining() {
  if (!currentTrainingId) {
    resetTrainingUI();
    return;
  }

  if (
    !confirm(
      "Are you sure you want to cancel the training? Progress will be lost."
    )
  ) {
    return;
  }

  $.ajax({
    url: "/lottery-prediction/api/retrain-cancel/",
    method: "POST",
    data: JSON.stringify({ training_id: currentTrainingId }),
    contentType: "application/json",
    headers: {
      "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
    },
    success: function (response) {
      console.log("Training cancelled:", response);

      // Stop monitoring
      stopMonitoring();

      // Update status
      updateTrainingStatus("cancelled", "Training Cancelled");

      // Log cancellation
      addLogMessage("warning", "Training cancelled by user");

      showAlert(
        "warning",
        "Training Cancelled",
        "Model retraining has been cancelled."
      );

      // Reset UI after delay
      setTimeout(() => {
        resetTrainingUI();
      }, 3000);
    },
    error: function (xhr, status, error) {
      console.error("Failed to cancel training:", error);
      showAlert(
        "danger",
        "Cancellation Error",
        "Failed to cancel training: " + error
      );
    },
  });
}

function deployModel() {
  if (!currentTrainingId) return;

  if (
    !confirm(
      "Deploy the new model to production? This will replace the current active model."
    )
  ) {
    return;
  }

  $.ajax({
    url: "/lottery-prediction/api/deploy-model/",
    method: "POST",
    data: JSON.stringify({ training_id: currentTrainingId }),
    contentType: "application/json",
    headers: {
      "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
    },
    success: function (response) {
      console.log("Model deployed:", response);
      showAlert(
        "success",
        "Deployment Successful",
        "New model has been deployed to production."
      );

      // Redirect to performance page after delay
      setTimeout(() => {
        window.location.href = "/lottery-prediction/performance/";
      }, 2000);
    },
    error: function (xhr, status, error) {
      console.error("Failed to deploy model:", error);
      showAlert(
        "danger",
        "Deployment Error",
        "Failed to deploy model: " + error
      );
    },
  });
}

function backupOldModel() {
  $.ajax({
    url: "/lottery-prediction/api/backup-model/",
    method: "POST",
    headers: {
      "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
    },
    success: function (response) {
      console.log("Model backed up:", response);
      showAlert(
        "success",
        "Backup Created",
        "Old model has been backed up successfully."
      );
    },
    error: function (xhr, status, error) {
      console.error("Failed to backup model:", error);
      showAlert("danger", "Backup Error", "Failed to backup model: " + error);
    },
  });
}

function downloadTrainingLogs() {
  if (!currentTrainingId) return;

  const url = `/lottery-prediction/api/download-logs/?training_id=${currentTrainingId}`;
  const a = document.createElement("a");
  a.href = url;
  a.download = `training_logs_${currentTrainingId}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function pauseTraining() {
  // Implementation for pausing training
  showAlert(
    "info",
    "Feature Coming Soon",
    "Training pause/resume functionality will be available in a future update."
  );
}

function resumeTrainingMonitoring(trainingInfo) {
  // Resume monitoring ongoing training
  currentTrainingId = trainingInfo.training_id;

  // Show progress container
  $("#progressContainer").show();
  $("#retrainForm :input").prop("disabled", true);
  $("#startRetrainBtn").prop("disabled", true);
  $("#cancelBtn").show();

  // Update status
  updateTrainingStatus("training", "Training in Progress");

  // Start monitoring
  startProgressMonitoring();

  // Restart timer
  trainingStartTime = new Date(trainingInfo.start_time);
  startTrainingTimer();

  showAlert(
    "info",
    "Training Resumed",
    "Resuming monitoring of ongoing training session."
  );
}

function startTrainingTimer() {
  if (trainingTimer) {
    clearInterval(trainingTimer);
  }

  trainingTimer = setInterval(() => {
    if (trainingStartTime) {
      const elapsed = new Date() - trainingStartTime;
      const hours = Math.floor(elapsed / 3600000);
      const minutes = Math.floor((elapsed % 3600000) / 60000);
      const seconds = Math.floor((elapsed % 60000) / 1000);

      $("#trainingTime").text(
        `${hours.toString().padStart(2, "0")}:${minutes
          .toString()
          .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`
      );
    }
  }, 1000);
}

function stopMonitoring() {
  if (progressInterval) {
    clearInterval(progressInterval);
    progressInterval = null;
  }

  if (logInterval) {
    clearInterval(logInterval);
    logInterval = null;
  }

  if (trainingTimer) {
    clearInterval(trainingTimer);
    trainingTimer = null;
  }
}

function resetTrainingUI() {
  // Re-enable form
  $("#retrainForm :input").prop("disabled", false);
  $("#startRetrainBtn").prop("disabled", false);
  $("#cancelBtn").hide();

  // Hide progress container
  $("#progressContainer").hide();
  $("#resultsContainer").hide();

  // Reset variables
  currentTrainingId = null;
  trainingStartTime = null;

  // Stop monitoring
  stopMonitoring();
}

function resetProgress() {
  $("#overallProgress").text("0%");
  $("#overallProgressBar").css("width", "0%");

  // Reset phases
  $(".training-phase").removeClass("active completed");
  $(".phase-icon").removeClass("active completed");

  // Reset metrics
  $("#currentAccuracy").text("--");
  $("#trainingLoss").text("--");
  $("#validationLoss").text("--");
  $("#epochCount").text("0");

  // Clear logs
  $("#trainingLog").html('<div class="text-muted">Training starting...</div>');
}

function updateTrainingStatus(status, message) {
  const statusElement = $("#trainingStatus");

  // Remove all status classes
  statusElement.removeClass(
    "status-idle status-training status-completed status-error status-cancelled"
  );

  // Add appropriate class and text
  switch (status) {
    case "training":
      statusElement.addClass("status-training").text(message);
      break;
    case "completed":
      statusElement.addClass("status-completed").text(message);
      break;
    case "error":
    case "cancelled":
      statusElement.addClass("status-error").text(message);
      break;
    default:
      statusElement.addClass("status-idle").text(message);
  }
}

function showAlert(type, title, message) {
  const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show alert-box" role="alert">
            <i class="fas fa-${
              type === "danger"
                ? "exclamation-triangle"
                : type === "warning"
                ? "exclamation-circle"
                : type === "success"
                ? "check-circle"
                : "info-circle"
            }"></i>
            <strong>${title}:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

  $("#retrainAlerts").append(alertHtml);
  $("#alertContainer").show();

  // Auto-hide after 10 seconds for success/info
  if (type === "success" || type === "info") {
    setTimeout(() => {
      $(".alert").last().fadeOut();
    }, 10000);
  }
}

// Utility functions
function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString();
}

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
}

function formatFileSize(bytes) {
  const sizes = ["Bytes", "KB", "MB", "GB"];
  if (bytes === 0) return "0 Bytes";

  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + " " + sizes[i];
}

// Cleanup on page unload
$(window).on("beforeunload", function () {
  stopMonitoring();
});
