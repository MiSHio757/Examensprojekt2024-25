from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import joblib
import os
import numpy as np

from app.db.session import get_db
from app.core.feature_engineering import generate_features_for_prediction

router = APIRouter()

MODEL_DIR = "ml_models"
MODEL_NAME = "logistic_regression_v1.joblib"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

model_pipeline = None 
if os.path.exists(MODEL_PATH):
    try:
        model_pipeline = joblib.load(MODEL_PATH)
        print(f"INFO:  Model '{MODEL_PATH}' loaded successfully at startup.")
    except Exception as e:
        print(f"ERROR:    Failed to load model '{MODEL_PATH}': {e}")
        model_pipeline = None
else:
    print(f"WARNING:  Model file not found at '{MODEL_PATH}'. Prediction endpoint will return errors.")

# Pydantic Schemas
class PredictionInput(BaseModel):
    home_team_id: int 
    away_team_id: int 

class PredictionOutput(BaseModel):
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    

# API Endpoint 
@router.post("/predict/", response_model=PredictionOutput)
async def predict_match_outcome(
    input_data: PredictionInput,
    db: AsyncSession = Depends(get_db) 
):
    if model_pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Machine Learning model is not loaded. Prediction service unavailable."
        )

    print(f"Received prediction request for home_id: {input_data.home_team_id}, away_id: {input_data.away_team_id}")

    feature_vector_1d = await generate_features_for_prediction( # <<--- ANROPA DIN NYA FUNKTION
        db=db, 
        home_team_id=input_data.home_team_id, 
        away_team_id=input_data.away_team_id
    )

    if feature_vector_1d is None:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Could not generate features for the given teams, possibly due to insufficient historical data."
        )

    features_for_model = feature_vector_1d.reshape(1, -1) 

    print(f"Generated features for model: {features_for_model}")

    

    try:
        probabilities = model_pipeline.predict_proba(features_for_model)[0] 
        print(f"Raw probabilities from model: {probabilities}")

        response_data = {
            "home_win_probability": float(probabilities[1]), # Sannolikhet för klass 1 (Home Win)
            "draw_probability": float(probabilities[0]),     # Sannolikhet för klass 0 (Draw)
            "away_win_probability": float(probabilities[2])  # Sannolikhet för klass 2 (Away Win)
        }

    except Exception as e:
        print(f"Error during model prediction: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during model prediction: {e}")

    return response_data
