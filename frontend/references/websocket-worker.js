// websocket-shared-worker.js
let socket;
let connections = 0;

// Open WebSocket connection
function initWebSocket() {
    socket = new WebSocket("ws://localhost:8000/ws/location");

    socket.onopen = () => {
        console.log("WebSocket connected.");
    };

    socket.onmessage = (event) => {
        console.log("Received message:", event.data);
        // Send message to all connected contexts (pages)
        broadcastToClients(event.data);
    };

    socket.onclose = (event) => {
        console.log("WebSocket disconnected, reconnecting...");
        setTimeout(initWebSocket, 5000); // Reconnect after 5s
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

// Broadcast messages to all connected contexts (pages/tabs)
function broadcastToClients(message) {
    clients.forEach((port) => port.postMessage(message));
}

// Handle connection requests from each tab/page
const clients = [];

onconnect = (event) => {
    const port = event.ports[0];
    clients.push(port);
    connections++;
    console.log(`New client connected. Total connections: ${connections}`);

    // Send initial message to the connected context
    port.postMessage({ message: "Connected to Shared Worker WebSocket" });

    // Handle messages sent from the connected page/tab
    port.onmessage = (event) => {
        const { type, payload } = event.data;

        if (type === "send") {
            // Send a message to the server via WebSocket
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify(payload));
            } else {
                console.warn("WebSocket is not open.");
            }
        }
    };

    // Handle disconnection
    port.onclose = () => {
        connections--;
        console.log(`Client disconnected. Total connections: ${connections}`);
    };

    // Initialize WebSocket if it’s not already open
    if (!socket || socket.readyState === WebSocket.CLOSED) {
        initWebSocket();
    }
};