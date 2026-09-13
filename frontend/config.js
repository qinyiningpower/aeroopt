/* Shared request context: every API request identifies its vehicle explicitly. */
window.escapeHTML = value => String(value).replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));
if (!/^[1-7]$/.test(localStorage.getItem('selectedCar') || '')) {
  localStorage.setItem('selectedCar', '1');
}
const nativeFetch = window.fetch.bind(window);
window.fetch = (input, options = {}) => {
  const url = new URL(input, location.href);
  if (url.origin === location.origin) {
    const headers = new Headers(options.headers);
    headers.set('X-Model-ID', `model_${localStorage.getItem('selectedCar').padStart(2, '0')}`);
    options = {...options, headers};
  }
  return nativeFetch(input, options);
};
document.addEventListener('DOMContentLoaded', () => {
  const notice = document.createElement('p');
  notice.className = 'demo-notice';
  notice.textContent = 'Research prototype · Precomputed case results · Model training and optimization run separately';
  document.body.prepend(notice);
  const car = document.getElementById('carImg');
  if (car) car.src = car.getAttribute('src').replace(/images\/\d+_/, `images/${localStorage.getItem('selectedCar')}_`);
  document.querySelectorAll('.dot').forEach(dot => {
    dot.setAttribute('role', 'button');
    dot.tabIndex = 0;
    dot.setAttribute('aria-label', `Analyze ${dot.dataset.type} region`);
    dot.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); dot.click(); }
    });
  });
  fetch('/health').then(r => r.json()).then(data => {
    if (!data.ai_enabled) notice.textContent += ' · AI explanations disabled (API key required)';
  }).catch(() => { notice.textContent += ' · API unavailable'; });
});
window.addEventListener('unhandledrejection', () => {
  const box = document.getElementById('infoBox') || document.getElementById('aiExplanation');
  if (box) box.textContent = 'Unable to load results. Check the server and try again.';
});
