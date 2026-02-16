#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Beads Integration Module

@Time    : 2026/02/15
@Author  : Meta Agent (Orchestrator Prime)
@File    : beads_integration.py
@Mission : Integrate Canonical Order tracking with Beads CLI for task management
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from metagpt.logs import logger
from metagpt.utils.canonical_order import CanonicalOrderEntry


# ============================================================================
# BEADS DATA TYPES
# ============================================================================

@dataclass
class BeadsIssue:
    """
    Represents a Beads issue/task.
    
    Maps to Canonical Order entries for seamless integration.
    """
    id: str = ""
    title: str = ""
    type: str = "task"  # task, bug, feature, epic
    status: str = "open"  # open, in_progress, closed
    priority: int = 2  # 0=critical, 1=high, 2=medium, 3=low
    description: str = ""
    design: str = ""
    notes: str = ""
    acceptance: str = ""
    assignee: str = ""
    parent: str = ""
    depends_on: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    
    def to_canonical_order(self) -> CanonicalOrderEntry:
        """Convert Beads issue to Canonical Order entry."""
        return CanonicalOrderEntry(
            order_id=self.id,
            timestamp=self.updated_at or datetime.now().isoformat(),
            world="Archon X",
            agent_name=self.assignee or "unassigned",
            agent_role="Agent",
            agent_profile="",
            action_type="task",
            description=self.title,
            input_data={
                "type": self.type,
                "priority": self.priority,
                "design": self.design,
            },
            output_data={
                "notes": self.notes,
                "acceptance": self.acceptance,
            },
            task_id=self.parent,
            collaborators=[self.assignee] if self.assignee else [],
            parent_order_id=self.parent,
        )


# ============================================================================
# BEADS CLI WRAPPER
# ============================================================================

