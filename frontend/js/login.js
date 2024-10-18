const backendUrl = 'localhost:8000'; // Replace with your base auth service url

function getToken() {
  return localStorage.getItem('authToken');
}

// Redirect to dashboard if token is already present
if (getToken()) {
  window.location.href = 'dashboard.html';
}

function saveToken(token) {
  localStorage.setItem('authToken', token);
}

// Handle login form submission
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const phone_number = document.getElementById('phone').value;
  const password = document.getElementById('password').value;
  const userType = document.getElementById('userType').value;

  // Use different URLs for customer and driver logins
  const loginUrl =
    userType === 'customer'
      ? `${backendUrl}/customer/login`
      : `${backendUrl}/driver/login`;

  try {
    const response = await fetch(loginUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone_number, password }) // Match backend models
    });

    const data = await response.json();

    if (response.ok) {
      saveToken(data.token);
      window.location.href = 'dashboard.html'; // Redirect on success
    } else {
      alert(data.message || 'Login failed');
    }
  } catch (error) {
    console.error('Error:', error);
  }
});