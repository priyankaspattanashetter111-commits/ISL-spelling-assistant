# Verification and remaining acceptance tests

Executed during packaging:

- Node core tests: 5 passed (stable hold, duplicate prevention, repeated letter release, low-confidence block, candidate transitions, short dropout, spelling typo/prefix/custom word checks).
- Vite production build: passed, 24 modules compiled.
- Python source compilation: passed; this checks syntax only.
- Python feature tests: 4 passed (missing hands, presence flags/feature length, translation/scale invariance, degenerate palms).
- Headless installed Chrome: application loaded without JavaScript errors; COVID example populated the editor; saved History rendered; desktop screenshot inspected; 390px mobile layout had no horizontal overflow.
- Live Node API on localhost: health 200 and honest offline-ML status; COVD suggestion returned COVID; BMS custom prefix returned persisted BMSIT; vocabulary save/delete and history save/delete succeeded; invalid numeric vocabulary returned 400; prebuilt page returned 200.

Not established by these checks: real ISL recognition accuracy, physical webcam compatibility, hand-landmark runtime performance, MongoDB runtime persistence, browser speech quality, and unseen-signer generalization. Python dependency installation was attempted but did not complete in the authoring environment; ML runtime integration remains unverified. No trained ISL model/evaluation metrics can be produced without real labelled recordings. The delivered setup commands are required locally before camera collection and training.

Manual acceptance table (record actual observations, never fill with assumed passes):

| Test | Procedure | Expected |
|---|---|---|
| Alphabet | Test each trained A–Z label on independent signer/session | Record per-class metrics, not only examples |
| Unknown gesture | Show non-alphabet poses | Record false accepts; forest may confidently misclassify |
| Double letter | Sign H E L, release, L, release, O | HELLO, no held-sign duplicates |
| Low confidence | Raise threshold | No auto insertion; explicit confirmation available |
| Correction | Edit letter, delete, undo | Previous text recovered |
| Suggestion | Enter COVD, select COVID | Current word corrected |
| Custom vocabulary | Add BMSIT; restart server | Saved word appears and suggested from BMS |
| Custom pose | Collect word-labelled samples; retrain | Word class appears in health; evaluate separately |
| History | Save sentence, restart, restore | Same sentence restored |
| Practice | Select A, predict A/B | Correct/incorrect stored accurately |
| MongoDB | Enable mongo; add word; restart API | UI shows mongo; data persists |
| Speech | Enter sentence, click Speak | Audible output with installed voice |
| Lighting | Repeat held-out protocol bright/dim/backlit | Record separate confusion matrices |
| Geometry | Repeat at varied angles/distances/hand overlap | Record failures and latency |
| Camera privacy | Click Stop | Camera tracks end; no footage files written |

An academic presentation should say “implemented prototype, awaiting real-data validation” until these tests are completed. Natural continuous signing and dynamic signs need a future temporal dataset/model.
