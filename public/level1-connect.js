/* Level 1 connector: the supplied /letter page and its in-code access key are
   unchanged. This separate file only mirrors reviewed records to the main
   website so /play progress stays in sync. */
(() => {
  'use strict';
  if (!window.ZodiacLevels) return;
  const LEVEL = 1;
  const reported = new Set();
  let tokenReady = false, ensuring = null, lastAttempt = 0, loginShown = false;

  function statusEl() {
    let el = document.getElementById('zodiac-connect-status');
    if (!el) {
      el = document.createElement('div'); el.id = 'zodiac-connect-status'; el.setAttribute('role', 'status');
      Object.assign(el.style, { position: 'fixed', bottom: '64px', left: '50%', transform: 'translateX(-50%)', background: '#392b22', color: '#fff6e4', border: '1px solid #ad8b4b', borderRadius: '4px', padding: '10px 17px', font: '12px/1.5 Arial,sans-serif', zIndex: '9999', maxWidth: '90vw', textAlign: 'center' });
      document.body.append(el);
    }
    return el;
  }
  function showLogin(error) {
    if (loginShown) return; loginShown = true;
    ZodiacLevels.errorMessage(error, statusEl());
  }
  function archiveOpen() {
    return document.querySelector('#archive')?.classList.contains('on') ||
           document.querySelector('#doc')?.classList.contains('on');
  }
  async function ensureUnlock() {
    if (tokenReady) return true;
    if (ensuring) return ensuring;
    if (Date.now() - lastAttempt < 10000) return false;
    lastAttempt = Date.now();
    ensuring = (async () => {
      try {
        const code = (typeof ACCESS_KEY !== 'undefined' ? String(ACCESS_KEY) : '').trim();
        if (!code) return false;
        const result = await ZodiacLevels.unlock(LEVEL, code);
        tokenReady = true;
        (result.viewed_items || []).forEach(id => { state.read.add(id); reported.add(id); });
        if (archiveOpen()) renderArchive();
        return true;
      } catch (error) {
        if (error.status === 401 || error.status === 403) showLogin(error);
        return false;
      } finally { ensuring = null; }
    })();
    return ensuring;
  }
  async function syncViews() {
    if (typeof state === 'undefined' || !archiveOpen()) return;
    if (!(await ensureUnlock())) return;
    for (const id of [...state.read]) {
      if (reported.has(id)) continue;
      reported.add(id);
      try { await ZodiacLevels.view(LEVEL, id); }
      catch (error) {
        reported.delete(id);
        if (error.status === 401 || error.status === 403) { tokenReady = false; showLogin(error); }
        break;
      }
    }
  }
  (async () => {
    try {
      const result = await ZodiacLevels.progress();
      (((result.viewed_items || {})[String(LEVEL)]) || []).forEach(id => { state.read.add(id); reported.add(id); });
      if (result.completed_levels.includes(LEVEL)) {
        show('archive'); renderArchive();
        ZodiacLevels.showCompleted(LEVEL); ZodiacLevels.showFinish(result);
      }
    } catch (_) { /* not logged in yet: the level still opens; progress saves after login */ }
    setInterval(syncViews, 700);
    document.addEventListener('click', () => setTimeout(syncViews, 120), true);
  })();
})();
