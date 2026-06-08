"""
ResearchMind AI — SQLAlchemy ORM Models
All 12 database models for the Multi-Agent Deep Research Platform.
"""

import uuid
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Text, Float, JSON, Index, Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


# ══════════════════════════════════════════════════════════════════════════════
# 1. USER
# ══════════════════════════════════════════════════════════════════════════════
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    email = Column(String(320), unique=True, index=True, nullable=False)
    password_hash = Column(String(512), nullable=False)
    role = Column(String(50), default="user")  # user | admin | moderator
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    team_memberships = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


# ══════════════════════════════════════════════════════════════════════════════
# 2. PROJECT
# ══════════════════════════════════════════════════════════════════════════════
class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    topic = Column(String(1000), nullable=False)
    status = Column(String(50), default="pending")  # pending | running | completed | failed
    progress = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="projects")
    tasks = relationship("ResearchTask", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")
    logs = relationship("AgentLog", back_populates="project", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="project", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="project", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="project", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_projects_user_status", "user_id", "status"),
    )

    def __repr__(self):
        return f"<Project {self.title}>"


# ══════════════════════════════════════════════════════════════════════════════
# 3. RESEARCH TASK
# ══════════════════════════════════════════════════════════════════════════════
class ResearchTask(Base):
    __tablename__ = "research_tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    celery_task_id = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")  # pending | running | completed | failed
    progress = Column(Integer, default=0)
    current_agent = Column(String(100), nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="tasks")

    def __repr__(self):
        return f"<ResearchTask {self.id} status={self.status}>"


# ══════════════════════════════════════════════════════════════════════════════
# 4. AGENT LOG
# ══════════════════════════════════════════════════════════════════════════════
class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(String, nullable=True)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    level = Column(String(20), default="info")  # info | warning | error
    metadata_json = Column(JSON, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="logs")

    __table_args__ = (
        Index("ix_agent_logs_project_time", "project_id", "timestamp"),
    )

    def __repr__(self):
        return f"<AgentLog {self.agent_name}: {self.action}>"


# ══════════════════════════════════════════════════════════════════════════════
# 5. REPORT
# ══════════════════════════════════════════════════════════════════════════════
class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    executive_summary = Column(Text, nullable=True)
    key_findings = Column(JSON, nullable=True)
    trend_analysis = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    risk_analysis = Column(Text, nullable=True)
    future_predictions = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    chart_data = Column(JSON, nullable=True)
    source_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="reports")

    def __repr__(self):
        return f"<Report project={self.project_id}>"


# ══════════════════════════════════════════════════════════════════════════════
# 6. SOURCE
# ══════════════════════════════════════════════════════════════════════════════
class Source(Base):
    __tablename__ = "sources"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(1000), nullable=False)
    url = Column(String(2048), nullable=False)
    content = Column(Text, nullable=True)
    snippet = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=True)  # web | academic | news | gov
    trust_score = Column(Float, nullable=True)
    is_verified = Column(Boolean, default=False)
    domain = Column(String(255), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="sources")

    __table_args__ = (
        Index("ix_sources_project", "project_id"),
    )

    def __repr__(self):
        return f"<Source {self.title[:50]}>"


# ══════════════════════════════════════════════════════════════════════════════
# 7. ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, default=0.0)
    metric_data = Column(JSON, nullable=True)
    period = Column(String(20), nullable=True)  # daily | weekly | monthly
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("ix_analytics_user_metric", "user_id", "metric_name"),
    )

    def __repr__(self):
        return f"<Analytics {self.metric_name}={self.metric_value}>"


# ══════════════════════════════════════════════════════════════════════════════
# 8. CONVERSATION
# ══════════════════════════════════════════════════════════════════════════════
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user | assistant
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="conversations")
    user = relationship("User", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation {self.role}: {self.message[:30]}>"


# ══════════════════════════════════════════════════════════════════════════════
# 9. NOTIFICATION
# ══════════════════════════════════════════════════════════════════════════════
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)  # project_completed | report_generated | team_invite | system
    title = Column(String(255), nullable=True)
    message = Column(String(1000), nullable=False)
    is_read = Column(Boolean, default=False)
    action_url = Column(String(500), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "is_read"),
    )

    def __repr__(self):
        return f"<Notification {self.type}: {self.message[:30]}>"


# ══════════════════════════════════════════════════════════════════════════════
# 10. TEAM
# ══════════════════════════════════════════════════════════════════════════════
class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team {self.name}>"


# ══════════════════════════════════════════════════════════════════════════════
# 11. TEAM MEMBER
# ══════════════════════════════════════════════════════════════════════════════
class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(String, primary_key=True, default=generate_uuid)
    team_id = Column(String, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), default="viewer")  # admin | editor | viewer
    invited_by = Column(String, nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")

    __table_args__ = (
        Index("ix_team_members_unique", "team_id", "user_id", unique=True),
    )

    def __repr__(self):
        return f"<TeamMember user={self.user_id} role={self.role}>"


# ══════════════════════════════════════════════════════════════════════════════
# 12. COMMENT
# ══════════════════════════════════════════════════════════════════════════════
class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(String, ForeignKey("comments.id"), nullable=True)  # threaded comments
    text = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="comments")
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])

    __table_args__ = (
        Index("ix_comments_project", "project_id"),
    )

    def __repr__(self):
        return f"<Comment by={self.user_id}: {self.text[:30]}>"
