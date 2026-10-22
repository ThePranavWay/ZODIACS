/* Level 3 connector: the supplied testimonies page is unchanged. When its
   witness file unseals, this separate file records Level 3 completion on
   the main website (server still verifies the key and level order). */
(() => {
  'use strict';
  if (!window.ZodiacLevels) return;
  const LEVEL = 3;
  let lastCode = '', reported = false, busy = false, failed = false;

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
    if (error.status === 403 && /Complete Level/i.test(error.message)) el.textContent = error.message + ' Re-enter the file key after finishing the earlier level so this completion can be saved.';
    else ZodiacLevels.errorMessage(error, el);
  }
  async function report() {
    if (reported || busy || failed || !lastCode) return;
    if (!document.querySelector('.shell')) return;
    busy = true;
    try { await ZodiacLevels.verify(LEVEL, lastCode); reported = true; }
    catch (error) { failed = true; showError(error); }
    finally { busy = false; }
  }
  document.addEventListener('submit', event => {
    if (event.target && event.target.id === 'unlock') {
      lastCode = document.querySelector('#code')?.value || ''; failed = false;
      setTimeout(report, 300); setTimeout(report, 1200);
    }
  }, true);
  new MutationObserver(() => report()).observe(document.body, { childList: true, subtree: true });
  ZodiacLevels.resume(LEVEL);
})();
