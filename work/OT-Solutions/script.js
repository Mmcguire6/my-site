(function () {
  'use strict';

  // ── Nav: backdrop/border once scrolled ──
  var nav = document.getElementById('site-nav');
  if (nav) {
    var onScroll = function () {
      if (window.scrollY > 8) nav.classList.add('nav-scrolled');
      else nav.classList.remove('nav-scrolled');
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ── Mobile hamburger menu ──
  var navToggle = document.getElementById('nav-toggle');
  var navDrawer = document.getElementById('nav-mobile');
  if (navToggle && navDrawer) {
    var setMenu = function (open) {
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      navDrawer.hidden = !open;
      document.body.classList.toggle('nav-open', open);
    };
    navToggle.addEventListener('click', function () { setMenu(navDrawer.hidden); });
    navDrawer.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !navDrawer.hidden) setMenu(false); });
    window.addEventListener('resize', function () { if (window.innerWidth > 760 && !navDrawer.hidden) setMenu(false); });
  }

  // ── Footer year ──
  var yearEl = document.getElementById('footer-year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // ── Services accordion ──
  document.querySelectorAll('.svc-row-head').forEach(function (head) {
    head.addEventListener('click', function () {
      var row = head.closest('.svc-row');
      if (!row) return;
      var isOpen = row.classList.toggle('open');
      head.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      var toggle = head.querySelector('.svc-row-toggle');
      if (toggle) toggle.textContent = isOpen ? '–' : '+';
    });
  });

  // ── Contact form: AJAX submit to Netlify Forms ──
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var submitBtn = form.querySelector('.cf-submit');
      var success = form.querySelector('.cf-success');
      var error = form.querySelector('.cf-error');
      if (success) success.hidden = true;
      if (error) error.hidden = true;
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.originalLabel = submitBtn.dataset.originalLabel || submitBtn.innerHTML;
        submitBtn.textContent = 'Sending…';
      }
      var data = new FormData(form);
      var body = new URLSearchParams();
      data.forEach(function (value, key) { body.append(key, value); });
      fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString(),
      })
        .then(function (response) {
          if (!response.ok) throw new Error('Network response was not ok: ' + response.status);
          form.querySelectorAll('input, textarea').forEach(function (el) { if (el.type !== 'hidden') el.value = ''; });
          if (success) success.hidden = false;
          if (typeof window.gtag === 'function') { window.gtag('event', 'contact_form_submit', { event_category: 'engagement' }); }
        })
        .catch(function () { if (error) error.hidden = false; })
        .finally(function () {
          if (submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = submitBtn.dataset.originalLabel; }
        });
    });
  }

  // ════════════════ MOTION LAYER ════════════════
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasGSAP = typeof window.gsap !== 'undefined';

  // Scroll-progress bar (injected — no markup needed)
  var bar = document.createElement('div');
  bar.setAttribute('aria-hidden', 'true');
  bar.style.cssText = 'position:fixed;top:0;left:0;height:3px;width:0;z-index:200;pointer-events:none;background:linear-gradient(90deg,var(--accent),var(--gold));';
  document.body.appendChild(bar);
  function setProgress(scroll) {
    var h = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (h > 0 ? (scroll / h) * 100 : 0) + '%';
  }

  // Fallback reveals (no GSAP / reduced motion) — CSS handles via .in
  function fallbackReveals() {
    var els = document.querySelectorAll('.reveal, .reveal-stagger');
    if (!('IntersectionObserver' in window)) { els.forEach(function (el) { el.classList.add('in'); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('in'); io.unobserve(entry.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    els.forEach(function (el) { io.observe(el); });
  }

  if (reduce || !hasGSAP) {
    fallbackReveals();
    window.addEventListener('scroll', function () { setProgress(window.scrollY); }, { passive: true });
    setProgress(window.scrollY);
    return;
  }

  var gsap = window.gsap;
  var ScrollTrigger = window.ScrollTrigger;
  gsap.registerPlugin(ScrollTrigger);

  // ── Lenis smooth scroll ──
  var lenis = null;
  if (typeof window.Lenis !== 'undefined') {
    document.documentElement.style.scrollBehavior = 'auto';
    lenis = new window.Lenis({
      duration: 1.1,
      smoothWheel: true,
      easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); }
    });
    lenis.on('scroll', function (e) { ScrollTrigger.update(); setProgress(e.scroll); });
    var raf = function (time) { lenis.raf(time); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
  } else {
    window.addEventListener('scroll', function () { setProgress(window.scrollY); }, { passive: true });
  }

  // ── Smooth same-page anchor links ──
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    var id = a.getAttribute('href');
    if (!id || id.length <= 1) return;
    a.addEventListener('click', function (e) {
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      if (lenis) lenis.scrollTo(target, { offset: -90, duration: 1.1 });
      else target.scrollIntoView();
    });
  });

  // GSAP owns the reveal targets — neutralize the CSS transition
  gsap.set('.reveal, .reveal-stagger > *', { transition: 'none' });

  // ── Reveals ──
  gsap.utils.toArray('.reveal').forEach(function (el) {
    gsap.fromTo(el, { autoAlpha: 0, y: 28 },
      { autoAlpha: 1, y: 0, duration: 0.9, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 86%' } });
  });
  gsap.utils.toArray('.reveal-stagger').forEach(function (group) {
    gsap.fromTo(group.children, { autoAlpha: 0, y: 24 },
      { autoAlpha: 1, y: 0, duration: 0.8, ease: 'power3.out', stagger: 0.09, scrollTrigger: { trigger: group, start: 'top 86%' } });
  });

  // ── Parallax homepage hero background ──
  gsap.utils.toArray('.hero-s-bg img').forEach(function (img) {
    gsap.set(img, { scale: 1.12, transformOrigin: 'center center' });
    gsap.to(img, { yPercent: 8, ease: 'none', scrollTrigger: { trigger: '.hero-split', start: 'top top', end: 'bottom top', scrub: true } });
  });

  // ── Magnetic primary buttons (fine pointers only) ──
  if (window.matchMedia('(pointer: fine)').matches) {
    document.querySelectorAll('.btn-primary').forEach(function (btn) {
      var xTo = gsap.quickTo(btn, 'x', { duration: 0.4, ease: 'power3' });
      var yTo = gsap.quickTo(btn, 'y', { duration: 0.4, ease: 'power3' });
      btn.addEventListener('mousemove', function (e) {
        var r = btn.getBoundingClientRect();
        xTo((e.clientX - (r.left + r.width / 2)) * 0.3);
        yTo((e.clientY - (r.top + r.height / 2)) * 0.45);
      });
      btn.addEventListener('mouseleave', function () { xTo(0); yTo(0); });
    });
  }

  setProgress(window.scrollY || 0);
  ScrollTrigger.refresh();
})();
