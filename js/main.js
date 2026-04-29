const nav = document.getElementById('nav');

window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
});

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, { threshold: 0.12 });

document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

// ── Active nav links ──
const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
const sections = [...navLinks].map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);

const setActiveLink = (id) => {
    navLinks.forEach(a => a.classList.toggle('nav-link--active', a.getAttribute('href') === `#${id}`));
};

const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) setActiveLink(entry.target.id);
    });
}, { rootMargin: '-50% 0px -50% 0px' });

sections.forEach(s => sectionObserver.observe(s));

// ── Mobile nav ──
const hamburger = document.getElementById('nav-hamburger');
const mobileMenu = document.getElementById('nav-mobile-menu');

hamburger?.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    mobileMenu.classList.toggle('open');
});

mobileMenu?.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('open');
        mobileMenu.classList.remove('open');
    });
});

// ── Row sliders ──
document.querySelectorAll('.row').forEach(row => {
    const track = row.querySelector('.row-cards');
    if (!track) return;

    const prev = document.createElement('button');
    const next = document.createElement('button');
    prev.className = 'row-arrow row-arrow--prev';
    next.className = 'row-arrow row-arrow--next';
    prev.innerHTML = '&#10094;';
    next.innerHTML = '&#10095;';
    row.appendChild(prev);
    row.appendChild(next);

    const scrollAmount = () => track.clientWidth * 0.75;

    prev.addEventListener('click', () => track.scrollBy({ left: -scrollAmount(), behavior: 'smooth' }));
    next.addEventListener('click', () => track.scrollBy({ left:  scrollAmount(), behavior: 'smooth' }));

    const updateArrows = () => {
        prev.classList.toggle('row-arrow--disabled', track.scrollLeft <= 0);
        const atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
        next.classList.toggle('row-arrow--disabled', atEnd);
    };

    track.addEventListener('scroll', updateArrows);
    updateArrows();

    // Click-and-drag with momentum
    let isDragging = false, startX = 0, scrollStart = 0;
    let velocity = 0, lastX = 0, lastTime = 0, rafId = null;

    track.addEventListener('mousedown', e => {
        isDragging = true;
        startX = e.pageX;
        scrollStart = track.scrollLeft;
        lastX = e.pageX;
        lastTime = Date.now();
        velocity = 0;
        cancelAnimationFrame(rafId);
        track.style.cursor = 'grabbing';
        track.style.userSelect = 'none';
    });

    window.addEventListener('mousemove', e => {
        if (!isDragging) return;
        const now = Date.now();
        const dt = now - lastTime;
        if (dt > 0) velocity = (e.pageX - lastX) / dt;
        lastX = e.pageX;
        lastTime = now;
        track.scrollLeft = scrollStart - (e.pageX - startX);
    });

    window.addEventListener('mouseup', () => {
        if (!isDragging) return;
        isDragging = false;
        track.style.cursor = '';
        track.style.userSelect = '';

        let v = velocity * 14;
        const decay = () => {
            if (Math.abs(v) < 0.5) return;
            track.scrollLeft -= v;
            v *= 0.92;
            rafId = requestAnimationFrame(decay);
        };
        rafId = requestAnimationFrame(decay);
    });
});
