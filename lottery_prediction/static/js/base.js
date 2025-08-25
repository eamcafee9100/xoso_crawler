// Initialize tooltips
const tooltipTriggerList = [].slice.call(
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
);
tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Enhanced notification functions
function showNotification(type, message, duration = 5000) {
  const toastHtml = `
        <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="${duration}">
            <div class="toast-header bg-${
              type === "error" ? "danger" : type
            } text-white">
                <strong class="me-auto">
                    ${
                      type === "error"
                        ? "❌ Error"
                        : type === "success"
                        ? "✅ Success"
                        : "ℹ️ Info"
                    }
                </strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

  const toastContainer =
    document.getElementById("toastContainer") ||
    document.getElementById("notificationArea");
  if (toastContainer) {
    toastContainer.insertAdjacentHTML("beforeend", toastHtml);

    // Initialize Bootstrap toast
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    // Remove element after it's hidden
    toastElement.addEventListener("hidden.bs.toast", () => {
      toastElement.remove();
    });
  } else {
    // Fallback to alert if no container
    alert(`${type.toUpperCase()}: ${message}`);
  }
}

// Global CSRF token helper
function getCSRFToken() {
  return (
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    document
      .querySelector('meta[name="csrf-token"]')
      ?.getAttribute("content") ||
    $("[name=csrfmiddlewaretoken]").val()
  );
}

// Handle CSRF token for AJAX requests
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Set up AJAX headers
$.ajaxSetup({
  headers: { "X-CSRFToken": getCookie("csrftoken") },
});
