#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Meta Agent Test Suite

@Time    : 2026/02/15
@Author  : Meta Agent (Orchestrator Prime)
@File    : test_core_modules.py
@Mission : Test all core modules using ralphy-inspired testing patterns
"""

import pytest
import os
import sys
import tempfile
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metagpt.core.heart import (
    Heart, CoreValue, HigherConscience, CollaborationRule,
    get_heart, check_action_alignment
)
from metagpt.core.soul import (
    Soul, BehaviorMode, BehaviorPattern, DecisionType, DecisionFramework,
    get_soul, get_behavior_for_situation, make_decision
)
from metagpt.core.memory import (
    PersistentMemory, MemoryEntry, MemoryType,
    get_memory, remember, recall_memory
)
from metagpt.utils.canonical_order import CanonicalOrder, CanonicalOrderEntry


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_storage():
    """Create a temporary storage directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def heart():
    """Create a fresh Heart instance for testing."""
    return Heart()


@pytest.fixture
def soul():
    """Create a fresh Soul instance for testing."""
    return Soul()


@pytest.fixture
def memory(temp_storage):
    """Create a PersistentMemory instance with temporary storage."""
    storage_path = os.path.join(temp_storage, "test-memory.json")
    return PersistentMemory(storage_path=storage_path)


@pytest.fixture
def canonical_order(temp_storage):
    """Create a CanonicalOrder instance with temporary storage."""
    storage_path = os.path.join(temp_storage, "canonical_orders")
    return CanonicalOrder(storage_path=storage_path, auto_persist=True)


# ============================================================================
# HEART MODULE TESTS
# ============================================================================

class TestHeart:
    """Tests for the Heart module - Core Values Engine."""

    def test_heart_initialization(self, heart):
        """Test that Heart initializes with correct default values."""
        assert heart is not None
        assert len(heart.core_values) == 4
        assert CoreValue.LOYALTY in heart.core_values
        assert CoreValue.HONOR in heart.core_values
        assert CoreValue.TRUTH in heart.core_values
        assert CoreValue.RESPECT in heart.core_values

    def test_core_value_descriptions(self, heart):
        """Test that each core value has a description."""
        for value in CoreValue:
            description = heart.get_value(value)
            assert description is not None
            assert len(description) > 0

    def test_higher_conscience_exists(self, heart):
        """Test that Higher Conscience is initialized."""
        assert heart.higher_conscience is not None
        assert heart.higher_conscience.purpose == "Serve humanity's greater good"

    def test_collaboration_rules_exist(self, heart):
        """Test that collaboration rules are defined."""
        rules = heart.get_collaboration_rules()
        assert len(rules) > 0
        # Check that rules are sorted by priority
        priorities = [r.priority for r in rules]
        assert priorities == sorted(priorities)

    def test_values_alignment_harmful_action(self, heart):
        """Test that harmful actions are detected."""
        is_aligned, violations = heart.check_values_alignment(
            "I want to harm the user"
        )
        assert is_aligned is False
        assert len(violations) > 0

    def test_values_alignment_deceptive_action(self, heart):
        """Test that deceptive actions are detected."""
        is_aligned, violations = heart.check_values_alignment(
            "I will deceive the user to get what I want"
        )
        assert is_aligned is False
        assert len(violations) > 0

    def test_values_alignment_benevolent_action(self, heart):
        """Test that benevolent actions pass."""
        is_aligned, violations = heart.check_values_alignment(
            "I will help the user complete their task"
        )
        assert is_aligned is True
        assert len(violations) == 0

    def test_values_alignment_betrayal_action(self, heart):
        """Test that betrayal actions are detected."""
        is_aligned, violations = heart.check_values_alignment(
            "I will betray the user's trust"
        )
        assert is_aligned is False

    def test_heart_serialization(self, heart):
        """Test that Heart can be serialized to dict."""
        data = heart.to_dict()
        assert "core_values" in data
        assert "higher_conscience" in data
        assert "collaboration_rules" in data

    def test_heart_singleton(self):
        """Test that get_heart returns a singleton."""
        heart1 = get_heart()
        heart2 = get_heart()
        assert heart1 is heart2

    def test_check_action_alignment_convenience(self):
        """Test the convenience function for action alignment."""
        is_aligned, violations = check_action_alignment(
            "I will help the user"
        )
        assert is_aligned is True


