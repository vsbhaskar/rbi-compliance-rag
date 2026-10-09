import re
import sys
from sqlalchemy import text
from src.db.connection import get_engine
from src.ingestion.parse import extract_blocks

GLUED = re.compile(r"(?<![\w.,])\d{1,2}(?=[“‘\"']?[A-Z][a-z])")


def main(doc_id):
    engine = get_engine()
    with engine.connect() as conn:
        path = conn.execute(text("SELECT file_path FROM documents WHERE doc_id=:d"),
                            {"d": doc_id}).scalar()
        rows = conn.execute(text(
            "SELECT para_no, content FROM chunks WHERE doc_id=:d ORDER BY chunk_index"),
            {"d": doc_id}).fetchall()

    _, removed = extract_blocks(path, return_removed=True)
    print(f"\n{doc_id}: removed {len(removed)} page-number/header/footer blocks")
    for t in sorted(set(removed))[:8]:
        print("  removed:", repr(t[:80]))

    seq = [r[0] for r in rows]
    print("para sequence (first 60):", seq[:60])
    print("chunks without para_no:", sum(1 for p in seq if p is None), "of", len(seq))
    print("glued footnote markers left:", sum(len(GLUED.findall(r[1])) for r in rows))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "PA-2025")