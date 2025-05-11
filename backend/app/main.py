
from fastapi import FastAPI
from app.routers import teams 
from app.routers import matches

app = FastAPI(title="AI Football Predictor API")

# Inkluderar team-routern
app.include_router(teams.router, prefix="/api/v1", tags=["Teams"]) 
#Inkluderar match-routern
app.include_router(matches.router, prefix="/api/v1", tags=["Matches"])

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Football Predictor API"}

