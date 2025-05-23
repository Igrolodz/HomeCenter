function updateClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    document.getElementById('clock').innerHTML = `${hours}:${minutes}`;

    const totalMinutes = now.getHours() * 60 + now.getMinutes();
    const percentageOfDay = (totalMinutes / 1440) * 100;
    document.getElementById('day').innerHTML = `${percentageOfDay.toFixed(2)}%`;
    document.querySelector('.day-progress').style.width = `${percentageOfDay}%`;

    const dayOfMonth = now.getDate();
    const totalDaysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
    const percentageOfMonth = (dayOfMonth / totalDaysInMonth) * 100;
    document.getElementById('month').innerHTML = `${percentageOfMonth.toFixed(2)}%`;
    document.querySelector('.month-progress').style.width = `${percentageOfMonth}%`;

    const dayOfYear = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / (1000 * 60 * 60 * 24));
    const isLeapYear = now.getFullYear() % 4 === 0 && (now.getFullYear() % 100 !== 0 || now.getFullYear() % 400 === 0);
    const totalDaysInYear = isLeapYear ? 366 : 365;
    const percentageOfYear = (dayOfYear / totalDaysInYear) * 100;
    document.getElementById('year').innerHTML = `${percentageOfYear.toFixed(2)}%`;
    document.querySelector('.year-progress').style.width = `${percentageOfYear}%`;
}

setInterval(updateClock, 1000);