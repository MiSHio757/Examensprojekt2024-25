from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List 

from app import schemas 
from app import crud    
from app.db.session import get_db 

router = APIRouter()

@router.post( 
    "/matches/", 
    response_model=schemas.match.MatchRead, 
    status_code=status.HTTP_201_CREATED
)
async def create_match_endpoint(
    match_in: schemas.match.MatchCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Skapa en ny match.
    Se till att team_id för home_team_id och away_team_id existerar i teams-tabellen.
    """
    home_team = await crud.team.get_team(db, team_id=match_in.home_team_id)
    if not home_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Home team with id {match_in.home_team_id} not found",
        )

    away_team = await crud.team.get_team(db, team_id=match_in.away_team_id)
    if not away_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Away team with id {match_in.away_team_id} not found",
        )

    if home_team.id == away_team.id:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Home team and away team cannot be the same.",
        )

    created_match = await crud.match.create_match(db=db, match=match_in)
    return created_match

@router.get("/matches/", response_model=List[schemas.match.MatchRead]) 
async def read_matches_endpoint(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    """
    Hämta en lista med matcher.
    """
    matches = await crud.match.get_matches(db=db, skip=skip, limit=limit)
    return matches

@router.get("/matches/{match_id}", response_model=schemas.match.MatchRead)
async def read_match_endpoint(
    match_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Hämta en specifik match med ID.
    """
    db_match = await crud.match.get_match(db=db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return db_match

@router.put("/matches/{match_id}", response_model=schemas.match.MatchRead)
async def update_match_endpoint(
    match_id: int,
    match_in: schemas.match.MatchUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Uppdatera en match med ett specifikt ID.
    """
    db_match = await crud.match.get_match(db=db, match_id=match_id)
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Match not found"
        )
    if match_in.home_team_id is not None and match_in.home_team_id != db_match.home_team_id:
        home_team = await crud.team.get_team(db, team_id=match_in.home_team_id)
        if not home_team:
            raise HTTPException(status_code=404, detail=f"New home team with id {match_in.home_team_id} not found")
    
    if match_in.away_team_id is not None and match_in.away_team_id != db_match.away_team_id:
        away_team = await crud.team.get_team(db, team_id=match_in.away_team_id)
        if not away_team:
            raise HTTPException(status_code=404, detail=f"New away team with id {match_in.away_team_id} not found")
            
    if match_in.home_team_id is not None and match_in.away_team_id is not None and match_in.home_team_id == match_in.away_team_id:
         raise HTTPException(status_code=400, detail="Home team and away team cannot be the same.")
    elif match_in.home_team_id is not None and match_in.home_team_id == db_match.away_team_id: 
         raise HTTPException(status_code=400, detail="Home team cannot be the same as the current away team.")
    elif match_in.away_team_id is not None and match_in.away_team_id == db_match.home_team_id: 
         raise HTTPException(status_code=400, detail="Away team cannot be the same as the current home team.")


    updated_match = await crud.match.update_match(db=db, db_match=db_match, match_in=match_in)
    return updated_match

@router.delete("/matches/{match_id}", response_model=schemas.match.MatchRead)
async def delete_match_endpoint(
    match_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Radera en match med ett specifikt ID.
    """
    deleted_match = await crud.match.delete_match(db=db, match_id=match_id)
    if not deleted_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Match not found"
        )
    return deleted_match