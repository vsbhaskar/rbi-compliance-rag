from pathlib import Path
from sqlalchemy import text
from src.db.connection import get_engine
from src.ingestion.parse import extract_blocks
from src.ingestion.chunk import chunk_blocks

INSERT = text("""
INSERT INTO chunks
 (chunk_id, doc_id, chunk_index, page_start, para_no, section_title, content, char_count)
VALUES
 (:chunk_id, :doc_id, :chunk_index, :page_start, :para_no, :section_title, :content, :char_count)
""")


def main():
    engine = get_engine()
    with engine.begin() as conn:
        docs = conn.execute(text("SELECT doc_id, file_path FROM documents")).fetchall()

    for doc_id, file_path in docs:
        if not file_path or not Path(file_path).exists():
            print(f"Skipping {doc_id}: PDF not found")
            continue
        print(f"Ingesting {doc_id} ...")
        blocks = extract_blocks(file_path)
        chunks = chunk_blocks(doc_id, blocks)
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM chunks WHERE doc_id = :d"), {"d": doc_id})
            if chunks:
                conn.execute(INSERT, chunks)
        avg = sum(c["char_count"] for c in chunks) // max(len(chunks), 1)
        print(f"  {len(chunks)} chunks, average {avg} characters")


if __name__ == "__main__":
    main()