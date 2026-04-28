window.addEventListener('DOMContentLoaded', () => {
    const introScreen  = document.getElementById('intro-screen');
    const introName    = document.getElementById('intro-name');
    const profileScreen = document.getElementById('profile-screen');
    const profiles     = document.querySelectorAll('.profile');

    function playIntroSound() {
        const audio = new Audio('audio/Netflix intro - QuickSounds.com.mp3');
        audio.play().catch(() => {});
    }

    // Fade in to idle state
    setTimeout(() => introName.classList.add('ready'), 300);

    introScreen.style.cursor = 'pointer';

    introScreen.addEventListener('click', () => {
        introScreen.style.cursor = 'default';
        introName.classList.remove('ready');
        playIntroSound();
        requestAnimationFrame(() => requestAnimationFrame(() => introName.classList.add('animate')));

        setTimeout(() => {
            introScreen.classList.add('fade-out');
            profileScreen.classList.add('visible');

            profiles.forEach((p, i) => {
                setTimeout(() => p.classList.add('visible'), 200 + i * 130);
            });
        }, 2850);
    }, { once: true });

});

function goToPortfolio() {
    const overlay = document.getElementById('fade-overlay');
    overlay.classList.add('active');
    setTimeout(() => {
        window.location.href = 'portfolio.html';
    }, 450);
}
