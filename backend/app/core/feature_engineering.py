import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import or_, and_ 
from app.models.match import Match as MatchModel
from app.models.team import Team as TeamModel

# Antal matcher bakåt vi tittar på för rullande medelvärden 
FORM_WINDOW = 5

async def get_team_recent_matches(db: AsyncSession, team_id: int, limit: int = FORM_WINDOW) -> pd.DataFrame:
    """
    Hämtar de senaste 'limit' spelade matcherna för ett givet lag.
    """
    stmt = (
        select(
            MatchModel.match_date,
            MatchModel.home_team_id,
            MatchModel.away_team_id,
            MatchModel.home_score,
            MatchModel.away_score
        )
        .filter(
            or_(MatchModel.home_team_id == team_id, MatchModel.away_team_id == team_id),
            MatchModel.status == 'FINISHED' 
        )
        .order_by(MatchModel.match_date.desc()) 
        .limit(limit)
    )
    result = await db.execute(stmt)
    matches = result.all() 

    # Konvertera till DataFrame
    df = pd.DataFrame(matches, columns=['match_date', 'home_team_id', 'away_team_id', 'home_score', 'away_score'])
    # Sortera igen med äldsta matchen först för rullande beräkningar
    return df.sort_values(by='match_date', ascending=True)


def calculate_features_for_team(team_id: int, team_matches_df: pd.DataFrame) -> dict:
    """
    Beräknar features för ETT lag baserat på dess senaste matcher.
    team_matches_df ska vara sorterad med äldsta matchen först.
    """
    if team_matches_df.empty or len(team_matches_df) == 0:
        print(f"Warning: No historical matches found for team_id {team_id} to calculate features. Returning defaults.")
        return {
            "avg_goals_scored": 1.0, 
            "avg_goals_conceded": 1.0, 
            "form_points": 1.0 
        }

    # Skapar kolumner för gjorda mål, insläppta mål och poäng för DETTA LAG
    team_matches_df['goals_scored'] = np.where(
        team_matches_df['home_team_id'] == team_id, 
        team_matches_df['home_score'], 
        team_matches_df['away_score']
    )
    team_matches_df['goals_conceded'] = np.where(
        team_matches_df['home_team_id'] == team_id, 
        team_matches_df['away_score'], 
        team_matches_df['home_score']
    )

    def get_points(row_team_id, row_home_id, row_away_id, row_home_score, row_away_score):
        if row_team_id == row_home_id: 
            if row_home_score > row_away_score: return 3
            if row_home_score == row_away_score: return 1
            return 0
        else: # Laget är bortalag
            if row_away_score > row_home_score: return 3
            if row_away_score == row_home_score: return 1
            return 0

    team_matches_df['points'] = team_matches_df.apply(
        lambda row: get_points(team_id, row['home_team_id'], row['away_team_id'], row['home_score'], row['away_score']), 
        axis=1
    )

    # Beräkna rullande medelvärden för de senaste matcherna (exklusive den "aktuella" om det vore en ny match)
    # Eftersom vi här beräknar formen *inför* en ny match, använder vi all data vi har.
    avg_goals_scored = team_matches_df['goals_scored'].mean()
    avg_goals_conceded = team_matches_df['goals_conceded'].mean()
    form_points = team_matches_df['points'].mean() # Snittpoäng från de senaste matcherna

    return {
        "avg_goals_scored": avg_goals_scored if pd.notna(avg_goals_scored) else 1.0,
        "avg_goals_conceded": avg_goals_conceded if pd.notna(avg_goals_conceded) else 1.0,
        "form_points": form_points if pd.notna(form_points) else 1.0,
    }


async def generate_features_for_prediction(
    db: AsyncSession, 
    home_team_id: int, 
    away_team_id: int
) -> np.ndarray | None:
    """
    Genererar feature-vektorn för en given match mellan home_team_id och away_team_id.
    Returnerar en NumPy-array med features i rätt ordning, eller None om features inte kan skapas.
    """
    print(f"Generating features for match between home_id={home_team_id} and away_id={away_team_id}")

    home_team_matches_df = await get_team_recent_matches(db, home_team_id, limit=FORM_WINDOW)
    away_team_matches_df = await get_team_recent_matches(db, away_team_id, limit=FORM_WINDOW)

    if home_team_matches_df.empty and away_team_matches_df.empty :
        # Om ingen data finns för något av lagen kan vi inte skapa meningsfulla features
        print(f"  Could not generate features: Insufficient historical data for both teams {home_team_id} and {away_team_id}.")
        # Alternativt, returnera en vektor med genomsnittliga ligavärden eller liknande. För demon: None.
        return None 

    home_features = calculate_features_for_team(home_team_id, home_team_matches_df)
    away_features = calculate_features_for_team(away_team_id, away_team_matches_df)

    feature_vector = np.array([
        home_features["avg_goals_scored"],
        home_features["avg_goals_conceded"],
        away_features["avg_goals_scored"],
        away_features["avg_goals_conceded"],
        home_features["form_points"],
        away_features["form_points"]
    ])

    print(f"  Generated feature vector: {feature_vector}")
    return feature_vector
