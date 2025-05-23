socket.on('system_stats_update', (data) => {
    let cpuUsage = data.cpu_usage;
    let ramUsage = data.ram_usage;
    let diskSpace = data.disk_space;

    document.getElementById('cpu').innerText = `${cpuUsage}%`;
    document.getElementById('ram').innerText = `${ramUsage}%`;
    document.getElementById('disk').innerText = `${diskSpace}%`;

    // Update progress bars
    document.querySelector('.progress').style.width = `${cpuUsage}%`;
    document.querySelector('.ram-progress').style.width = `${ramUsage}%`;
    document.querySelector('.disk-progress').style.width = `${diskSpace}%`;
});