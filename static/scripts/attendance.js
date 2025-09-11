const socket = io();

socket.emit('get_attendance');

const states = {
    'loading':{
        'text': 'Ładowanie...',
        'color': '#FFFFFF'
    },
    'safe':{
        'text': 'Safe',
        'color': '#4CAF50'
    },
    'warning':{
        'text': 'Risky',
        'color': '#FFC107'
    },
    'danger':{
        'text': 'AVOID',
        'color': '#F44336'
    }
}

const daysOfWeek = {
    'Monday': ["j_polski", "j_angielski_zawodowy", "j_angielski", "wychowanie_fizyczne", "tworzenie_i_administrowanie_bazami_danych"],
    'Tuesday': ["tworzenie_stron_i_aplikacji_internetowych", "j_angielski", "wychowanie_fizyczne", "j_polski", "tworzenie_i_administrowanie_bazami_danych"],
    'Wednesday': ["j_polski", "biologia", "witryny_i_aplikacje_internetowe", "chemia", "matematyka", "j_zyk_niemiecki"],
    'Thursday': ["matematyka", "tworzenie_stron_i_aplikacji_internetowych", "zaj_cia_z_wychowawc"],
    'Friday': ["matematyka", "fizyka", "witryny_i_aplikacje_internetowe", "historia"]
}

socket.on('attendance_data', (data) =>{

    console.log("Received attendance data:", data);

    for (const subject in data){
        try {
            let totalHours = data[subject].hours_per_week * 12;

            let safeSkip = Math.floor(totalHours * 0.4);
            let maxSkip = Math.floor(totalHours * 0.5);
            let predictedAttendance = totalHours - data[subject].absent_excused - data[subject].absent_unexcused;
            let predictedRate = (predictedAttendance / totalHours) * 100;
            let progress = Math.min(((predictedRate - 50) / 50) * 100, 100);

            document.getElementById(`${subject}-safe-skip`).innerText = `Safe skip: ${safeSkip}`;
            document.getElementById(`${subject}-max-skip`).innerText = `Max skip: ${maxSkip}`;
            document.getElementById(`${subject}-progress`).style.width = `${progress}%`;
            document.getElementById(`${subject}-attendance`).innerText = `Frekwencja: ${predictedRate.toFixed(1)}%`;

            if (predictedRate >= 80) {
                document.getElementById(`${subject}-panel`).style.borderColor = states.safe.color;
                document.getElementById(`${subject}-progress`).style.backgroundColor = states.safe.color;
            } else if (predictedRate >= 60) {
                document.getElementById(`${subject}-panel`).style.borderColor = states.warning.color;
                document.getElementById(`${subject}-progress`).style.backgroundColor = states.warning.color;
            } else if (predictedRate < 60) {
                document.getElementById(`${subject}-panel`).style.borderColor = states.danger.color;
                document.getElementById(`${subject}-progress`).style.backgroundColor = states.danger.color;
            } else {
                document.getElementById(`${subject}-panel`).style.borderColor = states.loading.color;
                document.getElementById(`${subject}-progress`).style.backgroundColor = states.loading.color;
            }
        } catch (error) {
            console.error(`Error updating attendance for ${subject}:`, error);
        }
    }

    for (const day in daysOfWeek) {
        let lowestRate = 100;
        let dayState = states.safe;

        for (const subject of daysOfWeek[day]) {
            if (data[subject]) {
                const totalHours = data[subject].hours_per_week * 12;
                const predictedAttendance = totalHours - data[subject].absent_excused - data[subject].absent_unexcused;
                const rate = (predictedAttendance / totalHours) * 100;
                
                if (rate < lowestRate) {
                    lowestRate = rate;
                    if (rate >= 80) dayState = states.safe;
                    else if (rate >= 60) dayState = states.warning;
                    else dayState = states.danger;
                }
            }
        }

        document.getElementById(`${day}`).style.borderColor = dayState.color;
        document.getElementById(`${day.toLowerCase()}-state`).innerText = dayState.text;
        document.getElementById(`${day.toLowerCase()}-state`).style.color = dayState.color;
    }

    // document.getElementById('matematyka-attendance').innerText = `Frekwencja: ${data.matematyka.attendance_rate}%`;
    // document.getElementById('matematyka-safe-skip').innerText = `Safe skip: ${data.matematyka.safe_skip}`;
    // document.getElementById('matematyka-max-skip').innerText = `Max skip: ${data.matematyka.max_skip}`;
    // document.getElementById('matematyka-progress').style.width = `${data.matematyka.progress}%`;
})