console.log('Worker script loaded');
let sse = null;
let ws = null;

let token = null;  // Store the token received from the main thread

// Connect to the Notification Service (SSE)
function connectToSSE() {
  console.log('Connecting to SSE');
  console.log('Token:', token);
  if (!token) return; 

  sse = new EventSource(`http://localhost:8005/notification-stream?token=${token}`);
  console.log('SSE:', sse);

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
  if (!token) return;

  ws = new WebSocket(`ws://localhost:8004/ws/location?token=${token}`);

  ws.onopen = () => {
    console.log('WebSocket connected');
  };

  ws.onerror = (err) => console.error('WebSocket Error:', err);

  ws.onclose = () => {
    console.log('WebSocket closed');
  };
}


// Listen for messages from the main script
self.onconnect = (event) => {
  const port = event.ports[0];

  port.onmessage = (event) => {
      console.log('Worker message:', event.data);
      if (event.data.action === 'startWebSocket') {
          console.log('Starting WebSocket');
          connectToWebSocket();
      } else if (event.data.action === 'stopWebSocket') {
          if (ws) ws.close();
      } else if (event.data.action === 'setToken') {
          token = event.data.token;  // Store the token
          console.log('Token received in worker:', token);
          // Initialize the SSE connection
          connectToSSE();
      } else if (event.data.action === 'updateLocation') {
          const { driver_id, latitude, longitude } = event.data;
          console.log('Location received in worker:', driver_id, latitude, longitude);
          // Here you can send the location to your WebSocket or handle it as needed
          if (ws && ws.readyState === WebSocket.OPEN) {
              console.log('Sending location to WebSocket');
              ws.send(JSON.stringify({ driver_id, latitude, longitude }));
          }
      }
  };
};