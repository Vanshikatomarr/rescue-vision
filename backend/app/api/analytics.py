from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    return analytics_service.get_analytics_summary(db)

@router.get("/models")
def get_model_analytics(db: Session = Depends(get_db)):
    summary = analytics_service.get_analytics_summary(db)
    return summary["model_evaluations"]
