#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Canonical Order Tracking System

@Time    : 2026/02/15
@Author  : Meta Agent (Orchestrator Prime)
@File    : canonical_order.py
@Mission : Track every agent action for transparency, training, and robot data
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from metagpt.logs import logger


# ============================================================================
# CANONICAL ORDER DATA STRUCTURES
# ============================================================================

class CanonicalOrderEntry(BaseModel):
    """
    A single canonical order entry representing one agent action.
    
    This is the atomic unit of tracking in Archon X.
    Every action, decision, and movement is logged as a CanonicalOrderEntry.
    """
    
    # Unique identifier
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Timestamp
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # World context
    world: str = "Archon X"
    
    # Agent information
    agent_name: str = ""
    agent_role: str = ""
    agent_profile: str = ""
    
    # Action details
    action_type: str = ""  # think, act, communicate, observe, create, deploy
    description: str = ""
    input_data: dict = Field(default_factory=dict)
    output_data: dict = Field(default_factory=dict)
    
    # Context
    task_id: Optional[str] = None
    project: Optional[str] = None
    collaborators: list[str] = Field(default_factory=list)
    environment: Optional[str] = None
    
    # Trace information
    parent_order_id: Optional[str] = None
    sequence_number: int = 0
    session_id: str = ""
    
    # Metadata
    model_used: str = ""
    tokens_consumed: int = 0
    duration_ms: int = 0
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "canonical_order": {
                "order_id": self.order_id,
                "timestamp": self.timestamp,
                "world": self.world,
                "agent": {
                    "name": self.agent_name,
                    "role": self.agent_role,
                    "profile": self.agent_profile,
                },
                "action": {
                    "type": self.action_type,
                    "description": self.description,
                    "input": self.input_data,
                    "output": self.output_data,
                },
                "context": {
                    "task_id": self.task_id,
                    "project": self.project,
                    "collaborators": self.collaborators,
                    "environment": self.environment,
                },
                "trace": {
                    "parent_order_id": self.parent_order_id,
                    "sequence_number": self.sequence_number,
                    "session_id": self.session_id,
                },
                "metadata": {
                    "model_used": self.model_used,
                    "tokens_consumed": self.tokens_consumed,
                    "duration_ms": self.duration_ms,
                    "success": self.success,
                    "error": self.error,
                },
            }
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class CanonicalOrder:
    """
    Canonical Order Tracking System
    
    Creates a comprehensive audit trail of every agent action.
    This data can be sold or used to train robots.
    
    Features:
    - Session-based tracking
    - Parent-child order relationships
    - Automatic persistence to disk
    - Session summaries for reporting
    
    Usage:
        tracker = CanonicalOrder(storage_path="./canonical_orders")
        
        # Create an order
        order = tracker.create_order(
            agent_name="Meta",
            agent_role="Orchestrator",
            action_type="communicate",
            description="Send task to Devika",
            input_data={"task": "Build landing page"},
            context={"project": "Archon X"}
        )
        
        # Get session summary
        summary = tracker.get_session_summary()
    """
    
    def __init__(self, storage_path: str = "./canonical_orders", auto_persist: bool = True):
        """
        Initialize the Canonical Order tracking system.
        
        Args:
            storage_path: Directory to store order logs
            auto_persist: Whether to automatically save orders to disk
        """
        self.storage_path = Path(storage_path)
        self.auto_persist = auto_persist
        self.session_id = str(uuid.uuid4())
        self.sequence_number = 0
        self.orders: list[CanonicalOrderEntry] = []
        self.session_start_time = datetime.now()
        
        # Create storage directory if needed
        if self.auto_persist:
            self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Ensure the storage directory exists."""
        today = datetime.now()
        session_dir = self.storage_path / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}" / self.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        self.session_storage_path = session_dir
    
    def create_order(
        self,
        agent_name: str,
        agent_role: str,
        action_type: str,
        description: str,
        input_data: dict = None,
        output_data: dict = None,
        context: dict = None,
        parent_order_id: str = None,
        agent_profile: str = "",
    ) -> CanonicalOrderEntry:
        """
        Create a new canonical order entry.
        
        Args:
            agent_name: Name of the agent performing the action
            agent_role: Role of the agent (e.g., "Orchestrator", "Engineer")
            action_type: Type of action (think, act, communicate, observe, create, deploy)
            description: Human-readable description of the action
            input_data: Input data for the action
            output_data: Output data from the action
            context: Additional context (task_id, project, collaborators, environment)
            parent_order_id: ID of parent order if this is a sub-action
            agent_profile: Full profile description of the agent
            
        Returns:
            CanonicalOrderEntry: The created order entry
        """
        self.sequence_number += 1
        
        # Extract context fields
        context = context or {}
        
        order = CanonicalOrderEntry(
            agent_name=agent_name,
            agent_role=agent_role,
            agent_profile=agent_profile,
            action_type=action_type,
            description=description,
            input_data=input_data or {},
            output_data=output_data or {},
            task_id=context.get("task_id"),
            project=context.get("project"),
            collaborators=context.get("collaborators", []),
            environment=context.get("environment"),
            parent_order_id=parent_order_id,
            sequence_number=self.sequence_number,
            session_id=self.session_id,
        )
        
        self.orders.append(order)
        
        # Auto-persist if enabled
        if self.auto_persist:
            self._persist_order(order)
        
        logger.debug(f"Canonical Order created: {order.order_id} - {action_type}: {description[:50]}")
        return order
    
    def _persist_order(self, order: CanonicalOrderEntry):
        """Persist an order to disk."""
        if not hasattr(self, 'session_storage_path'):
            return
        
        orders_file = self.session_storage_path / "orders.jsonl"
        
        # Append to JSONL file
        with open(orders_file, 'a') as f:
            f.write(order.to_json() + '\n')
    
    def get_session_summary(self) -> dict:
        """
        Get a summary of the current session.
        
        Returns:
            dict: Summary containing session_id, total_orders, agents_involved, action_types, duration
        """
        agents_involved = list(set(order.agent_name for order in self.orders))
        action_types = list(set(order.action_type for order in self.orders))
        
        # Count by action type
        action_counts = {}
        for order in self.orders:
            action_counts[order.action_type] = action_counts.get(order.action_type, 0) + 1
        
        # Count by agent
        agent_counts = {}
        for order in self.orders:
            agent_counts[order.agent_name] = agent_counts.get(order.agent_name, 0) + 1
        
        duration = (datetime.now() - self.session_start_time).total_seconds()
        
        return {
            "session_id": self.session_id,
            "session_start": self.session_start_time.isoformat(),
            "duration_seconds": duration,
            "total_orders": len(self.orders),
            "agents_involved": agents_involved,
            "agent_counts": agent_counts,
            "action_types": action_types,
            "action_counts": action_counts,
            "success_rate": sum(1 for o in self.orders if o.success) / len(self.orders) if self.orders else 1.0,
        }
    
    def get_orders_by_agent(self, agent_name: str) -> list[CanonicalOrderEntry]:
        """Get all orders for a specific agent."""
        return [order for order in self.orders if order.agent_name == agent_name]
    
    def get_orders_by_type(self, action_type: str) -> list[CanonicalOrderEntry]:
        """Get all orders of a specific type."""
        return [order for order in self.orders if order.action_type == action_type]
    
    def get_order_tree(self, root_order_id: str) -> dict:
        """
        Get a tree of orders starting from a root order.
        
        Args:
            root_order_id: The ID of the root order
            
        Returns:
            dict: Tree structure with order and children
        """
        def build_tree(order_id):
            order = next((o for o in self.orders if o.order_id == order_id), None)
            if not order:
                return None
            
            children = [build_tree(o.order_id) for o in self.orders if o.parent_order_id == order_id]
            children = [c for c in children if c is not None]
            
            return {
                "order": order.to_dict(),
                "children": children,
            }
        
        return build_tree(root_order_id)
    
    def export_session(self, format: str = "json") -> str:
        """
        Export the entire session for external use.
        
        Args:
            format: Export format (json, jsonl, summary)
            
        Returns:
            str: Exported data
        """
        if format == "json":
            return json.dumps({
                "session": self.get_session_summary(),
                "orders": [order.to_dict() for order in self.orders],
            }, indent=2)
        elif format == "jsonl":
            return '\n'.join(order.to_json() for order in self.orders)
        elif format == "summary":
            summary = self.get_session_summary()
            lines = [
                f"# Canonical Order Session Summary",
                f"",
                f"**Session ID:** {summary['session_id']}",
                f"**Duration:** {summary['duration_seconds']:.2f} seconds",
                f"**Total Orders:** {summary['total_orders']}",
                f"",
                f"## Agents Involved",
                "",
            ]
            for agent, count in summary['agent_counts'].items():
                lines.append(f"- {agent}: {count} actions")
            
            lines.extend([
                "",
                "## Action Types",
                "",
            ])
            for action, count in summary['action_counts'].items():
                lines.append(f"- {action}: {count}")
            
            lines.extend([
                "",
                f"**Success Rate:** {summary['success_rate'] * 100:.1f}%",
            ])
            
            return '\n'.join(lines)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def save_summary(self):
        """Save a human-readable summary to disk."""
        if not hasattr(self, 'session_storage_path'):
            return
        
        summary_file = self.session_storage_path / "summary.md"
        with open(summary_file, 'w') as f:
            f.write(self.export_session(format="summary"))
        
        # Also save full JSON
        json_file = self.session_storage_path / "session.json"
        with open(json_file, 'w') as f:
            f.write(self.export_session(format="json"))


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_session_summary(orders: list[CanonicalOrderEntry]) -> dict:
    """
    Create a summary from a list of orders.
    
    Args:
        orders: List of CanonicalOrderEntry objects
        
    Returns:
        dict: Summary statistics
    """
    if not orders:
        return {"total_orders": 0}
    
    return {
        "total_orders": len(orders),
        "agents": list(set(o.agent_name for o in orders)),
        "action_types": list(set(o.action_type for o in orders)),
        "success_rate": sum(1 for o in orders if o.success) / len(orders),
    }


# ============================================================================
# EXPORT
# ============================================================================

__all__ = ["CanonicalOrder", "CanonicalOrderEntry", "create_session_summary"]
