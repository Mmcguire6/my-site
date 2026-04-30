/* global React */
function TrackRecord() {
  const items = [
    {
      n: '01',
      kicker: 'Enterprise Delivery',
      title: 'Multimillion-dollar projects, delivered.',
      body: 'Supported enterprise initiatives at APS with reduced timelines and budgets — consistently exceeding executive expectations.',
      stat: '$M+',
      statLabel: 'in delivered initiatives',
    },
    {
      n: '02',
      kicker: 'Systems Integration',
      title: 'ERP & CRM integration experience.',
      body: 'Delivered interface and support work across SAP, Microsoft, and other industry-specific business systems for global manufacturers.',
      stat: 'SAP',
      statLabel: 'Microsoft · industry stacks',
    },
    {
      n: '03',
      kicker: 'Long-Tenured Expertise',
      title: '25+ years of trusted consulting.',
      body: 'Long-running data and systems expertise across industrial, manufacturing, and workforce environments — since 2000.',
      stat: '25+',
      statLabel: 'years, since 2000',
    },
  ];
  return (
    <section className="section track">
      <div className="wrap">
        <header className="track-head">
          <span className="eyebrow">Proven track record</span>
          <h2 className="display h2 track-title reveal">
            Proven across complex<br />
            <em>enterprise environments.</em>
          </h2>
          <p className="lede track-lede reveal">
            Senior consultants delivering measurable results on the systems large organizations rely on every day.
          </p>
        </header>

        <ol className="track-list reveal-stagger">
          {items.map(it => (
            <li className="track-item" key={it.n}>
              <div className="track-item-meta">
                <span className="mono track-item-n">{it.n}</span>
                <span className="mono track-item-kicker">{it.kicker}</span>
              </div>
              <div className="track-item-body">
                <h3 className="display track-item-title">{it.title}</h3>
                <p className="body track-item-blurb">{it.body}</p>
              </div>
              <div className="track-item-stat">
                <div className="track-item-stat-num">{it.stat}</div>
                <div className="mono track-item-stat-label">{it.statLabel}</div>
              </div>
            </li>
          ))}
        </ol>
      </div>
      <style>{`
        .track-head {
          display: grid;
          grid-template-columns: 1.4fr 1fr;
          column-gap: 48px;
          row-gap: 24px;
          padding-bottom: 64px;
        }
        .track-head .eyebrow { grid-column: 1 / -1; }
        .track-title { margin: 0; }
        .track-lede { margin: 0; align-self: end; }

        .track-list {
          list-style: none;
          margin: 0;
          padding: 0;
          border-top: 1px solid var(--rule);
        }
        .track-item {
          display: grid;
          grid-template-columns: 220px 1fr 240px;
          gap: 48px;
          padding: 40px 0;
          border-bottom: 1px solid var(--rule);
          align-items: start;
          position: relative;
          transition: background 200ms ease;
        }
        .track-item:hover { background: var(--bg-2); }
        .track-item-meta {
          display: flex;
          flex-direction: column;
          gap: 8px;
          padding-top: 8px;
        }
        .track-item-n {
          font-size: 11px;
          letter-spacing: 0.1em;
          color: var(--ink-3);
        }
        .track-item-kicker {
          font-size: 12px;
          letter-spacing: 0.06em;
          color: var(--ink);
          text-transform: uppercase;
        }
        .track-item-title {
          font-family: var(--serif);
          font-size: clamp(24px, 2.6vw, 34px);
          line-height: 1.15;
          letter-spacing: -0.01em;
          margin: 0 0 14px;
          color: var(--ink);
          font-weight: 400;
        }
        .track-item-blurb {
          margin: 0;
          font-size: 15px;
          line-height: 1.6;
          max-width: 56ch;
        }
        .track-item-stat {
          text-align: right;
          padding-top: 8px;
        }
        .track-item-stat-num {
          font-family: var(--serif);
          font-size: clamp(48px, 5vw, 72px);
          line-height: 1;
          letter-spacing: -0.02em;
          color: var(--ink);
        }
        .track-item-stat-label {
          margin-top: 8px;
          font-size: 11px;
          letter-spacing: 0.06em;
          text-transform: uppercase;
          color: var(--ink-3);
        }
        @media (max-width: 980px) {
          .track-head { grid-template-columns: 1fr; }
          .track-item { grid-template-columns: 1fr; gap: 16px; }
          .track-item-stat { text-align: left; }
        }
      `}</style>
    </section>
  );
}
window.TrackRecord = TrackRecord;
