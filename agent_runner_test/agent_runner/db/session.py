from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from agent_runner.config import settings


engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
