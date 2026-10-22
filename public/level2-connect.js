/* Level 2 connector: the supplied DOCUMENT Z-K page is unchanged. When its
   sealed map opens, this separate file records Level 2 completion on the
   main website. Its YES button is also kept on the current website
   (/testemonies) instead of the file's hard-coded live domain, so the same
   flow works in previews and after deployment. */
(() => {
  'use strict';
  if (!window.ZodiacLevels) return;
  const LEVEL = 2;
  let lastCode = '', reported = false, busy = false, failed = false, redirecting = false;

  function statusEl() {
    let el = document.getElementById('zodiac-connect-status');
    if (!el) {
      el = document.createElement('div'); el.id = 'zodiac-connect-status'; el.setAttribute('role', 'status');
      Object.assign(el.style, { position: 'fixed', bottom: '64px', left: '50%', transform: 'translateX(-50%)', background: '#392b22', color: '#fff6e4', border: '1px solid #ad8b4b', borderRadius: '4px', padding: '10px 17px', font: '12px/1.5 Arial,sans-serif', zIndex: '99999', maxWidth: '90vw', textAlign: 'center' });
      document.body.append(el);
    }
    return el;
  }
  function showError(error) {
    const el = statusEl();
    if (error.status === 403 && /Complete Level/i.test(error.message)) el.textContent = error.message + ' Your map progress here will be saved once the earlier level is complete — re-enter the map code after finishing it.';
    else ZodiacLevels.errorMessage(error, el);
  }
  async function report() {
    if (reported || busy || failed || !lastCode) return;
    const opened = (typeof mapOpen !== 'undefined' && mapOpen) || document.body.textContent.includes('LOCATION INDEX / UNSEALED');
    if (!opened) return;
    busy = true;
    try { await ZodiacLevels.verify(LEVEL, lastCode); reported = true; }
    catch (error) { failed = true; showError(error); }
    finally { busy = false; }
  }
  document.addEventListener('submit', event => {
    if (event.target && event.target.id === 'mapform') {
      lastCode = document.querySelector('#mapcode')?.value || ''; failed = false;
      setTimeout(report, 500); setTimeout(report, 1600);
    }
  }, true);
  document.addEventListener('click', async event => {
    const yes = event.target && event.target.closest ? event.target.closest('#yes') : null;
    if (!yes || redirecting) return;
    event.preventDefault(); event.stopPropagation(); event.stopImmediatePropagation();
    redirecting = true;
    await report();
    location.assign('/testemonies');
  }, true);
  new MutationObserver(() => report()).observe(document.body, { childList: true, subtree: true });
  ZodiacLevels.resume(LEVEL);
})();
