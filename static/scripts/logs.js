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

        // // Example fetch for network logs
        // fetch('/api/logs/network')
        //     .then(response => response.text())
        //     .then(logs => {
        //         const networkLogs = document.getElementById('networkLogList');
        //         networkLogs.textContent = logs;
        //         networkLogs.scrollTop = networkLogs.scrollHeight;
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
