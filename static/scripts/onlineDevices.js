socket.on("network_devices", (data) => {
    console.log("Received network devices data:", data);
    const count = data.length;
    document.getElementById("online").innerText = `Online network devices: ${count}`;
});