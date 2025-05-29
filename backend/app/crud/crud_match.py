from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload 
from typing import List, Optional 

from app.models.match import Match 
from app.models.team import Team 
from app.schemas.match import MatchCreate, MatchUpdate 

async def create_match(db: AsyncSession, match: MatchCreate) -> Match:
    """
    Skapa en ny match i databasen.
    """
    db_match = Match(
        match_date=match.match_date,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        home_score=match.home_score,
        away_score=match.away_score,
        league=match.league,
        season=match.season,
        status=match.status
    )
    db.add(db_match)
    await db.commit()
    await db.refresh(db_match)
    await db.refresh(db_match, attribute_names=['home_team', 'away_team'])
    return db_match

async def get_match(db: AsyncSession, match_id: int) -> Optional[Match]:
    """
    Hämta en specifik match baserat på dess ID, inklusive relaterad laginformation.
    """
    stmt = (
        select(Match)
        .options(
            selectinload(Match.home_team), 
            selectinload(Match.away_team) 
        )
        .filter(Match.id == match_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_matches(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[Match]: 
    """
    Hämta en lista med matcher, inklusive relaterad laginformation, med paginering.
    """
    stmt = (
        select(Match)
        .options(
            selectinload(Match.home_team), 
            selectinload(Match.away_team) 
        )
        .offset(skip)
        .limit(limit)
        .order_by(Match.match_date.desc()) 
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_match(
    db: AsyncSession, 
    db_match: Match, 
    match_in: MatchUpdate 
) -> Match:
    """
    Uppdatera en existerande match.
    """
    update_data = match_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_match, field, value)
            
    db.add(db_match)
    await db.commit()
    await db.refresh(db_match)
    await db.refresh(db_match, attribute_names=['home_team', 'away_team'])
    return db_match 

async def delete_match(db: AsyncSession, match_id: int) -> Optional[Match]:
    """
    Radera en match från databasen baserat på dess ID.
    Returnerar det raderade matchobjektet om det hittades, annars None.
    """
    db_match = await get_match(db=db, match_id=match_id) 
    if db_match:
        await db.delete(db_match) 
        await db.commit()        
        
        return db_match 
    return None 
