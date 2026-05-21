// Bluebird RV Park — shared interactions
(function () {
    var nav = document.getElementById('nav');
    if (nav) {
        window.addEventListener('scroll', function () {
            nav.classList.toggle('scrolled', window.scrollY > 40);
        }, { passive: true });
    }
    var t = document.getElementById('navToggle');
    var l = document.getElementById('navLinks');
    if (t && l) {
        t.addEventListener('click', function () {
            t.classList.toggle('open');
            l.classList.toggle('open');
        });
        l.querySelectorAll('a').forEach(function (a) {
            a.addEventListener('click', function () {
                t.classList.remove('open');
                l.classList.remove('open');
            });
        });
    }
    // Seed any .stars containers with twinkling star elements
    document.querySelectorAll('.stars').forEach(function (el) {
        var n = parseInt(el.getAttribute('data-n'), 10) || 60;
        var h = '';
        for (var i = 0; i < n; i++) {
            var x = (Math.random() * 100).toFixed(2);
            var y = (Math.random() * 100).toFixed(2);
            var d = (Math.random() * 4).toFixed(2);
            var s = (3 + Math.random() * 3).toFixed(2);
            h += '<span style="left:' + x + '%;top:' + y + '%;animation-delay:' + d + 's;animation-duration:' + s + 's"></span>';
        }
        el.innerHTML = h;
    });
    // Patio string lights — draw a sagging string with glowing bulbs across the hero
    document.querySelectorAll('.string-lights').forEach(function (el) {
        var count = 18;
        var w = 100, h = 100; // viewBox units (percent-like)
        var bulbs = '';
        for (var i = 0; i < count; i++) {
            var fx = (i + 0.5) / count;
            var cx = fx * w;
            // sag follows a parabola: y = a*(x-0.5)^2 + base
            var cy = 30 + 30 * (1 - Math.pow((fx - 0.5) * 2, 2));
            bulbs += '<g class="bulb" transform="translate(' + cx.toFixed(2) + ',' + cy.toFixed(2) + ')">' +
                '<line x1="0" y1="-6" x2="0" y2="0" stroke="rgba(40,30,20,0.6)" stroke-width=".6"/>' +
                '<circle cx="0" cy="3.5" r="2.6" fill="#F6CE7E"/>' +
                '<circle cx="0" cy="3.5" r="5.5" fill="#F6CE7E" opacity=".22"/>' +
            '</g>';
        }
        // Sagging wire path
        var d = 'M 0 30 Q 50 80 100 30';
        el.innerHTML = '<svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">' +
            '<path d="' + d + '" stroke="rgba(255,235,180,.45)" stroke-width=".6" fill="none"/>' +
            bulbs + '</svg>';
    });
    // Lightbox — intercept clicks on any anchor pointing to an image and overlay it
    (function () {
        var imgExt = /\.(jpe?g|png|webp|gif|avif)(\?.*)?$/i;
        var triggers = Array.prototype.filter.call(
            document.querySelectorAll('a[href]'),
            function (a) {
                var href = a.getAttribute('href') || '';
                if (!imgExt.test(href)) return false;
                if (a.hasAttribute('data-no-lightbox')) return false;
                return true;
            }
        );
        if (!triggers.length) return;

        var box = document.createElement('div');
        box.className = 'lightbox';
        box.setAttribute('aria-hidden', 'true');
        box.innerHTML =
            '<button class="lightbox-close" type="button" aria-label="Close">' +
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="22" height="22"><path d="M6 6l12 12M18 6L6 18"/></svg>' +
            '</button>' +
            '<figure class="lightbox-figure">' +
                '<img alt="" />' +
                '<figcaption class="lightbox-cap"></figcaption>' +
            '</figure>';
        document.body.appendChild(box);

        var imgEl = box.querySelector('img');
        var capEl = box.querySelector('.lightbox-cap');
        var closeBtn = box.querySelector('.lightbox-close');
        var lastFocus = null;

        function captionFor(a) {
            var cap = a.querySelector('.cap, .scene-cap');
            if (cap) return cap.textContent.trim();
            var img = a.querySelector('img');
            if (img && img.alt) return img.alt;
            return '';
        }

        function open(href, alt, caption, trigger) {
            lastFocus = trigger || document.activeElement;
            imgEl.src = href;
            imgEl.alt = alt || '';
            if (caption) {
                capEl.textContent = caption;
                capEl.style.display = '';
            } else {
                capEl.textContent = '';
                capEl.style.display = 'none';
            }
            box.classList.add('open');
            box.setAttribute('aria-hidden', 'false');
            document.documentElement.style.overflow = 'hidden';
            setTimeout(function () { closeBtn.focus(); }, 50);
        }

        function close() {
            box.classList.remove('open');
            box.setAttribute('aria-hidden', 'true');
            document.documentElement.style.overflow = '';
            imgEl.src = '';
            if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
        }

        triggers.forEach(function (a) {
            a.removeAttribute('target');
            a.addEventListener('click', function (e) {
                if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button === 1) return;
                e.preventDefault();
                var inner = a.querySelector('img');
                open(a.getAttribute('href'), inner ? inner.alt : '', captionFor(a), a);
            });
        });

        box.addEventListener('click', function (e) {
            if (e.target === box || e.target.closest('.lightbox-close')) close();
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && box.classList.contains('open')) close();
        });
    })();

    if ('IntersectionObserver' in window) {
        var io = new IntersectionObserver(function (es) {
            es.forEach(function (e) {
                if (e.isIntersecting) {
                    e.target.classList.add('in');
                    io.unobserve(e.target);
                }
            });
        }, { threshold: 0.14, rootMargin: '0px 0px -40px 0px' });
        document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
    } else {
        document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in'); });
    }
})();
