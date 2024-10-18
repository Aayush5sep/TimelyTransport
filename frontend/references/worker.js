let websocket = null;
let eventSource = null;
let locationInterval = null;
let user_id = null;
let user_type = null;

onconnect = (e) => {
    const port = e.ports[0];

    port.onmessage = (event) => {
        const { action, token } = event.data;

        if (action === "start") {
            ({ user_id, user_type } = token);
            startConnections();
        } else if (action === "stop") {
            stopConnections();
        }
    };

    // Send notifications or location acknowledgments to the connected page
    function sendToClient(data) {
        port.postMessage(data);
    }

    function startConnections() {
        if (!user_id || !user_type) {
            console.error("No user data available.");
            return;
        }

        // WebSocket connection
        websocket = new WebSocket(`ws://localhost:8001/location/${user_id}/${user_type}`);
        websocket.onmessage = (event) => sendToClient({ type: "location_ack", data: event.data });

        // SSE connection
        eventSource = new EventSource(`http://localhost:8000/stream/${user_id}/${user_type}`);
        eventSource.onmessage = (event) => sendToClient({ type: "notification", data: event.data });

        // Send location every 5 seconds
        locationInterval = setInterval(() => {
            navigator.geolocation.getCurrentPosition(
                (position) => sendLocation(position.coords),
                (error) => console.error("Geolocation error:", error)
            );
        }, 5000);
    }

    function sendLocation(coords) {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            const { latitude, longitude } = coords;
            websocket.send(JSON.stringify({ latitude, longitude }));
        }
    }

    function stopConnections() {
        if (websocket) websocket.close();
        if (eventSource) eventSource.close();
        clearInterval(locationInterval);
    }
};