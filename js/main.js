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
    const container = row.querySelector('.row-cards');
    if (!container) return;

    const track = document.createElement('div');
    track.className = 'row-track';
    while (container.firstChild) track.appendChild(container.firstChild);
    container.appendChild(track);

    const firstCard = track.querySelector('.card');
    if (!firstCard) return;

    const gap = 14;
    const cardW    = () => firstCard.offsetWidth + gap;
    const pageW    = () => Math.floor(container.offsetWidth / cardW()) * cardW();
    const maxOff   = () => Math.max(0, track.children.length * cardW() - gap - container.offsetWidth);

    let offset = 0;

    const prevBtn = document.createElement('button');
    const nextBtn = document.createElement('button');
    prevBtn.className = 'row-arrow row-arrow--prev';
    nextBtn.className = 'row-arrow row-arrow--next';
    prevBtn.innerHTML = '&#10094;';
    nextBtn.innerHTML = '&#10095;';
    row.appendChild(prevBtn);
    row.appendChild(nextBtn);

    const update = () => {
        track.style.transform = `translateX(${-offset}px)`;
        const atStart = offset <= 0;
        const atEnd   = offset >= maxOff() - 2;
        prevBtn.classList.toggle('row-arrow--disabled', atStart);
        nextBtn.classList.toggle('row-arrow--disabled', atEnd);
        row.classList.toggle('row--has-prev', !atStart);
        row.classList.toggle('row--has-next', !atEnd);
    };

    prevBtn.addEventListener('click', () => { offset = Math.max(0,        offset - pageW()); update(); });
    nextBtn.addEventListener('click', () => { offset = Math.min(maxOff(), offset + pageW()); update(); });

    // Drag scroll (touch + mouse)
    let dragStartX = 0;
    let dragStartY = 0;
    let dragBase   = 0;
    let dragging   = false;

    const onDragStart = (x, y) => {
        dragStartX = x;
        dragStartY = y;
        dragBase   = offset;
        dragging   = false;
        track.style.transition = 'none';
    };

    const onDragMove = (x, y, isTouch) => {
        const dx = x - dragStartX;
        const dy = y - dragStartY;
        if (!dragging) {
            if (isTouch && Math.abs(dx) < Math.abs(dy)) { track.style.transition = ''; return; }
            if (Math.abs(dx) < 4) return;
            dragging = true;
            container.style.cursor = 'grabbing';
        }
        track.style.transform = `translateX(${-(Math.max(0, Math.min(maxOff(), dragBase - dx)))}px)`;
    };

    const onDragEnd = (x) => {
        track.style.transition = '';
        container.style.cursor = '';
        if (!dragging) return;
        const dx = x - dragStartX;
        offset = Math.round(Math.max(0, Math.min(maxOff(), dragBase - dx)) / cardW()) * cardW();
        update();
        // Block the click that fires after mouseup on the card
        track.addEventListener('click', e => e.stopPropagation(), { once: true, capture: true });
    };

    // Touch
    row.addEventListener('touchstart', e => onDragStart(e.touches[0].clientX, e.touches[0].clientY), { passive: true });
    row.addEventListener('touchmove',  e => { e.preventDefault(); onDragMove(e.touches[0].clientX, e.touches[0].clientY, true); }, { passive: false });
    row.addEventListener('touchend',   e => onDragEnd(e.changedTouches[0].clientX));

    // Mouse
    let mouseIsDown = false;
    row.addEventListener('mousedown', e => { e.preventDefault(); mouseIsDown = true; onDragStart(e.clientX, e.clientY); });
    window.addEventListener('mousemove', e => { if (mouseIsDown) onDragMove(e.clientX, e.clientY, false); });
    window.addEventListener('mouseup',   e => { if (!mouseIsDown) return; mouseIsDown = false; onDragEnd(e.clientX); });

    update();
});
