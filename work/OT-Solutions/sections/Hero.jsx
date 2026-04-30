/* global React */
function Hero({ heroVariant }) {
  // heroVariant: 'split' | 'editorial' | 'centered'

  if (heroVariant === 'centered') {
    return (
      <section id="top" className="hero hero-centered">
        <div className="hero-c-bg" aria-hidden="true">
          <img src="assets/hero.jpg" alt="" />
          <div className="hero-c-bg-veil" />
        </div>
        <div className="wrap">
          <div className="hero-c-inner reveal">
            <span className="eyebrow no-rule">Est. 2000 · Sherwood Park, AB</span>
            <h1 className="display h1 hero-c-title">
              Smarter data.<br />
              Stronger <em>decisions.</em>
            </h1>
            <p className="lede hero-c-lede">
              We help organizations modernize their data infrastructure, unlock insights, and drive measurable business outcomes.
            </p>
            <div className="hero-c-actions">
              <a href="#services" className="btn btn-primary">Our services <span className="arrow">→</span></a>
              <a href="#contact" className="btn btn-ghost">Connect with us</a>
            </div>
          </div>
          <HeroMeta />
        </div>
        <style>{heroStyles}</style>
      </section>
    );
  }

  if (heroVariant === 'editorial') {
    return (
      <section id="top" className="hero hero-editorial">
        <div className="wrap">
          <div className="hero-e-grid">
            <div className="hero-e-left reveal">
              <span className="eyebrow">A data consultancy</span>
              <h1 className="display h1 hero-e-title">
                Smarter data.<br />
                Stronger <em>decisions.</em>
              </h1>
            </div>
            <div className="hero-e-right reveal">
              <p className="lede">
                OT Solutions modernizes data infrastructure for the systems large enterprises rely on every day — quietly, for twenty-five years.
              </p>
              <div className="hero-e-actions">
                <a href="#services" className="btn btn-primary">Our services <span className="arrow">→</span></a>
                <a href="#contact" className="btn btn-ghost">Connect</a>
              </div>
            </div>
          </div>
          <div className="hero-e-image reveal">
            <img src="assets/hero.jpg" alt="Skyline view from a corporate office at sunset" />
          </div>
          <HeroMeta />
        </div>
        <style>{heroStyles}</style>
      </section>
    );
  }

  // default: split — full-bleed hero image with text overlay on left
  return (
    <section id="top" className="hero hero-split">
      <div className="hero-s-bg" aria-hidden="true">
        <img src="assets/hero.jpg" alt="" />
        <div className="hero-s-veil" />
      </div>
      <div className="wrap hero-s-wrap">
        <div className="hero-s-text reveal">
          <span className="eyebrow">A data consultancy · since 2000</span>
          <h1 className="display h1 hero-s-title">
            Smarter data.<br />
            Stronger <em>decisions.</em>
          </h1>
          <p className="lede hero-s-lede">
            OT Solutions helps organizations modernize their data infrastructure, unlock insights, and drive measurable business outcomes.
          </p>
          <div className="hero-s-actions">
            <a href="#services" className="btn btn-primary">Our services <span className="arrow">→</span></a>
            <a href="#contact" className="btn btn-ghost hero-s-ghost">Connect with us</a>
          </div>
        </div>
      </div>
      <style>{heroStyles}</style>
    </section>
  );
}

function HeroMeta() {
  return (
    <div className="hero-meta">
      <div className="hero-meta-row mono">
        <span>HQ — Sherwood Park, AB</span>
        <span className="hide-sm">·</span>
        <span className="hide-sm">Enterprise data &amp; workforce systems</span>
      </div>
    </div>
  );
}

