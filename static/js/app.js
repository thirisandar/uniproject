// Define the bounding box (approximate coordinates for the three townships)
var bounds = L.latLngBounds(
    [21.9400, 96.0400], // Southwest corner (Lat, Lng)
    [22.0000, 96.1200]  // Northeast corner (Lat, Lng)
);

// Initialize the map and set the initial view to Mandalay University
let map = L.map('map', {
    center: [21.95687923791962, 96.09466804195264], // Mandalay University coordinates
    zoom: 15, // Adjust zoom level
});

map.setMaxBounds(bounds);  // Prevent dragging far away
map.on('drag', function() {
    map.panInsideBounds(bounds, { animate: false });
});


// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Create a custom red pin with text beside it (Mandalay University)
let mandalayUniversityIcon = L.divIcon({
    className: 'mandalay-university-pin',
    html: `
        <div style="position: relative; display: flex; align-items: center;">
            <div style=" width: 25px; height: 40px; border-radius: 50%;"></div>
            <div style="margin-left: 10px; font-size: 14px; color: black; font-weight: bold; display:inline-flex;">
                <i class="fas fa-map-marker-alt fa-2x" style="color:rgb(199, 130, 130); display:flex;"><span style="display:flex; font-weight:600; font-size:14px;  color:black;">University Of Mandalay</span></i>
            </div>
        </div>
    `, // Red circle pin with text beside it
    iconSize: [100, 50], // Adjust icon size to fit both pin and text
    iconAnchor: [25, 50], // Position the pin correctly (the pin's base)
    popupAnchor: [0, -50], // Position the popup above the pin
});

// Place the red pin on the map for Mandalay University
let mandalayUniversityMarker = L.marker([21.95714044159443, 96.09435422351598], { icon: mandalayUniversityIcon })
    .addTo(map)
    .bindPopup('<b>Mandalay University</b><br>Location of Mandalay University');

// Array to store the markers for other locations
let markers = [];
let currentRoute = null;  // Store the current route to clear it later

// Default township to 'Maharaungmyay' if no township is selected
let activeTownship = null;  // Initially, no township is selected
let activeCategory = null;  // Initially, no category is selected

// Left panel HTML elements
let closePanelButton = document.getElementById("close-panel");  // Close button

let locationPanel = document.getElementById("location-panel");  // Assuming you have a div for this
let locationName = document.getElementById("location-name");
let locationAddress = document.getElementById("location-address");
let locationImage = document.getElementById("location-image");

// Function to handle selecting a township
function selectTownship(township) {
    activeTownship = township;

    // Clear existing markers (except for Mandalay University marker)
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    // Remove the current route if it exists
    if (currentRoute) {
        map.removeControl(currentRoute);
        currentRoute = null;
    }

    // Set the active button style for township
    document.querySelectorAll('.township-buttons button').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelector(`button[onclick="selectTownship('${township}')"]`).classList.add('active');

    // Reset category and clear previous markers
    activeCategory = null;
    document.querySelectorAll('#category-list a').forEach(link => {
        link.classList.remove('active');
    });
}

