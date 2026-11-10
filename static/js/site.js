/* ==========================================================================
   Shared site script — header, footer, scroll reveals.
   Edit NAV / SOCIALS here once and every page updates.
   ========================================================================== */
(function () {
  const NAV = [
    { href: 'index.html', label: 'Home', key: 'home' },
    { href: 'portfolio.html', label: 'Portfolio', key: 'portfolio' },
    { href: 'blog.html', label: 'Blog', key: 'blog' },
    { href: 'book.html', label: 'Read', key: 'read' },
  ];

  const SOCIALS = [
    { href: 'https://github.com/TalhaMahamud', icon: 'fab fa-github', label: 'GitHub' },
    { href: 'https://www.linkedin.com/in/talhamahamud/', icon: 'fab fa-linkedin-in', label: 'LinkedIn' },
    { href: 'https://orcid.org/0009-0002-7103-8420', icon: 'fab fa-orcid', label: 'ORCID' },
    { href: 'https://scholar.google.com/citations?user=YOUR_ID', icon: 'fas fa-graduation-cap', label: 'Google Scholar' },
    { href: 'https://talhamahamud.substack.com/', icon: 'fas fa-bookmark', label: 'Substack' },
    { href: 'https://medium.com/@iamtalhamahamud', icon: 'fab fa-medium', label: 'Medium' },
    { href: 'https://www.youtube.com/@talhamahamud3176', icon: 'fab fa-youtube', label: 'YouTube' },
    { href: 'mailto:talhamahamudd@gmail.com', icon: 'fas fa-envelope', label: 'Email' },
  ];

  const page = document.body.dataset.page || '';
  const root = document.documentElement;
  root.classList.remove('no-js');

  /* ---------- Header ---------- */
  const logoSvg =
    '<svg class="logo-mark" viewBox="0 0 68 40" fill="none" aria-hidden="true">' +
    '<path class="logo-orbit" d="M34 20C27 9 21 6 14 6 6.3 6 2 12.3 2 20s4.3 14 12 14c7 0 13-3 20-14s13-14 20-14c7.7 0 12 6.3 12 14s-4.3 14-12 14c-7 0-13-3-20-14z" stroke-width="4" stroke-linecap="round"/>' +
    '</svg>';

  const header = document.querySelector('.site-header');
  if (header) {
    header.innerHTML =
      '<a class="logo" href="index.html" aria-label="Talha Mahamud — home">' + logoSvg +
      '<span class="logo-text">Talha Mahamud</span></a>' +
      '<nav class="nav-links" aria-label="Main">' +
      NAV.map(n => '<a href="' + n.href + '"' + (n.key === page ? ' class="active" aria-current="page"' : '') + '>' + n.label + '</a>').join('') +
      '</nav>';
  }

  /* ---------- Socials (any .socials[data-fill]) ---------- */
  const socialsHtml = SOCIALS.map(s =>
    '<a href="' + s.href + '"' + (s.href.startsWith('mailto:') ? '' : ' target="_blank" rel="noopener"') +
    ' title="' + s.label + '" aria-label="' + s.label + '"><i class="' + s.icon + '"></i></a>'
  ).join('');
  document.querySelectorAll('.socials[data-fill]').forEach(el => { el.innerHTML = socialsHtml; });

  /* ---------- Footer ---------- */
  const footer = document.querySelector('.site-footer');
  if (footer) {
    footer.innerHTML =
      '<div class="wrap">' +
      '<div class="footer-top">' +
      '<div><span class="eyebrow">Say hello</span>' +
      '<p class="footer-cta" style="margin-top:14px"><a href="mailto:talhamahamudd@gmail.com">Let’s talk <em class="grad">physics.</em></a></p></div>' +
      '<div class="socials">' + socialsHtml + '</div>' +
      '</div>' +
      '<div class="footer-bottom"><span>© ' + new Date().getFullYear() + ' Talha Mahamud</span><span>To infinity &amp; beyond ∞</span></div>' +
      '</div>';
  }

  /* ---------- Reveal on scroll ---------- */
  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(el => io.observe(el));
  } else {
    reveals.forEach(el => el.classList.add('in'));
  }

  /* ---------- Back-to-top button ---------- */
  const toTop = document.querySelector('.to-top');
  if (toTop) {
    window.addEventListener('scroll', () => toTop.classList.toggle('visible', window.scrollY > 500), { passive: true });
    toTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }
})();
