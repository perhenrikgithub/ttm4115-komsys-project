// Function to get the user's current location
async function getUserLocation() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function (position) {
                    const userLat = position.coords.latitude;
                    const userLon = position.coords.longitude;
                    resolve({ lat: userLat, lon: userLon }); // Resolve with user's coordinates
                },
                function (error) {
                    reject("Error getting location: " + error.message); // Reject if there is an error
                }
            );
        } else {
            reject("Geolocation is not supported by this browser.");
        }
    });
}

// Function to calculate the distance between two coordinates using Haversine formula
function calculateDistance(userLat, userLon, targetLat, targetLon) {
    const R = 6371000; // Radius of the Earth in meters (use 6371 for kilometers)
    const dLat = ((targetLat - userLat) * Math.PI) / 180; // Convert degrees to radians
    const dLon = ((targetLon - userLon) * Math.PI) / 180; // Convert degrees to radians

    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos((userLat * Math.PI) / 180) * Math.cos((targetLat * Math.PI) / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)); // Central angle

    const distance = R * c; // Distance in meters
    return distance;
}

// Function to parse a string of coordinates and calculate distance from user location
async function calculateDistanceFromString(coordString) {
    const coords = coordString.split(",").map(Number); // Split string into an array of numbers
    if (coords.length === 2) {
        const targetLat = coords[0];
        const targetLon = coords[1];

        try {
            const userLocation = await getUserLocation(); // Wait for user's location
            const distance = calculateDistance(userLocation.lat, userLocation.lon, targetLat, targetLon);
            console.log(`The distance from your location to the target is: ${distance.toFixed(2)} meters`);
        } catch (error) {
            console.error(error); // If there's an error, log it
        }
    } else {
        console.error("Invalid coordinate format. Please provide a string in the format 'lat, long'.");
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const userLocation = await getUserLocation(); // Get user's location

        // Select all elements with the data-location attribute
        const scooterElements = document.querySelectorAll("[data-location]");

        scooterElements.forEach((element) => {
            const coordString = element.getAttribute("data-location");
            if (coordString) {
                const coords = coordString.split(",").map(Number);
                if (coords.length === 2) {
                    const distance = calculateDistance(userLocation.lat, userLocation.lon, coords[0], coords[1]);
                    // Update the distance in the corresponding <span>
                    const distanceSpan = element.querySelector(".distance");
                    if (distanceSpan) {
                        distanceSpan.textContent = `${(distance / 1000).toFixed(2)} km`; // Convert to kilometers
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error calculating distances:", error);
    }
});
