/* global React */
function CTA() {
  return (
    <section id="contact" className="cta">
      <div className="wrap">
        <div className="cta-inner">
          <div className="cta-text reveal">
            <span className="eyebrow no-rule cta-eyebrow">Connect with us</span>
            <h2 className="display cta-title">
              Ready to unlock the<br />
              power of your <em>data?</em>
            </h2>
            <p className="cta-lede">
              Let&rsquo;s build smarter solutions and drive meaningful results — together.
            </p>
            <div className="cta-actions">
              <a href="#contact" className="btn btn-primary cta-btn-primary">
                Contact us <span className="arrow">→</span>
              </a>
            </div>
          </div>

          <aside className="cta-meta">
            <div className="cta-meta-row">
              <span className="mono cta-meta-key">Office</span>
              <span className="cta-meta-val">Sherwood Park,<br />Alberta · Canada</span>
            </div>
            <div className="cta-meta-row">
              <span className="mono cta-meta-key">Practice</span>
              <span className="cta-meta-val">Enterprise data &<br />workforce systems</span>
            </div>
            <div className="cta-meta-row">
              <span className="mono cta-meta-key">Since</span>
              <span className="cta-meta-val">2000<br />(25+ years)</span>
            </div>
          </aside>
        </div>
      </div>
      <style>{`
        .cta {
          background: var(--navy-3);
          color: oklch(0.97 0.008 250);
          padding: clamp(80px, 10vw, 140px) 0;
          position: relative;
          overflow: hidden;
          --gold: oklch(0.82 0.13 78);
          --gold-rule: oklch(0.68 0.11 78);
        }
        .cta::before {
          content: "";
          position: absolute;
          inset: 0;
          background:
            radial-gradient(ellipse at 85% 0%, oklch(0.32 0.09 245 / 0.5) 0%, transparent 55%),
            radial-gradient(ellipse at 0% 100%, oklch(0.22 0.07 258 / 0.6) 0%, transparent 60%);
          pointer-events: none;
        }
        .cta .wrap { position: relative; }
        [data-theme="dark"] .cta {
          background: var(--navy-3);
          color: var(--ink);
          border-top: 1px solid var(--rule);
          border-bottom: 1px solid var(--rule);
        }
        .cta-inner {
          display: grid;
          grid-template-columns: 1.4fr 1fr;
          gap: clamp(40px, 6vw, 96px);
          align-items: end;
        }
        .cta-eyebrow { color: var(--gold); margin-bottom: 24px; }
        .cta-eyebrow::before { background: var(--gold-rule); }
        .cta-title {
          font-family: var(--serif);
          font-size: clamp(48px, 6vw, 88px);
          line-height: 1.02;
          letter-spacing: -0.02em;
          margin: 0 0 24px;
          font-weight: 400;
          color: inherit;
          text-wrap: pretty;
        }
        .cta-title em {
          font-style: italic;
          color: var(--accent);
        }
        .cta-lede {
          font-size: clamp(17px, 1.3vw, 19px);
          line-height: 1.5;
          color: oklch(0.86 0.02 250);
          max-width: 50ch;
          margin: 0 0 36px;
        }
        .cta-actions { display: flex; gap: 12px; flex-wrap: wrap; }
        .cta .btn { border-radius: 4px; }
        .cta-btn-primary {
          background: var(--bg);
          color: var(--ink);
        }
        .cta-btn-primary:hover {
          background: var(--accent);
          color: var(--ink);
          box-shadow: 0 8px 24px -8px oklch(0.72 0.13 70 / 0.5);
        }
        .cta-btn-ghost {
          color: var(--bg);
          border-color: oklch(1 0 0 / 0.2);
        }
        [data-theme="dark"] .cta-btn-ghost {
          color: var(--ink);
          border-color: var(--rule);
        }
        .cta-btn-ghost:hover {
          border-color: var(--bg);
          background: oklch(1 0 0 / 0.05);
        }
        [data-theme="dark"] .cta-btn-ghost:hover {
          border-color: var(--ink);
          background: var(--bg-2);
        }

        .cta-meta {
          display: flex;
          flex-direction: column;
          gap: 24px;
          padding-left: clamp(24px, 3vw, 48px);
          border-left: 1px solid oklch(1 0 0 / 0.15);
        }
        [data-theme="dark"] .cta-meta { border-left-color: var(--rule); }
        .cta-meta-row {
          display: grid;
          grid-template-columns: 80px 1fr;
          gap: 16px;
          font-size: 14px;
          line-height: 1.4;
        }
        .cta-meta-key {
          font-size: 10px;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: oklch(0.66 0.03 250);
          padding-top: 4px;
        }
        .cta-meta-val { color: inherit; }

        @media (max-width: 880px) {
          .cta-inner { grid-template-columns: 1fr; }
          .cta-meta { padding-left: 0; border-left: 0; padding-top: 24px; border-top: 1px solid oklch(1 0 0 / 0.15); }
        }
      `}</style>
    </section>
  );
}
window.CTA = CTA;
