(() => {
  // Keep local previews and Vercel preview deployments out of production data.
  if (!['jpessay.com', 'www.jpessay.com'].includes(location.hostname)) return;

  window.clarity = window.clarity || function () {
    (window.clarity.q = window.clarity.q || []).push(arguments);
  };
  const script = document.createElement('script');
  script.async = true;
  script.src = 'https://www.clarity.ms/tag/z5y0yiji9u';
  document.head.appendChild(script);

  window.clarity('set', 'page_type', location.pathname.endsWith('/sample.html') ? 'sample' : 'landing');
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
