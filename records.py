"""The catalogue records a book is already tied to, and what they say.

`enrich` matched each book to an Open Library work and, where the imprint
allowed, to one edition of it. Those two records are the only ones the
subtitle, cover and validation passes are allowed to read from: nothing here
searches for a book again, so nothing here can find a *different* book. A
looser search is how a guess gets in.

Google Books is asked one question only: what volume carries this exact
ISBN. A result counts only if its own identifiers list that ISBN. On 1 Oct
2026 its structured search (`isbn:`, `intitle:`) returned nothing for any
book, keyed or not, and free text returned unrelated titles, so this side
currently contributes nothing; it starts contributing when Google answers
again, and the passes can simply be rerun. See log.md.

Responses are cached in work/ (gitignored) so a rerun is cheap and a run can
be audited against exactly what it read.
"""

import hashlib, json, re, struct, sys, time, urllib.parse, urllib.request
from pathlib import Path
from importlib.machinery import SourceFileLoader

HERE = Path(__file__).resolve().parent
E = SourceFileLoader("enrich", str(HERE / "enrich")).load_module()
CACHE = HERE / "work" / "records-cache.json"
PAUSE = 0.3

_cache = None


def _load():
    global _cache
    if _cache is None:
        try:
            _cache = json.loads(CACHE.read_text())
        except (OSError, ValueError):
            _cache = {}
    return _cache


def save():
    if _cache is not None:
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text(json.dumps(_cache))


def fetch(path):
    """An Open Library JSON record by key, through the cache."""
    c = _load()
    if path not in c:
        c[path] = E.get(f"https://openlibrary.org{path}.json")
        time.sleep(PAUSE)
    return c[path]


def google_by_isbn(isbn13):
    """The Google Books volume whose identifiers include this ISBN, or None.

    Cached under the ISBN, never under the request URL, so the API key never
    reaches the cache file. Only a hit is cached: Google answering "no such
    ISBN" for every book on the shelf is an outage, not an answer, and a rerun
    should ask again."""
    if not isbn13:
        return None
    c = _load().setdefault("_gb", {})
    if isbn13 in c:
        return c[isbn13]
    key = E.google_key()
    params = {"q": f"isbn:{isbn13}", "maxResults": 5}
    if key:
        params["key"] = key
    data = E.get("https://www.googleapis.com/books/v1/volumes?" + urllib.parse.urlencode(params))
    time.sleep(PAUSE)
    if data is None:
        return None
    hit = None
    for item in data.get("items") or []:
        vi = item.get("volumeInfo") or {}
        ids = {i.get("identifier") for i in vi.get("industryIdentifiers") or []}
        if isbn13 in ids:
            hit = {k: vi.get(k) for k in ("title", "subtitle", "authors", "publisher",
                                          "publishedDate", "imageLinks")}
            break
    if hit:
        c[isbn13] = hit
    return hit


def record(book):
    """{'ed', 'work', 'authors'} for the records this book is tied to."""
    ed = fetch(book["ol_edition"]) if book.get("ol_edition") else None
    work = fetch(book["ol_work"]) if book.get("ol_work") else None
    keys = [a.get("key") for a in (ed or {}).get("authors") or []]
    if not keys:
        keys = [(a.get("author") or {}).get("key") for a in (work or {}).get("authors") or []]
    names = []
    for k in filter(None, keys):
        a = fetch(k) or {}
        names += [a.get("name"), a.get("personal_name")]
    return {"ed": ed, "work": work, "authors": [n for n in names if n],
            "gb": google_by_isbn(book.get("isbn13"))}


def editions(work_key):
    """Every edition Open Library lists for a work (first 50)."""
    data = fetch(f"{work_key}/editions") if work_key and work_key.endswith("W") else None
    return (data or {}).get("entries") or []


# --- titles ----------------------------------------------------------------

SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "into",
         "nor", "of", "on", "or", "over", "per", "the", "to", "vs", "via", "with"}

# Genre labels Open Library files as a subtitle. They are on the jacket, but
# they say what kind of book it is, not what this one is called.
GENRE = {"novel", "a novel", "memoir", "a memoir", "stories", "poems", "essays",
         "a novella", "novella", "a play"}


