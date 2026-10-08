import json
from pathlib import Path
from sqlalchemy import text
from src.db.connection import get_engine

SEED = Path("data/seed/documents.json")

UPSERT_DOC = text("""
INSERT INTO documents
 (doc_id, title, domain, doc_type, issue_date, effective_date, status,
  repeal_date, applies_to, source_url, file_path)
VALUES
 (:doc_id, :title, :domain, :doc_type, :issue_date, :effective_date, :status,
  :repeal_date, :applies_to, :source_url, :file_path)
ON DUPLICATE KEY UPDATE
  title=VALUES(title), domain=VALUES(domain), doc_type=VALUES(doc_type),
  issue_date=VALUES(issue_date), effective_date=VALUES(effective_date),
  status=VALUES(status), repeal_date=VALUES(repeal_date),
  applies_to=VALUES(applies_to), source_url=VALUES(source_url),
  file_path=VALUES(file_path)
""")

INSERT_REL = text("""
INSERT INTO document_relations (new_doc_id, old_doc_id, relation_type, note)
VALUES (:new_doc_id, :old_doc_id, :relation_type, :note)
""")


def main():
    data = json.loads(SEED.read_text(encoding="utf-8"))
    engine = get_engine()

    for d in data["documents"]:
        if not Path(d["file_path"]).exists():
            print(f"WARNING: PDF missing for {d['doc_id']}: {d['file_path']}")

    with engine.begin() as conn:
        for d in data["documents"]:
            conn.execute(UPSERT_DOC, d)
        conn.execute(text("DELETE FROM document_relations"))
        for r in data["relations"]:
            conn.execute(INSERT_REL, r)

        rows = conn.execute(text(
            "SELECT doc_id, status, issue_date, repeal_date FROM documents ORDER BY domain, issue_date"
        )).fetchall()

    print("\nDocuments in registry:")
    for r in rows:
        print(" ", r)


if __name__ == "__main__":
    main()