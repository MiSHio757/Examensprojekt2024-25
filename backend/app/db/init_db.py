import asyncio
from app.db.base_class import Base 
from app.db.session import async_engine 
from app.models.team import Team 
from app.models.match import Match 

async def init_db():
    async with async_engine.begin() as conn:
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all) 
        print("Tables created (if they didn't exist).")

if __name__ == "__main__":
    print("Initializing database...")
    # Hantera eventloopen korrekt
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError: 
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(init_db())
    print("Database initialization finished.")