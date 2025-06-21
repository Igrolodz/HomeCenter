// Add this at the top of your file
const serviceHeartbeats = new Map(); // Store last heartbeat time for each service
const OFFLINE_THRESHOLD = 10000; // 10 seconds in milliseconds

socket.on('heartbeat_pass', (data) => {
    let service_id = data.service_id;
    let service_name = data.service_name;
    let heartbeatElement = document.getElementById(service_id);
    let heartbeatIcon = document.getElementById(`${service_id}_icon`);
    
    // Update last heartbeat time
    serviceHeartbeats.set(service_id, Date.now());
    
    if (heartbeatElement) {
        heartbeatElement.innerText = `${service_name}: ONLINE`;
        heartbeatIcon.style.color = "#2ecc71"; // Green color for online status
    } else {
        console.warn('Heartbeat element not found in the DOM.');
    }
});

// Add this function to check for stale services
function checkStaleServices() {
    const now = Date.now();
    serviceHeartbeats.forEach((lastHeartbeat, service_id) => {
        if (now - lastHeartbeat > OFFLINE_THRESHOLD) {
            let element = document.getElementById(service_id);
            if (element) {
                const serviceName = element.innerText.split(':')[0];
                element.innerText = `${serviceName}: OFFLINE`;

                let heartbeatIcon = document.getElementById(`${service_id}_icon`);
                heartbeatIcon.style.color = "#e74c3c"; // Red color for offline status
            }
        }
    });
}

// Start periodic checking
checkStaleServices(); // Initial check
setInterval(checkStaleServices, 1000); // Check every second