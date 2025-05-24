async function fetchDevices() {
    const response = await fetch('/static/DB/devices.json');
    const data = await response.json();
    let count = data.length;
    document.getElementById("online").innerText = `Online network devices: ${count}`;
    // or update your UI with device info
}

// Call it on load and every few minutes
fetchDevices();
setInterval(fetchDevices, 1000*60); // every 3 minutes