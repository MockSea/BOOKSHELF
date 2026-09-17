# library

Cataloging the books on Mo's shelves from photographs.

```
library/
  catalog             CLI over the database
  schema.sql          the schema, with the reasoning in comments
  catalog.db          SQLite, tracked - the source of truth
  photos/             shelf photos as sent (gitignored)
  exports/            generated JSON/CSV for whatever comes next
  enrich              Open Library: the work, then the printing on the shelf
  enrich-retry        re-runs the misses with looser matching
  render              catalog.db -> docs/index.html  (the public site)
  render-swipe        catalog.db -> swipe.html       (private verification)
  apply-verdicts      swipe verdicts -> catalog.db
  docs/               what GitHub Pages serves; generated, committed
```

## The rule

No title gets entered as a guess. If a spine is blurred, cropped, angled past
reading, or two editions are equally plausible, the row goes in as
`status=needs_input` with a `question` written on it, and Mo gets asked.

`./catalog open` prints every one of those with the question attached, so the
questions arrive in a batch rather than one text at a time.

## Status values

| status        | means |
|---------------|-------|
| `unverified`  | read cleanly off the spine, nothing has checked it since |
| `needs_input` | I can't resolve it; `question` says what I need |
| `confirmed`   | Mo confirmed it, or it was checked against a catalog record |

`spine` holds what the photo actually shows, verbatim. Every other field is
inference from that, which is why the two are separate columns.

## Enrichment

```sh
./enrich              # match each book to an Open Library work, then to an edition
./enrich --editions   # only the edition pass, for books already matched to a work
./enrich-retry        # re-run the misses with looser matching
```

Two lookups, because a shelf holds an *edition* and the obvious lookup answers
about the *work*. Year, ISBN, binding and page count are properties of a
printing, and Open Library's work search carries none of them - which is why
`year` and `isbn13` sat empty on every row while subjects and covers filled in.

An edition is only tied to a book when its imprint agrees with what the spine
says: "Custom House" picks one of Davos Man's three editions and leaves the two
HarperCollins ebook records alone. Where nothing agrees, the pass writes
nothing and the record view says why. A year taken off the wrong printing is
exactly the guess the `status` column exists to prevent, and the three times a
looser rule was tried it produced a dissertation microfilm, a large-print
reprint, and a hardcover ISBN on a paperback.

Every write is `COALESCE`d against what is already there, so a reading off the
photograph and a verdict from Mo both outrank a catalogue.

Summaries are the one real gap. They come from the work record's `description`,
and most Open Library work records have none. Google Books has them and rejects
every unauthenticated request with a 429, so closing that gap needs an API key.

## Commands

```sh
./catalog photo ~/path/to/shelf.heic --shelf "living room, top"
./catalog add title="Dune" authors="Herbert, Frank" photo_id=1 shelf="living room, top" position=3
./catalog set 12 year=1965 publisher="Ace" status=confirmed
./catalog confirm 12 13 14
./catalog list --status needs_input
./catalog open
./catalog stats
./catalog export --format json
```

## Where the photos come from

A Google Drive folder, `BOOKSHELF`, shared privately with me - the folder ids
are not in this repo. Mo uploads into `NEW/`; once a photo's books are in the database the image moves
to `SORTED/`, so the two folders are the work queue. Every photo processed gets
an entry in `log.md`.

## The page

Live at <https://mocksea.github.io/BOOKSHELF/>.

GitHub Pages serves the `docs/` folder off `main`, so the published site is
exactly what was last pushed. The loop is two commands and a push:

```sh
./render          # catalog.db -> docs/index.html
git add -A && git commit -m "catalog: <what changed>" && git push
```

`catalog.db` is committed alongside the page it generated, which is the point:
the database and the site move together, and the repo's history is the history
of the shelf. A rendered page is a snapshot, so a commit that changes the
database without re-running `./render` publishes a stale site. Do both.

`TARGET` in `render` is the denominator on the progress meter. Mo set it to 60.

The photos themselves stay out of the repo (`photos/` is ignored). The
catalogue is public; pictures of someone's living room are not.

`bookshelf.template.html` is a fragment with no `<html>` or `<head>`, because
that is the shape the artifact runtime wanted - it supplied the skeleton. Pages
supplies nothing, so `render` prepends its own: charset, viewport, and the
three reset rules the artifact wrapper used to give us. Without the viewport
meta a phone lays the page out at 980px and the 720px media query never fires,
which is exactly what happened on the first push.

That makes `docs/index.html` a complete document and therefore the wrong shape
to publish as an artifact. The old artifact at
<https://claude.ai/code/artifact/e377db7d-9cb4-426d-bb2c-c689f30e2c02> is
frozen at its last version and is no longer the live page.

## Verification

Verification does not happen on the public page. It happens on a second,
private artifact, **Shelf Check**
(<https://claude.ai/code/artifact/deaf3649-298b-459a-b7a6-47716c623213>), built
by `./render-swipe` from `swipe.template.html` the same way `render` builds
BOOKSHELF. One book per card: swipe right if the record is good, left if
something is off, with an optional note. Arrow keys and an undo do the same
job from a keyboard.

Verification stays an artifact and does not move to Pages. Pages is static
hosting - there is no server to write a verdict to, and the swipe portal needs
somewhere to put one. The artifact runtime's `db` capability is that
somewhere.

Two pages rather than one because of a second constraint: an artifact declaring
`db` (or `assets`, or full `comments`) is organization-internal and cannot be
shared publicly. BOOKSHELF is public and therefore declares no capabilities at
all — it is embedded JSON and nothing else. Shelf Check declares
`capabilities: {db: {}}` and stays private.

The loop back:

```sh
# Artifact tool: read_db, db_op=list, collection=verdicts, out_dir=<dir>
./apply-verdicts <dir>/verdicts
./render
# republish bookshelf.html to the same URL
```

`ok` sets `status=confirmed`. `off` sets `status=needs_input` and parks the note
in `question` — it never rewrites a field, because the note says something is
wrong, not what the right answer is. That still comes from asking Mo.

## Contributor

`contributor` records who owns the physical copy, not who wrote it. Everything
on shelf 1 is TNK's.