def titlecase(s):
    """Open Library stores many titles in library style ("the making of the
    modern identity"). A string that starts lowercase is recased word by word,
    keeping any capitals already inside a word (neo-Luddite, Internet). Short
    connecting words go lowercase mid-title either way, so "The Social Virtues
    and The Creation of Prosperity" reads the way the jacket does."""
    if not s:
        return s
    words = s.split(" ")
    recase = s[:1].islower() or (len(words) > 2 and not any(w[:1].isupper() for w in words[1:]))
    out = []
    for i, w in enumerate(words):
        lead = i == 0 or out[-1].endswith((":", "\u2014"))
        bare = w.lower().strip(",;")
        if not lead and i < len(words) - 1 and bare in SMALL:
            out.append(w.lower())
        elif recase:
            out.append(w[:1].upper() + w[1:])
        else:
            out.append(w)
    return " ".join(out)


def clean(s):
    """Drop a trailing series label, edition note or stray punctuation."""
    if not s:
        return None
    s = re.sub(r"\s*\([^)]*\)\s*$", "", s.strip())   # "(Delta Fiction)"
    s = re.sub(r"[\s.;,/:]+$", "", s)
    s = s.replace("--", "\u2014")
    return s or None


def split(title):
    """'Social origins of dictatorship and democracy: lord and peasant...'
    -> ('Social origins of dictatorship and democracy', 'lord and peasant...')"""
    t = clean(title) or ""
    if ":" in t:
        main, sub = t.split(":", 1)
        return main.strip(), clean(sub)
    return t, None


def offered(rec_json):
    """(title, subtitle) as one record states them."""
    if not rec_json:
        return None, None
    main, from_title = split(rec_json.get("title"))
    sub = clean(rec_json.get("subtitle")) or from_title
    if sub and E.norm(sub) in GENRE:
        sub = None
    return main or None, titlecase(sub)


def propose_title(book, rec):
    """A fuller title, but only where the edition and the work both give the
    same longer one and ours is part of it. The spine is where we read the
    title, and a spine leaves words off ("Bubble or Revolution?" under a
    small "Blockchain"); one record saying so is not enough to change it."""
    et, _ = offered(rec["ed"])
    wt, _ = offered(rec["work"])
    if not et or not wt or E.norm(et) != E.norm(wt):
        return None
    ours, theirs = E.norm(book["title"]), E.norm(et)
    if ours == theirs or ours not in theirs:
        return None
    new = titlecase(et)
    if book["title"][-1:] in "?!" and new[-1:] not in "?!":
        new += book["title"][-1]
    return new


def full(title, subtitle):
    """'Davos Man: How the Billionaires...'; a title ending in ? or ! takes
    no colon. Mirrors fullTitle() in the two page templates."""
    if not subtitle:
        return title
    return f"{title} {subtitle}" if title[-1:] in "?!" else f"{title}: {subtitle}"


# --- subtitles -------------------------------------------------------------

def propose_subtitle(book, rec):
    """('fill', subtitle, source) | ('ask', question, None) | ('none', why, None)

    The edition is the printing on the shelf; the work is every printing at
    once. Where both state a subtitle and they disagree, the edition wins only
    if the spine can't tell them apart either - otherwise the spine decides.
    A work subtitle is used alone only when the edition states none, and only
    when the work's title is the same title we hold.
    """
    et, es = offered(rec["ed"])
    wt, ws = offered(rec["work"])
    spine = E.norm(book.get("spine"))

    def same_title(t):
        return t and E.title_score(book["title"], t) == 1.0

    ed_ok = es and same_title(et)
    wk_ok = ws and same_title(wt)
    if ed_ok and wk_ok and E.norm(es) != E.norm(ws):
        on_spine = [s for s in (es, ws) if E.norm(s) and E.norm(s) in spine]
        if len(on_spine) == 1:
            return "fill", on_spine[0], "spine agrees with " + ("edition" if on_spine[0] == es else "work")
        if E.norm(es) in E.norm(ws) or E.norm(ws) in E.norm(es):
            return "fill", es, "edition"
        return ("ask", f"Subtitle: the matched edition says \"{es}\", the work says "
                f"\"{ws}\". Which is printed on this copy?", None)
    if ed_ok:
        return "fill", es, "edition"
    if wk_ok and rec["ed"]:
        return "fill", ws, "work"
    if wk_ok:
        # No printing tied, so the work's subtitle stands only if every
        # printing on record carries it. Pure War's 2008 reissue added
        # "Twenty Five Years Later"; the 1997 one has no subtitle at all.
        eds = editions(book.get("ol_work"))
        subs = {E.norm(offered(e)[1] or "") for e in eds}
        if eds and subs == {E.norm(ws)}:
            return "fill", ws, f"work (all {len(eds)} editions agree)"
        if eds:
            return ("ask", f"Subtitle: some printings of this book are subtitled \"{ws}\" "
                    "and some are not. Is it on this copy?", None)
        return "fill", ws, "work"
    if not rec["ed"] and not rec["work"]:
        return "none", "no matched record", None
    return "none", "matched record states no subtitle", None


