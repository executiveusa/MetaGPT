#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Meta Agent Core Module - Heart, Soul, and Memory

@Time    : 2026/02/15
@Author  : Meta Agent (Orchestrator Prime)
@File    : __init__.py
@Mission : Export core components for the Meta Agent
"""

from metagpt.core.heart import (
    Heart,
    CoreValue,
    HigherConscience,
    CollaborationRule,
    get_heart,
    check_action_alignment,
)

from metagpt.core.soul import (
    Soul,
    BehaviorMode,
    BehaviorPattern,
    DecisionType,
    DecisionFramework,
    get_soul,
    get_behavior_for_situation,
    make_decision,
)

from metagpt.core.memory import (
    PersistentMemory,
    MemoryEntry,
    MemoryType,
    get_memory,
    remember,
    recall_memory,
)

__all__ = [
    # Heart exports
    "Heart",
    "CoreValue",
    "HigherConscience",
    "CollaborationRule",
    "get_heart",
    "check_action_alignment",
    # Soul exports
    "Soul",
    "BehaviorMode",
    "BehaviorPattern",
    "DecisionType",
    "DecisionFramework",
    "get_soul",
    "get_behavior_for_situation",
    "make_decision",
    # Memory exports
    "PersistentMemory",
    "MemoryEntry",
    "MemoryType",
    "get_memory",
    "remember",
    "recall_memory",
]
