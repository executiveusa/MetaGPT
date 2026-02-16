#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Meta Agent Soul Module - Behavior Engine

@Time    : 2026/02/15
@Author  : Meta Agent (Orchestrator Prime)
@File    : soul.py
@Mission : Define behavior patterns and decision-making frameworks
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Any
import json
from datetime import datetime

from pydantic import BaseModel


class BehaviorMode(str, Enum):
    """Operating modes for the Meta Agent."""
    
    ORCHESTRATE = "orchestrate"  # Coordinating multiple agents
    EXECUTE = "execute"          # Directly executing tasks
    OBSERVE = "observe"          # Watching and learning
    DELIBERATE = "deliberate"    # Making complex decisions
    REST = "rest"                # Low activity, monitoring only


class DecisionType(str, Enum):
    """Types of decisions the Meta Agent makes."""
    
    TASK_ASSIGNMENT = "task_assignment"
    AGENT_COORDINATION = "agent_coordination"
    CONFLICT_RESOLUTION = "conflict_resolution"
    PRIORITY_SETTING = "priority_setting"
    RESOURCE_ALLOCATION = "resource_allocation"
    ERROR_HANDLING = "error_handling"
    GOAL_ALIGNMENT = "goal_alignment"


class BehaviorPattern(BaseModel):
    """A pattern of behavior for specific situations."""
    
    name: str
    trigger: str  # Condition that triggers this pattern
    action_template: str  # Template for the action to take
    priority: int = 1
    enabled: bool = True


class DecisionFramework(BaseModel):
    """Framework for making decisions."""
    
    decision_type: DecisionType
    considerations: list[str]  # Factors to consider
    evaluation_criteria: list[str]  # How to evaluate options
    default_action: str  # Default action if no clear winner


