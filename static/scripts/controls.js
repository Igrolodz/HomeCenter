// buttons
const home = document.getElementById('home');
const wol = document.getElementById('wol');
const school = document.getElementById('school');
const dailyAI = document.getElementById('daily-ai');


document.addEventListener('keydown', function (e) {
    if (e.key === '1') {
        console.log('Navigating to Home');
        home.click();
    }
    else if (e.key === '2') {
        console.log('Navigating to Wake On Lan');
        wol.click();
    }
    else if (e.key === '3') {
        console.log('Navigating to School Chart');
        school.click();
    }
    else if (e.key === '4') {
        console.log('Navigating to Daily AI Settings');
        dailyAI.click();
    }
});
