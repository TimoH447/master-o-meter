let isPlaying = false;
let currentSongIndex = 0;
const songs = [
    { title: 'Ways of the wizard', artist: 'Geoffharvey', file: '/static/pomo/audio/ways-of-the-wizard-geoffharvey.m4a' },
    { title: 'Aquarium', artist: 'Saint Saens', file: '/static/pomo/audio/aquarium-by-saint-saens.mp3' },
    { title: 'School of magic', artist: 'Luis Humanoide', file: '/static/pomo/audio/school-of-magic-inspired-by-harry-potter.mp3' },
    { title: 'Dance of the sugar plum fairy', artist: 'Tchaikovsky', file: '/static/pomo/audio/dance-of-the-sugar-plum-fairy-tchaikovsky.mp3' },
    { title: 'Summer rain', artist: 'Xethrocc', file: '/static/pomo/audio/summer-rain-xethrocc.m4a' },
    { title: 'Deep', artist: 'Xethrocc', file: '/static/pomo/audio/deep-xethrocc.mp3' },
    { title: 'For a dream', artist: 'Xethrocc', file: '/static/pomo/audio/for-a-dream-xethrocc.m4a' },
    { title: 'Forest guitar', artist: 'Xethrocc', file: '/static/pomo/audio/forest-guitar-xethrocc.m4a' },
    { title: 'Power of the wind', artist: 'Xethrocc', file: '/static/pomo/audio/power-of-the-wind-xethrocc.m4a' },
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

function collapseMusicBar() {
    document.getElementById('music-bar').style.display = 'none'; // Hide the music bar
    document.getElementById('expand-button').style.display = 'block'; // Show the expand button
}

function expandMusicBar() {
    document.getElementById('music-bar').style.display = 'flex'; // Show the music bar
    document.getElementById('expand-button').style.display = 'none'; // Hide the expand button
}

// Initialize song info when the page loads

document.addEventListener('DOMContentLoaded', function() {
    updateSongInfo();  // Update song info when the page loads
});
music.addEventListener('ended', nextSong);