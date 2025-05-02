from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate

# Funktion för att hämta ett lag baserat på ID
async def get_team(db: AsyncSession, team_id: int) -> Team | None:
    result = await db.execute(select(Team).filter(Team.id == team_id))
    return result.scalar_one_or_none()

# Funktion för att hämta ett lag baserat på namn (bra för att undvika dubbletter)
async def get_team_by_name(db: AsyncSession, name: str) -> Team | None:
    result = await db.execute(select(Team).filter(Team.name == name))
    return result.scalar_one_or_none()

# Funktion för att hämta en lista med lag (med paginering)
async def get_teams(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Team]:
    result = await db.execute(select(Team).offset(skip).limit(limit))
    return result.scalars().all() # Använd .scalars() för att få ORM-objekten

# Funktion för att skapa ett nytt lag
async def create_team(db: AsyncSession, team: TeamCreate) -> Team:
    db_team = Team(**team.model_dump()) 
    db.add(db_team) 
    await db.commit() 
    await db.refresh(db_team) 
    return db_team