# --- covers ----------------------------------------------------------------

def _dims(data):
    """Pixel size from the header of a JPEG, PNG or GIF, else None."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return struct.unpack("<HH", data[6:10])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


MIN_SIDE = 40   # Open Library's "no cover" answer is a 1x1 GIF


# Some "covers" on Open Library are themselves an uploaded "No image
# available" graphic, a full-size image that passes every other test. Known
# ones are listed by md5 of the bytes; add to this when one turns up.
PLACEHOLDER_MD5 = {
    "681e43bb536038b0ecb97ed0c13b5948",  # Amazon's "No image available" (OL cover 11224707)
}


def check_image(url):
    """(ok, detail). Real means 200, an image type, and a plausible size."""
    if not url.startswith("https://"):
        return (False, "not https")
    c = _load().setdefault("_img", {})
    if url in c:
        return tuple(c[url])
    req = urllib.request.Request(url, headers={"User-Agent": E.UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            ctype = r.headers.get("Content-Type", "")
            data = r.read()
    except Exception as e:
        res = (False, f"{type(e).__name__}: {getattr(e, 'code', '')}".strip(": "))
    else:
        d = _dims(data) if ctype.startswith("image/") else None
        if not d:
            res = (False, f"not an image ({ctype}, {len(data)} bytes)")
        elif min(d) < MIN_SIDE:
            res = (False, f"placeholder {d[0]}x{d[1]}")
        elif hashlib.md5(data).hexdigest() in PLACEHOLDER_MD5:
            res = (False, "known placeholder image")
        else:
            res = (True, f"{d[0]}x{d[1]}")
    # Covers by ISBN are rate-limited (100 per 5 minutes); covers by id are not.
    time.sleep(3.1 if "/isbn/" in url else PAUSE)
    c[url] = list(res)
    return res


def cover_candidates(book, rec):
    """Edition covers first, then the ISBN, then the work. Each one names
    where it came from, so the choice is auditable."""
    out = []
    for cid in (rec["ed"] or {}).get("covers") or []:
        if isinstance(cid, int) and cid > 0:
            out.append((f"https://covers.openlibrary.org/b/id/{cid}-M.jpg", "edition"))
    if book.get("isbn13"):
        out.append((f"https://covers.openlibrary.org/b/isbn/{book['isbn13']}-M.jpg?default=false", "isbn"))
    thumb = ((rec.get("gb") or {}).get("imageLinks") or {}).get("thumbnail")
    if thumb:
        thumb = thumb.replace("http://", "https://").replace("&edge=curl", "")
        out.append((thumb, "google books (isbn)"))
    for cid in (rec["work"] or {}).get("covers") or []:
        if isinstance(cid, int) and cid > 0:
            out.append((f"https://covers.openlibrary.org/b/id/{cid}-M.jpg", "work"))
    # urlopen also opens file:// and ftp://, so only https ever reaches check_image.
    return [(u, src) for u, src in out if isinstance(u, str) and u.startswith("https://")]


assert cover_candidates({}, {"ed": None, "work": None, "gb": {"imageLinks": {"thumbnail": "file:///etc/passwd"}}}) == []


# --- validation ------------------------------------------------------------

def isbn13_ok(s):
    if not s or not re.fullmatch(r"97[89]\d{10}", s):
        return False
    total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(s[:12]))
    return (10 - total % 10) % 10 == int(s[12])


def isbn10_to_13(s):
    s = (s or "").replace("-", "")
    if not re.fullmatch(r"\d{9}[\dXx]", s):
        return None
    core = "978" + s[:9]
    total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(core))
    return core + str((10 - total % 10) % 10)


NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
           "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


def volume(text):
    """'Saga, Volume Ten' -> 10. Only an explicit vol/volume/book marker."""
    m = re.search(r"\b(?:vol(?:ume)?|book)\.?\s+(\d+|" + "|".join(NUMBERS) + r")\b",
                  (text or "").lower())
    if not m:
        return None
    v = m.group(1)
    return int(v) if v.isdigit() else NUMBERS[v]


def check(book, rec):
    """Every disagreement between our row and its matched records.

    Returns (field, ours, theirs, source, severity). severity is 'error'
    when the matched edition itself contradicts the spine (the tie is
    wrong), 'doubt' when sources disagree and nothing here can settle it,
    'info' for differences of form that change nothing.
    """
    out = []
    ed, work = rec["ed"], rec["work"]
    et, es = offered(ed)
    wt, ws = offered(work)
    # Square brackets mark letters guessed through a crease on the spine.
    spine = E.norm(re.sub(r"[\[\]]", "", book.get("spine") or ""))

    # title
    for t, src in ((et, "edition"), (wt, "work")):
        if not t:
            continue
        s = E.title_score(book["title"], t)
        if s == 0:
            out.append(("title", book["title"], t, src, "doubt"))
        elif s < 1:
            out.append(("title", book["title"], t, src, "info"))

    # subtitle we already hold
    if book.get("subtitle"):
        for s, src in ((es, "edition"), (ws, "work")):
            if s and E.norm(s) != E.norm(book["subtitle"]):
                out.append(("subtitle", book["subtitle"], s, src, "info"))

    # authors
    if rec["authors"]:
        ok = E.author_ok(book.get("authors"), rec["authors"])
        if ok is False:
            out.append(("authors", book.get("authors"), "; ".join(rec["authors"]), "author record", "doubt"))

    if ed:
        y = E.year_of(ed.get("publish_date"))
        if y and book.get("year") and y != book["year"]:
            out.append(("year", book["year"], y, "edition", "doubt"))
        pubs = ed.get("publishers") or []
        if book.get("publisher") and pubs and not E.pub_match(book["publisher"], pubs):
            out.append(("publisher", book["publisher"], "; ".join(pubs), "edition", "doubt"))
        isbns = set(ed.get("isbn_13") or []) | {isbn10_to_13(i) for i in ed.get("isbn_10") or []}
        isbns.discard(None)
        if book.get("isbn13") and isbns and book["isbn13"] not in isbns:
            out.append(("isbn13", book["isbn13"], "; ".join(sorted(isbns)), "edition", "doubt"))
        sv = _spine_volume(book.get("spine"))
        ev = volume(f"{ed.get('title')} {ed.get('subtitle') or ''}")
        if sv and ev and sv != ev:
            out.append(("edition", f"spine vol {sv}", f"{ed.get('title')} (vol {ev})", "edition", "error"))

    if book.get("year") and book.get("ol_first_year") and book["year"] < book["ol_first_year"]:
        out.append(("year", book["year"], f"first published {book['ol_first_year']}", "work", "doubt"))

    # The spine is the observation everything else hangs off. Author and
    # imprint usually appear on it; where the spine names neither the
    # author we hold nor the publisher, that is worth a look, not a verdict.
    toks = set(spine.split())
    names = E.surnames(book.get("authors"))
    if spine and names and not names & toks:
        out.append(("authors", book.get("authors"), book.get("spine"), "spine", "info"))
    marks = E.imprint(book.get("publisher"))
    if spine and marks and not marks & toks:
        out.append(("publisher", book.get("publisher"), book.get("spine"), "spine", "info"))

    gb = rec.get("gb")
    if gb and gb.get("title") and E.title_score(book["title"], gb["title"]) == 0:
        out.append(("isbn13", book["isbn13"], f"Google Books files it as {gb['title']!r}",
                    "google books", "doubt"))

    if book.get("isbn13") and not isbn13_ok(book["isbn13"]):
        out.append(("isbn13", book["isbn13"], "bad checksum", "arithmetic", "error"))

    # spine: every meaningful word of the title should be on it
    words = [w for w in E.norm(book["title"]).split() if w not in SMALL and len(w) > 2]
    missing = [w for w in words if w not in spine.split()]
    if spine and words and len(missing) > len(words) / 2:
        out.append(("title", book["title"], book.get("spine"), "spine", "doubt"))
    return out


def _spine_volume(spine):
    """A bare number segment on the spine ('... / 7') or 'vol 7'."""
    for seg in (spine or "").split("/"):
        seg = seg.strip()
        if re.fullmatch(r"\d{1,2}", seg):
            return int(seg)
    return volume(spine)


# --- passes ----------------------------------------------------------------

def connect():
    import sqlite3
    con = sqlite3.connect(E.DB)
    con.row_factory = sqlite3.Row
    return con


def ask(con, book, question):
    """Park a book at needs_input with a question, keeping any question it
    already had. A confirmed row is Mo's word and is left alone."""
    if book["status"] == "confirmed":
        return False
    old = book.get("question") or ""
    if question in old:
        return False
    q = f"{old} | {question}" if old else question
    con.execute("UPDATE books SET status='needs_input', question=? WHERE id=?", (q, book["id"]))
    book["status"], book["question"] = "needs_input", q
    return True


