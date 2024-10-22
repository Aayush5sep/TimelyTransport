const backendUrl = 'http://localhost:8000'; // Auth Service URL

const olaMaps = new OlaMapsSDK.OlaMaps({
    apiKey: 'OyIE1iZDygLFJkrzgVxKLeufCGHd3UHLblmHWFSa' 
});

let homeLocation = { latitude: 0, longitude: 0 };
let map;
let marker;

// Get token from localStorage
function getToken() {
    return localStorage.getItem('authToken');
}

// Redirect to dashboard if token is present
if (getToken()) {
    window.location.href = 'dashboard.html';
}

// Save token in localStorage
function saveToken(token) {
    localStorage.setItem('authToken', token);
}

// Debounce function to limit the rate of autocomplete requests
function debounce(func, delay) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

// Initialize map with user's current location
async function initializeMap() {
    try {
        const position = await getCurrentLocation();
        const { latitude, longitude } = position.coords;

        homeLocation = { latitude, longitude };
        document.getElementById('mapContainer').style.display = 'block'; // Show the map

        // Initialize the map centered at the current location
        map = olaMaps.init({
            style: 'https://api.olamaps.io/tiles/vector/v1/styles/default-light-standard/style.json',
            container: 'mapContainer',
            center: [longitude, latitude],
            zoom: 15,
        });

        // Add a draggable marker at the current location
        marker = olaMaps
        .addMarker({
            offset: [0, -10],  // Optional: Adjust marker position if needed
            anchor: 'bottom',  // Anchor at the bottom for a pin-like marker
            color: 'red',      // Set marker color
            draggable: true    // Make the marker draggable
        })
        .setLngLat([longitude, latitude])  // Set initial marker position
        .addTo(map);  // Add the marker to the map

        // Update homeLocation when the marker is dragged
        marker.on('dragend', () => {
            const newCoords = marker.getLngLat();
            homeLocation = { latitude: newCoords.lat, longitude: newCoords.lng };
        });
    } catch (error) {
        console.error('Error getting current location:', error);
        alert('Unable to retrieve your location. Please ensure location services are enabled.');
    }
}

// Get the user's current location
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
        });
    });
}

// Perform autocomplete search with debounce
const performAutocompleteSearch = debounce(async (query) => {
    const apiKey = 'OyIE1iZDygLFJkrzgVxKLeufCGHd3UHLblmHWFSa';
    try {
        const response = await fetch(
            `https://api.olamaps.io/places/v1/autocomplete?input=${encodeURIComponent(query)}&api_key=${apiKey}`
        );
        const data = await response.json();

        if (data.predictions.length > 0) {
            showAddressSuggestions(data.predictions);
        }
    } catch (error) {
        console.error('Error fetching autocomplete results:', error);
    }
}, 500);

// Show autocomplete suggestions
function showAddressSuggestions(predictions) {
    const suggestionsContainer = document.getElementById('addressSuggestions');
    suggestionsContainer.innerHTML = ''; // Clear previous suggestions

    predictions.forEach((prediction) => {
        const suggestion = document.createElement('div');
        suggestion.classList.add('suggestion');
        suggestion.textContent = prediction.description;

        // Set up click event for each suggestion
        suggestion.addEventListener('click', () => {
            const { lng, lat } = prediction.geometry.location;
            document.getElementById('homeAddress').value = prediction.description; // Fill address input
            marker.setLngLat([lng, lat]); // Move marker to selected location
            map.setCenter([lng, lat]);
            homeLocation = { latitude: lat, longitude: lng }; // Update home location
            suggestionsContainer.innerHTML = ''; // Clear suggestions
        });

        suggestionsContainer.appendChild(suggestion);
    });
}

// Update additional fields based on user type
function updateAdditionalFields(userType) {
    const additionalFieldsDiv = document.getElementById('additionalFields');
    additionalFieldsDiv.innerHTML = ''; // Clear previous fields

    if (userType === 'customer') {
        additionalFieldsDiv.innerHTML = `
            <input type="text" id="homeAddress" placeholder="Home Address" required />
            <input type="text" id="autocompleteInput" placeholder="Search Location..." />
            <div id="addressSuggestions" class="suggestions"></div>
            <button type="button" id="setLocationButton">Set Current Location</button>
        `;

        // Add event listener for the autocomplete input
        document.getElementById('autocompleteInput').addEventListener('input', (e) => {
            performAutocompleteSearch(e.target.value);
        });

        // Set the current location when button is clicked
        document.getElementById('setLocationButton').addEventListener('click', () => {
            // Set marker to current location
            marker.setLngLat([homeLocation.longitude, homeLocation.latitude]);
            document.getElementById('homeAddress').value = "Current Location"; // Optional: Update the address input
        });
    } else {
        additionalFieldsDiv.innerHTML = `
            <input type="date" id="dob" placeholder="Date of Birth" required />
        `;
    }
}

// Handle form submission
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const phone = document.getElementById('phone').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;
    const name = document.getElementById('name').value;
    const gender = document.getElementById('gender').value;
    const userType = document.getElementById('userType').value;

    let additionalFields = {};
    if (userType === 'customer') {
        additionalFields = {
            home_address: document.getElementById('homeAddress').value,
            home_location: homeLocation,
        };
    } else {
        additionalFields = { dob: document.getElementById('dob').value };
    }

    const registerUrl =
        userType === 'customer'
            ? `${backendUrl}/customer/register`
            : `${backendUrl}/driver/register`;

    try {
        const response = await fetch(registerUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone_number: phone, 
                password: password, 
                email: email, 
                name: name, 
                gender: gender, 
                ...additionalFields }),
        });

        const data = await response.json();
        if (response.ok) {
            saveToken(data.token);
            window.location.href = userType === 'driver' ? 'vehicle.html' : 'dashboard.html';
        } else {
            alert(data.message || 'Registration failed');
        }
    } catch (error) {
        console.error('Error during registration:', error);
    }
});

// Initialize the map and fields on page load
initializeMap();
updateAdditionalFields('customer');

// Switch fields when the user type changes
document.getElementById('userType').addEventListener('change', (e) => {
    updateAdditionalFields(e.target.value);
});
