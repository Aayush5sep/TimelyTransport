function checkAuthentication() {
    const token = localStorage.getItem('authToken');

    if (!token) {
        alert('You must be logged in to continue.');
        window.location.href = 'login.html'; // Redirect to login page
        return false;
    }

    const userDetails = parseJwt(token);
    if (userDetails.user !== 'customer') {
        alert('Only customers can access this feature.');
        window.location.href = 'dashboard.html'; // Redirect to login page
        return false;
    }

    console.log('Customer authenticated');
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

checkAuthentication();

const olaMaps = new OlaMapsSDK.OlaMaps({
    apiKey: 'YOUR_API_KEY'
});

let myMap, sourceMarker, destinationMarker;

// Initialize map and markers
function initializeMap(latitude, longitude) {
    myMap = olaMaps.init({
        style: "https://api.olamaps.io/tiles/vector/v1/styles/default-light-standard/style.json",
        container: 'map',
        center: [longitude, latitude],
        zoom: 15
    });

    // Create draggable markers with dragend handlers
    sourceMarker = addDraggableMarker([longitude, latitude], 'red', debounce(updateStartAddress, 500));
    destinationMarker = addDraggableMarker([longitude, latitude], 'blue', debounce(updateEndAddress, 500));
}

// Add a draggable marker to the map
function addDraggableMarker(coords, color, onDragEnd) {
    const marker = olaMaps.addMarker({
        offset: [0, -10],
        anchor: 'bottom',
        color,
        draggable: true
    }).setLngLat(coords).addTo(myMap);

    // Trigger only when the user releases the marker
    marker.on('dragend', () => {
        const position = marker.getLngLat();
        onDragEnd(position);  // Call the handler with the new position
    });

    return marker;
}

// Fetch reverse geocoded address
async function reverseGeocode(lat, lng) {
    const apiKey = 'YOUR_API_KEY';
    const url = `https://api.olamaps.io/places/v1/reverse-geocode?latlng=${lat},${lng}&api_key=${apiKey}`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        return data.results[0]?.formatted_address || 'Address not found';
    } catch (error) {
        console.error('Error in reverse geocoding:', error);
        return 'Error fetching address';
    }
}

// Update start address
async function updateStartAddress(coords) {
    const address = await reverseGeocode(coords.lat, coords.lng);
    document.getElementById('startAddress').value = address;
}

// Update destination address
async function updateEndAddress(coords) {
    const address = await reverseGeocode(coords.lat, coords.lng);
    document.getElementById('endAddress').value = address;
}

// Debounce function to limit API calls
function debounce(func, delay) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), delay);
    };
}

// Handle location autocomplete
async function handleAutocomplete(input, suggestionsContainer) {
    const query = input.value;
    if (query.length < 5) return;

    const apiKey = 'OyIE1iZDygLFJkrzgVxKLeufCGHd3UHLblmHWFSa'; // Replace with your API key
    try {
        const response = await fetch(
            `https://api.olamaps.io/places/v1/autocomplete?input=${encodeURIComponent(query)}&api_key=${apiKey}`
        );
        const data = await response.json();
        if (data.predictions.length > 0) {
            showSuggestions(data.predictions, suggestionsContainer);
        }
    } catch (error) {
        console.error('Error fetching autocomplete results:', error);
    }
}

// Show autocomplete suggestions
function showSuggestions(predictions, container) {
    container.innerHTML = '';
    predictions.forEach(prediction => {
        const suggestion = document.createElement('div');
        suggestion.textContent = prediction.description;
        suggestion.addEventListener('click', async () => {
            const { lat, lng } = prediction.geometry.location;
            const marker = container.id === 'startSuggestions' ? sourceMarker : destinationMarker;
            marker.setLngLat([lng, lat]);
            myMap.setCenter([lng, lat]);

            if (container.id === 'startSuggestions') {
                document.getElementById('startAddress').value = await reverseGeocode(lat, lng);
            } else {
                document.getElementById('endAddress').value = await reverseGeocode(lat, lng);
            }
            container.innerHTML = '';
        });
        container.appendChild(suggestion);
    });
}

// Attach autocomplete to input fields
document.getElementById('startLocation').addEventListener(
    'input',
    debounce(() => handleAutocomplete(document.getElementById('startLocation'), document.getElementById('startSuggestions')), 300)
);

document.getElementById('endLocation').addEventListener(
    'input',
    debounce(() => handleAutocomplete(document.getElementById('endLocation'), document.getElementById('endSuggestions')), 300)
);

// Initialize map on page load
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        position => initializeMap(position.coords.latitude, position.coords.longitude),
        error => {
            console.error('Error getting location:', error);
            alert('Unable to retrieve your location.');
            initializeMap(18.760290, 73.381424); // Default location
        }
    );
} else {
    alert('Geolocation is not supported by your browser.');
    initializeMap(18.760290, 73.381424); // Default location
}

// Format distance in km and meters
function formatDistance(distanceInMeters) {
    const kilometers = Math.floor(distanceInMeters / 1000);
    const meters = distanceInMeters % 1000;
    return `${kilometers} km ${meters} m`;
}

// Format time in minutes and seconds
function formatTime(timeInSeconds) {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = timeInSeconds % 60;
    return `${minutes} min ${seconds} sec`;
}

// Fare and ETA calculation
document.getElementById("calculateBtn").addEventListener("click", async () => {
    const source = sourceMarker.getLngLat();
    const destination = destinationMarker.getLngLat();
    const vehicleType = document.getElementById("vehicleType").value;

    try {
        const response = await fetch('http://127.0.0.1:8001/eta-fare', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'token': `${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({
                source_location: {
                    latitude: source.lat,
                    longitude: source.lng
                },
                destination_location: {
                    latitude: destination.lat,
                    longitude: destination.lng
                },
                source_address: document.getElementById('startAddress').value,
                destination_address: document.getElementById('endAddress').value,
                vehicle_type: vehicleType
            })
        });

        const data = await response.json();
        if (response.ok) {
            document.getElementById("distance").innerText = `${data.distance} km`;
            document.getElementById("eta").innerText = `${data.eta} minutes`;
            document.getElementById("fare").innerText = `${data.fare} currency units`;
            document.getElementById("result").style.display = "block";
        } else {
            console.error('Error:', data.detail);
            alert(data.detail || 'Failed to calculate route. Please try again.');
        }
    } catch (error) {
        console.error('Error fetching route details:', error);
        alert('Failed to calculate route. Please try again.');
    }
});

// WebSocket for booking request
document.getElementById("requestBookingBtn").addEventListener("click", () => {
    const socket = new WebSocket("ws://localhost:8001/ws/request-booking");
    socket.onopen = () => {
        const source = sourceMarker.getLngLat();
        const destination = destinationMarker.getLngLat();
        socket.send(JSON.stringify({
            source_location: { latitude: source.lat, longitude: source.lng },
            destination_location: { latitude: destination.lat, longitude: destination.lng },
            vehicleType: document.getElementById("vehicleType").value
        }));
        document.getElementById("bookingStatus").style.display = "block";
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.status === "success") {
            alert("Booking request successful. Driver Found");
            window.location.href = "activetrip.html";
        }
        else {
            alert(data.message);
            window.location.href = "dashboard.html";
        }
    };
});