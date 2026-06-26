from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.base import Base
from app.models import Document, Message, SupportSession, User  # noqa: F401 - registers models

settings = get_settings()
engine = create_async_engine(settings.database_url, pool_pre_ping=True, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create tables and seed a demo user.

    For a portfolio project, auto-create keeps the demo friction low. In production,
    replace this with Alembic migrations. Recruiters will survive this compromise.
    """
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(User).where(User.id == settings.demo_user_id))
        if existing is None:
            session.add(
                User(
                    id=settings.demo_user_id,
                    email="demo.customer@example.com",
                    full_name="Demo Customer",
                )
            )
            await session.commit()
