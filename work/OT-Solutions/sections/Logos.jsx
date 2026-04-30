/* global React */
function Logos() {
  const clients = [
    { name: 'APS', meta: 'Enterprise delivery' },
    { name: 'DKS Data', meta: 'Strategic partnership' },
    { name: 'Lehigh Cement', meta: 'ERP & CRM systems' },
    { name: 'Lehigh Inland', meta: 'Industrial systems' },
    { name: 'UKG / Workforce Central', meta: '25+ years' },
  ];
  return (
    <section className="logos">
      <div className="wrap">
        <div className="logos-row">
          <div className="logos-label">
            <span className="eyebrow no-rule">Trusted by</span>
            <p className="logos-blurb">Senior consultants delivering on the systems large organizations rely on every day.</p>
          </div>
          <div className="logos-list reveal-stagger">
            {clients.map(c => (
              <div className="logo-card" key={c.name}>
                <div className="logo-name">{c.name}</div>
                <div className="logo-meta mono">{c.meta}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <style>{`
        .logos {
          padding: clamp(48px, 7vw, 88px) 0;
          border-top: 1px solid var(--rule);
        }
        .logos-row {
          display: grid;
          grid-template-columns: 280px 1fr;
          gap: 48px;
          align-items: start;
        }
        .logos-label .eyebrow { margin-bottom: 16px; }
        .logos-blurb {
          font-size: 14px;
          color: var(--ink-3);
          line-height: 1.5;
          margin: 0;
          max-width: 24ch;
        }
        .logos-list {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          border-left: 1px solid var(--rule);
        }
        .logo-card {
          padding: 8px 20px;
          border-right: 1px solid var(--rule);
          min-height: 88px;
          display: flex;
          flex-direction: column;
          justify-content: center;
          transition: background 200ms ease;
        }
        .logo-card:hover { background: var(--bg-2); }
        .logo-name {
          font-family: var(--serif);
          font-size: 22px;
          line-height: 1.1;
          letter-spacing: -0.01em;
          color: var(--ink);
        }
        .logo-meta {
          margin-top: 8px;
          font-size: 10px;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: var(--ink-3);
        }
        @media (max-width: 980px) {
          .logos-row { grid-template-columns: 1fr; gap: 24px; }
          .logos-list { grid-template-columns: repeat(2, 1fr); border-left: 0; border-top: 1px solid var(--rule); }
          .logo-card { border-right: 1px solid var(--rule); border-bottom: 1px solid var(--rule); }
        }
      `}</style>
    </section>
  );
}
window.Logos = Logos;
