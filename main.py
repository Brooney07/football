from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine, Session, select
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional

app = FastAPI()

origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

DATABASE_URL = "sqlite:///./predictions.db"
engine = create_engine(DATABASE_URL, echo=True)

class PredictionResult(SQLModel, table=True):
    id: Optional[int] = None
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
        total = session.exec(select(PredictionResult).where(PredictionResult.actual_1x2 != None)).count()
        correct_1x2 = session.exec(select(PredictionResult).where(PredictionResult.prediction_1x2 == PredictionResult.actual_1x2)).count()
        correct_ou = session.exec(select(PredictionResult).where(PredictionResult.prediction_ou == PredictionResult.actual_ou)).count()
        correct_btts = session.exec(select(PredictionResult).where(PredictionResult.prediction_btts == PredictionResult.actual_btts)).count()
        return {
            "total": total,
            "accuracy_1x2": round(correct_1x2 / total, 3) if total else 0,
            "accuracy_ou": round(correct_ou / total, 3) if total else 0,
            "accuracy_btts": round(correct_btts / total, 3) if total else 0,
        }
