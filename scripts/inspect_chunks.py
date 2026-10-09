import sys
from collections import Counter
from sqlalchemy import text
from src.db.connection import get_engine
from src.ingestion.parse import extract_blocks
from src.ingestion.chunk import clean


def show_chunks(doc_id, n=4):
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT chunk_id, page_start, para_no, char_count, content "
            "FROM chunks WHERE doc_id=:d ORDER BY chunk_index LIMIT 40"
        ), {"d": doc_id}).fetchall()
        path = conn.execute(text(
            "SELECT file_path FROM documents WHERE doc_id=:d"), {"d": doc_id}).scalar()

    print(f"\n=== {doc_id}: sample chunks (from chunks 10-{9+n}) ===")
    for r in rows[10:10 + n]:
        print(f"\n[{r[0]}] page={r[1]} para={r[2]} chars={r[3]}")
        print(r[4][:500])

    print(f"\n=== {doc_id}: repeated text (likely headers/footers) ===")
    blocks = extract_blocks(path)
    pages_per_text = {}
    for page, raw in blocks:
        t = clean(raw)
        if len(t) < 150:
            pages_per_text.setdefault(t, set()).add(page)
    repeated = sorted(((len(p), t) for t, p in pages_per_text.items() if len(p) >= 4),
                      reverse=True)
    for count, t in repeated[:8]:
        print(f"  on {count} pages: {t!r}")
    if not repeated:
        print("  none found")


if __name__ == "__main__":
    show_chunks(sys.argv[1] if len(sys.argv) > 1 else "PA-2025")