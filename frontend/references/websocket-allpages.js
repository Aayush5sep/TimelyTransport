// Check if Shared Workers are supported
if (window.SharedWorker) {
    const worker = new SharedWorker("/websocket-shared-worker.js");

    // Listen for messages from the worker
    worker.port.onmessage = (event) => {
        console.log("Message from Shared Worker:", event.data);
    };

    // Send a message to the Shared Worker (example: send location data)
    function sendMessageToWebSocket(type, payload) {
        worker.port.postMessage({ type, payload });
    }

    // Example: Sending driver location updates
    sendMessageToWebSocket("send", { driver_id: "123", latitude: 37.7749, longitude: -122.4194 });

    // Start the communication with the worker
    worker.port.start();
} else {
    console.error("Shared Workers are not supported in this browser.");
}