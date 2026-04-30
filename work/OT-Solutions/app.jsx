/* global React, ReactDOM, useTweaks, TweaksPanel, TweakSection, TweakRadio, TweakToggle, TweakColor */
const { useEffect: useEffectApp, useRef: useRefApp } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "light",
  "heroVariant": "split",
  "serviceCardStyle": "list",
  "accent": "#3D7DC4"
}/*EDITMODE-END*/;

function applyAccent(hex) {
  // Allow tweaking the accent live by overriding the --accent var
  document.documentElement.style.setProperty('--accent', hex);
}

function App() {
  const [tweaks, setTweak] = useTweaks(TWEAK_DEFAULTS);

  // Apply theme + accent to root
  useEffectApp(() => {
    document.documentElement.dataset.theme = tweaks.theme;
  }, [tweaks.theme]);
  useEffectApp(() => {
    applyAccent(tweaks.accent);
  }, [tweaks.accent]);

  // Reveal-on-scroll observer
  useEffectApp(() => {
    const els = document.querySelectorAll('.reveal, .reveal-stagger');
    if (!('IntersectionObserver' in window)) {
      els.forEach(el => el.classList.add('in'));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    els.forEach(el => io.observe(el));
    return () => io.disconnect();
  }, [tweaks.heroVariant, tweaks.serviceCardStyle]);

  return (
    <>
      <Nav />
      <main>
        <Hero heroVariant={tweaks.heroVariant} />
        <Logos />
        <Services cardStyle={tweaks.serviceCardStyle} />
        <WhyUs />
        <TrackRecord />
        <Testimonials />
        <CTA />
      </main>
      <Footer />

      <TweaksPanel title="Tweaks">
        <TweakSection label="Theme" />
        <TweakRadio
          label="Mode"
          value={tweaks.theme}
          options={[
            { value: 'light', label: 'Light' },
            { value: 'dark', label: 'Dark' },
          ]}
          onChange={(v) => setTweak('theme', v)}
        />
        <TweakColor
          label="Accent"
          value={tweaks.accent}
          onChange={(v) => setTweak('accent', v)}
        />

        <TweakSection label="Hero" />
        <TweakRadio
          label="Layout"
          value={tweaks.heroVariant}
          options={[
            { value: 'split', label: 'Split' },
            { value: 'editorial', label: 'Editorial' },
            { value: 'centered', label: 'Centered' },
          ]}
          onChange={(v) => setTweak('heroVariant', v)}
        />

        <TweakSection label="Services" />
        <TweakRadio
          label="Style"
          value={tweaks.serviceCardStyle}
          options={[
            { value: 'list', label: 'List' },
            { value: 'grid', label: 'Grid' },
          ]}
          onChange={(v) => setTweak('serviceCardStyle', v)}
        />
      </TweaksPanel>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