def note(con, book, text):
    old = book.get("notes") or ""
    if text in old:
        return
    n = f"{old} | {text}" if old else text
    con.execute("UPDATE books SET notes=? WHERE id=?", (n, book["id"]))
    book["notes"] = n


def subtitles_pass():
    """Fill subtitles, and complete cut-off titles, from the matched records.

    Idempotent: a book with a subtitle is never rewritten (that subtitle was
    read off the spine, or by an earlier run of this), and a title is only
    lengthened when the edition and the work agree on the longer one.
    """
    con = connect()
    rows = [dict(r) for r in con.execute("SELECT * FROM books ORDER BY id")]
    filled = titled = asked = 0
    for b in rows:
        if b["status"] == "confirmed":
            continue
        rec = record(b)
        new = propose_title(b, rec)
        if new:
            print(f"[{b['id']:>3}] title  {b['title']!r} -> {new!r}  (edition + work)")
            note(con, b, f"title was \"{b['title']}\" as read off the spine; "
                         f"the matched edition and work both give \"{offered(rec['ed'])[0]}\"")
            con.execute("UPDATE books SET title=? WHERE id=?", (new, b["id"]))
            b["title"] = new
            titled += 1
        if b["subtitle"]:
            continue
        kind, val, src = propose_subtitle(b, rec)
        if kind == "fill":
            print(f"[{b['id']:>3}] sub    {val!r}  ({src})")
            con.execute("UPDATE books SET subtitle=? WHERE id=?", (val, b["id"]))
            filled += 1
        elif kind == "ask" and ask(con, b, val):
            print(f"[{b['id']:>3}] ask    {val}")
            asked += 1
        con.commit()
    con.commit()
    save()
    print(f"\ndone: {filled} subtitles filled, {titled} titles completed, {asked} questions raised")


