async function wakeComputer() {
    try {
        const response = await fetch('/wake');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        alert(data.message);
    }
    catch (error) {
        console.error("Error:", error);
        alert('Failed to wake computer');
    }
}