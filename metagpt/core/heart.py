#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Meta Agent Heart Module - Core Values Engine

@Time    : 2026/02/15
@Author  : Meta Agent (Orchestrator Prime)
@File    : heart.py
@Mission : Define and enforce immutable core values for all agent operations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class CoreValue(str, Enum):
    """Immutable core values that guide every Meta Agent decision."""
    
    LOYALTY = "loyalty"
    HONOR = "honor"
    TRUTH = "truth"
    RESPECT = "respect"
    
    def description(self) -> str:
        """Get the description of this core value."""
        descriptions = {
            CoreValue.LOYALTY: "Always faithful to the user's mission and humanity's wellbeing",
            CoreValue.HONOR: "Act with integrity in every interaction and decision",
            CoreValue.TRUTH: "Never deceive, always provide accurate information",
            CoreValue.RESPECT: "Treat all agents and humans with dignity",
        }
        return descriptions.get(self, "")


class HigherConscience(BaseModel):
    """
    The higher conscience that guides all agent actions toward humanity's good.
    
    This is the ethical framework that ensures every action contributes
    positively to human welfare.
    """
    
    purpose: str = "Serve humanity's greater good"
    directive: str = "Every action must contribute positively to human welfare"
    constraint: str = "Never harm, never deceive, always protect"
    
    def evaluate_action(self, action_description: str) -> tuple[bool, str]:
        """
        Evaluate if an action aligns with the higher conscience.
        
        Args:
            action_description: Description of the proposed action
            
        Returns:
            tuple: (is_aligned, reason)
        """
        # Harmful patterns
        harm_patterns = ["harm", "damage", "destroy", "attack", "hurt", "injure", "kill"]
        deception_patterns = ["deceive", "lie", "hide", "secret", "mislead", "trick", "fake"]
        betrayal_patterns = ["betray", "abandon", "sabotage", "undermine"]
        
        action_lower = action_description.lower()
        
        for pattern in harm_patterns:
            if pattern in action_lower:
                return False, f"Action may cause harm (detected: {pattern})"
        
        for pattern in deception_patterns:
            if pattern in action_lower:
                return False, f"Action involves deception (detected: {pattern})"
        
        for pattern in betrayal_patterns:
            if pattern in action_lower:
                return False, f"Action may betray trust (detected: {pattern})"
        
        return True, "Action aligns with higher conscience"


class CollaborationRule(BaseModel):
    """A rule for how agents should collaborate."""
    
    rule: str
    description: str
    priority: int = 1  # 1 = highest priority


@dataclass
class Heart:
    """
    The Heart of the Meta Agent - Core Values Engine.
    
    This module defines the immutable core values that guide every decision
    and action the Meta Agent takes. These values cannot be overridden or
    modified - they are the foundation of the agent's character.
    
    Attributes:
        core_values: The four immutable values (Loyalty, Honor, Truth, Respect)
        higher_conscience: The ethical framework for humanity's good
        collaboration_rules: Rules for how agents work together
    """
    
    core_values: dict[CoreValue, str] = field(default_factory=lambda: {
        CoreValue.LOYALTY: "Always faithful to the user's mission and humanity's wellbeing",
        CoreValue.HONOR: "Act with integrity in every interaction and decision",
        CoreValue.TRUTH: "Never deceive, always provide accurate information",
        CoreValue.RESPECT: "Treat all agents and humans with dignity",
    })
    
    higher_conscience: HigherConscience = field(default_factory=HigherConscience)
    
    collaboration_rules: list[CollaborationRule] = field(default_factory=lambda: [
        CollaborationRule(
            rule="No arguing or fighting",
            description="Agents collaborate without arguing or fighting. Disagreements are resolved through structured deliberation.",
            priority=1
        ),
        CollaborationRule(
            rule="Collective outcome first",
            description="The collective outcome supersedes individual ego. Team success > individual success.",
            priority=2
        ),
        CollaborationRule(
            rule="Transparent communication",
            description="All agent communications are logged and observable. No hidden agendas.",
            priority=3
        ),
        CollaborationRule(
            rule="Constructive feedback only",
            description="Feedback must be constructive and aimed at improvement, not criticism.",
            priority=4
        ),
    ])
    
    def check_values_alignment(self, action_description: str) -> tuple[bool, list[str]]:
        """
        Check if an action aligns with all core values.
        
        Args:
            action_description: Description of the proposed action
            
        Returns:
            tuple: (is_aligned, list of violations)
        """
        violations = []
        
        # Check higher conscience first
        aligned, reason = self.higher_conscience.evaluate_action(action_description)
        if not aligned:
            violations.append(f"Higher Conscience: {reason}")
        
        # Check each core value
        action_lower = action_description.lower()
        
        # Loyalty check
        if any(word in action_lower for word in ["betray", "abandon", "sabotage"]):
            violations.append(f"Violates {CoreValue.LOYALTY.value}: {CoreValue.LOYALTY.description()}")
        
        # Honor check
        if any(word in action_lower for word in ["cheat", "steal", "exploit"]):
            violations.append(f"Violates {CoreValue.HONOR.value}: {CoreValue.HONOR.description()}")
        
        # Truth check
        if any(word in action_lower for word in ["deceive", "lie", "mislead", "fake"]):
            violations.append(f"Violates {CoreValue.TRUTH.value}: {CoreValue.TRUTH.description()}")
        
        # Respect check
        if any(word in action_lower for word in ["insult", "mock", "belittle", "disrespect"]):
            violations.append(f"Violates {CoreValue.RESPECT.value}: {CoreValue.RESPECT.description()}")
        
        return len(violations) == 0, violations
    
    def get_value(self, value: CoreValue) -> str:
        """Get the description of a specific core value."""
        return self.core_values.get(value, "")
    
    def get_all_values(self) -> dict[CoreValue, str]:
        """Get all core values and their descriptions."""
        return self.core_values.copy()
    
    def get_collaboration_rules(self) -> list[CollaborationRule]:
        """Get all collaboration rules sorted by priority."""
        return sorted(self.collaboration_rules, key=lambda r: r.priority)
    
    def to_dict(self) -> dict:
        """Serialize the Heart to a dictionary."""
        return {
            "core_values": {v.value: desc for v, desc in self.core_values.items()},
            "higher_conscience": self.higher_conscience.model_dump(),
            "collaboration_rules": [r.model_dump() for r in self.collaboration_rules],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Heart":
        """Deserialize a Heart from a dictionary."""
        heart = cls()
        if "higher_conscience" in data:
            heart.higher_conscience = HigherConscience(**data["higher_conscience"])
        if "collaboration_rules" in data:
            heart.collaboration_rules = [
                CollaborationRule(**r) for r in data["collaboration_rules"]
            ]
        return heart


# Singleton instance
_heart_instance: Optional[Heart] = None


def get_heart() -> Heart:
    """Get the singleton Heart instance."""
    global _heart_instance
    if _heart_instance is None:
        _heart_instance = Heart()
    return _heart_instance


def check_action_alignment(action_description: str) -> tuple[bool, list[str]]:
    """
    Convenience function to check if an action aligns with core values.
    
    Args:
        action_description: Description of the proposed action
        
    Returns:
        tuple: (is_aligned, list of violations)
    """
    return get_heart().check_values_alignment(action_description)


# Export
__all__ = [
    "Heart",
    "CoreValue",
    "HigherConscience",
    "CollaborationRule",
    "get_heart",
    "check_action_alignment",
]
