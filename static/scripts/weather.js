const socket = io();

socket.on('weather_update', (data) => {
    document.getElementById('temp').innerText = `${data.temp.toFixed(1)}°C`;

    // Optional: Change background color or image based on condition
    const iconUrl = `https://openweathermap.org/img/wn/${data.icon}@2x.png`;
    document.getElementById('icon').src = iconUrl;
});