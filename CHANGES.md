# Changes from the supplied repository

## 21 October 2026 organizer update

- Deleted the four level HTML files and level-session.js; removed their
  Vercel headers, clean-URL mapping, build-check entries and preservation
  hashes; tests now assert those routes are 404. Backend level-verification
  API, progress/podium tables and existing records were intentionally kept.
- Launch page: larger Poppins/responsive hero title, full-screen layout,
  removed the "Four levels. One investigation." line, added glowing orange
  VIEW BROCHURE button serving public/zodiac-seeker-brochure.pdf.
- /play: added Mission Briefing, Objectives and Initial Evidence sidebar tabs
  (new public/mission.css; minimal app.js tab routing update with refreshed
  preservation hash). Case overview, notebook and leaderboard retained.
- Added public/initial-evidence-reddit-post.png. See UPDATE-2026-10-21.md.
- Launch date moved from 24 October to 1 November 2026 (still 12:00 AM IST);
  the 13 November 2026 noon closing is unchanged.
- Registration fixes: the register button now states when registration is
  closed, form errors scroll into view, and post-registration tab routing
  is guarded against stale/mismatched cached page scripts.
- Registration/login direct-entry fix: after registering, the student enters
  the dashboard immediately and stays in; login is only for returning later.
  The bounce-back ("Please log in to your investigator account.") happened
  inside cross-site iframes (hosted previews) where the browser blocks the
  third-party session cookie, so the calls right after register/login got 401.
  SESSION_COOKIE_SAMESITE=None (trusted embedding only) now sets a
  Secure+Partitioned (CHIPS) cookie and returns the just-issued session token
  to the page for an Authorization fallback, so notes/leaderboard/polling keep
  working even with cookies blocked. Default stays Lax with the HttpOnly
  cookie only — identical to the original GitHub build for the public site.
  Login/token forms reset only after the /api/me session check succeeds.
  One admission number can still register only once (database-enforced, 409).
- New seven-level system (22 Oct): progress is now x/7, levels unlock strictly
  in order, and finish/podium occur only after all seven. Levels 1-3 live at
  typed URLs only (/letter, /document-z-k, /testemonies; no links on / or
  /play) via a restored public/level-session.js plus per-level external
  connectors. Except for replacing Level 3's pending-audio placeholder with
  an organizer-supplied Jumpshare LISTEN AUDIO link, supplied level files are
  unchanged apart from connector script tags - their in-file codes remain for
  students to find, per the organizer -
  while the server re-verifies codes, tracks Level 1's reviewed records
  (zs_level_views, complete at 6/6), and is the only writer of progress.
  SOLUTION.md (GM key) and the printable handout are not published. From
  31 October night 12:00 AM IST (1 Nov 2026) the main/index URL directs
  everyone to /play.

Source commit: c2122feaa6b661a629c2dcf1b433cf47cb37002c.

## Theme integration

Added public/zodiac-theme.css, public/zodiac-theme.js and locally bundled reference font families/licenses. Added the two theme tags at the end of the head of index.html, play.html, organizer.html and event-ended.html. Their original page content, form IDs, scripts, dates and existing closing gate remain in place.

## Backend consistency repair

The supplied app.py imported `advanced`, but advanced.py was absent. The supplied frontend app.js and schema.sql were already the separate four-level/podium versions. The complete package therefore restores the matching four-level backend (version 4), retains the supplied /play route and scheduled event-ending hook, and does not add any extra levels or advanced module.

## Preserved byte-for-byte

- All four original level HTML files and level-session.js.
- public/app.js, public/organizer.js, public/style.css and public/event-redirect.js.
- storage.py, schema.sql and vercel.json.
- Original images/fonts/assets from the supplied repository.

preservation-sha256.json records the protected public-file hashes. The main case image source is retained.

## Tests and documentation

Added four-level podium regressions and integrated theme/launch/ending tests. Main-page assertions now check play.html, because index.html is the launch landing. Build validation now includes play/end inline scripts plus the new theme/closing scripts. Updated the outdated v2/new-event deployment documents so installation does not instruct a reset.

Only the additive four-level podium SQL migration is supplied. The obsolete destructive legacy reset SQL file is intentionally omitted; no database operations were performed.

## Not changed or performed

No live repository push, Vercel deployment, database migration, account deletion, signing-key/password rotation, real participant export or public winner publication. No .git directory, real .env, local database, signing key or test-browser state is included in the archive.
