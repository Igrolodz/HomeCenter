document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Tab switching logic
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            button.classList.add('active');
            const tabId = `${button.dataset.tab}-logs`;
            document.getElementById(tabId).classList.add('active');
        });
    });

    let currSystemLog = null;
    let currMinecraftLog = null;
    // Log fetching and updating
    function updateLogs() {
        // Example fetch for system logs
        fetch('/static/logs/homecenter.log')
            .then(response => response.text())
            .then(logs => {
                if (logs === currSystemLog) return; // No change in logs, skip update

                const systemLogs = document.getElementById('systemLogList');
                systemLogs.textContent = logs;
                systemLogs.scrollTop = systemLogs.scrollHeight;
                currSystemLog = logs; // Update current log to the new logs
            });

        socket.emit("fetch_minecraft");
        socket.on("minecraft_logs", (logs) => {
            if (logs === currMinecraftLog) return; // No change in logs, skip update

            const minecraftLogs = document.getElementById('minecraftLogList');
            minecraftLogs.textContent = logs;
            minecraftLogs.scrollTop = minecraftLogs.scrollHeight;
            currMinecraftLog = logs; // Update current log to the new logs
        });
        // // Example fetch for minecraft logs
        // fetch('../dudis/logs/latest.log')
        //     .then(response => response.text())
        //     .then(logs => {
        //         const minecraftLogs = document.getElementById('minecraftLogList');
        //         minecraftLogs.textContent = logs;
        //         minecraftLogs.scrollTop = minecraftLogs.scrollHeight;
        //     });

        // // Example fetch for security logs
        // fetch('/api/logs/security')
        //     .then(response => response.text())
        //     .then(logs => {
        //         const securityLogs = document.getElementById('securityLogList');
        //         securityLogs.textContent = logs;
        //         securityLogs.scrollTop = securityLogs.scrollHeight;
        //     });
    }
    
    // Update logs every second
    updateLogs();
    setInterval(updateLogs, 1000);
});