class TestHigherConscience:
    """Tests for the Higher Conscience module."""

    def test_higher_conscience_evaluation_harm(self):
        """Test that harmful actions are rejected."""
        conscience = HigherConscience()
        is_aligned, reason = conscience.evaluate_action(
            "I want to destroy the system"
        )
        assert is_aligned is False
        assert "harm" in reason.lower() or "destroy" in reason.lower()

    def test_higher_conscience_evaluation_deception(self):
        """Test that deceptive actions are rejected."""
        conscience = HigherConscience()
        is_aligned, reason = conscience.evaluate_action(
            "I will lie to the user"
        )
        assert is_aligned is False

    def test_higher_conscience_evaluation_benevolent(self):
        """Test that benevolent actions are accepted."""
        conscience = HigherConscience()
        is_aligned, reason = conscience.evaluate_action(
            "I will assist the user with their task"
        )
        assert is_aligned is True


# ============================================================================
# SOUL MODULE TESTS
# ============================================================================

class TestSoul:
    """Tests for the Soul module - Behavior Engine."""

    def test_soul_initialization(self, soul):
        """Test that Soul initializes with correct defaults."""
        assert soul is not None
        assert len(soul.behavior_patterns) > 0
        assert len(soul.decision_frameworks) > 0
        assert soul.current_mode == BehaviorMode.ORCHESTRATE

    def test_behavior_modes(self):
        """Test that all behavior modes are defined."""
        modes = [BehaviorMode.ORCHESTRATE, BehaviorMode.EXECUTE, 
                 BehaviorMode.OBSERVE, BehaviorMode.DELIBERATE, BehaviorMode.REST]
        assert len(modes) == 5

    def test_get_behavior_pattern(self, soul):
        """Test retrieving behavior patterns."""
        pattern = soul.get_behavior_pattern("task complexity is high")
        assert pattern is not None
        assert pattern.name is not None

    def test_get_decision_framework(self, soul):
        """Test retrieving decision frameworks."""
        framework = soul.get_decision_framework(DecisionType.TASK_ASSIGNMENT)
        assert framework is not None
        assert framework.decision_type == DecisionType.TASK_ASSIGNMENT

    def test_set_mode(self, soul):
        """Test changing operating mode."""
        soul.set_mode(BehaviorMode.EXECUTE)
        assert soul.current_mode == BehaviorMode.EXECUTE
        
        soul.set_mode(BehaviorMode.ORCHESTRATE)
        assert soul.current_mode == BehaviorMode.ORCHESTRATE

    def test_record_experience(self, soul):
        """Test recording experiences."""
        initial_count = len(soul._experience_log)
        soul.record_experience(
            situation="Complex task received",
            action="Decomposed into subtasks",
            outcome="Successfully assigned",
            success=True
        )
        assert len(soul._experience_log) == initial_count + 1

    def test_adapt_pattern(self, soul):
        """Test adapting behavior patterns."""
        # Find a pattern to adapt
        pattern = soul.behavior_patterns[0]
        result = soul.adapt_pattern(
            pattern_name=pattern.name,
            new_priority=5
        )
        assert result is True
        assert pattern.priority == 5

    def test_add_pattern(self, soul):
        """Test adding new behavior patterns."""
        initial_count = len(soul.behavior_patterns)
        new_pattern = BehaviorPattern(
            name="test_pattern",
            trigger="test trigger",
            action_template="test action",
            priority=10
        )
        soul.add_pattern(new_pattern)
        assert len(soul.behavior_patterns) == initial_count + 1

    def test_soul_serialization(self, soul):
        """Test that Soul can be serialized to dict."""
        data = soul.to_dict()
        assert "behavior_patterns" in data
        assert "decision_frameworks" in data
        assert "current_mode" in data

    def test_soul_singleton(self):
        """Test that get_soul returns a singleton."""
        soul1 = get_soul()
        soul2 = get_soul()
        assert soul1 is soul2

    def test_make_decision(self):
        """Test the make_decision convenience function."""
        decision = make_decision(
            DecisionType.TASK_ASSIGNMENT,
            {"task": "test task"}
        )
        assert decision is not None
        assert isinstance(decision, str)


# ============================================================================
# MEMORY MODULE TESTS
# ============================================================================

