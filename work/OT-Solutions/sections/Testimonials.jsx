/* global React */
function Testimonials() {
  const quotes = [
    {
      quote: "OT Solutions contractors are exceptional in their ability to think outside the box and complete tasks others would find impossible. Their technical skills are second to none. They helped me take a number of multimillion-dollar projects at APS to places the executive never expected. With their help I over-delivered while reducing timelines and budget significantly — they made me look very good.",
      name: 'David Dickson',
      role: 'DKS Data',
      context: 'on enterprise delivery at APS',
    },
    {
      quote: "OT Solutions contractors provided design, development, and ongoing support for a variety of business system interfaces and user interfaces for ERP and CRM systems. The technical platform was predominantly Microsoft, with business system solutions from SAP and other industry-specific software. In short, I could not be happier to endorse and recommend OT Solutions for I.T. development solutions.",
      name: 'Sherryl O\u2019Connor',
      role: 'Lehigh Inland',
      context: 'on ERP & CRM delivery at Lehigh Cement',
    },
  ];
  return (
    <section id="testimonials" className="section testimonials">
      <div className="wrap">
        <header className="t-head">
          <span className="eyebrow">Client endorsements</span>
          <h2 className="display h2 t-title reveal">
            In their <em>own words.</em>
          </h2>
          <p className="lede t-lede reveal">
            Senior leaders who&rsquo;ve worked alongside our consultants on multimillion-dollar enterprise initiatives.
          </p>
        </header>

        <div className="t-grid reveal-stagger">
          {quotes.map((q, i) => (
            <figure className="t-card" key={i}>
              <span className="t-mark" aria-hidden="true">&ldquo;</span>
              <blockquote className="t-quote">{q.quote}</blockquote>
              <figcaption className="t-cap">
                <div className="t-cap-name">{q.name}</div>
                <div className="t-cap-meta mono">{q.role} &middot; {q.context}</div>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
      <style>{`
        .t-head {
          display: grid;
          grid-template-columns: 1.4fr 1fr;
          column-gap: 48px;
          row-gap: 20px;
          padding-bottom: 56px;
        }
        .t-head .eyebrow { grid-column: 1 / -1; }
        .t-title { margin: 0; }
        .t-lede { margin: 0; align-self: end; }

        .t-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 24px;
        }
        .t-card {
          margin: 0;
          padding: 48px 40px 36px;
          background: var(--bg-2);
          border: 1px solid var(--rule);
          position: relative;
          display: flex;
          flex-direction: column;
          gap: 28px;
          transition: transform 320ms cubic-bezier(.2,.7,.2,1), box-shadow 320ms ease;
        }
        .t-card:hover {
          transform: translateY(-3px);
          box-shadow: 0 24px 48px -28px oklch(0.18 0.04 250 / 0.25);
        }
        .t-mark {
          position: absolute;
          top: 24px;
          left: 32px;
          font-family: var(--serif);
          font-size: 96px;
          line-height: 1;
          color: var(--accent);
          opacity: 0.5;
        }
        .t-quote {
          font-family: var(--serif);
          font-size: clamp(18px, 1.6vw, 22px);
          line-height: 1.5;
          letter-spacing: -0.005em;
          margin: 0;
          color: var(--ink);
          padding-top: 36px;
          text-wrap: pretty;
        }
        .t-cap {
          padding-top: 24px;
          border-top: 1px solid var(--rule);
        }
        .t-cap-name {
          font-size: 14px;
          font-weight: 500;
          color: var(--ink);
          margin-bottom: 6px;
        }
        .t-cap-meta {
          font-size: 11px;
          letter-spacing: 0.06em;
          text-transform: uppercase;
          color: var(--ink-3);
        }
        @media (max-width: 880px) {
          .t-head { grid-template-columns: 1fr; }
          .t-grid { grid-template-columns: 1fr; }
        }
      `}</style>
    </section>
  );
}
window.Testimonials = Testimonials;
