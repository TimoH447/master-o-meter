// Main pomodoro timer
let mainTimer;
let mainSeconds = 0;
let mainMinutes = 25;
let mainHours = 0;
let mainIsTimerRunning = false;

const audio = new Audio('static/media/audio/Airtel Mp3 - Airtel Song.mp3');

function startMainTimer(minutes, pomodoroCount) {
    mainMinutes = minutes;
    mainSeconds = 0;
    mainHours = 0;

    if (!mainIsTimerRunning) {
        mainTimer = setInterval(() => updateMainTimer(pomodoroCount), 1000);
        mainIsTimerRunning = true;
    }
}

function updateMainTimer(pomodoroCount) {
    mainSeconds--;

    if (mainSeconds < 0) {
        mainSeconds = 59;
        mainMinutes--;

        if (mainMinutes < 0) {
            mainMinutes = 0;
            mainHours--;

            if (mainHours < 0) {
                clearInterval(mainTimer);
                timerComplete(pomodoroCount);  // Call timerComplete with 1 or 2 pomodoros
                return;
            }
        }
    }

    updateMainTimerDisplay();
}


/*function updateMainTimerDisplay() {
    const formattedMainHours = padTime(mainHours);
    const formattedMainMinutes = padTime(mainMinutes);
    const formattedMainSeconds = padTime(mainSeconds);

    document.getElementById('hours').innerText = formattedMainHours;
    document.getElementById('minutes').innerText = formattedMainMinutes;
    document.getElementById('seconds').innerText = formattedMainSeconds;
}*/
function updateMainTimerDisplay() {
    document.getElementById("hours").innerText = String(mainHours).padStart(2, '0');
    document.getElementById("minutes").innerText = String(mainMinutes).padStart(2, '0');
    document.getElementById("seconds").innerText = String(mainSeconds).padStart(2, '0');
}

function pauseTimer() {
    clearInterval(mainTimer);
    mainIsTimerRunning = false;
}

function resetTimer() {
    clearInterval(mainTimer);
    mainIsTimerRunning = false;
    mainSeconds = 0;
    mainHours = 0;
    mainMinutes = 25;
    updateMainTimerDisplay();
}

function padTime(time) {
    return (time < 10) ? `0${time}` : time;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function timerComplete(pomodoroCount) {
    // Play a sound
    const audio1 = new Audio('/static/media/audio/Airtel Mp3 - Airtel Song.mp3');
    console.log("Played...");
    audio1.play();

    // Send the completion data to the Django view
    fetch('/timer-complete/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),  // CSRF token for Django
        },
        body: JSON.stringify({
            'duration': pomodoroCount  // 1 for 25 min, 2 for 50 min
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
