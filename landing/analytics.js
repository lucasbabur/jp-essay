(() => {
  const production = ['jpessay.com', 'www.jpessay.com'].includes(location.hostname);
  const local = ['localhost', '127.0.0.1', '::1', '[::1]'].includes(location.hostname);
  let localTest = false;
  if (local) {
    try {
      const option = new URLSearchParams(location.search).get('clarity');
      if (option === '1') sessionStorage.setItem('clarity_local_test', '1');
      if (option === '0') sessionStorage.removeItem('clarity_local_test');
      localTest = sessionStorage.getItem('clarity_local_test') === '1';
    } catch (_) {
      localTest = new URLSearchParams(location.search).get('clarity') === '1';
    }
  }
  if (!production && !localTest) return;

  window.clarity = window.clarity || function () {
    (window.clarity.q = window.clarity.q || []).push(arguments);
  };
  const script = document.createElement('script');
  script.async = true;
  script.src = 'https://www.clarity.ms/tag/z5y0yiji9u';
  document.head.appendChild(script);

  window.clarity('set', 'environment', production ? 'production' : 'local_test');
  window.clarity('set', 'page_type', location.pathname.endsWith('/sample.html') ? 'sample' : 'landing');

  // UTMs take priority. Keep the entry source while navigating within the site.
  const params = new URLSearchParams(location.search);
  const clean = value => (value || '').trim().toLowerCase().slice(0, 100);
  const normalizeSource = value => {
    const source = clean(value);
    const aliases = {
      'twitter': 'x', 'twitter.com': 'x', 'x.com': 'x', 't.co': 'x',
      'bsky': 'bluesky', 'bsky.app': 'bluesky', 'bsky.social': 'bluesky',
      'reddit.com': 'reddit', 'dev.to': 'devto', 'dev.to/': 'devto', 'dev': 'devto',
    };
    return aliases[source] || source;
  };
  let referrer = '';
  try { referrer = new URL(document.referrer).hostname.toLowerCase(); } catch (_) {}
  const fromDomain = domain => referrer === domain || referrer.endsWith('.' + domain);
  const internal = referrer === location.hostname ||
    (['jpessay.com', 'www.jpessay.com'].includes(referrer) && production);
  let source = '';
  if (fromDomain('reddit.com') || fromDomain('redd.it')) source = 'reddit';
  else if (fromDomain('x.com') || fromDomain('twitter.com') || fromDomain('t.co')) source = 'x';
  else if (fromDomain('bsky.app') || fromDomain('bsky.social')) source = 'bluesky';
  else if (fromDomain('dev.to')) source = 'devto';
  else if (/^(www\.)?google\.(com|[a-z]{2}|com\.[a-z]{2}|co\.[a-z]{2})$/.test(referrer)) source = 'google';

  let attribution;
  const utmSource = normalizeSource(params.get('utm_source'));
  if (utmSource || (referrer && !internal)) {
    source = utmSource || source || referrer;
    attribution = {
      source,
      medium: clean(params.get('utm_medium')) ||
        (utmSource ? 'unspecified' : source === 'google' ? 'organic' : ['reddit', 'x', 'bluesky'].includes(source) ? 'social' : 'referral'),
      campaign: clean(params.get('utm_campaign')),
      method: utmSource ? 'utm' : 'referrer',
      capturedAt: Date.now(),
    };
  }
  try {
    if (!attribution) {
      const saved = JSON.parse(sessionStorage.getItem('clarity_attribution'));
      if (saved && Date.now() - saved.capturedAt < 30 * 60 * 1000) attribution = saved;
    }
  } catch (_) {}
  attribution = attribution || { source: 'direct_or_unknown', medium: 'none', campaign: '', method: 'unknown' };
  attribution.capturedAt = Date.now();
  try { sessionStorage.setItem('clarity_attribution', JSON.stringify(attribution)); } catch (_) {}
  window.clarity('set', 'traffic_source', attribution.source);
  window.clarity('set', 'traffic_medium', attribution.medium);
  window.clarity('set', 'attribution_method', attribution.method);
  if (attribution.campaign) window.clarity('set', 'traffic_campaign', attribution.campaign);

  document.addEventListener('click', event => {
    const target = event.target.closest('a, [data-install]');
    if (!target) return;
    if (target.dataset.install) {
      window.clarity('set', 'install_method', target.dataset.install);
      window.clarity('event', 'install_method_selected');
    } else if (target.hostname === 'github.com') {
      window.clarity('event', 'github_click');
    } else if (target.pathname.endsWith('/sample.html')) {
      window.clarity('event', 'sample_open');
    } else if (target.hash === '#install') {
      window.clarity('event', 'install_cta_click');
    }
  });
})();
