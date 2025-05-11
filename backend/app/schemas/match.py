from pydantic import BaseModel, ConfigDict
from typing import Optional 
import datetime 
from .team import TeamRead

class MatchBase(BaseModel):
    match_date: datetime.datetime
    league: str
    season: str
    home_team_id: int 
    away_team_id: int
    status: Optional[str] = None

#Schema för att skapa en match 

class MatchCreate(MatchBase):
    home_score: Optional[int] = None
    away_score: Optional[int] = None 

# Schema för att uppdatera en match 

class MatchUpdate(BaseModel): 
    match_date: Optional[datetime.datetime] = None
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    league: Optional[str] = None
    season: Optional[str] = None
    status: Optional[str] = None

# Schema för att läsa en match från API:et

class MatchRead(MatchBase):
    id: int
    home_score: Optional[int] = None
    away_score: Optional[int] = None 
    home_team: Optional[TeamRead] = None
    away_team: Optional[TeamRead] = None

    model_config = ConfigDict(from_attributes=True)