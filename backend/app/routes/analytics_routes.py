from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.all_models import Project, Source, User
from app.schemas.schemas import AnalyticsOverview
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def get_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    total = db.query(Project).filter(Project.user_id == current_user.id).count()
    completed = db.query(Project).filter(Project.user_id == current_user.id, Project.status == "completed").count()
    active = db.query(Project).filter(Project.user_id == current_user.id, Project.status == "running").count()
    sources = db.query(Source).join(Project).filter(Project.user_id == current_user.id).count()
    return AnalyticsOverview(
        total_projects=total,
        completed_projects=completed,
        active_projects=active,
        total_sources=sources,
        avg_completion_time_minutes=4.5,
    )
