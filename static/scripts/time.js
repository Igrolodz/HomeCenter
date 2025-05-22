function updateClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    document.getElementById('clock').innerHTML = `${hours}:${minutes}`;
}

setInterval(updateClock, 1000);
updateClock();