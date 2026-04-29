const hamburger = document.getElementById('ac-hamburger');
const mobileNav = document.getElementById('ac-mobile-nav');
const closeBtn  = document.getElementById('ac-mobile-close');

hamburger?.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    mobileNav.classList.toggle('open');
});

closeBtn?.addEventListener('click', () => {
    hamburger.classList.remove('open');
    mobileNav.classList.remove('open');
});

mobileNav?.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('open');
        mobileNav.classList.remove('open');
    });
});