def covers_pass():
    """Give every book a cover that is really there, from its own printing.

    Order: the matched edition's covers, then its ISBN, then the work's. An
    existing cover is kept unless it fails to load, or the book is tied to an
    edition by imprint and that edition has a cover of its own - the work
    search that set the first covers picks whichever printing it likes, and
    a Saga volume came out wearing another volume's cover that way.
    """
    con = connect()
    rows = [dict(r) for r in con.execute("SELECT * FROM books ORDER BY id")]
    added = swapped = dropped = 0
    for b in rows:
        rec = record(b)
        cands = cover_candidates(b, rec)
        cur = b["cover_url"]
        keep = cur and check_image(cur)[0]
        prefer_edition = b.get("edition_match") == "publisher" and any(s == "edition" for _, s in cands)
        if keep and not (prefer_edition and cur not in [u for u, s in cands if s == "edition"]):
            continue
        pick = None
        for url, src in cands:
            ok, detail = check_image(url)
            if ok:
                pick = (url, src, detail)
                break
        if not pick:
            if cur and not keep:
                con.execute("UPDATE books SET cover_url=NULL WHERE id=?", (b["id"],))
                dropped += 1
                print(f"[{b['id']:>3}] drop   {cur} (does not load)")
            continue
        if pick[0] == cur:
            continue
        con.execute("UPDATE books SET cover_url=? WHERE id=?", (pick[0], b["id"]))
        if cur:
            swapped += 1
        else:
            added += 1
        print(f"[{b['id']:>3}] {'swap ' if cur else 'add  '}  {pick[0]}  ({pick[1]}, {pick[2]})")
        con.commit()
    con.commit()
    save()
    print(f"\ndone: {added} covers added, {swapped} replaced with the edition's own, {dropped} dropped")
