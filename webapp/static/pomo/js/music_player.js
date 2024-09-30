let isPlaying = false;
let currentSongIndex = 0;
const songs = [
    { title: 'Summer rain', artist: 'Xethrocc', file: '/static/pomo/audio/summer-rain-xethrocc.m4a' },
    { title: 'Deep', artist: 'Xethrocc', file: '/static/pomo/audio/deep-xethrocc.mp3' },
    { title: 'For a dream', artist: 'Xethrocc', file: '/static/pomo/audio/for-a-dream-xethrocc.m4a' },
    // Add more songs here
];
const music = new Audio(songs[currentSongIndex].file);

// Update the displayed title and artist
function updateSongInfo() {
    document.getElementById('music-title').innerText = `${songs[currentSongIndex].title} - ${songs[currentSongIndex].artist}`;
}

function togglePlay() {
    if (isPlaying) {
        music.pause();
    } else {
        music.play();
    }
    isPlaying = !isPlaying;
    document.getElementById('play-pause').innerText = isPlaying ? '⏸' : '⏯';
}



function nextSong() {
    currentSongIndex = (currentSongIndex + 1) % songs.length;
    music.src = songs[currentSongIndex].file;
    updateSongInfo();
    music.play();
    isPlaying = true;
    document.getElementById('play-pause').innerText = '⏸';
}

function prevSong() {
    currentSongIndex = (currentSongIndex - 1 + songs.length) % songs.length;
    music.src = songs[currentSongIndex].file;
    updateSongInfo();
    music.play();
    isPlaying = true;
    document.getElementById('play-pause').innerText = '⏸';
}

function setVolume(value) {
    music.volume = value;
}

// Initialize song info when the page loads

document.addEventListener('DOMContentLoaded', function() {
    updateSongInfo();  // Update song info when the page loads
});
