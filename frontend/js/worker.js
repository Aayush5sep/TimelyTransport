console.log('Worker script loaded');
let sse = null;
let ws = null;
let token = null;  // Store the token received from the main thread
const ports = [];  // Store connected ports from different tabs

// Function to broadcast messages to all connected clients
function broadcastToClients(message) {
  ports.forEach((port) => port.postMessage(message));
}

// Connect to the Notification Service (SSE)
function connectToSSE() {
  console.log('Connecting to SSE');
  if (!token) return;

  // Close existing SSE connection if open
  if (sse) {
    sse.close();
    console.log('Existing SSE connection closed.');
  }

  sse = new EventSource(`http://localhost:8005/notification-stream?token=${token}`);
  console.log('SSE:', sse);

  sse.onmessage = (event) => {
    // console.log('Notification:', event.data);
    // Broadcast the message to all connected clients (tabs)
    broadcastToClients({ type: 'notification', data: event.data });
  };

  sse.onerror = (error) => {
    console.error('SSE Error:', error);
    // Optionally reconnect on error (depending on your requirements)
  };
}

// Connect to WebSocket for sending location updates
function connectToWebSocket() {
  if (!token) return;

  // Close existing WebSocket connection if open
  if (ws) {
    ws.close();
    console.log('Existing WebSocket connection closed.');
  }

  ws = new WebSocket(`ws://localhost:8004/ws/location?token=${token}`);

  ws.onopen = () => {
    console.log('WebSocket connected');
  };

  ws.onerror = (err) => console.error('WebSocket Error:', err);

  ws.onclose = () => {
    console.log('WebSocket closed');
  };
}

// Handle messages from connected clients (tabs)
self.onconnect = (event) => {
  const port = event.ports[0];
  ports.push(port);  // Store the connected port
  console.log('New client connected to shared worker.');

  // Listen for messages from this client
  port.onmessage = (event) => {
    const data = event.data;
    console.log('Worker message:', data);

    switch (data.action) {
      case 'setToken':
        token = data.token;  // Store the token
        console.log('Token received in worker:', token);
        connectToSSE();  // Initialize the SSE connection
        break;

      case 'startWebSocket':
        console.log('Starting WebSocket');
        connectToWebSocket();  // Initialize WebSocket connection
        break;

      case 'stopWebSocket':
        console.log('Stopping WebSocket');
        if (ws) ws.close();  // Close WebSocket connection
        break;

      case 'updateLocation':
        const { driver_id, latitude, longitude } = data;
        console.log('Location received in worker:', driver_id, latitude, longitude);

        // Send location update via WebSocket if connected
        if (ws && ws.readyState === WebSocket.OPEN) {
          console.log('Sending location to WebSocket');
          ws.send(JSON.stringify({ driver_id, latitude, longitude }));
        }
        break;

      default:
        console.warn('Unknown action:', data.action);
    }
  };

  // Clean up: Remove the port when it disconnects
  port.onclose = () => {
    console.log('Client disconnected from shared worker.');
    const index = ports.indexOf(port);
    if (index > -1) ports.splice(index, 1);  // Remove the port
  };
};
