const backendUrl = 'http://localhost:8002';

// Helper to get token from localStorage
function getToken() {
  return localStorage.getItem('authToken');
}

// Helper to remove token and redirect to login page
function removeToken() {
  localStorage.clear();
  window.location.href = 'index.html';
}

// Redirect to login if token is not present
if (!getToken()) {
  window.location.href = 'index.html';
}

// Parse JWT token to extract user information
function parseJwt(token) {
  try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
          atob(base64).split('').map(function (c) {
              return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
          }).join('')
      );

      return JSON.parse(jsonPayload);
  } catch (error) {
      console.error('Invalid token:', error);
      return {};
  }
}
const token_payload = parseJwt(getToken());

// Import the shared worker
import { getSharedWorker } from './workerSingleton.js';
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

// Display a popup with the notification and buttons
function displayNotificationPopup(message) {
  const displayMessage = message;
  if(message.status === 'trip_request') {
    const parsedMessage = JSON.parse(message);
    const tripDetails = parsedMessage.params;
    displayMessage = `
      <p><strong>New Trip Request</strong></p>
      <p><strong>From:</strong> ${tripDetails.source_address}</p>
      <p><strong>To:</strong> ${tripDetails.destination_address}</p>
      <p><strong>Vehicle Type:</strong> ${tripDetails.vehicle_type}</p>
    `;
  }
  const popup = document.createElement('div');
  popup.className = 'notification-popup';
  popup.innerHTML = `
    <p>${displayMessage}</p>
    <button id="acceptButton">Accept</button>
    <button id="rejectButton">Reject</button>
  `;

  document.body.appendChild(popup);

  document.getElementById('acceptButton').addEventListener('click', () => {
    const token = getToken();
    const parsedMessage = JSON.parse(message);
    const requestBody = {
      customer_id: parsedMessage.params.user_id,
      driver_id: token_payload.user_id,
      status: 'accepted'
    };

    fetch('http://localhost:8001/driver/response', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'token': token
      },
      body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log('Response sent successfully:', data);
        setTimeout(() => {
          window.location.href = 'activetrip.html';
        }, 2000);
      } else {
        console.error('Failed to send response:', data.message);
      }
    })
    .catch(error => {
      console.error('Error sending response:', error);
    });

    popup.remove();
  });

  document.getElementById('rejectButton').addEventListener('click', () => {
    const token = getToken();
    const parsedMessage = JSON.parse(message);
    const requestBody = {
      customer_id: parsedMessage.params.user_id,
      driver_id: token_payload.user_id,
      status: 'denied'
    };

    fetch('http://localhost:8001/driver/response', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'token': token
      },
      body: JSON.stringify(requestBody)
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log('Response sent successfully:', data);
        setTimeout(() => {
          window.location.href = 'activetrip.html';
        }, 2000);
      } else {
        console.error('Failed to send response:', data.message);
      }
    })
    .catch(error => {
      console.error('Error sending response:', error);
    });

    popup.remove();
  });
}

// Fetch completed trips from the backend
async function fetchCompletedTrips() {
  const token = getToken();
  try {
    const response = await fetch(`${backendUrl}/bookings/completed`, {
      headers: { 'token': `${token}` },
    });

    const data = await response.json();
    if (response.ok) {
      renderTrips(data);
    } else {
      alert('Failed to fetch completed trips:', data.message);
      window.location.href = 'index.html';
    }
  } catch (error) {
    alert('Error fetching completed trips:', error);
    window.location.href = 'index.html';
  }
}

// Render trips in the trips list
function renderTrips(trips) {
  const tripsList = document.getElementById('tripsList');
  tripsList.innerHTML = ''; // Clear existing trips
  trips.forEach(trip => {
    const tripItem = document.createElement('div');
    tripItem.className = 'trip-item';
    tripItem.innerHTML = `
      <h4>Trip ID: ${trip.id}</h4>
      <p>Customer ID: ${trip.customer_id}</p>
      <p>Driver ID: ${trip.driver_id}</p>
      <p>Source: ${trip.source_address} (Lat: ${trip.source_location.lat}, Lng: ${trip.source_location.lng})</p>
      <p>Destination: ${trip.destination_address} (Lat: ${trip.destination_location.lat}, Lng: ${trip.destination_location.lng})</p>
      <p>Status: ${trip.status}</p>
      <p>Started At: ${new Date(trip.startedAt).toLocaleString()}</p>
      <p>Ended At: ${new Date(trip.endedAt).toLocaleString()}</p>
      <hr>
    `;
    tripsList.appendChild(tripItem);
  });
}

// Call the fetch function on page load
fetchCompletedTrips();

let locationUpdateInterval;
const isActive = localStorage.getItem('rideActive');
if (isActive) {
  console.log('Starting WebSocket');
  worker.port.postMessage({ action: 'startWebSocket' });
  locationUpdateInterval = setInterval(startGeolocationUpdates, 5000);
} else {
  worker.port.postMessage({ action: 'stopWebSocket' });
  clearInterval(locationUpdateInterval);
}

// Logout functionality
document.getElementById('logoutButton').addEventListener('click', () => {
  removeToken();
});