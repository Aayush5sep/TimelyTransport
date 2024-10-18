const loginButton = document.getElementById("login-btn");
const phoneInput = document.getElementById("phone");
const passwordInput = document.getElementById("password");
const loginError = document.getElementById("login-error");

// Login button handler
loginButton.onclick = async () => {
    const phone = phoneInput.value;
    const password = passwordInput.value;

    try {
        const token = await login(phone, password);
        localStorage.setItem("driver_token", JSON.stringify(token));
        window.location.href = "app.html"; // Redirect to dashboard
    } catch (error) {
        loginError.textContent = error.message;
    }
};

// Send login request to auth service
async function login(phone, password) {
    const response = await fetch("http://localhost:8002/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone, password }),
    });

    if (!response.ok) throw new Error("Invalid phone number or password.");
    return response.json(); // Response contains { user_id, phone_number }
}