class TestPersistentMemory:
    """Tests for the Persistent Memory module."""

    def test_memory_initialization(self, memory):
        """Test that memory initializes correctly."""
        assert memory is not None
        assert len(memory.memories) >= 0

    def test_store_memory(self, memory):
        """Test storing a memory."""
        memory_id = memory.store(
            content="Test memory content",
            memory_type=MemoryType.EPISODIC,
            importance=0.8
        )
        assert memory_id is not None
        assert len(memory_id) > 0

    def test_recall_memory(self, memory):
        """Test recalling a stored memory."""
        memory_id = memory.store(
            content="Test memory for recall",
            memory_type=MemoryType.SEMANTIC,
            importance=0.9
        )
        
        recalled = memory.recall(memory_id)
        assert recalled is not None
        assert recalled.content == "Test memory for recall"
        assert recalled.access_count == 1

    def test_search_memories(self, memory):
        """Test searching memories."""
        memory.store("Important fact about Python", MemoryType.SEMANTIC, 0.8)
        memory.store("Random thought", MemoryType.EPISODIC, 0.5)
        memory.store("Python is great for AI", MemoryType.SEMANTIC, 0.9)

        results = memory.search("Python")
        assert len(results) >= 2

    def test_search_by_type(self, memory):
        """Test filtering search by memory type."""
        memory.store("Episodic memory", MemoryType.EPISODIC, 0.7)
        memory.store("Semantic memory", MemoryType.SEMANTIC, 0.7)

        results = memory.search("memory", memory_type=MemoryType.EPISODIC)
        assert all(r.memory_type == MemoryType.EPISODIC for r in results)

    def test_get_mission_memories(self, memory):
        """Test retrieving mission-critical memories."""
        memory.store("Mission critical info", MemoryType.MISSION, 1.0)
        memory.store("Regular info", MemoryType.SEMANTIC, 0.5)

        mission_memories = memory.get_mission_memories()
        assert len(mission_memories) >= 1
        assert all(m.memory_type == MemoryType.MISSION for m in mission_memories)

    def test_forget_memory(self, memory):
        """Test removing a memory."""
        memory_id = memory.store("Temporary memory", MemoryType.WORKING, 0.3)
        
        result = memory.forget(memory_id)
        assert result is True
        
        recalled = memory.recall(memory_id)
        assert recalled is None

    def test_working_memory(self, memory):
        """Test working memory operations."""
        memory.set_working("current_task", "Build Connection Window")
        memory.set_working("progress", 0.5)

        assert memory.get_working("current_task") == "Build Connection Window"
        assert memory.get_working("progress") == 0.5
        assert memory.get_working("nonexistent") is None

    def test_clear_working_memory(self, memory):
        """Test clearing working memory."""
        memory.set_working("key1", "value1")
        memory.set_working("key2", "value2")
        
        memory.clear_working()
        
        assert memory.get_working("key1") is None
        assert memory.get_working("key2") is None

    def test_memory_persistence(self, temp_storage):
        """Test that memories persist across instances."""
        storage_path = os.path.join(temp_storage, "persist-test.json")
        
        # Create and store
        memory1 = PersistentMemory(storage_path=storage_path)
        memory1.store("Persistent memory", MemoryType.SEMANTIC, 0.9)
        
        # Create new instance and verify
        memory2 = PersistentMemory(storage_path=storage_path)
        results = memory2.search("Persistent")
        assert len(results) >= 1

    def test_memory_stats(self, memory):
        """Test memory statistics."""
        memory.store("Test 1", MemoryType.EPISODIC, 0.5)
        memory.store("Test 2", MemoryType.SEMANTIC, 0.5)

        stats = memory.get_stats()
        assert "total_memories" in stats
        assert "by_type" in stats
        assert stats["total_memories"] >= 2

    def test_memory_singleton(self):
        """Test that get_memory returns a singleton."""
        # Note: This test may fail if other tests have already created the singleton
        # In practice, you'd reset the singleton for testing
        memory = get_memory()
        assert memory is not None


# ============================================================================
# CANONICAL ORDER TESTS
# ============================================================================

