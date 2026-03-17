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
    'Monday': {},
    'Tuesday': {},
    'Wednesday': {},
    'Thursday': {},
    'Friday': {}
}

var weeks = 22;

socket.on('attendance_data', (data) =>{

    console.log("Received attendance data:", data);
    const container = document.getElementById(`container`);

    for (const subject in data){
        if (!data[subject].subject_hours || data[subject].subject_hours == 0) continue;

        try {
            let totalHours = (data[subject].subject_hours.hours * data[subject].weeks) - data[subject].subject_hours.times_replaced;

            let safeSkip = Math.floor(totalHours * 0.4) - data[subject].absent_excused - data[subject].absent_unexcused;
            let maxSkip = Math.floor(totalHours * 0.5) - data[subject].absent_excused - data[subject].absent_unexcused;
            let predictedAttendance = totalHours - data[subject].absent_excused - data[subject].absent_unexcused;
            let predictedRate = (predictedAttendance / totalHours) * 100;
            let progress = Math.min(((predictedRate - 50) / 50) * 100, 100);

            const panel = document.createElement("div");
            panel.className = "info-panel";
            panel.id = `${subject}-panel`;
            panel.innerHTML = `
                <div class='panel-header'><span>${data[subject].name}</span></div>
                <div class='panel-content'>
                <span id='${subject}-attendance'>Frekwencja: ${predictedRate.toFixed(1)}%</span>

                <div class="attendance-details">
                    <span id='${subject}-safe-skip'>Safe skip: ${safeSkip}</span>
                    <span id='${subject}-max-skip'>Max skip: ${maxSkip}</span>
                </div>
                <div class='progress-bar'><div class='progress' id='${subject}-progress'></div></div>
                </div></div>
            `;
            container.appendChild(panel);
            document.getElementById(`${subject}-progress`).style.width = `${progress}%`;

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

            for (const day in data[subject].subject_hours.days) {
                daysOfWeek[day][subject] = data[subject].name;
            }

        } catch (error) {
            console.error(`Error updating attendance for ${subject}:`, error);
        }
    }

    for (const day in daysOfWeek) {
        let lowestRate = 100;
        let dayState = states.safe;
        let maxSkip = 9999;

        const dayElement = document.getElementById(`${day}`);
        for (const subject in daysOfWeek[day]) {
            if (data[subject]) {
                const totalHours = (data[subject].subject_hours.hours * data[subject].weeks) - data[subject].subject_hours.times_replaced;
                const predictedAttendance = totalHours - data[subject].absent_excused - data[subject].absent_unexcused;
                const rate = (predictedAttendance / totalHours) * 100;
                const subjectMaxSkip = Math.floor(totalHours * 0.5) - data[subject].absent_excused - data[subject].absent_unexcused;
                
                if (rate < lowestRate) {
                    lowestRate = rate;
                    if (rate >= 80) dayState = states.safe;
                    else if (rate >= 60) dayState = states.warning;
                    else dayState = states.danger;
                }

                if(subjectMaxSkip <= maxSkip){
                    maxSkip = subjectMaxSkip;
                }
                
                const subjectList = dayElement.getElementsByTagName('ul')[0];
                const listItem = document.createElement('li');
                listItem.innerText = data[subject].name;
                subjectList.appendChild(listItem);

            }else{
                console.warn(`Subject ${subject} not found in data for ${day}`);
            }
        }

        document.getElementById(`${day}`).style.borderColor = dayState.color;
        document.getElementById(`${day.toLowerCase()}-state`).innerText = dayState.text;
        document.getElementById(`${day.toLowerCase()}-state`).style.color = dayState.color;
        document.getElementById(`${day.toLowerCase()}-max-skip`).innerText = `${maxSkip}`;
    }
})