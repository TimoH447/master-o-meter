// Main pomodoro timer
let mainTimer;
let mainSeconds = 0;
let mainMinutes = 24;
let mainHours = 0;
let mainIsTimerRunning = false;
let selectedPomodoroCount = 1;  // 1 for 25 min, 2 for 50 min

const audio = new Audio('static/pomo/audio/alarm1.mp3');
document.addEventListener('DOMContentLoaded', function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Function to set the timer's duration (but not start it)
function setTimer(minutes, pomodoroCount) {
    selectedPomodoroCount = pomodoroCount;
    mainMinutes = minutes;
    mainSeconds = 0;
    mainHours = 0;

    clearInterval(mainTimer);  // Ensure any previous timers are cleared
    updateMainTimerDisplay();

}

// Toggle between start and pause
function toggleTimer() {
    if (mainIsTimerRunning) {
        pauseTimer();
    } else {
        startMainTimer(selectedPomodoroCount === 1 ? 25 : 50, selectedPomodoroCount);
    }
}

function startMainTimer() {
    if (!mainIsTimerRunning) {
        mainTimer = setInterval(() => updateMainTimer(selectedPomodoroCount), 1000);
        mainIsTimerRunning = true;
    
        // Change the "Start" button to "Pause"
        document.getElementById('startPauseBtn').textContent = 'Pause';
        // Disable the 25-min and 50-min buttons after starting Timer
        document.getElementById('set25min').disabled = true;
        document.getElementById('set50min').disabled = true;
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


function updateMainTimerDisplay() {
    const formattedMainHours = padTime(mainHours);
    const formattedMainMinutes = padTime(mainMinutes);
    const formattedMainSeconds = padTime(mainSeconds);

    document.getElementById('hours').innerText = formattedMainHours;
    document.getElementById('minutes').innerText = formattedMainMinutes;
    document.getElementById('seconds').innerText = formattedMainSeconds;
}


function pauseTimer() {
    clearInterval(mainTimer);
    mainIsTimerRunning = false;

    // Change the "Pause" button back to "Start"
    document.getElementById('startPauseBtn').textContent = 'Start';
}

function resetTimer() {
    clearInterval(mainTimer);
    mainIsTimerRunning = false;
    mainSeconds = 0;
    mainHours = 0;
    mainMinutes = selectedPomodoroCount === 1 ? 25 : 50;  // Reset to selected duration (25 or 50 minutes)

    updateMainTimerDisplay();
    
    // Change the "Pause" button back to "Start"
    document.getElementById('startPauseBtn').textContent = 'Start';

    // Re-enable the 25-min and 50-min buttons
    document.getElementById('set25min').disabled = false;
    document.getElementById('set50min').disabled = false;
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
    const audio1 = new Audio('/static/pomo/audio/alarm1.mp3');
    console.log("Played...");
    audio1.play();

    // Send the completion data to the Django view
    fetch('/pomo/timer-complete/', {
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