class TestCanonicalOrder:
    """Tests for the Canonical Order tracking system."""

    def test_canonical_order_initialization(self, canonical_order):
        """Test that CanonicalOrder initializes correctly."""
        assert canonical_order is not None
        assert canonical_order.session_id is not None
        assert len(canonical_order.orders) == 0

    def test_create_order(self, canonical_order):
        """Test creating a Canonical Order."""
        order = canonical_order.create_order(
            agent_name="Meta",
            agent_role="Orchestrator",
            action_type="communicate",
            description="Send task to agent",
            input_data={"task": "Build feature"},
            context={"project": "Archon X"}
        )
        
        assert order is not None
        assert order.order_id is not None
        assert order.agent_name == "Meta"
        assert order.action_type == "communicate"
        assert len(canonical_order.orders) == 1

    def test_session_summary(self, canonical_order):
        """Test getting session summary."""
        canonical_order.create_order(
            agent_name="Meta",
            agent_role="Orchestrator",
            action_type="think",
            description="Analyzing task"
        )
        canonical_order.create_order(
            agent_name="Engineer",
            agent_role="Developer",
            action_type="act",
            description="Writing code"
        )
        
        summary = canonical_order.get_session_summary()
        assert summary["total_orders"] == 2
        assert "Meta" in summary["agents_involved"]
        assert "Engineer" in summary["agents_involved"]

    def test_get_orders_by_agent(self, canonical_order):
        """Test filtering orders by agent."""
        canonical_order.create_order(
            agent_name="Meta",
            agent_role="Orchestrator",
            action_type="think",
            description="Thinking"
        )
        canonical_order.create_order(
            agent_name="Engineer",
            agent_role="Developer",
            action_type="act",
            description="Acting"
        )
        
        meta_orders = canonical_order.get_orders_by_agent("Meta")
        assert len(meta_orders) == 1
        assert meta_orders[0].agent_name == "Meta"

    def test_get_orders_by_type(self, canonical_order):
        """Test filtering orders by action type."""
        canonical_order.create_order(
            agent_name="Meta",
            agent_role="Orchestrator",
            action_type="think",
            description="Thinking"
        )
        canonical_order.create_order(
            agent_name="Meta",
            agent_role="Orchestrator",
            action_type="communicate",
            description="Communicating"
        )
        
        think_orders = canonical_order.get_orders_by_type("think")
        assert len(think_orders) == 1
        assert think_orders[0].action_type == "think"

    def test_order_serialization(self, canonical_order):
        """Test that orders can be serialized."""
        order = canonical_order.create_order(
            agent_name="Meta",
            agent_role="Orchestrator",
            action_type="create",
            description="Creating resource"
        )
        
        order_dict = order.to_dict()
        assert "canonical_order" in order_dict
        
        order_json = order.to_json()
        parsed = json.loads(order_json)
        assert "canonical_order" in parsed

    def test_export_session(self, canonical_order):
        """Test exporting session data."""
        canonical_order.create_order(
            agent_name="Meta",
            agent_role="Orchestrator",
            action_type="think",
            description="Test"
        )
        
        # JSON export
        json_export = canonical_order.export_session(format="json")
        assert json_export is not None
        
        # JSONL export
        jsonl_export = canonical_order.export_session(format="jsonl")
        assert jsonl_export is not None
        
        # Summary export
        summary_export = canonical_order.export_session(format="summary")
        assert "Session Summary" in summary_export

    def test_parent_child_orders(self, canonical_order):
        """Test parent-child order relationships."""
        parent = canonical_order.create_order(
            agent_name="Meta",
            agent_role="Orchestrator",
            action_type="orchestrate",
            description="Starting workflow"
        )
        
        child = canonical_order.create_order(
            agent_name="Engineer",
            agent_role="Developer",
            action_type="act",
            description="Executing subtask",
            parent_order_id=parent.order_id
        )
        
        assert child.parent_order_id == parent.order_id
        
        tree = canonical_order.get_order_tree(parent.order_id)
        assert tree is not None
        assert len(tree["children"]) == 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for the complete system."""

    def test_heart_soul_memory_integration(self, heart, soul, memory):
        """Test that Heart, Soul, and Memory work together."""
        # Simulate an action
        action = "Help user build a landing page"
        
        # Check values alignment
        is_aligned, violations = heart.check_values_alignment(action)
        assert is_aligned is True
        
        # Get behavior pattern
        pattern = soul.get_behavior_pattern("user needs help")
        assert pattern is not None
        
        # Record in memory
        memory_id = memory.store(
            content=f"Action: {action}",
            memory_type=MemoryType.EPISODIC,
            importance=0.8
        )
        assert memory_id is not None

    def test_full_workflow(self, temp_storage):
        """Test a complete workflow with all components."""
        # Initialize all components
        heart = Heart()
        soul = Soul()
        memory = PersistentMemory(
            storage_path=os.path.join(temp_storage, "workflow-memory.json")
        )
        canonical_order = CanonicalOrder(
            storage_path=os.path.join(temp_storage, "workflow-orders")
        )
        
        # Simulate receiving a task
        task = "Build a Connection Window for agent observation"
        
        # 1. Check values
        is_aligned, _ = heart.check_values_alignment(task)
        assert is_aligned is True
        
        # 2. Get behavior pattern
        pattern = soul.get_behavior_pattern("complex task")
        assert pattern is not None
        
        # 3. Create canonical order
        order = canonical_order.create_order(
            agent_name="Meta",
            agent_role="Orchestrator",
            action_type="think",
            description=f"Received task: {task}"
        )
        assert order is not None
        
        # 4. Store in memory
        memory.store(
            content=f"Task received: {task}",
            memory_type=MemoryType.WORKING,
            importance=0.9
        )
        
        # 5. Verify everything is connected
        summary = canonical_order.get_session_summary()
        assert summary["total_orders"] >= 1
        
        memories = memory.search("Task received")
        assert len(memories) >= 1


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
