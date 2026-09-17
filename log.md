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

## Moved to GitHub Pages — 2026-09-17

Mo asked for the catalogue to live on GitHub Pages so the database is tracked
as it grows, instead of the artifact needing a manual republish each time.
Then: host it under my account.

So `library/` became its own repo instead of an untracked corner of
`workspace/`. `render` now writes `docs/index.html`, which is what Pages
serves off `main`, and `catalog.db` is tracked rather than ignored — the whole
point being that the database and the page it produced land in the same commit.

Scrubbed before anything went near a public repo: the Drive folder id out of
this file and the README, and Mo's email out of the Open Library User-Agent in
`enrich` (replaced with the repo URL, which is a contact Open Library can
actually use). `photos/` and `work/` are ignored — the catalogue is public,
pictures of TNK's living room are not.

No GitHub Action. The token here has `repo` but not `workflow`, so a workflow
file can't be pushed, and Pages-from-branch does the same job here: a push is
a deploy. It also means the site can only be as current as the last `./render`,
so that is now written into the README as one step and not two.

Verification does not move. Pages is static; the swipe portal has to write a
verdict somewhere, and that somewhere is the artifact runtime's `db`. Shelf
Check stays an artifact.

Blocked at the last step: creating the public repo was denied here, so the push
and the Pages switch are waiting on Mo.

## The record and the table, reworked — 2026-09-17

Mo, on the detail view: *"There's got to be a better way of showing this
information. Libraries and bookstores do it, we can too."* And on the table:
*"Maybe we can reduce the information here. change status to a color to save
space, give the column titles some room to breathe. Text wrapping for book
information."*

**The record.** It was a summary sitting on top of twelve undifferentiated
label/value rows, which at 390px stacked into 1393px of scroll. What a library
actually does is split the record in two: the **work** (true of every copy ever
printed, and it came from a catalogue) against the **item** (true of this one,
and it came from the photograph). Mo's columns fall on that line already —
`ol_first_year`, `page_count` and `subjects` are the work; `shelf`, `position`,
`contributor`, `spine` and `confidence` are the copy. Two headed blocks instead
of one flat list, and the page stops hiding that it knows the difference.

Around that: a call-number strip pinned above the scroll (where · whose ·
checked or not), the blurb leading as a jacket blurb does, subject headings as
chips underneath it rather than as a labelled row, and an empty field simply
not rendering — `Year: —` twelve times was most of the old height. The three
that a spine genuinely cannot supply get named once at the bottom instead.

On a phone the dialog is the screen: `max-width:none`, full height, no border.
A 560px card inside a 390px viewport spent a gutter, a border and a max-height
before it reached any words. The label column stays two-column at 88px rather
than stacking — stacking is what doubled the scroll. 1230px now, with the
summary reachable at y=139 and the close button in the head, which doesn't
scroll.

**The table.** `WHERETITLE` in his screenshot was a 44px grid track with a
header word wider than the value it labels, bleeding right. Now 52px, and every
header cell shrinks and clips. Status is a swatch — the same solid-yellow /
hatched pair the meter in the hero already uses — with a key above the list;
forty-six rows reading UNVERIFIED said one thing forty-six times for 124px.
Publisher left the table entirely, and the mobile meta line is the author alone:
the contributor chip was the same three letters on all forty-six rows and was
what the author line kept wrapping around. `overflow-wrap` went from `anywhere`
to `break-word`, which is why "McDaniel," was splitting oddly.

One thing worth keeping: `.lhead` and each `.lrow` are separate grids, so an
`auto` track sizes to the header word in one and to the 15px swatch in the
other, and the title column starts in a different place on every line. Both
breakpoints use fixed tracks now. Verified aligned at 1280 and 390.

## Enrichment, and what was empty — 2026-09-17

Mo: *"How's enrichment going? I'm seeing a lot of empty stuff"*. He was right,
and the reason was structural rather than a bad run.

`enrich` asked Open Library one question — `search.json`, which answers about a
**work**. A shelf holds an **edition**. Year, ISBN, binding and page count are
properties of a printing and `search.json` carries none of them, so `year` and
`isbn13` were at 0 of 46 while subjects and covers filled in normally. Worse,
the one ISBN the work search did return was being written to `ol_isbn13`, a
different column from the `isbn13` the record view reads, so it never appeared.

The fix is a third request, to `{work}/editions.json`, and a rule for choosing
from the list. The tie to *this copy* is the imprint off the spine, compared by
token containment rather than substring: "Belknap / Harvard" has to match
"Belknap Press of Harvard University Press", while "Anchor Books" has to refuse
"Pantheon Books" — they agree only on the word "books", which is why the
stopword set exists. Davos Man has three editions; exactly one says Custom
House, and that one carries the ISBN, 336 pages and "hardcover".

**34 of 46 are tied to an edition, all of them by publisher.** year 0 → 34,
isbn 0 → 34, publisher 40, format 22, pages 38, subjects 32, cover 34.

The twelve with no tie write nothing, and the record view now says which of the
two reasons applies — no work matched at all, or a work matched and no edition
under this imprint. A blank with a reason is more use than a blank, and much
more use than a plausible wrong year.

