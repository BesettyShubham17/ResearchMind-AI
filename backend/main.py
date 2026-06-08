from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import agents, projects, auth

app = FastAPI(
    title="ResearchMind AI API",
    description="Multi-Agent Deep Research Platform API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])

@app.get("/")
def read_root():
    return {"message": "Welcome to ResearchMind AI API"}
