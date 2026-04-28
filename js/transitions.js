(function () {
    'use strict';

    // Fade in on page load
    document.documentElement.style.opacity = '0';
    document.documentElement.style.transition = 'opacity 0.4s ease';

    document.addEventListener('DOMContentLoaded', function () {
        requestAnimationFrame(function () {
            document.documentElement.style.opacity = '1';
        });

        // Fade out on internal navigation
        document.querySelectorAll('a[href]').forEach(function (link) {
            var href = link.getAttribute('href');
            if (!href ||
                href.charAt(0) === '#' ||
                link.getAttribute('target') === '_blank' ||
                href.indexOf('mailto:') === 0 ||
                href.indexOf('http') === 0 ||
                href.indexOf('tel:') === 0) return;

            link.addEventListener('click', function (e) {
                e.preventDefault();
                var dest = href;
                document.documentElement.style.opacity = '0';
                setTimeout(function () { window.location.href = dest; }, 380);
            });
        });

        // Scroll fade-up
        var els = document.querySelectorAll('.fade-up');
        if (!els.length) return;

        if (!('IntersectionObserver' in window)) {
            els.forEach(function (el) { el.classList.add('visible'); });
            return;
        }

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var delay = parseInt(entry.target.dataset.delay || 0, 10);
                setTimeout(function () { entry.target.classList.add('visible'); }, delay);
                io.unobserve(entry.target);
            });
        }, { threshold: 0.08 });

        els.forEach(function (el) { io.observe(el); });
    });
})();
