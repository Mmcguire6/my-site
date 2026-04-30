/* global React */
const { useState: useStateSvc } = React;

function Services({ cardStyle }) {
  // cardStyle: 'list' | 'grid'
  const items = [
    {
      n: '01',
      title: 'Data Strategy & Roadmaps',
      blurb: 'Build a roadmap for data success aligned with your business goals — from current-state assessment to a multi-year delivery plan.',
      bullets: ['Maturity & gap assessment', 'Capability roadmaps', 'Investment cases'],
    },
    {
      n: '02',
      title: 'Data Platform Modernization',
      blurb: 'Modernize your data infrastructure for scale, performance, and agility. Migrate confidently from legacy stacks to cloud-native foundations.',
      bullets: ['Cloud migration', 'Architecture & integration', 'ERP / CRM interfaces'],
    },
    {
      n: '03',
      title: 'Analytics & BI Enablement',
      blurb: 'Turn raw data into insight with advanced analytics and intuitive dashboards your operators and executives will actually use.',
      bullets: ['Executive dashboards', 'Self-serve enablement', 'Embedded analytics'],
    },
    {
      n: '04',
      title: 'Data Governance & Quality',
      blurb: 'Ensure trusted, secure, and compliant data across your organization — with practical controls that don\u2019t slow delivery down.',
      bullets: ['Stewardship models', 'Quality monitoring', 'Compliance frameworks'],
    },
  ];

  return (
    <section id="services" className="section services tinted-section">
      <div className="wrap">
        <header className="services-head">
          <div>
            <span className="eyebrow">Our services</span>
            <h2 className="display h2 services-title reveal">
              End-to-end data solutions <em>built for impact.</em>
            </h2>
          </div>
          <p className="lede services-lede reveal">
            From strategy to implementation, we help you harness the power of your data — practically and with measurable results.
          </p>
        </header>

        {cardStyle === 'grid' ? (
          <div className="svc-grid reveal-stagger">
            {items.map(it => <ServiceCard key={it.n} {...it} />)}
          </div>
        ) : (
          <div className="svc-list">
            {items.map((it, i) => <ServiceRow key={it.n} {...it} index={i} />)}
          </div>
        )}
      </div>
      <style>{servicesStyles}</style>
    </section>
  );
}

function ServiceCard({ n, title, blurb, bullets }) {
  return (
    <article className="svc-card">
      <div className="svc-card-top">
        <span className="mono svc-card-n">{n}</span>
      </div>
      <h3 className="h3 svc-card-title">{title}</h3>
      <p className="body svc-card-blurb">{blurb}</p>
      <ul className="svc-card-bullets">
        {bullets.map(b => <li key={b}>{b}</li>)}
      </ul>
      <a href="#contact" className="svc-card-link">
        Learn more <span className="arrow">→</span>
      </a>
    </article>
  );
}

function ServiceRow({ n, title, blurb, bullets, index }) {
  const [open, setOpen] = useStateSvc(index === 0);
  return (
    <div className={`svc-row ${open ? 'open' : ''}`}>
      <button className="svc-row-head" onClick={() => setOpen(!open)} aria-expanded={open}>
        <span className="mono svc-row-n">{n}</span>
        <span className="svc-row-title">{title}</span>
        <span className="svc-row-toggle" aria-hidden="true">{open ? '–' : '+'}</span>
      </button>
      <div className="svc-row-body" aria-hidden={!open}>
        <div className="svc-row-body-inner">
          <p className="body svc-row-blurb">{blurb}</p>
          <ul className="svc-row-bullets">
            {bullets.map(b => <li key={b}>{b}</li>)}
          </ul>
          <a href="#contact" className="svc-card-link">
            Learn more <span className="arrow">→</span>
          </a>
        </div>
      </div>
    </div>
  );
}

