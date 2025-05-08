from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select
from pydantic import BaseModel

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "sqlite:///./predictions.db"
engine = create_engine(DATABASE_URL, echo=True)

class PredictionResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime
    home_team: int
    away_team: int
    prediction_1x2: str
    confidence_1x2: float
    prediction_ou: str
    confidence_ou: float
    prediction_btts: str
    confidence_btts: float
    actual_1x2: Optional[str] = None
    actual_ou: Optional[str] = None
    actual_btts: Optional[str] = None

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/accuracy")
def get_accuracy():
    with Session(engine) as session:
        total = session.exec(select(PredictionResult)).all()
        correct_1x2 = [r for r in total if r.actual_1x2 == r.prediction_1x2]
        accuracy = len(correct_1x2) / len(total) if total else 0
        return {"accuracy_1x2": accuracy}

# New input model for /predict
class PredictionInput(BaseModel):
    home_team: int
    away_team: int

# New endpoint for predictions
@app.post("/predict")
def predict(input: PredictionInput):
    # Dummy prediction logic — replace with your ML model
    prediction_1x2 = "1" if input.home_team > input.away_team else "2"
    confidence_1x2 = 0.75
    prediction_ou = "Over 2.5"
    confidence_ou = 0.65
    prediction_btts = "Yes"
    confidence_btts = 0.70

    # Save to database
    new_record = PredictionResult(
        timestamp=datetime.utcnow(),
        home_team=input.home_team,
        away_team=input.away_team,
        prediction_1x2=prediction_1x2,
        confidence_1x2=confidence_1x2,
        prediction_ou=prediction_ou,
        confidence_ou=confidence_ou,
        prediction_btts=prediction_btts,
        confidence_btts=confidence_btts,
    )
    with Session(engine) as session:
        session.add(new_record)
        session.commit()

    return {
        "prediction_1x2": prediction_1x2,
        "confidence_1x2": confidence_1x2,
        "prediction_ou": prediction_ou,
        "confidence_ou": confidence_ou,
        "prediction_btts": prediction_btts,
        "confidence_btts": confidence_btts,
    }
