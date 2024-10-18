const backendUrl = 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('authToken');
}

// Redirect to login if token is not present
if (!getToken()) {
  window.location.href = 'index.html';
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