### Two things already wrong on the live page

Both found by the edition pass and fixed in the data, with a guard added to the
scripts so neither recurs.

**Three wrong printings.** My first rule took a work's sole edition when the
imprint couldn't settle it. That gave The Edge of Islam a 2002 UMI dissertation
microfilm (the spine says Duke), Radical Dharma a ReadHowYouWant large-print
reprint (North Atlantic Books), and China in Ten Words the Pantheon hardcover's
ISBN for an Anchor paperback. A sole edition is now only taken when we have no
imprint of our own to check it against — where we do have one and it disagrees,
the disagreement *is* the finding. Zero `sole` matches remain.

**A wholly wrong work.** Baldwin's *Collected Essays* had matched
`/works/OL1528260W` — an 1902 C. Scribner's Sons volume, subjects "Philosophy;
Psychology", someone else's cover, all of it live on the page. It scored 0.85 on
an exact title match against a record naming no author, and nothing objected
because there was no author to disagree with. `confirmable()` now says a bare
title match on an authorless record only stands if the title is doing real
work — three meaningful words is a book, two is a category. That keeps China in
Ten Words (filed under 余华, unreadable after normalisation) and rejects
Collected Essays. The Library of America edition is not in Open Library's index
at all, so the right answer there is no match; the row is cleared.

### Summaries stay at 19 of 46

Not a bug and not fixable here. The only source is `description` on the work
record and most work records don't have one — sampled six of the blanks, all
`None`; edition records have no description field at all. Google Books has
descriptions and returns 429 to every unauthenticated request, re-confirmed
today. Closing it needs a free Google Books API key, which is Mo's call.

## Summaries, from Google Books — 2026-09-17

Mo supplied the key the previous entry said it needed. `./enrich --summaries`
is its own pass rather than part of `main` because the work match was settled
long before a key existed; re-running `main` would ask Open Library 46 more
questions to change one column. It writes `summary` and nothing else — subjects
and page count already came from a record tied to this printing, and Google's
are about some edition of the work.

22 of the 27 blanks filled on the first run. Summaries went 19 → 41 of 46.

Spot-checking the results found two blurbs that were not blurbs:

**"315 p" as the summary of *Imagined Communities*.** A physical-extent note
filed in Open Library's description field. Diffing the live db against
`git show HEAD:catalog.db` put it before this run, so it came through
`ol_description` → `clamp()`, which had no minimum length. `BLURB_MIN = 40`
now rejects it. Google had a real 773-character blurb once the field was clear.

**Mojibake and stray markup in *The Watchman in Pieces*.** A probe against the
live API confirmed Google ships both: codepoints `0xe2 0x20ac 0x201d` where an
em dash belongs — cp1252's rendering of that dash's UTF-8 bytes — and Project
MUSE's `DIV` / `/div` wrappers passed through as literal text, which is why the
HTML-tag stripper missed them. `demojibake()` re-encodes by the same table and
decodes as UTF-8; anything holding a character cp1252 cannot represent was
never mojibake and is left alone. A `MUSE` regex takes the markers.

The guards are in `clamp()`, so both fixes apply to whatever arrives next, and
every stored summary was re-run through it rather than patched by hand.

Five books still have no summary: 4 *The Relational Self*, 6 *Toothpicks &
Logos*, 15 *eTrust*, 32 *Handbook of Trust Research*, 40 *A Drop of Midnight*.
Google has no description for any of them — the first four are academic titles
with thin trade metadata.

---

## 2026-09-17 — shelves 2 and 3, eight photos

Mo: *"New photos added for bookshelf. I added them into specific folders for the
shelves their on"*. `NEW/SHELF 2` held `IMG_2137`–`IMG_2140`, `NEW/SHELF 3` held
`IMG_2141`–`IMG_2144`. Four stacks each, shot left to right, same unit geometry
as shelf 1, so the stacks are 2A–2D and 3A–3D. **108 books.**

Two route notes for next time.

`download_file_content` on a multi-megabyte Drive file always over-caps and
returns `result (N characters) exceeds maximum allowed tokens`. That is not a
failure — the harness writes the whole JSON envelope to `tool-results/`, and
base64-decoding `content` out of the saved file is the delivery mechanism. HEIC
then needs `sips -s format jpeg` before it can be looked at at all.

These frames are 5712x4284, not shelf 1's 4032x3024, and `sips` crops in
*stored* pixel coordinates while the EXIF orientation flips the image 90° for
display — so a horizontal band on screen is a vertical crop on disk, and
`-c H W --cropOffset Y X` takes those transposed. Worth knowing before cropping
a spine again.

### IMG_2137 → shelf 2A, 13 books
Toxic Sludge Is Good For You! down to Sources of the Self. Two Spanish-language
psychedelics books at the top. **Jill Fisher's *Adverse Events* appears twice**,
at positions 10 and 12 — not a misread, there are two copies on the stack.

### IMG_2138 → shelf 2B, 13 books
The Soul of an Octopus down to The Disciplinary Frame. All legible.

