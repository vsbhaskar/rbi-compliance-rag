from pathlib import Path
from sqlalchemy import text
from src.db.connection import get_engine


def init_db():
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    statements = [s.strip() for s in schema.split(";") if s.strip()]
    engine = get_engine()
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        tables = conn.execute(text("SHOW TABLES")).fetchall()
    print("Tables in database:", [t[0] for t in tables])


if __name__ == "__main__":
    init_db()