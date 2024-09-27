// Main pomodoro timer
let mainTimer;
let mainSeconds = 0;
let mainMinutes = 25;
let mainHours = 0;
let mainIsTimerRunning = false;

const audio = new Audio('static/media/audio/Airtel Mp3 - Airtel Song.mp3');

function startMainTimer() {
    if (!mainIsTimerRunning) {
        mainTimer = setInterval(updateMainTimer, 1000);
        mainIsTimerRunning = true;
    }
}

function updateMainTimer() {
    mainSeconds--;

    if (mainSeconds < 0) {
        mainSeconds = 59;

        mainMinutes--;

        if (mainMinutes < 0) {
            mainMinutes = 59;

            mainHours--;

            if (mainHours < 0) {
                clearInterval(mainTimer);
                timerComplete();
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

function timerComplete() {
    audio.play();
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



// For individual timer
const timers = {};

function startITimer(timerId) {
    const initialMinutes = parseInt(document.getElementById(`initialMinutes${timerId}`).innerText) || 0;
    const initialSeconds = parseInt(document.getElementById(`initialSeconds${timerId}`).innerText) || 0;

    const totalSeconds = initialMinutes * 60 + initialSeconds;

    timers[timerId] = {
        timer: setInterval(() => updateITimer(timerId), 1000),
        isTimerRunning: true,
        hours: 0,
        minutes: initialMinutes,
        seconds: initialSeconds,
        totalSeconds: totalSeconds,
        progressBar: document.getElementById(`progressBar${timerId}`)
    };

    setProgressBarDuration(timerId, totalSeconds);
    updateITimerDisplay(timerId);
}

function setProgressBarDuration(timerId, duration) {
    const progressBar = timers[timerId].progressBar;
    progressBar.style.setProperty('--duration', duration + 's');
}

function updateITimer(timerId) {
    let timer = timers[timerId];

    // Check if the timer is running
    if (timer.isTimerRunning) {
        timer.seconds--;

        if (timer.seconds < 0) {
            timer.seconds = 59;
            timer.minutes--;

            if (timer.minutes < 0) {
                timer.minutes = 59;
                timer.hours--;

                if (timer.hours < 0) {
                    clearInterval(timer.timer);
                    timerComplete(timerId);
                    timer.isTimerRunning = false;
                    return;
                }
            }
        }

        updateITimerDisplay(timerId);
        updateProgressBar(timerId);
    }
}

function updateProgressBar(timerId) {
    let timer = timers[timerId];

    // Check if the timer is still running
    if (timer.isTimerRunning) {
        let remainingSeconds = timer.hours * 3600 + timer.minutes * 60 + timer.seconds;
        let progressPercentage = ((timer.totalSeconds - remainingSeconds) / timer.totalSeconds) * 100;

        timer.progressBar.style.width = `${progressPercentage}%`;
    }
}


function pauseITimer(timerId) {
    const timer = timers[timerId];

    if (timer.isTimerRunning) {
        clearInterval(timer.timer);
        timer.isTimerRunning = false;
    }
}

function resumeITimer(timerId) {
    const timer = timers[timerId];

    if (!timer.isTimerRunning) {
        timer.timer = setInterval(() => updateITimer(timerId), 1000);
        timer.isTimerRunning = true;
    }
}

function resetITimer(timerId) {
    const timerIdInput = document.querySelector(`input.timerId[value='${timerId}']`);
    const initialMinutes = parseInt(document.getElementById(`initialMinutes${timerId}`).innerText) || 0;
    const initialSeconds = parseInt(document.getElementById(`initialSeconds${timerId}`).innerText) || 0;

    let timer = timers[timerId];
    clearInterval(timer.timer);
    timer.isTimerRunning = false;
    timer.seconds = initialSeconds;
    timer.hours = 0;
    timer.minutes = initialMinutes;
    updateITimerDisplay(timerId);
}

function timerComplete(timerId) {
    const audio1 = new Audio('static/media/audio/Airtel Mp3 - Airtel Song.mp3');
    console.log("Played...")
    audio1.play();
}

function updateITimerDisplay(timerId) {
    let timer = timers[timerId];
    const formattedHours = padTime(timer.hours);
    const formattedMinutes = padTime(timer.minutes);
    const formattedSeconds = padTime(timer.seconds);

    document.getElementById(`hours${timerId}`).innerText = formattedHours;
    document.getElementById(`minutes${timerId}`).innerText = formattedMinutes;
    document.getElementById(`seconds${timerId}`).innerText = formattedSeconds;
}

function padTime(time) {
    return (time < 10) ? `0${time}` : time;
}