const heroStyles = `
  .hero {
    padding-top: clamp(48px, 8vw, 96px);
    padding-bottom: clamp(48px, 8vw, 96px);
  }

  /* Hero CTA buttons — more rectangular */
  .hero .btn { border-radius: 4px; }

  /* SPLIT — full-bleed image with overlay text */
  .hero-split {
    position: relative;
    overflow: hidden;
    padding-top: 0;
    padding-bottom: 0;
    margin-top: -1px;
  }
  .hero-s-bg { position: absolute; inset: 0; z-index: 0; }
  .hero-s-bg img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
  .hero-s-veil {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      to right,
      color-mix(in oklch, var(--bg) 92%, transparent) 0%,
      color-mix(in oklch, var(--bg) 78%, transparent) 28%,
      color-mix(in oklch, var(--bg) 30%, transparent) 55%,
      transparent 80%
    );
  }
  [data-theme="dark"] .hero-s-veil {
    background: linear-gradient(
      to right,
      color-mix(in oklch, var(--bg) 90%, transparent) 0%,
      color-mix(in oklch, var(--bg) 70%, transparent) 30%,
      color-mix(in oklch, var(--bg) 25%, transparent) 60%,
      transparent 85%
    );
  }
  .hero-s-wrap {
    position: relative;
    z-index: 1;
    min-height: clamp(520px, 72vh, 760px);
    display: flex;
    align-items: center;
    padding-top: clamp(48px, 8vw, 96px);
    padding-bottom: clamp(48px, 8vw, 96px);
  }
  .hero-s-text { max-width: 56ch; }
  .hero-s-title { margin: 24px 0 24px; }
  .hero-s-lede { margin: 0 0 32px; max-width: 50ch; }
  .hero-s-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
  .hero-s-ghost {
    background: color-mix(in oklch, var(--bg) 70%, transparent);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
  }
  .hero-s-meta-wrap {
    position: relative;
    z-index: 1;
    background: var(--bg);
    border-top: 1px solid var(--rule);
  }
  .hero-s-meta-wrap .hero-meta {
    margin-top: 0;
    border-top: 0;
    padding-top: 24px;
    padding-bottom: 24px;
  }

  /* CENTERED */
  .hero-centered { position: relative; overflow: hidden; }
  .hero-c-bg {
    position: absolute;
    inset: 0;
    z-index: 0;
  }
  .hero-c-bg img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.22;
    filter: saturate(0.7);
  }
  [data-theme="dark"] .hero-c-bg img { opacity: 0.35; }
  .hero-c-bg-veil {
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom,
      color-mix(in oklch, var(--bg) 55%, transparent) 0%,
      var(--bg) 85%);
  }
  .hero-centered .wrap { position: relative; z-index: 1; }
  .hero-c-inner {
    text-align: center;
    max-width: 1000px;
    margin: 0 auto;
    padding: clamp(24px, 5vw, 80px) 0 64px;
  }
  .hero-c-title { margin: 28px 0 28px; }
  .hero-c-lede { margin: 0 auto; }
  .hero-c-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-top: 36px;
    flex-wrap: wrap;
  }

  /* EDITORIAL */
  .hero-e-grid {
    display: grid;
    grid-template-columns: 1.3fr 1fr;
    gap: clamp(32px, 5vw, 64px);
    align-items: end;
    padding: 32px 0 48px;
  }
  .hero-e-title { margin: 20px 0 0; }
  .hero-e-right .lede { margin-bottom: 24px; }
  .hero-e-actions { display: flex; gap: 12px; flex-wrap: wrap; }
  .hero-e-image {
    aspect-ratio: 21 / 9;
    width: 100%;
    margin-top: 16px;
    overflow: hidden;
    background: var(--bg-3);
  }
  .hero-e-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }

  /* META */
  .hero-meta {
    margin-top: 64px;
    padding-top: 24px;
    border-top: 1px solid var(--rule);
  }
  .hero-meta-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--ink-3);
  }

  @media (max-width: 880px) {
    .hero-e-grid { grid-template-columns: 1fr; align-items: stretch; }
    .hero-s-veil {
      background: linear-gradient(to bottom,
        color-mix(in oklch, var(--bg) 30%, transparent) 0%,
        color-mix(in oklch, var(--bg) 88%, transparent) 100%);
    }
    .hero-s-wrap { min-height: 560px; }
  }
`;

window.Hero = Hero;
