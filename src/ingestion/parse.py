import re
import pymupdf

PAGE_NO_RE = re.compile(r"^\s*(page\s*)?\d{1,3}(\s*(of|/)\s*\d{1,3})?\s*$", re.I)
# Footnote marker glued to the next word, e.g. "8Where" or "7“Controlling”"
FOOTNOTE_RE = re.compile(r"(?<![\w.,])\d{1,2}(?=[“‘\"']?[A-Z][a-z])")
# "non- bank" -> "non-bank"
HYPHEN_RE = re.compile(r"(\w)-\s+([a-z])")

FOOTNOTE_TEXT_RE = re.compile(
    r"^\s*\d{1,3}\s+(Amended|Inserted|Substituted|Deleted|Added|Omitted|Updated|Revised|Modified)\b",
    re.I,
)


def _norm(t: str) -> str:
    """Normalize text so page-specific digits don't hide repeated headers."""
    return re.sub(r"\d+", "#", re.sub(r"\s+", " ", t)).strip()


def extract_blocks(pdf_path: str, return_removed: bool = False):
    doc = pymupdf.open(pdf_path)
    raw = []
    empty_pages = 0
    for page_no, page in enumerate(doc, start=1):
        found = False
        for b in page.get_text("blocks", sort=True):
            if b[6] != 0:  # skip image blocks
                continue
            t = b[4].strip()
            if t:
                raw.append((page_no, t))
                found = True
        if not found:
            empty_pages += 1

    n_pages = len(doc)
    if empty_pages > n_pages * 0.3:
        print(f"  WARNING: {empty_pages}/{n_pages} pages have no text (scanned PDF? needs OCR)")

    # Find short texts that repeat on many pages (running headers/footers)
    pages_for = {}
    for page_no, t in raw:
        if len(t) < 120:
            pages_for.setdefault(_norm(t), set()).add(page_no)
    threshold = max(4, int(n_pages * 0.25))
    repeated = {k for k, p in pages_for.items() if len(p) >= threshold and len(k) >= 8}

    blocks, removed = [], []
    for page_no, t in raw:
        if (PAGE_NO_RE.match(t)
                or (len(t) < 120 and _norm(t) in repeated)
                or FOOTNOTE_TEXT_RE.match(t)):
            removed.append(t)
            continue
        t = FOOTNOTE_RE.sub("", t)
        t = HYPHEN_RE.sub(r"\1-\2", t)
        blocks.append((page_no, t))

    return (blocks, removed) if return_removed else blocks