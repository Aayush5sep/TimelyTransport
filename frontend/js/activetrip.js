const backendUrl = 'http://localhost:8002'; // Replace with your backend URL

// Get token from localStorage
function getToken() {
    return localStorage.getItem('authToken');
}

// Redirect to login if token is not present
if (!getToken()) {
    window.location.href = 'index.html';
}

const olaMaps = new OlaMapsSDK.OlaMaps({
    apiKey: 'OyIE1iZDygLFJkrzgVxKLeufCGHd3UHLblmHWFSa' // Replace with your API key
});

let homeLocation = { latitude: 0, longitude: 0 };
let map;
let driverMarker;
let driverLocation = { latitude: 12.9716, longitude: 77.5946 }; // Initial placeholder for driver's location

// Import the shared worker
import { getSharedWorker } from 'js/workerSingleton.js';
const worker = getSharedWorker();
worker.port.start();  // Ensure port is active
worker.port.postMessage({ action: 'setToken', token: getToken() });

// Listen for notifications from the worker
worker.port.onmessage = (event) => {
    if (event.data.type === 'notification') {
        displayNotificationPopup(event.data.data);
    }
};

// Handle geolocation and send updates to the worker
function startGeolocationUpdates() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            const { latitude, longitude } = position.coords;
            // Send location data to the worker
            worker.port.postMessage({ action: 'updateLocation', driver_id: token_payload.user_id, latitude: latitude, longitude: longitude });
            console.log('Location sent to worker:', latitude, longitude);
        }, (error) => {
            console.error('Geolocation error:', error);
        });
    } else {
        console.error('Geolocation is not supported by this browser.');
    }
}

// Fetch active trip from the backend
async function fetchActiveTrip() {
    const token = getToken();
    try {
        const response = await fetch(`${backendUrl}/active`, {
            headers: { 'token': `${token}` },
        });

        const data = await response.json();
        if (response.ok) {
            renderTrip(data);
        } else {
            handleError(data);
        }
    } catch (error) {
        console.error('Error fetching active trip:', error);
        removeToken();
    }
}

// Handle errors and display appropriate messages
function handleError(data) {
    console.error('Error:', data.message);
    const tripDetails = document.getElementById('tripDetails');
    tripDetails.innerHTML = `<p class="error">${data.message}</p>`;
}

// Render trip details and map based on user type
function renderTrip(data) {
    const { active_trip, tracking_token } = data;

    const tripDetails = document.getElementById('tripDetails');
    tripDetails.innerHTML = `
        <h4>Trip ID: ${active_trip.id}</h4>
        <p>Customer ID: ${active_trip.customer_id}</p>
        <p>Driver ID: ${active_trip.driver_id}</p>
        <p>Source: ${active_trip.source_address}</p>
        <p>Destination: ${active_trip.destination_address}</p>
        <p>Status: ${active_trip.status}</p>
        <p>Started At: ${new Date(active_trip.startedAt).toLocaleString()}</p>
    `;

    // Check user type
    const userType = localStorage.getItem('userType'); // Assume user type is stored in local storage
    if (userType === 'driver') {
        renderDriverMap(active_trip);
    } else if (userType === 'customer') {
        connectToWebSocket(tracking_token);
        renderCustomerMap(active_trip);
    }
}

// Initialize the Ola Map for the driver
function renderDriverMap(active_trip) {
    const { source_location, destination_location, status } = active_trip;

    // Initialize the map centered at the driver's current location
    map = olaMaps.init({
        style: 'https://api.olamaps.io/tiles/vector/v1/styles/default-light-standard/style.json',
        container: 'mapContainer',
        center: [source_location.longitude, source_location.latitude],
        zoom: 15,
    });

    // Initial driver marker
    driverMarker = olaMaps.addMarker({
        offset: [0, -10],
        anchor: 'bottom',
        color: 'red',
        draggable: false
    })
    .setLngLat([driverLocation.longitude, driverLocation.latitude])
    .addTo(map);

    // Source and Destination Markers
    if (status === 'ACCEPTED') {
        olaMaps.addMarker({
            offset: [0, -10],
            anchor: 'bottom',
            color: 'blue',
        })
        .setLngLat([source_location.longitude, source_location.latitude])
        .addTo(map);
    }

    if (status === 'STARTED') {
        olaMaps.addMarker({
            offset: [0, -10],
            anchor: 'bottom',
            color: 'green',
        })
        .setLngLat([destination_location.longitude, destination_location.latitude])
        .addTo(map);
    }

    // Start updating the driver's location every 2 seconds
    setInterval(updateDriverLocation, 2000);
}

