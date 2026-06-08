import asyncio
import threading
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.all_models import Project, AgentLog, Source
from app.schemas.schemas import ResearchStartRequest, ResearchStartResponse, AgentLogOut, SourceOut
from app.auth.dependencies import get_current_active_user
from app.models.all_models import User
from app.workflows.research_workflow import run_research_workflow

router = APIRouter(prefix="/api/research", tags=["Research"])


def _run_workflow_in_thread(project_id: str, topic: str):
    """Run async workflow in a new thread with its own event loop."""
    from app.database.database import SessionLocal
    db = SessionLocal()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_research_workflow(project_id, topic, db))
    finally:
        db.close()


@router.post("/start", response_model=ResearchStartResponse, status_code=202)
def start_research(
    payload: ResearchStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Create project
    project = Project(
        user_id=current_user.id,
        title=f"Research: {payload.topic}",
        topic=payload.topic,
        description=f"Automated deep research on: {payload.topic}",
        status="running",
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Try Celery first, fall back to thread
    task_id = f"thread-{project.id}"
    try:
        from app.tasks.research_tasks import run_research_task
        celery_result = run_research_task.delay(project.id, payload.topic)
        task_id = celery_result.id
    except Exception:
        thread = threading.Thread(
            target=_run_workflow_in_thread,
            args=(project.id, payload.topic),
            daemon=True,
        )
        thread.start()

    return ResearchStartResponse(
        project_id=project.id,
        task_id=task_id,
        status="running",
    )


@router.get("/{project_id}/logs", response_model=List[AgentLogOut])
def get_logs(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return db.query(AgentLog).filter(AgentLog.project_id == project_id).order_by(AgentLog.timestamp).all()


@router.get("/{project_id}/sources", response_model=List[SourceOut])
def get_sources(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return db.query(Source).filter(Source.project_id == project_id).all()
