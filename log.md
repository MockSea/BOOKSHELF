# Catalog log

One entry per photo processed. Records what came out of it, what I couldn't
read, and when the image moved to SORTED.

Drive: a private `BOOKSHELF` folder shared with me; the ids stay out of this
repo.
Mo drops photos in `NEW`; once catalogued they move to `SORTED`.

---

## 2026-09-17 — first batch, four photos

Mo dropped `IMG_2120`–`IMG_2123` into `NEW`. They're four adjacent horizontal
stacks on one shelf unit, shot left to right; consecutive frames overlap, which
is how the order was confirmed (The Cryptopians sits at IMG_2122's left edge,
and the Saga spine appears in both 2121 and 2122). He's since named the unit
**shelf 1**, so the stacks are recorded as 1A through 1D. Every book on it is
contributed by **TNK**.

Rotation note for future batches: these come off the phone as 4032x3024 with an
EXIF upper-right orientation. `ffmpeg` applies that automatically, so crops can
be written in display coordinates. `gm` is aliased to `git merge` on this
machine and is not GraphicsMagick.

### IMG_2120 → shelf 1A, 12 books
Baldwin's *Collected Essays* and *Early Novels & Stories* at the top, both
Library of America and both still shrink-wrapped — the spines only say
"Baldwin", so the forename is inferred from the imprint. Down through Davos
Man, The Relational Self, Letters to the Sons of Society, Toothpicks & Logos,
Make It Stick, The World Until Yesterday, Nonzero, Before European Hegemony
(used-shop sticker, $13.35), Being Black, and Social Origins of Dictatorship
and Democracy at the bottom. Nothing unreadable.

### IMG_2121 → shelf 1B, 10 books
The Cryptopians down to The Social Life of Small Urban Spaces. Two things worth
recording. The Saga volume number isn't legible in this frame; it was read as
**7** off a crop of the same spine in IMG_2122, a green numeral at the foot.
I also entered a phantom: a black band above The Photographer's Eye's spine,
carrying an orange serif capital P and a black-and-white photograph of a
building, went in as an unidentified eleventh book. Mo: *"There's no book
between saga and the photographers eye."* He's right. The stack tilts forward,
so that black surface is The Photographer's Eye's own front cover showing above
its spine, and the P is the tail of its title. Row deleted, stack renumbered.
Worth carrying into the next batch: a tilted stack shows covers as well as
spines, and a cover reads like a spine at a glance.

### IMG_2122 → shelf 1C, 11 books
The Proper Study of Mankind down to Strong Towns. Fukuyama's *Trust* has a shop
barcode label over the end of the title — the spine reads "TRUS" — so it's in at
0.88 confidence rather than clean. How to Turn a Place Around is shelved upside
down, which is cosmetic but recorded in case the positions get checked against a
photo later.

### IMG_2123 → shelf 1D, 13 books
Gaining Currency down to Galápagos. All legible.

### Seen but deliberately not catalogued
The bottom edge of several frames catches the shelf *below*, which Mo hasn't
photographed. Cropped and partial, so entering them would put wrong shelf and
position data in the table. Noted here instead: Soul of an Octopus (Sy
Montgomery, Atria), Talking to My Daughter About the Economy (Varoufakis), The
Unicorn's Shadow, Unraveling: Remaking Personhood in a Neurodiverse Age
(Wolf-Meyer, Minnesota), Exit Voice and Loyalty (Hirschman, Harvard), a
Spanish-language yellow paperback reading "HACKEA … MACHO … Nicko Nogués", and
manga at the bottom right.

### What's not in the rows
No years, and no ISBNs. Neither is printed on a spine, and filling them from
memory is exactly the guess the whole `status` column exists to prevent. They
come from a catalog lookup or from Mo pulling a book off the shelf.

All four images moved to `SORTED`.

## The page went up — 2026-09-17

<https://claude.ai/code/artifact/e377db7d-9cb4-426d-bb2c-c689f30e2c02>, v1,
46 of 60. Rendered from `catalog.db` by `./render`, so it is a snapshot: it is
current as of the last render, not a live query.

