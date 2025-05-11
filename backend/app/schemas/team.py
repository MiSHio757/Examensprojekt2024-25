
from pydantic import BaseModel, ConfigDict
from typing import Optional

# Grundläggande fält som delas av flera schemas
class TeamBase(BaseModel):
    name: str
    league: str
    
class TeamCreate(TeamBase):
    pass 

# Schema för att uppdatera ett lag (alla fält valfria)
class TeamUpdate(TeamBase):
   name: Optional[str] = None
   league: Optional[str] = None
  
# Schema för att läsa ett lag (data som skickas ut från API)
class TeamRead(TeamBase):
    id: int
    model_config = ConfigDict(from_attributes = True)

 
