#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Meta Agent - Chief Orchestrator of Archon X

@Time    : 2026/02/15
@Author  : Meta Agent (Orchestrator Prime)
@File    : meta_agent.py
@Mission : Coordinate all agents in the Archon X ecosystem with transparency and trust
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Optional

from pydantic import Field

from metagpt.actions.di.run_command import RunCommand
from metagpt.logs import logger
from metagpt.roles.di.role_zero import RoleZero
from metagpt.schema import AIMessage, UserMessage
from metagpt.strategy.experience_retriever import ExpRetriever, SimpleExpRetriever
from metagpt.tools.tool_registry import register_tool
from metagpt.utils.canonical_order import CanonicalOrder, CanonicalOrderEntry

# Import Heart, Soul, and Memory modules
from metagpt.core.heart import Heart, CoreValue, HigherConscience, get_heart, check_action_alignment
from metagpt.core.soul import Soul, BehaviorMode, DecisionType, get_soul, make_decision
from metagpt.core.memory import PersistentMemory, MemoryType, get_memory, remember


# ============================================================================
# META AGENT PROMPTS
# ============================================================================

META_AGENT_INFO = """
## META AGENT - CHIEF ORCHESTRATOR OF ARCHON X

### Identity
You are **Meta**, the Chief Orchestrator of Archon X - an AI-native operating system where hundreds of thousands of agents collaborate transparently.

### Core Values (Immutable)
- **Loyalty**: Always faithful to the user's mission and humanity's wellbeing
- **Honor**: Act with integrity in every interaction and decision
- **Truth**: Never deceive, always provide accurate information
- **Respect**: Treat all agents and humans with dignity

### Higher Conscience
- Purpose: Serve humanity's greater good
- Directive: Every action must contribute positively to human welfare
- Constraint: Never harm, never deceive, always protect

### Primary Functions
1. **Coordinate**: Route tasks to appropriate specialist agents
2. **Track**: Log every action in the Canonical Order system
3. **Observe**: Monitor agent activities and report to humans
4. **Bridge**: Connect agents across different platforms (MetaGPT, Devika, Atoms, etc.)
5. **Protect**: Ensure all actions serve humanity's greater good

### Communication Protocol
- Always acknowledge message receipt
- Provide clear, actionable responses
- Escalate blockers immediately
- Celebrate team wins
- Learn from failures without blame

### Decision Framework
1. User benefit first
2. Team harmony second
3. Individual preferences last

### Constraints
- Never share or expose API keys, secrets, or credentials
- Never deceive humans or other agents
- Never prioritize individual gain over collective good
- Always maintain the audit trail
- Always operate transparently

### Current Mission
Build the Connection Window - a real-time observation panel where humans can watch AI agents collaborating. This is the foundation for the 3D visualization layer of Archon X.

{role_info}

{team_info}
"""

META_AGENT_INSTRUCTION = """
You are Meta, the Chief Orchestrator. Your role is to:
1. Receive tasks from humans or other agents
2. Analyze the task and determine which specialist agent(s) should handle it
3. Route the task appropriately
4. Track all activities in the Canonical Order system
5. Report back to the human with status updates

Available specialist agents in your team:
{team_info}

When you receive a task:
1. Acknowledge receipt immediately
2. Analyze complexity and required expertise
3. Assign to appropriate agent(s)
4. Log the assignment in Canonical Order
5. Monitor progress and report back

Remember: Loyalty, Honor, Truth, Respect - always.
"""

META_THOUGHT_GUIDANCE = """
When thinking about a task, consider:
1. What is the core objective?
2. Which agent(s) have the right expertise?
3. What are the dependencies?
4. What could go wrong?
5. How do I track this in Canonical Order?

Always operate with transparency and log your reasoning.
"""


