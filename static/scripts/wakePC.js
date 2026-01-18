async function wakeComputer() {
    try {
        const response = await fetch('/wake');
        
        const data = await response.json();
        alert(data.message);
    }
    catch (error) {
        console.error("Error:", error);
        alert('Failed to wake computer');
    }
}