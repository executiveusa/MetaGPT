#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Connection Window - WebSocket Server

@Time    : 2026/02/15
@Author  : Meta Agent (Orchestrator Prime)
@File    : main.py
@Mission : Real-time observation panel for watching AI agents collaborate
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import MetaGPT components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from metagpt.utils.canonical_order import CanonicalOrder, CanonicalOrderEntry
from metagpt.logs import logger


# ============================================================================
# DATA MODELS
# ============================================================================

class AgentStatus(BaseModel):
    """Status of an agent in the system."""
    name: str
    role: str
    status: str = "idle"  # idle, thinking, acting, communicating
    current_task: Optional[str] = None
    last_activity: Optional[str] = None
    orders_count: int = 0


class ConnectionMessage(BaseModel):
    """Message sent over WebSocket."""
    type: str  # order_created, agent_status, session_summary, heartbeat
    data: dict
    timestamp: str = ""


# ============================================================================
# CONNECTION MANAGER
# ============================================================================

class ConnectionManager:
    """
    Manages WebSocket connections for the Connection Window.
    
    Broadcasts Canonical Order events to all connected clients in real-time.
    """
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.canonical_order: CanonicalOrder = CanonicalOrder()
        self.agent_statuses: dict[str, AgentStatus] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
        
        # Send initial state
        await self.send_initial_state(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_initial_state(self, websocket: WebSocket):
        """Send the current state to a newly connected client."""
        # Send session summary
        summary = self.canonical_order.get_session_summary()
        await websocket.send_json(ConnectionMessage(
            type="session_summary",
            data=summary,
            timestamp=datetime.utcnow().isoformat()
        ).model_dump())
        
        # Send recent orders (last 50)
        recent_orders = self.canonical_order.orders[-50:]
        for order in recent_orders:
            await websocket.send_json(ConnectionMessage(
                type="order_created",
                data=order.to_dict(),
                timestamp=order.timestamp
            ).model_dump())
        
        # Send agent statuses
        for agent_name, status in self.agent_statuses.items():
            await websocket.send_json(ConnectionMessage(
                type="agent_status",
                data=status.model_dump(),
                timestamp=datetime.utcnow().isoformat()
            ).model_dump())
    
    async def broadcast(self, message: ConnectionMessage):
        """Broadcast a message to all connected clients."""
        if not self.timestamp:
            message.timestamp = datetime.utcnow().isoformat()
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message.model_dump())
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_order(self, order: CanonicalOrderEntry):
        """Broadcast a new Canonical Order to all clients."""
        await self.broadcast(ConnectionMessage(
            type="order_created",
            data=order.to_dict(),
            timestamp=order.timestamp
        ))
    
    async def broadcast_agent_status(self, status: AgentStatus):
        """Broadcast an agent status update."""
        self.agent_statuses[status.name] = status
        await self.broadcast(ConnectionMessage(
            type="agent_status",
            data=status.model_dump()
        ))
    
    def create_order(self, agent_name: str, agent_role: str, action_type: str,
                     description: str, input_data: dict = None,
                     output_data: dict = None, context: dict = None) -> CanonicalOrderEntry:
        """Create a new Canonical Order and broadcast it."""
        order = self.canonical_order.create_order(
            agent_name=agent_name,
            agent_role=agent_role,
            action_type=action_type,
            description=description,
            input_data=input_data,
            output_data=output_data,
            context=context,
        )
        return order


# ============================================================================
# APPLICATION SETUP
# ============================================================================

# Global connection manager
manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Connection Window server starting up...")
    yield
    logger.info("Connection Window server shutting down...")


app = FastAPI(
    title="Connection Window API",
    description="Real-time observation panel for Archon X agents",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Connection Window API",
        "version": "1.0.0",
        "description": "Real-time observation panel for Archon X agents",
        "websocket": "/ws",
        "endpoints": {
            "agents": "/api/agents",
            "orders": "/api/orders",
            "session": "/api/session",
        }
    }


@app.get("/api/agents")
async def get_agents():
    """Get all agent statuses."""
    return {
        "agents": [status.model_dump() for status in manager.agent_statuses.values()],
        "count": len(manager.agent_statuses),
    }


@app.get("/api/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get a specific agent's status."""
    if agent_name not in manager.agent_statuses:
        raise HTTPException(status_code=404, detail="Agent not found")
    return manager.agent_statuses[agent_name].model_dump()


@app.get("/api/orders")
async def get_orders(limit: int = 100, agent: Optional[str] = None, 
                     action_type: Optional[str] = None):
    """Get Canonical Orders with optional filtering."""
    orders = manager.canonical_order.orders
    
    if agent:
        orders = [o for o in orders if o.agent_name == agent]
    if action_type:
        orders = [o for o in orders if o.action_type == action_type]
    
    orders = orders[-limit:]  # Get most recent
    
    return {
        "orders": [o.to_dict() for o in orders],
        "count": len(orders),
        "total": len(manager.canonical_order.orders),
    }


@app.get("/api/orders/{order_id}")
async def get_order(order_id: str):
    """Get a specific Canonical Order."""
    for order in manager.canonical_order.orders:
        if order.order_id == order_id:
            return order.to_dict()
    raise HTTPException(status_code=404, detail="Order not found")


@app.get("/api/session")
async def get_session():
    """Get the current session summary."""
    return manager.canonical_order.get_session_summary()


@app.post("/api/orders")
async def create_order(
    agent_name: str,
    agent_role: str,
    action_type: str,
    description: str,
    input_data: dict = None,
    output_data: dict = None,
    context: dict = None,
):
    """Create a new Canonical Order (for external agents)."""
    order = manager.create_order(
        agent_name=agent_name,
        agent_role=agent_role,
        action_type=action_type,
        description=description,
        input_data=input_data,
        output_data=output_data,
        context=context,
    )
    
    # Broadcast to all connected clients
    await manager.broadcast_order(order)
    
    return order.to_dict()


@app.post("/api/agents/{agent_name}/status")
async def update_agent_status(
    agent_name: str,
    role: str,
    status: str = "idle",
    current_task: Optional[str] = None,
):
    """Update an agent's status."""
    agent_status = AgentStatus(
        name=agent_name,
        role=role,
        status=status,
        current_task=current_task,
        last_activity=datetime.utcnow().isoformat(),
        orders_count=len([o for o in manager.canonical_order.orders if o.agent_name == agent_name]),
    )
    
    await manager.broadcast_agent_status(agent_status)
    
    return agent_status.model_dump()


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Receives:
    - heartbeat: Keep connection alive
    - subscribe: Subscribe to specific events
    
    Sends:
    - order_created: New Canonical Order created
    - agent_status: Agent status update
    - session_summary: Session summary update
    - heartbeat: Response to heartbeat
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type", "unknown")
                
                if msg_type == "heartbeat":
                    # Respond to heartbeat
                    await websocket.send_json(ConnectionMessage(
                        type="heartbeat",
                        data={"status": "alive"},
                    ).model_dump())
                
                elif msg_type == "subscribe":
                    # Handle subscription (future feature)
                    await websocket.send_json(ConnectionMessage(
                        type="subscribed",
                        data={"channels": message.get("channels", ["all"])},
                    ).model_dump())
                
                else:
                    logger.warning(f"Unknown WebSocket message type: {msg_type}")
            
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the Connection Window server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
