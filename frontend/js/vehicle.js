const backendUrl = 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('authToken');
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

if (userDetails.user !== 'driver') {
  alert('Only drivers can access this page.');
  window.location.href = 'dashboard.html'; // Redirect to dashboard
}

document.getElementById('vehicleForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const token = getToken();
  const registrationNumber = document.getElementById('registrationNumber').value;
  const vehicleType = document.getElementById('vehicleType').value;
  const capacity = document.getElementById('capacity').value;

  // Construct the JSON payload with snake_case keys
  const vehicleData = {
    registration_number: registrationNumber,
    vehicle_type: vehicleType,
    capacity: capacity,
  };

  try {
    const response = await fetch(`${backendUrl}/vehicle/register`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'token': `${token}`
      },
      body: JSON.stringify(vehicleData)
    });

    if (response.ok) {
      // If registration is successful, attempt to refresh the token
      const refreshResponse = await fetch(`${backendUrl}/auth/refresh-token`, {
        method: 'POST',
        headers: { 'token': `${token}` }
      });

      const refreshData = await refreshResponse.json();
      if (refreshResponse.ok) {
        // Store the new token and redirect to the dashboard
        localStorage.setItem('authToken', refreshData.newToken);
        window.location.href = 'dashboard.html';
      } else {
        alert('Failed to refresh token');
      }
    } else {
      alert('Vehicle registration failed');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred during registration.');
  }
});