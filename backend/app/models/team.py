
from sqlalchemy import Integer, String, Column 
from sqlalchemy.orm import Mapped, mapped_column 
from typing import Optional # Används om du har kolumner som kan vara NULL
from app.db.base_class import Base 

class Team(Base):
    # Definierar det faktiska tabellnamnet i PostgreSQL-databasen
    __tablename__ = "teams" 

    # Definierar kolumnerna i tabellen med moderna type hints

    # id: Primärnyckel, heltal, indexerad för snabba sökningar
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) 

    # name: Lagets namn, textsträng, måste finnas (nullable=False), 
    #       ska vara unikt, indexerat för snabba sökningar
    name: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=True)

    # league: Ligan laget spelar i, textsträng, måste finnas, indexerad
    league: Mapped[str] = mapped_column(String, index=True, nullable=False) 


    # En __repr__ är bra för att enkelt kunna skriva ut objekt vid debugging
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', league='{self.league}')>"