const backendUrl = 'http://localhost:8002';

// Helper to get token from localStorage
function getToken() {
  return localStorage.getItem('authToken');
}

// Helper to remove token and redirect to login page
function removeToken() {
  localStorage.removeItem('authToken');
  window.location.href = 'login.html';
}

// Redirect to login if token is not present
if (!getToken()) {
  window.location.href = 'login.html';
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

// Initialize the shared worker
const worker = new SharedWorker('js/worker.js');
worker.port.start();  // Ensure port is active

// Listen for notifications from the worker
worker.port.onmessage = (event) => {
  if (event.data.type === 'notification') {
    displayNotificationPopup(event.data.data);
  }
};

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
      console.error('Failed to fetch completed trips:', data.message);
      removeToken();
    }
  } catch (error) {
    console.error('Error fetching completed trips:', error);
    removeToken();
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

// Logout functionality
document.getElementById('logoutButton').addEventListener('click', () => {
  removeToken();
});