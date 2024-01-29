from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from config.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # noqa

Base = declarative_base()


async def get_db() -> Session:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            session.close()