### IMG_2139 → shelf 2C, 15 books, one unreadable
Hackea tu macho down to Engineering Culture. **The third spine from the top is
plain green with no lettering caught by the frame** — logged as `needs_input`
with the question for Mo rather than guessed at. Panofsky's *Perspective as
Symbolic Form* has its first word hidden under the stack above, so it went in at
0.85. "STRONG TOWNS" is visible along the top of this frame; that is shelf 1C
seen from below and was not re-entered.

### IMG_2140 → shelf 2D, 13 books
The Manga Guide to Regression Analysis down to Getting Ahead Collectively.
**Barbara Smith's *The Truth That Never Hurts* appears twice**, at positions 4
and 5 — again two real copies, not a double read.

### IMG_2141 → shelf 3A, 11 books
Fugitives, Smugglers, and Thieves down to Turing's Cathedral. **The third spine
is covered by two resale barcode stickers**; what reads is "The Timeless Way"
and a name ending "…der", so it is in as Christopher Alexander's *The Timeless
Way of Building* at `needs_input`, not as a clean row.

### IMG_2142 → shelf 3B, 13 books
The Studs Terkel Reader down to Consent of the Networked. All legible.

### IMG_2143 → shelf 3C, 17 books, one uncertain
Voices of the Wild down to Cyclonopedia — the longest stack in either shelf.
**Position 12 is mostly buried under the book resting on it**: "STOCKHOLM", "&
Carl-Michael Edenborg" and the Akashic colophon. Read as *Stockholm Noir* from
the Akashic Noir series, at `needs_input`, because the co-editor's name is the
half that is covered.

### IMG_2144 → shelf 3D, 13 books
Yotsuba&! vol. 14 down to Out of Mao's Shadow. The Yotsuba spine faces the
opposite way from every other book in the frame and reads mirrored; a 180°
rotation of the crop resolves it — Kiyohiko Azuma, Yen Press, volume 14 in the
green roundel. **Not a question, just an upside-down book.** The Giles
*Civilization of China* below it is an old cloth hardcover with the spine cloth
torn away at the head, so the author line is the only clean reading, at 0.85.

### Same-author clusters worth noting
Albert O. Hirschman turns up three more times across these two shelves (*Exit,
Voice, and Loyalty*, *Getting Ahead Collectively*, *Rival Views of Market
Society*), which makes four with *The Rhetoric of Reaction* on shelf 1D.
Sarah Igo twice (*The Known Citizen*, *The Averaged American*), and Lo &
Hasanhodzic twice. Shame and personhood run through both shelves as a theme —
seven titles between them.

### The matcher was rejecting books it had already found
Enrichment came back with twelve rows it could not match, and the shape looked
right — Spanish-language paperbacks and thin academic titles. Three of them were
not that. *A Libertarian Walks Into a Bear* is in Open Library, the search
returned it, and the title scored a clean 1.0; the author test threw it away.

`norm()` turned punctuation into spaces, so our side of the comparison held the
single string `"hongoltz hetling"` while Open Library's side had been split into
`{"hongoltz", "hetling"}`. Two sets that agree completely and intersect in
nothing. Every compound or hyphenated surname in the catalogue had the same
hole: Balachandran Orihuela, Thøgersen, Abu-Lughod, Wolf-Meyer, Gómez-Escolar.

The same substitution was eating accents. `"Oña"` normalised to `"o a"`, both
tokens too short to survive the filter, which left an empty author set — and an
empty set does not read as "no match", it reads as *this row claims no author*,
which switches off the guard instead of failing it. `norm()` now folds accented
letters onto their ASCII base before stripping punctuation, and surnames are
tokenised the same way both sides are.

Two smaller things fell out of it. `enrich-retry` was appending the author to
the free-text query, which takes a query that finds the book and makes it find
nothing — Open Library's `q=` does not index author names reliably, and the
match test checks the author anyway, so the query is now the title alone. And
its write was a plain overwrite, which would have replaced a Google Books
summary with an Open Library blank; it now fills nulls and adds to the source
label rather than replacing it.

Recovered: five of the thirteen, including three rows that already had a Google
Books record and were missing Open Library's subjects and cover. Coverage across
all 154 books at the time was 132 summaries, 133 subject lists, 112 covers, 92
years.

Eight rows still had nothing, and those are the real thing: three Spanish-
language titles, *A Chuukese Theory of Personhood*, *A John Heskett Reader*,
*Unraveling*, *The Relational Self*, and the green spine nobody could read.

### The green spine was a notebook
Mo answered the 2C question: it is a blank notebook, not a book. Row 76 is
deleted and 2C renumbered to a contiguous 1-14, so the catalogue is 153 books
and the unmatched list is seven, not eight. Worth saying because the row was
never a failure of the enrichment pass - nothing was going to match it, and the
only thing that could resolve it was asking.

### Open with Mo
1. The Timeless Way of Building in 3A.
2. Stockholm Noir in 3C.
3. Whether the two duplicate pairs should stay as two rows each or collapse to
   one row with a count. They are two rows for now, because that is what the
   shelf holds.
