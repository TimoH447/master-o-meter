document.addEventListener('DOMContentLoaded', function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

function playMusic() {
    const musicold = document.getElementById('music');
    
    if (musicold.paused) {
        musicold.volume = 0.2;  // Set volume (adjust as needed)
        musicold.play();
    } else {
        musicold.pause();
        musicold.currentTime = 0;  // Optional: reset the music to the start
    }
}