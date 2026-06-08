from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.all_models import Team, TeamMember, Comment, User, Notification
from app.schemas.schemas import TeamInvite, CommentCreate, CommentOut
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/api/team", tags=["Team Collaboration"])


@router.post("/invite")
def invite_member(payload: TeamInvite, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    invited_user = db.query(User).filter(User.email == payload.email).first()
    if not invited_user:
        raise HTTPException(status_code=404, detail="User with that email not found.")

    # Create or get team for project
    team = db.query(Team).filter(Team.project_id == payload.project_id).first()
    if not team:
        team = Team(name=f"Project Team", project_id=payload.project_id)
        db.add(team)
        db.commit()
        db.refresh(team)

    existing = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == invited_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already a member.")

    member = TeamMember(team_id=team.id, user_id=invited_user.id, role=payload.role)
    db.add(member)

    # Create notification
    notif = Notification(
        user_id=invited_user.id,
        type="team_invite",
        message=f"{current_user.name} invited you to collaborate on a research project.",
    )
    db.add(notif)
    db.commit()

    return {"message": f"Invitation sent to {payload.email}."}


@router.post("/comments", response_model=CommentOut, status_code=201)
def add_comment(payload: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    comment = Comment(project_id=payload.project_id, user_id=current_user.id, text=payload.text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/comments/{project_id}", response_model=List[CommentOut])
def get_comments(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return db.query(Comment).filter(Comment.project_id == project_id).order_by(Comment.created_at).all()