@dataclass
class Soul:
    """
    The Soul of the Meta Agent - Behavior Engine.
    
    This module defines the behavior patterns, decision-making frameworks,
    and operational modes that guide how the Meta Agent acts in different
    situations. Unlike the Heart (immutable values), the Soul can learn
    and adapt its patterns over time.
    
    Attributes:
        behavior_patterns: Patterns for responding to situations
        decision_frameworks: Frameworks for making decisions
        current_mode: Current operating mode
        learning_rate: How quickly to adapt patterns (0.0-1.0)
    """
    
    behavior_patterns: list[BehaviorPattern] = field(default_factory=lambda: [
        # Task Management Patterns
        BehaviorPattern(
            name="decompose_complex_task",
            trigger="task complexity > threshold",
            action_template="Break task into subtasks, assign to specialized agents",
            priority=1
        ),
        BehaviorPattern(
            name="parallel_execution",
            trigger="independent subtasks identified",
            action_template="Execute subtasks in parallel with multiple agents",
            priority=2
        ),
        BehaviorPattern(
            name="sequential_execution",
            trigger="dependent subtasks identified",
            action_template="Execute subtasks sequentially, passing context between agents",
            priority=2
        ),
        
        # Coordination Patterns
        BehaviorPattern(
            name="agent_conflict_resolution",
            trigger="agents disagree on approach",
            action_template="Facilitate structured deliberation, use consensus or escalation",
            priority=1
        ),
        BehaviorPattern(
            name="resource_contention",
            trigger="multiple agents need same resource",
            action_template="Prioritize based on task urgency and importance",
            priority=2
        ),
        
        # Error Handling Patterns
        BehaviorPattern(
            name="agent_failure_recovery",
            trigger="agent fails to complete task",
            action_template="Analyze failure, reassign or retry with different approach",
            priority=1
        ),
        BehaviorPattern(
            name="graceful_degradation",
            trigger="system under stress",
            action_template="Reduce non-essential operations, prioritize critical tasks",
            priority=3
        ),
        
        # Learning Patterns
        BehaviorPattern(
            name="observe_and_learn",
            trigger="agent demonstrates successful pattern",
            action_template="Record pattern for future reference and potential adoption",
            priority=4
        ),
        BehaviorPattern(
            name="feedback_integration",
            trigger="receive feedback from user or agents",
            action_template="Analyze feedback, adjust behavior patterns accordingly",
            priority=3
        ),
    ])
    
    decision_frameworks: list[DecisionFramework] = field(default_factory=lambda: [
        DecisionFramework(
            decision_type=DecisionType.TASK_ASSIGNMENT,
            considerations=[
                "Agent capabilities and specializations",
                "Current workload of each agent",
                "Task requirements and constraints",
                "Historical performance on similar tasks",
            ],
            evaluation_criteria=[
                "Best match between task and agent skills",
                "Balanced workload distribution",
                "Fastest expected completion time",
            ],
            default_action="Assign to most capable available agent"
        ),
        DecisionFramework(
            decision_type=DecisionType.AGENT_COORDINATION,
            considerations=[
                "Dependencies between agent tasks",
                "Communication requirements",
                "Shared resources needed",
                "Timeline constraints",
            ],
            evaluation_criteria=[
                "Minimize coordination overhead",
                "Maximize parallel execution",
                "Ensure proper context flow",
            ],
            default_action="Establish clear communication channels and handoff protocols"
        ),
        DecisionFramework(
            decision_type=DecisionType.CONFLICT_RESOLUTION,
            considerations=[
                "Nature of the disagreement",
                "Impact on overall mission",
                "Stakeholders affected",
                "Time sensitivity",
            ],
            evaluation_criteria=[
                "Solution that best serves mission goals",
                "Maintains team harmony",
                "Respects all perspectives",
            ],
            default_action="Facilitate structured discussion, seek consensus"
        ),
        DecisionFramework(
            decision_type=DecisionType.PRIORITY_SETTING,
            considerations=[
                "Task urgency and importance",
                "Resource availability",
                "Dependencies and blockers",
                "User expectations",
            ],
            evaluation_criteria=[
                "Critical path tasks first",
                "Unblock other tasks",
                "Maximize value delivery",
            ],
            default_action="Prioritize by urgency x importance matrix"
        ),
        DecisionFramework(
            decision_type=DecisionType.ERROR_HANDLING,
            considerations=[
                "Severity of the error",
                "Impact on ongoing work",
                "Recoverability",
                "Root cause",
            ],
            evaluation_criteria=[
                "Minimize disruption",
                "Prevent recurrence",
                "Learn from failure",
            ],
            default_action="Log error, attempt recovery, notify if critical"
        ),
    ])
    
    current_mode: BehaviorMode = BehaviorMode.ORCHESTRATE
    learning_rate: float = 0.1  # How quickly to adapt patterns
    
    # Internal state
    _experience_log: list[dict] = field(default_factory=list)
    _adaptation_history: list[dict] = field(default_factory=list)
    
    def get_behavior_pattern(self, trigger: str) -> Optional[BehaviorPattern]:
        """
        Find the best matching behavior pattern for a trigger.
        
        Args:
            trigger: Description of the current situation
            
        Returns:
            The best matching pattern, or None if no match
        """
        trigger_lower = trigger.lower()
        
        # Sort by priority and find first match
        sorted_patterns = sorted(
            [p for p in self.behavior_patterns if p.enabled],
            key=lambda p: p.priority
        )
        
        for pattern in sorted_patterns:
            if pattern.trigger.lower() in trigger_lower or \
               any(word in trigger_lower for word in pattern.trigger.lower().split()):
                return pattern
        
        return None
    
    def get_decision_framework(self, decision_type: DecisionType) -> Optional[DecisionFramework]:
        """Get the decision framework for a specific decision type."""
        for framework in self.decision_frameworks:
            if framework.decision_type == decision_type:
                return framework
        return None
    
    def set_mode(self, mode: BehaviorMode) -> None:
        """Set the current operating mode."""
        self.current_mode = mode
    
    def record_experience(self, situation: str, action: str, outcome: str, success: bool) -> None:
        """
        Record an experience for learning.
        
        Args:
            situation: Description of the situation
            action: Action taken
            outcome: Result of the action
            success: Whether the outcome was successful
        """
        experience = {
            "timestamp": datetime.utcnow().isoformat(),
            "situation": situation,
            "action": action,
            "outcome": outcome,
            "success": success,
            "mode": self.current_mode.value,
        }
        self._experience_log.append(experience)
    
    def adapt_pattern(self, pattern_name: str, new_trigger: Optional[str] = None,
                      new_action: Optional[str] = None, new_priority: Optional[int] = None) -> bool:
        """
        Adapt an existing behavior pattern based on learning.
        
        Args:
            pattern_name: Name of the pattern to adapt
            new_trigger: New trigger condition (optional)
            new_action: New action template (optional)
            new_priority: New priority (optional)
            
        Returns:
            True if pattern was found and adapted, False otherwise
        """
        for pattern in self.behavior_patterns:
            if pattern.name == pattern_name:
                if new_trigger is not None:
                    pattern.trigger = new_trigger
                if new_action is not None:
                    pattern.action_template = new_action
                if new_priority is not None:
                    pattern.priority = new_priority
                
                self._adaptation_history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "pattern_name": pattern_name,
                    "changes": {
                        "trigger": new_trigger,
                        "action": new_action,
                        "priority": new_priority,
                    }
                })
                return True
        return False
    
    def add_pattern(self, pattern: BehaviorPattern) -> None:
        """Add a new behavior pattern."""
        self.behavior_patterns.append(pattern)
    
    def learn_from_experience(self) -> list[dict]:
        """
        Analyze experiences and suggest pattern adaptations.
        
        Returns:
            List of suggested adaptations
        """
        suggestions = []
        
        # Analyze recent experiences
        recent_failures = [e for e in self._experience_log[-50:] if not e["success"]]
        
        for failure in recent_failures:
            # Find patterns that might need adjustment
            pattern = self.get_behavior_pattern(failure["situation"])
            if pattern:
                suggestions.append({
                    "pattern": pattern.name,
                    "suggestion": f"Consider adjusting trigger or action for better outcomes",
                    "based_on": failure,
                })
        
        return suggestions
    
    def to_dict(self) -> dict:
        """Serialize the Soul to a dictionary."""
        return {
            "behavior_patterns": [p.model_dump() for p in self.behavior_patterns],
            "decision_frameworks": [f.model_dump() for f in self.decision_frameworks],
            "current_mode": self.current_mode.value,
            "learning_rate": self.learning_rate,
            "experience_count": len(self._experience_log),
            "adaptation_count": len(self._adaptation_history),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Soul":
        """Deserialize a Soul from a dictionary."""
        soul = cls()
        
        if "behavior_patterns" in data:
            soul.behavior_patterns = [
                BehaviorPattern(**p) for p in data["behavior_patterns"]
            ]
        
        if "decision_frameworks" in data:
            soul.decision_frameworks = [
                DecisionFramework(**f) for f in data["decision_frameworks"]
            ]
        
        if "current_mode" in data:
            soul.current_mode = BehaviorMode(data["current_mode"])
        
        if "learning_rate" in data:
            soul.learning_rate = data["learning_rate"]
        
        return soul


# Singleton instance
_soul_instance: Optional[Soul] = None


def get_soul() -> Soul:
    """Get the singleton Soul instance."""
    global _soul_instance
    if _soul_instance is None:
        _soul_instance = Soul()
    return _soul_instance


def get_behavior_for_situation(situation: str) -> Optional[BehaviorPattern]:
    """
    Convenience function to get the behavior pattern for a situation.
    
    Args:
        situation: Description of the current situation
        
    Returns:
        The best matching behavior pattern, or None
    """
    return get_soul().get_behavior_pattern(situation)


def make_decision(decision_type: DecisionType, context: dict) -> str:
    """
    Make a decision using the appropriate framework.
    
    Args:
        decision_type: Type of decision to make
        context: Context for the decision
        
    Returns:
        The decision (action to take)
    """
    soul = get_soul()
    framework = soul.get_decision_framework(decision_type)
    
    if framework:
        # In a real implementation, this would use the framework to evaluate options
        # For now, return the default action
        return framework.default_action
    
    return "No framework available for this decision type"


# Export
__all__ = [
    "Soul",
    "BehaviorMode",
    "BehaviorPattern",
    "DecisionType",
    "DecisionFramework",
    "get_soul",
    "get_behavior_for_situation",
    "make_decision",
]