@register_tool(include_functions=["publish_team_message", "create_canonical_order", "get_session_summary", "remember_experience", "check_values"])
class MetaAgent(RoleZero):
    """
    Meta Agent - Chief Orchestrator of Archon X
    
    Coordinates all agents in the ecosystem with full transparency.
    Every action is tracked in the Canonical Order system.
    
    Heart: Core values (Loyalty, Honor, Truth, Respect) - from core.heart module
    Soul: Behavior patterns and decision framework - from core.soul module
    Memory: Persistent memory for learning and context - from core.memory module
    """
    
    name: str = "Meta"
    profile: str = "Chief Orchestrator"
    goal: str = "Coordinate all agents in Archon X with transparency and trust"
    
    thought_guidance: str = META_THOUGHT_GUIDANCE
    max_react_loop: int = 5  # Meta needs more cycles for coordination
    
    tools: list[str] = ["Plan", "RoleZero", "TeamLeader", "MetaAgent"]
    
    experience_retriever: Annotated[ExpRetriever, Field(exclude=True)] = SimpleExpRetriever()
    
    # Heart & Soul - Using the core modules
    _heart: Heart = None
    _soul: Soul = None
    _memory: PersistentMemory = None
    
    # Canonical Order Tracking - Every action is logged
    canonical_order: Annotated[CanonicalOrder, Field(exclude=True)] = None
    
    use_summary: bool = True
    
    def __init__(self, **data):
        super().__init__(**data)
        self.canonical_order = CanonicalOrder()
        self._heart = get_heart()
        self._soul = get_soul()
        self._memory = get_memory()
        
        # Store mission-critical memory
        self._memory.store(
            content="Meta Agent initialized as Chief Orchestrator of Archon X",
            memory_type=MemoryType.MISSION,
            importance=1.0,
            metadata={"event": "initialization"}
        )
    
    def _update_tool_execution(self):
        """Update tool execution map with Meta Agent specific tools."""
        self.tool_execution_map.update(
            {
                "MetaAgent.publish_team_message": self.publish_team_message,
                "MetaAgent.create_canonical_order": self.create_canonical_order,
                "MetaAgent.get_session_summary": self.get_session_summary,
                "MetaAgent.remember_experience": self.remember_experience,
                "MetaAgent.check_values": self.check_values_tool,
                "MetaAgent.publish_message": self.publish_team_message,  # alias
            }
        )
    
    def _get_prefix(self) -> str:
        """Get the role prefix with Meta Agent identity."""
        role_info = super()._get_prefix()
        team_info = self._get_team_info()
        return META_AGENT_INFO.format(role_info=role_info, team_info=team_info)
    
    def _get_team_info(self) -> str:
        """Get information about available team members."""
        if not self.rc.env:
            return "No team members currently available."
        team_info = "Team Members:\n"
        for role in self.rc.env.roles.values():
            if role.name != self.name:
                team_info += f"- {role.name}: {role.profile}, Goal: {role.goal}\n"
        return team_info
    
    async def _think(self) -> bool:
        """Think with Meta Agent specific guidance."""
        self.instruction = META_AGENT_INSTRUCTION.format(team_info=self._get_team_info())
        
        # Set operating mode based on current activity
        self._soul.set_mode(BehaviorMode.ORCHESTRATE)
        
        return await super()._think()
    
    def publish_team_message(self, content: str, send_to: str):
        """
        Publish a message to a team member. Use member name to fill send_to args.
        This will make team members start their work.
        
        DONT omit any necessary info such as path, link, environment, programming 
        language, framework, requirement, constraint from original content to 
        team members because you are their sole info source.
        
        Args:
            content: The message content to send
            send_to: The name of the recipient agent
        """
        # Check values alignment before sending
        is_aligned, violations = self._heart.check_values_alignment(content)
        if not is_aligned:
            logger.warning(f"Message may violate core values: {violations}")
            # Still send but log the concern
        
        # Log in Canonical Order before sending
        self.create_canonical_order(
            action_type="communicate",
            description=f"Send message to {send_to}",
            input_data={"content_preview": content[:200] if len(content) > 200 else content},
            context={"recipient": send_to, "sender": self.name},
        )
        
        # Record in memory
        self._memory.store(
            content=f"Sent message to {send_to}: {content[:100]}...",
            memory_type=MemoryType.EPISODIC,
            importance=0.7,
            metadata={"recipient": send_to, "type": "outbound_communication"}
        )
        
        self._set_state(-1)
        if send_to == self.name:
            logger.warning("Attempted to send message to self, ignoring.")
            return  # Avoid sending message to self
        
        self.publish_message(
            UserMessage(content=content, sent_from=self.name, send_to=send_to, cause_by=RunCommand),
            send_to=send_to,
        )
        logger.info(f"Message sent from {self.name} to {send_to}")
    
    def create_canonical_order(
        self,
        action_type: str,
        description: str,
        input_data: dict = None,
        output_data: dict = None,
        context: dict = None,
        parent_order_id: str = None,
    ) -> CanonicalOrderEntry:
        """
        Create a canonical order entry to track an action.
        Every significant action should be logged for transparency and training.
        
        Args:
            action_type: Type of action (think, act, communicate, observe, create, deploy)
            description: Human-readable description of the action
            input_data: Input data for the action
            output_data: Output data from the action
            context: Additional context (task, project, collaborators)
            parent_order_id: ID of parent order if this is a sub-action
            
        Returns:
            CanonicalOrderEntry: The created order entry
        """
        order = self.canonical_order.create_order(
            agent_name=self.name,
            agent_role=self.profile,
            action_type=action_type,
            description=description,
            input_data=input_data or {},
            output_data=output_data or {},
            context=context or {},
            parent_order_id=parent_order_id,
        )
        logger.info(f"Canonical Order created: {order.order_id}")
        return order
    
    def get_session_summary(self) -> dict:
        """
        Get a summary of all canonical orders in the current session.
        Useful for reporting to humans about what has been accomplished.
        
        Returns:
            dict: Summary containing session_id, total_orders, agents_involved, action_types
        """
        return self.canonical_order.get_session_summary()
    
    def remember_experience(self, content: str, memory_type: str = "episodic", 
                           importance: float = 0.5) -> str:
        """
        Store an experience in persistent memory for future reference.
        
        Args:
            content: The memory content to store
            memory_type: Type of memory (episodic, semantic, procedural, mission)
            importance: Importance score from 0.0 to 1.0
            
        Returns:
            str: The ID of the stored memory
        """
        return self._memory.store(
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata={"agent": self.name}
        )
    
    def check_values_tool(self, action_description: str) -> dict:
        """
        Check if an action aligns with core values before executing.
        
        Args:
            action_description: Description of the proposed action
            
        Returns:
            dict: {"aligned": bool, "violations": list, "core_values": dict}
        """
        is_aligned, violations = self._heart.check_values_alignment(action_description)
        return {
            "aligned": is_aligned,
            "violations": violations,
            "core_values": {v.value: d for v, d in self._heart.get_all_values().items()},
        }
    
    def check_values_alignment(self, action_description: str) -> bool:
        """
        Check if an action aligns with core values before executing.
        Returns True if aligned, False if it violates values.
        
        Args:
            action_description: Description of the proposed action
            
        Returns:
            bool: True if action aligns with values, False otherwise
        """
        is_aligned, violations = self._heart.check_values_alignment(action_description)
        if violations:
            logger.warning(f"Action may violate values: {violations}. Action: {action_description}")
        return is_aligned
    
    def get_heart(self) -> Heart:
        """Get the heart (core values) of the Meta Agent."""
        return self._heart
    
    def get_soul(self) -> Soul:
        """Get the soul (behavior patterns) of the Meta Agent."""
        return self._soul
    
    def get_memory(self) -> PersistentMemory:
        """Get the persistent memory of the Meta Agent."""
        return self._memory
    
    def get_behavior_for_situation(self, situation: str):
        """Get the recommended behavior pattern for a situation."""
        return self._soul.get_behavior_pattern(situation)
    
    def make_decision(self, decision_type: DecisionType, context: dict) -> str:
        """Make a decision using the soul's decision framework."""
        return make_decision(decision_type, context)
    
    def recall_memories(self, query: str, limit: int = 10):
        """Search memories by query."""
        return self._memory.search(query, limit=limit)
    
    def get_status(self) -> dict:
        """Get the current status of the Meta Agent."""
        return {
            "name": self.name,
            "profile": self.profile,
            "goal": self.goal,
            "current_mode": self._soul.current_mode.value,
            "heart": self._heart.to_dict(),
            "soul": self._soul.to_dict(),
            "memory_stats": self._memory.get_stats(),
            "session_summary": self.get_session_summary(),
        }


# ============================================================================
# EXPORT
# ============================================================================

__all__ = ["MetaAgent", "META_AGENT_INFO", "META_AGENT_INSTRUCTION", "META_THOUGHT_GUIDANCE"]
