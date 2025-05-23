document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('networkFlowChart');
    if (!canvas) {
        console.error('Could not find canvas element');
        throw new Error('Canvas element not found');
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('Could not initialize 2D context');
        throw new Error('Failed to get 2D context');
    }
    
    const networkFlowChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Timestamps or just seconds
            datasets: [
            {
                label: 'Download (Mbps)',
                data: [],
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.3
            },
            {
                label: 'Upload (Mbps)',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.3
            }
            ]
        },
        options: {
            responsive: true,
            animation: true,
            scales: {
            y: {
                beginAtZero: true
            }
            },
            plugins: {
            legend: {
                labels: {
                color: '#fff'
                }
            }
            }
        }
    });
    socket.on('network_stats_update', (data) => {
        const uploadSpeed = data.upload_speed; // in Mbps
        const downloadSpeed = data.download_speed; // in Mbps
        const timestamp = new Date().toLocaleTimeString(); // or use a more precise timestamp if needed
    
        // Add new data points
        networkFlowChart.data.labels.push(timestamp);
        networkFlowChart.data.datasets[0].data.push(downloadSpeed);
        networkFlowChart.data.datasets[1].data.push(uploadSpeed);
    
        // Remove old data points if necessary (e.g., keep only the last 10)
        if (networkFlowChart.data.labels.length > 60) {
            networkFlowChart.data.labels.shift();
            networkFlowChart.data.datasets[0].data.shift();
            networkFlowChart.data.datasets[1].data.shift();
        }
    
        // Update the chart
        networkFlowChart.update();
    });
});

socket.on('network_stats_update', (data) => {
    const uploadSpeed = data.upload_speed; // in Mbps
    const downloadSpeed = data.download_speed; // in Mbps

    document.getElementById('network').innerText = `Download: ${downloadSpeed}Mb/s Upload: ${uploadSpeed}Mb/s`;
});

