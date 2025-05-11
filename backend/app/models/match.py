from sqlalchemy import Integer, String, DateTime, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import datetime 
from app.db.base_class import Base
from .team import Team 

class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    match_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)

    # Foreign Key som pekar på id-kolumnen i 'teams'-tabellen
    home_team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), nullable=False)

    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) 
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    league: Mapped[str] = mapped_column(String, index=True, nullable=False)
    season: Mapped[str] = mapped_column(String, index=True, nullable=False) 

    status: Mapped[Optional[str]] = mapped_column(String, nullable=True) 

    # external_api_id: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True) # För ID från externt API

    # Relationer till Team-modellen
    # Detta skapar attribut på Match-objektet för att enkelt komma åt hemmalag och bortalag
    home_team: Mapped["Team"] = relationship("Team", foreign_keys=[home_team_id])
    away_team: Mapped["Team"] = relationship("Team", foreign_keys=[away_team_id])

    def __repr__(self):
        return (
            f"<Match(id={self.id}, date='{self.match_date}', "
            f"home_team_id={self.home_team_id}, away_team_id={self.away_team_id}, "
            f"league='{self.league}')>"
        )