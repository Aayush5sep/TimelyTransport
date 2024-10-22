const backendUrl = 'http://localhost:8000';

// Helper to get token from localStorage
function getToken() {
  return localStorage.getItem('authToken');
}

// Redirect to login if token is not present
if (!getToken()) {
  window.location.href = 'index.html';
}

// Parse JWT token to extract user information
let token_payload = {};
function parseJwt() {
  try {
      const token = getToken();
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
          atob(base64).split('').map(function (c) {
              return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
          }).join('')
      );

      token_payload = JSON.parse(jsonPayload);
  } catch (error) {
      console.error('Invalid token:', error);
      return {};
  }
}
parseJwt();

// Helper to remove token and redirect to login page
function removeToken() {
  localStorage.removeItem('authToken');
  window.location.href = 'index.html';
}

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

// Display a popup with the notification and buttons
function displayNotificationPopup(message) {
  const popup = document.createElement('div');
  popup.className = 'notification-popup';
  popup.innerHTML = `
    <p>${message}</p>
    <button id="acceptButton">Accept</button>
    <button id="rejectButton">Reject</button>
  `;

  document.body.appendChild(popup);

  document.getElementById('acceptButton').addEventListener('click', () => {
    console.log('Accepted');
    popup.remove();
  });

  document.getElementById('rejectButton').addEventListener('click', () => {
    console.log('Rejected');
    popup.remove();
  });
}

// Fetch and display user profile
async function fetchUserProfile() {
  const token = getToken();
  try {
    const response = await fetch(`${backendUrl}/auth/profile`, {
      headers: { 'token': `${token}` },
    });
    const data = await response.json();
    if (response.ok) {
      return data;
    } else {
      console.error('Failed to fetch profile:', data.message);
      removeToken();
    }
  } catch (error) {
    console.error('Error fetching profile:', error);
    removeToken();
  }
}


let locationUpdateInterval;
// Initialize the dashboard
async function initializeDashboard() {
  const profile = await fetchUserProfile();
  if (!profile) return;

  document.getElementById('profileBox').innerHTML = `
    <h3>Welcome, ${profile.name}</h3>
    <p>Phone: ${profile.phone_number}</p>
    <p>Email: ${profile.email}</p>
    <p>User Type: ${profile.user}</p>
  `;

  const userActionButtons = document.getElementById('userActionButtons');
  if (profile.user === 'customer') {
    userActionButtons.innerHTML = `
      <button id="newBookingButton">Request New Booking</button>
    `;
    document.getElementById('newBookingButton').addEventListener('click', () => {
      window.location.href = 'bookingrequest.html';
    });
  } else if (profile.user === 'driver') {
    const isActive = localStorage.getItem('rideActive') === 'true';

    userActionButtons.innerHTML = `
      <label>
        <input type="checkbox" id="activationToggle" ${isActive ? 'checked' : ''}>
        Start Accepting Rides
      </label>
    `;

    const activationToggle = document.getElementById('activationToggle');
    activationToggle.addEventListener('change', (e) => {
      console.log('Toggle:', e.target.checked);
      const isActive = e.target.checked;
      localStorage.setItem('rideActive', isActive);
      if (isActive) {
        console.log('Starting WebSocket');
        worker.port.postMessage({ action: 'startWebSocket' });
        locationUpdateInterval = setInterval(startGeolocationUpdates, 5000);
      } else {
        worker.port.postMessage({ action: 'stopWebSocket' });
        clearInterval(locationUpdateInterval);
      }
    });

    if (isActive) {
      worker.port.postMessage({ action: 'startWebSocket' });
      locationUpdateInterval = setInterval(startGeolocationUpdates, 5000);
    }
  }
}

// Call the initialize function on page load
initializeDashboard();

document.getElementById('activeTripButton').addEventListener('click', () => {
  window.location.href = 'activetrip.html'; // Redirect to Active Trip page
});

document.getElementById('tripHistoryButton').addEventListener('click', () => {
  window.location.href = 'tripshistory.html'; // Redirect to Trip History page
});

// Logout functionality
document.getElementById('logoutButton').addEventListener('click', () => {
  removeToken();
});