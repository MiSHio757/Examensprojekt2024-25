from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import schemas 
from app import crud    
from app.db.session import get_db 

router = APIRouter()

# Endpoint för att skapa ett nytt lag
@router.post("/teams/", response_model=schemas.team.TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team_endpoint(
    team_in: schemas.team.TeamCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Kolla om ett lag med samma namn redan finns (valfritt men bra)
    existing_team = await crud.team.get_team_by_name(db=db, name=team_in.name)
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team with this name already exists",
        )
    created_team = await crud.team.create_team(db=db, team=team_in)
    return created_team

# Endpoint för att hämta en lista med lag
@router.get("/teams/", response_model=List[schemas.team.TeamRead]) 
async def read_teams_endpoint(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    teams = await crud.team.get_teams(db=db, skip=skip, limit=limit)
    return teams

# Endpoint för att hämta ett specifikt lag med ID
@router.get("/teams/{team_id}", response_model=schemas.team.TeamRead)
async def read_team_endpoint(
    team_id: int, 
    db: AsyncSession = Depends(get_db)
):
    db_team = await crud.team.get_team(db=db, team_id=team_id)
    if db_team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return db_team

# Endpoint för att updatera ett lag
@router.put("/teams/{team_id}", response_model=schemas.team.TeamRead)
async def update_team_endpoint(
    team_id: int,
    team_in: schemas.team.TeamUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Uppdatera ett lag med ett specifikt ID.
    """
    db_team = await crud.team.get_team(db=db, team_id=team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Team not found"
        )

    # Om namnet ändras, kolla att det nya namnet inte redan finns för ett annat lag
    if team_in.name and team_in.name != db_team.name:
        existing_team_with_new_name = await crud.team.get_team_by_name(db=db, name=team_in.name)
        if existing_team_with_new_name and existing_team_with_new_name.id != team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another team with this name already exists",
            )

    updated_team = await crud.team.update_team(db=db, db_team=db_team, team_in=team_in)
    return updated_team