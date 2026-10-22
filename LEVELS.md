# Levels — new seven-level structure (from 22 October 2026)

The event now has **7 levels**. Progress on `/play` shows **x / 7**, levels
unlock **strictly in order** (Level 2 cannot be submitted before Level 1 is
complete, and so on), and the timer/podium finish only after **all seven**
levels are verified. Each solo/team entry shares one progress record; a level
can be completed only once per entry.

## Current levels

| Level | URL | File | How it completes |
|---|---|---|---|
| 1 — Document 001 · Letter | `/letter` | `public/letter.html` | Supplied file unchanged (its access code intentionally stays in its source for students to find). Enter the code, then review **all 6 records**; an external connector (`public/level1-connect.js`) mirrors reviewed records to the server, which marks Level 1 complete at 6/6. |
| 2 — Document Z-K | `/document-z-k` | `public/document-z-k.html` | Supplied file unchanged. Completes when its sealed map opens; `public/level2-connect.js` records the completion and keeps its **YES** witness-files button on the current website (`/testemonies`) instead of the file's hard-coded live domain. |
| 3 — Witness File | `/testemonies` | `public/testemonies.html` | Completes when the witness file unseals; `public/level3-connect.js` records the completion. At the organizer's request, the supplied file's pending-audio placeholder is now a **LISTEN AUDIO** button opening the organizer's Jumpshare page in a new tab, where students can listen or download the audio. Playing/downloading it is optional and does not affect completion. |
| 4–7 | to be announced | not yet added | Added one by one with the same pattern below. |

Per the organizer's instruction, **supplied level files are otherwise not
altered**: their content, gates and in-file codes remain exactly as provided
apart from two `<script>` tags before `</body>` loading the bridge and that
level's connector, plus the single organizer-requested Level 3 audio link
described above. Connectors talk to the backend through
`public/level-session.js` (`ZodiacLevels.unlock`, `.view`, `.verify`,
`.progress`). A level page can never mark itself complete on the main
website: the server re-verifies the same code against
`LEVEL_<n>_PASSWORD_SHA256` (a SHA-256 hex digest set as an environment
variable), enforces the order, and is the only place that writes completions
(`zs_completions`) and finishes (`zs_finishes`). Keeping a code inside a
level file means any student can find it with view-source — that is intended
by the organizer for these levels.

There are **no level links on `/` or `/play`**. A student opens a level only
by deliberately typing its URL (for example `/letter`).

Students must be logged in to use a level page. If they are not, the page
links them to `/play` to log in and returns them to the level afterwards.

## Not part of the website

- The organizer's **GM solution key** (`SOLUTION.md` supplied with Level 1) is
  never uploaded to the website or the public GitHub repo.
- The printable **sticky-note handout** supplied with Level 1 is a physical
  prop for the organizer; the same note is already available inside
  `/letter` after the gate. It is not published as a web page.

## Old levels (removed)

The previous standalone level pages were deleted on the organizer's
instruction and their URLs return 404:

- `public/attacks.html` (formerly `/attacks`)
- `public/investigate.html` (formerly `/investigate`)
- `public/next.html` (formerly `/next`)
- `public/later.html` (formerly `/later`)

**GitHub upload warning:** dragging files into GitHub's web uploader does NOT
delete files missing from the upload. Delete those four files individually on
GitHub (open each file → Delete file → Commit). Do **not** delete
`public/level-session.js`: the upload replaces it with the new version that
`/letter` (and future levels) need. See `UPDATE-2026-10-21.md`.

## Adding the next level (Levels 4–7)

1. Add the level file under `public/` at its chosen URL (e.g.
   `public/<slug>.html` → `/<slug>`) and register the slug in `LEVEL_FILES`
   in `app.py` plus cache headers in `vercel.json`.
2. Leave the supplied level file itself unchanged. Add a separate
   `public/level<n>-connect.js` that observes the level's own completion
   moment and calls `ZodiacLevels.unlock(n, code)` for a gate,
   `ZodiacLevels.view(n, itemId)` for reviewed records, or
   `ZodiacLevels.verify(n, answer)` for a password-completes level; load the
   bridge + connector with two script tags before `</body>`.
3. If the level completes after reviewing records, add its required count to
   `LEVEL_VIEW_REQUIREMENTS` in `app.py`.
4. Set `LEVEL_<n>_PASSWORD_SHA256` in Vercel (and in the local preview
   environment) to the SHA-256 hex of that level's code.
5. Add the file to `scripts/build-check.js`, extend the tests, run
   `npm run build`, and test the full student journey in the preview.
