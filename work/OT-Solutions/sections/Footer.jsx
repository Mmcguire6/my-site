/* global React */
function Footer() {
  return (
    <footer className="footer">
      <div className="wrap">
        <div className="footer-top">
          <div className="footer-brand">
            <div className="footer-mark" aria-hidden="true">
              <img className="logo-light" src="assets/logo-mark-navy.png" alt="" />
              <img className="logo-dark" src="assets/logo-mark-accent.png" alt="" />
            </div>
            <div className="footer-name">OT Solutions</div>
            <p className="footer-blurb">
              A data consulting firm helping organizations modernize, analyze, and activate their data to drive business transformation.
            </p>
          </div>

          <div className="footer-cols">
            <div className="footer-col">
              <h4 className="footer-col-h">Services</h4>
              <ul>
                <li><a href="#services">Data Strategy &amp; Roadmaps</a></li>
                <li><a href="#services">Platform Modernization</a></li>
                <li><a href="#services">Analytics &amp; BI</a></li>
                <li><a href="#services">Governance &amp; Quality</a></li>
                <li><a href="#services">Managed Services</a></li>
              </ul>
            </div>
            <div className="footer-col">
              <h4 className="footer-col-h">Company</h4>
              <ul>
                <li><a href="#why">About</a></li>
                <li><a href="#testimonials">References</a></li>
                <li><a href="#contact">Contact</a></li>
              </ul>
            </div>
            <div className="footer-col">
              <h4 className="footer-col-h">Contact</h4>
              <ul>
                <li><a href="tel:7809740124">+1 (780) 974&ndash;0124</a></li>
                <li><a href="mailto:OTSolutions@shaw.ca">OTSolutions@shaw.ca</a></li>
                <li className="muted">Sherwood Park, AB · Canada</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <span className="mono">© 2026 OT Solutions Inc. — All rights reserved.</span>
          <div className="footer-legal">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
          </div>
        </div>
      </div>
      <style>{`
        .footer {
          padding: clamp(64px, 8vw, 96px) 0 32px;
          border-top: 1px solid var(--rule);
        }
        .footer-top {
          display: grid;
          grid-template-columns: 1.1fr 2fr;
          gap: clamp(40px, 5vw, 80px);
          padding-bottom: 56px;
        }
        .footer-mark { color: var(--ink); margin-bottom: 16px; }
        .footer-mark img { width: 42px; height: 42px; display: block; object-fit: contain; }
        .footer-mark .logo-dark { display: none; }
        [data-theme="dark"] .footer-mark .logo-light { display: none; }
        [data-theme="dark"] .footer-mark .logo-dark { display: block; }
        .footer-name {
          font-family: var(--serif);
          font-size: 28px;
          letter-spacing: -0.01em;
          color: var(--ink);
          margin-bottom: 12px;
        }
        .footer-blurb {
          font-size: 14px;
          line-height: 1.55;
          color: var(--ink-3);
          margin: 0;
          max-width: 38ch;
        }
        .footer-cols {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 32px;
        }
        .footer-col-h {
          font-size: 11px;
          font-weight: 500;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: var(--ink-3);
          margin: 0 0 18px;
          font-family: var(--mono);
        }
        .footer-col ul {
          list-style: none;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .footer-col li { font-size: 14px; }
        .footer-col a {
          color: var(--ink-2);
          transition: color 200ms ease;
        }
        .footer-col a:hover { color: var(--ink); }

        .footer-bottom {
          padding-top: 24px;
          border-top: 1px solid var(--rule);
          display: flex;
          justify-content: space-between;
          gap: 16px;
          flex-wrap: wrap;
          font-size: 11px;
          letter-spacing: 0.04em;
          color: var(--ink-3);
        }
        .footer-legal { display: flex; gap: 24px; }
        .footer-legal a { color: var(--ink-3); transition: color 200ms ease; }
        .footer-legal a:hover { color: var(--ink); }

        @media (max-width: 880px) {
          .footer-top { grid-template-columns: 1fr; }
          .footer-cols { grid-template-columns: repeat(2, 1fr); }
        }
      `}</style>
    </footer>
  );
}
window.Footer = Footer;
