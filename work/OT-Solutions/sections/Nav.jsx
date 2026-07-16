/* global React */
const { useState, useEffect } = React;

function Nav({ onContactClick }) {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);
  useEffect(() => {
    document.body.classList.toggle('nav-open', open);
    const onKey = (e) => { if (e.key === 'Escape') setOpen(false); };
    const onResize = () => { if (window.innerWidth > 760) setOpen(false); };
    window.addEventListener('keydown', onKey);
    window.addEventListener('resize', onResize);
    return () => {
      document.body.classList.remove('nav-open');
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('resize', onResize);
    };
  }, [open]);

  const links = [
    { href: '#services', label: 'Services' },
    { href: '#why', label: 'Why Us' },
    { href: '#testimonials', label: 'References' },
    { href: '#contact', label: 'Contact' },
  ];

  return (
    <header className={`nav ${scrolled ? 'nav-scrolled' : ''}`}>
      <div className="wrap nav-inner">
        <a href="#top" className="nav-brand" aria-label="OT Solutions home">
          <span className="nav-mark" aria-hidden="true">
            <img className="logo-light" src="assets/logo-mark-navy.png" alt="" />
            <img className="logo-dark" src="assets/logo-mark-accent.png" alt="" />
          </span>
          <span className="nav-words">
            <span className="nav-name">OT Solutions</span>
            <span className="nav-tag">Putting Data In Your Hands</span>
          </span>
        </a>
        <nav className="nav-links hide-sm" aria-label="Primary">
          {links.map(l => (
            <a key={l.href} href={l.href}>{l.label}</a>
          ))}
        </nav>
        <a href="#contact" className="btn btn-primary nav-cta" onClick={onContactClick}>
          Connect <span className="arrow">→</span>
        </a>
        <button
          className="nav-toggle"
          type="button"
          aria-label={open ? 'Close menu' : 'Open menu'}
          aria-expanded={open}
          aria-controls="nav-mobile"
          onClick={() => setOpen(o => !o)}
        >
          <span className="nav-toggle-bar"></span>
          <span className="nav-toggle-bar"></span>
          <span className="nav-toggle-bar"></span>
        </button>
      </div>
      <div className="nav-mobile" id="nav-mobile" hidden={!open}>
        <nav className="nav-mobile-links" aria-label="Mobile navigation">
          {links.map(l => (
            <a key={l.href} href={l.href} onClick={() => setOpen(false)}>{l.label}</a>
          ))}
        </nav>
        <a
          href="#contact"
          className="btn btn-primary nav-mobile-cta"
          onClick={(e) => { setOpen(false); if (onContactClick) onContactClick(e); }}
        >
          Connect <span className="arrow">→</span>
        </a>
      </div>
      <style>{`
        .nav {
          position: sticky;
          top: 0;
          z-index: 50;
          background: transparent;
          backdrop-filter: none;
          -webkit-backdrop-filter: none;
          border-bottom: 1px solid transparent;
          transition: border-color 200ms ease, background 200ms ease, backdrop-filter 200ms ease;
        }
        .nav-scrolled {
          background: color-mix(in oklch, var(--bg) 88%, transparent);
          backdrop-filter: saturate(140%) blur(12px);
          -webkit-backdrop-filter: saturate(140%) blur(12px);
          border-bottom-color: var(--rule);
        }
        .nav-inner {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-top: 16px;
          padding-bottom: 16px;
          gap: 24px;
        }
        .nav-brand {
          display: inline-flex;
          align-items: center;
          gap: 12px;
          color: var(--ink);
        }
        .nav-mark {
          display: inline-flex;
          color: var(--ink);
        }
        .nav-mark img {
          width: 34px;
          height: 34px;
          display: block;
          object-fit: contain;
        }
        .nav-mark .logo-dark { display: none; }
        [data-theme="dark"] .nav-mark .logo-light { display: none; }
        [data-theme="dark"] .nav-mark .logo-dark { display: block; }
        .nav-words {
          display: flex;
          flex-direction: column;
          line-height: 1;
        }
        .nav-name {
          font-weight: 600;
          font-size: 15px;
          letter-spacing: -0.01em;
        }
        .nav-tag {
          font-family: var(--mono);
          font-size: 10px;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: var(--ink-3);
          margin-top: 4px;
        }
        .nav-links {
          display: flex;
          gap: 32px;
          align-items: center;
        }
        .nav-links a {
          font-size: 14px;
          color: var(--ink-2);
          position: relative;
          padding: 4px 0;
          transition: color 200ms ease;
        }
        .nav-links a::after {
          content: "";
          position: absolute;
          left: 0; right: 0; bottom: 0;
          height: 1px;
          background: currentColor;
          transform: scaleX(0);
          transform-origin: left;
          transition: transform 240ms cubic-bezier(.2,.7,.2,1);
        }
        .nav-links a:hover { color: var(--ink); }
        .nav-links a:hover::after { transform: scaleX(1); }
        .nav-cta { border-radius: 4px; }
        @media (max-width: 760px) {
          .nav-cta { padding: 10px 16px; font-size: 13px; }
          .nav-tag { display: none; }
        }
      `}</style>
    </header>
  );
}

window.Nav = Nav;
