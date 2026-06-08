"""
ResearchMind AI — Pydantic Schemas
Request / response validation for all API endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Any, Dict
from datetime import datetime
import re


# ══════════════════════════════════════════════════════════════════════════════
# AUTH SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_verified: bool
    is_active: bool = True
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar_url: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# PROJECT SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    topic: str = Field(..., min_length=1, max_length=1000)


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    topic: Optional[str] = Field(None, min_length=1, max_length=1000)
    status: Optional[str] = None


class ProjectOut(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    topic: str
    status: str
    progress: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectListOut(BaseModel):
    items: List[ProjectOut]
    total: int
    page: int
    page_size: int
    pages: int


# ══════════════════════════════════════════════════════════════════════════════
# RESEARCH SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class ResearchStartRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=1000)
    description: Optional[str] = None
    search_depth: str = Field(default="advanced", pattern="^(basic|advanced)$")
    max_sources: int = Field(default=10, ge=1, le=50)


class ResearchStartResponse(BaseModel):
    project_id: str
    task_id: str
    status: str
    message: str = "Research workflow started successfully"


class ResearchStatusResponse(BaseModel):
    project_id: str
    task_id: Optional[str] = None
    status: str
    progress: int
    current_agent: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# AGENT LOG SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class AgentLogOut(BaseModel):
    id: str
    project_id: str
    agent_name: str
    action: str
    message: str
    level: str = "info"
    duration_ms: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class AgentLogListOut(BaseModel):
    items: List[AgentLogOut]
    total: int


# ══════════════════════════════════════════════════════════════════════════════
# REPORT SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class ReportOut(BaseModel):
    id: str
    project_id: str
    executive_summary: Optional[str] = None
    key_findings: Optional[Any] = None
    trend_analysis: Optional[Any] = None
    recommendations: Optional[Any] = None
    risk_analysis: Optional[str] = None
    future_predictions: Optional[str] = None
    confidence_score: Optional[float] = None
    chart_data: Optional[Any] = None
    source_count: int = 0
    word_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════════════
# SOURCE SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class SourceOut(BaseModel):
    id: str
    project_id: str
    title: str
    url: str
    content: Optional[str] = None
    snippet: Optional[str] = None
    source_type: Optional[str] = None
    trust_score: Optional[float] = None
    is_verified: bool = False
    domain: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SourceListOut(BaseModel):
    items: List[SourceOut]
    total: int


# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class AnalyticsOverview(BaseModel):
    total_projects: int
    completed_projects: int
    active_projects: int
    failed_projects: int
    total_sources: int
    total_reports: int
    avg_completion_time_minutes: float
    avg_confidence_score: float
    total_agent_logs: int
    agent_performance: Dict[str, Any] = {}


# ══════════════════════════════════════════════════════════════════════════════
# NOTIFICATION SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class NotificationOut(BaseModel):
    id: str
    type: str
    title: Optional[str] = None
    message: str
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListOut(BaseModel):
    items: List[NotificationOut]
    total: int
    unread_count: int


class NotificationMarkReadRequest(BaseModel):
    notification_ids: List[str]


# ══════════════════════════════════════════════════════════════════════════════
# TEAM SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class TeamInvite(BaseModel):
    project_id: str
    email: EmailStr
    role: str = Field(default="viewer", pattern="^(admin|editor|viewer)$")


class TeamMemberOut(BaseModel):
    id: str
    user_id: str
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    role: str
    joined_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TeamOut(BaseModel):
    id: str
    name: str
    project_id: str
    description: Optional[str] = None
    members: List[TeamMemberOut] = []
    created_at: datetime

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════════════
# COMMENT SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class CommentCreate(BaseModel):
    project_id: str
    text: str = Field(..., min_length=1, max_length=5000)
    parent_id: Optional[str] = None


class CommentOut(BaseModel):
    id: str
    project_id: str
    user_id: str
    user_name: Optional[str] = None
    parent_id: Optional[str] = None
    text: str
    is_edited: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    replies: List["CommentOut"] = []

    class Config:
        from_attributes = True


class CommentUpdate(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


# ══════════════════════════════════════════════════════════════════════════════
# CHAT ASSISTANT SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    project_id: str
    message: str = Field(..., min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    answer: str
    project_id: str
    sources_used: int = 0
    conversation_id: Optional[str] = None


class ConversationOut(BaseModel):
    id: str
    project_id: str
    message: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════════════════════
# WEBSOCKET SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class WSMessage(BaseModel):
    type: str  # agent_update | completed | error | heartbeat | connected
    agent: Optional[str] = None
    message: str
    progress: Optional[int] = None
    status: Optional[str] = None
    project_id: Optional[str] = None


# ══════════════════════════════════════════════════════════════════════════════
# GENERIC SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class MessageResponse(BaseModel):
    message: str
    status: str = "ok"


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[datetime] = None
