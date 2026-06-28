"""
Creates all tables in the configured PostgreSQL database.

Usage:
    python init_db.py

This is the simplest way to get the schema into a fresh database (e.g. a
free Neon/Supabase/Render Postgres instance). Alembic is also set up in
./alembic for teams that want versioned migrations going forward — to
switch to it, run `alembic revision --autogenerate -m "init"` once this
script's tables exist, then `alembic stamp head`.
"""

from app.db.session import Base, engine
import app.models  # noqa: F401  (registers all models on Base.metadata)


def main() -> None:
    print(f"Creating tables on {engine.url.render_as_string(hide_password=True)} ...")
    Base.metadata.create_all(bind=engine)
    print("Done.")


if __name__ == "__main__":
    main()
