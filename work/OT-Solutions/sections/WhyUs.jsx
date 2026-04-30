/* global React */
function WhyUs() {
  const points = [
    {
      label: 'Proven Expertise',
      body: 'Certified data professionals with deep industry and technical knowledge across enterprise stacks.',
    },
    {
      label: 'Client-Centric',
      body: 'We listen, collaborate, and deliver solutions tailored to how your business actually operates.',
    },
    {
      label: 'Outcome-Focused',
      body: 'Practical solutions designed to improve reporting, operations, and the decisions you make every day.',
    },
  ];
  return (
    <section id="why" className="section why dark-section">
      <div className="wrap">
        <div className="why-grid">
          <div className="why-left">
            <span className="eyebrow">Why OT Solutions</span>
            <h2 className="display h2 why-title reveal">
              Deep expertise.<br />
              A <em>client-first</em> approach.
            </h2>
            <p className="lede why-lede reveal">
              Our team brings decades of experience delivering complex data solutions that drive real business value — quietly, on time, and on budget.
            </p>

            <ul className="why-points reveal-stagger">
              {points.map((p, i) => (
                <li key={p.label} className="why-point">
                  <span className="mono why-point-num">0{i + 1}</span>
                  <div>
                    <div className="why-point-label">{p.label}</div>
                    <p className="body why-point-body">{p.body}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="why-right">
            <div className="why-image reveal">
              <img src="assets/why-ot.jpg" alt="OT Solutions team meeting in a glass-walled boardroom overlooking the city" />
            </div>
            <div className="why-caption mono">
              <span>Fig. 01</span>
              <span>OT Solutions consultants in session.</span>
            </div>
          </div>
        </div>
      </div>
      <style>{`
        .why-grid {
          display: grid;
          grid-template-columns: 1.05fr 1fr;
          gap: clamp(40px, 6vw, 96px);
          align-items: start;
        }
        .why-title { margin: 20px 0 24px; }
          .why-lede { margin: 32px 0 56px; }
        .why-points {
          list-style: none;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: column;
          border-top: 1px solid var(--rule);
        }
        .why-point {
          display: grid;
          grid-template-columns: 64px 1fr;
          gap: 24px;
          padding: 28px 0;
          border-bottom: 1px solid var(--rule);
        }
        .why-point-num {
          font-size: 11px;
          letter-spacing: 0.1em;
          color: var(--ink-3);
          padding-top: 4px;
        }
        .why-point-label {
          font-size: 16px;
          font-weight: 500;
          letter-spacing: -0.01em;
          color: var(--ink);
          margin-bottom: 6px;
        }
        .why-point-body {
          margin: 0;
          font-size: 14px;
          line-height: 1.6;
          max-width: 48ch;
        }
        .why-right { position: sticky; top: 100px; }
        .why-image {
          aspect-ratio: 4 / 5;
          width: 100%;
          overflow: hidden;
          background: var(--bg-3);
          border: 1px solid var(--rule);
        }
        .why-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
        }
        .why-caption {
          display: flex;
          gap: 24px;
          margin-top: 16px;
          font-size: 11px;
          letter-spacing: 0.06em;
          text-transform: uppercase;
          color: var(--ink-3);
        }
        @media (max-width: 880px) {
          .why-grid { grid-template-columns: 1fr; }
          .why-right { position: static; }
        }
      `}</style>
    </section>
  );
}
window.WhyUs = WhyUs;