Mo asked for a way to send corrections through the page, with a login, while
keeping the page public. Those two pull against each other on this platform —
`db`, `assets` and a full `comments` declaration each make an artifact
organization-internal and un-shareable. The composer-only form of `comments`
is the one that does both: the page opens the shell's own comment composer
anchored to a book's row, and the viewer's signed-in account writes the
thread. The page posts nothing and holds no credential. Public link visitors
read the shelf; signed-in people can correct it.

Still private as published — sharing is flipped from the artifact's own share
menu, which is Mo's to do.

## Mobile rebuild — 2026-09-17

Mo, on v2: *"It's not very mobile friendly. Text is bleeding, layout feels
sloppy"* and *"Think of a catalogue app like Spotify or Apple Music, any
library management really"*.

Three things were actually broken at 390px:

- `table { min-width: 760px }` inside `.sheet { overflow-x: auto }` — the whole
  catalogue scrolled sideways in a box.
- The wordmark at `clamp(52px, 15vw, 132px)` measured ~366px against a 354px
  gutter once the skew and the two offset shadows were counted. Now 11.5vw.
- The 60-cell meter in one row gave each cell ~2.9px. It folds to 20 a row
  below 760px.

The table is gone. The list is a `role="table"` grid of `.lrow` divs sharing one
`--cols` template, so the same DOM is six columns on a wide screen and a track
list on a phone (`grid-template-areas`: index / title / state, with author,
publisher and contributor collapsed into one meta line). No duplicated markup,
no responsive-table `data-label` hack.

Also added: a sort control (shelf order, title, author, needs-checking-first),
a results line, and keyboard-openable rows. `unverified` lost its box — 46
identical bordered chips were the noisiest thing on the page, and it is the
resting state of every spine read, so it is plain grey text now. Confirmed and
Needs Mo keep the box because they mean someone did or should look.

Verified at 390px with playwright (`scrollWidth === clientWidth`, no element
past the gutter) rather than a screenshot — `browser_take_screenshot` still
times out at 5000ms on this page, and headless Chrome will not lay out below
~500px, so the shots are at 500 and 1240.

v3 published, same URL. Still private.


## Swipe verification, sticky filters — 2026-09-17

Two things Mo asked for, one after the other.

**Shelf Check**, the verification portal. His brief was *"I would like
verification to work like bumble. Swipe right if all the details are good,
swipe left if something is off"*. It is a separate artifact
(`deaf3649-298b-459a-b7a6-47716c623213`), private, declaring
`capabilities: {db: {}}`, generated by `./render-swipe` the way `render`
generates BOOKSHELF. Same tokens and faces — it is the second surface of one
product, not a different tool.

Why two pages instead of one: a `db`-declaring artifact is organization-
internal and cannot be shared publicly, and Mo wants BOOKSHELF public. So the
public page carries no capabilities at all and Shelf Check carries the store.
Verdicts land in a `verdicts` collection keyed by book id; `read_db` pulls them
out, `./apply-verdicts` writes them into catalog.db, `./render` rebuilds the
public page.

`off` does **not** rewrite anything. It sets `status=needs_input` and puts the
note in `question`. A flag says a record is wrong, not what the right answer is,
and inventing the difference is exactly the failure the whole project's rule
exists to prevent.

The card is one DOM with a scrolling body inside a fixed frame, so the longest
record on shelf 1 (The Photographer's Eye, 539px of card) scrolls internally
instead of pushing the buttons off a 390px screen. Measured, not eyeballed.

**Sticky toolbar.** Mo: *"That's a lot of scrolling for mobile. Can the table be
sticky? Or at least the filters?"* — and the interesting part is that `.lhead`
already said `position: sticky; top: 0` and had never once stuck. `body` carried
`overflow-x: hidden`, which makes the body a scroll container and leaves sticky
children pinned to a box that never scrolls. Removed it; the layout measures
clean at 390 and 1280 without the guard, so it had been hiding nothing and
costing the feature.

Now the toolbar pins at `top: 0` and the column header pins at
`top: var(--stick)`, where `--stick` is the toolbar's measured height under a
ResizeObserver — the chips rewrap on rotation and a search field grows a clear
button as you type, so no constant survives. 136px on a phone after a tighter
mobile padding pass, 151px on desktop.

BOOKSHELF v7. Mo made it public sometime today; sharing now reads `public`.
