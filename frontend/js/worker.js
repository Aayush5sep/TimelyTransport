let sse = null;
let ws = null;
let locationInterval = null;

// Connect to the Notification Service (SSE)
function connectToSSE() {
  const token = localStorage.getItem('authToken'); 
  if (!token) return; 

  sse = new EventSource(`http://localhost:8000/notifications?token=${token}`);

  sse.onmessage = (event) => {
    console.log('Notification:', event.data); 
    self.postMessage({ type: 'notification', data: event.data });
  };

  sse.onerror = (error) => {
    console.error('SSE Error:', error);
  };
}

// Connect to WebSocket for sending location updates
function connectToWebSocket() {
  const token = localStorage.getItem('authToken');
  if (!token) return;

  ws = new WebSocket(`ws://localhost:8000/location?token=${token}`);

  ws.onopen = () => {
    console.log('WebSocket connected');
    startLocationUpdates(); // Start sending location every 5 seconds
  };

  ws.onerror = (err) => console.error('WebSocket Error:', err);

  ws.onclose = () => {
    console.log('WebSocket closed');
    stopLocationUpdates();
  };
}

// Start sending the current location every 5 seconds
function startLocationUpdates() {
  if (locationInterval) return;

  locationInterval = setInterval(() => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ lat: latitude, lng: longitude }));
          console.log('Location sent:', latitude, longitude);
        }
      },
      (error) => console.error('Geolocation error:', error),
      { enableHighAccuracy: true }
    );
  }, 5000);
}

// Stop location updates by clearing the interval
function stopLocationUpdates() {
  if (locationInterval) {
    clearInterval(locationInterval);
    locationInterval = null;
  }
}

// Initialize the SSE connection
connectToSSE();

// Listen for messages from the main script
self.onmessage = (event) => {
  if (event.data.action === 'startWebSocket') {
    connectToWebSocket();
  } else if (event.data.action === 'stopWebSocket') {
    if (ws) ws.close();
  }
};