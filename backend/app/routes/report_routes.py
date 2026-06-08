from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.all_models import Report
from app.schemas.schemas import ReportOut
from app.auth.dependencies import get_current_active_user
from app.models.all_models import User

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/{project_id}", response_model=ReportOut)
def get_report(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    report = db.query(Report).filter(Report.project_id == project_id).order_by(Report.created_at.desc()).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not yet generated for this project.")
    return report
