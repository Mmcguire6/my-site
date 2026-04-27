window.addEventListener('DOMContentLoaded', () => {
    const introScreen  = document.getElementById('intro-screen');
    const introName    = document.getElementById('intro-name');
    const profileScreen = document.getElementById('profile-screen');
    const profiles     = document.querySelectorAll('.profile');

    function playIntroSound() {
        try {
            const Ctx = window.AudioContext || window.webkitAudioContext;
            if (!Ctx) return;
            const ctx = new Ctx();
            const now = ctx.currentTime;

            function hit(t, freq, vol, dur) {
                // Main tone
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.frequency.setValueAtTime(freq, t);
                osc.frequency.exponentialRampToValueAtTime(freq * 0.28, t + dur);
                gain.gain.setValueAtTime(0, t);
                gain.gain.linearRampToValueAtTime(vol, t + 0.012);
                gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(t);
                osc.stop(t + dur + 0.1);

                // Sub octave
                const sub = ctx.createOscillator();
                const subGain = ctx.createGain();
                sub.frequency.setValueAtTime(freq * 0.5, t);
                sub.frequency.exponentialRampToValueAtTime(freq * 0.12, t + dur * 1.4);
                subGain.gain.setValueAtTime(0, t);
                subGain.gain.linearRampToValueAtTime(vol * 0.6, t + 0.02);
                subGain.gain.exponentialRampToValueAtTime(0.0001, t + dur * 1.4);
                sub.connect(subGain);
                subGain.connect(ctx.destination);
                sub.start(t);
                sub.stop(t + dur * 1.4 + 0.1);

                // Attack transient click
                const click = ctx.createOscillator();
                const clickGain = ctx.createGain();
                click.type = 'triangle';
                click.frequency.setValueAtTime(280, t);
                clickGain.gain.setValueAtTime(vol * 0.25, t);
                clickGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.04);
                click.connect(clickGain);
                clickGain.connect(ctx.destination);
                click.start(t);
                click.stop(t + 0.05);
            }

            hit(now,        125, 0.65, 0.85);  // first dum
            hit(now + 0.62, 105, 0.95, 1.3);   // second dum (louder, longer)
        } catch (e) {
            // AudioContext blocked or unavailable — silent fallback
        }
    }

    // Kick off sequence after a brief pause
    setTimeout(() => {
        playIntroSound();
        introName.classList.add('animate');
    }, 250);

    // Transition to profile selection
    setTimeout(() => {
        introScreen.classList.add('fade-out');
        profileScreen.classList.add('visible');

        profiles.forEach((p, i) => {
            setTimeout(() => p.classList.add('visible'), 200 + i * 130);
        });
    }, 3100);
});

function goToPortfolio() {
    const overlay = document.getElementById('fade-overlay');
    overlay.classList.add('active');
    setTimeout(() => {
        window.location.href = 'portfolio.html';
    }, 450);
}