// Function to handle showing locations for a specific category
function showLocations(category) {
    // Check if a township has been selected
    if (!activeTownship) {
        window.alert('Please choose a township first.');
        return;
    }

    // Set the active category
    activeCategory = category;

    // Set the active button style for category
    document.querySelectorAll('#category-list a').forEach(link => {
        link.classList.remove('active');
    });
    
    document.querySelector(`a[data-category="${category}"]`).classList.add('active');

    console.log(`Fetching data for: ${activeTownship}/${category}`);

    // Fetch the locations data from the Flask API (or local file)
    fetch(`/locations/${activeTownship}/${category}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to fetch data for ${activeTownship}/${category}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Fetched Data:', data);

            // Clear existing markers (except for Mandalay University marker)
            markers.forEach(marker => map.removeLayer(marker));
            markers = [];

            // If locations are found, display them on the map
            if (data.locations && data.locations.length > 0) {
                data.locations.forEach(location => {
                    // Create the marker for the location
                    const marker = L.marker([location.latitude, location.longitude])
                        .addTo(map)
                        .bindPopup(`
                            <b>${location.name}</b><br>
                            <p>Distance: ${location.distance_km} km</p>
                            <p>Motorbike: ${location.motorbike_time} min</p>
                            <p>Car: ${location.car_time} min</p>
                            
                        `);

                    // Add a click event to show route when the user clicks on the marker
                    marker.on('click', () => {
                        // Remove the existing route if any
                        if (currentRoute) {
                            map.removeControl(currentRoute);
                        }

                        // // Calculate and display the route from Mandalay University to the selected location
                        // calculateRoute([21.95714044159443, 96.09435422351598], [location.latitude, location.longitude], marker);

                        // // Display location details in the left panel
                        // showLocationDetails(location);
                        calculateRoute(
                            [21.95714044159443, 96.09435422351598], // start
                            [location.latitude, location.longitude], // end
                            marker,
                            location // pass the location object here
                        );
                        showLocationDetails(location);
                    });

                    // Add the marker to the markers array
                    markers.push(marker);
                });
            } else {
                console.log(`No ${category} found in ${activeTownship}.`);
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            alert(`Error fetching data: ${error.message}`);
        });
}

// Function to calculate and display the route
function calculateRoute(startCoords, endCoords, marker, location) {
    // Create the route control using Leaflet Routing Machine
    currentRoute = L.Routing.control({
        waypoints: [
            L.latLng(startCoords), // Start: Mandalay University coordinates
            L.latLng(endCoords)    // End: Location coordinates
        ],
        routeWhileDragging: true,  // Optional: allows the user to drag the route to change it
        createMarker: function() { return null; }  // Prevent marker creation along the route
    }).addTo(map);

    // After the route is created, calculate and display distance and time
    currentRoute.on('routesfound', function(event) {
        const route = event.routes[0]; // The first (and only) route
        const distance = route.summary.totalDistance / 1000; // Convert from meters to kilometers
        const time = route.summary.totalTime / 60; // Convert from seconds to minutes

        // Update the marker's popup to show the route distance and time
        marker.bindPopup(`
            <b>${marker.getPopup().getContent().split('<br>')[0]}</b><br>
            <p>Distance: ${distance.toFixed(2)} km</p>
            <p>Motorbike: ${location.motorbike_time} </p>
            <p>Car: ${location.car_time} </p>
        `).openPopup();
    });
}



// Function to handle closing the left panel
closePanelButton.addEventListener('click', () => {
    locationPanel.style.display = 'none';  // Hide the panel when clicked
});


// Function to show location details in the left panel
function showLocationDetails(location) {
    console.log(location);
    // Update the left panel with location information
    locationName.textContent = location.name;
    locationAddress.textContent = location.address;  // Assuming you have an 'address' field in your location data
    locationImage.src = location.image || 'https://via.placeholder.com/150';  // Default image if not available

    // Show the left panel
    locationPanel.style.display = 'block';
}

// Event listeners for category links
document.querySelectorAll('#category-list a').forEach(link => {
    link.addEventListener('click', event => {
        event.preventDefault();
        const category = event.target.textContent.trim().toLowerCase();
        
        // Set the active category and display the locations
        showLocations(category);
    });
});

// Event listeners for township buttons
document.querySelectorAll('.township-buttons button').forEach(button => {
    button.addEventListener('click', event => {
        const township = event.target.textContent.trim();
        // Set the active township and reset the category (category selection is required after choosing a township)
        selectTownship(township);
    });
});

function displayLocationsOnMap(locations) {
    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    // Clear any existing route
    if (currentRoute) {
        map.removeControl(currentRoute);
        currentRoute = null;
    }

    locations.forEach(location => {
        const marker = L.marker([location.latitude, location.longitude])
            .addTo(map)
            .bindPopup(`
                <b>${location.name}</b><br>
                <p>Distance: ${location.distance_km} km</p>
                <p>Motorbike: ${location.motorbike_time}</p>
                <p>Car: ${location.car_time}</p>
            `);

        marker.on('click', () => {
            if (currentRoute) {
                map.removeControl(currentRoute);
            }

            calculateRoute(
                [21.95714044159443, 96.09435422351598],
                [location.latitude, location.longitude],
                marker,
                location
            );
            showLocationDetails(location);
        });

        markers.push(marker);
    });

    // Optionally, fit map to these 3 nearest markers
    const bounds = L.latLngBounds(locations.map(loc => [loc.latitude, loc.longitude]));
    map.fitBounds(bounds.pad(0.1)); // Add some padding so it's not tight
}


function showNearestLocations() {
    const category = document.getElementById("nearest-select").value;
    if (!category) return;

    // Default township to search in (search all)
    const townships = ["Maharaungmyay", "Chanmyathazi", "Chanayetharzan"];
    let allLocations = [];

    let fetches = townships.map(township =>
        fetch(`/locations/${township}/${category}`)
            .then(res => res.json())
            .then(data => {
                if (data.locations) {
                    allLocations = allLocations.concat(data.locations);
                }
            })
    );

    Promise.all(fetches).then(() => {
        // Sort by motorbike_time in seconds
        allLocations.sort((a, b) => {
            const getSecs = timeStr => {
                const parts = timeStr.split(" ");
                let min = 0, sec = 0;
                parts.forEach((p, i) => {
                    if (p === "min") min = parseInt(parts[i - 1]);
                    if (p === "sec") sec = parseInt(parts[i - 1]);
                });
                return min * 60 + sec;
            };
            return getSecs(a.motorbike_time) - getSecs(b.motorbike_time);
        });

        const top3 = allLocations.slice(0, 3);
        displayLocationsOnMap(top3);
    });
}

// Initialize with no locations visible and no township selected
selectTownship("Maharaungmyay");