class BeadsCLI:
    """
    Wrapper for Beads CLI commands.
    
    Provides a Python interface to the `bd` CLI tool for:
    - Creating and managing issues
    - Tracking dependencies
    - Syncing with git
    - Querying ready tasks
    
    Usage:
        beads = BeadsCLI()
        
        # Create an issue
        issue = beads.create_issue("Build landing page", priority=1)
        
        # List ready tasks
        ready = beads.get_ready_tasks()
        
        # Claim a task
        beads.claim_issue(issue.id, assignee="Meta")
        
        # Close when done
        beads.close_issue(issue.id, reason="Completed")
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize Beads CLI wrapper.
        
        Args:
            db_path: Optional path to Beads database (for testing)
        """
        self.db_path = db_path
        self._env = {"BEADS_DB": db_path} if db_path else {}
    
    def _run_command(self, args: list[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a bd CLI command."""
        cmd = ["bd"] + args
        logger.debug(f"Running: {' '.join(cmd)}")
        return subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            env={**dict(subprocess.os.environ), **self._env}
        )
    
    def is_installed(self) -> bool:
        """Check if bd CLI is installed."""
        result = self._run_command(["--version"])
        return result.returncode == 0
    
    def init(self, prefix: str = "archon", stealth: bool = False) -> bool:
        """
        Initialize Beads in the current project.
        
        Args:
            prefix: Prefix for issue IDs
            stealth: Use stealth mode (local only)
            
        Returns:
            bool: True if successful
        """
        args = ["init", "--prefix", prefix]
        if stealth:
            args.append("--stealth")
        
        result = self._run_command(args)
        if result.returncode == 0:
            logger.info(f"Beads initialized with prefix '{prefix}'")
            return True
        else:
            logger.error(f"Failed to initialize Beads: {result.stderr}")
            return False
    
    def create_issue(
        self,
        title: str,
        type: str = "task",
        priority: int = 2,
        description: str = "",
        design: str = "",
        parent: str = "",
        json_output: bool = True,
    ) -> Optional[BeadsIssue]:
        """
        Create a new Beads issue.
        
        Args:
            title: Issue title
            type: Issue type (task, bug, feature, epic)
            priority: Priority (0=critical, 1=high, 2=medium, 3=low)
            description: Issue description
            design: Design notes
            parent: Parent issue ID for hierarchy
            json_output: Return as JSON for parsing
            
        Returns:
            BeadsIssue: The created issue, or None if failed
        """
        args = [
            "create", title,
            "-t", type,
            "-p", str(priority),
        ]
        
        if description:
            args.extend(["--description", description])
        if design:
            args.extend(["--design", design])
        if parent:
            args.extend(["--parent", parent])
        if json_output:
            args.append("--json")
        
        result = self._run_command(args)
        
        if result.returncode == 0 and json_output:
            try:
                data = json.loads(result.stdout)
                return BeadsIssue(
                    id=data.get("id", ""),
                    title=data.get("title", title),
                    type=data.get("type", type),
                    priority=data.get("priority", priority),
                    status=data.get("status", "open"),
                    created_at=data.get("created_at", ""),
                )
            except json.JSONDecodeError:
                logger.warning(f"Could not parse JSON output: {result.stdout}")
        
        if result.returncode == 0:
            logger.info(f"Created issue: {title}")
        else:
            logger.error(f"Failed to create issue: {result.stderr}")
        
        return None
    
    def update_issue(
        self,
        issue_id: str,
        title: str = None,
        description: str = None,
        design: str = None,
        notes: str = None,
        acceptance: str = None,
        status: str = None,
        claim: bool = False,
        assignee: str = None,
    ) -> bool:
        """
        Update a Beads issue.
        
        Args:
            issue_id: Issue ID to update
            title: New title
            description: New description
            design: New design notes
            notes: Additional notes
            acceptance: Acceptance criteria
            status: New status
            claim: Claim the issue (sets assignee and in_progress)
            assignee: Assignee name
            
        Returns:
            bool: True if successful
        """
        args = ["update", issue_id]
        
        if title:
            args.extend(["--title", title])
        if description:
            args.extend(["--description", description])
        if design:
            args.extend(["--design", design])
        if notes:
            args.extend(["--notes", notes])
        if acceptance:
            args.extend(["--acceptance", acceptance])
        if status:
            args.extend(["--status", status])
        if claim:
            args.append("--claim")
        if assignee:
            args.extend(["--assignee", assignee])
        
        result = self._run_command(args)
        
        if result.returncode == 0:
            logger.info(f"Updated issue {issue_id}")
            return True
        else:
            logger.error(f"Failed to update issue {issue_id}: {result.stderr}")
            return False
    
    def claim_issue(self, issue_id: str, assignee: str = None) -> bool:
        """
        Claim a Beads issue (sets assignee and status to in_progress).
        
        Args:
            issue_id: Issue ID to claim
            assignee: Assignee name (defaults to current user)
            
        Returns:
            bool: True if successful
        """
        args = ["update", issue_id, "--claim"]
        if assignee:
            args.extend(["--assignee", assignee])
        
        result = self._run_command(args)
        
        if result.returncode == 0:
            logger.info(f"Claimed issue {issue_id}")
            return True
        else:
            logger.error(f"Failed to claim issue {issue_id}: {result.stderr}")
            return False
    
    def close_issue(self, issue_id: str, reason: str = "Completed") -> bool:
        """
        Close a Beads issue.
        
        Args:
            issue_id: Issue ID to close
            reason: Reason for closing
            
        Returns:
            bool: True if successful
        """
        args = ["close", issue_id, "--reason", reason]
        
        result = self._run_command(args)
        
        if result.returncode == 0:
            logger.info(f"Closed issue {issue_id}: {reason}")
            return True
        else:
            logger.error(f"Failed to close issue {issue_id}: {result.stderr}")
            return False
    
    def get_ready_tasks(self) -> list[BeadsIssue]:
        """
        Get list of tasks with no open blockers.
        
        Returns:
            list[BeadsIssue]: List of ready tasks
        """
        result = self._run_command(["ready", "--json"])
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return [
                    BeadsIssue(
                        id=item.get("id", ""),
                        title=item.get("title", ""),
                        type=item.get("type", "task"),
                        priority=item.get("priority", 2),
                        status=item.get("status", "open"),
                    )
                    for item in data
                ]
            except json.JSONDecodeError:
                logger.warning(f"Could not parse JSON output: {result.stdout}")
        
        return []
    
    def show_issue(self, issue_id: str) -> Optional[BeadsIssue]:
        """
        Show details of a specific issue.
        
        Args:
            issue_id: Issue ID to show
            
        Returns:
            BeadsIssue: The issue details, or None if not found
        """
        result = self._run_command(["show", issue_id, "--json"])
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return BeadsIssue(
                    id=data.get("id", issue_id),
                    title=data.get("title", ""),
                    type=data.get("type", "task"),
                    priority=data.get("priority", 2),
                    status=data.get("status", "open"),
                    description=data.get("description", ""),
                    design=data.get("design", ""),
                    notes=data.get("notes", ""),
                    acceptance=data.get("acceptance", ""),
                    assignee=data.get("assignee", ""),
                    parent=data.get("parent", ""),
                    depends_on=data.get("depends_on", []),
                    created_at=data.get("created_at", ""),
                    updated_at=data.get("updated_at", ""),
                )
            except json.JSONDecodeError:
                logger.warning(f"Could not parse JSON output: {result.stdout}")
        
        return None
    
    def add_dependency(self, child_id: str, parent_id: str) -> bool:
        """
        Add a dependency between issues.
        
        Args:
            child_id: Issue that is blocked
            parent_id: Issue that blocks
            
        Returns:
            bool: True if successful
        """
        result = self._run_command(["dep", "add", child_id, parent_id])
        
        if result.returncode == 0:
            logger.info(f"Added dependency: {child_id} blocked by {parent_id}")
            return True
        else:
            logger.error(f"Failed to add dependency: {result.stderr}")
            return False
    
    def sync(self) -> bool:
        """
        Sync database with git (export JSONL, commit, pull, push).
        
        Returns:
            bool: True if successful
        """
        result = self._run_command(["sync"])
        
        if result.returncode == 0:
            logger.info("Synced Beads database with git")
            return True
        else:
            logger.error(f"Failed to sync: {result.stderr}")
            return False
    
    def list_issues(self, status: str = None, limit: int = 30) -> list[BeadsIssue]:
        """
        List issues, optionally filtered by status.
        
        Args:
            status: Filter by status (open, in_progress, closed)
            limit: Maximum number of issues to return
            
        Returns:
            list[BeadsIssue]: List of issues
        """
        args = ["list", "--limit", str(limit), "--json"]
        if status:
            args.extend(["--status", status])
        
        result = self._run_command(args)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return [
                    BeadsIssue(
                        id=item.get("id", ""),
                        title=item.get("title", ""),
                        type=item.get("type", "task"),
                        priority=item.get("priority", 2),
                        status=item.get("status", "open"),
                    )
                    for item in data
                ]
            except json.JSONDecodeError:
                logger.warning(f"Could not parse JSON output: {result.stdout}")
        
        return []


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_task_from_canonical_order(order: CanonicalOrderEntry, beads: BeadsCLI = None) -> Optional[BeadsIssue]:
    """
    Create a Beads issue from a Canonical Order entry.
    
    Args:
        order: The Canonical Order entry
        beads: BeadsCLI instance (creates new one if None)
        
    Returns:
        BeadsIssue: The created issue, or None if failed
    """
    beads = beads or BeadsCLI()
    
    # Map action type to Beads issue type
    type_map = {
        "think": "task",
        "act": "task",
        "communicate": "task",
        "observe": "task",
        "create": "feature",
        "deploy": "task",
    }
    
    # Map priority (default to medium)
    priority = 2
    
    return beads.create_issue(
        title=order.description[:100] if len(order.description) > 100 else order.description,
        type=type_map.get(order.action_type, "task"),
        priority=priority,
        description=f"From Canonical Order: {order.order_id}",
        parent=order.parent_order_id,
    )


# ============================================================================
# EXPORT
# ============================================================================

__all__ = ["BeadsCLI", "BeadsIssue", "create_task_from_canonical_order"]