// Update driver location using Geolocation API
function updateDriverLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            driverLocation.latitude = position.coords.latitude;
            driverLocation.longitude = position.coords.longitude;

            // Update the driver marker position
            driverMarker.setLngLat([driverLocation.longitude, driverLocation.latitude]);
            map.setCenter([driverLocation.longitude, driverLocation.latitude]); // Center map to driver's new location
        }, (error) => {
            console.error('Error getting location:', error);
        });
    } else {
        console.error('Geolocation is not supported by this browser.');
    }
}

// Initialize the Ola Map for the customer
function renderCustomerMap(active_trip) {
    const { source_location, destination_location } = active_trip;

    // Initialize the map centered at the source location
    map = olaMaps.init({
        style: 'https://api.olamaps.io/tiles/vector/v1/styles/default-light-standard/style.json',
        container: 'mapContainer',
        center: [source_location.longitude, source_location.latitude],
        zoom: 15,
    });

    // Markers for Source and Destination
    olaMaps.addMarker({
        offset: [0, -10],
        anchor: 'bottom',
        color: 'blue',
    })
    .setLngLat([source_location.longitude, source_location.latitude])
    .addTo(map);

    olaMaps.addMarker({
        offset: [0, -10],
        anchor: 'bottom',
        color: 'green',
    })
    .setLngLat([destination_location.longitude, destination_location.latitude])
    .addTo(map);

    // This marker will be updated via WebSocket
    driverMarker = olaMaps.addMarker({
        offset: [0, -10],
        anchor: 'bottom',
        color: 'red',
    })
    .setLngLat([0, 0]) // Initial position will be updated by WebSocket
    .addTo(map);
}

// Connect to WebSocket to receive driver location updates for customer
function connectToWebSocket(tracking_token) {
    const socket = new WebSocket(`ws://localhost:8004/ws/driver-location?token=${getToken()}&tracking_token=${tracking_token}`);

    socket.onopen = () => {
        console.log("WebSocket connection established.");
    };

    socket.onmessage = (event) => {
        const driverInfo = JSON.parse(event.data);
        const { latitude, longitude } = driverInfo;

        // Update customer marker position
        driverMarker.setLngLat([longitude, latitude]);
        map.setCenter([longitude, latitude]); // Center map to driver's location
    };

    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
        console.log('WebSocket connection closed.');
    };
}

// Display a popup with the notification and buttons
function displayNotificationPopup(message) {
    const popup = document.createElement('div');
    popup.className = 'notification-popup';
    popup.innerHTML = `
        <p>${message}</p>
        <button id="acceptButton">Ok</button>
        <button id="rejectButton">Cancel</button>
    `;

    document.body.appendChild(popup);

    document.getElementById('acceptButton').addEventListener('click', () => {
        console.log('Ok');
        popup.remove();
    });

    document.getElementById('rejectButton').addEventListener('click', () => {
        console.log('Cancel');
        popup.remove();
    });
}

// Logout functionality
document.getElementById('logoutButton').addEventListener('click', () => {
    removeToken();
});

// Call the fetch function on page load
fetchActiveTrip();

let locationUpdateInterval;
isActive = localStorage.getItem('rideActive');
if (isActive) {
  console.log('Starting WebSocket');
  worker.port.postMessage({ action: 'startWebSocket' });
  locationUpdateInterval = setInterval(startGeolocationUpdates, 5000);
} else {
  worker.port.postMessage({ action: 'stopWebSocket' });
  clearInterval(locationUpdateInterval);
}