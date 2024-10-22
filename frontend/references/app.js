let worker = null;
const token = JSON.parse(localStorage.getItem("driver_token"));
const isActivated = JSON.parse(localStorage.getItem("is_activated")) || false;

const dashboardContainer = document.getElementById("dashboard-container");
const activationButton = document.getElementById("activation-btn");
const logoutButton = document.getElementById("logout-btn");
const notificationsContainer = document.getElementById("notifications");

// Redirect to login if token is missing
if (!token) {
    window.location.href = "index.html";
} else {
    initWorker();
    dashboardContainer.style.display = "block";
    if (isActivated) activateConnections();
}

// Initialize Web Worker
function initWorker() {
    // Use Shared Web Worker to ensure a single instance
    worker = new SharedWorker("worker.js");

    // Listen for messages from the worker
    worker.port.onmessage = (event) => handleWorkerMessage(event.data);

    // Start the worker only if the activation is enabled
    if (isActivated) {
        worker.port.postMessage({ action: "start", token });
    }
}

// Activation button logic
activationButton.onclick = () => {
    const isActivated = JSON.parse(localStorage.getItem("is_activated")) || false;
    if (isActivated) stopWorkerConnections();
    else activateConnections();
};

// Start worker connections
function activateConnections() {
    worker.port.postMessage({ action: "start", token });
    localStorage.setItem("is_activated", JSON.stringify(true));
    document.getElementById("activation-btn").textContent = "Deactivate";
}

// Stop worker connections
function stopConnections() {
    worker.port.postMessage({ action: "stop" });
    localStorage.setItem("is_activated", JSON.stringify(false));
    document.getElementById("activation-btn").textContent = "Activate";
}

// Display notifications in the UI
function handleWorkerMessage(data) {
    if (data.type === "notification") {
        const { message, status, params } = data.data;  // Extract message and status
        displayNotification(message, status);   // Pass both to the display function
    } else if (data.type === "location_ack") {
        console.log("Location acknowledged:", data.data);
    }
}

// Display notification with status-based styling
function displayNotification(message, status) {
    const notification = document.createElement("div");
    notification.className = "notification";
    notification.textContent = message;

    // Apply styling based on the status
    switch (status) {
        case "warning":
            notification.style.backgroundColor = "orange";
            notification.style.color = "white";
            break;
        case "error":
            notification.style.backgroundColor = "red";
            notification.style.color = "white";
            break;
        case "info":
            notification.style.backgroundColor = "blue";
            notification.style.color = "white";
            break;
        default:
            notification.style.backgroundColor = "green";  // Default for normal messages
            notification.style.color = "white";
    }

    // Append notification to the container
    notificationsContainer.appendChild(notification);

    // Auto-remove notification after 5 seconds
    setTimeout(() => {
        notificationsContainer.removeChild(notification);
    }, 5000);
}


// Logout handler
logoutButton.onclick = () => {
    localStorage.removeItem("driver_token");
    localStorage.removeItem("is_activated");
    worker.postMessage({ action: "stop" });
    window.location.href = "index.html";
};