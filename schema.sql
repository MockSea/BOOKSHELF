-- Shelf catalog.
--
-- The split that matters here: `spine` on a book row is what I could actually
-- read off the photo, verbatim. Everything else in the row is inference from
-- it, and `status` says how far that inference has been checked. Keeping the
-- observation separate from the resolution is the whole reason this is a
-- table and not a list of titles.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS photos (
  id          INTEGER PRIMARY KEY,
  path        TEXT NOT NULL UNIQUE,   -- relative to library/
  shelf       TEXT,                   -- whatever Mo calls this shelf or unit
  received_at TEXT NOT NULL DEFAULT (datetime('now')),
  note        TEXT
);

CREATE TABLE IF NOT EXISTS books (
  id           INTEGER PRIMARY KEY,

  -- the observation
  spine        TEXT,                  -- verbatim, as printed on the spine
  photo_id     INTEGER REFERENCES photos(id) ON DELETE SET NULL,
  shelf        TEXT,
  position     INTEGER,               -- left to right within that photo

  -- the resolution
  title        TEXT NOT NULL,
  subtitle     TEXT,
  authors      TEXT,                  -- "Last, First; Last, First"
  publisher    TEXT,
  year         INTEGER,
  edition      TEXT,
  isbn13       TEXT,
  isbn10       TEXT,
  format       TEXT,                  -- hardcover | paperback | boxed | other
  language     TEXT DEFAULT 'en',
  series       TEXT,
  series_index TEXT,
  contributor  TEXT,                  -- who owns this physical copy

  -- how much to trust the row
  status       TEXT NOT NULL DEFAULT 'unverified'
                 CHECK (status IN ('unverified','needs_input','confirmed')),
  confidence   REAL,                  -- 0..1, my read of the spine itself
  question     TEXT,                  -- what I need Mo to answer, if anything
  notes        TEXT,

  created_at   TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at   TEXT NOT NULL DEFAULT (datetime('now')),

  -- What a catalogue lookup added, kept apart from what the photo said. Two
  -- lookups, because a shelf holds an *edition* and the first lookup answers
  -- about the *work*: `ol_work` is the book Open Library thinks this is, and
  -- `ol_edition` is the printing, tied by matching the imprint on the spine.
  -- Nothing below ever overwrites a column above it; `enrich` COALESCEs, so a
  -- reading off the photograph and a verdict from Mo both outrank a catalogue.
  summary          TEXT,     -- the work's own description, where it has one
  subjects         TEXT,     -- "Fiction; Economics", semicolon-separated
  page_count       INTEGER,  -- of the matched edition, not of the work
  cover_url        TEXT,
  ol_work          TEXT,     -- /works/OL...W
  ol_first_year    INTEGER,  -- first publication of the work, any edition
  ol_isbn13        TEXT,     -- what the *work* search returned; see note below
  ol_edition       TEXT,     -- /books/OL...M, the printing on this shelf
  edition_match    TEXT,     -- how it was tied: 'publisher' | 'sole'
  enrich_source    TEXT,     -- 'openlibrary', 'none', or a '+' join
  enrich_confidence REAL,
  enriched_at      TEXT
);

-- `ol_isbn13` is deliberately not `isbn13`. It is whatever ISBN the work-level
-- search happened to surface, which belongs to some printing and not
-- necessarily this one. `isbn13` is only written from a matched edition.

CREATE INDEX IF NOT EXISTS books_status_idx ON books(status);
CREATE INDEX IF NOT EXISTS books_shelf_idx  ON books(shelf, position);
CREATE INDEX IF NOT EXISTS books_author_idx ON books(authors);
CREATE UNIQUE INDEX IF NOT EXISTS books_isbn13_idx ON books(isbn13) WHERE isbn13 IS NOT NULL;

CREATE TRIGGER IF NOT EXISTS books_touch AFTER UPDATE ON books
BEGIN
  UPDATE books SET updated_at = datetime('now') WHERE id = NEW.id;
END;
