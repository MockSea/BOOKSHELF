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
  updated_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS books_status_idx ON books(status);
CREATE INDEX IF NOT EXISTS books_shelf_idx  ON books(shelf, position);
CREATE INDEX IF NOT EXISTS books_author_idx ON books(authors);
CREATE UNIQUE INDEX IF NOT EXISTS books_isbn13_idx ON books(isbn13) WHERE isbn13 IS NOT NULL;

CREATE TRIGGER IF NOT EXISTS books_touch AFTER UPDATE ON books
BEGIN
  UPDATE books SET updated_at = datetime('now') WHERE id = NEW.id;
END;
