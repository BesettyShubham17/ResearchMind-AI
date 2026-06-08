from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.schemas import ChatRequest, ChatResponse
from app.auth.dependencies import get_current_active_user
from app.models.all_models import User, Source, Conversation
from app.services.openai_service import openai_service
from app.vectorstore.pinecone_store import pinecone_service

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # Try Pinecone RAG context first
    context_docs = pinecone_service.similarity_search(payload.message, payload.project_id, top_k=5)

    if context_docs:
        context = "\n\n".join([d.get("content", "") for d in context_docs])
    else:
        # Fall back to DB sources
        sources = db.query(Source).filter(Source.project_id == payload.project_id).limit(5).all()
        context = "\n\n".join([s.content or "" for s in sources])

    answer = openai_service.answer_question(payload.message, context or "No context available.")

    # Persist conversation
    db.add(Conversation(project_id=payload.project_id, user_id=current_user.id, message=payload.message, role="user"))
    db.add(Conversation(project_id=payload.project_id, user_id=current_user.id, message=answer, role="assistant"))
    db.commit()

    return ChatResponse(answer=answer, project_id=payload.project_id)
