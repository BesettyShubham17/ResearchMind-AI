from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
import asyncio
import json

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/research/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await manager.connect(websocket, project_id)
    # Send initial heartbeat
    try:
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": f"Connected to research stream for project {project_id}",
            "project_id": project_id,
        }))
        while True:
            try:
                # Heartbeat every 30s, also listen for client pings
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_text(json.dumps({"type": "heartbeat"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
    except Exception:
        manager.disconnect(websocket, project_id)