const servicesStyles = `
  .services-head {
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    gap: 48px;
    align-items: end;
    padding-bottom: 56px;
  }
  .services-title { margin-top: 20px; }
  .services-lede { margin: 0; }

  /* GRID variant */
  .svc-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0;
    border-top: 1px solid var(--rule);
    border-left: 1px solid var(--rule);
  }
  .svc-card {
    padding: 36px 36px 32px;
    border-right: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    display: flex;
    flex-direction: column;
    background: var(--bg);
    transition: background 240ms ease;
    position: relative;
  }
  .svc-card:hover { background: var(--bg-2); }
  .svc-card::after {
    content: "";
    position: absolute;
    left: 0; right: 0; top: 0;
    height: 2px;
    background: var(--accent);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 320ms cubic-bezier(.2,.7,.2,1);
  }
  .svc-card:hover::after { transform: scaleX(1); }
  .svc-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28px;
  }
  .svc-card-n {
    font-size: 11px;
    letter-spacing: 0.1em;
    color: var(--ink-3);
  }
  .svc-card-title {
    margin: 0 0 12px;
    color: var(--ink);
  }
  .svc-card-blurb {
    margin: 0 0 24px;
    font-size: 14px;
    line-height: 1.6;
    max-width: 42ch;
  }
  .svc-card-bullets {
    list-style: none;
    margin: 0 0 28px;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .svc-card-bullets li {
    font-family: var(--mono);
    font-size: 12px;
    color: var(--ink-2);
    padding-left: 18px;
    position: relative;
  }
  .svc-card-bullets li::before {
    content: "";
    position: absolute;
    left: 0; top: 8px;
    width: 8px;
    height: 1px;
    background: var(--ink-3);
  }
  .svc-card-link {
    margin-top: auto;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 500;
    color: var(--ink);
    align-self: flex-start;
    padding-bottom: 4px;
    border-bottom: 1px solid var(--rule);
    transition: border-color 200ms ease, gap 200ms ease;
  }
  .svc-card-link:hover {
    border-bottom-color: var(--ink);
  }
  .svc-card-link:hover .arrow { transform: translateX(3px); }

  /* LIST variant */
  .svc-list { border-top: 1px solid var(--rule); }
  .svc-row { border-bottom: 1px solid var(--rule); }
  .svc-row-head {
    width: 100%;
    display: grid;
    grid-template-columns: 60px 1fr 32px;
    align-items: center;
    gap: 24px;
    padding: 28px 4px;
    text-align: left;
    transition: padding 240ms ease;
  }
  .svc-row-head:hover { padding-left: 12px; }
  .svc-row-n {
    font-size: 11px;
    letter-spacing: 0.1em;
    color: var(--ink-3);
  }
  .svc-row-title {
    font-family: var(--serif);
    font-size: clamp(24px, 2.8vw, 36px);
    letter-spacing: -0.01em;
    line-height: 1.1;
    color: var(--ink);
  }
  .svc-row-toggle {
    font-family: var(--serif);
    font-size: 28px;
    color: var(--ink-3);
    text-align: center;
    transition: color 200ms ease, transform 200ms ease;
  }
  .svc-row.open .svc-row-toggle { color: var(--ink); transform: rotate(180deg); }
  .svc-row-body {
    display: grid;
    grid-template-rows: 0fr;
    transition: grid-template-rows 360ms cubic-bezier(.2,.7,.2,1);
  }
  .svc-row.open .svc-row-body { grid-template-rows: 1fr; }
  .svc-row-body-inner {
    overflow: hidden;
    display: grid;
    grid-template-columns: 60px 1.2fr 1fr 32px;
    gap: 24px;
    padding-bottom: 0;
    transition: padding-bottom 360ms cubic-bezier(.2,.7,.2,1);
  }
  .svc-row.open .svc-row-body-inner { padding-bottom: 32px; }
  .svc-row-body-inner > :first-child { grid-column: 2; }
  .svc-row-blurb { margin: 0; max-width: 50ch; font-size: 15px; }
  .svc-row-bullets {
    grid-column: 3;
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .svc-row-bullets li {
    font-family: var(--mono);
    font-size: 12px;
    color: var(--ink-2);
    padding-left: 18px;
    position: relative;
  }
  .svc-row-bullets li::before {
    content: "";
    position: absolute;
    left: 0; top: 8px;
    width: 8px;
    height: 1px;
    background: var(--ink-3);
  }
  .svc-row .svc-card-link {
    grid-column: 2 / 4;
    margin-top: 8px;
  }

  @media (max-width: 880px) {
    .services-head { grid-template-columns: 1fr; gap: 24px; align-items: start; }
    .svc-grid { grid-template-columns: 1fr; }
    .svc-row-head { grid-template-columns: 40px 1fr 24px; gap: 16px; }
    .svc-row-body-inner { grid-template-columns: 1fr; }
    .svc-row-body-inner > :first-child,
    .svc-row-bullets,
    .svc-row .svc-card-link { grid-column: 1; }
  }
`;

window.Services = Services;
