# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# Korrekt import från app/core/config.py
from app.core.config import settings 

# Skapa en asynkron SQLAlchemy engine
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URI,
    pool_pre_ping=True, # Kollar anslutningen innan användning
    # echo=True, # Avkommentera för att se SQL-frågor (bra för debugging)
)

# Skapa en asynkron session maker (fabrik för sessioner)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,      # Commits görs manuellt
    autoflush=False,       # Flush görs manuellt
    expire_on_commit=False # Objekt förblir tillgängliga efter commit
)

# Dependency för FastAPI för att få en DB-session i endpoints
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            
        except Exception:
            await session.rollback() 
            raise
        finally:
            # Sessionen stängs automatiskt av 'async with'
            pass