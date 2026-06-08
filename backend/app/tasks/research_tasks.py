import asyncio
import logging
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.database.database import SessionLocal
from app.workflows.research_workflow import run_research_workflow

logger = logging.getLogger("researchmind.tasks")


@celery_app.task(bind=True, name="tasks.run_research", max_retries=3)
def run_research_task(self, project_id: str, topic: str):
    """Celery background task to execute the full research workflow."""
    db: Session = SessionLocal()
    try:
        logger.info(f"Starting research task for project {project_id}")
        asyncio.run(run_research_workflow(project_id, topic, db))
        logger.info(f"Research task completed for project {project_id}")
        return {"status": "completed", "project_id": project_id}
    except Exception as exc:
        logger.error(f"Research task failed: {exc}", exc_info=True)
        self.retry(exc=exc, countdown=30)
    finally:
        db.close()


@celery_app.task(name="tasks.generate_embeddings")
def generate_embeddings_task(project_id: str, documents: list):
    """Celery task to generate and store embeddings in Pinecone."""
    from app.vectorstore.pinecone_store import pinecone_service
    try:
        pinecone_service.upsert_documents(documents, project_id)
        return {"status": "done", "count": len(documents)}
    except Exception as e:
        logger.error(f"Embedding task failed: {e}")
        return {"status": "failed", "error": str(e)}


@celery_app.task(name="tasks.update_analytics")
def update_analytics_task():
    """Periodic task to update analytics counters."""
    from app.models.all_models import Project, Analytics
    db: Session = SessionLocal()
    try:
        total = db.query(Project).count()
        completed = db.query(Project).filter(Project.status == "completed").count()
        for name, value in [("total_projects", total), ("completed_projects", completed)]:
            record = db.query(Analytics).filter(Analytics.metric_name == name).first()
            if record:
                record.metric_value = value
            else:
                db.add(Analytics(metric_name=name, metric_value=value))
        db.commit()
        return {"status": "updated"}
    finally:
        db.close()
