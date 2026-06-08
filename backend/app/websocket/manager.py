import asyncio
import logging
from typing import Dict, Set
from fastapi import WebSocket
import json

logger = logging.getLogger("researchmind.websocket")

class ConnectionManager:
    def __init__(self):
        # project_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        self.active_connections[project_id].add(websocket)
        logger.info(f"Client connected to project {project_id}. Total: {len(self.active_connections[project_id])}")

    def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        logger.info(f"Client disconnected from project {project_id}")

    async def broadcast_to_project(self, project_id: str, message: dict):
        if project_id not in self.active_connections:
            return
        dead = set()
        payload = json.dumps(message)
        for ws in self.active_connections[project_id]:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.active_connections[project_id].discard(ws)

    async def send_agent_update(self, project_id: str, agent: str, message: str, progress: int, status: str = "running"):
        await self.broadcast_to_project(project_id, {
            "type": "agent_update",
            "agent": agent,
            "message": message,
            "progress": progress,
            "status": status,
        })

    async def send_completion(self, project_id: str):
        await self.broadcast_to_project(project_id, {
            "type": "completed",
            "message": "Research complete! Report is ready.",
            "progress": 100,
            "status": "completed",
        })

    async def send_error(self, project_id: str, error: str):
        await self.broadcast_to_project(project_id, {
            "type": "error",
            "message": error,
            "status": "failed",
        })

manager = ConnectionManager()
