from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from farmlink.config import settings


class Base(DeclarativeBase):
    pass


def make_engine(url):
    kwargs = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **kwargs)


engine = make_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db():
    """Apply versioned Alembic migrations; safe to call on app startup."""
    if settings.DATABASE_URL.startswith("sqlite:///"):
        path = settings.DATABASE_URL.replace("sqlite:///", "", 1)
        if path != ":memory:":
            db_path = Path(path)
            if not db_path.is_absolute():
                db_path = Path(__file__).resolve().parent.parent / db_path
            db_path.parent.mkdir(parents=True, exist_ok=True)
    from alembic import command
    from alembic.config import Config
    from farmlink import models  # noqa: F401 - register model metadata for migrations
    project_dir = Path(__file__).resolve().parent.parent
    migration_config = Config(str(project_dir / "alembic.ini"))
    migration_config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))
    command.upgrade(migration_config, "head")


def get_session():
    return SessionLocal()
