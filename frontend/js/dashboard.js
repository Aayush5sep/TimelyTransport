const backendUrl = 'http://localhost:8000';

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

// Initialize the dashboard
async function initializeDashboard() {
  const profile = await fetchUserProfile();
  if (!profile) return;

  document.getElementById('profileBox').innerHTML = `
    <h3>Welcome, ${profile.name}</h3>
    <p>Phone: ${profile.phone}</p>
    <p>Email: ${profile.email}</p>
    <p>User Type: ${profile.user_type}</p>
  `;

  const userActionButtons = document.getElementById('userActionButtons');
  if (profile.user_type === 'customer') {
    userActionButtons.innerHTML = `
      <button id="newBookingButton">Request New Booking</button>
    `;
    document.getElementById('newBookingButton').addEventListener('click', () => {
      window.location.href = 'bookingrequest.html';
    });
  } else if (profile.user_type === 'driver') {
    const isActive = localStorage.getItem('rideActive') === 'true';

    userActionButtons.innerHTML = `
      <label>
        <input type="checkbox" id="activationToggle" ${isActive ? 'checked' : ''}>
        Start Accepting Rides
      </label>
    `;

    const activationToggle = document.getElementById('activationToggle');
    activationToggle.addEventListener('change', (e) => {
      const isActive = e.target.checked;
      localStorage.setItem('rideActive', isActive);
      if (isActive) {
        worker.port.postMessage({ action: 'startWebSocket' });
      } else {
        worker.port.postMessage({ action: 'stopWebSocket' });
      }
    });

    if (isActive) {
      worker.port.postMessage({ action: 'startWebSocket' });
    }
  }
}

// Call the initialize function on page load
initializeDashboard();

document.getElementById('activeTripButton').addEventListener('click', () => {
  window.location.href = 'active-trip.html'; // Redirect to Active Trip page
});

document.getElementById('tripHistoryButton').addEventListener('click', () => {
  window.location.href = 'trip-history.html'; // Redirect to Trip History page
});

// Logout functionality
document.getElementById('logoutButton').addEventListener('click', () => {
  removeToken();
});