from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session, select

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
        return {"total_predictions": len(total)}
